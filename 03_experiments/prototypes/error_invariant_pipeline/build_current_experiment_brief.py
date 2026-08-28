from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

OUT = Path(__file__).resolve().parents[3] / '03_experiments' / 'outputs' / '当前实验进展简报.docx'
BLUE = '2E74B5'; DARK = '1F4D78'; LIGHT = 'F2F4F7'

def set_font(run, name='Microsoft YaHei', size=11, bold=False, color=None):
    run.font.name = name; run._element.rPr.rFonts.set(qn('w:eastAsia'), name)
    run.font.size = Pt(size); run.bold = bold
    if color: run.font.color.rgb = RGBColor.from_string(color)

def shade(cell, color):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd'); shd.set(qn('w:fill'), color); tcPr.append(shd)

def set_cell_width(cell, dxa):
    tcPr = cell._tc.get_or_add_tcPr(); tcW = tcPr.find(qn('w:tcW'))
    if tcW is None: tcW = OxmlElement('w:tcW'); tcPr.append(tcW)
    tcW.set(qn('w:w'), str(dxa)); tcW.set(qn('w:type'), 'dxa')

def fixed_table(table, widths):
    table.alignment = WD_TABLE_ALIGNMENT.LEFT; table.autofit = False
    tblPr = table._tbl.tblPr; tblW = tblPr.first_child_found_in('w:tblW'); tblW.set(qn('w:w'), '9360'); tblW.set(qn('w:type'), 'dxa')
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            set_cell_width(cell, width); cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(2); p.paragraph_format.space_before = Pt(2)

def add_bullet(doc, text):
    p = doc.add_paragraph(style='List Bullet'); p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text); set_font(r); return p

def main():
    doc = Document(); sec = doc.sections[0]
    sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Inches(1)
    sec.header_distance = sec.footer_distance = Inches(.492)
    normal = doc.styles['Normal']; normal.font.name='Microsoft YaHei'; normal._element.rPr.rFonts.set(qn('w:eastAsia'),'Microsoft YaHei'); normal.font.size=Pt(11)
    normal.paragraph_format.space_after=Pt(6); normal.paragraph_format.line_spacing=1.10
    for sty,size,color,before,after in [('Heading 1',16,BLUE,16,8),('Heading 2',13,BLUE,12,6)]:
        s=doc.styles[sty]; s.font.name='Microsoft YaHei'; s._element.rPr.rFonts.set(qn('w:eastAsia'),'Microsoft YaHei'); s.font.size=Pt(size); s.font.color.rgb=RGBColor.from_string(color); s.paragraph_format.space_before=Pt(before); s.paragraph_format.space_after=Pt(after)
    title=doc.add_paragraph(); title.paragraph_format.space_after=Pt(4); r=title.add_run('当前实验进展简报'); set_font(r,size=20,bold=True,color=DARK)
    sub=doc.add_paragraph(); sub.paragraph_format.space_after=Pt(12); r=sub.add_run('主题：语义切片、测试行为契约与 LLM 闭环代码修复'); set_font(r,size=10,color='555555')
    doc.add_heading('一、研究目标',level=1)
    p=doc.add_paragraph('研究目标是：在大型项目源码较长的情况下，利用动态语义切片帮助 LLM 聚焦故障相关代码；再将项目原有失败测试自动转化为修复必须满足的行为契约，并通过验证闭环提高修复可靠性。')
    doc.add_heading('二、实验怎么做',level=1)
    for x in ['选取 3 个真实历史缺陷：JacksonDatabind 3b、Gson Reader 4b、Gson Writer 4b。','先运行项目原有触发测试复现错误，再用 Slicer4J 从失败路径反向生成动态切片。','定位对比：完整相关类（纯 LLM）、动态切片、动态切片加证据引用。','修复对比：自由文本补丁，及“完整测试契约 + 受限语法编辑块选择”的新方案。','验证分两层：原触发测试；以及与正确语义控制比较的 Maven 全量回归。']:
        add_bullet(doc,x)
    doc.add_heading('三、关键结果',level=1)
    table=doc.add_table(rows=1, cols=4); table.style='Table Grid'; fixed_table(table,[2300,2200,2400,2460])
    headers=['指标','JacksonDatabind 3b','Gson Reader 4b','Gson Writer 4b']
    for c,t in zip(table.rows[0].cells,headers): shade(c,LIGHT); p=c.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run(t); set_font(r,size=9,bold=True,color=DARK)
    rows=[('切片后输入量变化','约减少 74%','约减少 93%','约减少 93%'),('G7 受限编辑触发测试','不重复','3/3 通过','3/3 通过'),('全量回归对照','环境旧版兼容性受限','3/3 与正确控制失败集合一致','3/3 与正确控制失败集合一致')]
    for row in rows:
        cells=table.add_row().cells
        for c,t in zip(cells,row):
            p=c.paragraphs[0]; r=p.add_run(t); set_font(r,size=9)
    doc.add_paragraph('定位阶段中，动态切片使模型输入大幅变短，同时仍落在参考修改区域；增加证据约束后，模型的判断可以追溯到具体切片行。',style='Normal')
    doc.add_heading('四、目前结论',level=1)
    for x in ['语义切片的主要价值是：减少 74%–93% 的无关上下文，同时保持本批真实案例中的定位效果。','自由生成 Java 补丁容易出现范围错误、漏改分支或编译失败。','新方案让模型只选择切片导出的完整语法编辑块，系统负责精确应用；在两个 Gson 场景中，6/6 通过触发测试，且全量测试表现与正确语义控制一致。']:
        add_bullet(doc,x)
    doc.add_heading('五、下一步',level=1)
    for x in ['自动化生成更多候选 AST/语法编辑单元，避免当前原型只覆盖少数类型。','扩展至更多 Defects4J 真实缺陷，并报告定位、编译、触发测试、回归一致性、成本和失败类型。','在可用的其他模型上重复同一对照；GLM 对照目前因 API 认证问题暂未完成。']:
        add_bullet(doc,x)
    footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT; r=footer.add_run('实验进展简报 | 2026-08-23'); set_font(r,size=8,color='777777')
    OUT.parent.mkdir(parents=True,exist_ok=True); doc.save(OUT); print(OUT)
if __name__=='__main__': main()
