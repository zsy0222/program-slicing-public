# Cascaded Hybrid Slicing Workflow

## Inputs

- A reproducible failing test, assertion, or exception.
- Program source and an executable environment.
- Optional static-analysis infrastructure and a test oracle.

## Workflow

1. **Reproduce the failure.** Freeze the failing revision, test command, failure criterion, and environment.
2. **Choose a criterion.** Select the assertion/exception location and the bad state that must be explained.
3. **Dynamic backward slicing.** Extract executed data and control dependencies from the criterion backward.
4. **Derive an Error Invariant.** State the required behavior, the observed violating state, and the relevant branch/transition.
5. **Static forward expansion.** From the candidate source locations, inspect feasible forward consequences and prune paths contradicted by runtime evidence.
6. **Create an evidence trajectory.** Store the criterion, slice facts, invariant, candidate set, provenance, and validation decisions.
7. **Validate candidates.** Use counterfactual runs and static differences; in repair experiments, apply a constrained patch and run compilation, trigger tests, and full regression tests.

## Expected outputs

- A ranked, auditable candidate set rather than an unbounded slice.
- A structured Error Invariant that can be inspected by a researcher or supplied to a repair model.
- Explicit validation records that distinguish a location hypothesis, a passing property, and a verified repair.
