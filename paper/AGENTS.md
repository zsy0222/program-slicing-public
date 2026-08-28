# LLM-Augmented Error Invariant Understanding for Fault Localization

> Current Phase: Phase 4 — LLM Deep Reading of Abstract Interpretation Intermediate Representations
> Last Updated: 2026-07-18

## Background

Building on Dimovski's (2024) Error Invariant-based fault localization via abstract interpretation, we investigate whether an LLM can semantically understand the intermediate representations (Error Invariant trajectories) produced by formal static analysis. The LLM is not a slicing engine, not a post-classifier — it is a semantic reader of the analysis process itself.

## Research Questions

See `notes/research_questions.md` for full RQ definitions.

- [CRQ] Can LLM reading Error Invariant trajectories achieve more precise + more explainable fault localization?
- [RQ1] Semantic translation accuracy: Can LLM faithfully translate invariant constraints → NL?
- [RQ2] Source localization via invariant trajectory vs. reading code directly
- [RQ3] Predicate discovery: Can LLM suggest predicates Dimovski cannot discover?
- [RQ4] Causal chain correctness: Do LLM narratives align with real fixes?
- [RQ5] Information ablation: Which invariant components are most critical?

## Target Outputs

- `paper/notes/paper_reading_notes.md` — All papers read with detailed annotations
- `paper/notes/research_development_timeline.md` — Full research evolution timeline
- `paper/notes/research_questions.md` — Updated research questions (Phase 4)
- `paper/notes/inclusion_exclusion_criteria.md` — Paper screening criteria
- `paper/matrix/literature_matrix.csv` — Literature matrix (40 papers)
- `paper/reports/comprehensive_research_summary.md` — Comprehensive research summary
- `paper/reports/evidence_map.md` — Evidence map (to be updated)
- `paper/reports/research_gaps.md` — Research gaps (to be updated)

## Infrastructure Dependency

- **Dimovski (COLA 2024)**: Iterative backward-forward abstract interpretation with BDD refinement
  - Produces Error Invariant sequences — the "text" that LLM reads
  - PDF: `C:\Users\chenm\Desktop\论文\Dimovski2024_COLA_Fault_Localization_Abstract_Interpretation.pdf`

## Key Design Principles

1. LLM does NOT do the analysis — Dimovski does
2. LLM reads the analysis's intermediate output (invariant trajectories)
3. LLM's errors affect precision only, never recall (conservative strategy)
4. Bidirectional: LLM can suggest predicates → Dimovski re-refines
5. Zero runtime overhead (all static)

## Constraints

- Do not delete or overwrite files outside `paper/` directory
- Do not fabricate DOIs, authors, years, venues
- Unverifiable information must be marked as `unknown` or `needs_manual_check`
- All extracted data must retain source filename
