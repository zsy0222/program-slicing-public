"""Create a valid, de-duplicated DeepSeek result JSONL without altering raw logs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    seen: set[tuple[str, str, int, int | None]] = set()
    valid: list[dict] = []
    malformed = 0
    duplicate = 0
    for line in args.input.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        key = (
            str(record.get("experiment_group")),
            str(record.get("case_id")),
            int(record.get("repetition", 0)),
            record.get("origin_repetition"),
        )
        if key in seen:
            duplicate += 1
            continue
        seen.add(key)
        valid.append(record)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("".join(json.dumps(record, ensure_ascii=False) + "\n" for record in valid), encoding="utf-8")
    print(f"valid={len(valid)} malformed={malformed} duplicate={duplicate}")


if __name__ == "__main__":
    main()
