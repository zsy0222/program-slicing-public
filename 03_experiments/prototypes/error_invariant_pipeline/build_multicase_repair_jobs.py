"""Build G4 repair tasks from the completed, blinded G3 localizations."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def parse_json(content: str) -> dict | None:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(content[start : end + 1])
            except json.JSONDecodeError:
                pass
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--localization-jobs", required=True, type=Path)
    parser.add_argument("--localization-responses", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    full_context: dict[str, dict] = {}
    for line in args.localization_jobs.read_text(encoding="utf-8").splitlines():
        job = json.loads(line)
        if job["experiment_group"] == "G1_pure_llm_full_class":
            full_context[job["user"]["case_id"]] = job["user"]

    choices: dict[str, list[dict]] = {}
    for line in args.localization_responses.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("status") != "completed" or record.get("experiment_group") != "G3_slice_with_evidence_contract":
            continue
        parsed = parse_json(record.get("content", ""))
        candidates = parsed.get("candidates", []) if parsed else []
        if candidates:
            choices.setdefault(record["case_id"], []).append(candidates[0])

    jobs: list[dict] = []
    selected: dict[str, dict] = {}
    for case_id, context in full_context.items():
        candidates = choices.get(case_id, [])
        if not candidates:
            raise ValueError(f"No completed G3 candidate for {case_id}")
        counter = Counter((candidate.get("file"), candidate.get("line")) for candidate in candidates)
        file_name, line_number = counter.most_common(1)[0][0]
        winner = next(candidate for candidate in candidates if (candidate.get("file"), candidate.get("line")) == (file_name, line_number))
        selected[case_id] = winner
        system = """You are the repair stage of a Java debugging workflow. A prior blinded localization stage selected a source location from a natural-failure dynamic slice. Use only the observed failure, the selected location, and the supplied original production class. Return valid JSON only:
{
  "patches": [
    {"file": "the supplied production file", "start_line": 0, "end_line": 0, "replacement": "exact Java source replacing the inclusive line range"}
  ],
  "mechanism_summary": "...",
  "uncertainty": "..."
}
Do not modify tests or files outside the supplied production file. Use one or more non-overlapping patches when necessary. Each replacement must contain all required Java lines, not a prose description. Do not claim access to a fixed version or reference patch."""
        user = {
            "case_id": case_id,
            "observed_failure": context["observed_failure"],
            "selected_localization": winner,
            "production_file": context["full_production_class"],
        }
        jobs.append({"experiment_group": "G4_slice_locate_repair", "system": system, "user": user})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(job, ensure_ascii=False) + "\n" for job in jobs), encoding="utf-8")
    args.output.with_suffix(".selected_locations.json").write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(jobs)} G4 repair jobs")


if __name__ == "__main__":
    main()
