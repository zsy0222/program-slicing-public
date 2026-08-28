"""Build blinded DeepSeek jobs for the JacksonCore 4 natural-failure pilot.

The job builder deliberately excludes Defects4J metadata identifying the
modified class, the fixed version, and every reference patch.  The only
evidence supplied to the model is the reproduced failure, the failing test,
and the context assigned to its experimental group.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = ROOT / "04_formal_tools" / "Slicer4J" / "benchmarks" / "JacksonCore_4b"
SLICE_PATH = ROOT / "03_experiments" / "outputs" / "jacksoncore_4b_failure_slice_2026-08-23" / "slice.log"
OUTPUT_PATH = ROOT / "03_experiments" / "outputs" / "jacksoncore_4b_failure_slice_2026-08-23" / "deepseek_jobs.jsonl"


BASE_SYSTEM = """You are debugging a Java program from an observed failing JUnit test.
Use only the supplied material. Do not claim access to Defects4J metadata, a
fixed version, a reference patch, or any other execution trace. Return valid
JSON only with this schema:
{
  \"candidates\": [
    {
      \"file\": \"relative Java source file\",
      \"line\": 0,
      \"role\": \"fault_origin|error_mechanism|control_enabler|context\",
      \"proposed_change\": \"concise code change, or empty string\",
      \"reason\": \"why this location explains the observed failure\",
      \"confidence\": 0.0
    }
  ],
  \"mechanism_summary\": \"...\",
  \"uncertainty\": \"...\"
}
Rank at most three candidate source locations. A fault_origin is a plausible
developer edit, whereas an error_mechanism may only explain how the failure is
reached. Keep these roles distinct."""


CONTRACT_SUFFIX = """

For every candidate add \"evidence_refs\", a nonempty list of identifiers
from the supplied sliced_source_lines. Every mechanism statement must be
supported by those cited lines. If the supplied evidence does not establish a
unique repair, retain the ambiguity instead of inventing a fix."""


def numbered(path: Path, start: int = 1, end: int | None = None) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    end = end or len(lines)
    return "\n".join(f"{path.relative_to(CASE_DIR)}:{number}: {lines[number - 1]}" for number in range(start, end + 1))


def source_path(qualified_class: str) -> Path:
    relative = Path(*qualified_class.split(".")) .with_suffix(".java")
    for root in (CASE_DIR / "src" / "main" / "java", CASE_DIR / "src" / "test" / "java"):
        candidate = root / relative
        if candidate.exists():
            return candidate
    raise FileNotFoundError(qualified_class)


def dynamic_slice_lines() -> list[dict]:
    seen: set[tuple[str, int]] = set()
    items: list[dict] = []
    for raw in SLICE_PATH.read_text(encoding="utf-8").splitlines():
        qualified, raw_line = raw.rsplit(":", 1)
        line = int(raw_line)
        if line < 1 or (qualified, line) in seen:
            continue
        seen.add((qualified, line))
        path = source_path(qualified)
        text = path.read_text(encoding="utf-8").splitlines()[line - 1]
        items.append(
            {
                "id": f"S{len(items) + 1}",
                "file": str(path.relative_to(CASE_DIR)),
                "line": line,
                "code": text,
            }
        )
    return items


def job(group: str, context: dict, system: str = BASE_SYSTEM) -> dict:
    return {
        "experiment_group": group,
        "system": system,
        "user": {
            "case_id": "JacksonCore_4b",
            "observed_failure": "TestTextBuffer.testExpand fails: Expected buffer of 262145 to expand, did not, length now 262144.",
            "failing_test_source": numbered(
                CASE_DIR / "src" / "test" / "java" / "com" / "fasterxml" / "jackson" / "core" / "util" / "TestTextBuffer.java",
                67,
                79,
            ),
            **context,
        },
    }


def main() -> None:
    text_buffer = CASE_DIR / "src" / "main" / "java" / "com" / "fasterxml" / "jackson" / "core" / "util" / "TextBuffer.java"
    slice_lines = dynamic_slice_lines()
    jobs = [
        job(
            "G1_pure_llm_full_class",
            {
                "context_scope": "The complete failing production class is supplied below.",
                "full_production_class": numbered(text_buffer),
            },
        ),
        job(
            "G2_pure_llm_dynamic_slice",
            {
                "context_scope": "Only source positions selected by a backward dynamic slice from the failing test line are supplied below.",
                "sliced_source_lines": slice_lines,
            },
        ),
        job(
            "G3_slice_with_evidence_contract",
            {
                "context_scope": "Only source positions selected by a backward dynamic slice from the failing test line are supplied below.",
                "sliced_source_lines": slice_lines,
            },
            BASE_SYSTEM + CONTRACT_SUFFIX,
        ),
    ]
    OUTPUT_PATH.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in jobs) + "\n", encoding="utf-8")
    print(f"Wrote {len(jobs)} blinded jobs to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
