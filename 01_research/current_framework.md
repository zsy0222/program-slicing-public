# Current Research Framework

## Goal

This research studies how assertion-guided program analysis can produce small, auditable fault candidate sets, and how these candidates can be converted into reliable inputs for LLM-assisted fault analysis and repair.

## Core hypothesis

A failure-relevant program slice is valuable, but it is not a root-cause explanation by itself. The slice must be interpreted as an **Error Invariant**: a concise rule describing which state or transition must hold, how the observed execution violates it, and what a valid candidate must preserve.

## Cascaded hybrid slicing

The design is a cascade, not an intersection:

1. **Dynamic backward stage.** Starting from an assertion failure or exception, trace the concrete data and control dependencies that produced the observed bad state.
2. **Candidate hand-off.** Use the dynamic result to identify the last relevant state and candidate source locations.
3. **Static forward stage.** Explore reachable consequences from each candidate while using assertions and runtime observations to prune paths that contradict the observed failure.
4. **Evidence contract.** Record the criterion, dependencies, invariant, candidate locations, and validation evidence in a structured trajectory.
5. **Candidate validation.** Validate candidates using runtime counterfactual observations and static differential checks; for repair experiments, also require compilation and tests.

## LLM-assisted repair track

The current repair pilot separates four sources of assistance: complete source only, static local context, dynamic semantic slice, and the full workflow. The full workflow supplies a slice-derived Error Invariant and a restricted editing scope, then uses tests as a feedback loop. It is designed to test whether semantic constraints reduce unguided LLM repair errors on long or ambiguous source code.

## Scope and limitations

- Passing a property or trigger test does not prove a unique root cause or developer intent.
- Pilot results are controlled observations, not population-level claims about real defects.
- Full regression validation, broader Defects4J coverage, multiple models, and stronger leakage controls are required before drawing general conclusions.
