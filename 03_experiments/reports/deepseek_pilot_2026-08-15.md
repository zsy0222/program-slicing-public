# DeepSeek pilot experiment — 2026-08-15

## Status

This is a smoke-test result, not a final effectiveness claim. It uses
DeepSeek-V4-Flash with thinking disabled, temperature 0, and three independent
requests per task. The actual returned model name and system fingerprint are
retained in the raw JSONL files.

## Fair comparison set

The seeded suite has three labelled faulty programs. Error Invariants completed
only Seed01 and Seed03, so trajectory-dependent groups can be compared only on
these two cases. Source-only G2 also ran Seed02, but its all-three-case score
must not be compared directly against trajectory groups.

## Results

| Group | Cases / responses | Top-1 | Top-3 | Evidence-valid rate | Mean response time |
|---|---:|---:|---:|---:|---:|
| G1 Error Invariants only | 2 completed cases | 50.0% | 100.0% | n/a | static analysis only |
| G2 source-only LLM, all cases | 3 / 9 | 66.7% | 100.0% | n/a | 3.587 s |
| G2 source-only LLM, common cases | 2 / 6 | 100.0% | 100.0% | n/a | subset of above |
| G5 v0.1 structured trajectory | 2 / 6 | 50.0% | 50.0% | 2 / 6 | 4.240 s |
| G5 v0.2 structured trajectory | 2 / 6 | 50.0% | 50.0% | 6 / 6 | 4.100 s |
| G3 slice-aware LLM | 2 / 6 | 100.0% | 100.0% | n/a | 3.389 s |
| G4 raw Error Invariant Map | 2 / 6 | 50.0% | 50.0% | n/a | 3.627 s |
| G6 feedback closed loop (v0.1) | 2 / 6 final answers | 50.0% | 50.0% | 3 / 6 | see below |

G2 used 5,872 total tokens across nine requests. G3 used 4,605 and G4 used
4,837 across six requests each. G5 v0.1 used 8,810 across six requests; G5
v0.2 used 9,168 across six requests. G6 issued four feedback requests using
8,293 tokens, in addition to the initial G5 v0.1 requests. Token totals are
not directly comparable because the groups have different numbers of tasks.

## Interpretation

- On the **initialization fault** (Seed03), source-only DeepSeek consistently
  ranked the true initial value at source line 3 first. G1 and G5 instead
  ranked the loop decrement first. The decrement is a genuine causal mechanism
  for the failure, but it is not the seeded developer error.
- G5 v0.1 omitted the initialization assignment from its evidence because its
  invariant was `top`. The evidence validator rejected four of six answers
  because an initialization claim cited a non-writing loop location.
- Schema v0.2 retains every direct write to an error-state variable, even when
  its invariant is `top`. This improved evidence-contract validity to 6 / 6,
  but the model still ranked the decrement first. Therefore grounding alone
  does not resolve root-cause ambiguity.
- **G3** matched source-only G2 on the two common cases: the semantic slice
  preserved the useful source cues while reducing context. This is the only
  configuration that did not reduce Top-1 in the current pilot.
- **G4** mixed source-line and analyzer-location conventions on Seed01 and
  did not improve localization. Raw analyzer text is therefore not a suitable
  direct interface for the LLM in this form.
- **G6** revised four v0.1 answers rejected by the validator. One revision
  became evidence-valid, but the three initialization-case revisions repeated
  the unsupported initialization claim. Overall evidence validity rose from
  2 / 6 to 3 / 6, with no localization improvement.

## Scope limit

All G1–G6 smoke-test groups have run where their required static artifact is
available. The main limit is scale: two cases are insufficient for a claim of
superiority or for statistical testing. The independent SV-COMP feasibility
set additionally shows that Error Invariants may terminate with
`Failure("nth")`, so analyzer coverage must remain a reported outcome.

## Consequence for the method

The pilot supports the feasibility of evidence-constrained explanation but not
an accuracy-improvement claim. The next method revision should add a mechanism
for distinguishing *error-path mechanism* from *developer-intended faulty
change*, such as counterfactual patch validation against a reference/oracle or
a separately labelled root-cause ranking objective.

## Raw artifacts

- `outputs/deepseek_runs_2026-08-15/G2_source_only_authorized.jsonl`
- `outputs/deepseek_runs_2026-08-15/G5_structured_evidence_authorized.jsonl`
- `outputs/deepseek_runs_2026-08-15/G5_v0_2_structured_evidence_authorized.jsonl`
- `outputs/deepseek_runs_2026-08-15/G5_v0_1_evidence_verification.json`
- `outputs/deepseek_runs_2026-08-15/G5_v0_2_evidence_verification.json`
- `outputs/deepseek_runs_2026-08-15/G3_slice_aware_authorized.jsonl`
- `outputs/deepseek_runs_2026-08-15/G4_raw_error_invariant_authorized.jsonl`
- `outputs/deepseek_runs_2026-08-15/G6_closed_loop_final.jsonl`
- `outputs/deepseek_runs_2026-08-15/G6_closed_loop_verification.json`
