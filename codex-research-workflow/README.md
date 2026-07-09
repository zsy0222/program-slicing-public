# Codex Research Workflow Template

A standardized project template for systematic literature reviews using Codex.

## Project Structure

Project files:
- AGENTS.md — Project specification with research goals and rules
- .env.local — Sensitive config (API keys), never committed
- .gitignore — Git ignore rules

Data directories:
- data/raw-pdfs/ — Original PDFs (read-only)
- data/references/ — BibTeX, RIS, DOI lists
- data/extracted/ — Extracted text and metadata JSON

Working directories:
- notes/ — Reading notes, research questions, screening criteria
- scripts/ — fetch_metadata.py, qa_check.py
- reports/ — Evidence map, research gaps, review briefs
- matrix/ — Literature matrix CSV/Excel
- skills/ — Reusable Codex Skill definitions

## Workflow Steps

1. **Define scope** — Write research questions in notes/research_questions.md
2. **Collect materials** — PDFs to data/raw-pdfs/, DOIs to data/references/
3. **Set rules** — Configure AGENTS.md with field definitions and constraints
4. **Pilot** — Process 3 sample papers to validate the workflow
5. **Extract** — Run fetch_metadata.py for DOI metadata enrichment
6. **Build matrix** — Extract key findings, quotes, and classifications
7. **Map evidence** — Generate evidence_map.md and research_gaps.md
8. **QA** — Run qa_check.py to verify matrix quality
9. **Freeze** — Save stable workflow as a Skill in skills/

## Key Rules

- Raw PDFs are read-only — never modify data/raw-pdfs/
- Never fabricate DOIs, authors, page numbers, or citations
- Unknown values must be marked as "unknown"
- API keys go in .env.local, never in code or logs
- Pilot with 3 papers before batch processing
- QA every output before writing conclusions
- Freeze repeatable processes as Skills
