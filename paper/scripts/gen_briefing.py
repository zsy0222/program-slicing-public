#!/usr/bin/env python3
"""Generate a concise briefing document — ideas, rationale, no examples."""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

def add_h(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = '黑体'
        rPr = run._element.get_or_add_rPr()
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:eastAsia'), '黑体')
        rPr.insert(0, rFonts)
    return h

def add_p(doc, text, bold=False, size=12, indent=True):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    run = p.add_run(text)
    run.font.name = '宋体'
    run.font.size = Pt(size)
    run.bold = bold
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), '宋体')
    rPr.insert(0, rFonts)
    return p

def add_table(doc, headers, rows):
    table = doc.add_table(rows=len(rows)+1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(10)
        shading = OxmlElement('w:shd')
        shading.set(qn('w:fill'), 'D9D9D9')
        cell._element.get_or_add_tcPr().append(shading)
    for r, row in enumerate(rows):
        for c, txt in enumerate(row):
            cell = table.rows[r+1].cells[c]
            cell.text = ''
            p = cell.paragraphs[0]
            run = p.add_run(str(txt))
            run.font.size = Pt(10)
    doc.add_paragraph()
    return table

def add_bullet(doc, text, size=11):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.4
    p.paragraph_format.left_indent = Cm(1)
    run = p.add_run('• ' + text)
    run.font.name = '宋体'
    run.font.size = Pt(size)
    return p

def add_box(doc, text):
    """Add an indented emphasized paragraph."""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.4
    p.paragraph_format.left_indent = Cm(1.5)
    p.paragraph_format.right_indent = Cm(1.5)
    run = p.add_run(text)
    run.font.name = '宋体'
    run.font.size = Pt(11)
    run.italic = True
    run.font.color.rgb = RGBColor(60, 60, 60)
    return p

# ============================================================
doc = Document()

for section in doc.sections:
    section.top_margin = Cm(2.2)
    section.bottom_margin = Cm(2.2)
    section.left_margin = Cm(2.8)
    section.right_margin = Cm(2.8)

style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(11.5)

# ===== COVER =====
for _ in range(5):
    doc.add_paragraph()

tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = tp.add_run('LLM增强的Error Invariant语义理解\n用于程序故障定位')
run.bold = True
run.font.size = Pt(20)
rPr = run._element.get_or_add_rPr()
rFonts = OxmlElement('w:rFonts')
rFonts.set(qn('w:eastAsia'), '黑体')
rPr.insert(0, rFonts)

doc.add_paragraph()
sp = doc.add_paragraph()
sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sp.add_run('研究方案简报')
run.font.size = Pt(15)
run.font.color.rgb = RGBColor(100, 100, 100)

for _ in range(3):
    doc.add_paragraph()
ip = doc.add_paragraph()
ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
ip.add_run(f'{datetime.date.today().strftime("%Y年%m月%d日")}').font.size = Pt(12)

doc.add_page_break()

# ===== 1. PROBLEM =====
add_h(doc, '一、问题：故障定位的两个世界', level=1)

add_p(doc,
    '软件调试中，程序员面对一个失败的测试，想知道"哪些代码导致了错误"。过去四十年的研究产生了大量工具，'
    '但它们分属两个互不往来的世界。')

add_h(doc, '世界A：形式化方法', level=2)
add_p(doc,
    '包括PDG静态切片（Weiser 1984）、动态DDG切片（Zhang 2007）、抽象解释（Dimovski 2024）。'
    '这些方法有严格的数学基础，能给出完备性保证——"不会遗漏任何可能相关的语句"。'
    '但它们的输出是数学符号、行号列表、或可疑度数字。对程序员而言，这些输出不仅不友好，'
    '而且不提供解释——为什么这些语句相关而另一些无关？分析过程是怎样的？这些方法无法回答。')

add_h(doc, '世界B：LLM方法', level=2)
add_p(doc,
    '包括SliceMate（2025）、SLICEFORMER（2026）等。LLM擅长语义理解，能用自然语言解释错误原因。'
    '但LLM做程序分析有根本缺陷：GPT-4o裸调做切片仅60.8%准确率（Shahandashti 2025），'
    '不提供完备性保证，可能遗漏关键依赖或编造不存在的依赖。')

add_h(doc, '核心问题', level=2)
add_box(doc,
    '形式化方法有完备性但不可解释，LLM有语义理解但没有完备性。'
    '两者从未真正对话——形式方法把分析过程锁在黑盒里，LLM只能对结果做浅层判断。')

add_h(doc, '我们的核心命题', level=2)
add_p(doc,
    '能否让LLM"阅读"形式分析的中间推理过程，而非仅仅接收最终结果？如果能，'
    '就可以同时获得形式方法的完备性保证和LLM的语义理解能力——在两者之间建立此前不存在的桥梁。',
    bold=True)

doc.add_page_break()

# ===== 2. WHY DIMOVSKI =====
add_h(doc, '二、为什么选择Dimovski作为桥梁', level=1)

add_p(doc,
    'Dimovski（2024, Journal of Computer Languages）提出了一种基于抽象解释的故障定位方法。'
    '在分析过程中，它在一个关键维度上区别于所有其他工具：')

add_h(doc, 'Dimovski产出了什么独特的东西', level=2)

add_table(doc,
    ['工具', '输出', '能否让LLM"阅读"'],
    [
        ['Ochiai / Tarantula (SBFL)', '可疑度分数（数值）', '❌ 数字没有语义可读'],
        ['Zhang 2007 MPS', '行号列表', '❌ 和读代码没区别'],
        ['SliceMate 2025', '行号列表（黑盒生成）', '❌ 中间过程不可见'],
        ['Dimovski 2024', 'Error Invariant 序列', '✅ 数学约束 + 语义可读 + 位置排列'],
    ]
)

add_p(doc,
    'Error Invariant是对程序每个位置上"所有可能导致错误的状态"的数学描述，如[y=x+1, x≥5]。'
    '它有三重身份：对形式方法是可计算的对象，对人类是可理解的约束，对LLM是可阅读的半形式化语言。')

add_h(doc, 'Dimovski浪费了什么', level=2)
add_p(doc,
    'Dimovski只用Error Invariant做了一件事——对比相邻位置的invariant是否相同，相同则删除语句。'
    '但invariant内部的丰富信息全部未被利用：哪个变量首次进入了错误条件？哪个变量消失了？'
    '约束之间的关系如何演化？何时发生了语义上的"质变"而不仅仅是数值上的"变化"？')

add_p(doc,
    '这些被浪费的信息恰好是LLM擅长处理的内容——不是数学推导，而是对"变化"的语义理解。')

doc.add_page_break()

# ===== 3. ARCHITECTURE =====
add_h(doc, '三、方案架构：四阶段', level=1)

add_h(doc, '整体逻辑', level=2)
add_p(doc,
    '整个方案建立在一条简单的逻辑链上：让形式分析做它擅长的事（计算完备的约束传播），'
    '让LLM做它擅长的事（理解约束的语义含义），两者通过Error Invariant序列对话，'
    'LLM的理解还能反馈来提高形式分析的精度。')

add_h(doc, 'Phase 1：Dimovski确定性骨干', level=2)
add_p(doc,
    '运行Dimovski的迭代后向-前向抽象解释。不需要程序可执行，不需要测试用例。'
    '产出一个完整的Error Invariant序列——沿程序位置排列的数学约束轨迹，记录了错误条件如何从一个位置传播到下一个位置。'
    '同时产出初始的语句级语义切片和精度损失点标记。')
add_p(doc,
    'Phase 1的输出已经是完备的（sound）——不会遗漏任何可能相关的语句。后续所有操作都在此基础上做减法。')

add_h(doc, 'Phase 2：LLM深度阅读Invariant轨迹 ★', level=2)
add_p(doc,
    '这是方案的核心创新。LLM执行三个递进的理解任务：')
add_bullet(doc, '语义翻译：将数学约束转为自然语言因果描述。验证"LLM能读懂invariant"这一基础假设。')
add_bullet(doc, '质变检测：沿轨迹找到语义性质发生转折的位置——变量何时进入/退出错误条件，约束何时从一类关系变为另一类。Dimovski只知道"变了"，LLM知道"变的是什么意思"。')
add_bullet(doc, '缺失推断：观察invariant轨迹中的语义断裂——两个位置之间的跳跃超出了程序语句能解释的范围——LLM推断缺失的语义条件，建议Dimovski自身无法发现的精化谓词。')

add_h(doc, 'Phase 3：反馈精化循环 ★', level=2)
add_p(doc,
    '区别于所有现有"LLM+形式方法"工作的关键设计。不是LLM单向接收分析结果，'
    '而是LLM将语义理解的发现（补充谓词）反馈给Dimovski，触发新一轮更精确的BDD分析。'
    '循环持续到LLM无法建议新谓词或切片不再显著缩减。')
add_p(doc,
    '三个终止条件保证循环不会失控：LLM连续两轮无新建议、切片缩减小于5%、硬上限5轮。')

add_h(doc, 'Phase 4：因果链重构与可读输出', level=2)
add_p(doc,
    '基于精化后的最终invariant轨迹，LLM生成面向程序员的完整报告：错误从哪起源、'
    '经过哪些关键转折、最终在哪表现为失败、修复建议指向哪个invariant变化点。'
    '每一条包含/排除决策都可追溯到具体的invariant证据或LLM语义判断。')

doc.add_page_break()

# ===== 4. SOUNDNESS =====
add_h(doc, '四、理论合理性', level=1)

add_h(doc, '完备性从哪来', level=2)
add_p(doc,
    '框架的完备性完全继承自Dimovski的过近似（over-approximation）性质——Error Invariant保证不会遗漏任何真实可能导致错误的状态。'
    'Phase 2-3的所有LLM操作都是"减法"——只从Dimovski的切片中移除LLM确信无关的语句，从不添加新语句。')

add_h(doc, 'LLM错了怎么办', level=2)
add_p(doc,
    '这是框架设计中最关键的安全机制：当LLM不确定某条语句是否无关时（输出UNCERTAIN），框架保守地保留它。'
    '这意味着LLM的错误影响是单向的——最多"保留了本可移除的无关语句"（精度损失），'
    '绝不可能"移除了真正相关的语句"（完备性损失）。最坏情况是所有LLM判断都不确定 → 切片退化为Dimovski原始输出。')

add_h(doc, '为什么invariant适合LLM读', level=2)
add_p(doc,
    'LLM对不同的输入格式有截然不同的处理能力。纯数字（SBFL分数）和纯形式逻辑（SMT公式）是LLM的弱项。'
    'Error Invariant恰好落在LLM强项区间——格式精炼（Dimovski已筛掉无关信息）、语义可读（数学约束接近自然语言）、'
    '结构化（沿位置排列成轨迹）。它比代码更精炼，比符号更可读。')

add_h(doc, '反馈循环为什么不会退化', level=2)
add_p(doc,
    'Dimovski的精化是单调的——每轮BDD分割只会增加精度，不会倒退。LLM的建议仅影响谓词集，'
    '不改变抽象解释的过近似性质。因此完备性在循环中保持不变，精度单调提升或持平。')

doc.add_page_break()

# ===== 5. DESIGN RATIONALE =====
add_h(doc, '五、核心设计决策及其理由', level=1)

decisions = [
    ('为什么用Dimovski，不自研分析？',
     'Dimovski经过三年打磨（SAS 2023→COLA 2024→SLE 2025），有同行评审的形式化正确性证明。'
     '自研分析不仅要重复大量已知工作，还可能不如它可靠。本方案的创新不在"切片引擎本身"，'
     '而在"让LLM理解引擎的中间推理"——这是全新的维度。使用已有的可靠基础设施是好的系统研究习惯。'),

    ('为什么不直接让LLM做切片？',
     'Shahandashti 2025证明GPT-4o裸调做切片仅60.8%。LLM不sound（可能漏依赖或编造依赖），不可审计（推理链不可复现）。'
     '让LLM做"理解分析过程"比做"替代分析引擎"更符合其能力边界。'),

    ('为什么是双向循环？',
     '单向模式（分析→LLM→输出）创新不足——LLM只是后分类器。双向意味着LLM能主动改善分析质量，'
     '从"旁观者"变为"参与者"。据我们所知，这是LLM+程序分析领域首个双向反馈设计。'),

    ('为什么舍弃运行时断言？',
     '更早的方案依赖LLM生成的运行时断言作为ground truth。问题：(1)断言生成工具只评估了语法正确性，'
     '未评估运行时正确性；(2)断言修改程序行为；(3)Dimovski不需要运行时——从纯静态退回到需要运行时是倒退而非升级。'),
]

for title, content in decisions:
    add_h(doc, title, level=2)
    add_p(doc, content)

doc.add_page_break()

# ===== 6. EVALUATION =====
add_h(doc, '六、实验思路', level=1)

add_p(doc, '实验围绕五个递进的问题设计，每个问题对应一个RQ：')

add_table(doc,
    ['实验', '回答什么问题', '最关键的指标', '最关键的对比'],
    [
        ['RQ1 语义翻译', 'LLM能读懂invariant吗？（可行性）', '人工忠实度评分', '翻译invariant vs 翻译对应代码'],
        ['RQ2 质变点定位 ★', '读invariant比读代码更准吗？（存在价值）', 'Top-1故障定位命中率', 'LLM+invariant vs LLM+代码'],
        ['RQ3 谓词有效性 ★', 'LLM建议对Dimovski有帮助吗？（独特性）', '切片缩减率、假阳性消除率', 'LLM谓词精化 vs Dimovski自身迭代'],
        ['RQ4 因果叙事', 'LLM输出的解释可信吗？（实用价值）', '因果一致性评分', 'invariant叙事 vs 代码叙事'],
        ['RQ5 信息消融', 'invariant的什么成分最关键？（设计验证）', '各配置退化量', '完整invariant vs 二元信号'],
    ]
)

add_p(doc,
    '实验的逻辑链：先证可行性（RQ1），再证存在价值（RQ2），再证独特性（RQ3），最后验证实用性和设计合理性（RQ4/5）。')

doc.add_page_break()

# ===== 7. POSITIONING =====
add_h(doc, '七、与最相关工作的定位关系', level=1)

add_table(doc,
    ['维度', 'SliceMate 2025', 'Dimovski 2024', '本方案'],
    [
        ['分析引擎', 'LLM Agent (黑盒)', '抽象解释 (白盒)', '抽象解释 (白盒)'],
        ['LLM的角色', '端到端切片引擎', '无', '中间推理的语义读者'],
        ['完备性', '❌', '✅', '✅ (继承)'],
        ['可解释性', '低 (Agent推理不可见)', '低 (数学符号)', '高 (语义+证据)'],
        ['过程透明', '低 (黑盒)', '中 (invariant可见)', '高 (每步语义标注)'],
        ['反馈能力', '无', '无', '★ 双向循环'],
        ['运行时需求', '仅API', '无', '无'],
    ]
)

doc.add_page_break()

# ===== 8. CONTRIBUTIONS =====
add_h(doc, '八、预期贡献', level=1)

contribs = [
    ('Error Invariant作为半形式化接口语言。',
     '首次提出将抽象解释的中间表示作为LLM与形式方法之间的共享语言，'
     '开辟了"LLM阅读理解形式分析过程"这一新的结合范式，区别于现有的"LLM替代分析"和"LLM分类输出"两种模式。'),
    ('LLM驱动的语义谓词发现。',
     'LLM主动参与分析精化——基于语义理解建议形式分析自身无法发现的谓词——'
     '从"旁观者"变为"参与者"。'),
    ('双向反馈架构。',
     'Dimovski⇄LLM双向循环，形式分析保证完备性，LLM提升精度和可解释性。'
     'LLM+程序分析领域首个双向反馈设计。'),
    ('从不变量到因果叙事。',
     'LLM解释的不是源代码而是invariant的演变轨迹，更精炼、更聚焦于"错误如何传播"。'),
]

for title, desc in contribs:
    add_h(doc, title, level=2)
    add_p(doc, desc)

doc.add_page_break()

# ===== 9. TIMELINE =====
add_h(doc, '九、时间规划', level=1)

add_table(doc,
    ['阶段', '时间', '核心任务', '交付物'],
    [
        ['准备', '第1-2周', '获取Dimovski工具/在TCAS上产出真实invariant', 'invariant样本+表示格式'],
        ['L1验证', '第3-4周', 'Prompt设计+3案例翻译测试', '翻译忠实度数据'],
        ['L2验证', '第5-7周', '质变检测Prompt+反馈循环原型', '5-10 bug初步数据'],
        ['规模化', '第8-11周', 'Defects4J 20+bug全流程+实验2-5', '完整实验数据'],
        ['写作', '第12-14周', '论文初稿+用户研究(实验6)', '论文初稿'],
        ['打磨', '第15-16周', '修改+补充+投稿', '投稿版本'],
    ]
)

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('—— 简报完 ——')
run.font.size = Pt(11)
run.font.color.rgb = RGBColor(128, 128, 128)

# ===== SAVE =====
out = r'C:\Users\chenm\Desktop\program_slicing\paper\reports\research_briefing.docx'
doc.save(out)
print(f'Saved: {out}')
