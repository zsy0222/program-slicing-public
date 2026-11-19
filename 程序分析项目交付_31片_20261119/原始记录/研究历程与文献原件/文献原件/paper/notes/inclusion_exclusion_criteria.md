# Literature Screening Criteria

## 当前综述的筛选规则 2026 年 9 月 12 日

当前研究范围为程序分析证据辅助 LLM 故障理解与修复。以下新规则用于当前综述；后面的英文部分保留为早期级联方案记录，不再作为当前筛选口径。

优先纳入：切片与抽象解释基础；切片作为修复上下文的直接研究；形式化或自动语义证据接入模型；上下文范围与反馈的受控比较；可执行的代码理解评价；真实缺陷基准与补丁过拟合研究。

预印本可以纳入，但明确版本、发表状态及核验深度。作者、会议或出版社的正式记录优先用于书目信息；方法和数值需要对应原文，不能用搜索摘要或他人综述代替细粒度依据。工具 README 只支持实现说明，不直接支持科学效果。

同一工作的预印本、会议版和期刊扩展版按版本关系维护；有独立方法变化时分别说明，不简单删除旧版，也不重复计算同一实验。经典论文按理论必要性纳入，不以年代机械排除。

排除出本次正文而非删除本地文件：与代码故障无关的 slicing、把神经网络自身作为修复对象的模型修补工作、无法确认的题名、与当前问题无关的外围论文。旧断言生成路线的文献保留在矩阵，但不强行映射成当前方案的核心证据。

本轮采用定向叙述性综述，选用 25 项核心文献并新增 15 项矩阵条目。这个数字是当前正文的覆盖范围，不是按完整数据库检索得到的 PRISMA 纳入数量；不补造历史初筛和全文筛选计数。检索关键词包括 program slicing + program repair、dynamic slicing + LLM、error invariants、fault localization context、semantic augmentation 和 code understanding evaluation，并回溯关键论文引用。

## 历史规则与未完成的旧筛选日志

## Research Domain

Cascaded hybrid slicing for fault localization: combining dynamic backward tracing,
static forward path validation, and runtime assertion guidance.

## Inclusion Criteria

1. **Program slicing** — Static, dynamic, hybrid, or LLM-based slicing methods
2. **Fault localization** — Slice-based fault localization, SBFL, delta debugging,
   cause transitions, or similar techniques
3. **LLM for code** — LLM-based assertion generation, program analysis, or code
   understanding (ASSERTIFY, TOGLL, Laurel, PALM, etc.)
4. **Assertion/invariant** — Assertion generation, dynamic invariant detection,
   or constraint-based debugging
5. **Hybrid analysis** — Any work combining dynamic + static program analysis
   for debugging or slicing
6. **Foundational** — Seminal papers in slicing, PDG, or fault localization
   (Weiser, Korel & Laski, Ferrante et al., etc.)
7. **Tools & benchmarks** — Program analysis frameworks (WALA, Slicer4J, dg, giri)
   relevant to implementation

## Exclusion Criteria

1. **Non-code domains** — Papers on slicing for non-software artifacts
   (natural language, databases, hardware, networks)
2. **Unrelated SE topics** — SE topics not involving program slicing, debugging,
   or fault localization
3. **Pre-2000 classics** — Only include if directly referenced by the above core
   papers or essential for foundational understanding
4. **Duplicate / superseded** — Superseded versions of the same work
   (prefer journal over conference, newer over older)
5. **Gray literature** — Blog posts, tutorials, or non-peer-reviewed technical
   reports (unless directly relevant to implementation)

## Screening Log

| Stage | Count | Date |
|-------|-------|------|
| Initial collection (paper_list.docx) | ~40 papers | 2026-07-08 |
| Title/Abstract screen | | |
| Full text review | | |
| Final included | | |
