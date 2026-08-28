"""Evaluate V2 candidate locations and causal-role labels using held-out labels."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with args.manifest.open(newline="", encoding="utf-8") as file:
        labels = {row["case_id"]: row for row in csv.DictReader(file)}
    grouped: dict[str, list[dict]] = defaultdict(list)
    for line in args.responses.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        record = json.loads(line)
        row = {key: record.get(key) for key in ("case_id", "repetition", "status", "elapsed_seconds")}
        group = record.get("experiment_group", "unknown")
        try:
            answer = json.loads(record["content"])
            candidates = answer.get("candidates", [])
            ranking = [item["source_line"] for item in candidates if isinstance(item.get("source_line"), int)]
            label = int(labels[record["case_id"]]["faulty_source_line"])
            matching_roles = [
                item.get("role") for item in candidates if item.get("source_line") == label
            ]
            row.update(
                {
                    "parse_status": "valid_json",
                    "ranking": ranking,
                    "top_1_hit": label in ranking[:1],
                    "top_3_hit": label in ranking[:3],
                    "fault_origin_at_true_location": "fault_origin" in matching_roles,
                }
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            row.update({"parse_status": "invalid_response", "parse_error": str(error)})
        grouped[group].append(row)

    summary = {}
    for group, rows in grouped.items():
        valid = [row for row in rows if row.get("parse_status") == "valid_json"]
        summary[group] = {
            "response_records": len(rows),
            "valid_json_records": len(valid),
            "top_1": sum(row["top_1_hit"] for row in valid) / len(valid) if valid else None,
            "top_3": sum(row["top_3_hit"] for row in valid) / len(valid) if valid else None,
            "fault_origin_at_true_location": (
                sum(row["fault_origin_at_true_location"] for row in valid) / len(valid) if valid else None
            ),
            "records": rows,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
