"""Build one targeted P-V2b revision job for every rejected initial response."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_v2_jobs import FULL_V2_SYSTEM, LOCATION_MAPPING_RULE


FEEDBACK_SYSTEM = FULL_V2_SYSTEM + LOCATION_MAPPING_RULE + """

This is a revision. The validator found one or more source-line to evidence
location mismatches. Keep a candidate's source_line only when at least one of
its cited evidence_refs denotes the same original statement after C/IR syntax
normalization. Analyzer locations and source line numbers are not interchangeable.
Revise only what is needed and return the complete JSON object again."""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", required=True, type=Path)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--verification", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    jobs = {
        json.loads(line)["user"]["case_id"]: json.loads(line)
        for line in args.jobs.read_text(encoding="utf-8").splitlines()
        if line
    }
    checks = {
        (item["case_id"], item["repetition"]): item
        for item in json.loads(args.verification.read_text(encoding="utf-8"))["records"]
    }
    feedback_jobs = []
    for line in args.responses.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        response = json.loads(line)
        check = checks[(response["case_id"], response["repetition"])]
        if response.get("status") != "completed" or check["valid"]:
            continue
        feedback_jobs.append(
            {
                "experiment_group": "P_V2b_ei_audited_feedback",
                "origin_repetition": response["repetition"],
                "system": FEEDBACK_SYSTEM,
                "user": {
                    **jobs[response["case_id"]]["user"],
                    "previous_answer": json.loads(response["content"]),
                    "validator_feedback": check["feedback_for_next_round"],
                },
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(job, ensure_ascii=False) + "\n" for job in feedback_jobs), encoding="utf-8")
    print(f"P-V2b feedback jobs: {len(feedback_jobs)}")


if __name__ == "__main__":
    main()
