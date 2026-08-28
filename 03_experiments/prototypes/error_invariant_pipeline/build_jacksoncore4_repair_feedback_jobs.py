"""Build validation-feedback repair jobs without disclosing the reference fix."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "03_experiments" / "outputs" / "jacksoncore_4b_failure_slice_2026-08-23"
INPUT = OUT_DIR / "deepseek_repair_raw.jsonl"
OUTPUT = OUT_DIR / "deepseek_repair_feedback_jobs.jsonl"
SOURCE = ROOT / "04_formal_tools" / "Slicer4J" / "benchmarks" / "JacksonCore_4b" / "src" / "main" / "java" / "com" / "fasterxml" / "jackson" / "core" / "util" / "TextBuffer.java"


def method_region() -> str:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    return "\n".join(f"src/main/java/com/fasterxml/jackson/core/util/TextBuffer.java:{number}: {lines[number - 1]}" for number in range(580, 589))


def main() -> None:
    system = """You are revising a Java repair after local validation rejected the
previous patch. Use only the supplied failure, previous patch, validation
feedback, and method region. Do not assume a reference patch exists. Return
valid JSON only:
{
  \"patch\": {
    \"file\": \"src/main/java/com/fasterxml/jackson/core/util/TextBuffer.java\",
    \"start_line\": 0,
    \"end_line\": 0,
    \"replacement\": \"exact Java source replacing the inclusive line range\"
  },
  \"mechanism_summary\": \"...\",
  \"uncertainty\": \"...\"
}
Do not modify tests. Return an exact compiling replacement, not prose."""
    jobs = []
    for record in (json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line):
        previous = json.loads(record["content"])["patch"]
        jobs.append(
            {
                "experiment_group": "G5_repair_validation_feedback",
                "origin_repetition": record["repetition"],
                "system": system,
                "user": {
                    "case_id": "JacksonCore_4b",
                    "observed_failure": "TestTextBuffer.testExpand fails: Expected buffer of 262145 to expand, did not, length now 262144.",
                    "previous_patch": previous,
                    "validation_feedback": "The previous patch compiled, but the original failing test still failed. The failure means old.length was 262145 and the next expandCurrentSegment() returned a buffer of length 262144. Revise the patch to prevent that observed transition.",
                    "method_region": method_region(),
                },
            }
        )
    OUTPUT.write_text("\n".join(json.dumps(job, ensure_ascii=False) for job in jobs) + "\n", encoding="utf-8")
    print(f"Wrote {len(jobs)} feedback jobs to {OUTPUT}")


if __name__ == "__main__":
    main()
