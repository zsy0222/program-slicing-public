"""Select one contract-valid Top-1 V2 candidate per case by majority vote."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def candidate_key(candidate: dict) -> tuple[int, str, str]:
    return (
        int(candidate.get("source_line", 0)),
        str(candidate.get("proposed_replacement", "")).strip(),
        str(candidate.get("role", "")),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--verification", required=True, type=Path)
    parser.add_argument("--patch-validation", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    valid_keys = {
        (item["case_id"], item["repetition"])
        for item in json.loads(args.verification.read_text(encoding="utf-8"))["records"]
        if item.get("valid")
    }
    grouped: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    for line in args.responses.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        record = json.loads(line)
        key = (record.get("case_id"), record.get("repetition"))
        if key not in valid_keys or record.get("status") != "completed":
            continue
        answer = json.loads(record["content"])
        candidates = answer.get("candidates", [])
        if candidates and isinstance(candidates[0], dict):
            grouped[record["case_id"]].append((int(record["repetition"]), candidates[0]))

    validations: dict[tuple[str, int, str], list[dict]] = defaultdict(list)
    for line in args.patch_validation.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        record = json.loads(line)
        candidate = record.get("candidate", {})
        validations[(record["case_id"], int(candidate.get("source_line", 0)), str(candidate.get("proposed_replacement", "")).strip())].append(record)

    selections = []
    for case_id in sorted(grouped):
        votes: dict[tuple[int, str, str], list[tuple[int, dict]]] = defaultdict(list)
        for repetition, candidate in grouped[case_id]:
            key = candidate_key(candidate)
            if key[0] > 0 and key[1]:
                votes[key].append((repetition, candidate))
        if not votes:
            selections.append({"case_id": case_id, "selection_status": "no_usable_valid_top1"})
            continue
        ranked = sorted(
            votes.items(),
            key=lambda item: (
                -len(item[1]),
                -sum(float(vote[1].get("confidence", 0)) for vote in item[1]) / len(item[1]),
                min(vote[0] for vote in item[1]),
                item[0][0],
            ),
        )
        (line_number, replacement, role), vote_records = ranked[0]
        validation_records = validations.get((case_id, line_number, replacement), [])
        validation_statuses = [record["validation"]["status"] for record in validation_records]
        selections.append(
            {
                "case_id": case_id,
                "selection_status": "selected",
                "source_line": line_number,
                "proposed_replacement": replacement,
                "role": role,
                "supporting_repetitions": [repetition for repetition, _ in vote_records],
                "vote_count": len(vote_records),
                "eligible_contract_repetitions": len(grouped[case_id]),
                "mean_confidence": round(
                    sum(float(candidate.get("confidence", 0)) for _, candidate in vote_records) / len(vote_records), 3
                ),
                "runtime_validation_statuses": validation_statuses,
                "runtime_validated": "validated_by_runtime" in validation_statuses,
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "selection_rule": "contract-valid Top-1 majority vote; ties by mean confidence, earliest repetition, then source line",
                "selections": selections,
            },
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"Selected cases: {sum(item['selection_status'] == 'selected' for item in selections)}")


if __name__ == "__main__":
    main()
