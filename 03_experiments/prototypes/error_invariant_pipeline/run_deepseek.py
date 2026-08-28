"""Run oracle-free LLM experiment jobs through the DeepSeek Chat Completions API.

The API key is read only from DEEPSEEK_API_KEY and is never written to disk.
Responses retain the model metadata, raw JSON text, usage, and request errors
needed for reproducibility.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


API_URL = "https://api.deepseek.com/chat/completions"


def call_deepseek(job: dict, api_key: str, model: str, temperature: float) -> dict:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": job["system"]},
            {"role": "user", "content": json.dumps(job["user"], ensure_ascii=False)},
        ],
        "temperature": temperature,
        "thinking": {"type": "disabled"},
        "response_format": {"type": "json_object"},
        "stream": False,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return {
            "status": "completed",
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "response_id": payload.get("id"),
            "model_returned": payload.get("model"),
            "system_fingerprint": payload.get("system_fingerprint"),
            "finish_reason": payload.get("choices", [{}])[0].get("finish_reason"),
            "content": payload.get("choices", [{}])[0].get("message", {}).get("content"),
            "usage": payload.get("usage"),
        }
    except urllib.error.HTTPError as error:
        return {
            "status": "api_error",
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "http_status": error.code,
            "error": error.read().decode("utf-8", errors="replace"),
        }
    except (urllib.error.URLError, TimeoutError) as error:
        return {
            "status": "transport_error",
            "elapsed_seconds": round(time.perf_counter() - started, 3),
            "error": str(error),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--jobs", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--resume", action="store_true", help="Keep completed records and run only missing repetitions")
    parser.add_argument("--case-id", action="append", dest="case_ids", help="Run only this case; repeatable")
    args = parser.parse_args()

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("DEEPSEEK_API_KEY is not configured; no requests were sent.")
    if args.repetitions < 1:
        raise SystemExit("--repetitions must be at least 1")

    jobs = [json.loads(line) for line in args.jobs.read_text(encoding="utf-8").splitlines() if line]
    if args.case_ids:
        selected = set(args.case_ids)
        jobs = [job for job in jobs if job["user"]["case_id"] in selected]
        missing = selected.difference(job["user"]["case_id"] for job in jobs)
        if missing:
            raise SystemExit(f"Unknown case_id values: {', '.join(sorted(missing))}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    completed: set[tuple[str, str, int, int | None]] = set()
    if args.resume and args.output.exists():
        for line in args.output.read_text(encoding="utf-8").splitlines():
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("status") == "completed":
                completed.add(
                    (
                        str(record.get("experiment_group")),
                        str(record.get("case_id")),
                        int(record.get("repetition", 0)),
                        record.get("origin_repetition"),
                    )
                )
    mode = "a" if args.resume else "w"
    with args.output.open(mode, encoding="utf-8") as output_file:
        for job in jobs:
            for repetition in range(1, args.repetitions + 1):
                key = (
                    job["experiment_group"],
                    job["user"]["case_id"],
                    repetition,
                    job.get("origin_repetition"),
                )
                if key in completed:
                    continue
                result = call_deepseek(job, api_key, args.model, args.temperature)
                record = {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "experiment_group": job["experiment_group"],
                    "case_id": job["user"]["case_id"],
                    "repetition": repetition,
                    "origin_repetition": job.get("origin_repetition"),
                    "request_model": args.model,
                    "temperature": args.temperature,
                    **result,
                }
                output_file.write(json.dumps(record, ensure_ascii=False) + "\n")
                output_file.flush()
                print(f"{record['experiment_group']} {record['case_id']} run {repetition}: {record['status']}")


if __name__ == "__main__":
    main()
