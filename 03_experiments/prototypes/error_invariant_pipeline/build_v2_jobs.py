"""Build oracle-free P-V2a and P-V2b jobs from completed Error-Invariant runs.

P-V2a receives source plus semantic slice and must separate causal roles.
P-V2b additionally receives the v0.2 evidence trajectory, which is used to
ground mechanism claims.  Neither job contains the manifest's reference patch
or ground-truth fields.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from build_llm_jobs import assertion_line, numbered_source, safe_evidence_view, section, write_jsonl
from verify_v2_contract import _source_matches_evidence


ROLE_VALUES = "fault_origin|error_mechanism|control_enabler|context"

ROLE_ONLY_SYSTEM = f"""You are analysing a C program that fails an assertion.
Use only the supplied source, failure information, and static semantic slice.
Do not assume access to tests, an execution trace, a correct program, or ground
truth. Return valid JSON only with this schema:
{{
  "candidates": [
    {{
      "source_line": 0,
      "role": "{ROLE_VALUES}",
      "proposed_replacement": "one complete replacement line of C code or empty string",
      "reason": "...",
      "confidence": 0.0
    }}
  ],
  "mechanism_summary": "...",
  "uncertainty": "..."
}}
Rank at most three non-assertion source lines. A fault_origin is a candidate
developer edit; an error_mechanism is a state transition that reaches failure;
a control_enabler is a guard or boundary enabling that path; context is relevant
but not causal. Do not present an error_mechanism as a fault_origin unless the
supplied information justifies that choice."""

FULL_V2_SYSTEM = f"""You are analysing a C program that fails an assertion.
Use only the supplied source, failure information, semantic slice, and
Error-Invariant evidence trajectory. Do not assume access to tests, an
execution trace, a correct program, or ground truth. Return valid JSON only:
{{
  "candidates": [
    {{
      "source_line": 0,
      "role": "{ROLE_VALUES}",
      "proposed_replacement": "one complete replacement line of C code or empty string",
      "reason": "...",
      "confidence": 0.0,
      "evidence_refs": ["L0"]
    }}
  ],
  "mechanism_claims": [
    {{"claim_type": "direct_write|initialization|control_guard|other", "claim": "...", "evidence_refs": ["L0"]}}
  ],
  "mechanism_summary": "...",
  "uncertainty": "..."
}}
Rank at most three non-assertion source lines. Every candidate and mechanism
claim must cite only existing L-IDs. The evidence trajectory is an audit source
for statements about the error-reaching mechanism; it does not by itself prove
the intended developer fault. If distinct edits remain plausible, state the
ambiguity in uncertainty rather than claiming a unique root cause."""

LOCATION_MAPPING_RULE = """

Use analyzer_to_source_map as the only conversion between analyzer L-IDs and
source lines. An L-ID is not a source line. For every candidate, its source_line
must be the source_line listed for at least one cited evidence reference. If a
relevant L-ID has no unique source mapping, do not use it as a repair location.
"""


def evidence_source_map(source_path: Path, trajectory: dict) -> list[dict]:
    source = {
        index: line
        for index, line in enumerate(source_path.read_text(encoding="utf-8").splitlines(), 1)
    }
    mappings = []
    for item in trajectory["evidence_locations"]:
        matches = [
            line_number
            for line_number, statement in source.items()
            if _source_matches_evidence(statement, item["statement"])
        ]
        mappings.append(
            {
                "evidence_ref": item["id"],
                "source_line": matches[0] if len(matches) == 1 else None,
                "mapping_status": "unique" if len(matches) == 1 else "unmapped_or_ambiguous",
            }
        )
    return mappings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--benchmark-dir", required=True, type=Path)
    parser.add_argument("--run-status", required=True, type=Path)
    parser.add_argument("--trajectory-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    with args.manifest.open(newline="", encoding="utf-8") as file:
        cases = list(csv.DictReader(file))
    with args.run_status.open(newline="", encoding="utf-8") as file:
        statuses = {row["case_id"]: row["analysis_status"] for row in csv.DictReader(file)}
    # Existing trajectories record analyzer outputs relative to the repository
    # root. The trajectory directory is <root>/03_experiments/outputs/<name>.
    workspace_root = args.trajectory_dir.resolve().parents[2]

    role_only_jobs: list[dict] = []
    full_v2_jobs: list[dict] = []
    for case in cases:
        if statuses.get(case["case_id"]) != "completed":
            continue
        source_path = args.benchmark_dir / case["faulty_program"]
        trajectory_path = args.trajectory_dir / f"{case['case_id']}.json"
        if not trajectory_path.exists():
            continue
        trajectory = json.loads(trajectory_path.read_text(encoding="utf-8"))
        analysis_path = Path(trajectory["source"]["analyzer_output"])
        if not analysis_path.is_absolute():
            analysis_path = workspace_root / analysis_path
        analysis_text = analysis_path.read_text(
            encoding="utf-8", errors="replace"
        )
        base_user = {
            "case_id": case["case_id"],
            "failure": f"The assertion at source line {assertion_line(source_path)} fails at runtime.",
            "numbered_c_source": numbered_source(source_path),
            "static_semantic_slice_ir": section(
                analysis_text, "Abstract Syntax of Program Slice:", "Total Time:"
            ),
        }
        role_only_jobs.append(
            {"experiment_group": "P_V2a_role_aware", "system": ROLE_ONLY_SYSTEM, "user": base_user}
        )
        full_v2_jobs.append(
            {
                "experiment_group": "P_V2b_ei_audited", 
                "system": FULL_V2_SYSTEM + LOCATION_MAPPING_RULE,
                "user": {
                    **base_user,
                    "evidence_trajectory": safe_evidence_view(trajectory),
                    "analyzer_to_source_map": evidence_source_map(source_path, trajectory),
                },
            }
        )

    write_jsonl(args.output_dir / "P_V2a_role_aware.jsonl", role_only_jobs)
    write_jsonl(args.output_dir / "P_V2b_ei_audited.jsonl", full_v2_jobs)
    print(f"P-V2a role-aware jobs: {len(role_only_jobs)}")
    print(f"P-V2b EI-audited jobs: {len(full_v2_jobs)}")


if __name__ == "__main__":
    main()
