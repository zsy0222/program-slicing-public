# 文献与工具来源一次性审计

审计日期：2026-08-09  
适用范围：`paper/matrix/literature_matrix.csv`、`paper/matrix/evidence_map.csv` 与现有阅读笔记。

## 结论

本轮已完成矩阵内全部条目的书目与来源性质核查，并统一了文献矩阵和证据地图的 citation key。当前矩阵包含三类材料：

1. **学术论文/预印本**：可用于背景、方法比较或实证论证，但预印本应在正式写作中标注其同行评审状态。
2. **同行评审论文**：可作为正式相关工作和可复现结果的优先引用来源。
3. **工程工具/软件项目**：只可说明实现选择或工程可行性，不能作为 Error Invariant、故障定位或 LLM 有效性的实证证据。

本轮没有保留“需要人工补 DOI、作者或题名”的学术条目。对无 DOI 的工程工具，统一使用 `not_applicable`；这不是缺失信息。

## 重要修正

- 原 `ZhangGupta2004` 的 DOI `10.1145/996841.996845` 实际属于 *KISS: Keep it Simple and Sequential*，与程序切片无关，已移除。
- 动态切片脉络被拆为两篇独立论文：
  - Zhang & Gupta (PLDI 2004), *Cost Effective Dynamic Program Slicing*, DOI `10.1145/996841.996855`；
  - Zhang, N. Gupta & R. Gupta (PLDI 2006), *Pruning Dynamic Slices With Confidence*, DOI `10.1145/1133255.1134002`。
- `Slicer4J` 已更正为 ESEC/FSE 2021 的 Java 动态切片工具论文，而不是“Java 切片基准数据集”。
- `WALA` 已更正为使用自身 SSA IR 的多语言静态分析框架；此前的 “Jimple IR” 描述错误，Jimple 属于 Soot 生态。
- `dg` 已关联到 Chalupa 的 ATVA 2020 论文；`giri` 标为历史 LLVM 切片基础设施，不再作为当前可复现实验基准。
- `TOGLL`、`ChatUniTest`、`CIll`、`AssertMsg`、`MASAI`、`CLDK`、`PSCSelector` 等均已补齐正式题名、作者和可用的发表/DOI 信息。

## 对当前研究主张的证据分级

| 用途 | 可优先引用的条目 | 使用边界 |
|---|---|---|
| Error Invariant 与语义故障定位主线 | `Dimovski2023`, `Dimovski2024`, `Dimovski2025` | 这是当前研究的理论与方法基础；2024 版是主要版本。 |
| 程序切片与故障定位基线 | `Weiser1984`, `KorelLaski1988`, `Ferrante1987`, `JacksonRollins1994`, `Zhang2007`, `ZhangGupta2004`, `ZhangGupta2006`, `Wong2016` | 用于建立切片、动态切片、chop 和故障定位的经典对照。 |
| LLM 不能替代结构化切片的论据 | `Shahandashti2025`, `Chang2025`, `SLICEFORMER2026`, `SLICET52025`, `NSSlicer2024`, `NDSlicer2024` | 直接 LLM/神经切片的结果应作为比较对象，不能与 Error Invariant 的评测混为同一任务。 |
| LLM 读取、验证或生成可执行中间语义的证据 | `Laurel2024`, `CIll2026`, `SpecCoder2026`, `TOGLL2024`, `CunhaMacedo2026` | 支持“LLM 需要可验证反馈与中间语义”的设计动机；不能单独证明 Error Invariant 方法有效。 |
| 实现参考 | `WALA`, `dg`, `Slicer4J`, `CLDK2025`, `codebadger2026`, `code2prompt`, `GitIngest`, `giri` | 只放在实现章节或复现说明；不得写作实证相关工作。 |

## 当前仍需在正式论文中遵守的写作约束

- 不把 arXiv 预印本写成已同行评审论文；在引用表与正文中保留预印本状态。
- 不把工具 README、GitHub 项目或 API 文档写成“研究结果”。
- 对于 `AssertMsg2025`，其结果是断言失败信息的可读性，不是断言/测试 oracle 的正确性；只能用于可解释性讨论。
- 对于 `PALM2025`、`EvoOtter2026`、`ChatUniTest2023`，它们服务于测试或测试生成，不直接评价故障定位；应明确其间接相关性。
- 论文的主张应以 `Dimovski2024` 的可运行基线和后续实验数据为中心，而不是以文献中的报告数值替代自身结果。

## 后续非文献缺口

文献检查已不构成阻塞。真正尚未完成的是正式实验闭环：运行 Dimovski 基线、导出 Error Invariant 轨迹、确定基准与人工标注方案、固定 LLM 提示/模型/成本记录，并产出 RQ1--RQ5 的可复现结果。
