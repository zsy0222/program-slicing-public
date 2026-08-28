"""Build blinded A--D repair jobs for the Gson-6b and Gson-7b Defects4J cases."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "03_experiments" / "outputs" / "defects4j_comparison_2026-08-27"
INPUTS = OUT / "inputs"


def numbered(path: Path) -> str:
    return "\n".join(f"{path.name}:{i}: {line}" for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1))


SYSTEM = """You are repairing one Java production source file from an observed failing test. Use only supplied evidence. Do not claim access to Defects4J metadata, a fixed version, reference patch, or hidden tests. Do not modify tests. Return valid JSON only:
{
  "patches": [{"file": "exact supplied file name", "start_line": 0, "end_line": 0, "replacement": "complete replacement Java lines"}],
  "mechanism_summary": "...",
  "uncertainty": "..."
}
Patches must be minimal, non-overlapping, and confined to the supplied production file."""


CASES = (
    {
        "case_id": "Gson_6b_d4j",
        "file": "gson/src/main/java/com/google/gson/internal/bind/JsonAdapterAnnotationTypeAdapterFactory.java",
        "source": INPUTS / "gson6_production.java",
        "failure": "JsonAdapterNullSafeTest.testNullSafeBugDeserialize throws NullPointerException at JsonAdapterAnnotationTypeAdapterFactory.getTypeAdapter line 68. The factory path invoked from Gson.getDelegateAdapter returns an adapter used for deserialization.",
        "static_range": (50, 69),
        "dynamic": [
            "S1 JsonAdapterAnnotationTypeAdapterFactory:43-47: @JsonAdapter is detected and getTypeAdapter(...) is called.",
            "S2 JsonAdapterAnnotationTypeAdapterFactory:61-62: a TypeAdapterFactory is constructed and create(gson, fieldType) produces typeAdapter.",
            "S3 JsonAdapterAnnotationTypeAdapterFactory:68: typeAdapter.nullSafe() is invoked on the observed failing path.",
            "S4 JsonAdapterNullSafeTest: the factory deliberately returns null on a recursive call.",
        ],
        "invariant": "Observed path constraint: before invoking typeAdapter.nullSafe(), typeAdapter must be non-null; an absent adapter must remain representable to the caller.",
        "scope": "Edit only lines 53-68 of the supplied class; preserve the public method signature and existing exception behavior.",
    },
    {
        "case_id": "Gson_7b_d4j",
        "file": "gson/src/main/java/com/google/gson/stream/JsonReader.java",
        "source": INPUTS / "gson7_production.java",
        "failure": "MapTest.testMapDeserializationWithUnquotedLongKeys throws IllegalStateException at JsonReader.nextLong line 965: an unquoted numeric map key is reported as STRING instead of being parsed as a long.",
        "static_range": (939, 979),
        "dynamic": [
            "S1 JsonReader:940-943: p is obtained from the current token via doPeek().",
            "S2 JsonReader:951-954: numeric and quoted token categories select parsing behavior.",
            "S3 JsonReader:965: the observed token reaches the IllegalStateException branch.",
            "S4 TypeAdapters$11:325: Map key deserialization calls JsonReader.nextLong().",
        ],
        "invariant": "Observed path constraint: a syntactically valid unquoted integer token must reach the integer/long parsing path rather than the token-type exception branch.",
        "scope": "Edit only lines 939-979 of the supplied class; preserve behavior for invalid and non-numeric tokens.",
    },
)


def section(source: Path, start: int, end: int) -> str:
    lines = source.read_text(encoding="utf-8").splitlines()
    return "\n".join(f"{source.name}:{i}: {lines[i - 1]}" for i in range(start, end + 1))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for case in CASES:
        full = numbered(case["source"])
        static = section(case["source"], *case["static_range"])
        common = {"case_id": case["case_id"], "observed_failure": case["failure"], "production_file": case["file"]}
        variants = [
            ("A_pure_llm_full_context", {"context": "Complete production class.", "source": full}),
            ("B_llm_static_local_context", {"context": "Static local source window centered on the failing stack location.", "source": static}),
            ("C_llm_dynamic_semantic_slice", {"context": "Dynamic semantic slice from the failing execution; entries are observed dependency facts.", "dynamic_slice": case["dynamic"]}),
            ("D_full_workflow", {"context": "Dynamic semantic slice plus an executable error invariant and constrained edit scope.", "dynamic_slice": case["dynamic"], "error_invariant": case["invariant"], "edit_scope": case["scope"]}),
        ]
        for group, evidence in variants:
            # C/D receive the relevant class window too, so a patch can be expressed;
            # the window is restricted to locations named by the slice/invariant.
            if group in {"C_llm_dynamic_semantic_slice", "D_full_workflow"}:
                evidence["source"] = static
            jobs.append({"experiment_group": group, "system": SYSTEM, "user": {**common, **evidence}})
    (OUT / "jobs.jsonl").write_text("".join(json.dumps(j, ensure_ascii=False) + "\n" for j in jobs), encoding="utf-8")
    (OUT / "protocol.json").write_text(json.dumps({"cases": [c["case_id"] for c in CASES], "groups": ["A", "B", "C", "D"], "repetitions": 3, "model": "deepseek-v4-flash", "temperature": 0.0}, indent=2), encoding="utf-8")
    print(f"Wrote {len(jobs)} jobs")


if __name__ == "__main__":
    main()
