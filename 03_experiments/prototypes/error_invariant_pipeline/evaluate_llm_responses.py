"""Evaluate saved LLM response records without making any network requests."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def candidate_field(group: str) -> str:
    return "source_line" if group in {"G2_source_only_llm", "G3_slice_aware_llm"} else "analysis_location"


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
        group = record["experiment_group"]
        row = {key: record.get(key) for key in ("case_id", "repetition", "status", "elapsed_seconds")}
        if record.get("status") != "completed":
            row["parse_status"] = "not_completed"
            grouped[group].append(row)
            continue
        try:
            answer = json.loads(record["content"])
            field = candidate_field(group)
            ranking = [item[field] for item in answer.get("ranked_candidates", []) if isinstance(item.get(field), int)]
            label_field = "faulty_source_line" if field == "source_line" else "ground_truth_analyzer_location"
            label = int(labels[record["case_id"]][label_field])
            row.update(
                {
                    "parse_status": "valid_json",
                    "ranking": ranking,
                    "top_1_hit": label in ranking[:1],
                    "top_3_hit": label in ranking[:3],
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
            "records": rows,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
