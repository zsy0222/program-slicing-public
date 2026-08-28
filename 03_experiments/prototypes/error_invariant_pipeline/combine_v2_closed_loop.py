"""Keep valid P-V2b answers and replace rejected ones with one feedback revision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initial-responses", required=True, type=Path)
    parser.add_argument("--verification", required=True, type=Path)
    parser.add_argument("--feedback-responses", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    checks = {
        (item["case_id"], item["repetition"]): item
        for item in json.loads(args.verification.read_text(encoding="utf-8"))["records"]
    }
    revisions = {
        (record["case_id"], record["origin_repetition"]): record
        for line in args.feedback_responses.read_text(encoding="utf-8").splitlines()
        if line
        for record in [json.loads(line)]
        if record.get("status") == "completed"
    }
    final_records = []
    for line in args.initial_responses.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        initial = json.loads(line)
        key = (initial["case_id"], initial["repetition"])
        if checks[key]["valid"]:
            final = initial
            action = "accepted_initial"
        else:
            final = revisions[key]
            action = "revised_after_location_feedback"
        final = {
            **final,
            "repetition": initial["repetition"],
            "experiment_group": "P_V2b_ei_audited_closed_loop",
            "closed_loop_action": action,
        }
        final_records.append(final)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in final_records), encoding="utf-8")
    print(f"P-V2b final records: {len(final_records)}")


if __name__ == "__main__":
    main()
