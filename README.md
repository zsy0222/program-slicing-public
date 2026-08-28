# Assertion-Guided Cascaded Hybrid Slicing for Fault Localization

This repository contains the research materials, original prototypes, controlled benchmarks, and reproducible summaries for an ongoing study of assertion-guided cascaded hybrid slicing and LLM-assisted fault analysis.

## Research idea

The method uses a **cascaded** two-stage analysis rather than a simple intersection of slices:

1. Dynamic backward analysis starts at an observed failure and reconstructs the executed dependency path.
2. Static forward analysis expands from candidate sources while assertions and runtime observations prune infeasible paths.
3. The resulting Error Invariant acts as both a location-mapping rule and an auditable explanation of the candidate.
4. Candidate repairs are checked with runtime counterfactual evidence, static differences, compilation, and tests.

The repository also contains a repair-oriented pilot that tests whether dynamic semantic slices become more useful to an LLM when translated into an explicit Error Invariant and constrained editing task.

## Repository map

```text
01_research/          Current framework, research questions, and workflow documentation
02_literature/        Public literature entry points and source policy
paper/                Literature matrix, evidence map, reading notes, and research reports
03_experiments/       Original prototypes, self-authored benchmarks, structured results, and reports
04_formal_tools/      Public tool inventory only; third-party source is local-only
90_local_only/        Local archive: tools, PDFs, raw model outputs, logs, QA renders, and unrelated files
```

`90_local_only/` is intentionally excluded from Git. It preserves local working material without making it part of a public release.

## Current evidence and scope

The current results are controlled pilot results, not a claim of general effectiveness on all real defects. In the first Defects4J Gson-7 comparison, the trigger-test success counts across three repeated generations were:

| Strategy | Trigger-test success |
|---|---:|
| Pure LLM with complete source | 0/3 |
| Static local context | 1/3 |
| Dynamic semantic slice without invariant | 0/3 |
| Full workflow: slice + Error Invariant + constrained edit + validation | 3/3 |

This observation motivates the hypothesis that a slice is useful as **evidence for constructing a semantic constraint**, not as a complete repair instruction by itself. Full regression and larger multi-project evaluation remain necessary.

## Reproducibility and release boundaries

- Run instructions, benchmarks, prototypes, reports, and structured evidence are kept in the public research tree.
- Third-party tools are described but not redistributed; obtain them from their official repositories.
- Original paper PDFs, API credentials, raw LLM requests/responses, execution traces, build products, and local environment files are excluded.
- Before publishing, follow [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) and review the proposed Git file list rather than staging the entire directory.

## Personal contribution

This project records the research framework, workflow design, prototype integration, seeded-fault experiments, controlled repair comparisons, evidence-trajectory analysis, and limitation discussion completed in this workspace. Third-party analysis tools remain external dependencies and are not claimed as original work.
