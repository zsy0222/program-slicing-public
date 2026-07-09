# Literature Screening Criteria

## Research Domain

Cascaded hybrid slicing for fault localization: combining dynamic backward tracing,
static forward path validation, and runtime assertion guidance.

## Inclusion Criteria

1. **Program slicing** — Static, dynamic, hybrid, or LLM-based slicing methods
2. **Fault localization** — Slice-based fault localization, SBFL, delta debugging,
   cause transitions, or similar techniques
3. **LLM for code** — LLM-based assertion generation, program analysis, or code
   understanding (ASSERTIFY, TOGLL, Laurel, PALM, etc.)
4. **Assertion/invariant** — Assertion generation, dynamic invariant detection,
   or constraint-based debugging
5. **Hybrid analysis** — Any work combining dynamic + static program analysis
   for debugging or slicing
6. **Foundational** — Seminal papers in slicing, PDG, or fault localization
   (Weiser, Korel & Laski, Ferrante et al., etc.)
7. **Tools & benchmarks** — Program analysis frameworks (WALA, Slicer4J, dg, giri)
   relevant to implementation

## Exclusion Criteria

1. **Non-code domains** — Papers on slicing for non-software artifacts
   (natural language, databases, hardware, networks)
2. **Unrelated SE topics** — SE topics not involving program slicing, debugging,
   or fault localization
3. **Pre-2000 classics** — Only include if directly referenced by the above core
   papers or essential for foundational understanding
4. **Duplicate / superseded** — Superseded versions of the same work
   (prefer journal over conference, newer over older)
5. **Gray literature** — Blog posts, tutorials, or non-peer-reviewed technical
   reports (unless directly relevant to implementation)

## Screening Log

| Stage | Count | Date |
|-------|-------|------|
| Initial collection (paper_list.docx) | ~40 papers | 2026-07-08 |
| Title/Abstract screen | | |
| Full text review | | |
| Final included | | |
