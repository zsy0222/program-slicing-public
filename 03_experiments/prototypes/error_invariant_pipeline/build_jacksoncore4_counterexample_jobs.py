"""Build counterexample-guided repair jobs from an automatically observed test invariant."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "03_experiments" / "outputs" / "jacksoncore_4b_failure_slice_2026-08-23"
OUTPUT = OUT_DIR / "deepseek_counterexample_repair_jobs.jsonl"
SOURCE = ROOT / "04_formal_tools" / "Slicer4J" / "benchmarks" / "JacksonCore_4b" / "src" / "main" / "java" / "com" / "fasterxml" / "jackson" / "core" / "util" / "TextBuffer.java"


def method_region() -> str:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    return "\n".join(f"src/main/java/com/fasterxml/jackson/core/util/TextBuffer.java:{number}: {lines[number - 1]}" for number in range(580, 589))


def main() -> None:
    system = """You are repairing a Java method after local execution exposed a
counterexample. Use only the observed failure, the automatically extracted
repair constraint, and the method region. Return valid JSON only:
{
  \"patch\": {
    \"file\": \"src/main/java/com/fasterxml/jackson/core/util/TextBuffer.java\",
    \"start_line\": 0,
    \"end_line\": 0,
    \"replacement\": \"exact Java source replacing the inclusive line range\"
  },
  \"constraint_check\": \"why the replacement prevents the supplied counterexample\",
  \"uncertainty\": \"...\"
}
Do not modify tests. The replacement must compile, must include every required
line, and must not allow the output buffer length to be less than or equal to
the input buffer length for the shown counterexample."""
    user = {
        "case_id": "JacksonCore_4b",
        "observed_failure": "TestTextBuffer.testExpand fails: Expected buffer of 262145 to expand, did not, length now 262144.",
        "automatically_extracted_repair_constraint": {
            "semantic_rule": "For an execution of expandCurrentSegment(), returned_buffer.length must be strictly greater than input_buffer.length.",
            "observed_counterexample": {"input_length": 262145, "returned_length": 262144},
            "source_of_rule": "The existing failing JUnit test compares old.length < buf.length; no assertion was added to the project.",
        },
        "method_region": method_region(),
    }
    OUTPUT.write_text(json.dumps({"experiment_group": "G6_counterexample_guided_repair", "system": system, "user": user}, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote counterexample-guided job to {OUTPUT}")


if __name__ == "__main__":
    main()
