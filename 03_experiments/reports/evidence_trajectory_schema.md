# Error-Invariant Evidence Trajectory Schema (Pilot v0.2)

## Purpose

This schema converts one Error Invariants analysis run into a compact,
machine-readable evidence object. It is the common input for the pure-tool
baseline, raw-trajectory baseline, structured-trajectory LLM baseline, and
the later verification-feedback loop.

## Fields

- `error`: the assertion location and the analyzer invariant at that location.
- `evidence_locations`: locations with a non-trivial first-pass Error
  Invariant, the error location, and every statement that directly writes an
  error-state variable. Each has a stable `L<id>` reference. The latter rule
  prevents initialization faults from disappearing merely because their
  invariant is `top`.
- `pure_tool_baseline`: a deterministic ranking. Version 0.1 ranks only
  statements that directly write a variable appearing in the error invariant;
  ties favour proximity to the error location.
- `annotation`: kept separate from analysis evidence. A suggested location is
  not ground truth until confirmed against a known fix or by human review.

## Evidence contract for later LLM experiments

Every LLM answer must return: (1) ranked candidate location references,
(2) a causal chain containing `L<id>` citations, (3) a repair hypothesis, and
(4) a statement of uncertainty. A verifier may reject a response if it cites
a location absent from `evidence_locations`, claims a write to a variable not
written by the cited statement, or provides no cited path to the error state.

## Scope and limits

This is an extraction and ranking prototype, not a proof of true root cause.
The Error Invariants analysis is an abstract interpretation result, and this
first schema does not reconstruct all loop-unwinding or BDD-refinement states.
Those richer states will be added only after this baseline is verified on a
small labelled benchmark.
