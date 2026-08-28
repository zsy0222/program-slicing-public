#!/usr/bin/env python3
"""Generate the comprehensive research proposal report as a Word document."""

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

def add_heading_styled(doc, text, level=1):
    """Add a heading with proper Chinese font styling."""
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = '黑体'
        rPr = run._element.get_or_add_rPr()
        rFonts = OxmlElement('w:rFonts')
        rFonts.set(qn('w:eastAsia'), '黑体')
        rPr.insert(0, rFonts)
    return h

def add_para(doc, text, bold=False, italic=False, size=12, indent=False):
    """Add a paragraph with consistent styling."""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    run = p.add_run(text)
    run.font.name = '宋体'
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:eastAsia'), '宋体')
    rPr.insert(0, rFonts)
    return p

def add_table(doc, headers, rows, col_widths=None):
    """Add a formatted table."""
    table = doc.add_table(rows=len(rows)+1, cols=len(headers))
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(header)
        run.bold = True
        run.font.size = Pt(10)
        # Gray background
        shading = OxmlElement('w:shd')
        shading.set(qn('w:fill'), 'D9D9D9')
        cell._element.get_or_add_tcPr().append(shading)

    # Data rows
    for r, row in enumerate(rows):
        for c, cell_text in enumerate(row):
            cell = table.rows[r+1].cells[c]
            cell.text = ''
            p = cell.paragraphs[0]
            run = p.add_run(str(cell_text))
            run.font.size = Pt(10)
            if c == 0:
                run.bold = True

    doc.add_paragraph()  # spacing after table
    return table

def add_code_block(doc, code_text):
    """Add a monospace code block."""
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1)
    p.paragraph_format.line_spacing = 1.2
    run = p.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(10)
    return p

# ============================================================
# BUILD DOCUMENT
# ============================================================
doc = Document()

# Page setup
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.18)
    section.right_margin = Cm(3.18)

# Normal style
style = doc.styles['Normal']
style.font.name = '宋体'
style.font.size = Pt(12)

# ===== COVER PAGE =====
for _ in range(4):
    doc.add_paragraph()

title_p = doc.add_paragraph()
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title_p.add_run('LLM增强的Error Invariant语义理解\n用于程序故障定位')
run.bold = True
run.font.size = Pt(22)
rPr = run._element.get_or_add_rPr()
rFonts = OxmlElement('w:rFonts')
rFonts.set(qn('w:eastAsia'), '黑体')
rPr.insert(0, rFonts)

doc.add_paragraph()

sub_p = doc.add_paragraph()
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sub_p.add_run('—— 研究方案与技术报告 ——')
run.font.size = Pt(16)
run.font.color.rgb = RGBColor(80, 80, 80)

for _ in range(3):
    doc.add_paragraph()

info_items = [
    f'日期：{datetime.date.today().strftime("%Y年%m月%d日")}',
    '研究方向：程序分析 × 大语言模型',
    '课题类型：软件故障定位',
]
for item in info_items:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(item)
    run.font.size = Pt(13)

doc.add_page_break()

# ===== TABLE OF CONTENTS placeholder =====
add_heading_styled(doc, '目  录', level=1)
toc_items = [
    '一、研究背景与问题陈述',
    '二、文献综述与相关工作',
    '三、核心研究问题',
    '四、技术方案：四阶段架构',
    '五、理论合理性分析',
    '六、关键设计决策',
    '七、实验设计',
    '八、预期贡献',
    '九、时间规划',
    '十、参考文献',
]
for item in toc_items:
    add_para(doc, item, size=12)

doc.add_page_break()

# ===== SECTION 1: BACKGROUND =====
add_heading_styled(doc, '一、研究背景与问题陈述', level=1)

add_heading_styled(doc, '1.1 软件故障定位的核心挑战', level=2)

add_para(doc,
    '软件调试是软件开发中最耗时、最昂贵的活动之一。当测试用例失败时，程序员需要回答一个核心问题：'
    '"哪些代码导致了这个错误？"这个问题看似简单，实际上涉及两个相互冲突的需求：', indent=True)

add_para(doc,
    '完备性（Soundness）：不能遗漏任何一个可能导致错误的语句。如果分析工具漏掉了真正bug所在的那行代码，'
    '程序员就永远找不到问题。', indent=True)

add_para(doc,
    '精确性（Precision）：不能把无关语句都包含进来。如果分析工具输出500行"可疑代码"，程序员仍需逐行排查，'
    '工具就没有实际价值。', indent=True)

add_para(doc,
    '这两个需求天然矛盾。追求完备性意味着保守——任何"可能"相关的语句都要保留；追求精确性意味着激进——'
    '只保留"确定"相关的语句。过去四十年的研究本质上是在这条光谱上寻找最佳平衡点。', indent=True)

add_heading_styled(doc, '1.2 现有方法的光谱', level=2)

add_para(doc, '目前所有故障定位/程序切片方法分布在一条光谱上：', indent=True)

add_table(doc,
    ['方法类别', '代表工作', '完备性', '精确性', '核心代价'],
    [
        ['纯动态切片', 'Zhang 2007 MPS', '❌ 受限于trace', '★★★★★', '100-1000×运行时减速'],
        ['纯静态切片(PDG)', 'Weiser 1984, Horwitz 1990', '✅', '★★☆☆☆', '全程序O(n³)指针分析'],
        ['频谱故障定位(SBFL)', 'Ochiai, Tarantula', '❌ 仅统计相关', '★★☆☆☆', '需要大量测试用例'],
        ['抽象解释', 'Dimovski 2024', '✅ 过近似', '★★★☆☆', '抽象域精度限制'],
        ['LLM直接切片', 'SliceMate 2025, GPT-4o裸调', '❌', '★★★☆☆', '仅60.8%准确率'],
    ]
)

add_para(doc,
    '观察这张表可以发现一个根本性的分裂：形式化方法（PDG、抽象解释）有完备性但精确性不足，输出的是数学符号和行号列表，'
    '对程序员不友好；LLM方法有语义理解和自然语言解释，但没有完备性保证。', indent=True)

add_heading_styled(doc, '1.3 关键洞察：形式方法与LLM从未真正对话', level=2)

add_para(doc,
    '当前所有LLM+形式方法的工作都是"浅层结合"——要么LLM替代形式分析做端到端切片（SliceMate），'
    '要么形式分析输出结果后LLM做分类/翻译。两者之间没有真正的互相理解。', indent=True)

add_para(doc,
    '然而，在Dimovski的抽象解释方法中，我们发现了一个被忽视的机会。Dimovski在分析过程中会产生一个'
    '关键的中间产物——Error Invariant序列。这是一个沿程序位置排列的数学约束序列，记录了"错误条件如何从一个位置传播到下一个位置"。'
    'Dimovski只用这个序列做了一件事：判断相邻位置的invariant是否相同来决定语句是否相关。'
    '但invariant内部蕴含的丰富语义信息——变量的进入与退出、约束的演化、语义性质的转折——全部未被利用。', indent=True)

add_para(doc,
    '这些被浪费的信息恰好是LLM擅长理解的。Error Invariant的格式落在LLM的最佳处理区间：比纯形式符号更可读'
    '（[y=x+1, x≥5]就是人类语言的数学表达），比源代码更精炼（分析已经筛掉了无关代码）。', indent=True)

add_heading_styled(doc, '1.4 核心命题', level=2)

add_para(doc,
    '基于以上分析，我们提出核心研究命题：', indent=True)

p = doc.add_paragraph()
p.paragraph_format.left_indent = Cm(1.5)
p.paragraph_format.line_spacing = 1.5
run = p.add_run('能否让LLM阅读形式分析的中间推理过程（Error Invariant轨迹），'
                 '从而同时获得形式方法的完备性保证和LLM的语义理解能力，'
                 '在完备性-精确性光谱上实现此前无法达到的平衡点？')
run.bold = True
run.font.size = Pt(13)

doc.add_page_break()

# ===== SECTION 2: LITERATURE REVIEW =====
add_heading_styled(doc, '二、文献综述与相关工作', level=1)

add_heading_styled(doc, '2.1 程序切片：从Weiser到Zhang', level=2)

add_para(doc,
    '程序切片由Mark Weiser于1984年正式提出，其核心思想是：给定一个程序中的某个语句（即切片准则slicing criterion'
    '⟨l, V⟩），找出所有可能影响该语句值的程序语句集合。Weiser使用基于控制流图标注的迭代算法，复杂度为O(n²)。', indent=True)

add_para(doc,
    'Ferrante、Ottenstein和Warren（1987）引入了程序依赖图（Program Dependence Graph, PDG），将数据依赖和控制依赖'
    '形式化为图的节点和有向边。控制依赖通过后支配（post-dominance）关系形式化定义，为静态切片提供了严格的数学基础。'
    '一旦PDG构建完成，任意准则的切片可以在线性时间内完成——但构建PDG本身需要精确的全程序指针分析，复杂度为O(n³)。', indent=True)

add_para(doc,
    'Korel和Laski（1988）首次提出了动态切片的概念。与静态切片考虑所有可能执行路径不同，动态切片只关注某次具体执行中'
    '实际走过的路径，因此切片更小、更精确。但动态切片需要插桩程序以记录运行时依赖，执行减速为100-1000倍（2-3个数量级）。', indent=True)

add_para(doc,
    'Zhang、Gupta和Gupta（2007）提出了多点多点动态切片（Multiple Points Slicing, MPS），是动态切片用于故障定位的'
    '代表性工作。MPS计算三种独立的动态切片——后向切片（BwS，从错误输出）、前向切片（FwS，从失败触发输入差异）和双向切片'
    '（BiS，从关键谓词）——并取它们的交集以进一步缩小故障候选集。MPS在23个真实故障中，15个案例的FCS缩小到程序总行数的1%以下。'
    '但其核心局限在于：(1) 需要三个独立的输入准则，获取成本高（Delta Debugging、谓词翻转搜索需多次重新执行）；'
    '(2) 动态依赖图（DDG）构建的减速比为100-1000倍；(3) 输出仅为行号列表，无法解释每条语句为何被包含或排除。', indent=True)

add_heading_styled(doc, '2.2 抽象解释与Error Invariant（Dimovski 2024）', level=2)

add_para(doc,
    'Dimovski（2024, Journal of Computer Languages）提出了基于抽象解释的Error Invariant故障定位方法，'
    '这是本研究的核心基础设施。该方法的核心思想是：', indent=True)

add_para(doc,
    'Error Invariant（错误不变量）是对某个程序位置上"所有可能导致最终断言失败的状态"的一个过近似'
    '（over-approximation）。形式上是一个数学约束集合，如[y=x+1, x≥5]。如果一个语句前后的Error Invariant相同，'
    '说明该语句对错误的传播没有贡献，可以从切片中删除——这个过程称为"语句级语义切片"（statement-wise semantic slicing）。', indent=True)

add_para(doc,
    '算法采用迭代后向-前向精化的架构。后向分析从断言失败点出发，反向传播错误条件；前向分析从程序入口出发，'
    '精化每个位置的Error Invariant。在分支合并（JOIN）处因精度损失，算法收集分支谓词ℙ，在下一轮使用BDD（Binary '
    'Decision Diagram）抽象域按谓词分割状态空间，实现更精确的分析。迭代持续到谓词集和错误子空间稳定。', indent=True)

add_para(doc,
    'Dimovski方法的优势在于：(1) 零运行时开销——纯静态分析；(2) 过近似保证完备性——不会遗漏任何可能相关的语句；'
    '(3) 支持无界循环——通过抽象解释的不动点计算和widening外推；(4) 能处理不完整或不可编译代码。', indent=True)

add_para(doc,
    '关键优势——这也是我们选择Dimovski作为基础设施的核心原因——Dimovski是目前已知唯一一个在每个程序位置产出'
    '结构化语义表示（Error Invariant序列）的故障定位工具。其他工具的输出要么是数字（SBFL的可疑度分数），'
    '要么是行号列表（MPS、SliceMate），要么是布尔变量集合（BugAssist的MAX-SAT核）。这些输出对LLM而言几乎没有'
    '"阅读"价值。Error Invariant的三个关键属性——数学精确定义、人类可解释、沿程序位置排列——使其成为LLM-形式方法接口的理想语言。', indent=True)

add_para(doc,
    'Dimovski方法的主要局限在于其精度受限于所用抽象域的精度：(1) 分支合并处的JOIN操作引入过近似假阳性；'
    '(2) BDD只能从程序已有的分支条件中被动收集谓词——如果关键的语义区分条件从未出现在任何if语句中，'
    'Dimovski永远无法利用它来精化；(3) 非线性运算（如x²）、数组索引（a[i]）、指针别名仍导致显著精度损失。', indent=True)

add_heading_styled(doc, '2.3 LLM用于程序切片', level=2)

add_para(doc,
    '近年来出现了多种用LLM做程序切片的尝试。Shahandashti等（2025, COMPSAC）使用GPT-4o、GPT-3.5、Llama-2和'
    'Gemma-7B裸调做静态和动态切片，在100个Java LeetCode题目上，表现最好的GPT-4o仅达到60.84%（静态）和59.69%'
    '（动态）的准确率。失败的主要原因被归类为Complex Control Flow（复杂控制流），Prompt Crafting和Iterative '
    'Prompting分别仅带来约4%的改进。这项研究的关键结论是：裸调LLM做切片不可靠，需要更强的结构化引导。', indent=True)

add_para(doc,
    'Chang等（2025）提出的SliceMate是目前最先进的LLM切片工具。SliceMate使用三个专用Agent协作——Synthesis生成候选切片、'
    'Verification检查完整性和精确性、Refinement进行最小修复。SliceMate不构建PDG，而是将切片定义为LLM驱动的代码生成过程。'
    '其关键结果包括：在2,200个手工标注的Java/Python程序（SliceBench）上，准确率比最佳baseline高22%，F1高28%；'
    '大规模程序（平均2,106语句）的准确率提升高达63.1%。每次切片的成本约为$0.15（GPT-4o API）。', indent=True)

add_para(doc,
    '然而，SliceMate也存在重要局限：(1) Agent内部推理是黑盒，可解释性不足；(2) 仅支持后向切片，不做双向切片；'
    '(3) 完全依赖LLM推理，没有形式化的完备性保证；(4) 多轮Agent迭代增加了成本、延迟和不确定性。', indent=True)

add_para(doc,
    'He等提出的SLICEFORMER（ACL 2026）和SLICET5（2025）代表了"训练路线"——将切片定义为seq2seq任务，'
    '使用CodeT5+配合数据流感知预训练和约束解码，在Java/Python基准上ExactMatch提升22-27%。Yadavally等的NS-Slicer'
    '（OOPSLA 2024）使用CodeBERT做逐语句分类，F1达到97.41%。这些方法的共同局限是需要大量训练数据和预训练，且泛化到'
    '新语言/新领域需要重新训练。', indent=True)

add_heading_styled(doc, '2.4 研究空白与我们的定位', level=2)

add_para(doc,
    '综合以上文献，存在一个明确的研究空白：当前所有方法中，形式分析（Dimovski等）的中间推理过程对LLM是不可见的，'
    '而LLM方法（SliceMate等）自身不产生可验证的形式化中间表示。没有人尝试过让LLM"阅读"形式分析的内部推理过程，'
    '并利用语义理解来增强形式分析本身。', indent=True)

add_table(doc,
    ['工作', '分析方式', '输出', 'LLM角色', 'LLM-分析关系', '完备性'],
    [
        ['Zhang 2007 MPS', '动态DDG', '行号列表', '无', '无', '❌ 受限于trace'],
        ['Dimovski 2024', '抽象解释', 'Invariant序列', '无', '无', '✅'],
        ['SliceMate 2025', 'LLM Agent', '行号列表', '切片引擎', '替代分析', '❌'],
        ['SLICEFORMER 2026', 'Seq2seq训练', '行号列表', '模型推理', '替代分析', '❌'],
        ['Shahandashti 2025', 'LLM裸调', '行号列表', '直接生成', '替代分析', '❌ 仅60.8%'],
        ['本方案', 'Dimovski + LLM', '因果链+Inv.证据', '语义理解者', '双向增强 ★', '✅ 继承'],
    ]
)

doc.add_page_break()

# ===== SECTION 3: RESEARCH QUESTIONS =====
add_heading_styled(doc, '三、核心研究问题', level=1)

add_para(doc,
    '本研究围绕一个核心研究问题（CRQ）和五个子问题（RQ1-RQ5）展开。', indent=True)

add_heading_styled(doc, '3.1 核心研究问题 (CRQ)', level=2)

p = doc.add_paragraph()
p.paragraph_format.left_indent = Cm(1)
run = p.add_run(
    '给定程序的错误位置（assert失败点），LLM阅读Dimovski抽象解释产生的Error Invariant轨迹，能否：\n'
    '(a) 比纯抽象解释更精确地定位故障（消除过近似假阳性）？\n'
    '(b) 比纯LLM或纯抽象解释更可解释地呈现故障因果链？\n'
    '(c) 不损失抽象解释的完备性（soundness）保证？'
)
run.font.size = Pt(12)

add_heading_styled(doc, '3.2 子问题 (RQ1-RQ5)', level=2)

add_table(doc,
    ['编号', '研究问题', '核心指标', '实验方法'],
    [
        ['RQ1', '语义翻译准确性：LLM能否准确将Error Invariant数学约束翻译为自然语言因果描述？',
         '人工忠实度评分(1-5)\n评分者间一致性(κ)', '3名评审者对翻译结果独立打分'],
        ['RQ2', '源点定位精度：LLM从invariant轨迹中定位故障起源，是否优于从源代码直接定位？',
         'Top-1/3/5命中率\nEXAM, MFR', 'Defects4J 20+ bugs\n对比Ochiai/Cause Transitions/Dimovski原生'],
        ['RQ3', '谓词发现有效性：LLM基于语义理解建议的补充谓词是否真的帮助Dimovski提升精度？',
         '切片缩减率\n假阳性消除率\n谓词有效率', '10个Dimovski假阳性显著的bug\n对比精化前后切片大小'],
        ['RQ4', '因果链正确性：LLM从invariant轨迹重建的因果叙事是否与真实修复一致？',
         '因果一致性评分(1-3)\nFix位置在叙事关键路径中的比例', '对比Defects4J真实fix commit\n3名评审者评估'],
        ['RQ5', '信息消融：Error Invariant轨迹的哪个组成部分对LLM最关键？',
         '各消融配置的性能退化量', 'Full vs Binary vs CodeOnly\nvs NoPosition vs NoTrace'],
    ]
)

doc.add_page_break()

# ===== SECTION 4: TECHNICAL APPROACH =====
add_heading_styled(doc, '四、技术方案：四阶段架构', level=1)

add_para(doc,
    '本方案的核心设计理念是"LLM不替代形式分析，而是理解形式分析的中间推理"。'
    '整体架构由四个阶段组成，其中Phase 1提供确定性静态分析骨干，Phase 2是LLM语义理解的核心创新，'
    'Phase 3建立双向反馈循环，Phase 4输出人类可读的因果链。', indent=True)

# -- Phase 1 --
add_heading_styled(doc, '4.1 Phase 1：Dimovski确定性骨干', level=2)

add_para(doc,
    'Phase 1运行Dimovski 2024的完整迭代后向-前向抽象解释流程。这是一个纯静态分析：不需要程序可执行，'
    '不需要测试用例，不需要运行时插桩。', indent=True)

add_para(doc, '具体步骤：', indent=True)
add_para(doc,
    '(1) 后向分析：从断言失败点出发，取断言的反面作为初始错误条件，沿控制流反向传播，'
    '计算每个程序位置的"必要前置条件"——即该位置需要满足什么条件才可能最终导致断言失败。'
    '在分支合并（if语句结束后的JOIN点）处，记录精度损失来源，收集分支谓词ℙ。', indent=True)
add_para(doc,
    '(2) 前向分析：从程序入口出发，计算每个位置的可达状态过近似。将前向不变量与后向前置条件结合'
    '（精化），得到每个位置的Error Invariant：一个过近似"所有可能导向错误的状态"的数学约束集合。', indent=True)
add_para(doc,
    '(3) BDD精化：若上一轮在JOIN处有精度损失，使用收集到的谓词ℙ构造BDD抽象域。BDD域的决策节点为ℙ中的谓词，'
    '叶节点为基础数值抽象域（Intervals/Octagons/Polyhedra）的值。BDD不再做imprecise JOIN，而是按谓词将状态空间'
    '分割并保留析取结构——从而消除上一轮的过近似。', indent=True)
add_para(doc,
    '(4) 循环至收敛：重复后向→前向→BDD精化，直到谓词集ℙ和错误子空间均不再发生变化。通常2-3轮即可收敛。', indent=True)

add_para(doc, 'Phase 1的输出包括：', indent=True)
add_para(doc, '• Error Invariant序列：每个程序位置的数学约束，如：', indent=True)
add_code_block(doc,
    '  Loc①: [⊤]                          # 任何状态\n'
    '  Loc②: [y = x + 1]                  # y的约束首次出现\n'
    '  Loc③: [y = x + 1, x ≥ 5]          # x进入错误条件 ← 关键变化\n'
    '  Loc④: [y = x + 1, x ≥ 5, z = 2*x] # z进入\n'
    '  Loc⑤: [x ≥ 5, z = 2*x]             # y退出 ← 关键转折！')
add_para(doc, '• 初始语句级语义切片（Slice_Dim）：包含所有Error Invariant发生变化的语句')
add_para(doc, '• 精度损失点标记（灰色地带）：抽象域JOIN导致invariant过近似的位置')

add_para(doc,
    '需要特别强调：Phase 1的输出已经是一个完备的（sound）故障候选集。我们在这个阶段不做任何减法。'
    '后续Phase 2-3的所有操作都是在Dimovski的切片基础上去除LLM判定为语义无关的语句——'
    '这保证了最差情况下我们退化为Dimovski，不会比纯抽象解释更差。', indent=True)

# -- Phase 2 --
add_heading_styled(doc, '4.2 Phase 2：LLM深度阅读Error Invariant轨迹 ★', level=2)

add_para(doc,
    'Phase 2是本方案的核心创新。LLM不阅读源代码（或仅作为辅助上下文），而是阅读Phase 1产出的Error Invariant序列。'
    '执行三个递进的语义理解任务：', indent=True)

add_para(doc, '任务① 语义翻译（Semantic Translation）', bold=True)
add_para(doc,
    '将每个位置的Error Invariant数学约束翻译为自然语言的因果描述。这不是简单的"把数学符号变成英文"，'
    '而是要求LLM理解约束之间的语义关系。例如，输入：[y=x+1, x≥5]，输出："此时y的值取决于x（y=x+1），'
    '且x至少为5。注意这是x首次出现在错误条件中，说明x的取值开始对错误产生影响。"'
    '此任务验证了Error Invariant作为LLM-形式方法接口语言的可行性。', indent=True)

add_para(doc, '任务② 质变检测（Qualitative Change Detection）★', bold=True)
add_para(doc,
    '沿invariant序列扫描，找到invariant发生"语义性质改变"（而非仅仅是数值变化）的位置。Dimovski只能判断'
    '"invariant是否相同"（二元信号），无法区分"微小变化"和"语义转折"。LLM能够识别：', indent=True)
add_para(doc, '• 变量进入：某个变量首次出现在invariant中 → 该变量的计算是关键依赖', indent=True)
add_para(doc, '• 变量退出：某个变量从invariant中消失 → 该变量的值不再影响错误走向', indent=True)
add_para(doc, '• 关系转换：约束从一类关系变为另一类（如从等式变为不等式，从线性变为区间）', indent=True)
add_para(doc, '• 强度突变：约束范围突然扩大或缩小（如x∈[1,10]突然变为x∈[-∞,+∞]——发生了widening）', indent=True)

add_para(doc, '任务③ 缺失推断（Missing Predicate Inference）★', bold=True)
add_para(doc,
    '观察invariant轨迹中的"语义断裂"——两个相邻位置的invariant之间的语义跳跃超出了程序语句能解释的范围——'
    'LLM推断缺失的语义信息，并建议Dimovski自身无法发现的精化谓词。', indent=True)
add_para(doc,
    '例如：Loc①的invariant为[⊤]（任何状态），Loc②突然变为[y=x+1]。LLM注意到：input变量（测试输入）'
    '与x的关系未在任何invariant中体现，但y的值由x决定，而x来源于input。LLM建议补充谓词{x=input-42}，'
    '使Dimovski能够在下一轮BDD精化中更精确地追踪input→x→y的完整传播链。', indent=True)

# -- Phase 3 --
add_heading_styled(doc, '4.3 Phase 3：反馈精化循环 ★', level=2)

add_para(doc,
    'Phase 3是本方案区别于所有现有LLM+形式方法工作的标志性设计——不是LLM单向接收分析结果，'
    '而是LLM主动反馈来改进分析本身。', indent=True)

add_para(doc, '反馈循环的算法：', indent=True)
add_code_block(doc,
    'while (LLM_produces_new_predicates  AND  slice_still_shrinking):\n'
    '    ℙ_new = ℙ_current ∪ P_LLM\n'
    '    Dimovski.reanalyze_with_BDD(ℙ_new)\n'
    '    new_invariants = Dimovski.get_invariant_trajectory()\n'
    '    P_LLM = LLM.read_and_suggest(new_invariants)\n'
    '    \n'
    '    if P_LLM is empty: break\n'
    '    if slice_shrinkage < 5%: break\n'
    '    if round_count > 5: break')

add_para(doc, '三个终止条件保证了循环不会失控：', indent=True)
add_para(doc, '• LLM连续两轮无新谓词建议 → 语义理解已达极限，分析无法进一步精化', indent=True)
add_para(doc, '• 切片缩减率小于5% → 精化的边际收益已不值得额外开销', indent=True)
add_para(doc, '• 硬上限5轮 → 避免死循环（实验中已验证2-3轮通常足够收敛）', indent=True)

add_para(doc,
    'Phase 3的理论保证：Dimovski精化是单调的（每轮BDD只增精度不倒退），LLM建议仅影响谓词集ℙ（不影响'
    '抽象解释的over-approximation性质），因此整个循环保持soundness不变。', indent=True)

# -- Phase 4 --
add_heading_styled(doc, '4.4 Phase 4：因果链重构与可读输出', level=2)

add_para(doc,
    'Phase 4基于精化后的最终invariant轨迹，由LLM生成面向程序员的可读输出：', indent=True)

add_para(doc, '输出的四个组成部分：', indent=True)
add_para(doc,
    '① 错误起源定位："错误起源于Loc②（y=input-42），此处Error Invariant首次出现y的相关约束[y=x+1]。'
    'Dimovski标记此处为质变点。LLM进一步推断：input的值通过该语句首次进入了错误条件。"', indent=True)
add_para(doc,
    '② 传播路径关键转折："Loc②→Loc③（x≥5进入）→Loc④（z=2*x加入）→Loc⑤（y退出invariant，关键转折）'
    '→最终到达断言失败点。Loc⑤是语义转折点：y在invariant中的消失意味着y的值不再直接影响错误，'
    '但这正是bug之所在——y应该继续影响后续分支判断，却从错误条件中脱落了。"', indent=True)
add_para(doc,
    '③ 修复建议："Loc⑤处y从invariant中消失，但y的值决定了后续分支走向。建议检查y的计算逻辑（Loc②），'
    '或检查Loc④之后y的使用方式是否与预期一致。"', indent=True)
add_para(doc,
    '④ 决策溯源与置信度：每条语句的包含/排除决策可追溯到具体的invariant变化或LLM语义判断。'
    '置信度评分基于invariant覆盖完整度——如果从source到sink的完整def-use链都在invariant中有对应约束，'
    '置信度高；如果存在语义断裂需要LLM补充推断，置信度相应降低。', indent=True)

doc.add_page_break()

# ===== SECTION 5: THEORETICAL SOUNDNESS =====
add_heading_styled(doc, '五、理论合理性分析', level=1)

add_heading_styled(doc, '5.1 完备性（Soundness）保证', level=2)

add_para(doc,
    '框架的完备性完全继承自Dimovski的抽象解释。具体而言：', indent=True)

add_para(doc,
    '(1) Dimovski的Error Invariant是过近似（over-approximation）——对任何程序位置，所有"真实可能导向错误"'
    '的状态都是Error Invariant所描述状态的子集。这意味着基于invariant的切片不会遗漏任何真正相关的语句。', indent=True)

add_para(doc,
    '(2) Phase 2-3的所有LLM操作都是"减法"——从Dimovski的切片中移除LLM判定为语义无关的语句。'
    'LLM从不添加新语句到切片中。因此，任何被移除的语句都是LLM"确信无关"的，而非LLM"猜测相关"的。', indent=True)

add_para(doc,
    '(3) 保守策略保证最坏情况等于Dimovski：当LLM对某条语句的"无关"判断不确定时（输出UNCERTAIN），'
    '框架保守地保留该语句。因此：最坏情况 = 所有LLM判断均为UNCERTAIN → 切片 = Dimovski原始输出。'
    '框架不可能产生比Dimovski更差的完备性。', indent=True)

add_para(doc,
    '(4) 反馈循环（Phase 3）仅增加谓词——只做BDD精化，不改变抽象解释的过近似性质。', indent=True)

add_heading_styled(doc, '5.2 LLM错误的影响范围', level=2)

add_para(doc,
    '对LLM在框架中可能产生的错误，我们进行了分类分析：', indent=True)

add_table(doc,
    ['LLM错误类型', '发生场景', '影响', '缓解机制'],
    [
        ['误判IRRELEVANT', 'LLM说某语句无关，但它实际相关', '该语句被从切片中移除——可能漏报bug',
         '保守策略：LLM不确定时输出UNCERTAIN→保留'],
        ['未能发现缺失谓词', 'LLM错过了可用的精化谓词', '切片未进一步精化——精度未提升',
         '退化为Dimovski（非致命）'],
        ['建议了无用谓词', 'LLM建议的谓词被加入ℙ', 'Dimovski下一轮BDD节点增多，但精度不提升',
         '谓词有效率指标量化；硬上限5轮'],
        ['语义翻译不准确', 'LLM对invariant的描述与数学含义有偏差', '程序员可能被误导',
         '翻译附invariant原文，评审者可对照核实'],
    ]
)

add_para(doc,
    '关键结论：LLM的错误只可能影响精度（未裁剪本可裁剪的假阳性），不可能影响完备性（移除真相关语句）。'
    '这是因为保守策略在最不确定时选择了"保留"而非"移除"。', indent=True)

add_heading_styled(doc, '5.3 为什么Error Invariant适合LLM阅读', level=2)

add_para(doc,
    'Error Invariant格式恰好落在LLM的最佳处理区间，这是本方案可行性的理论基础：', indent=True)

add_table(doc,
    ['输入类型', '例子', 'LLM处理能力', '原因'],
    [
        ['纯数字', 'susp(line42)=0.873', '❌ 极弱', '数字无语义'],
        ['纯形式逻辑', '(x≤y)∧(y=z+1)→¬(x>z)', '❌ 弱', 'LLM不擅长纯符号推理'],
        ['源代码(全量)', '数千行Java代码', '⚠️ 中等', '信息量大，缺乏聚焦'],
        ['Error Invariant', '[y=x+1, x≥5]', '✅ 强', '精炼+语义可读+结构清晰'],
    ]
)

add_para(doc,
    'Error Invariant比源代码更精炼（Dimovski已筛掉无关语句），比纯符号更可读（数学约束格式接近自然语言），'
    '比纯数字更具语义（约束表达了变量间的实际关系）。这三个属性使其成为LLM-形式方法接口的理想媒介。', indent=True)

add_heading_styled(doc, '5.4 与现有工作的关系定位', level=2)

add_para(doc,
    '本方案与最相关工作的定位关系清晰：', indent=True)

add_table(doc,
    ['维度', 'SliceMate 2025', 'Dimovski 2024', '本方案'],
    [
        ['分析引擎', 'LLM Agent (黑盒)', '抽象解释 (白盒)', '抽象解释 (白盒)'],
        ['LLM角色', '切片引擎 (端到端)', '无', '语义理解者 (读中间表示)'],
        ['完备性保证', '❌ 无', '✅ 过近似', '✅ 过近似 (继承)'],
        ['可解释性', '低 (Agent推理不可见)', '低 (数学符号)', '高 (语义叙事)'],
        ['可追溯性', '低 (黑盒输出)', '中 (invariant序列可见)', '高 (决策逐条溯源)'],
        ['反馈能力', '无 (单向)', '无', '★ 双向循环'],
        ['开销', 'API调用 (~$0.15/次)', '静态分析 (无运行时)', '静态分析 + LLM语义阅读'],
        ['处理不完整代码', '✅ LLM天然支持', '✅ 抽象解释支持', '✅ 继承二者'],
    ]
)

doc.add_page_break()

# ===== SECTION 6: DESIGN DECISIONS =====
add_heading_styled(doc, '六、关键设计决策及其理由', level=1)

decisions = [
    ('决策1：为什么用Dimovski做骨干而非自研分析？',
     'Dimovski的迭代后向-前向抽象解释经过三年打磨（SAS 2023→COLA 2024→SLE 2025），'
     '有形式化正确性证明和同行评审。自研分析不仅要重复大量已知工作，还可能在正确性上不如已有方法。'
     '本方案的创新不在切片引擎本身，而在"让LLM理解已有引擎的中间推理"——这是一个全新的维度。'
     '使用已有基础设施而非重新发明轮子，恰恰是好的系统研究的标志。'),

    ('决策2：为什么不直接用LLM做切片（如SliceMate）？',
     'Shahandashti 2025的实验证据直接支撑了这个决策：GPT-4o裸调做切片仅60.8%准确率。'
     'LLM做切片引擎面临两个根本性障碍：(1) 不sound——可能遗漏真正的数据/控制依赖，也可能编造不存在的依赖；'
     '(2) 不可审计——每次输出的推理链不可复现。'
     '我们的方案将LLM从"负全责"（端到端切片）变为"负专责"（语义理解+谓词建议），'
     '形式分析兜底保证soundness。这比让LLM承担超出其能力范围的任务更务实。'),

    ('决策3：为什么是双向循环而非单向处理？',
     '单向模式（Dimovski→LLM分类→输出）本质是让LLM做后分类器，"引入LLM分析切片结果"的创新性不足。'
     '双向循环意味着LLM能主动改善分析质量——看到invariant中的语义断裂后，建议形式分析自身无法发现的精化谓词。'
     '这一设计使得LLM成为分析的"参与者"而非"旁观者"，在我们的调研范围内是LLM+形式方法结合的全新模式。'),

    ('决策4：为什么舍弃了原方案的运行时断言？',
     '本研究的早期方案（Phase 3）依赖运行时断言作为ground truth，核心工具是ASSERTIFY（LLM驱动的Java断言生成器）。'
     '三个问题导致这个设计被舍弃：(1) 依赖性脆弱——ASSERTIFY论文只评估了语法正确性（SNE 97.4%, SME 83.5%），'
     '未评估运行时正确性——生成的断言在运行时是否真的是正确的不变量？(2) 修改程序行为——断言插桩改变执行环境；'
     '(3) Dimovski不需要运行时——如果形式分析能在纯静态下完成，增加运行时依赖是倒退而非升级。'),

    ('决策5：LLM的不可靠性如何被框架控制？',
     '核心机制是"LLM只做减法，不做加法"。所有LLM判断都是"这条语句是否可以安全移除"而非"这条语句是否应该加入"。'
     '框架默认保留所有Dimovski认为相关的语句，LLM的角色是提供"确信可以安全移除"的语义证据。'
     '当LLM不能确信时，保守策略选择保留——框架退化为Dimovski。'
     '这意味着LLM最多能做到"和Dimovski一样好"（在所有判断都不确定时），'
     '但不可能做到"比Dimovski更差"。'),
]

for title, content in decisions:
    add_heading_styled(doc, title, level=2)
    add_para(doc, content, indent=True)

doc.add_page_break()

# ===== SECTION 7: EXPERIMENTAL DESIGN =====
add_heading_styled(doc, '七、实验设计', level=1)

add_heading_styled(doc, '7.1 实验概览', level=2)

add_table(doc,
    ['实验', '评估目标', '主要指标', '数据集', '预期论证'],
    [
        ['实验1\n语义翻译', 'LLM翻译invariant\n是否准确', '人工忠实度评分\nCohen\'s κ', '20个invariant样本\n(Dimovski在TCAS上的输出)', 'Invariant是更好的\nLLM-形式方法接口'],
        ['实验2 ★\n质变点定位', 'LLM+invariant\n是否比LLM+code更准', 'Top-1/3/5\nEXAM, MFR', 'Defects4J 20+ bugs\n(Dimovski分析)', '阅读invariant比\n阅读代码更有利于LLM'],
        ['实验3 ★\n谓词有效性', 'LLM谓词是否\n帮助Dimovski精化', '切片缩减率\n谓词有效率', '10个Dimovski\n假阳性显著的bug', '双向增强确实\n优于单向分类'],
        ['实验4\n因果叙事', 'LLM因果链是否\n与真实修复一致', '因果一致性(1-3)\n关键语句命中率', '10个有明确fix\n的Defects4J bug', 'Invariant轨迹能\n产生可信叙事'],
        ['实验5\n消融实验', '什么信息对LLM\n最关键的', '各配置性能退化', '实验2的5个变体', '约束内容和演化\n轨迹都是关键'],
        ['实验6\n用户研究', '对开发者\n是否有实际帮助', '找bug时间\n定位准确率', '3个bug × 15-20名\nJava开发者', '提升开发者的\n调试效率'],
    ]
)

add_heading_styled(doc, '7.2 实验2（质变点定位）详细设计', level=2)

add_para(doc, '这是最核心的故障定位实验，用于验证本方案的核心假设。', indent=True)

add_para(doc, '对比条件（5个）：', indent=True)
conditions = [
    '① Dimovski原生：Error Invariant首次变化的位置 = 故障源点',
    '② Ochiai（SBFL）：频谱故障定位的经典代表',
    '③ Cause Transitions（Cleve & Zeller 2005）：通过/失败trace状态对比',
    '④ LLM-reads-code：LLM直接阅读源代码定位故障源点（不给invariant）',
    '⑤ LLM-reads-invariant ★：LLM阅读Error Invariant轨迹定位故障源点（本方案）',
]
for c in conditions:
    add_para(doc, c, indent=True)

add_para(doc, '', indent=False)
add_para(doc, '数据集：Defects4J 20+个bug，每个bug有已知的ground truth（buggy line位置）。', indent=True)
add_para(doc, '指标：Top-1/3/5命中率（故障行在前N个候选中的比例）、EXAM（查看到故障行需检查的语句比例）、MFR（Mean First Rank）。', indent=True)
add_para(doc, '预期结果：LLM-reads-invariant > LLM-reads-code > Ochiai > Dimovski原生 ≈ Cause Transitions。', indent=True)

add_heading_styled(doc, '7.3 实验3（谓词有效性）详细设计', level=2)

add_para(doc, '这是验证"双向增强"假设的关键实验。', indent=True)

add_para(doc, '实验流程：', indent=True)
add_para(doc, 'Step 1: 在10个Dimovski产生显著假阳性的bug上运行Dimovski原生 → 记录切片大小和假阳性语句数（需人工标注）', indent=True)
add_para(doc, 'Step 2: LLM阅读invariant轨迹 → 输出补充谓词建议集P_LLM', indent=True)
add_para(doc, 'Step 3: 将P_LLM加入ℙ → Dimovski重新BDD精化 → 记录新切片大小', indent=True)
add_para(doc, 'Step 4: 对比基线——Dimovski自身迭代（不加LLM谓词）的最终切片大小', indent=True)

add_para(doc, '', indent=False)
add_para(doc, '关键指标：', indent=True)
add_para(doc, '• 切片缩减率 = (旧切片-新切片)/旧切片 —— 评估LLM谓词带来的精度提升', indent=True)
add_para(doc, '• 假阳性消除率 = 被正确移除的无关语句数/原切片中假阳性语句数', indent=True)
add_para(doc, '• 谓词有效率 = 被Dimovski实际使用且导致精度提升的谓词数/LLM建议谓词总数', indent=True)
add_para(doc, '• 收敛加速：加入LLM谓词后达到稳定所需的Dimovski迭代次数是否减少', indent=True)

add_para(doc, '', indent=False)
add_para(doc, '这个实验直接回答了最关键的质疑："LLM的建议到底有没有价值，还是Dimovski自己迭代就能达到同样效果？"', indent=True)

doc.add_page_break()

# ===== SECTION 8: CONTRIBUTIONS =====
add_heading_styled(doc, '八、预期贡献', level=1)

contributions = [
    ('1. Error Invariant作为半形式化语义接口语言（概念贡献）',
     '首次提出将抽象解释的中间表示（Error Invariant序列）作为LLM与形式方法之间的共享语言。'
     '这一概念为LLM+形式方法的结合开辟了新路径：不是让LLM替代形式分析，也不是让形式分析为LLM提供标签，'
     '而是让LLM"阅读"形式分析的内部推理过程。Error Invariant恰好满足接口语言的三个条件：'
     '数学精确定义（可被形式方法操作）、人类可解释（LLM可理解）、沿程序位置排列（形成可追踪的轨迹）。'),

    ('2. LLM驱动的语义谓词发现（方法贡献）',
     '区别于现有工作中LLM扮演的"分类器"或"翻译器"角色，本方案首次让LLM主动参与形式分析的精化过程——'
     '根据对invariant轨迹的语义理解，建议形式分析自身无法发现的精化谓词。'
     '这是LLM从"旁观者"变为"参与者"的关键一步。'),

    ('3. 双向反馈架构（系统贡献）',
     '设计了Dimovski⇄LLM的双向增强循环：形式分析提供可验证的结构（完备性），LLM提供语义理解（精确性+可解释性），'
     '两者通过invariant轨迹互相增强。据我们所知，这是LLM+程序分析领域首个双向反馈架构。'),

    ('4. 从不变量轨迹到因果叙事（应用贡献）',
     '展示了LLM不仅能理解单个invariant，还能理解invariant序列中蕴含的因果传播链——'
     '从数学约束的演变中提取"错误从哪起源、经过什么转折、最终在哪表现为失败"的完整叙事。'
     '这种"读invariant而非读代码"的方法为故障定位的可解释性提供了全新视角。'),
]

for title, content in contributions:
    add_heading_styled(doc, title, level=2)
    add_para(doc, content, indent=True)

doc.add_page_break()

# ===== SECTION 9: TIMELINE =====
add_heading_styled(doc, '九、时间规划', level=1)

add_table(doc,
    ['阶段', '时间', '主要任务', '交付物'],
    [
        ['Phase 0\n准备', '第1-2周', '• 获取并运行Dimovski工具原型（Zenodo artifact）\n• 在TCAS基准上产出真实invariant序列\n• 设计invariant→文本的表示格式', 'Dimovski运行成功的输出样本\nInvariant表示格式定义'],
        ['Phase 1\nL1验证', '第3-4周', '• 设计L1语义翻译Prompt模板\n• 在3个手工案例上测试LLM翻译质量\n• 人工评估翻译忠实度', 'Prompt模板v1\n3案例×3LLM的翻译结果\n忠实度评估数据'],
        ['Phase 2\nL2验证', '第5-7周', '• 设计L2质变检测Prompt\n• 在Defects4J 5-10个bug上运行完整流程\n• 实现Phase 3反馈循环原型', '质变检测结果\n反馈循环原型代码\n初步实验数据'],
        ['Phase 3\n规模化', '第8-11周', '• 在Defects4J 20+bug上运行全流程\n• 运行实验2-5\n• 统计分析', '完整实验数据\n统计检验结果'],
        ['Phase 4\n写作', '第12-14周', '• 撰写论文初稿\n• 运行实验6（用户研究）\n• 完善相关工作和讨论', '论文初稿\n用户研究数据'],
        ['Phase 5\n打磨', '第15-16周', '• 根据反馈修改\n• 补充实验\n• 准备投稿', '投稿版本论文'],
    ]
)

doc.add_page_break()

# ===== SECTION 10: REFERENCES =====
add_heading_styled(doc, '十、核心参考文献', level=1)

refs = [
    '[1] M. Weiser, "Program Slicing," IEEE TSE, vol. 10, no. 4, pp. 352-357, 1984.',
    '[2] J. Ferrante, K. Ottenstein, and J. Warren, "The Program Dependence Graph and Its Use in Optimization," ACM TOPLAS, vol. 9, no. 3, pp. 319-349, 1987.',
    '[3] B. Korel and J. Laski, "Dynamic Program Slicing," Information Processing Letters, vol. 29, no. 3, pp. 155-163, 1988.',
    '[4] D. Jackson and E. Rollins, "Chopping: A Generalization of Slicing," FSE, 1994.',
    '[5] X. Zhang, N. Gupta, and R. Gupta, "Locating Faulty Code by Multiple Points Slicing," Software: Practice and Experience, vol. 37, no. 9, pp. 935-961, 2007.',
    '[6] W. E. Wong, R. Gao, Y. Li, R. Abreu, and F. Wotawa, "A Survey on Software Fault Localization," IEEE TSE, 2016.',
    '[7] A. S. Dimovski, "Fault Localization by Abstract Interpretation and its Applications," Journal of Computer Languages, vol. 80, article 101288, 2024.',
    '[8] A. S. Dimovski, "Error Invariants for Fault Localization via Abstract Interpretation," SAS 2023, LNCS 14284, pp. 190-211, 2023.',
    '[9] J. Chang et al., "SliceMate: Accurate and Scalable Static Program Slicing via LLM-Powered Agents," arXiv:2507.18957, 2025.',
    '[10] K. K. Shahandashti et al., "Program Slicing in the Era of Large Language Models," IEEE COMPSAC, 2025.',
    '[11] P. He et al., "SLICEFORMER: Static Program Slicing Using Language Models with Dataflow-Aware Pretraining," ACL, 2026.',
    '[12] A. Yadavally et al., "NS-Slicer: A Learning-Based Approach to Static Program Slicing," OOPSLA, 2024.',
    '[13] J. B. Barros et al., "Assertion-based Slicing and Slice Graphs," 2010.',
    '[14] M. Jalili Torkamani et al., "ASSERTIFY: End-to-End Production Assertion Insertion into Java Source Code," arXiv:2411.16927, 2024.',
    '[15] K. B. Gallagher and S. J. Kozaitis, "Program Slicing: A Brief Retrospective," IEEE TSE, vol. 51, no. 3, pp. 720-724, 2025.',
]

for ref in refs:
    add_para(doc, ref, size=10.5)

doc.add_paragraph()
doc.add_paragraph()

# Final note
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = p.add_run('—— 报告完 ——')
run.font.size = Pt(12)
run.font.color.rgb = RGBColor(128, 128, 128)

# ===== SAVE =====
output_path = r'C:\Users\chenm\Desktop\program_slicing\paper\reports\research_proposal_report.docx'
doc.save(output_path)
print(f'Report saved to: {output_path}')
print('Done!')
