# Cascaded Hybrid Slicing Research

A research project on **assertion-guided cascaded hybrid slicing** for fault localization.

## Current Progress

### Research Framework

A two-phase cascaded architecture for fault localization:

- **Phase 1 (Dynamic Backward)**: Scans execution trace from sink (assertion failure point) backward, identifying the last correct value point as the bug source.
- **Phase 2 (Static Forward)**: From the source, traverses all program paths forward, using runtime assertion results for path pruning (assertion PASS = correct, prune; assertion FAIL = retain).

### Key Features

- Single input point (sink) — unlike Zhang 2007 MPS requiring three criteria
- Cascaded not intersected — Phase 1 output feeds Phase 2 input, avoiding information loss
- Assertion-guided path pruning — runtime assertion results as objective decision signals
- LLM-constrained role — LLM limited to Phase 1 source hypothesis generation

## Project Structure

```
.
├── paper/                      # Literature review workflow
│   ├── AGENTS.md              # Project rules
│   ├── notes/                 # Research questions, screening criteria
│   ├── matrix/                # Literature matrix (38 papers)
│   ├── reports/               # Evidence map, research gaps
│   └── scripts/               # Metadata fetch, QA scripts
├── codex-research-workflow/   # Reusable workflow template
├── chop4llm/                  # Initial prototype
├── swp_harness/               # SWP harness
├── WALA/                      # Program analysis framework
├── dg/                        # LLVM PDG tool
├── giri/                      # LLVM dynamic slicing tool
├── Slicer4J/                  # Java slicing benchmark
└── reference-tools/           # Reference implementations
```

## Literature Matrix

Currently **38 papers** across 6 categories:

- **A**: Core papers on local disk (6)
- **B**: LLM-based slicing (4)
- **C**: Assertion / Oracle / Invariant (12)
- **D**: Foundational slicing (6)
- **E**: LLM + Code / Tools (6)
- **F**: Implementation tools (4)

## Research Questions

See `paper/notes/research_questions.md` for full definitions.

- [CRQ] Can cascaded hybrid slicing produce more complete fault candidate sets than MPS?
- [RQ1] Source localization accuracy of assertion-guided dynamic backward?
- [RQ2] Assertion density effectiveness (cost-quality non-monotonic relationship)?
- [RQ3] Comparative effectiveness vs MPS, SliceMate, SBFL?
- [RQ4] Sensitivity to assertion quality and cost?
- [RQ5] Cascaded vs. intersected architecture?

## Generated Documents

- `hybrid_slicing_plan.docx` — Full research plan with 5 experiments
- `framework_desc.docx` — Detailed framework description
- `workflow_overview.docx` — Workflow overview
- `paper_list.docx` — Full paper list (167 entries)
- `research_log.md` — Ongoing research log
