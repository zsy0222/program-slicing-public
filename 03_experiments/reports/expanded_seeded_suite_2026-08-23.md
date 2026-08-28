# 扩展种子案例筛选报告（2026-08-23）

## 目的与边界

本轮新增 8 个与正确参考程序只有一处源代码差异的 C 案例，并和原有
3 个案例组成 11 例扩展种子套件。它用于检验工作流能否覆盖不同的错误
类型；不是 SV-COMP 或真实缺陷基准，不能用于宣称真实世界的总体有效性。

每个案例的纳入条件为：

1. 错误版本编译后触发断言；
2. 正确参考版本编译后正常退出；
3. Ubuntu 中的 Error Invariant 分析器以 `-full -domain polyhedra` 完成；
4. 分析输出可以被解析为结构化 Evidence Trajectory。

## 筛选结果

| 指标 | 结果 |
|---|---:|
| 已标注的单行故障对 | 11 |
| 错误版运行时失败 | 11 / 11 |
| 正确版运行时通过 | 11 / 11 |
| Error Invariant 分析完成 | 11 / 11 |
| Evidence Trajectory 解析完成 | 11 / 11 |
| 可进入 V2 比较的案例 | 11 / 11 |

新增案例覆盖：更新步长（Seed04）、循环边界（Seed05）、计数器初值
（Seed06）、步长初值（Seed07）、分支边界（Seed08）、更新方向（Seed09）、
特殊迭代分支（Seed10）与计数器更新（Seed11）。

## 纯工具基线（G1）

使用既定的“直接写入 Error Invariant 中错误变量，按接近断言的位置排序”
规则，11 个完成案例的结果为：

| 指标 | 结果 |
|---|---:|
| Top-1 | 3 / 11（27.3%） |
| Top-3 | 4 / 11（36.4%） |
| 分析覆盖率 | 11 / 11（100%） |

命中的三个 Top-1 都是直接对 `z` 做错误更新的案例（Seed01、Seed04、
Seed09）。循环、初始化、控制条件和计数器更新等错误虽然会进入错误相关
轨迹，却不会被这条纯工具启发式选为根因。这是扩展 V2 对比的有效难点，
不是 LLM 已经优于工具的证据。

## V2 就绪状态

已为全部 11 个案例生成：

- P-V2a：源码 + 语义切片 + 因果角色；
- P-V2b：P-V2a + Error Invariant 轨迹 + 分析器位置到源码行映射。

这些输入尚未发送到任何外部模型。下一阶段需要在获得对新增 8 个源码、
切片和 Error Invariant 轨迹的 API 发送授权后，才运行 DeepSeek 的三次
重复调用、结构约束检查、定向反馈、运行时反事实验证与 Top-1 静态差分。

## 可复核产物

- 配对源码和标注：`benchmarks/seeded_faults/`
- 筛选运行状态：`outputs/expanded_seeded_suite_2026-08-23/run_status.csv`
- 静态分析原始输出：`outputs/expanded_seeded_suite_2026-08-23/analysis/`
- 结构化轨迹：`outputs/expanded_evidence_trajectories_2026-08-23/`
- 纯工具基线：`outputs/expanded_seeded_suite_2026-08-23/pure_tool_baseline.json`
- 已生成、未发送的 V2 作业：`outputs/expanded_v2_jobs_2026-08-23/`
