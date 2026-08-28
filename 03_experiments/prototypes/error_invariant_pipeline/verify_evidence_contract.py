"""Validate whether an LLM's structured explanation is grounded in evidence."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ASSIGNMENT_RE = re.compile(r"\b([A-Za-z_]\w*)\s*:=")
ALLOWED_CLAIM_TYPES = {"direct_write", "initialization", "control_guard", "other"}


def verify(trajectory: dict, response: dict) -> dict:
    evidence_by_ref = {item["id"]: item for item in trajectory["evidence_locations"]}
    error_location = trajectory["error"]["location_id"]
    error_variables = set(trajectory["error"]["variables"])
    violations: list[str] = []

    candidates = response.get("ranked_candidates")
    if not isinstance(candidates, list) or not candidates:
        violations.append("missing_ranked_candidates")
        candidates = []
    if len(candidates) > 3:
        violations.append("too_many_ranked_candidates")
    for index, candidate in enumerate(candidates, 1):
        location = candidate.get("analysis_location")
        ref = f"L{location}" if isinstance(location, int) else None
        refs = candidate.get("evidence_refs")
        if ref not in evidence_by_ref:
            violations.append(f"candidate_{index}_unknown_location")
        elif location == error_location:
            violations.append(f"candidate_{index}_is_assertion_location")
        if not isinstance(refs, list) or not refs:
            violations.append(f"candidate_{index}_missing_evidence_refs")
        else:
            unknown = [item for item in refs if item not in evidence_by_ref]
            if unknown:
                violations.append(f"candidate_{index}_unknown_evidence_refs")
            if ref is not None and ref not in refs:
                violations.append(f"candidate_{index}_does_not_cite_own_location")

    chain = response.get("causal_chain")
    if not isinstance(chain, list) or not chain:
        violations.append("missing_causal_chain")
        chain = []
    for index, step in enumerate(chain, 1):
        if not isinstance(step, dict):
            violations.append(f"chain_{index}_not_structured")
            continue
        claim_type = step.get("claim_type")
        refs = step.get("evidence_refs")
        if claim_type not in ALLOWED_CLAIM_TYPES:
            violations.append(f"chain_{index}_unknown_claim_type")
        if not isinstance(refs, list) or not refs:
            violations.append(f"chain_{index}_missing_evidence_refs")
            continue
        referenced = [evidence_by_ref[item] for item in refs if item in evidence_by_ref]
        if len(referenced) != len(refs):
            violations.append(f"chain_{index}_unknown_evidence_refs")
        if claim_type in {"direct_write", "initialization"}:
            writes_error_variable = any(
                error_variables.intersection(ASSIGNMENT_RE.findall(item["statement"]))
                for item in referenced
            )
            if not writes_error_variable:
                violations.append(f"chain_{index}_write_claim_not_supported")
        if claim_type == "control_guard" and not any(
            item["role"] == "control_guard" for item in referenced
        ):
            violations.append(f"chain_{index}_guard_claim_not_supported")

    feedback = (
        "Evidence contract satisfied."
        if not violations
        else "Revise the answer: " + "; ".join(violations)
    )
    return {
        "valid": not violations,
        "violations": violations,
        "feedback_for_next_round": feedback,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trajectory", required=True, type=Path)
    parser.add_argument("--response", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    trajectory = json.loads(args.trajectory.read_text(encoding="utf-8"))
    response = json.loads(args.response.read_text(encoding="utf-8"))
    result = verify(trajectory, response)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
