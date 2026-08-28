"""Run Error-Invariant static deltas for runtime-validated case-consensus patches."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path

from validate_v2_patches import apply_one_line_replacement


LOCATION_RE = re.compile(r"^\[\s*\d+\s*:\]\s*:?\s*(.*)$", re.MULTILINE)
TIME_RE = re.compile(r"Analysis Time:\s*([0-9.]+)\s*s")


def invoke(command: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)


def final_static_result(text: str) -> dict[str, object]:
    if "Error Invariant Map::" not in text:
        return {"final_map_all_bottom": False, "the_end": False}
    final_map = text.rsplit("Error Invariant Map::", 1)[1].split("Type :", 1)[0]
    values = [value.strip() for value in LOCATION_RE.findall(final_map)]
    time_match = TIME_RE.search(text)
    return {
        "final_map_all_bottom": bool(values) and all(value == "bottom" for value in values),
        "the_end": "the_end : true" in text,
        "analysis_time_seconds": float(time_match.group(1)) if time_match else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consensus", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--benchmark-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--ssh-key", required=True, type=Path)
    parser.add_argument("--ssh-host", default="vboxuser@127.0.0.1")
    parser.add_argument("--ssh-port", type=int, default=2222)
    parser.add_argument("--remote-dir", default="/tmp/v2_consensus_static_delta")
    parser.add_argument("--timeout-seconds", type=int, default=20)
    parser.add_argument("--case-id", action="append", dest="case_ids", help="Run only this case; repeatable")
    args = parser.parse_args()

    cases = {row["case_id"]: row for row in csv.DictReader(args.manifest.open(newline="", encoding="utf-8"))}
    selections = json.loads(args.consensus.read_text(encoding="utf-8"))["selections"]
    selected = {item["case_id"]: item for item in selections if item.get("selection_status") == "selected"}
    requested = set(args.case_ids or selected)
    missing = requested.difference(selected)
    if missing:
        raise SystemExit(f"No selected candidate for: {', '.join(sorted(missing))}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    source_dir = args.output_dir / "sources"
    analysis_dir = args.output_dir / "analysis"
    source_dir.mkdir(exist_ok=True)
    analysis_dir.mkdir(exist_ok=True)
    summary_path = args.output_dir / "static_delta_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {"cases": {}}
    ssh_base = ["ssh", "-o", "BatchMode=yes", "-i", str(args.ssh_key), "-p", str(args.ssh_port), args.ssh_host]
    scp_base = ["scp", "-q", "-o", "BatchMode=yes", "-i", str(args.ssh_key), "-P", str(args.ssh_port)]
    ready = invoke(ssh_base + [f"mkdir -p {args.remote_dir}"], args.timeout_seconds)
    if ready.returncode != 0:
        raise SystemExit(f"Cannot prepare analyzer directory: {ready.stderr.strip()}")

    for case_id in sorted(requested):
        choice = selected[case_id]
        if not choice.get("runtime_validated"):
            summary["cases"][case_id] = {
                **choice,
                "static_status": "not_run",
                "reason": "case-consensus patch was not runtime-validated",
            }
        else:
            source = args.benchmark_dir / cases[case_id]["faulty_program"]
            patched = source_dir / f"{case_id}_consensus.c"
            old_line = apply_one_line_replacement(source, int(choice["source_line"]), str(choice["proposed_replacement"]), patched)
            if old_line is None:
                summary["cases"][case_id] = {**choice, "static_status": "not_run", "reason": "invalid selected replacement"}
            else:
                remote_source = f"{args.remote_dir}/{case_id}_consensus.c"
                remote_output = f"{args.remote_dir}/{case_id}_consensus.out"
                local_output = analysis_dir / f"{case_id}_consensus.out"
                upload = invoke(scp_base + [str(patched), f"{args.ssh_host}:{remote_source}"], args.timeout_seconds)
                analysis = invoke(
                    ssh_base + [
                        f"timeout {args.timeout_seconds}s /home/vboxuser/error-invariants-work/error_inv/Main.native "
                        f"-full -domain polyhedra {remote_source} > {remote_output} 2>&1"
                    ],
                    args.timeout_seconds + 10,
                ) if upload.returncode == 0 else None
                download = invoke(scp_base + [f"{args.ssh_host}:{remote_output}", str(local_output)], args.timeout_seconds) if analysis else None
                if analysis and analysis.returncode == 0 and download and download.returncode == 0:
                    result = final_static_result(local_output.read_text(encoding="utf-8", errors="replace"))
                    summary["cases"][case_id] = {
                        **choice,
                        "static_status": "completed",
                        "original_source_line": old_line.strip(),
                        "analysis_output": str(local_output).replace("\\", "/"),
                        "static_error_path_eliminated": result["final_map_all_bottom"] and result["the_end"],
                        **result,
                    }
                else:
                    summary["cases"][case_id] = {
                        **choice,
                        "static_status": "failed",
                        "analyzer_exit": analysis.returncode if analysis else None,
                        "transport_exit": download.returncode if download else upload.returncode,
                    }
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{case_id}: {summary['cases'][case_id]['static_status']}")


if __name__ == "__main__":
    main()
