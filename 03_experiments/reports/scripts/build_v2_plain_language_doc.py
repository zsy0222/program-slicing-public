from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUT = Path(__file__).with_name("V2工作流与当前实验_通俗版.docx")

BLUE = "2E74B5"
DARK_BLUE = "1F4D78"
INK = "1F2937"
MUTED = "667085"
HEADER_FILL = "E8EEF5"
CALLOUT_FILL = "F4F6F9"


def set_run_font(run, size=11, bold=None, color=INK, italic=None):
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths):
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.first_child_found_in("w:tblW")
    tbl_w.set(qn("w:w"), str(sum(widths)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.first_child_found_in("w:tblInd")
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), "120")
    tbl_ind.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for col, width in zip(grid.gridCol_lst, widths):
        col.set(qn("w:w"), str(width))
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = width
            tc_w = cell._tc.tcPr.tcW
            tc_w.set(qn("w:w"), str(width))
            tc_w.set(qn("w:type"), "dxa")
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell)


def set_paragraph_border(paragraph, color=BLUE, size="8", space="1"):
    p_pr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), space)
    bottom.set(qn("w:color"), color)
    borders.append(bottom)
    p_pr.append(borders)


def add_text(paragraph, text, size=11, bold=None, color=INK, italic=None):
    run = paragraph.add_run(text)
    set_run_font(run, size=size, bold=bold, color=color, italic=italic)
    return run


def style_doc(doc):
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor.from_string(INK)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25

    for name, size, color, before, after in (
        ("Heading 1", 16, BLUE, 18, 10),
        ("Heading 2", 13, BLUE, 14, 7),
        ("Heading 3", 12, DARK_BLUE, 10, 5),
    ):
        style = doc.styles[name]
        style.font.name = "Calibri"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.line_spacing = 1.0

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    header.paragraph_format.space_after = Pt(4)
    add_text(header, "研究进展  |  V2 工作流简要说明", size=9, color=MUTED)
    set_paragraph_border(header, color="D0D5DD", size="4")
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footer.paragraph_format.space_before = Pt(4)
    add_text(footer, "程序切片研究 · 2026-08-23", size=8.5, color=MUTED)


def add_section_heading(doc, text):
    paragraph = doc.add_paragraph(style="Heading 1")
    add_text(paragraph, text, size=16, bold=True, color=BLUE)
    return paragraph


def add_callout(doc, label, body):
    table = doc.add_table(rows=1, cols=1)
    set_table_geometry(table, [9360])
    cell = table.cell(0, 0)
    set_cell_shading(cell, CALLOUT_FILL)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    add_text(p, label + "  ", size=11, bold=True, color=DARK_BLUE)
    add_text(p, body, size=11, color=INK)
    return table


def fill_header_cell(cell, text):
    set_cell_shading(cell, HEADER_FILL)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(0)
    add_text(p, text, size=10, bold=True, color=DARK_BLUE)


def fill_body_cell(cell, text, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = cell.paragraphs[0]
    p.alignment = align
    p.paragraph_format.space_after = Pt(0)
    add_text(p, text, size=10.5, color=INK)


def build():
    doc = Document()
    style_doc(doc)
    core = doc.core_properties
    core.title = "V2工作流与当前实验（通俗版）"
    core.subject = "LLM、语义切片与 Error Invariant 的实验流程说明"
    core.author = "程序切片研究项目"

    title = doc.add_paragraph()
    title.paragraph_format.space_before = Pt(18)
    title.paragraph_format.space_after = Pt(4)
    add_text(title, "V2 工作流与当前实验", size=23, bold=True, color="0B2545")
    subtitle = doc.add_paragraph()
    subtitle.paragraph_format.space_after = Pt(14)
    add_text(subtitle, "通俗版：让 LLM 找候选，让静态分析负责核对和验证", size=12.5, color=MUTED)
    rule = doc.add_paragraph()
    rule.paragraph_format.space_after = Pt(10)
    set_paragraph_border(rule, color=BLUE, size="10")

    add_callout(
        doc,
        "一句话理解：",
        "V2 不是让模型凭轨迹直接宣布“根因”。它先从源码和语义切片提出几个可能位置，"
        "再用 Error Invariant 轨迹检查这些说法是否对得上，最后用运行和静态分析验证候选能否消除错误路径。",
    )

    add_section_heading(doc, "1. 现在的 V2 工作流")
    p = doc.add_paragraph()
    add_text(p, "目标是把“猜测故障位置”变成一个可核查的闭环。流程如下：", size=11)

    flow = doc.add_table(rows=1, cols=3)
    set_table_geometry(flow, [1300, 2300, 5760])
    for cell, text in zip(flow.rows[0].cells, ["步骤", "输入 / 动作", "通俗解释"]):
        fill_header_cell(cell, text)
    steps = [
        ("1", "故障程序 + 失败断言", "从一个实际会失败的 C 程序开始。"),
        ("2", "Error Invariant 分析", "工具给出语义切片和“错误状态如何到达”的静态轨迹。"),
        ("3", "LLM 生成候选", "模型阅读源码和切片，列出最多三个可能位置，并区分根因、机制、条件。"),
        ("4", "证据与位置核对", "检查模型引用的 L-ID 是否真的对应它声称的源码行；不对应就反馈重答一次。"),
        ("5", "运行时反事实验证", "把候选替换到独立副本，编译并运行，确认断言是否真的不再失败。"),
        ("6", "静态差分验证", "对通过运行的代表候选再跑 Error Invariant；若最终全为 bottom，说明该错误路径已消失。"),
    ]
    for number, action, explanation in steps:
        cells = flow.add_row().cells
        fill_body_cell(cells[0], number, WD_ALIGN_PARAGRAPH.CENTER)
        fill_body_cell(cells[1], action)
        fill_body_cell(cells[2], explanation)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(0)
    add_text(p, "Error Invariant 的作用：", size=10.5, bold=True, color=DARK_BLUE)
    add_text(p, "它不是直接替模型判定根因，而是提供“错误机制与位置”的审计证据，并在最后验证错误路径是否真的被消除。", size=10.5)

    add_section_heading(doc, "2. 目前做了哪些实验")
    p = doc.add_paragraph()
    add_text(p, "我们使用了 11 个单行故障对：错误版会触发断言，正确参考版能正常运行。每个 LLM 条件独立运行 3 次。", size=11)

    results = doc.add_table(rows=1, cols=4)
    set_table_geometry(results, [3000, 1850, 1850, 2660])
    for cell, text in zip(results.rows[0].cells, ["条件", "Top-1 定位", "契约合格", "说明"]):
        fill_header_cell(cell, text)
    rows = [
        ("纯工具：Error Invariant 启发式", "27.3%", "不适用", "只看直接写入错误变量的位置。"),
        ("P-V2a：源码 + 切片 + 角色", "54.5%", "100%", "模型能更常找到正确行，但角色判断仍会混淆。"),
        ("P-V2b：再加入轨迹与位置映射", "60.6%", "87.9%", "定位略有提升；轨迹主要帮助核对位置和机制。"),
    ]
    for row in rows:
        cells = results.add_row().cells
        for cell, text in zip(cells, row):
            fill_body_cell(cell, text)

    add_callout(
        doc,
        "验证结果：",
        "闭环共检查了 84 个模型候选，其中 71 个能消除运行时断言失败。按每个案例的多数 Top-1 选择代表候选后，"
        "7 个候选先通过运行时验证，随后 7 个都通过静态 Error Invariant 差分验证。",
    )

    add_section_heading(doc, "3. 现在能说明什么，不能说明什么")
    claim = doc.add_table(rows=1, cols=2)
    set_table_geometry(claim, [4680, 4680])
    for cell, text in zip(claim.rows[0].cells, ["现在可以说明", "现在还不能说明"]):
        fill_header_cell(cell, text)
    cells = claim.add_row().cells
    fill_body_cell(cells[0], "V2 比纯工具更容易找到与真实故障相近的位置；并且能用运行时和静态分析双重验证一个候选是否消除了当前错误路径。")
    fill_body_cell(cells[1], "“断言通过”不等于“找到了开发者原本想修改的唯一代码”。不同的替代修改也可能让当前断言通过。")

    add_section_heading(doc, "4. 下一步")
    p = doc.add_paragraph()
    add_text(p, "第一，", size=11, bold=True, color=DARK_BLUE)
    add_text(p, "为每个案例补充能区分替代修复的回归测试或额外规格，避免只用一条断言判断“修复正确”。", size=11)
    p = doc.add_paragraph()
    add_text(p, "第二，", size=11, bold=True, color=DARK_BLUE)
    add_text(p, "在真实缺陷或更大基准上重复相同流程，检验结论是否仍成立。", size=11)

    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
