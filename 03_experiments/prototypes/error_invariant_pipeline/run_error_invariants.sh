#!/usr/bin/env bash
# Run one normalized C input with the reproduced Error Invariants analyzer.
# Usage: run_error_invariants.sh INPUT_C OUTPUT_LOG
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 INPUT_C OUTPUT_LOG" >&2
  exit 64
fi

eval "$(opam env)"
timeout 60s /home/vboxuser/error-invariants-work/error_inv/Main.native \
  -full -domain polyhedra "$1" > "$2" 2>&1
