"""Run model repair candidates in isolated Linux copies of public benchmarks.

This helper runs on the Ubuntu VM. It reads model JSONL, permits edits only to
the one production file selected for each case, and records compile/trigger
test outcomes.  It never accesses fixed versions or reference patches.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


RUNNER_CP = "/home/vboxuser/research-tools/Slicer4J/scripts/SingleJUnitTestRunner.jar:/home/vboxuser/research-tools/Slicer4J/scripts/junit-4.8.2.jar"

CASES = {
    "Gson_6b_d4j": {
        "source": Path("/home/vboxuser/d4j_runs/Gson_6b_manual"),
        "file": "gson/src/main/java/com/google/gson/internal/bind/JsonAdapterAnnotationTypeAdapterFactory.java",
        "test": "com.google.gson.regression.JsonAdapterNullSafeTest#testNullSafeBugDeserialize",
        "compile": ["mvn", "-q", "-pl", "gson", "-DskipTests", "compile", "test-compile"],
        "test_cp": RUNNER_CP + ":gson/target/classes:gson/target/test-classes",
    },
    "Gson_7b_d4j": {
        "source": Path("/home/vboxuser/d4j_runs/Gson_7b_manual"),
        "file": "gson/src/main/java/com/google/gson/stream/JsonReader.java",
        "test": "com.google.gson.functional.MapTest#testMapDeserializationWithUnquotedLongKeys",
        "compile": ["mvn", "-q", "-pl", "gson", "-DskipTests", "compile", "test-compile"],
        "test_cp": RUNNER_CP + ":gson/target/classes:gson/target/test-classes",
    },
    "JacksonDatabind_3b": {
        "source": Path("/home/vboxuser/research-benchmarks/JacksonDatabind_3b"),
        "file": "src/main/java/com/fasterxml/jackson/databind/deser/std/StringArrayDeserializer.java",
        "test": "com.fasterxml.jackson.databind.deser.TestArrayDeserialization#testStringArray",
        "compile": ["ant", "-q", "-f", "maven-build-java17.xml", "compile-tests"],
        "test_cp": RUNNER_CP + ":target/classes:target/test-classes:target/dependency/*",
    },
    "Gson_4b_reader": {
        "source": Path("/home/vboxuser/research-benchmarks/Gson_4b/gson"),
        "file": "src/main/java/com/google/gson/stream/JsonReader.java",
        "test": "com.google.gson.stream.JsonReaderTest#testTopLevelValueTypes",
        "compile": ["mvn", "-q", "-DskipTests", "compile", "test-compile"],
        "test_cp": RUNNER_CP + ":target/classes:target/test-classes:target/dependency/*",
    },
    "Gson_4b_writer": {
        "source": Path("/home/vboxuser/research-benchmarks/Gson_4b/gson"),
        "file": "src/main/java/com/google/gson/stream/JsonWriter.java",
        "test": "com.google.gson.stream.JsonWriterTest#testTopLevelValueTypes",
        "compile": ["mvn", "-q", "-DskipTests", "compile", "test-compile"],
        "test_cp": RUNNER_CP + ":target/classes:target/test-classes:target/dependency/*",
    },
}


def compact(text: str | None, limit: int = 6000) -> str:
    text = text or ""
    return text[-limit:]


def run(command: list[str], cwd: Path, timeout: int = 120) -> dict[str, Any]:
    try:
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        return {"status": "completed", "returncode": result.returncode, "stdout": compact(result.stdout), "stderr": compact(result.stderr)}
    except subprocess.TimeoutExpired as error:
        return {"status": "timeout", "returncode": None, "stdout": compact(error.stdout), "stderr": compact(error.stderr)}
    except OSError as error:
        return {"status": "execution_error", "returncode": None, "stdout": "", "stderr": str(error)}


def parse_answer(record: dict) -> dict | None:
    try:
        answer = json.loads(record.get("content", ""))
    except json.JSONDecodeError:
        return None
    return answer if isinstance(answer, dict) else None


def apply_patches(source: Path, expected_file: str, answer: dict) -> tuple[bool, str]:
    patches = answer.get("patches")
    if not isinstance(patches, list) or not patches:
        return False, "missing_patches"
    lines = source.read_text(encoding="utf-8").splitlines()
    normalized = []
    for patch in patches:
        if not isinstance(patch, dict) or patch.get("file") != expected_file:
            return False, "out_of_scope_file"
        start, end, replacement = patch.get("start_line"), patch.get("end_line"), patch.get("replacement")
        if not isinstance(start, int) or not isinstance(end, int) or not isinstance(replacement, str):
            return False, "invalid_patch_schema"
        if start < 1 or end < start or end > len(lines):
            return False, "invalid_line_range"
        normalized.append((start, end, replacement.splitlines()))
    ordered = sorted(normalized, reverse=True)
    previous_start = len(lines) + 1
    for start, end, replacement in ordered:
        if end >= previous_start:
            return False, "overlapping_patches"
        lines[start - 1 : end] = replacement
        previous_start = start
    source.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True, "applied"


def prepare_worktree(case: dict, work_dir: Path) -> None:
    shutil.copytree(case["source"], work_dir)
    if "JacksonDatabind" in str(case["source"]):
        original = work_dir / "maven-build.xml"
        java17 = work_dir / "maven-build-java17.xml"
        java17.write_text(original.read_text(encoding="utf-8").replace("1.6", "1.7"), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--work-root", required=True, type=Path)
    args = parser.parse_args()
    args.work_root.mkdir(parents=True, exist_ok=True)
    results = []
    for line in args.responses.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        case = CASES.get(record.get("case_id"))
        origin = record.get("origin_repetition")
        suffix = f"o{origin}" if origin is not None else f"r{record.get('repetition')}"
        run_id = f"{record.get('case_id')}_{suffix}"
        result: dict[str, Any] = {"experiment_group": record.get("experiment_group"), "case_id": record.get("case_id"), "repetition": record.get("repetition"), "origin_repetition": origin, "run_id": run_id}
        if record.get("status") != "completed" or case is None:
            result["validation"] = {"status": "skipped", "reason": "missing_case_or_model_response"}
            results.append(result)
            continue
        work_dir = args.work_root / run_id
        if work_dir.exists():
            shutil.rmtree(work_dir)
        prepare_worktree(case, work_dir)
        answer = parse_answer(record)
        if answer is None:
            result["validation"] = {"status": "rejected", "reason": "invalid_model_json"}
            results.append(result)
            continue
        applied, reason = apply_patches(work_dir / case["file"], case["file"], answer)
        result["model_answer"] = answer
        if not applied:
            result["validation"] = {"status": "rejected", "reason": reason}
            results.append(result)
            continue
        compilation = run(case["compile"], work_dir)
        if compilation["status"] != "completed" or compilation["returncode"] != 0:
            result["validation"] = {"status": "rejected_compile", "patch_application": reason, "compilation": compilation}
            results.append(result)
            continue
        trigger = run(["java", "-Xmx2g", "-cp", case["test_cp"], "SingleJUnitTestRunner", case["test"]], work_dir)
        passed = trigger["status"] == "completed" and trigger["returncode"] == 0 and "Test pass" in trigger["stdout"]
        result["validation"] = {
            "status": "trigger_pass" if passed else "trigger_fail",
            "patch_application": reason,
            "compilation": compilation,
            "trigger_test": trigger,
        }
        results.append(result)
    args.output.write_text("".join(json.dumps(result, ensure_ascii=False) + "\n" for result in results), encoding="utf-8")
    summary: dict[str, int] = {}
    for result in results:
        status = result["validation"]["status"]
        summary[status] = summary.get(status, 0) + 1
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
