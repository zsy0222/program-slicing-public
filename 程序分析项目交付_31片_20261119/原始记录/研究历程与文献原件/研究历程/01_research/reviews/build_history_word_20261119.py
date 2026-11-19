"""Create dated Word copies of the project's saved research documents."""
from pathlib import Path
import re
import subprocess
from urllib.parse import urlparse
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / '01_research' / 'reviews'
OUT = REVIEW / 'Word交付_20261119'

EARLY = '''# 补充：2026 年 4—8 月的早期项目历程与资料位置

本节按现存研究日志、回顾文档和版本记录重建。时间线中关于 4 月的说法来自后来整理的回顾，不是已经找到的 4 月当月原始会议纪要；文件时间和 Git 提交时间也不等于研究真正开始的日期。历史设想、未经独立复核的比较与后来的实际实验结论应分开阅读。

## 2026 年初至 4 月：研究起点

《程序切片科研过程记录》写明研究在 2026 年初开始，前期包括程序切片、依赖图与相关论文阅读。另一份最后更新于 2026 年 7 月 18 日的《研究发展全过程》将发现 Chop 列在 2026 年 4 月，并描述将双向切片与大模型用于自动化调试的早期思路。这是后续回顾中对 4 月的定位，并未发现可据此核实具体日期、出席者或决议的当月会议记录。

资料：paper/notes/research_development_timeline.md；90_local_only/legacy/early_framework_documents/research_log.md。后者也保存在 Git 的 master 历史提交 0999878 的根目录 research_log.md。

## 2026 年 5—6 月：工具调研与 Chop4LLM

研究日志自述从 5 月 20 日开始正式记录环境与工具开发，最后更新至 6 月 6 日。日志记述了对 WALA、dg、giri、Slicer4J、CLDK 等工具的调研，以及 Chop4LLM 的程序依赖图和受限可达性设计；其中列出四个小测试案例。Discount 案例记为 8 条原始语句、6 条后向切片和 3 条 Chop 语句。这是早期工具样例的记录，不是后续大规模模型实验，也不能外推为普遍性能。

本地 Git 中 main 最早提交 96e7ecf 的提交日期为 5 月 23 日，内容为初始提交。这只能证明该提交的版本历史，不能证明研究从当天才开始。

## 2026 年 6 月底至 7 月：研究方案转向

7 月 18 日回顾文档描述了从 Chop4LLM 向让 LLM 参与切片推理的 SWP 探索，继而转向断言引导的级联混合切片，又在方案评审后考虑 Error Invariant 轨迹与 LLM 的结合。回顾记录提到曾与学长讨论设计问题，但未给出完整会议日期、参会者、逐项决议和原始纪要，不能将其补写成一场已核实的正式会议。

7 月 9 日 master 提交 0999878 保存了早期框架、代码、研究日志及若干 Word 文档；项目另有本地 .mygit 历史提交 6242d42（同日），它是单独的本地版本库记录，不应与普通 .git 提交混成一个提交。远程 GitHub 可见 main、master 和 codex/reorganize-research-workspace 三个分支，master 保留的内容不能仅从 main 的初始提交判断。

本地早期 Word 文档目录：90_local_only/legacy/early_framework_documents/。其中包括 framework_desc.docx、hybrid_slicing_plan.docx、program_slicing_updated.docx、workflow_overview.docx；另有文献列表 90_local_only/literature_sources/sources/paper_list.docx。不同文件的修改时间、版本和来源应分别核对，不把目录中所有版本推断为同日生成。

## 2026 年 8 月及之后：工作区整理与结果审查

2026 年 8 月 28 日的 c87e0a0 记录研究工作区整理。此后项目逐渐形成当前研究框架、可追溯实验设计与证据审查；9—11 月的具体节点见本文后续章节。早期提出的 Error Invariant 闭环是研究方案，不等于已证明最终 BP17 对照使用原论文 EI。

## 资料位置与会议资料缺口

- 本地项目根目录：C:/Users/chenm/Desktop/program_slicing。
- 早期日志：90_local_only/legacy/early_framework_documents/research_log.md。
- 早期回顾：paper/notes/research_development_timeline.md。
- 早期 Word 资料：90_local_only/legacy/early_framework_documents/；文献列表见 90_local_only/literature_sources/sources/paper_list.docx。
- GitHub 私有仓库：https://github.com/zsy0222/program-slicing；核对分支 main、master、codex/reorganize-research-workspace。该仓库需有权限才能访问。
- 已查询该仓库可见议题与拉取请求，查询结果为空；这不证明其他平台、其他仓库、本地聊天或未纳入搜索范围的会议资料不存在。
- 尚未取得每次会议的完整原始记录。需要以录音、聊天导出或实际纪要补齐日期、参会者、决定和待办；不得根据一般项目进展虚构会议。

'''

def add_link(p, label, target):
    part = p.part
    rid = part.relate_to(target, RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
    link = OxmlElement('w:hyperlink')
    link.set(qn('r:id'), rid)
    run = OxmlElement('w:r')
    props = OxmlElement('w:rPr')
    color = OxmlElement('w:color'); color.set(qn('w:val'), '245C80'); props.append(color)
    run.append(props)
    text = OxmlElement('w:t'); text.text = label; run.append(text); link.append(run)
    p._p.append(link)

def inline(p, s, base):
    # Keep the source document's emphasis readable and preserve links as links.
    pat = re.compile(r'\[([^\]]+)\]\(([^)]+)\)|(\*\*([^*]+)\*\*)|(`([^`]+)`)' )
    end = 0
    for m in pat.finditer(s):
        p.add_run(s[end:m.start()])
        if m.group(1) is not None:
            target = m.group(2)
            if not urlparse(target).scheme:
                target = (base / target).resolve().as_uri()
            add_link(p, m.group(1), target)
        elif m.group(4) is not None:
            p.add_run(m.group(4)).bold = True
        else:
            p.add_run(m.group(6))
        end = m.end()
    p.add_run(s[end:])

def set_font(style, name='Microsoft YaHei', size=11):
    style.font.name = name; style.font.size = Pt(size)
    style._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), name)

def new_doc():
    d = Document(); sec = d.sections[0]
    sec.page_width = Inches(8.5); sec.page_height = Inches(11)
    sec.left_margin = sec.right_margin = Inches(.85)
    sec.top_margin = sec.bottom_margin = Inches(.78)
    set_font(d.styles['Normal']); d.styles['Normal'].paragraph_format.space_after = Pt(6)
    d.styles['Normal'].paragraph_format.line_spacing = 1.2
    for name, size in [('Title',21),('Heading 1',16),('Heading 2',13),('Heading 3',11.5)]:
        set_font(d.styles[name], size=size)
        d.styles[name].font.color.rgb = RGBColor.from_string('173F57')
    return d

def table_row_repeat(row):
    trpr = row._tr.get_or_add_trPr(); el = OxmlElement('w:tblHeader'); el.set(qn('w:val'),'true'); trpr.append(el)

def render_markdown(d, content, base, first_title=True):
    lines=content.splitlines(); i=0; code=False; first=first_title
    while i < len(lines):
        line=lines[i]; stripped=line.strip(); i += 1
        if stripped.startswith('```'):
            code = not code; continue
        if not stripped or stripped == '---': continue
        if code:
            p=d.add_paragraph(); p.paragraph_format.space_after=Pt(0)
            r=p.add_run(line); r.font.name='Consolas'; r.font.size=Pt(8.5)
            continue
        if stripped.startswith('|') and i < len(lines) and re.match(r'^\s*\|[\s:\-|]+\|\s*$',lines[i]):
            rows=[[c.strip() for c in stripped.strip('|').split('|')]]; i += 1
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            count=max(map(len,rows)); table=d.add_table(rows=0,cols=count); table.style='Table Grid'; table.autofit=True
            for j,row in enumerate(rows):
                cells=table.add_row().cells
                if j==0: table_row_repeat(table.rows[-1])
                for k,value in enumerate(row):
                    p=cells[k].paragraphs[0]; p.paragraph_format.space_after=Pt(2); inline(p,value,base)
                    for run in p.runs:
                        run.font.size=Pt(9)
                        if j==0: run.bold=True
            d.add_paragraph().paragraph_format.space_after=Pt(2)
            continue
        m=re.match(r'^(#{1,4})\s+(.*)',stripped)
        if m:
            level=len(m.group(1)); style='Title' if first and level==1 else 'Heading '+str(min(level,3))
            p=d.add_paragraph(style=style); inline(p,m.group(2),base); first=False; continue
        bullet=re.match(r'^[-*]\s+(.*)',stripped)
        if bullet:
            p=d.add_paragraph(style='List Bullet'); inline(p,bullet.group(1),base); continue
        numbered=re.match(r'^\d+\.\s+(.*)',stripped)
        if numbered:
            p=d.add_paragraph(style='List Number'); inline(p,numbered.group(1),base); continue
        if stripped.startswith('>'): stripped=stripped.lstrip('> ')
        p=d.add_paragraph(); inline(p,stripped,base)

def main():
    OUT.mkdir(exist_ok=True)
    entries=[
      ('项目综合报告_20261118_v1.md','01_项目综合报告.docx',False),
      ('项目历程与会议记录_20261118_v1.md','02_项目历程与会议记录.docx',True),
      ('结论性论文草稿_20261118_v1.md','03_结论性论文草稿.docx',False),
    ]
    for source,name,prepend in entries:
        d=new_doc()
        if prepend: render_markdown(d,EARLY,ROOT)
        text=(REVIEW/source).read_text(encoding='utf-8')
        render_markdown(d,text,REVIEW,first_title=not prepend)
        path=OUT/name
        if path.exists(): raise FileExistsError(path)
        d.save(path); print(path)
    for src,name in [
      (ROOT/'90_local_only/legacy/early_framework_documents/research_log.md','04_早期科研过程原始记录.docx'),
      (ROOT/'paper/notes/research_development_timeline.md','05_早期研究发展回顾原文.docx')]:
        d=new_doc()
        p=d.add_paragraph(); p.add_run('历史资料原文转换；其中的方案、结论和时间是当时记录，不自动代表当前项目结论。').italic=True
        render_markdown(d,src.read_text(encoding='utf-8'),src.parent)
        path=OUT/name
        if path.exists(): raise FileExistsError(path)
        d.save(path); print(path)

if __name__=='__main__': main()
