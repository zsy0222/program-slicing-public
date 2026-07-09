# Cascaded Hybrid Slicing: Research Questions

## Background

A cascaded hybrid slicing framework that uses assertion-guided dynamic backward tracing (Phase 1) to locate the source of a bug, followed by assertion-guided static forward traversal (Phase 2) to validate the complete bug-propagation path. Only one input point (sink/assertion failure point) is required.

## Core Research Question

[CRQ] Given a failing test and its assertion failure point (sink), can a cascaded hybrid slicing framework (dynamic backward + static forward with assertion pruning) produce a fault candidate set that is:
  (a) smaller than pure dynamic MPS (Zhang 2007), and
  (b) theoretically more complete than LLM-only slicing (SliceMate),
while requiring only a single input point (sink)?

## Sub-questions

[RQ1] Source localization accuracy
  How accurately can assertion-guided dynamic backward tracing locate the source
  (last correct value point) along the execution trace?
  - Metric: Distance from true bug origin vs. MPS backward slice

[RQ2] Path pruning effectiveness
  How effectively can assertion-guided static forward pruning reduce path explosion
  in Phase 2?
  - Metric: Path count reduction ratio, false positive rate
  - Hypothesis: Assertion PASS on a branch correlates with bug-free code

[RQ3] Comparative effectiveness
  How does the cascaded framework compare against established baselines?
  - Baselines: Zhang 2007 MPS, Tarantula/Ochiai (SBFL), SliceMate, Cause Transitions
  - Metrics: Slice size, precision, recall, fault localization rank

[RQ4] Assertion quality sensitivity
  How sensitive is the framework to assertion quality?
  - Assertion density (L0-L4)
  - Assertion correctness (mutation: add/remove/modify assertions)
  - Metric: Framework degradation curve

[RQ5] Cascaded vs. intersected
  Does the cascaded architecture (Phase 1 output as Phase 2 input) outperform
  traditional hybrid slicing (set intersection/union of independent slices)?
  - Metric: Slice precision, recall, theoretical completeness guarantee

## Design Decisions (derived from RQs)

- Phase 1: Dynamic backward on trace, scan assertion results from sink to source
- Source: Last passing assertion point on trace
- Phase 2: Static forward from source, prune paths with assertion PASS
- LLM role: Limited to Phase 1 source hypothesis generation
- Assertion source: External LLM-based assertion generation (ASSERTIFY etc.)
- Input: Single point (sink), unlike Zhang 2007's three criteria
