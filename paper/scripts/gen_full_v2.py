# -*- coding: utf-8 -*-
import docx
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.element.rPr.rFonts.set(qn("w:eastAsia"), "SimSun")

def h(text, level=1): doc.add_heading(text, level=level)
def p(text, bold=False):
    para = doc.add_paragraph()
    run = para.add_run(text)
    if bold: run.bold = True
    return para
def bp(): doc.add_page_break()

doc.add_paragraph(); doc.add_paragraph()
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("Cascaded Hybrid Slicing\nfor Fault Localization"); r.bold = True; r.font.size = Pt(24)
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("级联混合切片故障定位"); r.font.size = Pt(16); r.font.color.rgb = RGBColor(80,80,80)
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("科研过程全记录"); r.font.size = Pt(14); r.font.color.rgb = RGBColor(80,80,80)
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
t.add_run("研究起始:2026年初 | 正式搭建:2026-05-20 | 文档生成:2026-07-12")
bp()
h("第一章  研究的起点")
p("本章记录研究的第一个阶段:从系统学习程序切片这一经典技术,到发现双向切片(Chop)的价值,再到最终确立 Chop 与 LLM 结合的研究方向.这个阶段持续了整个 2026 年初至 2026 年 5 月.")

h("1.1  最初的方向:程序切片在调试中的应用", 2)
p("研究始于对程序切片(Program Slicing)这一经典程序分析技术的系统学习.程序切片最早由 Weiser 于 1984 年提出,其核心思想是:给定一个程序中的某个语句(即切片准则 slicing criterion),找出所有可能影响该语句值的程序语句集合.这个方法被广泛用于软件调试------程序员看到一个错误输出,想知道哪些代码导致了它.")
p("研究者系统阅读了该领域的奠基性文献:")
p("(1) Weiser(1984)------程序切片的原始定义,开创了整个研究领域.")
p("(2) Ferrante,Ottenstein 和 Warren(1987)------引入程序依赖图(Program Dependence Graph, PDG),将数据依赖和控制依赖形式化为图的节点和有向边,为静态切片提供了严格的数学基础.")
p("(3) Korel 和 Laski(1988)------首次提出动态切片概念.与静态切片考虑所有可能的程序执行路径不同,动态切片只关注某次具体执行中实际走过的路径,因此产出的切片更小,更精确.")
p("在深入理解后向切片(从错误输出点回溯所有可能影响该输出的语句)和前向切片(从某个输入或赋值出发,追踪它可能影响的所有语句)的基本概念后,研究者发现了动态后向切片的一个核心局限:它是依赖关系的传递闭包.对于一个包含一万行代码的方法,后向切片虽然能把搜索范围从一万行缩减到约五百行,但它不会自动在 bug 所在的那一行停下来.它会把从错误点到程序入口的所有依赖链上的语句都包含进来,程序员还是得从头看到尾.更根本的问题是:后向切片没有回答程序员真正想知道的问题------bug 到底是从哪一行开始的?")

h("1.2  发现 Chop:为切片引入第二个锚点", 2)
p("在探索如何改进动态后向切片的过程中,研究者思考了前向切片和后向切片结合的可能性.一个重要发现是 Jackson 和 Rollins 于 1994 年发表的论文 Chopping: A Generalization of Slicing.")
p("Chop 的核心思想非常简洁而深刻:通过引入第二个锚点(source 源点),将切片从一条单方向的追溯变成两个锚点之间的定向搜索.传统切片只需要一个 criterion(比如错误输出点),然后沿着依赖链无限追溯.Chop 则要求同时给出 source(怀疑的源语句或输入点)和 sink(错误输出点),在 PDG 上计算从 source 到 sink 的所有可达路径上的节点集合------恰好连接两者的语句链.")
p("Jackson 和 Rollins 在论文中指出了传统 PDG 取交集方法的关键缺陷:直接简单地将前向切片和后向切片取交集,可能包含逻辑上根本不在同一条因果链上的节点.一个节点 A 可能在前向切片中是因为某条路径,在后向切片中却是因为另一条完全不同的路径,这两条路径根本没有连接起来.Chop 通过受限于前向可达子图再计算后向切片的算法,解决了这个问题.")
p("研究者用一个具体例子验证了这个理解:考虑方法 add(),输入是 x 的初始值.问题是:初始值 x 如何影响最终值 s?正向切片(source={x_entry})得到 {x=1, add(), x<11};反向切片(sink={s_exit})得到 {s=0, add(), x<11}.错误地取交集会漏掉 x=1 和 s=0------但如果用 chop 算法(先限制到前向可达子图再做后向切片),结果恰好是 {x=1, add(), x<11},完整且精确.")
p("研究者敏锐地意识到:Chop 的第二个锚点(source)本质上是一个人工输入.如果程序员需要手动指定 source 在哪里,那么这个方法的自动化程度就大打折扣.但如果能用大语言模型(LLM)自动推测 bug 可能的 source 候选点,Chop 就能从一个需要人工辅助的方法变成一个自动化调试工具.这就是将 Chop 与 LLM 结合的核心动机.")

h("1.3  确立方向:Chop + LLM", 2)
p("基于上述推理,研究者在 2026 年 5 月做出关键决策:将双向切片(Chop)与大语言模型(LLM)结合,探索自动化调试的新范式.同时期调研了多个开源程序分析工具,为后续实现做准备:")
p("WALA(IBM, 2006 年至今):Java 程序分析框架,使用自研的 Jimple 中间表示,支持完整的指针分析和 PDG 构建.有 20 余年历史,成熟度高.")
p("dg:LLVM 生态下的 C/C++ 程序依赖图构建工具(学术项目).")
p("giri:LLVM 动态切片工具(学术项目).")
p("Slicer4J(2022):Java 程序切片 benchmark 数据集,包含来自 12 个真实开源项目的约 1200 个切片样本.")
p("CodeQL:GitHub 提供的代码查询与静态分析引擎.")
bp()
h("第二章  基础工具探索与研究方向转折")
p("时间:2026-05-20 至 2026-06-06")

h("2.1  从最新论文出发:重新思考 LLM 的角色", 2)
p("在确定了 Chop + LLM 方向后,研究者在 2026 年暑假期间大量阅读了该领域的最新论文.这个阅读过程带来了一个关键认知转变.")
p("研究者发现,自己最初构想的方案------先用程序分析工具(Chop4LLM)做切片,再把切片结果交给 LLM 去分析------在思路上其实并不新颖.多篇最新论文已经触及了类似的想法:")
p("-- Zhang 和 Gupta 等人(2004, PLDI)的实用动态切片工作,已经探索了在大规模 trace 上做压缩动态依赖图的技术,其核心的 Multiple Points Slicing(MPS)方法需要三个输入点取交集来确定故障位置.")
p("-- NESA(FSE 2026,神经符号静态分析)把 Datalog 子问题拆解后交给 LLM 逐个解决,在切片和漏洞检测任务上达到了 F1=0.72.")
p("-- CLDK / CodeLLM-Devkit(IBM, ICSE 2025)直接把 PDG 分析定义为分析层级,试图在程序分析工具和 LLM 之间架桥,但后端 PDG 构建部分标注了 not yet implemented.")
p("-- SLICE(NeurIPS 2025)从 AST 构建语义知识图谱,结合后向切片检索,在代码生成任务上实现了 48-67% 的提升.")
p("-- codebadger(SVM 2026)用 MCP 协议封装 Joern CPG 引擎,让 LLM 可以直接调用切片和污点追踪工具.")
p("这些工作的共同特征是:都在探索传统程序分析(切片,依赖图,符号执行)与 LLM 的结合方式.但研究者注意到一个深层的共性缺陷:LLM 在这些方案中始终处于辅助地位------要么做后处理(分析切片结果),要么做子问题求解(Datalog 子问题),要么做工具调用者(MCP).没有一篇文章让 LLM 参与到切片的核心决策过程中.而另一条研究线索------纯 LLM 切片------如 SliceMate 和 Shahandashti 的工作------则完全抛弃了传统程序分析,但这带来了不可验证的问题.GPT-4o 的静态切片准确率仅有 60.8%,远不足以用于安全关键的故障定位.")
p("这个发现促使研究者重新思考:不是简单地让 LLM 做工具的后处理,也不是天真地让 LLM 替代传统分析,而是需要一个根本性的重新分工.LLM 擅长什么?传统分析擅长什么?答案应该是:LLM 擅长语义推理(模糊,基于上下文,不需要精确性),传统分析擅长形式完备性(确定,基于数据流,保证覆盖面).二者不是替代关系,而是互补关系.")

h("2.2  参考工具调研", 2)
p("在阅读最新论文的同时,研究者也调研了三类具有代表性的代码转 LLM 提示词工具,重点关注它们的设计模式:")
p("(1) code2prompt(GitHub 7300 颗星, Rust 实现):将整个代码库转换为 LLM 可读的提示词,核心是 Handlebars 模板系统,内置 fix-bugs,find-security-vulnerabilities 等多个分析模板.值得借鉴的是其模板方法论------用模板约束 LLM 的输出格式和分析路径.")
p("(2) GitIngest(GitHub 4000+ 颗星, Python 实现):极简 API 设计理念,一个 ingest(source) 函数返回 (summary, tree, content) 三元组.借鉴其 API 设计范式------用户不需要知道内部有多复杂,只需要一行调用.")
p("(3) IBM CLDK / CodeLLM-Devkit(ICSE 2025):程序分析和 LLM 之间的正式桥梁框架.它在架构层面定义了 program_dependency_graph 这个分析层级,并提供了 TreesitterSanitizer 用于基于调用图的粗粒度代码裁剪.但 PDG 级别的分析后端尚未实现(源代码标注为 not yet implemented),这恰好给了研究者的工具一个明确的定位------填补 CLDK 框架中 PDG 层的空白.")

h("2.3  自建工具 Chop4LLM:第一个 PDG 级切片工具", 2)
p("带着上述新认知,研究者独立开发了 Chop4LLM,一个实现基于 PDG 的双向程序切片并生成 LLM 提示词的 Python 工具.这是在所有代码转 LLM 工具链中,首次在流程中插入 PDG 级精细依赖分析的尝试.")

p("核心贡献共有四项:", True)
p("贡献一:首次在代码转 LLM 流程中插入 PDG 级切片.此前包括 code2prompt,GitIngest 在内的所有工具,本质都是全量代码转提示词------即把代码文件的内容原样或按目录结构排列后交给 LLM.它们没有对代码做任何依赖分析或过滤.Chop4LLM 是第一个在提示词生成之前,先用 PDG 分析裁剪出相关代码片段的工具.")
p("贡献二:超越粗粒度调用图裁剪,实现真正的数据依赖加控制依赖.IBM CLDK 的 TreesitterSanitizer 虽然也是裁剪工具,但它基于调用图做正向粗粒度裁剪------保留焦点方法及其被调用者.这本质上是方法级别的正向切片,缺少语句级别,变量级别的精细度.Chop4LLM 则实现了完整的到达定值分析(GEN/KILL/IN/OUT 迭代不动点算法)和后支配分析(CFG 加迭代不动点),做到了变量粒度,语句粒度的依赖关系判定.")
p("贡献三:正确实现 Jackson 和 Rollins(1994)的 Chop 算法.Chop 不是简单的前向切片与后向切片取交集.正确的算法分为两阶段:Phase 1 计算从 source 出发的前向可达节点集合 F,Phase 2 在限制到 F 的子图上计算到 sink 的后向切片.这个受限可达性计算消除了一些看似有关联但实际上不在同一条因果链上的节点.")
p("贡献四:带依赖标注的切片输出.每条被保留的切片语句都标注了依赖类型和原因(如 [D:discount] 表示数据依赖于变量 discount,[C] 表示控制依赖于某个条件分支).这些标注帮助 LLM 理解代码之间的逻辑关联,而不是仅仅面对一段不相关的代码片段.")

p("技术架构分为四个层次:", True)
p("解析层:使用 javalang 库解析 Java AST,提取语句列表,定义变量集合,使用变量集合,控制结构边界.")
p("PDG 构建层:在 AST 基础上构造控制流图(CFG),通过后支配分析(迭代不动点算法)计算控制依赖,通过到达定值分析(GEN/KILL + 迭代不动点)计算数据依赖.这一步是整个工具的理论核心------区分基于变量名匹配的假切片和基于逻辑依赖的真切片.")
p("切片层:实现 forward_slice → backward_slice → chop 三连函数.forward_slice 从 source 出发沿依赖边前向遍历;backward_slice 从 sink 出发沿依赖边后向遍历;chop 先调用 forward_slice 获取前向可达子图,再在该子图上调用 backward_slice.")
p("格式化层:Handlebars 风格的模板系统,将切片语句包装为带行号,依赖标注,上下文代码的结构化 Markdown,附上调试引导问题供 LLM 分析.")

p("初步测试结果(在自编的几个 Java 测试用例上验证):", True)
p("(1) Discount Bug 用例(8 条语句):原始 8 句 → 纯后向切片 6 句(缩减 25%)→ Chop 仅 3 句(缩减 62.5%).Chop 从 source 精准裁剪到 sink,比纯后向切片减少了三句冗余.")
p("(2) 线性 def-use 链用例(4 条语句):因为每条语句都在依赖链上,后向切片和 Chop 都保留了全部 4 句,说明工具不会为了缩减而缩减------无冗余时不误删.")
p("(3) if-else 分支用例(5 条语句):正确保留了 if 条件和两个分支内的语句,说明分支追踪(skip_next 机制)工作正常.")
p("(4) 无 bug 用例(5 条语句):全部保留,说明在正常代码中不会产生误报.")
p("验证通过的五个关键特性:(a) 控制依赖正确------if 条件指向被控语句,基于 Ferrante 1987 的后支配分析;(b) 数据依赖正确------def-use 链而非变量名匹配,基于到达定值迭代不动点;(c) KILL 机制正确------被重新赋值的变量不再追溯旧的变量定义;(d) if-else 分支正确保留------两个分支都出现在切片中;(e) Chop 比纯后向切片更精确(62.5% vs 25% 缩减率).")

h("2.4  关键转折:从 Chop4LLM 到研究方向的重构", 2)
p("Chop4LLM 的开发过程本身带来了研究方向的深刻重构.在实现 PDG 分析的过程中,研究者逐步认识到:")
p("第一,传统 PDG 分析的核心瓶颈在于入场费.要确定依赖链上的函数,需要调用图和指针分析------这两个都是全程序的,O(n³) 复杂度的计算.类型决议(如虚函数调用)必须跑全程序 Andersen 分析或 CFA 分析,不可绕过.这意味着传统方法有一个巨大的固定成本,且完全无法处理不可编译的代码.")
p("第二,LLM 恰好可以绕过这些瓶颈.LLM 不需要精确的类型分析,在语义层面直接判断依赖关系;LLM 不依赖编译和调用图构建,不可编译代码也能切;LLM 能区分语法上有关但逻辑上无关的语句(如日志打印语句);LLM 按需付费,只分析依赖链上的函数而非全程序;LLM 语言无关,同一范式切 Java 和 Python 只需换输入代码;LLM 可解释,可以要求它用自然语言解释每句话为什么被包含.")
p("但 LLM 也有明显的劣势:不 sound(可能漏依赖或多包含),不确定(相同输入可能不同输出),受 context window 限制,成本不可预测.")
p("一句话总结:传统方法用数学精确性换取工程不实用;LLM 用语义推断换取工程实用.Debug 场景天然容忍不完美------不需要 soundness,需要一条合理的因果链.")
p("这个认识直接导向了接下来三轮研究方向的迭代.")
bp()


# Chapter 3
h("第三章  三轮研究方向迭代")
p("本章记录研究方向从 Chop4LLM 到 SWP,再到 Cascaded Hybrid Slicing 的完整演化过程.每一次迭代都不是凭空产生的,而是由上一阶段暴露出的具体问题驱动的.理解这个演化过程,对于理解最终框架的设计决策至关重要.", True)

h("3.1  第一轮:Chop4LLM ------ 传统 PDG 切片 + LLM 后处理", 2)
p("原始方案的核心理念是:用传统的 PDG 程序分析工具产出切片结果(一个精确裁剪的代码子集),再把切片交给 LLM 做语义分析和 bug 定位.这是一个两阶段的流水线------先切,再分析.")
p("但在这个方案的实现过程中,研究者逐步发现了三个根本性问题:")
p("问题一:切片和分析是两个独立步骤,缺乏协同.切片工具按照依赖图的拓扑结构裁剪语句,LLM 按照语义理解分析代码.两者的判断标准完全不同------切片工具说某句话有数据依赖所以保留,LLM 说某句话虽然和数据有依赖但语义上显然不可能是 bug.它们之间没有反馈回路.切得太宽,LLM 被无关语句分散注意力;切得太窄,LLM 没有足够上下文做推理.没有在切片过程中让 LLM 给出意见的机制.")
p("问题二:PDG 构建质量制约整个流程的上限.传统 PDG 分析要达到可靠水平,需要完整的调用图,精确的指针分析(Andersen 或更高精度),全程序的类型决议(特别是虚函数调用).任何一个环节的精度损失都会传导到最终的切片结果.而且这些分析都是 O(n³) 的------对于一个中等规模项目,光是构建调用图就可能需要几分钟.这不实用.")
p("问题三:LLM 在这个方案中只是后处理工具.它拿到的是已经被 PDG 分析判定为相关的代码片段,能做的只有\"请在这些代码里找 bug\".LLM 丰富的语义理解能力------它能区分语法有关但逻辑无关的语句,能从上下文推断程序员意图,能用自然语言解释因果链------完全被浪费了.")
p("核心反思:切片不应该是一个先切完再分析的线性流程,而应该是一个边切边分析的迭代过程.需要让 LLM 参与到切片决策本身,而不是只做后处理.")

h("3.2  第二轮:SWP(Slicing Workflow Paradigm)------ LLM 作为切片引擎", 2)
p("基于第一轮的认识,研究者提出了一个大胆的修正方案:不再让传统程序分析做切片的核心工作,而是让 LLM 直接做切片.SWP(Slicing Workflow Paradigm,切片工作流范式)把切片变成 LLM 的一个结构化推理任务.")
p("SWP 设计了一个五阶段推理框架:")
p("阶段 1:角色定义(Role)------ 告诉 LLM 你现在是一个程序分析专家.")
p("阶段 2:输入说明(Input)------ 注入代码,切片准则,上下文信息.")
p("阶段 3:依赖定义文本化(Dependency Definitions)------ 把数据依赖和控制依赖的数学定义写成自然语言,作为推理规则注入 prompt.")
p("阶段 4:执行规则(Execution Rules)------ 约束推理步骤和判断标准.")
p("阶段 5:输出格式约束(Output Format)------ 要求 LLM 输出结构化的行号列表及每行的包含理由.")
p("同时,研究者从 SliceMate 的分析中学到了 6 个提高 LLM 切片质量的工程设计要点:")
p("(1) ACI 外挂工具------LLM 看不到项目全局,需要结构化注入函数签名,全局变量,继承关系等信息.")
p("(2) 依赖定义文本化------把数据依赖,控制依赖的图论定义写成自然语言,让 LLM 按规则推理而非自由发挥.")
p("(3) 双重 Verification------Conciseness(检查是否有冗余语句被误保留)和 Completeness(检查是否有必要语句被漏掉)分别进行.")
p("(4) Refinement 仅从原文补------修正时强制 LLM 只能从原始代码文件中取行,禁止编造不存在的行号.")
p("(5) 迭代上限 5 次------实验验证最优,超过 5 次收益递减.")
p("(6) 五段 Prompt 结构------Role + Input + Dependency Definitions + Execution Rules + Output Format 的固定格式.")
p("但 SWP 很快暴露了新的问题.研究者仔细阅读了 Shahandashti(2025, COMPSAC)的实证结果后意识到:即使使用 GPT-4o,纯 LLM 的静态切片准确率也仅 60.8%,动态切片准确率 59.7%.而且失败根因的类型非常基础------Complex Control Flow 是最频繁的失败类别,Variable Declarations/Assignments 的位置误判最多.即使通过 Prompt Crafting(+4%)和 Iterative Prompting(+3.9%)优化,提升也极其有限.")
p("更致命的是:SWP 与 SliceMate(多 Agent 迭代生成切片)在方法上高度重叠.SliceMate 已经用了多 Agent 架构做 LLM 切片,SWP 只是把多 Agent 换成了多阶段,把迭代换成了结构化,但本质上都是\"让 LLM 做切片\"的思路.这不是一个新的研究贡献.")
p("核心反思:不能指望 LLM 替代精确的程序分析.LLM 不是计算器,它不擅长做需要形式完备性的图遍历计算.但同时,传统程序分析虽然精确但不实用(入场费太高,不能处理不可编译代码).那能不能让 LLM 做它擅长的(语义推理),让静态分析做它擅长的(形式验证),然后通过一个精巧的架构把它们串联起来?")

h("3.3  第三轮(当前):级联混合切片 ------ 让 LLM 和静态分析各司其职", 2)
p("这是研究方向的第三个,也是当前正在推进的版本.它的核心思想可以用一句话概括:不是让一个范式解决所有问题,而是承认不同技术的优劣,通过级联架构让每个阶段用最适合它的工具.")
p("这个方案的产生有一个具体的触发点:研究者在反复对比 Zhang 2007 的 MPS(Multiple Points Slicing)和 Jackson 和 Rollins 1994 的 Chop 时,注意到了一个被长期忽视的问题.")
p("MPS 需要三个输入点------后向切片从错误输出出发,前向切片从失败诱导输入差异出发,双向切片从关键谓词出发.三个切片各自独立计算,最后取交集作为故障候选集.这听起来很合理:三个方向互相校验,取交集应该最准.但仔细想来有一个严重的理论漏洞:如果一个 bug 在某个方向上表现为输入差异,在另一个方向上表现为输出错误,但在第三个方向上根本没有切片到相关语句------那么这个交集就不包含这个 bug 的任何代码.MPS 的完备性依赖于一个未经验证的假设:bug 必须在所有三个方向上都产生影响.这个假设显然不总是成立.")
p("Chop 则不同.它不是三个独立切片的交集,而是一个顺序执行的过程------先确定从 source 出发哪些语句可能被影响(前向可达子图),再在这个受限范围内找到通向 sink 的依赖链.这是一种级联(Cascaded)的结构:第一阶段输出限定了第二阶段的范围,而非独立决策后取交集.级联是理论上更完备的做法.")
p("但 Chop 需要一个 source 点.这个 source 怎么来?传统做法是手动指定------程序员说\"我认为这里可能有问题\".这又回到了手动调试的老路.但如果能在程序执行过程中自动发现 source 呢?")
p("这又引出了另一个关键文献:Barros 等人(2010)提出了基于断言的切片------用运行时断言作为切片准则.断言通过表示这段代码在当前执行中正确,断言失败表示这里出了问题.虽然 Barros 的工作只是理论探讨(它没有给出实际工具,也没有讨论如何利用断言序列做双向切片),但它打开了一个关键思路:断言不仅仅是\"检测错误\"的工具,还是\"回溯错误源头\"的路标.")
p("于是,级联混合切片方案的核心逻辑水到渠成:")
p("Phase 1(动态后向 + 断言):从断言失败点(sink)沿执行 trace 向后扫描.每遇到一个断言点就判断:断言通过了(PASS)说明代码在这之前还是正确的,继续往回扫;断言失败了(FAIL)说明错误已经出现了.最后一个 PASS 断言点就是 source------这一切是在 LLM 的语义辅助下完成的,LLM 可以做额外的 source 候选推测,但最终由断言结果验证.这里需要的是\"语义推理\"------LLM 不需要数出精确的依赖边,只需要理解代码在做什么,判断哪里有可疑之处.")
p("Phase 2(静态前向 + 断言剪枝):从 Phase 1 找出的 source 出发,用传统的静态分析沿所有可能路径向前推进.在每个分支点,看断言的运行结果:这个分支上的断言通过了?剪枝------这条路径上的代码是正确的.断言失败了?保留------这条路径可能传播了 bug.最终到达 sink 的路径就是故障候选集.这里需要的是\"形式完备性\"------静态分析要保证覆盖了从 source 到 sink 的每一条逻辑上的可能路径.")
p("这个方案的精妙之处在于:它绕过了传统 PDG 分析的入场费.Phase 2 不需要完整的指针分析------断言的运行时结果已经告诉了哪些路径是对的,哪些是错的.不再需要 O(n³) 的 Andersen 分析来消歧虚函数调用------因为断言的 PASS/FAIL 是运行时确定的,比任何静态推断都更精确.同时对 LLM 的使用也是克制的------仅在 Phase 1 做推测,且推测结果会被断言的运行时结果验证,不会出现\"看起来对,其实引用错了\"的问题.")
p("这个方案仅需一个输入点(sink/断言失败点),而非 MPS 的三个.这是因为它不需要用三个方向的交集来互验------断言序列本身就在 trace 上提供了一串天然的路标.Failing/Passing 交叉验证的合理性已被多篇最新论文实证:LLMvsHuman(2026, arXiv: 2606.08588)证明 LLM 生成的测试用例能检测 69% 的 bug(而人工测试仅 17.2%);SpecCoder(2026, arXiv: 2607.04232)证明可以让 LLM 学习在代码内部插入可执行断言,正确性提升 55.8%.")
p("同时,研究者在 2026 年 7 月初发现了 EvoOtter(arXiv: 2607.02854),这是一个基于进化编程和 LLM 的 bug 复现测试生成工具,采用 successive halving 加 batched crossover 策略,API 成本低,效果 SOTA.它与当前框架的需求高度匹配------用来生成 failing test + passing tests,前者用于定位 bug,后者用于建立断言基线.经过与用户的讨论,确定现阶段可以直接使用 EvoOtter 完成测试用例生成这一环节.")
p("对断言质量敏感性的讨论也是在这个阶段完成的.关于\"断言密度从 L0 到 L4 变化时效果会单调退化还是非单调\"这个问题,研究者经过分析认为:效果不一定退化.需要考虑三个维度------断言插入的准确性(高密度低质量的断言反而是噪音),断言的实际语义价值(是否每条断言都覆盖了有意义的语义边界),以及成本(密度高则插入 costs 高,密度低则动态切片终止过早,静态切片展开范围过大).因此断言密度被定为 RQ4 的实验变量,不做预先假设.")

bp()

# Chapter 4
h("第四章  关键设计决策与论证")
p("本章在前面三轮迭代的基础上,整理出框架的核心设计决策,每一条都附带其推理过程和文献依据.", True)

h("4.1  核心研究问题 [CRQ]", 2)
p("给定一个 failing test 及其断言失败点(sink),级联混合切片框架能否产生一个故障候选集(Fault Candidate Set, FCS),满足三个条件:")
p("(a) 比纯动态 MPS(Zhang 2007)更小------在相同的 benchmark 上对比 slice size.")
p("(b) 理论上比纯 LLM 切片(SliceMate)更完备------级联架构有形式化完备性保证,而 LLM 推理没有.")
p("(c) 仅需单输入点(sink)------降低使用门槛和人工标注成本.")

h("4.2  五个子研究问题", 2)
p("RQ1:源点定位精度.断言引导的动态后向追踪能多准确地沿执行 trace 定位 bug 源点?度量指标为到真实 bug 起点的距离(与 MPS 后向切片比较).")
p("RQ2:路径剪枝有效性.断言引导的静态前向剪枝能在多大程度上减少 Phase 2 路径爆炸?度量指标为路径数量缩减比,误报率.核心假设:断言 PASS 的分支与无 bug 代码有强相关性.")
p("RQ3:对比有效性.级联框架与各基线的综合对比.基线包括 Zhang 2007 MPS,Tarantula 和 Ochiai(SBFL 类),SliceMate(纯 LLM 多 Agent),Cause Transitions.度量指标包括切片大小,精确率,召回率,故障定位排名.")
p("RQ4:断言质量敏感度.框架对断言密度的敏感程度,实验变量包括断言密度(L0=无断言,L1=方法边界,L2=分支点,L3=赋值点,L4=每条语句),断言正确性(通过变异操作增/删/改断言).重点分析框架性能退化曲线.")
p("RQ5:级联架构 vs 交集架构.级联执行(Phase 1 出→Phase 2 入)是否优于传统混合切片(独立计算两个方向的切片,然后取交集)?度量指标包括切片精度,召回率,理论完备性保证.")

h("4.3  与 Zhang 2007 MPS 的详细对比", 2)
p("Zhang 2007 的 MPS 在 23 个真实故障(来自 flex 和 grep)上验证,是目前故障定位领域最广泛引用的基线之一.但 MPS 有三个关键局限:")
p("第一,需要三个输入点(erroneous output,failure-inducing input difference,critical predicate),大大增加了人工标注成本.本框架只需单输入点(sink).")
p("第二,三个输入点各自产生独立切片后取交集,这个操作可能系统性漏掉只在某一方向上表现异常的 bug.本框架的级联架构是顺序约束而非取交集,理论上更完备.")
p("第三,MPS 不产生 per-statement 的解释------用户看到的只是一个行号集合.本框架的 Phase 2 输出为每条语句标注了断言证据(PASS = 剪枝原因, FAIL = 保留原因),实现了可追溯性.")

h("4.4  断言密度的非单调效应分析", 2)
p("断言密度从 L0 到 L4 变化时,效果曲线未必单调------这是一个需要实验验证的假设而非预设结论.分析如下:")
p("L0(无断言):Phase 1 只能依赖 LLM 推测 source,准确率受限(参考 Shahandashti 的 60.8%).Phase 2 无剪枝能力,等同于纯静态前向切片.")
p("L1(仅方法边界断言):断言稀疏,Phase 1 可能过早停在不准确的方法入口,Phase 2 展开范围大.")
p("L2(加分支点断言):这是最有希望的最优点------分支是执行流分叉的天然路标,断言 PASS/FAIL 直接决定剪枝方向.")
p("L3(加赋值点断言):增加的计算成本可能超过信息增益.并非每条赋值都承载有意义的语义不变量.")
p("L4(每条语句断言):综合成本过高,且冗余断言可能相互矛盾(同一位置的多个断言对运行时语义的一致性要求极高).")
p("因此,断言密度是 RQ4 的核心变量,目标是找到性价比最优区间(初步假设为 L2 附近).")

h("4.5  测试用例需求与实现方案", 2)
p("本框架对测试用例的需求为:至少 1 个 failing test(定位 bug 并产生断言失败点 sink) + 多个 passing tests(建立断言 PASS/FAIL 基线,用于 Phase 2 剪枝判定).")
p("测试用例将通过 EvoOtter(arXiv: 2607.02854, 2026)生成.EvoOtter 是当前 state-of-the-art 的 bug reproduction test(BRT)生成器,采用 successive halving 评估策略 + batched crossover 变异 + LLM 适应度评估,API 成本低.LLMvsHuman(2026)和 SpecCoder(2026)的实证结果已为 Failing/Passing 交叉验证方法提供了充分的理论支撑.")

h("4.6  实现工具选型(待定)", 2)
p("Phase 1(动态后向):LLM 驱动,可替换为不同后端(GPT-5,DeepSeek 等).选型不需要工具支持.")
p("Phase 2(静态前向):核心候选工具为 WALA(Java,IBM 维护 20+ 年,Jimple IR,完整指针分析),dg(LLVM C/C++ PDG 构建),CodeQL(GitHub,代码查询和静态分析引擎).选型需进一步调研------如果目标语言是 Java,WALA 是首选;如果目标是 C/C++,dg 更合适;如果需要在不可编译代码上工作,CodeQL 的宽松分析模式可能更好.")
p("测试用例生成:已选定 EvoOtter.")
p("断言生成:外部 LLM 方法,候选为 ASSERTIFY(语法正确率 97.4%)和 SpecCoder(可执行断言 + 55.8% 正确性提升).")

bp()

# Chapter 5
h("第五章  文献系统化调研")
p("本章记录按照 Codex 科研工作流标准执行的文献调研全流程.工作流的模板来源于一篇关于 Codex 科研工作流方法论的微信文章(mp.weixin.qq.com/s/gCoVRJNdSmZnQZJWrey9Xw),该文系统阐述了如何从空文件夹开始搭建一套可追溯,可复用,可验证的 AI 辅助科研工作流.", True)

h("5.1  Codex 科研工作流的方法论来源", 2)
p("在开始文献调研之前,研究者先学习了 Codex 科研工作流的方法论.该工作流的核心设计原则是:AI 辅助科研不应只是把论文丢给 AI 让它总结一下,而应该让每一步都有文件,有规则,有证据,有复核入口------最终产出的不是一段顺滑的文本,而是一套能追溯,能修改,能继续积累的研究资产.")
p("基于该工作流标准,本研究工作流定义了以下目标产出:一个边界清晰的研究项目文件夹(paper/),一份可持续维护的 AGENTS.md(AI 助手行为规则),一个安全的 .env.local(API Key 存放),一套可验证的文献元数据补全脚本,一张字段稳定的文献矩阵,一份证据地图,一份研究缺口报告,一个可复用的 Skill,一套质量检查规则.")
p("以下 Step 1-3 均在此框架下执行.")

h("5.2  Step 1:定义研究问题与筛选标准", 2)
p("在 paper/ 目录下创建了以下初始文件:")
p("-- AGENTS.md:项目级的 AI 助手行为规则文件,定义了研究背景,五个子研究问题,目标产出路径,文献质量约束(不编造 DOI 作者年份页码,不可验证信息标记为 unknown 或 needs_manual_check,所有外部知识需标注来源).")
p("-- notes/research_questions.md:CRQ 加五个子问题的完整定义,以及从这些 RQ 推导出的设计决策(Phase 1 动态后向 + 断言,Phase 2 静态前向 + 断言剪枝,LLM 仅用于 Phase 1 的可替换模块,断言来自外部 LLM 生成方法,单输入点架构).")
p("-- notes/inclusion_exclusion_criteria.md:七个纳入标准(程序切片,故障定位,LLM for code,断言与不变量,混合分析,基础文献,工具与基准)和五个排除标准(非代码域,无关 SE 主题,2000 年前经典(除非直接引用),已替代版本,灰色文献).")
p("-- matrix/literature_matrix.csv:初始空矩阵,定义了 citation_key,title,authors,year,venue,doi,category,method,key_findings,relevance,confidence,manual_check_needed 共 12 个字段.")

h("5.3  Step 2:文献收集与元数据补全", 2)
p("文献的初始来源是用户提供的 paper_list.docx(约 40 篇论文).这是研究者在此前数月的论文阅读过程中积累的清单.")
p("元数据补全过程通过调用 Crossref REST API 完成.具体方法是:用论文标题在 Crossref 中检索,匹配得分最高的结果,提取 DOI,年份,期刊/会议名,作者列表.38 篇论文中:")
p("-- 26 篇被成功自动匹配,DOI 和元数据由 Crossref 直接返回.")
p("-- 6 篇因 Crossref 返回了错误的匹配结果(如同一标题关键词匹配到不同论文),被标记为 needs_manual_check.")
p("-- 6 篇工具类论文(如 code2prompt,dg,giri 等开源工具)没有标准 DOI,元数据采用 GitHub 仓库信息和工具文档.")
p("在文献矩阵建立后,研究者又补充了多篇 2026 年最新发表的相关论文:")
p("-- EvoOtter(arXiv: 2607.02854, 2026.07):进化编程 + LLM 的 bug 复现测试生成,SOTA 性能.")
p("-- SpecCoder(arXiv: 2607.04232, 2026.07):训练 LLM 在代码内部插入可执行断言,要求正确执行通过,错误执行拒绝,正确性提升 55.8%.")
p("-- LLMvsHuman(arXiv: 2606.08588, 2026.06):LLM 生成测试检测 69% bug vs 人工测试 17.2%,证明 LLM 测试生成有效.")
p("-- Cunha 和 Macedo(arXiv: 2510.23350, 2025):GPT-5 从自然语言规约生成正负测试用例,检测错误 Alloy 规约.")
p("-- FMAgent(arXiv: 2604.11556, 2026):LLM + Hoare 推理的混合形式化方法.")
p("-- SLICEFORMER(ACL 2026 long paper):数据流感知预训练 + 约束解码的 seq2seq 切片.")
p("最终文献矩阵:38 篇论文,按 A-F 六个类别编码(A=故障定位基线,B=神经/LLM 切片,C=断言与测试生成,D=传统切片基础,E=混合方法框架,F=实现工具与基准).")

h("5.4  Step 3:证据地图", 2)
p("证据地图的目标是将文献矩阵中的 38 篇论文按方法学进行系统聚类,并逐篇标注证据方向(核心支持,方法论支持,对比基线,中性参考,基础性文献),对应的研究问题(RQ1-5),证据强度,以及矛盾发现.")
p("聚类结果---七个技术簇:")
p("C1 传统程序切片与 Chop(7 篇).以 Weiser 1984,Korel 和 Laski 1988,Ferrante 1987,Jackson 和 Rollins 1994 为基础,涵盖 Zhang 和 Gupta 2004 的大规模动态切片,Barros 2010 的断言引导切片,Multi-Stage ISSTA 2026 的多阶段按需切片.这些是本框架理论基础的直接来源.")
p("C2 神经/LLM 切片(4 篇).包括 SLICEFORMER 2026,SLICET5 2025,NS-Slicer 2024,ND-Slicer 2024.全部是 PDG-free 的端到端学习方法,与本框架的混合范式不同,证据方向为中性参考.")
p("C3 断言生成与测试预言(6 篇).包括 ASSERTIFY 2024(97.4% 语法正确率,但无运行时语义正确性评估------这是一个被标注为核心研究缺口的发现),TOGLL 2024(断言预言正确率 3.8 倍于 TOGA),Laurel 2024(SMT 验证的 Dafny 断言),CIll 2026(反例引导的不变量生成),PALM 2025(分支点断言插入策略),PSCSelector 2025(CodeBERT 选最优切片准则).全部为支持或核心支持.")
p("C4 LLM 测试用例生成(6 篇).包括 EvoOtter 2026(可直接为本框架生成测试用例),LLMvsHuman 2026(关键实证证据),SpecCoder 2026(核心对齐论文------可执行断言加正确性保证),Cunha 和 Macedo 2025(LLM 生成正负测试),ChatUniTest 2023(生成-验证-修复多轮框架),OracleUnderstanding 2026(LLM 预言失效分析).")
p("C5 故障定位基线(5 篇).Zhang2007 MPS 是核心对比基线,SliceMate 为本框架提供了可验证性的对照组,Shahandashti 2025 的 60.8% 实证数据直接支撑了混合方法必要性的论证.Wong 2016 的 178+ 篇故障定位综述提供了领域全景图.")
p("C6 混合分析与工具框架(6 篇).NESA 2026(神经符号 F1=0.72)是与本框架最直接相关的混合方法.CLDK 2025 的 PDG 分析层未实现恰好是本工具可填补的空白.SLICE NeurIPS 2025,codebadger 2026,code2prompt,FMAgent 2026 提供了架构和工具参考.")
p("C7 实现工具与基准(4 篇).WALA(Java PDG, Phase 2 候选),dg(LLVM C/C++ PDG),giri(LLVM 动态切片),Slicer4J(1200+ Java 切片 benchmark).")
p("产出文件---evidence_map.csv(38 条逐篇标注记录)和 evidence_map_summary.docx(摘要报告,包含标红的 17 篇需人工复核论文清单,RQ 覆盖矩阵,逐篇证据方向和矛盾分析).")

h("5.5  三大矛盾发现(直接支撑论文创新点)", 2)
p("矛盾一:LLM-Only vs 静态分析的张力.SliceMate(Chang 2025)声称多 Agent LLM 可以在无 PDG 的情况下做切片并取得有竞争力的结果.然而 Shahandashti(2025)以 100 个 Java LeetCode 题目为基准,得出 GPT-4o 静态切片准确率仅 60.8%,动态切片 59.7%.这说明纯 LLM 切片在安全关键的故障定位中不可靠.本框架的混合方案(LLM 做推测 + 静态分析做验证)恰恰弥合了这个矛盾.")
p("矛盾二:断言语法质量 vs 运行时语义质量的鸿沟.ASSERTIFY(2024)的语法正确率高达 97.4%,但论文作者从未评估过运行时语义正确性.而 SpecCoder(2026)证明,通过训练 LLM 学习可执行断言(正确执行通过,错误执行拒绝),可以实现 55.8% 的断言正确性提升.这个鸿沟意味着断言质量作为一个独立维度的研究价值极高------本框架的 RQ4(断言密度 L0-L4 敏感度)正是对准这个方向.")
p("矛盾三:MPS 完备性问题的理论依据.Zhang 2007 MPS 用三个输入点取交集------这个操作可能系统性漏掉仅在某一方向上表现的 bug.Jackson 和 Rollins(1994)的 Chop 定义从理论上支持级联架构的完备性(Phase 2 后向切片限于 Phase 1 前向可达子图,不丢失任何从 source 到 sink 的节点).但从未有人将 Chop 级别的级联架构应用于故障定位并与 MPS 做直接对比------这是本研究的核心创新空间.")

bp()



# Chapter 6
h("第六章  当前进度与待推进工作")

h("6.1  已完成", 2)
p("Step 1 --- 研究问题定义 --- 已完成.创建了 AGENTS.md,research_questions.md,inclusion_exclusion_criteria.md,literature_matrix.csv.")
p("Step 2 --- 文献收集与元数据补全 --- 已完成.通过 Crossref API 补全了 38 篇论文的元数据,添加了 2026 年最新文献,文献矩阵按 6 个类别编码.17 篇论文因 Crossref 匹配不确定或缺少标准 DOI 被标记为 needs_manual_check.")
p("Step 3 --- 证据地图 --- 已完成.完成了 7 簇聚类,逐篇证据方向标注,RQ 覆盖分析,三大矛盾发现.产出 evidence_map.csv 和 evidence_map_summary.docx(含标红的 17 篇需复核论文).")
p("Step 3 补充 --- 科研过程总结(本文档)--- 已完成.将自 2026 年初至今的研究历程,三轮方向迭代,关键设计决策,文献调研全流程整理为一份完整的 Word 文档.")

h("6.2  待推进(按工作流顺序)", 2)
p("Step 4:研究缺口报告.基于 evidence_map.csv 的 7 簇聚类 + 5 RQ 覆盖矩阵,系统分析目前未被充分研究的子领域.预期发现包括:断言密度的实验研究(RQ4)在文献中完全空白------32 篇研究论文中没有一篇将断言密度作为独立实验变量;单输入点与三输入点的精度对比(RQ5)无任何直接实证------Zhang 2007 MPS 和 Jackson 和 Rollins 1994 Chop 各自孤立存在了 20 年;Chop 变体与 LLM 的结合研究尚未出现------全部 LLM + 切片的工作(SliceMate,SLICEFORMER 等)要么纯 LLM 要么纯传统,没有级联混合方案.缺口报告的产出位置:paper/reports/research_gaps.md.")
p("Step 5:综述简报.基于文献矩阵和证据地图,生成可以直接使用的写作段落草稿.内容包括:相关工作总结(按簇组织),研究动机论证(从三大矛盾出发),方法对比表(MPS vs SliceMate vs 本框架在输入点数,理论完备性,可验证性上的维度对比),贡献声明草稿.产出位置:paper/reports/literature_review_brief.md.")
p("Step 6:质量检查.运行 qa_check.py 做最终验证,检查项包括:文献引用一致性(literature_matrix.csv 与 evidence_map.csv 的 citation_key 对应是否一一匹配),DOI 格式有效性(是否以 10. 开头且符合 Crossref 规范),RQ 覆盖完整性(每个 RQ 是否至少有 2 篇以上论文覆盖),元数据准确度(needs_manual_check 标记是否合理).产出位置:paper/scripts/qa_check.py.")
p("Step 7:Skill 沉淀.将稳定的文献整理流程(从 paper_list.docx 到 evidence_map.csv 的完整管线)写入 .codex/skills/ 目录,实现流程的自动化可复用.目的是:下一次做文献调研时,只需要更新 paper_list.docx 并运行 skill,整个工作流自动执行.")

h("6.3  技术实现待定项", 2)
p("Phase 2 静态前向分析实现工具选型.当前候选:WALA(Java PDG, IBM 维护 20+ 年,Jimple IR,完整指针分析),dg(LLVM C/C++ PDG 构建),CodeQL(代码查询与静态分析,支持宽松分析模式可处理不可编译代码).选型依赖实验目标语言(Java 推荐 WALA + Slicer4J 基准,C/C++ 推荐 dg + 自建或已有 C 项目的 bug 数据集).")
p("EvoOtter 适配方案.EvoOtter 生成的是 bug reproduction test,需要适配为框架所需的 failing test + passing tests 格式.需要确认 EvoOtter 输出的测试粒度(方法级 vs 文件级),断言格式,以及是否能批量生成多个 passing tests.")
p("断言密度实验设计.L0-L4 共 5 个密度等级需要通过 ASSERTIFY 或 SpecCoder 的断言生成方法实现.需要确定每个密度等级的断言插入规则(例如 L2=每个 if/while/for 分支入口 + 出口插断言),同一代码在不同密度下的断言一致性验证方案.")
p("Git 推送.将项目推送到 github.com/zsy0222/program-slicing.当前 .git 目录存在所有权冲突------目录所有者是 CodexSandboxOffline 用户而非当前登录的 chenm 用户,需手动解决(删除 .git 后重新 git init + 重新添加远程仓库并推送).")

bp()

# Chapter 7
h("第七章  项目文件索引与关键数据")

h("7.1  完整的目录结构", 2)
p("program_slicing/                         项目根目录")
p("  paper/                                 科研工作流主目录")
p("    AGENTS.md                            AI 助手行为规则(研究背景 + RQ + 约束)")
p("    notes/")
p("      research_questions.md              核心研究问题 CRQ + 5 个 RQ + 设计决策推导")
p("      inclusion_exclusion_criteria.md     文献筛选标准(7 纳入 + 5 排除)")
p("    matrix/")
p("      literature_matrix.csv              文献元数据矩阵(38 篇, 12 个字段)")
p("      evidence_map.csv                   证据地图(38 条逐篇标注记录)")
p("      evidence_map_summary.docx           证据地图摘要报告(标红 17 篇需复核论文)")
p("    reports/")
p("      research_process_summary.docx       本科研过程全记录文档")
p("    scripts/")
p("      gen_full_v2.py                      本文档的 Python-docx 生成脚本")
p("  .gitignore                              Git 忽略规则")
p("  README.md                               GitHub 项目介绍")
p("  program slicing.docx                    早期研究笔记(Chop4LLM + SWP, 2026-06)")
p("  program_slicing_updated.docx            研究笔记更新版")
p("  hybrid_slicing_plan.docx                级联混合切片框架完整方案(含工作流 6 步骤)")
p("  framework_desc.docx                     框架详细描述(动机,架构,设计原则,已知缺口)")
p("  workflow_overview.docx                  当前工作流概述(聚焦 Phase 1+2 的 4 步骤)")
p("  paper_list.docx                         研究者初始论文阅读清单(约 40 篇)")
p("  draw_comparison.py                      框架与基线的方法对比图绘制脚本")
p("  test_chop4llm.py                        Chop4LLM 的五项特性验证测试脚本")
p("  research_log.md                         科研过程日志(2026-05-20 至 2026-06-06)")

h("7.2  关键数据一览", 2)
p("论文总数:38 篇(分布于 7 个技术簇)")
p("核心支撑论文:5 篇(ASSERTIFY 2024,TOGLL 2024,EvoOtter 2026,LLMvsHuman 2026,SpecCoder 2026)")
p("对比基线论文:3 篇(Zhang2007 MPS,SliceMate Chang2025,Shahandashti 2025)")
p("需人工复核论文:17 篇(已在 evidence_map_summary.docx 中红色高亮标注)")
p("研究问题:1 个 CRQ + 5 个 RQ")
p("研究方向迭代:3 轮(Chop4LLM → SWP → Cascaded Hybrid Slicing)")
p("2026 年最新引用论文:5 篇(EvoOtter 07.03, SpecCoder 07.04, LLMvsHuman 06.06, CunhaMacedo 10.23, FMAgent 04.11)")
p("早期论文(1984-2024 经典):约 20 篇")
p("工具与基准论文:约 10 篇")

bp()

# Appendix A
h("附录A  七个技术簇的文献详情")

p("C1:传统程序切片与 Chop(7 篇)", True)
p("Weiser 1984 --- 程序切片的原始定义.(TSE, 10.1109/TSE.1984.5010248)")
p("Ferrante,Ottenstein,Warren 1987 --- 程序依赖图(PDG)的形式化,通过后支配分析定义控制依赖.(TOPLAS, 10.1145/24039.24041)")
p("Korel 和 Laski 1988 --- 首次动态切片.(IPL, 10.1016/0020-0190(88)90055-9)")
p("Jackson 和 Rollins 1994 --- Chopping 的原始定义,受限可达性问题,非简单交集.本框架的理论基石.(Workshop, 10.1016/S0167-6423(96)00020-6)")
p("Zhang 和 Gupta 等人 2004 --- 实用二进制动态切片,压缩 DDG 处理十亿级指令 trace.(PLDI, 10.1145/996841.996845)")
p("Barros 和 Pinto 2010 --- 基于断言的切片,断言作为切片准则:与本框架的直接方法论前驱.(Workshop, 10.1016/j.entcs.2010.08.001, needs_manual_check)")
p("Multi-Stage ISSTA 2026 --- 多线程程序的粗到细按需切片.(ISSTA, needs_manual_check)")

p("C2:神经与 LLM 切片(4 篇)", True)
p("SLICEFORMER 2026 --- 数据流感知预训练 + 约束解码,ACL 2026 长文.(10.18653/v1/2026.acl-long.1649)")
p("SLICET5 2025 --- CodeT5+ 加 Copy Mechanism,ExactMatch +27%.(arXiv: 2509.17338)")
p("NS-Slicer 2024 --- 首个神经静态切片,CodeBERT/GraphCodeBERT, F1=97.41%.(OOPSLA, 10.1145/3649814)")
p("ND-Slicer 2024 --- 预测式动态切片,无需实际执行.(FSE 2024, needs_manual_check)")

p("C3:断言生成与测试预言(6 篇)", True)
p("ASSERTIFY 2024 --- 端到端断言插入工具,语法正确率 97.4%,但无运行时语义评估.(arXiv: 2411.16927)")
p("TOGLL 2024 --- LLM 测试预言生成,正确断言预言 3.8 倍于 TOGA.(arXiv: 2405.03786)")
p("Laurel 2024 --- 生成 Dafny 代码内嵌断言,经 SMT 验证.(arXiv: 2405.16792)")
p("CIll 2026 --- 反例引导 LLM 迭代生成归纳不变量.(arXiv: 2602.23389)")
p("PALM 2025 --- AST 路径枚举,分支点断言插入策略.(Published 2025, 10.23919/date69613.2026.11539183, needs_manual_check)")
p("PSCSelector 2025 --- CodeBERT 选择最优切片准则,找 74% bug + 减 69% 切片大小.(JSEP, 10.1002/smr.70092, needs_manual_check)")

p("C4:LLM 测试用例生成(6 篇)", True)
p("EvoOtter 2026 --- 进化编程 + LLM 的 bug 复现测试,SOTA(successive halving + batched crossover).可直接为本框架生成测试用例.(arXiv: 2607.02854)")
p("LLMvsHuman 2026 --- LLM 生成测试检测 69% bug vs 人工 17.2%,覆盖度非充分代理指标.(arXiv: 2606.08588)")
p("SpecCoder 2026 --- 训练 LLM 在代码内部插入可执行断言(正确执行通过,错误执行拒绝),正确性 +55.8%.核心对齐.(arXiv: 2607.04232)")
p("Cunha 和 Macedo 2025 --- GPT-5 从自然语言规约生成正/负测试用例检测错误 Alloy 规约.(arXiv: 2510.23350)")
p("ChatUniTest 2023 --- 生成-验证-修复多轮框架.(arXiv: 2305.04764, needs_manual_check)")
p("OracleUnderstanding 2026 --- LLM 测试预言生成的失效模式分析.(arXiv: 2601.05542)")

p("C5:故障定位基线(5 篇)", True)
p("Zhang2007 MPS --- 多输入点切片,DDG 图交集,23 个真实故障(flex, grep).核心对比基线.(SPE, 10.1002/spe.795)")
p("SliceMate Chang2025 --- 多 Agent LLM 切片,无 PDG.可验证性对照.(arXiv: 2507.18957)")
p("Shahandashti 2025 --- GPT-4o 切片仅 60.8% 准确率.支撑混合方法必要性的关键实证.(COMPSAC, 2409.12369)")
p("Wong 2016 --- 178+ 篇故障定位综述,领域全景.(TSE, 10.1109/TSE.2016.2552102)")
p("Arora 2024 --- MASAI,SE AI Agent 的模块化架构.(DOI unknown, needs_manual_check)")

p("C6:混合分析与工具框架(6 篇)", True)
p("NESA 2026 --- 神经符号静态分析,Datalog + LLM, F1=0.72.与本框架最相关的混合方法.(FSE 2026, needs_manual_check)")
p("CLDK 2025 --- IBM 代码分析→LLM 桥梁,PDG 分析层 not yet implemented.(FSE 2025, 10.1145/3696630.3728555, needs_manual_check)")
p("SLICE NeurIPS 2025 --- AST → 语义知识图谱 + 后向切片检索.(NeurIPS 2025, needs_manual_check)")
p("codebadger 2026 --- Joern CPG 的 MCP 封装.(SVM 2026, needs_manual_check)")
p("code2prompt --- 代码库→LLM 提示词.(GitHub, needs_manual_check)")
p("FMAgent 2026 --- LLM + Hoare 推理混合方法.(arXiv: 2604.11556, needs_manual_check)")

p("C7:实现工具与基准(4 篇)", True)
p("WALA --- IBM Java PDG + 指针分析,Jimple IR,20+ 年维护.Phase 2 首选实现工具.")
p("dg --- LLVM C/C++ PDG 构建,学术项目.(needs_manual_check)")
p("giri --- LLVM 动态切片,学术项目.(needs_manual_check)")
p("Slicer4J --- Java 切片 benchmark,12+ 项目,约 1200 个切片样本.(needs_manual_check)")

bp()

# Appendix B
h("附录B  证据方向分布与理论支撑链")

h("证据方向分布", 2)
p("核心支持(直接验证框架设计):5 篇(ASSERTIFY,TOGLL,EvoOtter,LLMvsHuman,SpecCoder),占比 13.2%.")
p("方法论与工具支撑:12 篇,占比 31.6%.")
p("对比基线(理论或实证对比):3 篇(Zhang2007 MPS,SliceMate,Shahandashti 2025),占比 7.9%.")
p("不同范式(中性参考):7 篇,占比 18.4%.")
p("基础性文献(领域根基):7 篇,占比 18.4%.")
p("工具与基准文献:4 篇,占比 10.5%.")
p("需人工复核元数据:17 篇,占比 44.7%.")

h("从基础到本框架的完整理论支撑链", 2)
p("Weiser 1984 / Korel 和 Laski 1988 ------ 动态切片基础概念")
p("  → Ferrante 1987 ------ PDG 形式化(数据依赖 + 控制依赖的严格定义)")
p("  → Jackson 和 Rollins 1994 ------ Chop(级联架构的原始理论基础)")
p("  → Zhang2007 MPS ------ 唯一直接对比基线(三输入点局限 = 本框架改进项)")
p("  → Barros 2010 ------ 断言作为切片准则(为本框架提供了断言信号的初始理论依据)")
p("  → Shahandashti 2025 ------ LLM 切片 60.8% 准确率(为混合方法的必要性提供了实证基石)")
p("  → ASSERTIFY / TOGLL / SpecCoder / Laurel ------ 断言生成工具链(为 Phase 1+2 的断言依赖提供了实现手段)")
p("  → EvoOtter / LLMvsHuman / Cunha 和 Macedo / ChatUniTest ------ 测试用例生成(为 Failing/Passing 实验设计提供了工具支撑)")
p("  → NESA / CLDK / FMAgent ------ 混合方法架构参考(为框架的混合哲学提供了先例)")
p("  → 本框架:Cascaded Hybrid Slicing ------ 级联替代交集 + 断言替代纯依赖分析 + LLM 仅做可验证的语义推理")

bp()

# Save
outpath = "C:/Users/chenm/Desktop/program_slicing/paper/reports/research_process_summary.docx"
doc.save(outpath)
print("DONE: " + outpath)
