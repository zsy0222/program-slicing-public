"""Build the repair-stage jobs after blinded slice-based localization."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = ROOT / "04_formal_tools" / "Slicer4J" / "benchmarks" / "JacksonCore_4b"
OUTPUT = ROOT / "03_experiments" / "outputs" / "jacksoncore_4b_failure_slice_2026-08-23" / "deepseek_repair_jobs.jsonl"
SOURCE = CASE_DIR / "src" / "main" / "java" / "com" / "fasterxml" / "jackson" / "core" / "util" / "TextBuffer.java"


def numbered(start: int, end: int) -> str:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    return "\n".join(f"src/main/java/com/fasterxml/jackson/core/util/TextBuffer.java:{number}: {lines[number - 1]}" for number in range(start, end + 1))


def main() -> None:
    system = """You are the repair stage of a Java debugging workflow. A prior
blind localization stage selected TextBuffer.java line 586 from a dynamic slice
of the failing test. Use only the observed failure and the supplied method
region. Return valid JSON only:
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
Do not modify tests. The replacement must compile as Java and must contain all
lines required for the repair; do not describe a patch in prose."""
    user = {
        "case_id": "JacksonCore_4b",
        "observed_failure": "TestTextBuffer.testExpand fails: Expected buffer of 262145 to expand, did not, length now 262144.",
        "selected_location": "The localization stage selected line 586 in this method region.",
        "method_region": numbered(580, 588),
    }
    OUTPUT.write_text(json.dumps({"experiment_group": "G4_slice_locate_repair", "system": system, "user": user}, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote repair job to {OUTPUT}")


if __name__ == "__main__":
    main()
