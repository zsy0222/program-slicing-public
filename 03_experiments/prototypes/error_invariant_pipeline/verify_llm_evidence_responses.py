"""Apply the evidence contract to all saved G5/G6 LLM responses locally."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from verify_evidence_contract import verify


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--trajectory-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    checked = []
    for line in args.responses.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        record = json.loads(line)
        result = {
            "case_id": record["case_id"],
            "repetition": record["repetition"],
            "response_status": record["status"],
        }
        if record["status"] == "completed":
            try:
                response = json.loads(record["content"])
                trajectory = json.loads(
                    (args.trajectory_dir / f"{record['case_id']}.json").read_text(encoding="utf-8")
                )
                result.update(verify(trajectory, response))
            except (KeyError, json.JSONDecodeError, OSError) as error:
                result.update({"valid": False, "violations": [f"unreadable_response:{error}"], "feedback_for_next_round": "Return valid JSON."})
        else:
            result.update({"valid": False, "violations": ["model_not_completed"], "feedback_for_next_round": "Retry the model response."})
        checked.append(result)

    summary = {
        "records": checked,
        "valid_records": sum(item["valid"] for item in checked),
        "invalid_records": sum(not item["valid"] for item in checked),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
