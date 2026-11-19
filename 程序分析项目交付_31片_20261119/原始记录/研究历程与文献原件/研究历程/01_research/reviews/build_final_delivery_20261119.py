"""Generate final-scope project documents from saved experiment records."""
from collections import Counter
from pathlib import Path
import csv, io, json, subprocess, sys, zipfile
from xml.sax.saxutils import escape

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak
from reportlab.graphics.shapes import Drawing, Rect, String, Line

ROOT=Path(__file__).resolve().parents[2]
REVIEW=ROOT/'01_research/reviews'
R=ROOT/'03_experiments/results/bp17_remainder_2026-10-17'
OUT=REVIEW/'项目交付_31片_20261119'
SOURCES=OUT/'原始记录'
for p in (OUT,SOURCES): p.mkdir(exist_ok=True)

raw=subprocess.check_output([sys.executable,str(REVIEW/'audit_31_shards_20261119.py')],cwd=ROOT)
data=json.loads(raw.decode('utf-8'))
(SOURCES/'31片回执统计.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

FONT='Microsoft YaHei'
def font_style(st,size,bold=False):
    st.font.name=FONT; st.font.size=Pt(size); st.font.bold=bold; st.font.color.rgb=RGBColor(0,0,0)
    st._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),FONT)

def base_doc(title,subtitle):
    d=Document(); sec=d.sections[0]; sec.page_width=Inches(8.27); sec.page_height=Inches(11.69)
    sec.left_margin=sec.right_margin=Inches(.9); sec.top_margin=sec.bottom_margin=Inches(.8)
    for name,size in [('Normal',13),('Title',22),('Heading 1',17),('Heading 2',14.5)]:
        font_style(d.styles[name],size,name!='Normal')
    title_ppr=d.styles['Title']._element.get_or_add_pPr()
    for border in title_ppr.findall(qn('w:pBdr')): title_ppr.remove(border)
    st=d.styles['Normal']; st.paragraph_format.line_spacing=1.28; st.paragraph_format.space_after=Pt(8)
    p=d.add_paragraph(style='Title'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run(title)
    p=d.add_paragraph(subtitle); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs: run.font.size=Pt(11.5)
    d.add_paragraph()
    return d

def word_section(d,title,paras):
    d.add_heading(title,level=1)
    for text in paras: d.add_paragraph(text)

def word_table(d,rows):
    t=d.add_table(rows=0,cols=len(rows[0])); t.style='Table Grid'; t.autofit=True
    for n,row in enumerate(rows):
        cells=t.add_row().cells
        if n==0:
            trpr=t.rows[0]._tr.get_or_add_trPr(); hdr=OxmlElement('w:tblHeader'); hdr.set(qn('w:val'),'true'); trpr.append(hdr)
        for c,txt in zip(cells,row):
            c.text=str(txt)
            for p in c.paragraphs:
                p.paragraph_format.space_after=Pt(3)
                for r in p.runs:
                    r.font.name=FONT; r.font.size=Pt(11); r.bold=(n==0)
                    r._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'),FONT)
    d.add_paragraph('')

def stats_row(seg,metric,denom):
    return [f"{data['results'][seg][metric+'_'+g]['whole_correct' if metric=='native_behavior_projection' else 'all_tests_passed']}/{denom}" for g in ('BP0','BP1','BP2','BP3')]

report=base_doc('程序分析证据辅助大模型故障理解与修复 项目报告','交付范围：31 片案例回执与先行 100 例 | 2026 年 11 月')
word_section(report,'一 项目概览',[
 '本项目考察程序分析提供的结构信息与大语言模型对程序行为的预测及错误修复之间的关系。研究从双向程序切片和依赖分析出发，经过多轮工具与实验方案探索，最终形成同一程序对、四组证据、理解和修复分开测量的 BP17 实验。',
 '本次按照 31 片现存归档回执及第 8 片恢复映射确定归档范围，覆盖 3,057 个互不重复案例、24,456 条任务记录；另有先行完成共同验收的 100 例、800 个任务。两部分合计涉及 3,157 个不同案例和 25,256 条任务记录。31 片采用原编号 1–12 和 14–32，并非重新编号。',
 '结论以可追溯的结果为准：先行 40 例相对独立确认样本中，四组完整测试修复数依次为 18、17、19、20；预设比较经校正后未达到显著性。31 片中观察到 CFG 组的记录状态通过数较高，但这些已暴露数据是探索性观察，不等同于新的独立确认，也不说明方法等效。'])
word_section(report,'二 研究问题与方案',[
 'BP0 使用缺陷源码及四组共同失败诊断；BP1 在此基础上增加编译器入口可达行索引；BP2 增加结构化函数内控制流图（CFG）；BP3 使用同一 CFG 的受控中文表达。每一案例按组分别执行理解与修复，比较均应基于相同案例。',
 'P1 理解任务预测固定输入下的退出类别、标准输出字节数及前 64 字节；13 个 U1 未定义行为分类案例单独统计。修复评价区分范围合规、构建、repair 与 heldout 测试；通过状态是有限测试条件下的观测，而不是所有输入均正确的证明。入口可达行索引和 CFG 不等同于语义切片，也不是原论文 Error Invariant。'])
word_section(report,'三 数据范围与方法',[
 '31 片中的第 8 片使用既有恢复映射，第 30 片有 99 例，第 32 片有 58 例。31 片案例中，e72d 指纹段为 1,200 例，bc19 为 1,857 例。它们对应不同模型快照和时间，下面分别呈现，不将跨段差异解释成模型变化的因果效应。',
 '先行 100 例包含 60 例开发和 40 例相对项目先前模型调用独立的确认样本。后续数据中已有暴露的案例不能追认为新的确认样本；独立性也不排除公开代码进入模型预训练。'])
word_table(report,[['证据层次','案例','任务记录','解释'],['先行批','100','800','含 40 例相对独立确认'],['31 片回执范围','3,057','24,456','30 份标准回执 + 第 8 片恢复映射'],['合计','3,157','25,256','不同案例和任务记录；不等同逐文件独立验收']])
word_section(report,'四 实验结果',[
 '下表为 31 片案例回执中 status=all_tests_passed 的计数与该指纹段案例数。该字段是保存的状态统计，与完整逐条测试字节审计不是同一件事。每组分母为该段案例数，拒绝和其他状态包含在分母中。'])
word_table(report,[['指纹段及状态','BP0','BP1','BP2','BP3'],['e72d 全测试状态']+stats_row('e72d','repair',1200),['bc19 全测试状态']+stats_row('bc19','repair',1857),['e72d P1 全题正确']+stats_row('e72d','native_behavior_projection',1196),['bc19 P1 全题正确']+stats_row('bc19','native_behavior_projection',1848)])
word_section(report,'五 同案例结果解释',[
 '在 31 片范围内，e72d 的全测试状态为 BP0 459/1,200、BP1 467/1,200、BP2 481/1,200、BP3 481/1,200；bc19 对应 717/1,857、726/1,857、752/1,857、757/1,857。不同指纹段保持分开。',
 '先行独立确认集的预设对照为 BP1−BP0、BP2−BP1 和 BP3−BP2；修复差分别为 −2.5、+5.0、+2.5 个百分点，三项 Holm 校正 p 均为 1。无显著差异不证明没有差异，也不构成等效性证明。',
 '31 片包含 13 个 U1 案例，按保存回执，四组各 13/13 分类正确；该结果仅限指定的受限类别。P1 与 U1 在结果表和论文中分开。'])
word_section(report,'六 记录与解释边界',[
 '31 片按保存的案例清单重新统计；这次未重新执行模型、候选程序或客机归档的逐成员流式审计。BP17-1477 不在 31 片案例范围内，其排除记录与旧回执之间的冲突仍保存在原始材料。混合身份案例 BP17-0431 不在 31 片范围内。原项目其他保存记录仍保留，未因范围调整而删除。',
 '31 片的结果是按回执状态重算的描述性结果；不能以此声称原 EI 得到验证，或把探索数据的组间差异作为新的确认性结论。原始回答、评分、失败与恢复记录和协议见随附原始记录包。'])
report.save(OUT/'01_项目综合报告.docx')

history=base_doc('程序切片与大模型研究 项目发展历程','研究过程、讨论节点与成果记录 | 2026 年 4 月至 11 月')
word_section(history,'一 项目起点 2026 年初至 4 月',[
 '项目从程序切片及其在调试中的应用出发，早期学习静态切片、动态切片和程序依赖图。2026 年 7 月形成的研究发展记录回顾，4 月开始关注 Chop：通过 source 与 sink 限定故障传播的相关程序区域，并探索让大模型协助调试。该月份来自后续回顾，不能据此确定具体会议日期。',
 '依据：paper/notes/research_development_timeline.md；90_local_only/legacy/early_framework_documents/research_log.md。'])
word_section(history,'二 工具探索 2026 年 5 月至 6 月',[
 '研究日志自述从 5 月 20 日起记录实验环境及工具开发，开展 WALA、dg、giri、Slicer4J 和程序分析上下文工具调研，设计 Chop4LLM 的依赖图、数据流与受限可达性。6 月 6 日记录的 Discount 小例中，8 条语句经过后向切片保留 6 条，Chop 保留 3 条；这只是该实例的工具观察。',
 '本地版本库 5 月 23 日有初始提交；7 月 9 日的 master 提交保存早期研究日志、方案文档和代码。提交日期是版本记录，不是研究开始日期。'])
word_section(history,'三 方案演化 2026 年 6 月底至 7 月',[
 '项目先考虑让模型依据结构化工作流生成切片，再转向将动态后向定位、静态前向验证与断言结合。历史回顾记载了与学长讨论断言依赖、工具覆盖和方案差异化问题；原始资料没有给出完整的会议纪要，因此只记录可以追溯的讨论主题。',
 '7 月 18 日的历史方案进一步探索读取抽象解释 Error Invariant 轨迹及反馈精化。它属于当时的研究设想，不能代替后来实验实际输入与实测结果。'])
word_section(history,'四 框架调整与实验准备 2026 年 8 月至 10 月',[
 '8 月 28 日工作区完成版本整理。9 月的框架审查将原论文 Error Invariant、人工辅助约束和自动局部规则分开；Java 路线探索 Slicer4J 与静态依赖分析，C 路线进行原生基线和分析器准备。',
 '10 月 16 日 BP17 固定同案例四组和两类任务；10 月 17 日先行 100 例完成模型任务及共同验收，其中 40 例作相对独立确认。结果未支持预设主对照的稳定优势。'])
word_section(history,'五 执行、保护与记录 2026 年 10 月至 11 月',[
 '10 月 18 日至 23 日的操作记录包括接口故障、手动恢复、原第 8 片恢复映射和资源保护停止；原尝试、停止记录及授权保留。11 月的继续执行记录和 11 月 18 日的汇总保留了不同模型指纹、恢复与排除情况。',
 '按本次交付口径，以 31 片保存案例清单为范围；第 8 片用既有映射，第 30 片排除 BP17-1477。对历史操作及错误不改写，不用回执数量取代独立字节验收。'])
word_section(history,'六 已保存的会议与交流线索',[
 '现存材料可确认曾就研究方案和断言依赖等问题进行讨论，也保存用户授权、停止与继续等操作沟通。现有文件未构成完整逐次会议纪要，不能根据普通研究节点编造会议日期、参与人员或决议。真实会议纪要、录音、聊天导出如另行提供，可与此历程对应归档。'])
word_section(history,'七 主要原始资料目录',[
 '早期日志与方案：90_local_only/legacy/early_framework_documents/。研究发展记录与文献矩阵：paper/notes/ 和 paper/matrix/。实验协议与评审：01_research/workflow/ 和 01_research/reviews/。原始案例和结果：03_experiments/results/bp17_remainder_2026-10-17/ 与 bp17_caseblock100_2026-10-17/。',
 'GitHub 私有仓库 zsy0222/program-slicing 的 main、master 和 codex/reorganize-research-workspace 分支保存不同阶段版本。原始资料包保留原目录结构，不将文档生成时间当作实验日期。'])
history.save(OUT/'02_项目发展历程与交流记录.docx')

pdfmetrics.registerFont(TTFont('CN','C:/Windows/Fonts/msyh.ttc',subfontIndex=0))
pdfmetrics.registerFont(TTFont('CNB','C:/Windows/Fonts/msyhbd.ttc',subfontIndex=0))
styles={
 'title':ParagraphStyle('title',fontName='CNB',fontSize=18,leading=28,alignment=TA_CENTER,spaceAfter=13),
 'abstract':ParagraphStyle('abstract',fontName='CN',fontSize=10.2,leading=17.8,spaceAfter=7,wordWrap='CJK'),
 'body':ParagraphStyle('body',fontName='CN',fontSize=10.5,leading=18.5,spaceAfter=8,wordWrap='CJK',alignment=TA_JUSTIFY),
 'h1':ParagraphStyle('h1',fontName='CNB',fontSize=14,leading=22,spaceBefore=11,spaceAfter=7,keepWithNext=True,wordWrap='CJK'),
 'h2':ParagraphStyle('h2',fontName='CNB',fontSize=11.5,leading=19,spaceBefore=7,spaceAfter=5,keepWithNext=True,wordWrap='CJK'),
 'caption':ParagraphStyle('caption',fontName='CN',fontSize=9,leading=14,alignment=TA_CENTER,spaceAfter=8,wordWrap='CJK'),
 'ref':ParagraphStyle('ref',fontName='CN',fontSize=9.3,leading=15,spaceAfter=5,wordWrap='CJK'),
}
story=[]
def para(text,style='body'): story.append(Paragraph(escape(text),styles[style]))
def heading(text): para(text,'h1')
def subheading(text): para(text,'h2')
def pdf_table(rows,widths=None):
    cells=[[Paragraph(escape(str(v)),styles['ref']) for v in row] for row in rows]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='CENTER')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EDEDED')),('GRID',(0,0),(-1,-1),.45,colors.HexColor('#B5B5B5')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(t); story.append(Spacer(1,8))

def plot(metric,denom_e,denom_b,axis_label):
    d=Drawing(475,205); left=48; base=39; height=125; top=55
    for tick in range(0,51,10):
        y=base+height*tick/top; d.add(Line(left,y,465,y,strokeColor=colors.HexColor('#DEDEDE'),strokeWidth=.5))
        d.add(String(10,y-3,str(tick)+'%',fontName='CN',fontSize=8))
    groups=['BP0','BP1','BP2','BP3']; vals=[]
    for i,g in enumerate(groups):
        e=data['results']['e72d'][metric+'_'+g]['whole_correct' if metric=='native_behavior_projection' else 'all_tests_passed']/denom_e*100
        b=data['results']['bc19'][metric+'_'+g]['whole_correct' if metric=='native_behavior_projection' else 'all_tests_passed']/denom_b*100
        x=75+i*95
        for j,(v,col) in enumerate([(e,'#59666F'),(b,'#B0B8BD')]):
            d.add(Rect(x+j*25,base,21,height*v/top,fillColor=colors.HexColor(col),strokeColor=None))
            d.add(String(x+j*25-3,base+height*v/top+4,f'{v:.1f}',fontName='CN',fontSize=7.5))
        d.add(String(x+9,20,g,fontName='CN',fontSize=9))
    d.add(Rect(235,184,10,10,fillColor=colors.HexColor('#59666F'),strokeColor=None)); d.add(String(249,184,'e72d',fontName='CN',fontSize=9))
    d.add(Rect(315,184,10,10,fillColor=colors.HexColor('#B0B8BD'),strokeColor=None)); d.add(String(329,184,'bc19',fontName='CN',fontSize=9))
    return d

para('程序分析证据对大语言模型程序理解与修复的影响','title')
para('摘要','h1')
para('背景：程序切片、依赖分析和控制流结构可以为代码任务提供不同粒度的上下文。本研究考察这些信息与大语言模型固定输入行为预测及缺陷修复结果的关系。方法：基于同一 C 程序对，设置源码及共同失败诊断、入口可达行索引、结构化函数内 CFG 和同一 CFG 的受控中文四组；理解和修复独立评价。按本次 31 片归档口径，案例回执覆盖 3,057 例、24,456 条任务记录，另有先行 100 例；按模型指纹分段描述，P1 与 13 个 U1 分类案例分开。结果：先行 40 例确认样本的四组完整修复分别为 18、17、19、20 例；三项预设主对照的 Holm 校正 p 均为 1。31 片范围中，e72d 段全测试状态为 459、467、481、481/1,200；bc19 段为 717、726、752、757/1,857。结论：探索性状态统计显示 CFG 组数值较高，但先行确认集未建立预设对照的稳定优势；两个指纹段与历史暴露限制因果和确认性解释。','abstract')
para('关键词：程序切片；控制流图；大语言模型；程序行为预测；自动程序修复；配对实验','abstract')
heading('1 引言')
para('自动程序修复需要模型同时处理代码范围、执行行为和具体测试约束。程序切片通过数据与控制依赖识别相对于给定准则的相关程序成分 [1–3]；双向依赖或 Chop 为限定两个程序位置之间的关系提供思路 [4]。这些方法得到的程序信息可能改善模型上下文，但“切片生成准确”“模型利用结构信息”与“补丁通过测试”是不同问题。')
para('KATANA 研究过基于双向切片的修复上下文 [5]，Slicer4J 提供 Java 动态切片工具 [6]；神经切片器和数据流预训练方法则尝试学习切片生成 [7–8]。CRUXEval 的可执行代码理解评价提供了相关背景 [11]。本研究不将这些工作等同于本项目的 CFG 输入，而是通过同案例分组比较，探究不同结构证据及表达方式与行为预测、修复结果的关系。')
para('项目的研究路径从 Chop4LLM 原型逐步发展：早期尝试程序依赖图、受限可达性和 LLM 上下文，随后探讨模型驱动切片、断言引导与抽象解释。抽象解释故障定位及 Error Invariant [9–10] 为研究提供方法背景；最终报告的 BP17 组实际提供入口行索引和函数内 CFG，而非原论文 EI。')
heading('2 研究问题与方案演进')
para('RQ1：加入入口可达行索引与源码基线相比是否改变任务结果？RQ2：在该索引基础上增加结构化 CFG 是否存在增量？RQ3：同一 CFG 的中文与结构化表达是否产生差异？三个对应比较为 BP1−BP0、BP2−BP1、BP3−BP2。')
para('2026 年 4 月的历史回顾记录了 Chop 与 LLM 的起点；5–6 月的 Chop4LLM 小规模样例验证了原型设计思路，但没有形成正式的大规模模型对照。之后的 SWP、断言级联和抽象解释反馈均属于阶段性方案探索。最终研究转向可追溯的实际模型输入、相同案例和可执行测试，避免把历史设计直接表述为已实现功能。')
heading('3 研究设计')
subheading('3.1 样本与归档范围')
para('原生 Codeflaws 基线包含 3,903 对；本交付按现存 31 片案例清单构建分析集合，并单列已经共同验收的先行 100 例。31 片清单经主机只读汇总得到 3,057 个互不重复案例、每例四组两任务共 24,456 条任务回执行；先行批为 800 条任务。该统计不替代对归档压缩包和其全部成员进行独立流式验收。')
para('31 片中 e72d 段 1,200 例、bc19 段 1,857 例；两段模型身份及运行时间不同。原第 8 片采用恢复映射，案例 BP17-1477 因排除而不在该集合中，混合身份案例 BP17-0431 也不在该集合中。另有 BP17-0787 的运行时变动记录，应保留作敏感性线索。')
subheading('3.2 组别与任务')
para('BP0 为源码及共同失败诊断；BP1 增加入口可达行索引；BP2 在 BP1 上加入结构化函数内 CFG；BP3 以同一 CFG 的受控中文替换结构化表述。组别含义以真实输入为准，行索引不是语义切片，CFG 也不是完整依赖图或 EI。')
para('理解任务 P1 判断固定输入下退出类别、输出长度与前 64 字节是否全部正确；13 个 U1 案例是对指定未定义行为类型的受限分类，单独列示。修复终点要求合法修改、可构建以及原 repair 和 heldout 测试通过；以下大样本图以回执 all_tests_passed 状态计数，未将其自动提升为逐条原始测试独立复核结果。')
subheading('3.3 统计与数据质量')
para('先行 100 例分为 60 例开发和 40 例相对项目历史调用独立的确认案例；确认集使用固定种子的 10,000 次簇 bootstrap，并在各任务内对三项预设比较实施 Holm 校正。31 片为既有暴露数据中的描述性分析，不新增独立确认。理解正确率以该段 P1 全部案例为分母，包含无效答案；有效回答数量在表中单列。')
heading('4 实验结果')
subheading('4.1 先行独立确认')
pdf_table([['组别','理解正确','完整修复','修复比例'],['BP0','9/40','18/40','45.0%'],['BP1','6/40','17/40','42.5%'],['BP2','8/40','19/40','47.5%'],['BP3','9/40','20/40','50.0%']],[80,120,120,120])
para('40 例修复比较 BP1−BP0 为 −2.5 个百分点，95% 簇区间 [−12.5, 7.5]；BP2−BP1 为 +5.0，区间 [−5.0, 15.0]；BP3−BP2 为 +2.5，区间 [−7.5, 12.5]。三项 Holm 校正 p 均为 1。样本量和区间不允许将未发现显著性解释成等效。')
subheading('4.2 31 片修复状态')
story.append(plot('repair',1200,1857,'修复')); para('图 1  31 片中各指纹段的全测试状态比例；分母分别为 1,200 和 1,857 例','caption')
pdf_table([['指纹段','BP0','BP1','BP2','BP3'],['e72d']+stats_row('e72d','repair',1200),['bc19']+stats_row('bc19','repair',1857)],[70,95,95,95,95])
para('两段描述性结果均显示 BP2、BP3 的全测试状态数高于 BP0。以 e72d 为例，BP2−BP1 为 14/1,200，BP3−BP2 为 0；bc19 相应为 26/1,857 和 5/1,857。这些是当前 31 片范围的原始状态比例差，不是经簇校正的预设确认检验，也不能解释为跨模型指纹的因果比较。')
subheading('4.3 理解与 U1 分类')
story.append(plot('native_behavior_projection',1196,1848,'P1')); para('图 2  P1 全题正确比例；e72d 为 1,196 例，bc19 为 1,848 例','caption')
pdf_table([['指纹段','BP0','BP1','BP2','BP3'],['e72d P1 正确']+stats_row('e72d','native_behavior_projection',1196),['e72d P1 有效','1070/1196','1066/1196','1057/1196','1068/1196'],['bc19 P1 正确']+stats_row('bc19','native_behavior_projection',1848),['bc19 P1 有效','1666/1848','1659/1848','1655/1848','1656/1848']],[92,90,90,90,90])
para('U1 共 13 例，其中 e72d 4 例、bc19 9 例；各组的保存回执均为 13/13 正确。受样本量、类别和任务边界限制，该比例不能外推为一般未定义行为识别能力。P1 的全部分母包含无效回答，不是以有效答案为分母的条件正确率。')
heading('5 讨论')
para('本研究以共同源码和诊断为起点，逐层引入入口可达信息、CFG 结构与中文表达，能够把“附加了什么信息”和“结果如何变化”联系起来。31 片状态计数可用于描述已保存的实验表现；在先行独立确认集中，主对照尚未提供稳定差异证据。')
para('不同模型快照与不同运行时段不构成随机化模型试验。不同的开发暴露程度、任务难度、提示上下文长度和案例簇可能影响结果。尽管若干数值呈相同方向，也不能据此证明 CFG 对修复存在一般性因果效应，更不能推导模型形成了因果性故障理解。')
para('历史探索与最终方法之间的区别同样重要：Chop4LLM、小例程序依赖图、断言级联、模型切片推理以及 EI 语义理解分别代表问题提出和早期方案，不能把它们并列为在最终 BP17 中全部完成的组件。相关工作 [4–10] 提供背景与设计参照，并不直接证明本研究的实验效果。')
heading('6 有效性与范围')
para('内部有效性方面，已保存回执能定位输入、回答及评价，但本次仅按回执重新统计，未重新流式复验全部客机归档。BP17-1477 的排除记录与历史评分行存在口径冲突，本次 31 片范围不包含该例。任务槽及案例回执是不同于有效测试、独立验收和样本代表性的概念。')
para('统计有效性方面，先行独立确认仅有 40 个簇，区间较宽；31 片分析为探索性且包含先前暴露。P1 使用有限输出投影，修复测试不能覆盖全部输入；13 个 U1 分类也不能代表全部未定义行为。公开基准还存在预训练暴露可能。')
heading('7 结论')
para('项目形成从程序分析到模型输入、执行观察和结果记录的同案例实验路径，并在指定 31 片归档范围和先行 100 例上整理了理解与修复结果。先行 40 例独立确认的预设对照未显示稳定优势；31 片中 CFG 条件的修复状态呈较高数值，属于值得后续独立研究检验的探索观察。研究说明，在评价分析证据与模型表现时，必须同时保留输入身份、样本层次、真实测试范围与未定义行为的边界。')
heading('参考文献')
refs=[
'[1] Weiser M. Program Slicing. IEEE Transactions on Software Engineering, 1984, SE-10(4): 352–357. doi:10.1109/TSE.1984.5010248.',
'[2] Ferrante J, Ottenstein K J, Warren J D. The Program Dependence Graph and Its Use in Optimization. ACM TOPLAS, 1987, 9(3): 319–349. doi:10.1145/24039.24041.',
'[3] Korel B, Laski J. Dynamic Program Slicing. Information Processing Letters, 1988, 29(3): 155–163. doi:10.1016/0020-0190(88)90054-3.',
'[4] Jackson D, Rollins E J. A New Model of Program Dependences for Reverse Engineering. Proceedings of FSE, 1994. https://www.cs.cmu.edu/~Compose/paper_abstracts/dnj/fse94.html.',
'[5] Sintaha M, Nashid N, Mesbah A. Katana: Dual Slicing-Based Context for Learning Bug Fixes. ACM TOSEM, 2023. doi:10.1145/3579640.',
'[6] Ahmed K, Lis M, Rubin J. Slicer4J: A Dynamic Slicer for Java. ESEC/FSE, 2021. doi:10.1145/3468264.3473123.',
'[7] Yadavally A, Li Y, Wang S, Nguyen T N. A Learning-Based Approach to Static Program Slicing. Proceedings of the ACM on Programming Languages, 2024, 8(OOPSLA1). doi:10.1145/3649814.',
'[8] He P, Wang S, Chen T-H, Asaduzzaman M. SLICEFORMER: Static Program Slicing Using Language Models With Dataflow-Aware Pretraining and Constrained Decoding. ACL, 2026. doi:10.18653/v1/2026.acl-long.1649.',
'[9] Ermis E, Schäf M, Wies T. Error Invariants. FM, 2012: 187–201. doi:10.1007/978-3-642-32759-9_17.',
'[10] Dimovski A S. Fault Localization by Abstract Interpretation and its Applications. Journal of Computer Languages, 2024, 80: 101288. doi:10.1016/j.cola.2024.101288.',
'[11] Gu A, Rozière B, Leather H, et al. CRUXEval: A Benchmark for Code Reasoning, Understanding and Execution. Proceedings of ICML, PMLR 235, 2024: 16568–16621. https://proceedings.mlr.press/v235/gu24c.html.'
]
for ref in refs: para(ref,'ref')
def page_number(canvas,doc):
    canvas.setFont('CN',8); canvas.setFillColor(colors.HexColor('#666666')); canvas.drawCentredString(A4[0]/2,13*mm,str(doc.page))
SimpleDocTemplate(str(OUT/'03_研究论文.pdf'),pagesize=A4,leftMargin=22*mm,rightMargin=22*mm,topMargin=20*mm,bottomMargin=20*mm,title='程序分析证据对大语言模型程序理解与修复的影响').build(story,onFirstPage=page_number,onLaterPages=page_number)
print('DOCUMENTS_CREATED',OUT)
