# Research Questions and Method Boundary (Revised after G1–G6 Pilot)

> Revision date: 2026-08-15
> Evidence basis: `03_experiments/reports/deepseek_pilot_2026-08-15.md`

## 1. What the pilot changed

The initial hypothesis was that an LLM could directly use an Error Invariant
trajectory to improve root-cause localization. The pilot does **not** support
that claim:

- On the two fair, analyzer-completed common cases, source-only and
  source-plus-semantic-slice prompting achieved 100% Top-1 localization.
- Raw Error Invariant Maps and structured trajectories achieved 50% Top-1.
- Trajectory v0.2 improved evidence-contract compliance from 2/6 to 6/6, but
  did not improve root-cause ranking.
- Feedback corrected one unsupported explanation but did not improve the
  aggregate ranking result.

The observed reason is conceptual rather than merely prompt-related. Error
Invariants characterize an **error-reaching state-transition mechanism**. In
the absence of a specification, tests, or a reference fix, that mechanism need
not uniquely identify the developer-intended faulty edit. For example, both a
wrong initialization and a wrong update may lead to the same error state.

Accordingly, Error Invariants are retained as auditable semantic evidence and
verification constraints, not as a standalone root-cause ranker.

## 2. Revised central research question

**CRQ.** Can a source-and-semantic-slice LLM generate useful, role-aware fault
candidates, while an Error Invariant trajectory and counterfactual validation
make the resulting mechanism explanation and proposed repair auditable without
overclaiming a unique developer root cause?

The contribution is a closed workflow, not a claim that an invariant alone
recovers intent:

1. static analysis constructs a semantic slice and an Error Invariant evidence
   trajectory;
2. the LLM reads source plus slice to propose and rank candidate edits;
3. every candidate is assigned a role: `fault_origin`, `error_mechanism`,
   `control_enabler`, or `context`;
4. the trajectory checks that mechanism claims cite actual, location-resolved
   evidence;
5. a minimal counterfactual patch is executed and re-analysed; and
6. only validated results are returned as repair hypotheses. If multiple
   patches work, the system reports ambiguity rather than inventing one root
   cause.

## 3. Research questions

### RQ1 — Candidate generation

Does source plus semantic slice improve or preserve fault-candidate
localization compared with source-only LLM analysis, on the same
analyzer-completed cases?

**Metric:** Top-1/Top-3 source-location accuracy against a manually checked
reference fault, valid-output rate, latency, and token use.

### RQ2 — Role-aware mechanism explanation

Can the LLM distinguish the developer-fault candidate from the error mechanism
and enabling control condition, rather than treating every error-path write as
the root cause?

**Metric:** role-label accuracy and mechanism-explanation correctness, both
manually adjudicated against the reference patch and trajectory.

### RQ3 — Evidence grounding

Does the v0.2 Error Invariant evidence trajectory increase the proportion of
mechanism claims that are location-resolved and supported by static evidence?

**Metric:** evidence-contract pass rate, unsupported-claim rate, and
location-identifier mismatch rate.

### RQ4 — Counterfactual repair validation

Can a proposed minimal patch eliminate the failure and preserve the checked
property or test result?

**Metric:** compiling-patch rate, failure-elimination rate, property/test pass
rate, analyzer re-run result, and number of distinct validated repairs per
case.

This RQ measures repair-hypothesis validity, **not** proof that the patch is
the unique intended fix.

### RQ5 — Component contribution and cost

What are the accuracy, grounding, repair-validation, latency, and token-cost
effects of semantic slicing, trajectory auditing, counterfactual validation,
and validation feedback?

**Metric:** fair-intersection ablation across all completed cases. Static
analyzer coverage and failures are reported separately from downstream quality.

## 4. Claims and non-claims

### Claims to test

- Semantic slicing can provide a compact, useful context for LLM candidate
  generation.
- Error Invariant trajectories can constrain and audit claims about an
  error-reaching mechanism.
- Counterfactual execution and re-analysis can distinguish an unverified
  explanation from a validated repair hypothesis.
- Explicit role separation can prevent conflating a mechanism with a root
  cause.

### Claims explicitly not made

- An Error Invariant trajectory alone identifies the developer-intended root
  cause.
- The LLM output is sound merely because the underlying static analysis is
  sound.
- A failure-eliminating patch is necessarily the unique or intended repair.
- Results from the present two-case fair intersection demonstrate general
  superiority or statistical significance.

## 5. Evaluation groups

| Group | Input / workflow | Purpose |
|---|---|---|
| G1 | Pure Error Invariants heuristic | Tool-only baseline |
| G2 | Source-only LLM | LLM baseline |
| G3 | Source + semantic slice LLM | Strong static-context baseline |
| G4 | Raw Error Invariant Map LLM | Tests the unsuitable direct interface |
| G5 | Structured trajectory LLM | Tests evidence-only prompting |
| G6 | G5 + evidence feedback | Tests explanation-feedback loop |
| P-V2a | Source + slice + role-aware candidates | Isolates role separation |
| P-V2b | P-V2a + trajectory audit + counterfactual patch validation + targeted feedback | Proposed full method |

All localization comparisons must use the same analyzer-completed case
intersection. Tool coverage, crashes, and timeouts are reported independently.

## 6. Required benchmark progression

The current pilot is a smoke test. Before any effectiveness claim, construct
at least 10–15 manually checked reference-fault cases that complete static
analysis; because the tool has observed crashes, more candidates may have to be
screened. Each case needs:

- faulty and corrected source (or a trusted reference patch);
- a failing assertion/test and an executable validation command;
- the designated fault location and fault category;
- a recorded analysis-completion status; and
- human adjudication rules for candidate role and explanation correctness.

Real bug/fix cases may be added only after their C sources, builds, and
reference fixes are normalized and independently checked.

## 7. Deferred extension

LLM-proposed predicates followed by abstract-domain re-refinement remains a
future extension. It is not part of the present core effectiveness claim until
there is an executable implementation and a benchmark that can assess it.
