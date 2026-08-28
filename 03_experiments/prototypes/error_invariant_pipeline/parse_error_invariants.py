"""Create a machine-readable evidence trajectory from Error Invariants output.

This is deliberately a conservative first-stage extractor.  It records facts
emitted by the analyzer and derives the *pure-tool* ranking only from direct
writes to variables occurring in the error-location invariant.  It does not
claim that a ranked statement is the developer-intended root cause.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


LOCATION_RE = re.compile(r"^\[\s*(\d+)\s*:\]\s*:?\s*(.*)$")
IDENTIFIER_RE = re.compile(r"\b[A-Za-z_]\w*\b")
ASSIGNMENT_RE = re.compile(r"\b([A-Za-z_]\w*)\s*:=")
IGNORED_IDENTIFIERS = {
    "top", "bottom", "true", "false", "bool", "unwind", "and", "or",
}


def _parse_locations(block: str) -> dict[int, str]:
    """Parse analyzer locations; append wrapped invariant lines when present."""
    locations: dict[int, str] = {}
    current_id: int | None = None
    for raw_line in block.splitlines():
        match = LOCATION_RE.match(raw_line.strip())
        if match:
            current_id = int(match.group(1))
            locations[current_id] = match.group(2).strip()
        elif current_id is not None and raw_line.strip():
            locations[current_id] = f"{locations[current_id]} {raw_line.strip()}".strip()
    return locations


def _first_section(text: str, header: str, terminator: str) -> str:
    start = text.find(header)
    if start < 0:
        raise ValueError(f"Could not find {header!r} in Error Invariants output")
    start += len(header)
    end = text.find(terminator, start)
    if end < 0:
        raise ValueError(f"Could not find terminator {terminator!r} after {header!r}")
    return text[start:end]


def _error_variables(invariant: str) -> list[str]:
    values = []
    for token in IDENTIFIER_RE.findall(invariant):
        if token.lower() not in IGNORED_IDENTIFIERS and not token.startswith("B"):
            if token not in values:
                values.append(token)
    return values


def _role(location_id: int, error_location_id: int, statement: str, invariant: str) -> str:
    if location_id == error_location_id:
        return "error_state"
    if ":=" in statement:
        return "state_update"
    if statement.startswith("if ") or statement.startswith("while "):
        return "control_guard"
    if invariant not in {"top", "bottom", ""}:
        return "error_relevant_location"
    return "context"


def _rank_pure_tool_candidates(
    syntax: dict[int, str], error_location_id: int, error_variables: list[str]
) -> list[dict[str, Any]]:
    """Rank direct writes to error variables with a transparent fixed heuristic."""
    candidates: list[dict[str, Any]] = []
    error_vars = set(error_variables)
    for location_id, statement in syntax.items():
        if location_id >= error_location_id or "assert(" in statement:
            continue
        writes = ASSIGNMENT_RE.findall(statement)
        matching_writes = [variable for variable in writes if variable in error_vars]
        if not matching_writes:
            continue
        distance = error_location_id - location_id
        candidates.append(
            {
                "location_id": location_id,
                "statement": statement,
                "rank": 0,
                "score": 200 - distance,
                "reason": (
                    "Directly writes error-state variable(s) "
                    f"{matching_writes}; closer statements rank higher."
                ),
                "evidence_refs": [f"L{location_id}", f"L{error_location_id}"],
            }
        )
    candidates.sort(key=lambda item: (-item["score"], item["location_id"]))
    for rank, candidate in enumerate(candidates, start=1):
        candidate["rank"] = rank
    return candidates


def build_trajectory(
    case_id: str,
    source_path: str,
    analysis_path: Path,
    ground_truth_location_id: int | None = None,
    ground_truth_source_line: int | None = None,
    ground_truth_kind: str | None = None,
) -> dict[str, Any]:
    text = analysis_path.read_text(encoding="utf-8", errors="replace")
    syntax = _parse_locations(_first_section(text, "Abstract Syntax:", "polyhedra"))
    invariant_block = _first_section(text, "Error Invariant Map::", "Type :")
    invariants = _parse_locations(invariant_block)

    assert_locations = [
        location_id for location_id, statement in syntax.items() if "assert(" in statement
    ]
    if not assert_locations:
        raise ValueError("No assertion location found in analyzer abstract syntax")
    error_location_id = assert_locations[-1]
    error_invariant = invariants.get(error_location_id, "unknown")
    error_variables = _error_variables(error_invariant)
    error_variable_set = set(error_variables)

    evidence_locations = []
    for location_id in sorted(syntax):
        statement = syntax[location_id]
        invariant = invariants.get(location_id, "unknown")
        direct_error_write = bool(error_variable_set.intersection(ASSIGNMENT_RE.findall(statement)))
        if (
            invariant in {"top", "bottom", "unknown", ""}
            and location_id != error_location_id
            and not direct_error_write
        ):
            continue
        evidence_locations.append(
            {
                "id": f"L{location_id}",
                "location_id": location_id,
                "statement": statement,
                "error_invariant": invariant,
                "role": _role(location_id, error_location_id, statement, invariant),
                "source": "Error Invariants first Error Invariant Map",
            }
        )

    return {
        "schema_version": "0.2",
        "case_id": case_id,
        "source": {
            "normalized_program": source_path,
            "analyzer_output": str(analysis_path).replace("\\", "/"),
            "analysis_mode": "full / polyhedra",
        },
        "error": {
            "location_id": error_location_id,
            "location_ref": f"L{error_location_id}",
            "statement": syntax[error_location_id],
            "error_invariant": error_invariant,
            "variables": error_variables,
        },
        "evidence_locations": evidence_locations,
        "pure_tool_baseline": {
            "method": "direct-write-to-error-variable ranking",
            "candidates": _rank_pure_tool_candidates(
                syntax, error_location_id, error_variables
            ),
            "interpretation_limit": (
                "Candidates are error-relevant statements, not established root-cause labels. "
                "Ground truth requires human confirmation or a known reference patch."
            ),
        },
        "annotation": {
            "ground_truth_status": (
                "confirmed" if ground_truth_location_id is not None else "needs_human_confirmation"
            ),
            "ground_truth_location_id": ground_truth_location_id,
            "ground_truth_source_line": ground_truth_source_line,
            "ground_truth_kind": ground_truth_kind,
            "suggested_fault_location": 8 if case_id == "SV01_Mono5_1" else None,
            "suggested_fault_rationale": (
                "L8 directly decrements z, the variable constrained to z == 0 at the assertion."
                if case_id == "SV01_Mono5_1"
                else "unknown"
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--source", required=True, help="Normalized C source path stored in output")
    parser.add_argument("--analysis-output", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--ground-truth-location-id", type=int)
    parser.add_argument("--ground-truth-source-line", type=int)
    parser.add_argument("--ground-truth-kind")
    args = parser.parse_args()

    trajectory = build_trajectory(
        args.case_id,
        args.source,
        args.analysis_output,
        args.ground_truth_location_id,
        args.ground_truth_source_line,
        args.ground_truth_kind,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(trajectory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
