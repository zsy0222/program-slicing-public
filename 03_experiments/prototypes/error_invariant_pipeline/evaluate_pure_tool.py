"""Evaluate the deterministic Error-Invariants-only baseline on labelled cases."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--run-status", required=True, type=Path)
    parser.add_argument("--trajectory-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    with args.manifest.open(newline="", encoding="utf-8") as file:
        labels = {row["case_id"]: row for row in csv.DictReader(file)}
    with args.run_status.open(newline="", encoding="utf-8") as file:
        statuses = list(csv.DictReader(file))

    rows = []
    completed = []
    for status in statuses:
        case_id = status["case_id"]
        label = labels[case_id]
        row = {
            "case_id": case_id,
            "analysis_status": status["analysis_status"],
            "ground_truth_location": int(label["ground_truth_analyzer_location"]),
        }
        if status["analysis_status"] == "completed":
            trajectory_path = args.trajectory_dir / f"{case_id}.json"
            trajectory = json.loads(trajectory_path.read_text(encoding="utf-8"))
            ranking = [item["location_id"] for item in trajectory["pure_tool_baseline"]["candidates"]]
            row["ranking"] = ranking
            row["top_1_hit"] = row["ground_truth_location"] in ranking[:1]
            row["top_3_hit"] = row["ground_truth_location"] in ranking[:3]
            completed.append(row)
        else:
            row["ranking"] = []
            row["top_1_hit"] = None
            row["top_3_hit"] = None
            row["failure_reason"] = status["reason"]
        rows.append(row)

    summary = {
        "baseline": "G1 Error Invariants only: direct-write-to-error-variable ranking",
        "total_labelled_cases": len(rows),
        "completed_analysis_cases": len(completed),
        "analysis_coverage": len(completed) / len(rows) if rows else 0,
        "top_1_on_completed_cases": (
            sum(row["top_1_hit"] for row in completed) / len(completed) if completed else None
        ),
        "top_3_on_completed_cases": (
            sum(row["top_3_hit"] for row in completed) / len(completed) if completed else None
        ),
        "cases": rows,
    }
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
