# 项目完整性检查报告

检查日期：2026-08-08

## 一、总体结论

当前项目已经形成较完整的研究叙事和文献资料库，但仍处于“方案与文献整理完成、正式实验尚未闭环”的阶段。最主要的缺口不在研究想法，而在证据链、实现链和实验结果链尚未完全接上。

## 二、已发现的问题

### 1. 文献矩阵与证据地图不一致

- `literature_matrix.csv`：45 条记录。
- `evidence_map.csv`：38 条记录。
- 仅出现在文献矩阵、尚未进入证据地图的条目：`AssertMsg2026`、`Dimovski2023`、`Dimovski2024`、`Dimovski2025`、`Gallagher2025`、`GitIngest`。
- RQ5 在证据地图中只有 1 条映射，支撑不足。
- `PALM2025` 原先重复出现两次，且其中一行 DOI 和 category 字段错位；已修正为 arXiv:2506.19287，并删除重复行。

### 2. 若干文献元数据仍不完整

仍有若干条目使用 `N/A`、`unknown` 或仅有工具名称，尤其是 ND-Slicer、MASAI、Multi-Stage Slicing、SLICE、代码工具条目等。它们需要逐条确认论文版本、作者、发表场所、DOI 或官方仓库地址。

已补正的条目：

- Laurel：补入作者和正式标题。
- PALM：改为实际论文标题、作者和 arXiv 编号。
- NESA：补入作者、正式标题和 FSE 2026 官方会议信息。

### 3. 阅读笔记与矩阵没有一一对应

阅读笔记约覆盖 30 余项，文献矩阵有 45 条记录；新增或仅在矩阵中的论文没有完整的逐篇阅读笔记。尤其是工具类、2026 年新论文和若干 LLM 测试/规约论文，只有摘要式元数据，没有方法、实验、局限和与 RQ 的详细分析。

### 4. 实验仍停留在设计和手工验证阶段

当前已有：实验流程、手工轨迹分析、指标定义和对照条件。

当前缺失：

- Dimovski 工具实际编译和批量运行记录。
- Error Invariant 导出格式和解析程序。
- 15 个实验程序及 Ground Truth 标注集。
- LLM 实际调用、结果保存和统计分析脚本。
- Defects4J 或 SV-COMP 的正式实验结果。
- RQ2、RQ3、RQ4、RQ5 的真实数据表和图表。

### 5. 研究方向文件之间存在历史版本混用

早期文件仍描述“断言引导的级联混合切片”，当前主方向已经转向“LLM 阅读 Error Invariant 轨迹”。后续正式汇报中应明确区分：

- 历史方案：Chop4LLM、SWP、断言级联混合切片。
- 当前方案：Dimovski Error Invariant + LLM 语义阅读。

## 三、外部检索核验结果

- Shahandashti 等人的论文可在 arXiv:2409.12369 核验，论文确实研究静态/动态程序切片，并报告 GPT-4o 静态切片准确率 60.84%、动态切片准确率 59.69%。
- Laurel 可在 arXiv:2405.16792 核验，正式标题为 “Laurel: Generating Dafny Assertions Using Large Language Models”，作者信息已补入矩阵。
- ChatUniTest 可在 arXiv:2305.04764 核验，作者信息仍应补入矩阵。
- CIll 可在 arXiv:2602.23389 核验，正式标题为 “CTI-Guided Invariant Generation via LLMs for Model Checking”，当前矩阵标题仍需修正。
- PALM 实际对应 “PALM: Path-aware LLM-based Test Generation with Comprehension”，arXiv:2506.19287，不是原矩阵中所写的“Path-Aware LLM Assertions”。
- NESA 的正式标题为 “NESA: Relational Neuro-Symbolic Static Program Analysis”，FSE 2026 官方页面已确认作者和论文信息。

## 四、下一步优先级

1. 先完成矩阵—证据地图—阅读笔记三者的 citation key 对齐。
2. 修正所有标题、作者、DOI、会议名称和年份字段；无法核验的内容保留 `needs_manual_check`。
3. 把当前方案的实验输入、输出、Ground Truth 和评价脚本真正落地。
4. 在至少 3 个手工程序和一批 SV-COMP/Defects4J 程序上完成端到端试跑。
5. 再撰写正式结果报告，避免把规划指标写成已获得结果。
