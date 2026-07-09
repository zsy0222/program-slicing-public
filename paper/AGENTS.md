# Cascaded Hybrid Slicing Research Project

## Background

I am researching a cascaded hybrid slicing framework that combines assertion-guided dynamic backward tracing (Phase 1) with assertion-guided static forward path validation (Phase 2) for fault localization. The framework uses runtime assertion results as decision signals for path pruning.

## Research Questions

See `notes/research_questions.md` for full RQ definitions.

- [CRQ] Cascaded hybrid slicing: smaller slice + more complete than MPS/LLM-only?
- [RQ1] Source localization accuracy of assertion-guided dynamic backward?
- [RQ2] Path pruning effectiveness of assertion-guided static forward?
- [RQ3] Comparative effectiveness vs MPS, SliceMate, SBFL?
- [RQ4] Sensitivity to assertion quality?
- [RQ5] Cascaded vs. intersected architecture?

## Target Outputs

- `paper/notes/research_questions.md` — Research questions and design decisions
- `paper/notes/inclusion_exclusion_criteria.md` — Paper screening criteria
- `paper/matrix/literature_matrix.csv` — Literature matrix
- `paper/matrix/seed_references.csv` — Seed reference list
- `paper/reports/evidence_map.md` — Evidence map
- `paper/reports/research_gaps.md` — Research gaps report
- `paper/reports/literature_review_brief.md` — Review brief

## Constraints

- Do not delete or overwrite files outside `paper/` directory
- Do not fabricate DOIs, authors, years, venues, or page numbers
- Unverifiable information must be marked as `unknown` or `needs_manual_check`
- All extracted data must retain source filename
- `.env.local` must not be committed to version control
- API keys read from `.env.local`, never written to code or logs

## Literature Matrix Fields

| Field | Required | Description |
|-------|----------|-------------|
| citation_key | Yes | Citation key |
| title | Yes | Paper title |
| authors | Yes | Author list |
| year | Yes | Publication year |
| venue | Yes | Journal/conference/arXiv |
| doi | Yes | Digital Object Identifier |
| category | Yes | Paper category (A-F) |
| research_question | No | Which RQ this paper addresses |
| method | Yes | Research method |
| key_findings | Yes | Key findings |
| relevance | Yes | Relevance to this review |
| confidence | Yes | Confidence in extraction |
| manual_check_needed | Yes | Needs human review |

## Work Habits

- Write scripts before batch processing
- Run 3-paper pilot before full batch
- Verify file existence before each output
- Never write uncertain conclusions as facts
- Before modifying matrix structure, explain impact
