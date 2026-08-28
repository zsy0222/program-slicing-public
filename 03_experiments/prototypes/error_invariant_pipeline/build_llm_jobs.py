"""Prepare comparable, oracle-free tasks for the LLM experiment groups."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


SOURCE_SYSTEM = """You are evaluating fault localization for a C program that fails an assertion.
Use only the supplied source and failure information. Do not assume access to tests,
execution, or a correct reference program. Return valid JSON only with this schema:
{
  \"ranked_candidates\": [{\"source_line\": 0, \"reason\": \"...\", \"confidence\": 0.0}],
  \"causal_chain\": [\"...\"],
  \"repair_hypothesis\": \"...\",
  \"uncertainty\": \"...\"
}
Rank at most three non-assertion source lines."""

EVIDENCE_SYSTEM = """You are evaluating fault localization for a C program that fails an assertion.
Use the supplied source and Error-Invariant evidence trajectory. Return valid JSON only:
{
  \"ranked_candidates\": [{\"analysis_location\": 0, \"evidence_refs\": [\"L0\"], \"reason\": \"...\", \"confidence\": 0.0}],
  \"causal_chain\": [{\"claim_type\": \"direct_write|initialization|control_guard|other\", \"claim\": \"...\", \"evidence_refs\": [\"L0\"]}],
  \"repair_hypothesis\": \"...\",
  \"uncertainty\": \"...\"
}
Every causal claim and candidate must cite only existing L-IDs. Rank at most three
non-assertion locations. Do not use information absent from the supplied evidence."""

SLICE_SYSTEM = """You are evaluating fault localization for a C program that fails an assertion.
Use the supplied source, failure information, and static semantic slice in the
analyzer's intermediate representation. Do not assume tests or a correct reference.
Return valid JSON only with this schema:
{
  \"ranked_candidates\": [{\"source_line\": 0, \"reason\": \"...\", \"confidence\": 0.0}],
  \"causal_chain\": [\"...\"],
  \"repair_hypothesis\": \"...\",
  \"uncertainty\": \"...\"
}
Rank at most three non-assertion source lines."""

RAW_MAP_SYSTEM = """You are evaluating fault localization for a C program that fails an assertion.
Use the supplied source, failure information, and raw Error Invariant Map exactly as
emitted by the analyzer. Return valid JSON only with this schema:
{
  \"ranked_candidates\": [{\"analysis_location\": 0, \"reason\": \"...\", \"confidence\": 0.0}],
  \"causal_chain\": [\"...\"],
  \"repair_hypothesis\": \"...\",
  \"uncertainty\": \"...\"
}
Rank at most three non-assertion analyzer locations."""


def numbered_source(path: Path) -> str:
    return "\n".join(f"{index:>3} | {line}" for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1))


def assertion_line(path: Path) -> int:
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if "assert(" in line:
            return index
    raise ValueError(f"No assertion in {path}")


def write_jsonl(path: Path, jobs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(job, ensure_ascii=False) + "\n" for job in jobs), encoding="utf-8")


def section(text: str, header: str, terminator: str) -> str:
    start = text.find(header)
    if start < 0:
        raise ValueError(f"Missing analyzer section: {header}")
    start += len(header)
    end = text.find(terminator, start)
    if end < 0:
        raise ValueError(f"Missing section terminator after: {header}")
    return text[start:end].strip()


def safe_evidence_view(trajectory: dict) -> dict:
    """Exclude annotations and G1 rankings so the LLM never sees ground truth."""
    return {
        "schema_version": trajectory["schema_version"],
        "error": trajectory["error"],
        "evidence_locations": trajectory["evidence_locations"],
    }


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
        status = {row["case_id"]: row["analysis_status"] for row in csv.DictReader(file)}

    source_only_jobs = []
    slice_jobs = []
    raw_map_jobs = []
    evidence_jobs = []
    for case in cases:
        source_path = args.benchmark_dir / case["faulty_program"]
        base_user = {
            "case_id": case["case_id"],
            "failure": f"The assertion at source line {assertion_line(source_path)} fails at runtime.",
            "numbered_c_source": numbered_source(source_path),
        }
        source_only_jobs.append(
            {
                "experiment_group": "G2_source_only_llm",
                "system": SOURCE_SYSTEM,
                "user": base_user,
            }
        )

        trajectory_path = args.trajectory_dir / f"{case['case_id']}.json"
        if status.get(case["case_id"]) == "completed" and trajectory_path.exists():
            trajectory = json.loads(trajectory_path.read_text(encoding="utf-8"))
            analysis_text = Path(trajectory["source"]["analyzer_output"]).read_text(encoding="utf-8")
            slice_jobs.append(
                {
                    "experiment_group": "G3_slice_aware_llm",
                    "system": SLICE_SYSTEM,
                    "user": {
                        **base_user,
                        "static_semantic_slice_ir": section(
                            analysis_text,
                            "Abstract Syntax of Program Slice:",
                            "Total Time:",
                        ),
                    },
                }
            )
            raw_map_jobs.append(
                {
                    "experiment_group": "G4_raw_error_invariant_llm",
                    "system": RAW_MAP_SYSTEM,
                    "user": {
                        **base_user,
                        "raw_error_invariant_map": section(
                            analysis_text, "Error Invariant Map::", "Type :"
                        ),
                    },
                }
            )
            evidence_jobs.append(
                {
                    "experiment_group": "G5_structured_evidence_llm",
                    "system": EVIDENCE_SYSTEM,
                    "user": {**base_user, "evidence_trajectory": safe_evidence_view(trajectory)},
                }
            )

    write_jsonl(args.output_dir / "G2_source_only.jsonl", source_only_jobs)
    write_jsonl(args.output_dir / "G3_slice_aware.jsonl", slice_jobs)
    write_jsonl(args.output_dir / "G4_raw_error_invariant.jsonl", raw_map_jobs)
    write_jsonl(args.output_dir / "G5_structured_evidence.jsonl", evidence_jobs)
    print(f"G2 source-only jobs: {len(source_only_jobs)}")
    print(f"G3 slice-aware jobs: {len(slice_jobs)}")
    print(f"G4 raw Error Invariant jobs: {len(raw_map_jobs)}")
    print(f"G5 structured-evidence jobs: {len(evidence_jobs)}")


if __name__ == "__main__":
    main()
