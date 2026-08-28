# Seeded-fault smoke test — 2026-08-15

## Purpose

Validate the experiment pipeline with programs whose fault locations are known
from a correct reference program. These results are a workflow smoke test only;
they must not be pooled with real-bug or SV-COMP effectiveness results.

## Runtime confirmation

All programs were compiled with MinGW GCC 12.1.0. The normalized sources omit
`assert.h` because the Error Invariants front end accepts native `assert`; the
runtime check supplied that standard header only at compilation time.

| Case | Seeded change | Faulty program | Correct reference | Result |
|---|---|---:|---:|---|
| Seed01 | `z = z + 1` → `z = z - 1` | assertion failure | normal exit | confirmed |
| Seed02 v2 | `x > 20` → `x >= 20` | assertion failure | normal exit | confirmed |
| Seed03 v2 | `z = 12` → `z = 11` | assertion failure | normal exit | confirmed |

## Ground truth

Ground-truth locations are the one mutated statement per pair, retained in
`benchmarks/seeded_faults/manifest.csv`. The C sources themselves contain no
ground-truth comments, so source-only LLM conditions cannot see oracle data.

## Error Invariants run

The reproduced original Error Invariants analyzer was run in Ubuntu 22.04 with
`-full -domain polyhedra` and a 60-second limit per input. Raw output is kept
under `outputs/error_invariants_seeded_2026-08-15/`.

| Case | Analyzer status | Time / outcome | Interpretation |
|---|---|---|---|
| Seed01 | completed | 0.666 s | full Error Invariant trajectory extracted |
| Seed02 v2 | internal error | `Failure("nth")` | tool limitation; not counted as a localization miss |
| Seed03 v2 | completed | 0.593 s | full Error Invariant trajectory extracted |

The earlier non-v2 Seed02 and Seed03 outputs are retained as an audit trail but
excluded from the manifest: the two preliminary cases accidentally shared the
same faulty input with different intended references, creating ambiguous
ground truth.

## G1: pure Error Invariants baseline

For a completed run, the deterministic baseline ranks statements that directly
write a variable mentioned in the error-location invariant; nearer writes rank
higher. This is intentionally transparent and contains no LLM.

| Metric | Result | Denominator |
|---|---:|---|
| Analysis coverage | 2 / 3 (66.7%) | all labelled smoke-test cases |
| Top-1 | 1 / 2 (50.0%) | completed analyses only |
| Top-3 | 2 / 2 (100.0%) | completed analyses only |

- **Seed01:** the true mutated update is analyzer location `L7`; ranked 1st.
- **Seed03 v2:** the true mutated initialization is `L3`; the baseline ranks
  loop update `L7` first and `L3` second. The tool identifies both as
  error-relevant, but cannot distinguish the intended faulty change by the
  direct-write heuristic alone.

These are smoke-test observations, not a final effectiveness claim: only two
analyses completed. The generated aggregate is
`outputs/error_invariants_seeded_2026-08-15/pure_tool_baseline.json`.
