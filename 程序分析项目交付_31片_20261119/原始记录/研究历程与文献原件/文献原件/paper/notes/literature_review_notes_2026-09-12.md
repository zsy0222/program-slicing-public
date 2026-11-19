# 当前文献综述核验与阅读记录

日期：2026-09-12。配套正文：[文献综述](../reports/literature_review_2026-09-12.md)。

## 本轮范围

正文选用 25 项核心文献，向已有矩阵新增 15 项；它们不是 25 篇均已逐页精读的声明。本轮以作者稿、出版社、作者机构和会议官方记录核对可用于正文的事实；以下逐项记录阅读深度。检索围绕切片辅助修复、形式化状态证据、上下文比较和理解评价进行，使用标题追溯和相关文献回溯，不声称系统检索无遗漏。

重要新先例是 CausalRepair。它要求收缩本项目对流程组合的创新主张，但本轮只更新文献，不实施新的实验方案。源码、模型回答和实验结果均未改动。

## 历史材料更正

| 旧说法 | 当前处理 |
| --- | --- |
| Error Invariant 由 Dimovski 2023 首次提出 | 纳入 Ermis2012，区分错误轨迹方法与程序级抽象解释 |
| 原论文只定位 没有修复应用 | 2024 版包含 AllRepair 应用；其中没有 LLM |
| Slicer4J 是数据集 | 更正为 Java 动态切片工具，Defects4J 才是本路线的缺陷基准 |
| 静态局部方法就是静态切片 | 区分结构窗口与依赖分析 |
| 原论文 Map BDD 切片是三个完全独立变量 | 记录其表示和派生关系，避免重复注入相同信息 |
| 给公式换成自然语言就是新的语义信息 | 信息等价转换与增加根因建议分开 |
| 动态切片加 LLM 属于空白方向 | 增补 KATANA 和 CausalRepair 等直接相关工作 |
| 切片越小或上下文越多必然越好 | 纳入 FLContext2026 的条件性结果 |
| 混合图遍历必然不同于前后可达交集 | 删除不成立的一般图论理由，单独说明上下文敏感和路径可行性 |
| KorelLaski1988 DOI 为 90055-9 | 出版社索引对应 90054-3 |
| JacksonRollins1994 使用 1996 年 DOI | 题名改为作者机构可核对的 FSE 1994 文献；DOI 留为 unknown 而非猜测 |

8 月更正单中已有的 WALA SSA 与 Soot Jimple 区别继续有效。此处不把未重验的旧“精读”标签、性能数字或 Phase/RQ 关系当作当前结论。旧报告保留，只添加了当前入口和失效提示。

## 来源与使用边界

### Weiser1984

核验深度：摘要与书目信息。来源：[原始或官方记录](https://faculty.cc.gatech.edu/~harrold/6340/cs6340_fall2009/Readings/Weiser.Slicing.TSE.pdf)。

用于静态切片定义；未复核历史笔记中的统一复杂度 O(n²)，正文不沿用该数值。

### Ferrante1987

核验深度：作者机构摘要与推荐引文。来源：[原始或官方记录](https://digitalcommons.mtu.edu/michigantech-p/12533/)。

用于区分数据依赖、控制依赖及状态谓词；不把图遍历成本写成整个分析工具的总成本。

### KorelLaski1988

核验深度：出版社索引摘要。来源：[原始或官方记录](https://www.sciencedirect.com/science/article/pii/0020019088900543)。

更正 DOI 为 90054-3；出版社页面直接打开受限，未标为本次全文精读。

### JacksonRollins1994

核验深度：作者机构摘要。来源：[原始或官方记录](https://www.cs.cmu.edu/~Compose/paper_abstracts/dnj/fse94.html)。

保留旧 citation key，但更正到可核对的 FSE 1994 题名。删除不匹配的旧 DOI；不凭普通图上的两条路径不同否定前后可达交集。

### Slicer4J

核验深度：论文索引摘要与官方工具说明。来源：[原始或官方记录](https://github.com/resess/Slicer4J)；[补充来源 1](https://people.ece.ubc.ca/mjulia/publications/Slicer4J_2021.pdf)。

用于确定工具性质与分析流程。直接 PDF 获取失败；未重新核对原论文的性能评测，正文不引用相关数字。

### Dimovski2023

核验深度：作者全文的摘要及相关工作。来源：[原始或官方记录](https://aleksdimovski.github.io/files/dimovski_sas23a.pdf)。

用于厘清分析对象及与 Ermis2012 的传承；不声称 2023 首创 Error Invariant。

### Dimovski2024

核验深度：作者全文的定义 算法与示例相关段落。来源：[原始或官方记录](https://aleksdimovski.github.io/files/dimovski-cola24.pdf)。

定位：第 2 节示例、Error Invariant Map 定义、Slice 过程、AllRepair 应用。Map、分区、切片不预设互相独立；抽象轮次不当作实际执行轨迹。

### CLDK2025

核验深度：预印本摘要与 IBM 官方说明。来源：[原始或官方记录](https://arxiv.org/abs/2410.13007)；[补充来源 1](https://research.ibm.com/blog/cldk-codellm-devkit)；[补充来源 2](https://www.rangeetpan.com/rangeet-CV-2026.pdf)。

正文仅使用分析上下文接入这一功能论据。FSE 版与早期 arXiv 版作者顺序不同，不混用；未以框架介绍代替本项目实证。

### Chang2025

核验深度：arXiv v1 摘要与版本记录。来源：[原始或官方记录](https://arxiv.org/abs/2507.18957)。

定位为 LLM 生成切片的工作；历史笔记的各项提升数字本次未重验，不进入新正文。

### Shahandashti2025

核验深度：arXiv v1 摘要与 COMPSAC 官方日程。来源：[原始或官方记录](https://arxiv.org/abs/2409.12369)；[补充来源 1](https://ieeecompsac.computer.org/2025/preliminary-program/)。

2024 预印本和 2025 会议论文按同一研究维护；正文不把切片预测准确率解释成修复准确率。

### Cousot1977

核验深度：作者摘要与书目。来源：[原始或官方记录](https://cs.nyu.edu/~pcousot/COUSOTpapers/POPL77.shtml)。

作者网页不同位置对会议届数存在不一致，引用使用 POPL 1977，不写未经确认的届数；DOI 留为 unknown。

### Ermis2012

核验深度：作者全文的摘要 引言与定义段。来源：[原始或官方记录](https://cs.nyu.edu/wies/publ/error_invariants.pdf)。

记录较早的 Error Invariant 来源；与后来对程序整体进行抽象分析的对象区别见综述第 3 节。

### Katana2023

核验深度：作者稿第 3 节及训练与推理段。来源：[原始或官方记录](https://nashid.github.io/resources/papers/katana-tosem23.pdf)；[补充来源 1](https://github.com/saltlab/Katana)；[补充来源 2](https://orcid.org/0000-0002-3816-4882)。

作者稿保留出版前占位字段；2023 出版身份由官方仓库确认，DOI 由作者 ORCID 记录交叉核对。训练成对版本与无答案推理必须分开。

### ReduceBeforeRepair2025

核验深度：会议官方摘要。来源：[原始或官方记录](https://conf.researchr.org/details/saner-2025/saner-2025-short-papers-and-posters-track/5/Reduce-before-you-repair-advantages-of-combining-program-slicing-with-automated-pro)。

未精读全文，只纳入 ORBS 与 APR 结合的方向性论据；不引用未核对的实验量值，DOI 保留 unknown。

### ChatRepair2024

核验深度：会议官方摘要与作者稿反馈段。来源：[原始或官方记录](https://lingming.cs.illinois.edu/publications/issta2024.pdf)。

采用 ISSTA 2024 正式题名，不与另篇 Conversational Automated Program Repair 混成一个书目条目；正文不搬用标题数字与本项目比较。

### ContrastRepair2025

核验深度：正式版机构记录与摘要 早期方法段。来源：[原始或官方记录](https://research.monash.edu/en/publications/contrastrepair-enhancing-conversation-based-automated-program-rep/)；[补充来源 1](https://researchmgt.monash.edu/ws/portalfiles/portal/758295374/736875182-oa.pdf)。

以 Monash 正式记录的 2025 年作者顺序和 DOI 为准。另查看了 arXiv 早期第 3 节；不同版本作者列表和结果不能混引。

### AutoCodeRover2024

核验深度：作者摘要与官方仓库 Overview Highlights。来源：[原始或官方记录](https://arxiv.org/abs/2404.05427)。

用于分析引导检索与修复的先例；不把 AST 检索等同于动态依赖切片，也不引用不断更新的仓库榜单分数。

### Agentless2025

核验深度：正式版作者稿首页与摘要。来源：[原始或官方记录](https://lingming.cs.illinois.edu/publications/fse2025.pdf)。

采用 PACMSE 2025 正式题名和 DOI；2024 arXiv 题名带 Agentless 前缀，是版本关系而非两个独立实验。

### ASAP2024

核验深度：作者 v3 的摘要 引言与贡献段。来源：[原始或官方记录](https://arxiv.org/html/2304.06815v3)。

用于自动语义提示增强的先例；代码摘要效果不能直接证明 Error Invariant 对修复有用。

### FLContext2026

核验深度：作者 v1 第 1 3 7.3 8 9 节。来源：[原始或官方记录](https://arxiv.org/html/2604.05481v1)。

核对理想定位、任务范围及测试通过评价的限制；不是所有动态切片方法的否定性结论。

### CausalRepair2026

核验深度：作者 v1 第 3 4.5 5.1 5.3 6.2 节。来源：[原始或官方记录](https://arxiv.org/html/2608.10613v1)；[补充来源 1](https://conf.researchr.org/details/issta-2026/issta-2026-research-papers/134/CausalRepair-Bridging-the-Causality-Gap-in-Large-Language-Model-based-Automated-Prog)。

会议身份另由 ISSTA 官网确认。比较前须对齐定位权限、候选预算、切片失败回退和正确性评价；本轮没有运行其实现。

### CRUXEval2024

核验深度：作者摘要与官方基准说明。来源：[原始或官方记录](https://arxiv.org/abs/2401.03065)；[补充来源 1](https://github.com/facebookresearch/cruxeval)。

仅借鉴有客观答案的执行型理解任务；不把短 Python 样本上的性能外推到大型 Java 修复。

### Defects4J2014

核验深度：论文索引摘要与官方框架说明。来源：[原始或官方记录](https://github.com/rjust/defects4j)；[补充来源 1](https://people.cs.umass.edu/~rjust/publ/defects4j_issta_2014.pdf)。

用于触发测试和版本关系定义。没有把 2014 初版规模当成当前完整数据库规模；本轮未运行测试。

### SWEbench2024

核验深度：ICLR 官方摘要与书目。来源：[原始或官方记录](https://proceedings.iclr.cc/paper_files/paper/2024/hash/edac78c3e300629acfe6cbe9ca88fb84-Abstract-Conference.html)。

用于仓库级任务定义；原始 SWE-bench 与 Verified 等子集不得混用规模和成功率。

### Smith2015

核验深度：正式作者稿摘要与独立测试段。来源：[原始或官方记录](https://www.cs.cmu.edu/~clegoues/docs/smith15fse.pdf)。

采用正式 FSE 版本，不使用标题带 A Large-Scale Analysis 的早期稿中不同规模数字；正文只引用过拟合与独立评价原则。


## 尚未完成但不妨碍当前正文的事项

本轮没有复现外部论文的代码或性能，没有穷尽矩阵中所有外围文献的全文。ReduceBeforeRepair2025 等摘要级条目不支撑细粒度算法或数值结论。部分 DOI 页面存在访问限制，已保留作者或机构替代来源；unknown 表示此字段尚未核对，不表示文献不合格。

纯动态组、信息等价转换、理解题评分等项目功能仍须按冻结协议实现和验证。本轮综述中对这些内容的表述均是研究设计或方法推论，不是已经完成的实验证明。
