# 阅读笔记书目更正单（2026-08-09）

本更正单与 `../matrix/literature_matrix.csv` 配套使用；如与历史阅读笔记或旧汇报的题名、作者、年份、DOI 冲突，以矩阵为准。

## 必须替换的旧表述

| 历史写法 | 已核验表述 |
|---|---|
| Zhang/Gupta 2004--2006 合为一篇，且 DOI 为 `10.1145/996841.996845` | 拆为 PLDI 2004 *Cost Effective Dynamic Program Slicing* (`10.1145/996841.996855`) 和 PLDI 2006 *Pruning Dynamic Slices With Confidence* (`10.1145/1133255.1134002`)；旧 DOI 属于无关论文。 |
| SliceMate: Multi-Agent LLM Slicing | *SLICEMATE: Accurate and Scalable Static Program Slicing via LLM-Powered Agents*。 |
| TOGLL: LLM Test Oracle Generation | *TOGLL: Correct and Strong Test Oracle Generation with LLMs*，ICSE 2025。 |
| ChatUniTest: LLM Unit Test Generation | *ChatUniTest: A Framework for LLM-Based Test Generation*，FSE 2024 Demonstrations。 |
| CIll: LLM Inductive Invariants for Model Checking | *CIll: CTI-Guided Invariant Generation via LLMs for Model Checking*。 |
| Assertion Messages with LLMs (2026) | *Assertion Messages with Large Language Models (LLMs) for Code*，EASE 2025，`10.1145/3756681.3757000`。 |
| PSCSelector (2025) | *PSCSelector: Appropriate Program Slicing Criteria Selection Based on Parameter-Efficient Lightweight LLM*，2026。 |
| WALA 使用 Jimple IR | WALA 使用自身的 SSA IR；Jimple 属于 Soot。 |
| Slicer4J 是 Java 切片基准数据集 | Slicer4J 是 Ahmed、Lis、Rubin 的 Java 动态切片工具论文（ESEC/FSE 2021，`10.1145/3468264.3473123`）。 |
| giri 为当前可用的 2020 工具 | giri 是历史 LLVM 静态/动态切片基础设施，维护与可用性有限，不应用作当前实验基准。 |

## 使用规则

- 阅读深度（精读/摘要级）仍由原笔记记录；本文件只更正书目与来源性质，不把摘要级材料误写为精读结论。
- `code2prompt`、`GitIngest`、WALA 和 giri 等软件项目只能作为实现参考，不能用于证明研究假设或报告经验结果。
