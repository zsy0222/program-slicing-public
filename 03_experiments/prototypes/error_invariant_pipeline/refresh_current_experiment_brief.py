from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUT = Path(r"C:\Users\chenm\Desktop\program_slicing\03_experiments\outputs\当前实验进展简报_更新版.docx")
BLUE = "1F4E79"
MID = "D9EAF7"
PALE = "EEF5FB"
GRAY = "666666"


def font(run, size=10.5, bold=False, color=None):
    run.font.name = "Microsoft YaHei"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    run.font.size = Pt(size)
    run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def shade(cell, color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), color)
    tc_pr.append(shd)


def cell_width(cell, dxa):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(dxa))
    tc_w.set(qn("w:type"), "dxa")


def table_geometry(table, widths):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.first_child_found_in("w:tblW")
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths)))
    tbl_w.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for col, width in zip(grid.gridCol_lst, widths):
        col.set(qn("w:w"), str(width))
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell_width(cell, width)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell.margin_top = 100
            cell.margin_bottom = 100
            cell.margin_left = 120
            cell.margin_right = 120


def add_text(doc, text, before=0, after=5):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.25
    font(p.add_run(text))
    return p


def add_step(doc, text):
    p = doc.add_paragraph(style="List Number")
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    font(p.add_run(text), size=10)
    return p


def add_bullet(doc, text):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.12
    font(p.add_run(text), size=10)
    return p


def main():
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.62)
    sec.bottom_margin = Inches(0.58)
    sec.left_margin = Inches(0.70)
    sec.right_margin = Inches(0.70)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Microsoft YaHei"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(10.5)
    for name, size in [("Heading 1", 13), ("Heading 2", 11)]:
        st = styles[name]
        st.font.name = "Microsoft YaHei"
        st._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor.from_string(BLUE)
        st.paragraph_format.space_before = Pt(7)
        st.paragraph_format.space_after = Pt(3)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(1)
    font(p.add_run("当前实验进展简报"), size=19, bold=True, color=BLUE)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    font(p.add_run("动态语义切片 + 测试行为契约 + 受限编辑的 LLM 代码修复闭环"), size=10, color=GRAY)

    callout = doc.add_table(rows=1, cols=1)
    table_geometry(callout, [9360])
    shade(callout.cell(0, 0), PALE)
    p = callout.cell(0, 0).paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("阶段结论：当前原型已验证“先压缩相关源码，再让模型选择可执行编辑，最后以原有测试和回归测试收口”的闭环可行性。它不是让 LLM 直接自由写补丁，而是把模型放在可追溯、可验证的决策环节。")
    font(r, size=10.2, bold=True, color=BLUE)

    doc.add_heading("一、研究目标：解决大项目中的理解与修改失真", level=1)
    add_text(doc, "当项目代码很长时，LLM 若直接阅读整类或整仓库，容易被无关上下文干扰，产生定位漂移或修改范围过大。本研究的目标是：利用一次真实失败测试产生的运行轨迹，自动压缩出与故障有关的语义代码片段，并让后续修复始终受测试行为与语法边界约束。")
    add_text(doc, "这里的“Error Invariant/测试行为契约”不是人工插入断言；它由已有失败测试和执行结果自动整理，例如失败的测试、异常或输出行为、以及修复后必须恢复的行为。它的作用是把“改得像”变成“满足可检查的行为要求”。", after=4)

    doc.add_heading("二、当前工作流：从失败测试到可验证修复", level=1)
    steps = [
        "触发故障：运行项目原有的失败测试，保留失败现象、栈信息和运行状态；不要求研究者额外手工写断言。",
        "生成动态语义切片：Slicer4J 沿失败相关变量、分支和调用链回溯，只保留对该错误可能有因果影响的源码语句。",
        "构造模型输入：将切片映射回源码，并附上可追溯的证据位置与测试行为契约。模型看到的是“相关代码 + 为什么相关”，而不是无边界的大段源码。",
        "定位与编辑决策：模型判断可疑位置，并从切片导出的完整语法编辑块中选择操作。新方案不让模型随意生成 Java 文本，系统负责精确应用所选编辑。",
        "验证与闭环：先运行原始触发测试，再运行 Maven 全量回归；若不通过，反馈失败类型并限制下一轮候选，直至得到可复核结果。",
    ]
    for item in steps:
        add_step(doc, item)

    doc.add_heading("三、实验如何对照", level=1)
    add_text(doc, "当前选取 3 个 Defects4J 真实历史缺陷：JacksonDatabind-3、Gson Reader-4、Gson Writer-4。定位阶段比较“纯 LLM 阅读完整相关类”“LLM 阅读动态切片”“切片 + 证据引用”；修复阶段比较自由生成补丁与受限语法编辑。所有结果均以原始触发测试和全量回归为准。", after=3)

    doc.add_page_break()
    doc.add_heading("四、目前实验成果", level=1)
    table = doc.add_table(rows=1, cols=4)
    table_geometry(table, [2140, 2350, 2430, 2440])
    headers = ["指标", "JacksonDatabind-3", "Gson Reader-4", "Gson Writer-4"]
    for cell, text in zip(table.rows[0].cells, headers):
        shade(cell, MID)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        font(p.add_run(text), size=9.2, bold=True, color=BLUE)
    rows = [
        ("切片输入量变化", "约减少 74%", "约减少 93%", "约减少 93%"),
        ("定位结果", "保持在参考修改区域", "保持在参考修改区域", "保持在参考修改区域"),
        ("自由生成补丁", "触发测试 3/3 通过", "0/3 通过", "0/3 通过（含编译问题）"),
        ("G7 受限编辑", "本轮不重复", "3/3 触发测试通过", "3/3 触发测试通过"),
        ("回归验证", "旧版兼容性限制", "3/3 与正确控制一致", "3/3 与正确控制一致"),
    ]
    for row in rows:
        cells = table.add_row().cells
        for i, (cell, text) in enumerate(zip(cells, row)):
            if i == 0:
                shade(cell, PALE)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i else WD_ALIGN_PARAGRAPH.LEFT
            font(p.add_run(text), size=8.7, bold=(i == 0))

    doc.add_heading("五、结果说明", level=1)
    for item in [
        "语义切片的直接收益已经清晰：在三条真实缺陷路径中，输入上下文减少 74% - 93%，而模型仍能把注意力放在参考修改区域。",
        "仅靠“自由写 Java 补丁”并不稳定：Gson 两个场景中出现修改范围不完整、分支遗漏或编译失败，说明定位正确不等于能够可靠实施修复。",
        "受限编辑把模型职责改为“选择正确的编辑单元”，把精确改写交给系统执行。在两个 Gson 场景中，6/6 次触发测试通过；每个结果的全量回归表现都与离线正确语义控制一致。",
        "因此，当前证据支持工作流的可行性，但尚不足以宣称普遍优于所有 LLM 修复方法：样本仍只有 3 个真实缺陷，后续需要扩大基准和模型范围。",
    ]:
        add_bullet(doc, item)

    doc.add_heading("六、下一步实验", level=1)
    for item in [
        "将受限编辑单元自动化为 AST/语法块候选，减少人为预设候选的影响。",
        "扩展到更多 Defects4J 缺陷，并统一统计定位命中、编译率、触发测试、回归一致性、令牌成本和失败类型。",
        "在不同模型上执行完全相同的对照，验证收益来自工作流，而不是单一模型或单一案例。",
    ]:
        add_bullet(doc, item)

    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    font(footer.add_run("实验进展简报 | 2026-08-23"), size=8, color=GRAY)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
