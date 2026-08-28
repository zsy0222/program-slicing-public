"""Apply V2 candidate edits in isolated copies and run a counterfactual test.

The validator never reads the manifest's correct-reference or ground-truth
columns while evaluating an LLM answer. It records whether the original program
fails and whether each proposed one-line replacement compiles and exits cleanly.
Static semantic-delta analysis is intentionally recorded as unavailable here;
it requires the reproduced Linux analyzer and is run as a separate stage.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


def run_command(command: list[str], timeout: int) -> dict[str, Any]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        return {
            "status": "completed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except FileNotFoundError:
        return {"status": "unavailable", "returncode": None, "stdout": "", "stderr": command[0]}
    except subprocess.TimeoutExpired as error:
        return {
            "status": "timeout",
            "returncode": None,
            "stdout": error.stdout or "",
            "stderr": error.stderr or "",
        }


def compile_and_run(source: Path, executable: Path, compiler: str, timeout: int) -> dict[str, Any]:
    compilation = run_command([compiler, "-include", "assert.h", str(source), "-o", str(executable)], timeout)
    if compilation["status"] != "completed" or compilation["returncode"] != 0:
        return {"compilation": compilation, "execution": None, "runtime_pass": False}
    execution = run_command([str(executable)], timeout)
    return {
        "compilation": compilation,
        "execution": execution,
        "runtime_pass": execution["status"] == "completed" and execution["returncode"] == 0,
    }


def apply_one_line_replacement(source: Path, line_number: int, replacement: str, destination: Path) -> str | None:
    lines = source.read_text(encoding="utf-8").splitlines()
    if not isinstance(line_number, int) or not 1 <= line_number <= len(lines):
        return None
    if "\n" in replacement or "\r" in replacement or not replacement.strip():
        return None
    old_line = lines[line_number - 1]
    indentation = old_line[: len(old_line) - len(old_line.lstrip())]
    lines[line_number - 1] = indentation + replacement.strip()
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return old_line


def parse_content(record: dict[str, Any]) -> dict[str, Any] | None:
    content = record.get("content")
    if not isinstance(content, str):
        return None
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--benchmark-dir", required=True, type=Path)
    parser.add_argument("--responses", required=True, type=Path, help="JSONL emitted by run_deepseek.py")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--compiler", default="gcc")
    parser.add_argument("--timeout-seconds", type=int, default=10)
    args = parser.parse_args()

    with args.manifest.open(newline="", encoding="utf-8") as file:
        source_by_case = {row["case_id"]: args.benchmark_dir / row["faulty_program"] for row in csv.DictReader(file)}
    records = [json.loads(line) for line in args.responses.read_text(encoding="utf-8").splitlines() if line]
    args.output_dir.mkdir(parents=True, exist_ok=True)

    output_path = args.output_dir / "counterfactual_patch_validation.jsonl"
    with output_path.open("w", encoding="utf-8") as output:
        for record in records:
            if record.get("status") != "completed":
                continue
            answer = parse_content(record)
            source = source_by_case.get(record.get("case_id"))
            if answer is None or source is None:
                continue
            run_key = f"{record['case_id']}_r{record.get('repetition', 0)}"
            work_dir = args.output_dir / "work" / run_key
            if work_dir.exists():
                shutil.rmtree(work_dir)
            work_dir.mkdir(parents=True)
            baseline_source = work_dir / "baseline.c"
            shutil.copy2(source, baseline_source)
            baseline = compile_and_run(
                baseline_source, work_dir / "baseline.exe", args.compiler, args.timeout_seconds
            )
            for rank, candidate in enumerate(answer.get("candidates", [])[:3], 1):
                candidate_source = work_dir / f"candidate_{rank}.c"
                old_line = apply_one_line_replacement(
                    source, candidate.get("source_line"), candidate.get("proposed_replacement", ""), candidate_source
                )
                if old_line is None:
                    validation = {"status": "rejected", "reason": "invalid_one_line_replacement"}
                else:
                    patched = compile_and_run(
                        candidate_source,
                        work_dir / f"candidate_{rank}.exe",
                        args.compiler,
                        args.timeout_seconds,
                    )
                    if not baseline["runtime_pass"] and patched["runtime_pass"]:
                        status = "validated_by_runtime"
                    elif patched["compilation"]["status"] != "completed" or patched["compilation"]["returncode"] != 0:
                        status = "rejected_compile"
                    elif not patched["runtime_pass"]:
                        status = "rejected_failure_retained"
                    else:
                        status = "inconclusive_baseline"
                    validation = {"status": status, "reason": "runtime counterfactual only", "patched": patched}
                result = {
                    "experiment_group": record.get("experiment_group"),
                    "case_id": record["case_id"],
                    "repetition": record.get("repetition"),
                    "candidate_rank": rank,
                    "candidate": candidate,
                    "original_source_line": old_line,
                    "baseline": baseline,
                    "validation": validation,
                    "static_semantic_delta": {"status": "not_run", "reason": "separate Linux analyzer stage"},
                }
                output.write(json.dumps(result, ensure_ascii=False) + "\n")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
