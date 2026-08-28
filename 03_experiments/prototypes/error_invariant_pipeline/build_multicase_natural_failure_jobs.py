"""Build blinded G1--G3 localization tasks for the new natural-failure cases.

The held-out reference change is deliberately absent from every generated job.
Only the original failing-test evidence and the designated group context are
written to disk.  This script performs no network request.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "03_experiments" / "outputs" / "multicase_natural_failure_g1_g3_2026-08-23"
OUT_PATH = OUT_DIR / "deepseek_localization_jobs.jsonl"


BASE_SYSTEM = """You are debugging a Java program from an observed failing JUnit test.
Use only the supplied material. Do not claim access to Defects4J metadata, a
fixed version, a reference patch, or any other execution trace. Return valid
JSON only with this schema:
{
  "candidates": [
    {
      "file": "relative Java source file",
      "line": 0,
      "role": "fault_origin|error_mechanism|control_enabler|context",
      "proposed_change": "concise code change, or empty string",
      "reason": "why this location explains the observed failure",
      "confidence": 0.0
    }
  ],
  "mechanism_summary": "...",
  "uncertainty": "..."
}
Rank at most three candidate source locations. A fault_origin is a plausible
developer edit, whereas an error_mechanism may only explain how the failure is
reached. Keep these roles distinct."""


CONTRACT_SUFFIX = """

For every candidate add "evidence_refs", a nonempty list of identifiers from
the supplied sliced_source_lines. Every mechanism statement must be supported
by those cited lines. If the supplied evidence does not establish a unique
repair, retain the ambiguity instead of inventing a fix."""


CASES = (
    {
        "case_id": "JacksonDatabind_3b",
        "case_dir": ROOT / "04_formal_tools" / "Slicer4J" / "benchmarks" / "JacksonDatabind_3b",
        "slice_dir": ROOT / "03_experiments" / "outputs" / "jacksondatabind_3b_minimal_dynamic_slice_2026-08-23",
        "production_class": "com.fasterxml.jackson.databind.deser.std.StringArrayDeserializer",
        "test_class": "com.fasterxml.jackson.databind.deser.TestArrayDeserialization",
        "test_start": 156,
        "test_end": 170,
        "observed_failure": "TestArrayDeserialization.testStringArray fails with NullPointerException: _elementDeserializer is null and getNullValue() is invoked.",
    },
    {
        "case_id": "Gson_4b_reader",
        "case_dir": ROOT / "04_formal_tools" / "Slicer4J" / "benchmarks" / "Gson_4b" / "gson",
        "slice_dir": ROOT / "03_experiments" / "outputs" / "gson_4b_reader_minimal_dynamic_slice_2026-08-23",
        "production_class": "com.google.gson.stream.JsonReader",
        "test_class": "com.google.gson.stream.JsonReaderTest",
        "test_start": 1218,
        "test_end": 1230,
        "observed_failure": "JsonReaderTest.testTopLevelValueTypes fails with MalformedJsonException: Use JsonReader.setLenient(true) to accept malformed JSON at line 1 column 1 path $.",
    },
    {
        "case_id": "Gson_4b_writer",
        "case_dir": ROOT / "04_formal_tools" / "Slicer4J" / "benchmarks" / "Gson_4b" / "gson",
        "slice_dir": ROOT / "03_experiments" / "outputs" / "gson_4b_writer_minimal_dynamic_slice_2026-08-23",
        "production_class": "com.google.gson.stream.JsonWriter",
        "test_class": "com.google.gson.stream.JsonWriterTest",
        "test_start": 24,
        "test_end": 39,
        "observed_failure": "JsonWriterTest.testTopLevelValueTypes fails with IllegalStateException: JSON must start with an array or an object.",
    },
)


def source_path(case_dir: Path, qualified_class: str) -> Path:
    relative = Path(*qualified_class.split(".")).with_suffix(".java")
    for root in (case_dir / "src" / "main" / "java", case_dir / "src" / "test" / "java"):
        candidate = root / relative
        if candidate.exists():
            return candidate
    raise FileNotFoundError(qualified_class)


def numbered(case_dir: Path, path: Path, start: int = 1, end: int | None = None) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    last = end or len(lines)
    relative = path.relative_to(case_dir)
    return "\n".join(f"{relative}:{number}: {lines[number - 1]}" for number in range(start, last + 1))


def dynamic_slice_lines(case: dict) -> list[dict]:
    csv_path = next(case["slice_dir"].glob("result_s_*.csv"))
    seen: set[tuple[str, int]] = set()
    items: list[dict] = []
    with csv_path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            qualified = row[" Class"].strip()
            # Slicer4J emits the Jimple statement before the source line even
            # though its CSV header labels those two columns in the reverse
            # order.  The numeric source position is therefore in `Source`.
            line = int(row[" Source"].strip())
            key = (qualified, line)
            if line < 1 or key in seen:
                continue
            seen.add(key)
            path = source_path(case["case_dir"], qualified)
            source = path.read_text(encoding="utf-8").splitlines()[line - 1]
            items.append(
                {
                    "id": f"S{len(items) + 1}",
                    "file": str(path.relative_to(case["case_dir"])),
                    "line": line,
                    "code": source,
                }
            )
    return items


def build_job(case: dict, group: str, context: dict, system: str = BASE_SYSTEM) -> dict:
    test_path = source_path(case["case_dir"], case["test_class"])
    return {
        "experiment_group": group,
        "system": system,
        "user": {
            "case_id": case["case_id"],
            "observed_failure": case["observed_failure"],
            "failing_test_source": numbered(case["case_dir"], test_path, case["test_start"], case["test_end"]),
            **context,
        },
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    jobs: list[dict] = []
    manifest: list[dict] = []
    for case in CASES:
        production_path = source_path(case["case_dir"], case["production_class"])
        slice_lines = dynamic_slice_lines(case)
        jobs.extend(
            (
                build_job(
                    case,
                    "G1_pure_llm_full_class",
                    {
                        "context_scope": "The complete failing production class is supplied below.",
                        "full_production_class": numbered(case["case_dir"], production_path),
                    },
                ),
                build_job(
                    case,
                    "G2_pure_llm_dynamic_slice",
                    {
                        "context_scope": "Only source positions selected by a backward dynamic slice from the natural failure are supplied below.",
                        "sliced_source_lines": slice_lines,
                    },
                ),
                build_job(
                    case,
                    "G3_slice_with_evidence_contract",
                    {
                        "context_scope": "Only source positions selected by a backward dynamic slice from the natural failure are supplied below.",
                        "sliced_source_lines": slice_lines,
                    },
                    BASE_SYSTEM + CONTRACT_SUFFIX,
                ),
            )
        )
        manifest.append(
            {
                "case_id": case["case_id"],
                "production_class": case["production_class"],
                "slice_source_lines": len(slice_lines),
                "slice_csv": str(next(case["slice_dir"].glob("result_s_*.csv"))),
            }
        )
    OUT_PATH.write_text("".join(json.dumps(job, ensure_ascii=False) + "\n" for job in jobs), encoding="utf-8")
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(jobs)} blinded localization jobs to {OUT_PATH}")


if __name__ == "__main__":
    main()
