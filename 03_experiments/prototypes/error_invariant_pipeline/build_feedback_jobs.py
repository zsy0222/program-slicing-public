"""Create one G6 revision task for each G5 response rejected by the verifier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


FEEDBACK_SYSTEM = """Revise a fault-localization answer after an evidence validator rejected it.
Use only the source and Error-Invariant trajectory provided below. Correct every reported
evidence violation; do not cite locations absent from the evidence. Return valid JSON only:
{
  \"ranked_candidates\": [{\"analysis_location\": 0, \"evidence_refs\": [\"L0\"], \"reason\": \"...\", \"confidence\": 0.0}],
  \"causal_chain\": [{\"claim_type\": \"direct_write|initialization|control_guard|other\", \"claim\": \"...\", \"evidence_refs\": [\"L0\"]}],
  \"repair_hypothesis\": \"...\",
  \"uncertainty\": \"...\"
}
Rank at most three non-assertion locations. Every candidate and causal claim must cite
only existing L-IDs."""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g5-jobs", required=True, type=Path)
    parser.add_argument("--g5-responses", required=True, type=Path)
    parser.add_argument("--verification", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    jobs = {json.loads(line)["user"]["case_id"]: json.loads(line) for line in args.g5_jobs.read_text(encoding="utf-8").splitlines() if line}
    verification = {
        (record["case_id"], record["repetition"]): record
        for record in json.loads(args.verification.read_text(encoding="utf-8"))["records"]
    }
    feedback_jobs = []
    for line in args.g5_responses.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        response = json.loads(line)
        check = verification[(response["case_id"], response["repetition"])]
        if check["valid"]:
            continue
        base_job = jobs[response["case_id"]]
        feedback_jobs.append(
            {
                "experiment_group": "G6_evidence_feedback_llm",
                "origin_repetition": response["repetition"],
                "system": FEEDBACK_SYSTEM,
                "user": {
                    **base_job["user"],
                    "previous_answer": json.loads(response["content"]),
                    "validator_feedback": check["feedback_for_next_round"],
                },
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(job, ensure_ascii=False) + "\n" for job in feedback_jobs), encoding="utf-8")
    print(f"G6 feedback jobs: {len(feedback_jobs)}")


if __name__ == "__main__":
    main()
