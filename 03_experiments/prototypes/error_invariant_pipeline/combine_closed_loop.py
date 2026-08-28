"""Keep accepted G5 answers and replace rejected ones with their G6 revision."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g5-responses", required=True, type=Path)
    parser.add_argument("--verification", required=True, type=Path)
    parser.add_argument("--g6-responses", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    checks = {(item["case_id"], item["repetition"]): item for item in json.loads(args.verification.read_text(encoding="utf-8"))["records"]}
    revisions = {}
    for line in args.g6_responses.read_text(encoding="utf-8").splitlines():
        if line:
            record = json.loads(line)
            revisions[(record["case_id"], record["origin_repetition"])] = record

    final_records = []
    for line in args.g5_responses.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        original = json.loads(line)
        key = (original["case_id"], original["repetition"])
        if checks[key]["valid"]:
            original["experiment_group"] = "G6_evidence_feedback_llm"
            original["closed_loop_action"] = "accepted_initial"
            final_records.append(original)
        else:
            revised = revisions[key]
            revised["closed_loop_action"] = "revised_after_feedback"
            final_records.append(revised)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in final_records), encoding="utf-8")
    print(f"G6 final records: {len(final_records)}")


if __name__ == "__main__":
    main()
