"""Check V2 role-aware answers against source and Error-Invariant evidence.

The contract verifies provenance and structural claims only. It deliberately
does not decide which candidate is the developer-intended repair.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ALLOWED_ROLES = {"fault_origin", "error_mechanism", "control_enabler", "context"}
ALLOWED_CLAIM_TYPES = {"direct_write", "initialization", "control_guard", "other"}
ASSIGNMENT_RE = re.compile(r"\b([A-Za-z_]\w*)\s*:=")
TOKEN_RE = re.compile(r"[A-Za-z_]\w*|\d+|>=|<=|==|!=|:=|[+*/<>=-]")
NON_SEMANTIC_TOKENS = {"int", "then", "do", "endif", "od"}


def _source_lines(numbered_source: str) -> dict[int, str]:
    result: dict[int, str] = {}
    for row in numbered_source.splitlines():
        if "|" not in row:
            continue
        number, source = row.split("|", 1)
        try:
            result[int(number.strip())] = source.strip()
        except ValueError:
            continue
    return result


def _statement_tokens(statement: str) -> list[str]:
    """Normalize the C and analyzer surface syntaxes before location binding."""
    statement = re.sub(r"\[\s*\d+\s*:\s*\]", "", statement.lower())
    tokens = TOKEN_RE.findall(statement)
    return ["=" if token == ":=" else token for token in tokens if token not in NON_SEMANTIC_TOKENS]


def _source_matches_evidence(source: str, evidence_statement: str) -> bool:
    return _statement_tokens(source) == _statement_tokens(evidence_statement)


def verify(user: dict[str, Any], response: dict[str, Any], require_evidence: bool) -> dict[str, Any]:
    source_lines = _source_lines(user.get("numbered_c_source", ""))
    assertion_lines = {line for line, text in source_lines.items() if "assert(" in text}
    trajectory = user.get("evidence_trajectory", {})
    evidence = {item["id"]: item for item in trajectory.get("evidence_locations", [])}
    error_variables = set(trajectory.get("error", {}).get("variables", []))
    violations: list[str] = []

    candidates = response.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        violations.append("missing_candidates")
        candidates = []
    if len(candidates) > 3:
        violations.append("too_many_candidates")
    for index, candidate in enumerate(candidates, 1):
        if not isinstance(candidate, dict):
            violations.append(f"candidate_{index}_not_object")
            continue
        line = candidate.get("source_line")
        if not isinstance(line, int) or line not in source_lines:
            violations.append(f"candidate_{index}_unknown_source_line")
        elif line in assertion_lines:
            violations.append(f"candidate_{index}_is_assertion")
        if candidate.get("role") not in ALLOWED_ROLES:
            violations.append(f"candidate_{index}_unknown_role")
        replacement = candidate.get("proposed_replacement")
        if not isinstance(replacement, str):
            violations.append(f"candidate_{index}_replacement_not_string")
        elif "\n" in replacement or "\r" in replacement:
            violations.append(f"candidate_{index}_replacement_not_single_line")
        if require_evidence:
            refs = candidate.get("evidence_refs")
            if not isinstance(refs, list) or not refs:
                violations.append(f"candidate_{index}_missing_evidence_refs")
            elif any(ref not in evidence for ref in refs):
                violations.append(f"candidate_{index}_unknown_evidence_refs")
            elif isinstance(line, int) and line in source_lines and not any(
                _source_matches_evidence(source_lines[line], evidence[ref]["statement"])
                for ref in refs
            ):
                violations.append(f"candidate_{index}_source_evidence_mismatch")

    if require_evidence:
        claims = response.get("mechanism_claims")
        if not isinstance(claims, list) or not claims:
            violations.append("missing_mechanism_claims")
            claims = []
        for index, claim in enumerate(claims, 1):
            if not isinstance(claim, dict):
                violations.append(f"claim_{index}_not_object")
                continue
            claim_type = claim.get("claim_type")
            refs = claim.get("evidence_refs")
            if claim_type not in ALLOWED_CLAIM_TYPES:
                violations.append(f"claim_{index}_unknown_type")
            if not isinstance(refs, list) or not refs:
                violations.append(f"claim_{index}_missing_evidence_refs")
                continue
            referenced = [evidence[ref] for ref in refs if ref in evidence]
            if len(referenced) != len(refs):
                violations.append(f"claim_{index}_unknown_evidence_refs")
            if claim_type in {"direct_write", "initialization"}:
                writes_error_variable = any(
                    error_variables.intersection(ASSIGNMENT_RE.findall(item["statement"]))
                    for item in referenced
                )
                if not writes_error_variable:
                    violations.append(f"claim_{index}_write_not_supported")
            if claim_type == "control_guard" and not any(
                item.get("role") == "control_guard" for item in referenced
            ):
                violations.append(f"claim_{index}_guard_not_supported")

    return {
        "valid": not violations,
        "violations": violations,
        "feedback_for_next_round": (
            "V2 evidence-and-role contract satisfied."
            if not violations
            else "Revise only the affected items: " + "; ".join(violations)
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path, help="One oracle-free job JSON object")
    parser.add_argument("--response", required=True, type=Path, help="One parsed LLM response JSON object")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    job = json.loads(args.job.read_text(encoding="utf-8"))
    response = json.loads(args.response.read_text(encoding="utf-8"))
    required = job.get("experiment_group") == "P_V2b_ei_audited"
    result = verify(job["user"], response, required)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
