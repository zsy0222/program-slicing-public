"""Verify saved P-V2a/P-V2b LLM records without making network requests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from verify_v2_contract import verify


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", required=True, type=Path)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    jobs = {
        json.loads(line)["user"]["case_id"]: json.loads(line)
        for line in args.jobs.read_text(encoding="utf-8").splitlines()
        if line
    }
    records = []
    for line in args.responses.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        response_record = json.loads(line)
        result = {
            "case_id": response_record.get("case_id"),
            "repetition": response_record.get("repetition"),
            "experiment_group": response_record.get("experiment_group"),
        }
        job = jobs.get(response_record.get("case_id"))
        if response_record.get("status") != "completed" or job is None:
            result.update({"valid": False, "violations": ["response_not_completed_or_job_missing"]})
        else:
            try:
                answer = json.loads(response_record["content"])
                result.update(
                    verify(
                        job["user"], answer, job["experiment_group"].startswith("P_V2b")
                    )
                )
            except (KeyError, TypeError, json.JSONDecodeError) as error:
                result.update({"valid": False, "violations": [f"invalid_json_response: {error}"]})
        records.append(result)
    summary = {
        "records": records,
        "valid_count": sum(item["valid"] for item in records),
        "total_count": len(records),
        "valid_rate": sum(item["valid"] for item in records) / len(records) if records else None,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("valid_count", "total_count", "valid_rate")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
