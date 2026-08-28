"""Build G5 repair retries from actual local validation feedback."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def compact(value: str | None, limit: int = 2500) -> str:
    value = value or ""
    return value[-limit:]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g4-jobs", required=True, type=Path)
    parser.add_argument("--g4-responses", required=True, type=Path)
    parser.add_argument("--validation", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    g4_jobs = {json.loads(line)["user"]["case_id"]: json.loads(line) for line in args.g4_jobs.read_text(encoding="utf-8").splitlines() if line}
    responses = {(record["case_id"], record["repetition"]): record for record in (json.loads(line) for line in args.g4_responses.read_text(encoding="utf-8").splitlines() if line)}
    jobs = []
    for line in args.validation.read_text(encoding="utf-8").splitlines():
        validation_record = json.loads(line)
        status = validation_record["validation"]["status"]
        if status == "trigger_pass":
            continue
        key = (validation_record["case_id"], validation_record["repetition"])
        previous_record = responses[key]
        previous_answer = json.loads(previous_record["content"])
        base = g4_jobs[key[0]]["user"]
        detail = validation_record["validation"]
        feedback = {
            "local_validation_status": status,
            "compilation_stderr": compact((detail.get("compilation") or {}).get("stderr")),
            "compilation_stdout": compact((detail.get("compilation") or {}).get("stdout")),
            "trigger_test_stdout": compact((detail.get("trigger_test") or {}).get("stdout")),
            "trigger_test_stderr": compact((detail.get("trigger_test") or {}).get("stderr")),
        }
        jobs.append(
            {
                "experiment_group": "G5_repair_validation_feedback",
                "origin_repetition": key[1],
                "system": """You are revising a Java repair after an isolated local validation rejected the previous patch. Use only the observed failure, selected localization, previous patch, validation feedback, and original production file. Return valid JSON only:
{
  "patches": [
    {"file": "the supplied production file", "start_line": 0, "end_line": 0, "replacement": "exact Java source replacing the inclusive line range"}
  ],
  "mechanism_summary": "...",
  "uncertainty": "..."
}
Do not modify tests or files outside the supplied production file. Use non-overlapping patches if necessary. Each replacement must contain complete compiling Java lines. Do not claim access to a fixed version or reference patch.""",
                "user": {
                    "case_id": key[0],
                    "observed_failure": base["observed_failure"],
                    "selected_localization": base["selected_localization"],
                    "previous_patch": previous_answer.get("patches"),
                    "validation_feedback": feedback,
                    "production_file": base["production_file"],
                },
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(job, ensure_ascii=False) + "\n" for job in jobs), encoding="utf-8")
    print(f"Wrote {len(jobs)} G5 validation-feedback jobs")


if __name__ == "__main__":
    main()
