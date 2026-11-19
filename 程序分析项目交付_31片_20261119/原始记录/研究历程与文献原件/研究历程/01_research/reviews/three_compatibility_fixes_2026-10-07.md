# 三项兼容性问题：实现、检查与剩余闸门

日期：2026-10-07。工作始于 10 月 6 日，私有构建/运行目录仍保留 `20261006`，未因日期改变覆盖文件。本轮为本机离线开发检查，**模型调用 0、Defects4J 实际案例运行 0、VM 数据删除 0**。用户随后明确选择独立 FC-Codeflaws 协议，不再把新路线称为原论文 EI。

## 结论

| 问题 | 本轮交付与实际验证 | 尚不能声称 |
| --- | --- | --- |
| WALA 适配器与同准则静态/动态切片 | 已实现适配器与严格运行门槛；两个已知依赖 Java 微型程序通过；修正动态循环映射错误，保留原工具与失败批次 | 不代表真实 Defects4J/JUnit、多线程、反射及完整 JDK 场景验收完成 |
| 11 对 C Seed 的来源与数量 | 双侧 11/11 基线复现；查明 13 个物理对、11 个清单条目，但只有 6 份不同错误源码；已修正文档与审计器 | 不能称为 11 个独立真实 bug 或确认性样本 |
| Codeflaws 与形式化分析适配 | 官方归档已解压，数据/测试/AST 适配与双侧开发基线可运行；新 FC 协议已保存，3 对 repair 输出规格绑定及形式 AST↔中文检查通过 | C 切片与内部状态约束后端尚未验收；原 EI 没被替换为等价实现，正式 FC 实验未开始 |

代码入口：[适配器说明](../../03_experiments/prototypes/tool_adapters/README.md)。可追溯机器汇总：[最终检查 v2](../../03_experiments/results/compatibility_checks_2026-10-07_v2.json)。首次汇总及全部失败运行保留。当前适配器单元测试 **26/26**，现有证据审查器测试 **8/8**；单元测试和实际工具用例分别报告，不能互相替代。

## 1. Java：根因与修正

原状态是下载工具而没有可用 WALA 适配器；同一行不等于同一方法/指令/执行事件。动态工具依赖定制 `soot-infoflow:2.10.0-mandoline`，不能以标准 2.10.0 冒充。

新增 `WalaSlice.java` / `wala.py`，使用 WALA 1.8.0、0-1-CFA、FULL 数据/控制依赖和固定入口。导出完整节点身份、SDG 边、SSA 使用/定义、PHI/常量、字节码位置、源行及应用/库来源。修正实际 WALA API 的类解析方式。包含 JDK 异常构造的早期用例曾在 90 秒内未完成，记录保留；最终两个微型用例用算术异常隔离应用依赖验证，不能据此宣称异常库路径问题已解决。

动态工具按 DynamicSlicingCore 官方 CI 路线构建 `resess/FlowDroid:mandoline-2.10.0`，再构建 core/Slicer4J。新副本 `90_local_only/adapter_builds_20261006/build_v2/` 三阶段全部返回 0。上游测试构建时跳过；功能结果来自后续实际微型程序，而不是 Maven 构建本身。

两处实际发现并修正：

1. 新包装器起初把固定输出名写成 `static_log.log`，实际上游是 `static-log.log`，导致插桩虽完成但门槛拒绝。修正包装器，首次拒绝记录仍在 `j_paired_branch_v1/`。
2. 原 core 按基本块保存首语句源行，且 trace→IR 的模糊字符串回退把循环 `if i >= 2` 错配成同一行的 `i = 0`。在 `j_paired_memory_v1/` 中切片漏循环控制依赖。新增 `build_dynamic_overlay.py`，只在全新 JAR 中替换两个 core 类：逐语句源行保存；去除跳转标签表示差异后按指令及源行精确匹配，0 或多个候选硬失败，不再编辑距离猜测。

这一通用修正叫 **本地兼容分支 compat_overlay_v3**，不是原版最新工具；没有逐案例加依赖行。旧源码、原构建和原错误输出不改动。新 JAR SHA-256：`51268fea2bdf717ae23da8725d68a351e94b24794626d35f0a46ecb5da702b20`。输入源码哈希与替换类清单在 `compat_overlay_v3/build_result.json`。

### 实际功能检查

| 开发程序 | 静态检查 | 动态检查 | 同准则/失败保留 |
| --- | --- | --- | --- |
| BranchFixture | 输入定义、分支控制、跨方法计算、准则；无关行排除；未执行分支的常量保留于 SSA | 真实执行的输入、分支、跨方法计算、准则保留；未执行分支与无关行排除 | 通过；同一 `observe(I)V` 调用，插桩前后同一算术异常签名 |
| MemoryFixture | 字段别名读写、数组读写、循环控制、PHI 初值、准则；无关行排除 | 字段/数组依赖、`sum=0`、循环条件及更新、准则保留；无关行排除 | 修正后通过；两侧准则为 `main` 第 15 行的同一调用 |

原始证据位于 `90_local_only/adapter_checks_20261006/`：`wala_branch_v6/`、`wala_memory_v2/`、最终 `j_paired_branch_v4/`、`j_paired_memory_v3/`。每个配对目录含静态 evidence、动态原始 slice/ICDG、插桩前后运行、步骤返回码、工具/228 个库摘要文件哈希和准则身份。

两个 Java 程序是 **2 个开发微型用例**；多次修复重跑不增加独立样本数。WALA SSA 优化会把 `y=0`、`sum=0` 等字面量初值折叠为 PHI/常量，不一定输出独立源行；本轮保留此语义信息，不伪造行号。后续模型实验应固定完整源码包后投影成员标记，不将仅源行集合说成可独立执行的程序切片。

`CheckedRunner.java` 已实现 JUnit4 精确方法入口，生产/测试类共同入应用 JAR；但这部分还没有真实 JUnit/Defects4J 端到端验收。负数 field identity、会被上游丢弃的重复 Logger 块直接拒绝；并发、反射、native、异常库及多指令映射还需开发覆盖。当前配置也未证明完整源映射或一般依赖语义正确性。

工具来源固定：WALA 1.8.0；Slicer4J `68f415a3d5cf8731dc2e43a83ffe14af376c887a`；DynamicSlicingCore `064a813c8be03bfc7ec634d06657a8533cfeae7f`。定制 FlowDroid 分支 ZIP 哈希 `30b6ebbad9f9d53c53234ab9ad6937f7d644623f8e5471565af1772a675cb268`；没有捏造未取得的 commit。便携 Temurin 8u504 ZIP 哈希 `ea43d46ede95b51e44a12c66711706cddc762e0a766c54bccea18954e902b2aa`。WALA 运行 JDK25，目标微型字节码为 Java8，动态工具/运行用 Java8；系统默认 Java/PATH 未更改。

## 2. Seed：11 对不等于 11 个独立 bug

这些是项目自行构造的微型 C 单行变异对，不是外部真实缺陷库。清单有 11 个 ID；物理目录有 13 对/26 个 C 文件，另两对旧版 Seed02/03 不入清单。新审计进一步发现：

`Seed01_update_sign`、`Seed04_update_magnitude`、`Seed05_loop_boundary`、`Seed06_initial_counter`、`Seed08_guard_equality`、`Seed11_counter_increment` 的错误源码完全相同，哈希均为 `678f97f3a84634361b13a416b08de2b58485fc9f14639c5a690624e0fb52e28f`；reference 变异位置不同。

因此只能报告 **11 个开发配对条目、6 个唯一 faulty 输入**。相同输入对应不同“故障行”标签，不能据此评价六个独立定位任务；正确修复也可能不唯一。历史模型回答/分数保持不变，但不再据清单数量宣称 11 个独立缺陷。本轮未删除、改写或暗中替换 Seed。

实际编译执行：11/11 faulty 触发原断言，11/11 reference 正常结束；单行差异与断言未改检查通过。记录 `seed_baseline_v2/summary.json`。**EI 分析器未重跑，确认样本数 0**。Seed README 与 `audit_seed_suite.py` 已增加重复源码门槛。

## 3. Codeflaws：先支持数据与 oracle，再验证分析语义

官方 tar.gz SHA-256：`2673fc16fa05590c5c1171f5b633594713ae9207346a3d0ba4c4d8b2eea82b11`。安全解压 407,746 个成员、1,388,863,876 字节普通文件。元数据 3,903 个唯一 ID；实际 3,904 个目录，多出的 `369-C-bug-5354958-5359647` 未登记；没有元数据 ID 缺目录。两个目录内的大压缩归档未再自动解压，不声称已检查其所有内层测试。

实际新增能力：识别正/负 repair 与 held-out 文件名；双侧原始 C 编译执行；保存输入/输出哈希、测试次数及状态；Clang AST 特性盘点；明确拒绝缺失测试、相同源码、reference 失败及超时。原始数据只读，未删数组、改入口或加入参考答案断言。

### 7 对开发样本结果

| ID | buggy 通过/执行 | reference 通过/执行 | 状态 |
| --- | ---: | ---: | --- |
| 1-A-bug-18353198-18353306 | 24/29 | 29/29 | portable 配对复现 |
| 1-A-bug-18353247-18353306 | 0/22 | 22/22 | portable 配对复现 |
| 1-C-bug-13350774-13350779 | 84/91 | 88/91 | execution_error；两侧各一次超时，且有输出不符 |
| 1-C-bug-15203581-15203678 | 未执行 | 未执行 | held-out 套件缺失 |
| 10-A-bug-13543524-13543571 | 0/25 | 0/25 | reference_failed |
| 10-A-bug-1998522-1998523 | 4/12 | 12/12 | portable 配对复现 |
| 71-A-bug-18359456-18359477 | 未执行 | 未执行 | identical_pair |

总计 **358 次程序测试执行**，包含 2 次超时。只有 3 对通过本机 portable 基线，不代表官方 Linux 原生复现或形式化准入。记录 `codeflaws_portable_v3/summary.json`；新增元数据核对另存 `codeflaws_inventory_v4/inventory.json`。本轮选择旨在诊断，不是全库随机抽样，不能外推覆盖率。

原 Fault_localyzer 的标量语言不支持这些数组/stdio 语义；输出测试也不是原生断言。用户已明确选择另开 [FC-Codeflaws 协议](../workflow/fc_codeflaws_protocol_2026-10-07.md)，故不再尝试把完整 C 强行降到旧语法后称作 EI。

新 `fc_oracle_spec.py` 已为 3 个 portable 成功案例绑定一个确定 repair 失败，构造退出码/规范化输出行序列的形式 AST，并生成受控中文、反向解析核对。对保存的 buggy/reference 观测分别得到 false/true。公开规格不含 reference 源码/哈希/补丁或 held-out 输出；全部组共享同一 repair oracle 信息。原始记录 `fc_output_spec_v1/`。

**这是输出规格绑定，不是内部状态约束、不是真正 C 切片，也不是语义证明。** 当前 `formal_model_ready=false`、`model_jobs_exportable=false`。Frama-C 探针实际返回 `backend_unavailable`；即便 Eva 可运行，前向值分析也不能自动冒充失败相关 EI。后续需完整 C 后端、oracle harness、源映射与至少 5 个独立开发程序的差分/分析检查，再冻结确认集。本轮没有形式化后端或 FC 模型成绩。

## 4. 保留记录与下一步

本轮只新增私有构建/运行目录与适配器代码，更新入口及台账。旧 J/F 模型数据、工具副本、失败运行全部保留；未清理 VM、不改 SSH 密钥/权限、不重启归档自动化。本机剩余空间检查约 C 105.82 GiB、D 52.69 GiB。SSH 身份文件不再可用，当前连接仍未取得；没有把用户另一终端登录当作本进程已登录。

下一步先补 Java 真实测试断言/跨项目开发验收，FC 先补 C 形式后端与输出 harness。两条路线均在当前结果基础上另开版本，不覆盖旧实验，不按模型收益挑工具；这些尚未完成的闸门不能以计划文字补作通过。

本报告按 `research-evidence-audit` 要求核对原始结果、重复源码和实际模型输入边界，将“实现”“运行”“验证”分别记录；没有将工具成功或数据集复现写成 LLM 修复成绩。
