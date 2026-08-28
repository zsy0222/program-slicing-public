"""Score G1--G3 localization only after all model requests have completed."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


# Derived offline from the fixed-vs-buggy upstream diffs.  These locations are
# intentionally not present in any DeepSeek job builder.
REFERENCE_REGIONS = {
    "JacksonDatabind_3b": {
        "file": "src/main/java/com/fasterxml/jackson/databind/deser/std/StringArrayDeserializer.java",
        "lines": {66},
    },
    "Gson_4b_reader": {
        "file": "src/main/java/com/google/gson/stream/JsonReader.java",
        "lines": set(range(571, 588)),
    },
    "Gson_4b_writer": {
        "file": "src/main/java/com/google/gson/stream/JsonWriter.java",
        "lines": set(range(315, 525)) | set(range(608, 627)),
    },
}


def parse_json(content: str) -> tuple[dict | None, bool]:
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


def is_reference_site(case_id: str, candidate: dict) -> bool:
    oracle = REFERENCE_REGIONS[case_id]
    return candidate.get("file") == oracle["file"] and candidate.get("line") in oracle["lines"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    records = [json.loads(line) for line in args.responses.read_text(encoding="utf-8").splitlines() if line]
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for record in records:
        if record.get("status") != "completed":
            continue
        parsed, strict = parse_json(record.get("content", ""))
        candidates = parsed.get("candidates", []) if parsed else []
        top = candidates[0] if candidates else {}
        grouped[(record["case_id"], record["experiment_group"])].append(
            {
                "repetition": record["repetition"],
                "strict_json": strict,
                "parseable_json": parsed is not None,
                "top1_reference_region": is_reference_site(record["case_id"], top),
                "top3_reference_region": any(is_reference_site(record["case_id"], item) for item in candidates[:3]),
                "all_candidates_have_evidence": bool(candidates) and all(item.get("evidence_refs") for item in candidates),
                "top_candidate": top,
                "total_tokens": (record.get("usage") or {}).get("total_tokens") or 0,
                "elapsed_seconds": record.get("elapsed_seconds") or 0,
            }
        )

    summary: dict[str, dict] = {}
    for (case_id, group), runs in sorted(grouped.items()):
        count = len(runs)
        summary[f"{case_id}/{group}"] = {
            "runs": count,
            "strict_json_valid": sum(run["strict_json"] for run in runs),
            "parseable_json": sum(run["parseable_json"] for run in runs),
            "top1_reference_region": sum(run["top1_reference_region"] for run in runs),
            "top3_reference_region": sum(run["top3_reference_region"] for run in runs),
            "all_candidates_have_evidence": sum(run["all_candidates_have_evidence"] for run in runs),
            "mean_total_tokens": round(sum(run["total_tokens"] for run in runs) / count, 1),
            "mean_elapsed_seconds": round(sum(run["elapsed_seconds"] for run in runs) / count, 3),
        }
    serializable_runs = {f"{case_id}/{group}": runs for (case_id, group), runs in grouped.items()}
    payload = {"reference_regions": {key: {"file": value["file"], "lines": sorted(value["lines"])} for key, value in REFERENCE_REGIONS.items()}, "summary": summary, "runs": serializable_runs}
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
