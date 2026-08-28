"""Build G6 repair jobs from obligations already asserted by failing tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


CONSTRAINTS = {
    "JacksonDatabind_3b": {
        "semantic_rule": "Deserializing the existing test input ` [ null ]` as String[] must complete without an exception and return a non-null array of length 1 whose only element is null.",
        "observed_counterexample": "The original execution throws NullPointerException before producing the required array because _elementDeserializer is null.",
        "source_of_rule": "Existing TestArrayDeserialization.testStringArray asserts assertNotNull(result), assertEquals(1, result.length), and assertNull(result[0]); no assertion was added.",
    },
    "Gson_4b_reader": {
        "semantic_rule": "For the existing top-level input `true`, JsonReader.nextBoolean() must return true and the following peek() must be END_DOCUMENT without enabling lenient mode.",
        "observed_counterexample": "The original execution throws MalformedJsonException before nextBoolean() can return a value.",
        "source_of_rule": "Existing JsonReaderTest.testTopLevelValueTypes asserts this exact behavior; no assertion was added.",
    },
    "Gson_4b_writer": {
        "semantic_rule": "For a new JsonWriter, writing the existing top-level value true and closing the writer must leave the StringWriter equal to `true` without enabling lenient mode.",
        "observed_counterexample": "The original execution throws IllegalStateException before writing the value.",
        "source_of_rule": "Existing JsonWriterTest.testTopLevelValueTypes asserts `assertEquals(\"true\", string1.toString())`; no assertion was added.",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--g4-jobs", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    jobs = []
    for line in args.g4_jobs.read_text(encoding="utf-8").splitlines():
        g4 = json.loads(line)
        user = g4["user"]
        case_id = user["case_id"]
        jobs.append(
            {
                "experiment_group": "G6_counterexample_guided_repair",
                "system": """You are repairing a Java production file after local execution exposed a counterexample to behavior already required by its existing test. Use only the failure, automatically extracted repair obligation, selected localization, and original production file. Return valid JSON only:
{
  "patches": [
    {"file": "the supplied production file", "start_line": 0, "end_line": 0, "replacement": "exact Java source replacing the inclusive line range"}
  ],
  "constraint_check": "why the replacement prevents the supplied counterexample",
  "uncertainty": "..."
}
Do not modify tests or files outside the supplied production file. Use non-overlapping patches if necessary. The exact replacements must compile as Java. Do not claim access to a fixed version or reference patch.""",
                "user": {
                    "case_id": case_id,
                    "observed_failure": user["observed_failure"],
                    "selected_localization": user["selected_localization"],
                    "automatically_extracted_repair_constraint": CONSTRAINTS[case_id],
                    "production_file": user["production_file"],
                },
            }
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(job, ensure_ascii=False) + "\n" for job in jobs), encoding="utf-8")
    print(f"Wrote {len(jobs)} G6 counterexample-guided repair jobs")


if __name__ == "__main__":
    main()
