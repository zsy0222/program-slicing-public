# Static analysis expansion — 2026-08-15

## Scope

This run extends the local feasibility study using three already-downloaded SV-COMP unsafe loop benchmarks. It evaluates only whether the reproduced Error Invariants analyzer can produce an Error Invariant trajectory. These programs do not provide developer-intended fault locations, so they are excluded from Top-k fault-localization accuracy statistics.

## Input handling

The raw SV-COMP programs are unchanged. New normalized copies remove verifier wrappers and use the analyzer's native assertion form. Two conversions from unsigned to signed integers were made only where all values on the relevant path remain inside the signed-int range. The rationale is retained in `benchmarks/pilot/svcomp_expansion_manifest.csv`.

## Results

| Case | Expected property | Analyzer result | Observation |
|---|---|---|---|
| SV04 Mono3_1 | unsafe | internal error | `Failure("nth")` after backward analysis |
| SV05 Mono4_1 | unsafe | internal error | `Failure("nth")` after backward analysis |
| SV06 Mono6_1 | unsafe | completed in 0.375 s | full Error Invariant trajectory extracted |

The completed SV06 trajectory identifies the error state `x == 10000000 && z == 10000000` and retains the relevant guard, `z` update, and `x` update. It is suitable for qualitative trajectory-understanding cases, but not for numerical localization evaluation without a separately justified root-cause label.

## Implication

The current reproduction demonstrably handles some large affine loop cases, but the recurring `Failure("nth")` means analyzer completion rate must be reported as a first-class metric. Future comparative LLM results must use the intersection of cases where required static artifacts are available, while reporting excluded cases and their reason separately.
