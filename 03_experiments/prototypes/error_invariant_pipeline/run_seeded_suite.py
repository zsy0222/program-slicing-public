"""Run paired runtime and Error-Invariant checks for the seeded-fault suite.

The script records every outcome.  It never filters a failing analyzer run out
of the status table, so the later V2 sample can be reconstructed exactly.
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
from pathlib import Path


def invoke(command: list[str], timeout: int, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, timeout=timeout, cwd=cwd, check=False)


def runtime_check(source: Path, executable: Path, compiler: str, timeout: int) -> tuple[str, str]:
    compilation = invoke([compiler, "-include", "assert.h", str(source), "-o", str(executable)], timeout)
    if compilation.returncode != 0:
        return "compile_error", compilation.stderr.strip().replace("\n", " ")[:300]
    execution = invoke([str(executable)], timeout)
    if execution.returncode == 0:
        return "pass", "normal_exit"
    return "fail", f"exit_{execution.returncode}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--benchmark-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--case-id", action="append", dest="case_ids", help="Run only this case; repeatable")
    parser.add_argument("--compiler", default="gcc")
    parser.add_argument("--ssh-key", required=True, type=Path)
    parser.add_argument("--ssh-host", default="vboxuser@127.0.0.1")
    parser.add_argument("--ssh-port", type=int, default=2222)
    parser.add_argument("--remote-dir", default="/tmp/v2_expanded_seeded_suite")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    args = parser.parse_args()

    if not args.ssh_key.exists():
        raise SystemExit(f"SSH key not found: {args.ssh_key}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir = args.output_dir / "runtime"
    analysis_dir = args.output_dir / "analysis"
    runtime_dir.mkdir(exist_ok=True)
    analysis_dir.mkdir(exist_ok=True)

    cases = list(csv.DictReader(args.manifest.open(newline="", encoding="utf-8")))
    if args.case_ids:
        selected = set(args.case_ids)
        cases = [case for case in cases if case["case_id"] in selected]
        missing = selected.difference(case["case_id"] for case in cases)
        if missing:
            raise SystemExit(f"Unknown case_id values: {', '.join(sorted(missing))}")
    ssh_base = ["ssh", "-o", "BatchMode=yes", "-i", str(args.ssh_key), "-p", str(args.ssh_port), args.ssh_host]
    scp_base = ["scp", "-q", "-o", "BatchMode=yes", "-i", str(args.ssh_key), "-P", str(args.ssh_port)]
    ready = invoke(ssh_base + [f"mkdir -p {args.remote_dir}"], args.timeout_seconds)
    if ready.returncode != 0:
        raise SystemExit(f"Cannot prepare analyzer directory: {ready.stderr.strip()}")

    status = args.output_dir / "run_status.csv"
    previous_rows = (
        list(csv.DictReader(status.open(newline="", encoding="utf-8")))
        if status.exists()
        else []
    )
    selected_ids = {case["case_id"] for case in cases}
    rows: list[dict[str, str]] = [
        row for row in previous_rows if row["case_id"] not in selected_ids
    ]

    def write_status() -> None:
        with status.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "case_id", "faulty_runtime", "faulty_runtime_note", "correct_runtime",
                    "correct_runtime_note", "analysis_status", "analysis_note", "eligible_for_v2",
                ],
            )
            writer.writeheader()
            writer.writerows(rows)
    for case in cases:
        case_id = case["case_id"]
        faulty = args.benchmark_dir / case["faulty_program"]
        correct = args.benchmark_dir / case["correct_reference"]
        faulty_state, faulty_note = runtime_check(faulty, runtime_dir / f"{case_id}_faulty.exe", args.compiler, args.timeout_seconds)
        correct_state, correct_note = runtime_check(correct, runtime_dir / f"{case_id}_correct.exe", args.compiler, args.timeout_seconds)

        remote_source = f"{args.remote_dir}/{case_id}_faulty.c"
        remote_output = f"{args.remote_dir}/{case_id}_faulty.out"
        local_output = analysis_dir / f"{case_id}_faulty.out"
        upload = invoke(scp_base + [str(faulty), f"{args.ssh_host}:{remote_source}"], args.timeout_seconds)
        if upload.returncode != 0:
            analyzer_state, analyzer_note = "transport_error", upload.stderr.strip()[:300]
        else:
            analysis = invoke(
                ssh_base + [
                    f"timeout {args.timeout_seconds}s /home/vboxuser/error-invariants-work/error_inv/Main.native "
                    f"-full -domain polyhedra {remote_source} > {remote_output} 2>&1"
                ],
                args.timeout_seconds + 10,
            )
            download = invoke(scp_base + [f"{args.ssh_host}:{remote_output}", str(local_output)], args.timeout_seconds)
            if analysis.returncode == 0 and download.returncode == 0:
                analyzer_state, analyzer_note = "completed", "completed_full_polyhedra"
            elif analysis.returncode == 124:
                analyzer_state, analyzer_note = "timeout", "analyzer_timeout"
            else:
                analyzer_state = "internal_error" if download.returncode == 0 else "output_unavailable"
                analyzer_note = f"analyzer_exit_{analysis.returncode}"
        rows.append(
            {
                "case_id": case_id,
                "faulty_runtime": faulty_state,
                "faulty_runtime_note": faulty_note,
                "correct_runtime": correct_state,
                "correct_runtime_note": correct_note,
                "analysis_status": analyzer_state,
                "analysis_note": analyzer_note,
                "eligible_for_v2": str(faulty_state == "fail" and correct_state == "pass" and analyzer_state == "completed").lower(),
            }
        )
        write_status()
        print(f"{case_id}: faulty={faulty_state}, correct={correct_state}, analyzer={analyzer_state}")

    print(f"Wrote {status}")


if __name__ == "__main__":
    main()
