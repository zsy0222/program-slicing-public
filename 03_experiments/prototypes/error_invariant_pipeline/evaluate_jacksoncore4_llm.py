"""Evaluate blinded JacksonCore 4 LLM responses against the held-out fix site."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


FAULT_FILE = "src/main/java/com/fasterxml/jackson/core/util/TextBuffer.java"
FAULT_LINE = 586


def parse_model_json(content: str) -> tuple[dict | None, bool]:
    try:
        return json.loads(content), True
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start < 0 or end <= start:
            return None, False
        try:
            return json.loads(content[start : end + 1]), False
        except json.JSONDecodeError:
            return None, False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    records = [json.loads(line) for line in args.responses.read_text(encoding="utf-8").splitlines() if line]
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        if record.get("status") != "completed":
            continue
        parsed, strict = parse_model_json(record.get("content", ""))
        candidates = parsed.get("candidates", []) if parsed else []
        top = candidates[0] if candidates else {}
        top1 = top.get("file") == FAULT_FILE and top.get("line") == FAULT_LINE
        top3 = any(item.get("file") == FAULT_FILE and item.get("line") == FAULT_LINE for item in candidates[:3])
        groups[record["experiment_group"]].append(
            {
                "repetition": record["repetition"],
                "strict_json": strict,
                "parseable_json": parsed is not None,
                "top1_fault_site": top1,
                "top3_fault_site": top3,
                "top_candidate": top,
                "all_candidates_have_evidence": bool(candidates) and all(item.get("evidence_refs") for item in candidates),
                "total_tokens": (record.get("usage") or {}).get("total_tokens"),
                "elapsed_seconds": record.get("elapsed_seconds"),
            }
        )

    summary = {}
    for name, items in groups.items():
        count = len(items)
        summary[name] = {
            "runs": count,
            "strict_json_valid": sum(item["strict_json"] for item in items),
            "parseable_json": sum(item["parseable_json"] for item in items),
            "top1_fault_site": sum(item["top1_fault_site"] for item in items),
            "top3_fault_site": sum(item["top3_fault_site"] for item in items),
            "all_candidates_have_evidence": sum(item["all_candidates_have_evidence"] for item in items),
            "mean_total_tokens": round(sum(item["total_tokens"] or 0 for item in items) / count, 1),
            "mean_elapsed_seconds": round(sum(item["elapsed_seconds"] or 0 for item in items) / count, 3),
        }

    payload = {
        "case": "JacksonCore_4b",
        "held_out_reference": {
            "fault_file": FAULT_FILE,
            "fault_line": FAULT_LINE,
            "reference_change_summary": "Replace cap-to-MAX length logic with 50% growth, switching to 25% growth once the proposed size exceeds MAX_SEGMENT_LEN.",
        },
        "summary": summary,
        "runs": groups,
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
