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
def pb(): doc.add_page_break()

# Cover
doc.add_paragraph(); doc.add_paragraph()
t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("Cascaded Hybrid Slicing\nfor Fault Localization"); r.bold = True; r.font.size = Pt(24)

t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("级联混合切片故障定位"); r.font.size = Pt(16); r.font.color.rgb = RGBColor(0x44,0x44,0x44)

t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("科研过程全记录"); r.font.size = Pt(14); r.font.color.rgb = RGBColor(0x44,0x44,0x44)

t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
t.add_run("研究起始：2026年初 | 正式搭建：2026-05-20 | 文档生成：2026-07-12")

pb()

# Chapter 1
h("第一章  研究的起点")
h("1.1  最初的方向：程序切片在调试中的应用", 2)
p("研究的起点是对程序切片这一经典技术的系统学习。研究者阅读了该领域奠基性文献：Weiser（1984）提出了程序切片的原始定义，Ferrante 等人（1987）对程序依赖图（PDG）进行了严格的形式化，Korel 和 Laski（1988）开创了动态切片方法。")
p("在理解后向切片（从错误输出回溯所有可能影响的语句）和前向切片（从输入前推影响范围）的基本概念后，研究者发现了一个核心局限：动态后向切片是依赖关系的传递闭包，无法在找到 bug 处自动停止。它可以把搜索范围从一万行缩到五百行，但不会告诉你 bug 到底在哪一句。")

h("1.2  发现 Chop", 2)
p("在探索前向加后向切片结合的过程中，研究者发现了 Jackson 和 Rollins（1994）的 Chopping 论文。Chop 的核心思想是通过引入两个锚点（source 源点和 sink 汇点）来约束追溯范围。它不是简单的前向切片与后向切片取交集，而是在 PDG 上做受限可达性计算——先限制到前向可达子图，再做后向切片。")
p("研究者意识到：Chop 的第二个锚点（source）本质上是一个人工输入。如果能用大模型（LLM）自动推测 source 候选点，Chop 就能成为一个自动化调试工具。")

h("1.3  确立方向", 2)
p("研究者做出关键决策：将双向切片（Chop）与大语言模型（LLM）结合，探索自动化调试的新范式。同时期调研了多个开源程序分析工具：WALA（Java PDG 框架）、dg（LLVM C/C++ PDG 构建）、giri（LLVM 动态切片）、Slicer4J（Java 切片 benchmark）、CodeQL（代码查询与静态分析）。")



# Chapter 2
h("第二章  基础工具探索")
p("时间：2026-05-20 至 2026-06-06", True)

h("2.1  参考工具学习", 2)
p("研究者系统调研了三类代码转LLM提示词工具：")
p("（1）code2prompt（GitHub 7300 颗星）：核心是 Handlebars 模板系统，借鉴其模板方法论。")
p("（2）GitIngest（GitHub 4000+ 颗星）：极简 API 设计，借鉴其 API 设计范式。")
p("（3）IBM CLDK / CodeLLM-Devkit（ICSE 2025）：程序分析和 LLM 之间的桥梁框架，已定义 PDG 分析层级但后端尚未实现。借鉴其架构设计。")

h("2.2  自建工具 Chop4LLM", 2)
p("研究者独立开发了 Chop4LLM，一个实现基于 PDG 的双向程序切片并生成 LLM 提示词的 Python 工具。核心贡献：")
p("贡献一：在所有已存在的代码转 LLM 工具中，首次在流程中插入 PDG 级切片。此前所有工具都是全量代码转提示词，未做依赖分析过滤。")
p("贡献二：CLDK 的 TreesitterSanitizer 基于调用图裁剪（粗粒度正向切片），Chop4LLM 实现的是真正的数据依赖加控制依赖分析。")
p("贡献三：正确实现了 Jackson 和 Rollins（1994）的 Chop 算法（受限可达性），而非简单的前向交后向。")
p("PDG 构建实现了到达定值分析（GEN/KILL 加迭代不动点算法）和控制依赖分析（CFG 加后支配分析），超越了基于变量名匹配的伪切片。")

h("2.3  关键验证结果", 2)
p("在 Discount Bug 测试用例（8 条语句）上：原始代码 8 句，纯后向切片 6 句（缩减 25%），Chop 仅 3 句（缩减 62.5%），证明 Chop 比纯后向切片精确得多。同时验证了 if-else 分支正确保留、被重新赋值的变量不再依赖旧定义（KILL 机制正确）、无 bug 用例不会误报。")

pb()

# Chapter 3
h("第三章  三轮研究方向迭代")
p("演化路径：Chop4LLM → SWP → 级联混合切片", True)

h("3.1  第一轮：Chop4LLM", 2)
p("原始方案：用 PDG 工具产出切片，再将切片交给 LLM 分析。")
p("诊断出的问题：第一，切片和 LLM 分析是两步独立操作，缺乏协同；第二，PDG 构建质量制约整个流程上限；第三，LLM 只做后处理，不参与核心推理。")
p("核心反思：切片不应该是先切完再分析，而应该是边切边分析，需要让 LLM 参与到切片决策本身。")

h("3.2  第二轮：SWP（切片工作流范式）", 2)
p("修正方案：让 LLM 直接做切片，用结构化范式（Slicing Workflow Paradigm）引导 LLM 的推理链。设计了五阶段框架：角色定义、输入说明、依赖定义文本化、执行规则、输出格式约束。借鉴了 SliceMate 的六个设计要点。")
p("诊断出的问题：SWP 与 SliceMate（多 Agent 迭代生成）存在方法重叠。更重要的是，Shahandashti（2025）的实证表明，即使 GPT-4o 直接做切片，准确率也仅 60.8%。裸调 LLM 做切片不可靠。")
p("核心反思：不能指望 LLM 替代精确的程序分析，而应该让 LLM 做它擅长的事，让静态分析做它擅长的事。")

h("3.3  第三轮（当前）：级联混合切片", 2)
p("最终方案：让 LLM 和传统分析各自发挥优势，通过级联架构（而非独立并行）串联。")
p("Phase 1（动态后向 + 断言）：LLM 沿执行 trace 从断言失败点（sink）向后追溯，扫描 trace 上的断言结果，最后一个通过的断言点即为 source。LLM 在此阶段做的是语义推理——理解代码含义、推测因果关系，不需要形式精确性。")
p("Phase 2（静态前向 + 断言剪枝）：从 source 出发，用静态分析做前向可达性计算。遇到断言通过的路径就剪枝，断言失败的路径保留。静态分析在此阶段做的是形式验证——确保不遗漏任何可能传播到 bug 的路径。")
p("核心理念：不是用一个范式解决所有问题，而是让 LLM 和静态分析各自做最擅长的事。这个框架仅需要一个输入点（sink/断言失败点），不需要像 Zhang 2007 MPS 那样输入三个点。")

pb()

# Chapter 4
h("第四章  关键设计决策")

h("4.1  核心研究问题 [CRQ]", 2)
p("给定一个 failing test 及其断言失败点（sink），级联混合切片框架能否产生一个故障候选集，满足三个条件：（a）比纯动态 MPS（Zhang 2007）更小；（b）理论上比纯 LLM 切片（SliceMate）更完备；（c）仅需单输入点？")

h("4.2  五个子问题", 2)
p("RQ1 源点定位精度：断言引导的动态后向追踪能多准确地沿执行 trace 定位 bug 源点？")
p("RQ2 路径剪枝有效性：断言引导的静态前向剪枝能在多大程度上减少 Phase 2 路径爆炸？")
p("RQ3 对比有效性：级联框架与 MPS、SliceMate、Ochiai 等基线的对比效果如何？")
p("RQ4 断言质量敏感度：框架对断言密度（L0-L4）和断言正确性有多敏感？")
p("RQ5 级联优于交集：级联架构（顺序执行）是否优于传统混合切片（独立切片取交集）？")

h("4.3  与 Zhang 2007 MPS 的关键差异", 2)
p("MPS 需要三个输入点（后向、前向、双向），结果取交集。三个独立方向的交集操作可能在某个方向上漏掉独有 bug。本框架只需单个输入点（sink），且采用级联（顺序）方式——Phase 1 输出作为 Phase 2 输入，而非独立推理后取交集。这在理论完备性上优于 MPS。")

h("4.4  断言密度的非单调效应", 2)
p("断言密度从 L0 到 L4 变化时，效果不一定单调退化。需要同时考虑三个维度：断言插入准确性（高密度低质量可能产生噪音）、断言的实际语义价值、成本（密度高插入成本大，密度低则切片展开范围变大）。因此，断言密度应作为实验变量（RQ4），而非预先假设。")

h("4.5  Source 选点与测试用例需求", 2)
p("本框架只需要一个输入点（sink/断言失败点），不需要 Zhang 2007 MPS 的三个输入点。然而，Failing/Passing 交叉验证的合理性需要至少一个 failing test（定位 bug）加多个 passing tests（建立断言基线）。LLMvsHuman（2026）和 SpecCoder（2026）的实证结果证明了这套机制的可行性。对于测试用例的生成，当前选定 EvoOtter（arXiv:2607.02854）作为工具。")

pb()

# Chapter 5
h("第五章  文献系统化调研")
p("按 Codex 科研工作流标准执行 Step 1-3", True)

h("5.1  Step 1：定义研究问题与筛选标准", 2)
p("在 paper/ 目录下建立了完整的工作流结构：")
p("AGENTS.md：项目规则文件。")
p("research_questions.md：核心研究问题 CRQ 和五个子问题 RQ1-5 以及设计决策推导。")
p("inclusion_exclusion_criteria.md：七条纳入标准、五条排除标准。")
p("literature_matrix.csv：初始矩阵模板。")

h("5.2  Step 2：文献元数据补全", 2)
p("从 paper_list.docx（约 40 篇初始文献）出发，通过 Crossref API 补全了 38 篇论文的 DOI 元数据（26 篇自动匹配，6 篇需人工复核，6 篇工具类论文无标准 DOI）。")
p("同时补充了最新文献：EvoOtter（2026.07，进化加 LLM 的 bug 复现测试）、SpecCoder（2026.07，验证引导的断言训练，正确性提升 55.8%）、LLMvsHuman（2026.06，LLM 测试检测 69% bug vs 人工 17.2%）、TOGLL、ChatUniTest 等。")
p("最终文献矩阵：38 篇论文，覆盖 7 个技术方向。")

h("5.3  Step 3：证据地图", 2)
p("对 38 篇论文进行系统聚类分析，分为 7 个技术簇，每篇标注证据方向、对应 RQ、证据强度、矛盾发现。")
p("产出：evidence_map.csv（38 条逐篇标注）+ evidence_map_summary.docx（含标红的 17 篇需人工复核论文、RQ 覆盖矩阵、三大矛盾发现）。")

p("三大矛盾发现：", True)
p("矛盾一：SliceMate 声称多 Agent LLM 不需要 PDG 也能做切片，但 Shahandashti（2025）实测 GPT-4o 切片准确率仅 60.8%。纯 LLM 切片不可靠，需混合方案。")
p("矛盾二：ASSERTIFY 断言语法正确率高达 97.4%，但对运行时语义正确性评估为零。同时 SpecCoder 证明可执行断言可以做到 55.8% 正确性提升。断言质量研究存在巨大缺口。")
p("矛盾三：Zhang 2007 MPS 三输入点取交集可能漏 bug，Jackson 和 Rollins（1994）的 Chop 级联定义从理论上更完备。但从未有人用 Chop 替代 MPS 做故障定位——这是本研究的核心创新空间。")

pb()

# Chapter 6
h("第六章  当前进度与待推进工作")

h("6.1  已完成", 2)
p("Step 1 - 研究问题定义 - 已完成")
p("Step 2 - 文献元数据补全 - 已完成")
p("Step 3 - 证据地图 - 已完成")
p("Step 3 补充 - 科研过程总结（本文档）- 已完成")

h("6.2  待推进（按工作流顺序）", 2)
p("Step 4：研究缺口报告。基于 evidence_map.csv 的 7 簇聚类和 5RQ 覆盖矩阵，分析未被充分研究的子领域。预期发现：断言密度的实验研究（RQ4）是空白、单输入点与三输入点精度对比（RQ5）无实证、Chop 变体与 LLM 的结合研究尚属空白。")
p("Step 5：综述简报。基于文献矩阵和证据地图，生成可写作的段落草稿。")
p("Step 6：质量检查。运行 qa_check.py 验证文献引用一致性、DOI 有效性。")
p("Step 7：Skill 沉淀。将稳定流程写入 skill 目录实现自动化复用。")
p("实现工具选型：确定 Phase 2 静态前向分析的实现工具（WALA Java vs dg LLVM C/C++ vs CodeQL），以及 EvoOtter 作为测试用例生成工具的适配方案。")
p("Git 推送：将项目代码推送到 github.com/zsy0222/program-slicing（.git 所有权冲突待解决）。")

pb()

# Chapter 7
h("第七章  项目文件索引")

h("7.1  目录结构", 2)
p("program_slicing/")
p("  paper/                        科研工作流主目录")
p("    AGENTS.md                   项目规则")
p("    notes/")
p("      research_questions.md     核心研究问题与子问题")
p("      inclusion_exclusion_criteria.md  文献筛选标准")
p("    matrix/")
p("      literature_matrix.csv     文献元数据矩阵（38 篇）")
p("      evidence_map.csv          证据地图（逐篇标注）")
p("      evidence_map_summary.docx  证据地图摘要报告（需复核论文已标红）")
p("    reports/")
p("      research_process_summary.docx  本科研过程总结文档")
p("    scripts/")
p("      gen_summary.py / gen_cn.py / gen_full.py  文档生成脚本")
p("  program slicing.docx           早期研究笔记（Chop4LLM + SWP）")
p("  program_slicing_updated.docx   研究笔记更新版")
p("  framework_desc.docx            框架设计描述")
p("  hybrid_slicing_plan.docx       混合切片方案")
p("  paper_list.docx                用户初始文献列表")
p("  draw_comparison.py             对比图绘制脚本")
p("  test_chop4llm.py               Chop4LLM 测试脚本")
p("  research_log.md                科研过程日志")
p("  README.md                      GitHub 项目说明")

h("7.2  关键数据", 2)
p("文献总数：38 篇，7 个技术簇")
p("核心支撑文献：5 篇（ASSERTIFY、TOGLL、EvoOtter、LLMvsHuman、SpecCoder）")
p("对比基线文献：3 篇（Zhang2007 MPS、SliceMate、Shahandashti 2025）")
p("需人工复核文献：17 篇（已在 evidence_map_summary.docx 中标红）")
p("研究问题：1 个 CRQ + 5 个 RQ")
p("研究方向迭代：3 轮（Chop4LLM → SWP → Cascaded Hybrid Slicing）")

pb()

# Appendix A
h("附录A  七个技术簇的文献分类")

p("C1：传统程序切片与 Chop（7 篇）", True)
p("Weiser1984 原始切片定义、Korel 和 Laski 1988 首次动态切片、Ferrante 1987 PDG 形式化、Jackson 和 Rollins 1994 Chop 原始论文（本框架的理论基石）、Zhang 和 Gupta 2004 二进制动态切片、Barros 2010 基于断言的切片（与本框架直接相关）、Multi-Stage ISSTA 2026 多阶段按需切片。")

p("C2：神经与 LLM 切片（4 篇）", True)
p("SLICEFORMER 2026 ACL 长文、SLICET5 2025 Copy Mechanism 将 ExactMatch 提升 27%、NS-Slicer 2024 首个神经静态切片 F1 达 97.41%、ND-Slicer 2024 预测式动态切片。全部为不同范式，证据方向中性。")

p("C3：断言生成与测试预言（6 篇）", True)
p("ASSERTIFY 2024 语法正确率 97.4% 但无运行时评估（核心缺口！）、TOGLL 2024 断言预言正确率 3.8 倍于 TOGA、Laurel 2024 SMT 验证的 Dafny 断言、CIll 2026 反例引导的不变量生成、PALM 2025 分支点断言插入、PSCSelector 2025 CodeBERT 选切片准则。全部为支持或核心支持。")

p("C4：LLM 测试用例生成（6 篇）", True)
p("EvoOtter 2026 SOTA 级 bug 复现测试（可直接为本框架生成测试用例）、LLMvsHuman 2026 LLM 测试检测 69% bug vs 人工 17.2%（关键实证证据）、SpecCoder 2026 可执行断言加正确性保证（55.8% 提升）、Cunha 和 Macedo 2025 正负测试用例生成、ChatUniTest 2023 多轮框架、OracleUnderstanding 2026 预言失效分析。")

p("C5：故障定位基线（5 篇）", True)
p("Zhang2007 MPS 核心对比基线、SliceMate 纯 LLM 多 Agent 切片（可验证性对照）、Shahandashti 2025 GPT-4o 切片准确率仅 60.8%（支撑混合方法必要性）、Wong 2016 178 篇故障定位综述、Arora 2024 MASAI 架构参考。")

p("C6：混合分析与工具框架（6 篇）", True)
p("NESA 2026 神经符号方法 F1 达 0.72（与本框架最相关的混合方法）、CLDK 2025 PDG 分析层未实现（本工具可填补）、SLICE NeurIPS 2025、codebadger 2026 Joern MCP、code2prompt 模板方法论、FMAgent 2026 LLM 加 Hoare 推理混合。")

p("C7：实现工具与基准（4 篇）", True)
p("WALA IBM Java PDG 框架（Phase 2 候选实现）、dg LLVM C/C++ PDG、giri LLVM 动态切片、Slicer4J 1200 余 Java 切片样本基准数据集。")

pb()

# Appendix B
h("附录B  证据方向分布")

p("证据方向分布：", True)
p("核心支持（直接验证框架设计）：5 篇，13.2%")
p("方法论与工具支撑：12 篇，31.6%")
p("对比基线：3 篇，7.9%")
p("不同范式（中性参考）：7 篇，18.4%")
p("基础性文献：9 篇，23.7%")
p("需人工复核元数据：17 篇，44.7%")

p("从基础到本框架的完整理论支撑链：", True)
p("Weiser 1984 / Korel 和 Laski 1988 —— 动态切片基础")
p("  → Ferrante 1987 / Jackson 和 Rollins 1994 —— PDG + Chop 理论")
p("  → Zhang 2007 MPS —— 唯一直接对比基线（三输入点局限）")
p("  → Barros 2010 —— 断言作为切片准则（直接方法论前驱）")
p("  → ASSERTIFY / TOGLL / SpecCoder / Laurel —— 断言生成工具链")
p("  → EvoOtter / LLMvsHuman / Cunha 和 Macedo —— 测试用例生成")
p("  → NESA / CLDK —— 混合分析框架参考")
p("  → 本框架：级联混合切片 —— 级联替代交集、断言替代纯依赖分析")


outpath = "C:/Users/chenm/Desktop/program_slicing/paper/reports/research_process_summary.docx"
doc.save(outpath)
print("OK")