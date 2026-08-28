"""Parse completed seeded-suite analyzer logs into V2 evidence trajectories."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from parse_error_invariants import build_trajectory


def optional_int(value: str | None) -> int | None:
    return int(value) if value and value.strip() else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--benchmark-dir", required=True, type=Path)
    parser.add_argument("--run-status", required=True, type=Path)
    parser.add_argument("--analysis-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    cases = list(csv.DictReader(args.manifest.open(newline="", encoding="utf-8")))
    statuses = {
        row["case_id"]: row
        for row in csv.DictReader(args.run_status.open(newline="", encoding="utf-8"))
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, str]] = []
    for case in cases:
        case_id = case["case_id"]
        status = statuses.get(case_id, {})
        output = args.analysis_dir / f"{case_id}_faulty.out"
        if status.get("eligible_for_v2") != "true" or not output.exists():
            records.append({"case_id": case_id, "trajectory_status": "not_eligible"})
            continue
        try:
            trajectory = build_trajectory(
                case_id=case_id,
                source_path=str(args.benchmark_dir / case["faulty_program"]),
                analysis_path=output,
                ground_truth_location_id=optional_int(case.get("ground_truth_analyzer_location")),
                ground_truth_source_line=optional_int(case.get("faulty_source_line")),
                ground_truth_kind=case.get("fault_kind") or None,
            )
            (args.output_dir / f"{case_id}.json").write_text(
                json.dumps(trajectory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            records.append(
                {
                    "case_id": case_id,
                    "trajectory_status": "completed",
                    "error_location_id": str(trajectory["error"]["location_id"]),
                    "error_invariant": trajectory["error"]["error_invariant"],
                }
            )
        except (ValueError, KeyError, IndexError) as error:
            records.append({"case_id": case_id, "trajectory_status": "parse_error", "detail": str(error)})
    with (args.output_dir / "trajectory_status.csv").open("w", newline="", encoding="utf-8") as file:
        columns = ["case_id", "trajectory_status", "error_location_id", "error_invariant", "detail"]
        writer = csv.DictWriter(file, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
    print(f"Completed trajectories: {sum(row['trajectory_status'] == 'completed' for row in records)} / {len(records)}")


if __name__ == "__main__":
    main()
