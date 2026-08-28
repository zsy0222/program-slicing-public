# -*- coding: utf-8 -*-
import docx
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()
style = doc.styles["Normal"]
font = style.font
font.name = "Times New Roman"
style.element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")

def h(text, level=1):
    doc.add_heading(text, level=level)

def p(text, bold=False):
    para = doc.add_paragraph()
    if bold:
        run = para.add_run(text)
        run.bold = True
    else:
        para.add_run(text)
    return para

# ==================== BUILD ====================
doc.add_paragraph()
doc.add_paragraph()

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("Cascaded Hybrid Slicing\nfor Fault Localization")
run.bold = True
run.font.size = Pt(22)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sub.add_run("Research Process Documentation (Chinese)")
run.font.size = Pt(14)
run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

info = doc.add_paragraph()
info.alignment = WD_ALIGN_PARAGRAPH.CENTER
info.add_run("Start: Early 2026 | Setup: 2026-05-20 | Generated: 2026-07-12")

doc.add_page_break()

# === Chapter 1 ===
h("Chapter 1: Research Origin", 1)
h("1.1 Initial Direction", 2)
p("The research began with systematic study of program slicing. Read Weiser (1984) original slicing definition, Ferrante et al. (1987) PDG formalization, and Korel and Laski (1988) dynamic slicing pioneer work. A core limitation was found: dynamic backward slicing is transitive closure, cannot auto-stop at bug location.")
h("1.2 Chop Discovery", 2)
p("Discovered Jackson and Rollins (1994) paper on Chop while exploring forward plus backward slicing combinations. Chop uses two anchor points to constrain tracing scope. NOT simple forward-intersection-backward, but restricted reachability on PDG.")
h("1.3 Direction: Chop plus LLM", 2)
p("Made decision to combine bidirectional slicing with LLMs for automated debugging. Surveyed: WALA, dg, giri, Slicer4J, CodeQL.")

doc.add_page_break()

# === Chapter 2 ===
h("Chapter 2: Tool Foundation", 1)
h("2.1 Reference Tools", 2)
p("code2prompt (7.3k stars, Handlebars), GitIngest (4k plus stars, minimalist API), IBM CLDK (ICSE 2025, PDG analysis layer defined but backend not implemented).")
h("2.2 Chop4LLM", 2)
p("Independently developed PDG-based bidirectional slicing plus LLM prompt generation tool. Core contributions: (1) First to insert PDG-level slice in code-to-LLM pipeline; (2) True data plus control dependency beyond call-graph trimming; (3) Correct Chop algorithm (restricted reachability).")
h("2.3 Validation", 2)
p("Discount Bug (8 stmts): Chop 3 stmts (62.5 pct reduction) vs backward 6 stmts (25 pct reduction). Verified if-else preservation, KILL mechanism, no false positives.")

doc.add_page_break()

# === Chapter 3 ===
h("Chapter 3: Three Iterations", 1)
h("3.1 Phase 1: Chop4LLM", 2)
p("PDG tool plus LLM postprocessing. Problems: (1) two independent steps no synergy; (2) PDG construction quality caps pipeline; (3) LLM restricted to postprocessing.")
h("3.2 Phase 2: SWP (Slicing Workflow Paradigm)", 2)
p("LLM as slicing engine with structured 5-stage reasoning. Problem: overlaps with SliceMate multi-agent; LLM-only slicing only 60.8 pct accuracy.")
h("3.3 Phase 3: Cascaded Hybrid Slicing (Current)", 2)
p("Phase 1 (Dynamic Backward plus Assertions): LLM traces from sink backwards on execution trace, last PASS assertion equals source. Phase 2 (Static Forward plus Assertion Pruning): from source, static forward reachable, PASS branches pruned, FAIL branches kept. Core philosophy: LLM for semantic reasoning, static analysis for formal completeness.")

doc.add_page_break()

# === Chapter 4 ===
h("Chapter 4: Design Decisions", 1)
h("4.1 Core Research Question", 2)
p("Given failing test plus sink, can cascaded hybrid slicing produce fault candidate set that is: (a) smaller than MPS, (b) more complete than SliceMate, requiring only single input point?")
h("4.2 Five Sub-questions", 2)
p("[RQ1] Source localization accuracy. [RQ2] Path pruning effectiveness. [RQ3] Comparative effectiveness vs baselines. [RQ4] Assertion quality sensitivity (L0-L4). [RQ5] Cascaded vs intersected architecture.")
h("4.3 Key Difference from MPS", 2)
p("Zhang 2007 MPS: 3 input points, intersection may miss bugs. This framework: 1 input point, cascaded (sequential) architecture, theoretically more complete.")
h("4.4 Assertion Density", 2)
p("L0-L4 not monotonic. Three dimensions: accuracy, value, cost. Makes RQ4 experimental variable not preset assumption.")

doc.add_page_break()

# === Chapter 5 ===
h("Chapter 5: Literature Survey", 1)
h("5.1 Step 1: Research Questions and Screening", 2)
p("Created paper/ structure: AGENTS.md, research_questions.md, inclusion_exclusion_criteria.md, literature_matrix.csv.")
h("5.2 Step 2: Metadata Completion", 2)
p("Extracted 38 papers from paper_list.docx. Crossref API completed DOIs (26 auto, 6 manual). Added: EvoOtter, SpecCoder, TOGLL, ChatUniTest, LLMvsHuman. 38 papers across 7 clusters.")
h("5.3 Step 3: Evidence Map", 2)
p("7-cluster classification. Per-paper annotation: evidence direction, RQ mapping, strength, contradictions. Output: evidence_map.csv plus evidence_map_summary.docx (red-highlighted 17 manual-check papers). Three key contradictions: LLM-only vs static analysis, assertion quality gap, MPS completeness.")

doc.add_page_break()

# === Chapter 6 ===
h("Chapter 6: Progress and Remaining", 1)
p("COMPLETED:", bold=True)
p("Step 1 Research Questions [COMPLETE]")
p("Step 2 Metadata Completion [COMPLETE]")
p("Step 3 Evidence Map [COMPLETE]")
doc.add_paragraph()
p("REMAINING:", bold=True)
p("Step 4: Research Gap Report - identify under-studied sub-areas")
p("Step 5: Review Briefing - writable paragraph drafts")
p("Step 6: Quality Check - qa_check.py")
p("Step 7: Skill Consolidation - reusable skill directory")
p("Tool Selection: WALA vs dg vs CodeQL for Phase 2")
p("Git Push: github.com/zsy0222/program-slicing")

doc.add_page_break()

# === Chapter 7 ===
h("Chapter 7: Outputs", 1)
h("7.1 Directory Structure", 2)
p("paper/ AGENTS.md notes/research_questions.md notes/inclusion_exclusion_criteria.md matrix/literature_matrix.csv (38 papers) matrix/evidence_map.csv matrix/evidence_map_summary.docx reports/ scripts/")
h("7.2 Key Statistics", 2)
p("Total: 38 papers (7 clusters) Core supporting: 5 Contrast: 3 Manual check: 17 papers RQs: 1 CRQ plus 5 RQs Iterations: 3")

doc.add_page_break()

# === Appendix A ===
h("Appendix A: Literature Matrix", 1)
clusters = [
    ("C1: Traditional Slicing and Chop (7)", "Weiser1984, KorelLaski1988, Ferrante1987, JacksonRollins1994, ZhangGupta2004, Barros2010, MultiStageISSTA2026"),
    ("C2: Neural/LLM Slicing (4)", "SLICEFORMER2026, SLICET52025, NSSlicer2024, NDSlicer2024"),
    ("C3: Assertion Generation (6)", "ASSERTIFY2024, TOGLL2024, Laurel2024, CIll2026, PALM2025, PSCSelector2025"),
    ("C4: LLM Test Generation (6)", "EvoOtter2026, LLMvsHuman2026, SpecCoder2026, CunhaMacedo2025, ChatUniTest2023, OracleUnderstanding2026"),
    ("C5: FL Baselines (5)", "Zhang2007, SliceMate Chang2025, Shahandashti2025, Wong2016, Arora2024"),
    ("C6: Hybrid Frameworks (5)", "NESA2026, codebadger2026, code2prompt, CLDK2025, FMAgent2026"),
    ("C7: Tools (4)", "WALA, dg, giri, Slicer4J")
]
for title, desc in clusters:
    p(title, bold=True)
    p(desc)

doc.add_page_break()

# === Appendix B ===
h("Appendix B: Evidence Direction", 1)
p("Core Supporting: 5 (13.2 pct)")
p("Supporting: 12 (31.6 pct)")
p("Contrasting: 3 (7.9 pct)")
p("Neutral: 7 (18.4 pct)")
p("Foundational: 9 (23.7 pct)")
p("Manual Check: 17 (44.7 pct)")
doc.add_paragraph()
p("Support Chain:", bold=True)
p("Weiser/KorelLaski [Foundation] -> Ferrante/JacksonRollins [PDG+Chop] -> Zhang2007 [Baseline] -> Barros [Assertion Criterion] -> ASSERTIFY/TOGLL/SpecCoder [Assertion Tools] -> EvoOtter/LLMvsHuman [Test Generation] -> NESA/CLDK [Hybrid Architecture] -> Cascaded Hybrid Slicing [THIS FRAMEWORK]")

# Save
outpath = "C:/Users/chenm/Desktop/program_slicing/paper/reports/research_process_summary.docx"
doc.save(outpath)
print("SUCCESS: " + outpath)
