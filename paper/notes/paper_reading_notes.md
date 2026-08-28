# 论文阅读笔记汇总

> 生成日期: 2026-07-18
> 覆盖论文数: 30+ 篇
> 分类: 经典切片 | 动态切片/故障定位 | LLM切片 | 断言/不变式 | 工具/数据集 | 抽象解释

---

## A. 经典程序切片 (Foundational Slicing)

### A1. Weiser (1984)
- **标题**: Program Slicing
- **出处**: IEEE TSE 10(4):352–357, 1984
- **贡献**: 程序切片的原始定义。静态切片作为调试辅助工具。引入切片准则 (slicing criterion) ⟨l, V⟩ 的概念。
- **算法**: 基于带标注的控制流图 (CFG) 的迭代算法，O(n²)
- **阅读状态**: ✅ 已读

### A2. Ferrante, Ottenstein & Warren (1987)
- **标题**: The Program Dependence Graph and Its Use in Optimization
- **出处**: ACM TOPLAS 9(3):319–349, 1987
- **贡献**: 引入程序依赖图 (PDG)。将数据依赖和控制依赖形式化为图的节点和有向边。控制依赖通过后支配 (post-dominance) 形式化定义。一旦 PDG 建成，切片可在线性时间完成。
- **阅读状态**: ✅ 已读

### A3. Korel & Laski (1988)
- **标题**: Dynamic Program Slicing
- **出处**: Information Processing Letters 29(3):155–163, 1988
- **贡献**: 首个动态切片概念。只关注某次具体执行中实际走过的路径，切片更小更精确。
- **阅读状态**: ✅ 已读

### A4. Horwitz, Reps & Binkley (1990)
- **标题**: Interprocedural Slicing Using Dependence Graphs
- **出处**: ACM TOPLAS 12(1):26–60, 1990
- **贡献**: 引入系统依赖图 (SDG)，解决跨过程切片问题。Summary edge 用于摘要调用点处的跨过程依赖。
- **阅读状态**: ⚠️ 了解核心思想，未精读

### A5. Jackson & Rollins (1994)
- **标题**: Chopping: A Generalization of Slicing
- **出处**: 1994
- **贡献**: 提出 Chop 概念——在 PDG 上从 source 到 sink 的所有可达路径上的节点集合。不是简单的前向∩后向交集，而是受限可达性问题：先限制到前向可达子图，再做后向切片。
- **关键洞察**: 传统 PDG 取交集方法会包含逻辑上不在同一条因果链上的节点。节点 A 在前向切片中因某条路径而在后向切片中因另一条不同路径，两者没有连接。
- **阅读状态**: ✅ 精读
- **与研究关系**: Chop4LLM 工具的核心算法基础

---

## B. 动态切片与故障定位 (Dynamic Slicing & Fault Localization)

### B1. Zhang, Gupta & Gupta (2007)
- **标题**: Locating Faulty Code by Multiple Points Slicing
- **出处**: Software: Practice and Experience 37(9):935–961, 2007
- **DOI**: 10.1002/spe.795
- **贡献**: 提出三种动态切片 (BwS 后向、FwS 前向、BiS 双向) 并取交集，得到多点多点动态切片 (MPS)。
  - BwS: 从错误输出值反向追溯 (传统方法)
  - FwS: 从最小失败触发输入差异正向传播 (需要 Delta Debugging)
  - BiS: 从关键谓词实例的双向切片（需要谓词翻转搜索）
- **开销**: DDG 构建 2-3 数量级减速 (100×–1000×)。数据：执行 2500 万条指令需 139 秒，正常执行 < 0.1 秒。DDG 内存数百 KB 到数百 MB。
- **效果**: MPS 在 15/23 个案例中 FCS < 1% LOC
- **局限**: 需要三个输入准则（获取成本高）；纯动态（受限于 trace）；结果是行号集合（无解释）；DDG 构建成本极高
- **阅读状态**: ✅ 精读
- **与研究关系**: 原方案的核心 baseline，级联架构的设计对照

### B2. Zhang & Gupta (2004–2006)
- **标题**: Cost Effective Dynamic Program Slicing (PLDI 2004) / Pruning Dynamic Slices With Confidence (PLDI 2006)
- **贡献**: x86 二进制上的实用动态切片。压缩 DDG 支持十亿指令级 trace。
- **阅读状态**: ⚠️ 通过 Zhang 2007 间接了解

### B2. Cleve & Zeller (2005)
- **标题**: Locating Causes of Program Failures (Cause Transitions)
- **出处**: ICSE 2005
- **贡献**: 通过对比通过/失败运行的逐点状态差异，找到 cause transition（状态首次出现差异的点）。Delta Debugging 隔离最小失败触发输入差异。
- **阅读状态**: ⚠️ 核心思想已理解，未精读全文

### B3. Wong, Gao, Li, Abreu & Wotawa (2016)
- **标题**: A Survey on Software Fault Localization
- **出处**: IEEE TSE 2016
- **贡献**: 故障定位领域全面综述。覆盖 178+ 篇论文。分类：基于切片、基于频谱 (SBFL)、统计方法、机器学习方法等。
- **关键数据**: SBFL 方法 (Tarantula, Ochiai) 仅给出可疑度排名，不含因果链
- **阅读状态**: ✅ 已读

### B4. Schleich & Wotawa (2025)
- **标题**: Combining Dynamic Slicing and Spectrum-Based Fault Localization
- **出处**: DX 2025 Workshop
- **贡献**: 首次实验评估动态切片 + SBFL 的组合方法。wasted effort 降低 5-15%。
- **阅读状态**: ⚠️ 通过检索了解

### B5. Soha (2023)
- **标题**: On The Efficiency Of Combination Of Program Slicing and Spectrum-Based Fault Localization
- **出处**: ICST 2023 Doctoral Symposium
- **贡献**: 系统探索切片 + SBFL 的组合空间
- **阅读状态**: ⚠️ 通过检索了解

---

## C. LLM 驱动的程序切片 (LLM-Based Slicing)

### C1. Chang et al. — SliceMate (2025.07) ★ 最直接竞品
- **标题**: SliceMate: Accurate and Scalable Static Program Slicing via LLM-Powered Agents
- **出处**: arXiv:2507.18957, 2025年7月
- **作者**: 东南大学、新加坡管理大学、阿尔伯塔大学 (Jianming Chang, Jieke Shi, David Lo 等)
- **方法**:
  - 三个专用 Agent 协作: Synthesis (生成候选切片) + Verification (检查完整性/精确性) + Refinement (最小修复)
  - 不做 PDG、不建依赖图，把切片定义为 LLM 驱动的代码生成过程
  - 四个 ACI (Agent-Computer Interface): Criterion Scope Search / Invocation Extraction / Project Function Retrieval / Module Information Extraction
  - 增量 Scope 扩展: 从 sink 出发 → LLM 推断依赖 → 发现函数调用 → 加载被调函数体 → 迭代至无新调用
  - 五段 Prompt 设计: Role + Input + Dependency Definitions + Execution Rules + Output Format
  - 双重验证: Conciseness + Completeness 分别检查
  - Refinement 仅从原始代码补漏，禁止 LLM 编造语句
- **关键结果**:
  - SliceBench: 2,200 个手工标注 Java/Python 程序 (5~8,577 行)
  - 准确率比最佳 baseline 高 +22%，F1 高 +28%
  - 大规模程序 (平均 2,106 语句) 准确率高 +63.1%
  - 成本: ~$0.15/次 (GPT-4o API)
  - 下游 bug 定位 Top-10 提升 +34%
- **局限**: 多轮 Agent 迭代成本高；Agent 内部推理黑盒；仅支持后向切片
- **阅读状态**: ✅ 精读
- **与研究关系**: 主要竞品。我们的方案差异化在：(1) 不做切片引擎；(2) LLM 阅读抽象解释的中间表示；(3) 双向增强而非 LLM 主导

### C2. Shahandashti et al. (2025)
- **标题**: Program Slicing in the Era of Large Language Models
- **出处**: IEEE COMPSAC 2025 / arXiv:2409.12369
- **作者**: York University
- **方法**: GPT-4o/GPT-3.5/Llama-2/Gemma-7B + Few-shot + CoT 直接做切片
- **关键结果**:
  - GPT-4o 最好但也只有 60.84% (静态) / 59.69% (动态)
  - Prompt Crafting +4%，Iterative Prompting +3.9%
  - 失败根因分类: Complex Control Flow 最频繁
- **结论**: **裸调 LLM 做切片不可靠，需要更强的结构化引导**
- **阅读状态**: ✅ 精读
- **与研究关系**: 关键证据——LLM 直接做切片不可靠，为我们的"LLM 不应做切片引擎"立场提供支撑

### C3. He et al. — SLICEFORMER (ACL 2026)
- **标题**: Static Program Slicing Using Language Models With Dataflow-Aware Pretraining and Constrained Decoding
- **出处**: ACL 2026 Long Paper
- **方法**: Seq2seq 切片 (CodeT5+)。数据流感知预训练 (DFG-preserving 语句排列 + DFG-aware span corruption)。约束解码 (词法+语法)。
- **结果**: Java/Python benchmark 上 ExactMatch 提升最高 22%
- **阅读状态**: ⚠️ 通过 paper_list.docx 了解

### C4. He et al. — SLICET5 (2025.09)
- **标题**: Static Program Slicing using Language Models with Copy Mechanism and Constrained Decoding
- **出处**: arXiv:2509.17338, 2025年9月
- **方法**: CodeT5+ 配合 Copy Mechanism + 约束解码 (词法 + TSED 单调性)
- **结果**: ExactMatch 比 SOTA 高 27%，可处理不可编译代码
- **阅读状态**: ⚠️ 通过 paper_list.docx 了解

### C5. Yadavally et al. — NS-Slicer (OOPSLA 2024)
- **标题**: A Learning-Based Approach to Static Program Slicing
- **出处**: OOPSLA 2024 (SPLASH) / Proc. ACM Program. Lang. 8(OOPSLA1):83–109
- **方法**: 首个神经静态切片。CodeBERT/GraphCodeBERT 做语句级分类。
- **结果**: F1=97.41% (后向), 95.82% (前向)。85.2% Exact Match with oracle。可处理不完整代码。
- **阅读状态**: ⚠️ 通过检索了解

### C6. Yadavally et al. — ND-Slicer (FSE 2024)
- **标题**: Predictive Program Slicing via Execution Knowledge-Guided Dynamic Dependence Learning
- **出处**: FSE 2024
- **方法**: 预测性动态切片，不实际执行。学习执行感知依赖。
- **结果**: 81.31% Exact Match，故障定位 63.88%
- **阅读状态**: ⚠️ 通过检索了解

---

## D. 断言、不变式与规约 (Assertion / Invariant / Specification)

### D1. Barros, da Cruz, Henriques & Pinto (2010)
- **标题**: Assertion-based Slicing and Slice Graphs
- **出处**: 2010 (2026 扩展版)
- **方法**: 基于公理语义的切片。使用前置条件前向传播和后置条件后向传播的组合。引入 Slice Graph (带语义标签的 CFG 扩展)。
- **贡献**: 比已有规约驱动切片算法更精确的语句可删除性测试
- **阅读状态**: ✅ 已读
- **与研究关系**: 断言作为切片准则的先驱工作，当前研究方向的前身之一

### D2. Jalili Torkamani et al. — ASSERTIFY (2024)
- **标题**: ASSERTIFY: End-to-End Production Assertion Insertion into Java Source Code
- **出处**: arXiv:2411.16927, 2024年11月
- **方法**: LLM 驱动的 Java 源代码断言自动插入。数据集: 2,810 个方法来自 22 个仓库。
- **结果**: SNE 97.4%, SME 83.5% (GPT-4o)。但**不评估运行时断言的正确性**。
- **阅读状态**: ✅ 已读
- **与研究关系**: 原方案 Phase 0 的断言生成工具。当前方案已舍弃断言依赖。

### D3. TOGLL (2024.05)
- **标题**: LLM-Based Test Oracle Generation
- **出处**: arXiv:2405.03786, 2024年5月
- **贡献**: LLM 生成测试 oracle，比 TOGA 等神经方法更精确
- **阅读状态**: ⚠️ 通过 paper_list.docx 了解

### D4. Bodicoat et al. (2026.01)
- **标题**: Understanding LLM-driven Test Oracle Generation
- **出处**: arXiv:2601.05542, 2026年1月
- **贡献**: 研究 LLM 生成测试 oracle 的失败模式。语义理解是关键缺口。
- **阅读状态**: ⚠️ 有 PDF，未精读

### D5. Laurel (2024.05)
- **标题**: LLM-Generated Inline Proof Assertions for Dafny Verification
- **出处**: arXiv:2405.16792, 2024年5月
- **方法**: LLM 为 Dafny 验证生成内联证明断言。Intermediate assert hints for SMT solver。
- **与研究方向**: 最接近"断言链引导分析"概念的工作
- **阅读状态**: ⚠️ 通过 paper_list.docx 了解

---

## E. 抽象解释与语义故障定位 (Abstract Interpretation & Semantic FL)

### E1. Dimovski — SAS 2023
- **标题**: Error Invariants for Fault Localization via Abstract Interpretation
- **出处**: SAS 2023, LNCS 14284, pp.190–211
- **DOI**: 10.1007/978-3-031-44245-2_10
- **贡献**: 首次提出基于抽象解释的 Error Invariant 概念。迭代后向-前向静态分析精化。BDD 域解决分支合并精度损失。
- **阅读状态**: ✅ 通过 2024 期刊版了解

### E2. Dimovski — COLA 2024 ★ 当前方案核心依赖
- **标题**: Fault Localization by Abstract Interpretation and its Applications
- **出处**: Journal of Computer Languages, Vol.80, Article 101288, 2024
- **DOI**: 10.1016/j.cola.2024.101288
- **贡献**:
  - Error Invariant: 对程序位置上所有可能导向断言失败状态集合的过近似
  - 语句级语义切片 (Statement-wise Semantic Slicing): 相邻位置 Error Invariant 相同 → 语句无关 → 删除
  - 迭代后向-前向精化: 后向分析收集谓词 → 前向分析精化 invariant → BDD 域分割 → 循环收敛
  - 工具实现: APRON + BDDAPRON + Z3, 面向 C 程序
  - 集成突变修复 (AllRepair)
- **抽象域**: Intervals, Octagons, Polyhedra, BDD(base, ℙ)
- **与传统切片对比**: 在 Related Work 明确分类为程序切片的特化——从通用的 ⟨l,V⟩ 准则特化为断言失败点
- **关键局限**:
  - 抽象域 JOIN 导致过近似假阳性
  - BDD 只能从已有分支条件被动收集谓词
  - 非线性运算、数组索引、指针别名仍损失精度
  - Polyhedra 域在高维时最坏指数复杂度
- **阅读状态**: ✅ 精读全文
- **与研究关系**: 当前方案的基础设施。我们不做切片引擎，改为 LLM 阅读其 Error Invariant 轨迹。

### E3. Dimovski — SLE 2025
- **标题**: Variability Fault Localization by Abstract Interpretation and its Application to SPL Repair
- **出处**: ACM SIGPLAN SLE 2025, pp.175–188
- **DOI**: 10.1145/3732771.3742722
- **贡献**: 将 Error Invariant 方法扩展到软件产品线 (SPL)。Lifted Error Invariant 处理 #ifdef 变体。SPL 专用突变修复。
- **阅读状态**: ✅ 已下载 PDF
- **与研究关系**: 证明了 Error Invariant 方法有扩展性，但对我们单程序场景不直接相关

### E4. Dimovski — Earlier Work
- **相关**: Decision-tree abstract domains, Quantitative program sketching
- **阅读状态**: 未读

---

## F. LLM+代码工具与其他 (LLM+Code Tools & Others)

### F1. Arora et al. — MASAI (2024)
- **标题**: MASAI: Modular Architecture for Software-Engineering AI Agents
- **出处**: 2024
- **贡献**: 多 Agent LLM 架构处理复杂软件工程任务
- **阅读状态**: ⚠️ 有 PDF，未精读

### F2. NESA (FSE 2026)
- **标题**: Neuro-Symbolic Static Analysis
- **出处**: FSE 2026 Research Papers
- **方法**: 神经符号静态分析。受限 Datalog 拆解分析任务 → LLM 逐个解决子问题。
- **结果**: F1=0.72 (切片+漏洞检测)
- **阅读状态**: ⚠️ 通过检索了解

### F4. Ahmed et al. — EvoOtter (2026)
- **标题**: EvoOtter: Evolutionary Reproduction Test Generator
- **出处**: 2026
- **阅读状态**: 有 PDF，未精读

---

## G. 综述 (Surveys & Retrospectives)

### G1. Gallagher & Kozaitis (2025)
- **标题**: Program Slicing: A Brief Retrospective
- **出处**: IEEE TSE 51(3):720–724, March 2025
- **贡献**: 程序切片 45 年发展简史。从 Weiser 1979 到量子切片 2024。覆盖 35 篇参考文献。
- **阅读状态**: ✅ 精读

### G2. Tip (1995)
- **标题**: A Survey of Program Slicing Techniques
- **出处**: Journal of Programming Languages 3(3):121–189, 1995
- **贡献**: 早期程序切片领域最全面的综述 (68页, 108篇参考文献)
- **阅读状态**: ⚠️ 通过 Gallagher 2025 间接了解

---

## H. 工具与数据集 (Tools & Benchmarks)

### H1. WALA (IBM)
- **类型**: Java 程序分析框架
- **功能**: PDG 构建、指针分析、切片
- **特点**: 20+ 年历史，Jimple IR
- **状态**: 已了解，考虑作为 Phase 2 静态分析后端

### H2. Slicer4J
- **类型**: Java 切片基准数据集
- **规模**: 12+ 个项目，~1,200 个切片样本
- **覆盖**: 后向和前向切片，代码长度 10-200 行
- **状态**: 已了解，考虑作为评估数据集

### H3. Defects4J
- **类型**: Java 缺陷基准数据集
- **用途**: 故障定位评估的黄金标准
- **状态**: 已了解，原方案实验设计中的主要评估数据集

### H4. SliceBench (来自 SliceMate)
- **类型**: LLM 切片评估基准
- **规模**: 2,200 个手工标注 Java/Python 程序 (5~8,577 行)
- **状态**: 已了解，考虑作为评估数据集

### H5. 自研工具
- **Chop4LLM**: Python 实现的 PDG 双向切片 + LLM 提示词生成工具
  - 技术栈: javalang (AST) → CFG → 后支配分析 → 到达定值迭代 → PDG → Chop
  - 验证结果: Discount Bug 62.5% 缩减率 (8→3 语句)
  - 状态: 已完成原型，不再作为主要方向
- **SWP (Slicing Workflow Paradigm)**: LLM 作为切片引擎的结构化推理范式
  - 状态: 设计阶段，方向已转变

---

## I. 矩阵补齐条目（当前仅完成元数据/摘要级核验）

以下条目已经进入文献矩阵和证据地图，但尚未完成与 A-H 部分同等深度的全文精读，不能视为已完成的逐篇阅读记录。

### I1. AssertMsg2026
- **标题**: Assertion Messages with LLMs
- **出处**: arXiv:2509.19673
- **研究关联**: 与 RQ1 的断言语义表达和错误信息可解释性相关。
- **阅读状态**: ⚠️ 仅完成矩阵级摘要核验，待补作者、实验设置和正式结论。

### I2. Dimovski2023
- **标题**: Error Invariants for Fault Localization via Abstract Interpretation
- **出处**: SAS 2023, LNCS 14284, 190–211
- **DOI**: 10.1007/978-3-031-44245-2_10
- **研究关联**: 当前 Error Invariant 方案的前置工作。
- **阅读状态**: ⚠️ 已完成书目信息核验，需补充与 COLA 2024 版本的差异分析。

### I3. Dimovski2024
- **标题**: Fault Localization by Abstract Interpretation and its Applications
- **出处**: Journal of Computer Languages 80:101288
- **DOI**: 10.1016/j.cola.2024.101288
- **研究关联**: 当前静态分析基础设施和主要方法来源。
- **阅读状态**: ✅ 已有中文翻译和手工轨迹分析；仍需建立原文关键定义、算法步骤和实验结果的逐节索引。

### I4. Dimovski2025
- **标题**: Variability Fault Localization by Abstract Interpretation and its Application to SPL Repair
- **出处**: ACM SIGPLAN SLE 2025, 175–188
- **DOI**: 10.1145/3732771.3742722
- **研究关联**: 支持 Error Invariant 方法可扩展性的证据。
- **阅读状态**: ⚠️ 已完成摘要级核验，待补全文方法、实验和局限。

### I5. Gallagher & Kozaitis 2025
- **标题**: Program Slicing: A Brief Retrospective
- **出处**: IEEE TSE 51(3):720–724
- **DOI**: 10.1109/TSE.2025.3538279
- **研究关联**: 用于补充程序切片历史脉络，不作为当前方法有效性的直接证据。
- **阅读状态**: ✅ 已有综述性记录，已统一 citation key 和证据地图映射。

### I6. GitIngest
- **标题**: GitIngest: Codebase-to-Prompt API
- **出处**: GitHub 工具项目
- **研究关联**: 仅作为代码库转提示词的工程参考，不属于同行评审证据。
- **阅读状态**: ⚠️ 工具级记录，正式论文中应降级为实现参考。

### I7. codebadger2026
- **标题**: Bridging Code Property Graphs and Language Models for Program Analysis
- **作者**: Ahmed Lekssays
- **出处**: arXiv:2603.24837；Software Vulnerability Management Workshop at ICSE 2026
- **研究关联**: 通过 MCP 将 Joern 的程序切片、污点跟踪和数据流分析暴露给 LLM；可作为工程实现备选，不是当前 Error Invariant 假设的直接实证。
- **阅读状态**: ⚠️ 已完成书目信息和摘要级核验，未精读全文。
