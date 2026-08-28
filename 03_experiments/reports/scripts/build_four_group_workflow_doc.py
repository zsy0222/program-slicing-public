from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


OUT = Path(r"C:\Users\chenm\Desktop\program_slicing\03_experiments\reports\workflow\四种修复策略对比实验工作流.docx")

BLUE = "2E74B5"
DARK_BLUE = "1F4D78"
LIGHT_BLUE = "E8EEF5"
LIGHT_GRAY = "F2F4F7"
CALL_OUT = "F4F6F9"
INK = RGBColor(11, 37, 69)


def set_font(run, name="Microsoft YaHei", size=None, bold=None, color=None, italic=None):
    run.font.name = name
    rfonts = run._element.get_or_add_rPr().get_or_add_rFonts()
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:eastAsia"), name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if italic is not None:
        run.italic = italic


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = tcPr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tcPr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = tcPr.first_child_found_in("w:tcMar")
    if tcMar is None:
        tcMar = OxmlElement("w:tcMar")
        tcPr.append(tcMar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tcMar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tcMar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths):
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tblPr = table._tbl.tblPr
    tblW = tblPr.first_child_found_in("w:tblW")
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    tblW.set(qn("w:w"), str(sum(widths)))
    tblW.set(qn("w:type"), "dxa")
    tblInd = tblPr.first_child_found_in("w:tblInd")
    if tblInd is None:
        tblInd = OxmlElement("w:tblInd")
        tblPr.append(tblInd)
    tblInd.set(qn("w:w"), "120")
    tblInd.set(qn("w:type"), "dxa")
    for row in table.rows:
        for index, cell in enumerate(row.cells):
            cell.width = Inches(widths[index] / 1440)
            tcPr = cell._tc.get_or_add_tcPr()
            tcW = tcPr.find(qn("w:tcW"))
            if tcW is None:
                tcW = OxmlElement("w:tcW")
                tcPr.append(tcW)
            tcW.set(qn("w:w"), str(widths[index]))
            tcW.set(qn("w:type"), "dxa")
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_rule(paragraph, color="2E74B5"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:space"), "6")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def add_text(doc, text, size=11, after=6, before=0, bold_prefix=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.10
    if bold_prefix and text.startswith(bold_prefix):
        r = p.add_run(bold_prefix)
        set_font(r, size=size, bold=True, color=DARK_BLUE)
        r = p.add_run(text[len(bold_prefix):])
        set_font(r, size=size)
    else:
        r = p.add_run(text)
        set_font(r, size=size)
    return p


def add_h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_font(r, size=16, bold=True, color=BLUE)
    return p


def add_h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_font(r, size=13, bold=True, color=BLUE)
    return p


def add_step(doc, number, title, body):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.10
    r = p.add_run(f"步骤 {number}  ")
    set_font(r, size=11, bold=True, color=DARK_BLUE)
    r = p.add_run(title)
    set_font(r, size=11, bold=True)
    add_text(doc, body, after=4)


def add_callout(doc, label, text):
    table = doc.add_table(rows=1, cols=1)
    set_table_geometry(table, [9360])
    cell = table.cell(0, 0)
    shade(cell, CALL_OUT)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(1)
    p.paragraph_format.line_spacing = 1.10
    r = p.add_run(label + "  ")
    set_font(r, size=10.5, bold=True, color=DARK_BLUE)
    r = p.add_run(text)
    set_font(r, size=10.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)


def add_matrix(doc):
    rows = [
        ("A 纯 LLM", "完整生产源码 + 失败信息", "无定位、无切片、无不变量", "直接生成补丁"),
        ("B 静态局部上下文", "报错位置附近的源码窗口 + 失败信息", "静态局部定位", "直接生成补丁"),
        ("C 仅动态切片", "动态语义切片 + 最小源码窗口 + 失败信息", "运行时依赖证据", "直接生成补丁"),
        ("D 完整工作流", "动态切片 + 不变量 + 编辑范围 + 失败信息", "运行时依赖、语义约束、受限修改", "受约束补丁 + 验证闭环"),
    ]
    table = doc.add_table(rows=1, cols=4)
    set_table_geometry(table, [1440, 3000, 2700, 2220])
    headers = ["组别", "提供给模型的主要信息", "额外机制", "修复输出"]
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        shade(cell, LIGHT_BLUE)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        set_font(r, size=9.5, bold=True, color=DARK_BLUE)
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(value)
            set_font(r, size=9.2, bold=(i == 0))
    return table


def add_group(doc, label, title, objective, inputs, steps, output, rationale, caution):
    add_h1(doc, f"{label}：{title}")
    add_callout(doc, "该组要回答的问题", objective)
    add_h2(doc, "输入")
    for item in inputs:
        add_text(doc, item, size=10.8, after=3)
    add_h2(doc, "工作流")
    for number, title_, body in steps:
        add_step(doc, number, title_, body)
    add_h2(doc, "输出与评价")
    add_text(doc, output, bold_prefix="输出：")
    add_h2(doc, "该组在对照中的意义")
    add_text(doc, rationale)
    add_callout(doc, "解释边界", caution)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Microsoft YaHei"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(11)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = header.add_run("实验设计说明 | LLM 辅助代码修复")
    set_font(r, size=9, color="666666")
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer.add_run("四种修复策略对比实验工作流")
    set_font(r, size=9, color="666666")

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("实验设计说明")
    set_font(r, size=11, bold=True, color=DARK_BLUE)
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("四种 LLM 代码修复策略的对比工作流")
    set_font(r, size=23, bold=True, color="000000")
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run("当前 Defects4J Gson-7 缺陷的对照实验说明")
    set_font(r, size=13, color="555555")
    rule = doc.add_paragraph()
    rule.paragraph_format.space_after = Pt(12)
    add_rule(rule)

    add_h1(doc, "一、实验目标与共同边界")
    add_text(doc, "本实验不是单纯比较“谁能修好代码”，而是逐层检验四类信息是否能帮助 LLM 更可靠地理解真实缺陷：完整源码、静态局部上下文、动态语义切片，以及由切片推导出的 Error Invariant（错误不变量）与编辑约束。")
    add_text(doc, "四组共享同一个缺陷版本、同一失败测试、同一模型设置和同一验证方式。模型均需输出可应用到缺陷版本的补丁；随后进行编译与触发测试验证。每组重复 3 次，以降低单次生成的偶然性。")
    add_callout(doc, "公平性原则", "四组的区别只在于给模型的证据和约束。所有组都获得失败信息；C 组和 D 组额外提供最小源码窗口，仅用于让模型能形成可应用补丁，不等同于给出正确修复。")

    add_h1(doc, "二、四组设置总览")
    add_matrix(doc)
    add_text(doc, "注：当前首轮结果中，Gson-7 的触发测试通过数依次为 A 组 0/3、B 组 1/3、C 组 0/3、D 组 3/3。该结果用于说明当前样本上的机制差异，不能替代更大规模的统计结论。", size=9.5, after=8)

    add_group(
        doc, "A 组", "纯 LLM（完整上下文）",
        "当模型只依赖完整源码与报错信息时，是否能自行完成定位、理解与修复？这构成最基础的 LLM 修复基线。",
        [
            "完整的生产源码文件（例如 JsonReader.java）。",
            "失败测试名称、异常类型、堆栈中的失败位置，以及简短的失败现象说明。",
            "不提供切片、不提供根因解释、不提供修改范围或不变量。",
        ],
        [
            ("1", "组织原始提示", "将完整源码和失败信息直接提供给 LLM，并要求返回统一 diff 格式的修复补丁。"),
            ("2", "模型自主推理", "LLM 自行在完整文件中寻找可疑分支、推断异常原因，并决定改动位置和改动方式。"),
            ("3", "应用补丁", "把模型输出的 diff 应用于缺陷版本；若格式错误、文件错误或冲突，则记为无效补丁。"),
            ("4", "编译与触发测试", "先检查补丁能否编译，再运行能重现该缺陷的触发测试。"),
        ],
        "输出：LLM 的原始补丁。评价：补丁是否可应用、能否编译、触发测试是否通过；首轮 Gson-7 为 0/3。",
        "它回答“不给额外方法支撑时，通用 LLM 本身能做到什么程度”，用于排除完整工作流的收益只是模型原有能力的可能性。",
        "完整源码并不必然更好：对长文件，干扰分支较多，模型可能选中表面相似但语义不相同的代码。"
    )

    add_group(
        doc, "B 组", "静态局部上下文",
        "仅缩小阅读范围是否已经足以让 LLM 修好缺陷？这代表传统“报错位置附近取代码”的上下文压缩方法。",
        [
            "失败测试、异常类型和异常位置。",
            "以异常行或静态定位行为中心截取的源码窗口，包含相邻判断、局部变量和必要的方法上下文。",
            "不提供实际运行依赖关系，不解释哪个条件被遗漏，也不限制模型最终可改的语句。",
        ],
        [
            ("1", "静态窗口定位", "根据堆栈和源代码行号，从失败点附近截取固定范围的源码，形成局部上下文。"),
            ("2", "提示 LLM 修复", "向模型说明失败现象和局部代码，要求在该类中给出最小化的修复 diff。"),
            ("3", "应用与编译", "将补丁应用到同一缺陷版本，检查是否存在语法错误、类型错误或错误的 diff 格式。"),
            ("4", "运行触发测试", "用同一失败测试判断修复是否消除了可观测错误。"),
        ],
        "输出：基于静态局部窗口的补丁。评价：与 A 组相同；首轮 Gson-7 为 1/3。",
        "它把“少给一些代码”与“真正理解运行时语义”区分开来。若 B 组提升，说明降噪有作用；但无法说明模型理解了缺陷机制。",
        "局部窗口只包含文本邻近关系。某个运行时关键条件可能在窗口内，却无法告诉模型该条件为何与本次失败有关。"
    )

    add_group(
        doc, "C 组", "仅动态语义切片",
        "动态切片本身能否把模型带到正确修复？该组单独检验“运行时依赖证据”的价值，不附加人工/规则化的根因约束。",
        [
            "失败测试和异常位置。",
            "从失败执行中提取的动态语义切片：异常点及其实际执行过的数据与控制依赖语句。",
            "围绕切片语句提供的最小源码窗口，保证模型能写出具体 diff。",
            "不提供 Error Invariant，不告诉模型遗漏的合法状态，也不预先规定可修改的条件分支。",
        ],
        [
            ("1", "重现失败", "在缺陷版本运行触发测试，获取稳定的异常位置作为切片准则。"),
            ("2", "生成动态语义切片", "使用动态切片工具追踪本次失败执行中真实发生的数据依赖与控制依赖，过滤未执行的噪声代码。"),
            ("3", "构造切片提示", "把切片中的关键语句、依赖关系和最小源码窗口提供给 LLM，要求模型自行从证据中解释根因并给出补丁。"),
            ("4", "应用与验证", "应用生成补丁，执行编译与相同的触发测试。"),
        ],
        "输出：基于动态切片证据、但没有不变量约束的补丁。评价：与 A、B 组相同；首轮 Gson-7 为 0/3。",
        "它直接检验动态切片是否“单独足够”。若 C 组未提升而 D 组提升，说明切片提供的是证据，不是 LLM 可直接执行的修复规则。",
        "动态切片告诉模型“哪些语句在本次失败中相关”，但通常不自动表达“哪类状态是合法的、分支为何漏处理、应该如何改”。"
    )

    add_group(
        doc, "D 组", "完整工作流：动态切片 + Error Invariant + 受约束修复 + 验证",
        "把运行时证据转为可解释、可执行的修复约束，是否能稳定提高 LLM 的修复成功率？这也是本研究方法的核心。",
        [
            "失败测试、异常位置和失败现象。",
            "动态语义切片及其关键数据/控制依赖。",
            "由切片与失败路径归纳得到的 Error Invariant：发生错误的状态约束，以及修复后必须保持的行为条件。",
            "允许编辑的文件与局部代码范围；禁止无关重构或绕过测试。",
        ],
        [
            ("1", "失败重现与切片", "与 C 组一致：从可复现的测试失败出发，在实际执行路径上得到语义切片。"),
            ("2", "解释切片语义", "把切片中的条件判断、状态值和异常路径进行结构化解释，明确本次错误不是发生在“哪里”，而是违反了什么行为规则。"),
            ("3", "形成 Error Invariant", "将根因写成简短约束。例如 Gson-7：合法的未加引号数值 token 必须进入整数/长整数解析路径，不能落入错误分支。"),
            ("4", "受约束生成补丁", "提示 LLM 只能在指定文件和分支附近修改，补丁必须恢复不变量，且不得通过删除测试、吞掉异常或无关重构规避问题。"),
            ("5", "自动验证与反馈", "依次执行补丁应用、编译和触发测试；不通过则记录失败原因，作为下一轮受限修复的反馈，而不是直接把失败补丁计为成功。"),
        ],
        "输出：满足错误不变量且在规定范围内的最小补丁。评价：补丁可应用、编译、触发测试，以及后续应补充的全量回归测试；首轮 Gson-7 为 3/3。",
        "它验证的不是“多给提示会不会更好”，而是完整链条是否有效：动态证据负责减少噪声，不变量负责给出语义方向，编辑约束抑制无关修改，测试负责闭环。",
        "D 组当前 3/3 是触发测试层面的结果。完整研究仍需在更多 Defects4J 缺陷、更多模型和全量回归测试上复核，才能形成稳健结论。"
    )

    add_h1(doc, "三、验证流程与结果判定")
    add_text(doc, "每一次模型输出都按照同一顺序判定：首先检查 diff 是否可应用；其次编译项目；编译成功后运行预先确定的触发测试。只有触发测试由失败转为通过，才计为一次触发修复成功。")
    add_callout(doc, "当前指标", "首轮对比表中的 0/3、1/3、0/3、3/3 均指 3 次独立生成中“编译成功且触发测试通过”的次数。它不是全量回归通过率，也不是对所有缺陷的一般化准确率。")
    add_text(doc, "完整评估应在触发测试之后继续运行项目全量回归测试，并报告：可应用率、编译率、触发修复率、全量回归通过率、平均修改行数、模型调用次数与耗时。这样可以区分“偶然让一个测试通过”与“真正没有引入新回归”的补丁。")

    add_h1(doc, "四、实验结论的正确表述")
    add_text(doc, "在当前 Gson-7 样本和 3 次重复生成下，静态局部上下文带来有限改善；仅提供动态切片并未稳定提升。加入 Error Invariant、编辑范围和测试闭环后，完整工作流在三次生成中均通过触发测试。该发现支持“切片应作为构造语义约束的证据，而非直接替代根因推理”的研究假设。")
    add_callout(doc, "下一步", "扩展到更多可稳定重现的 Defects4J 缺陷；为四组补做去重后的全量回归验证；再替换不同模型，检验工作流收益是否具有跨模型一致性。")

    doc.core_properties.title = "四种修复策略对比实验工作流"
    doc.core_properties.subject = "LLM 辅助代码修复的实验设计说明"
    doc.core_properties.author = "ChenM"
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
