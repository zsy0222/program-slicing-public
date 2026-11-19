# JUnit 静态分析超时修正与复验

日期：2026-10-07。范围：本机 WALA / Slicer4J 开发验收；未运行新的真实 Defects4J 缺陷或模型调用。依 research-evidence-audit 核对原始运行、独立样本与结论边界。

## 结论

原先超时的 **同一个 JUnitFixture 已完成静态分析与静态—动态同准则验收**。最新 WALA 执行耗时 **21.2324 秒**；前一次新配置复验为 25.7029 秒，均在 90 秒上限内。旧记录的 240 秒超时及本轮诊断失败全部保留。

3 个不同开发微型程序均通过联合检查及同源四视图生成；73 项单元测试通过，失败/错误/跳过均为 0。它们不是 3 个 Defects4J bug，也不是模型修复结果。真实项目开发验收、原生测试完成证据接入仍未完成，正式模型导出保持关闭。

## 原因：抽象对象传播与全图堆分析开销

不是 JUnit 测试本身卡住。真实失败运行约 0.2 秒，恰好执行 1 个目标测试、失败 1 个、忽略 0 个，插桩前后同为 expected 3 / actual 2。

旧配置使用 `makeVanillaZeroOneCFABuilder`：分配点和常量特定对象区分，使 JUnit 断言错误格式化、异常以及 JDK 库代码带来的指针传播和全图 Mod/Ref 计算成本过高。

- 原 240 秒记录已经完成 15,124 节点调用图，但未完成切片。不能把它描述成调用图从未完成。
- 本轮 90 秒诊断在 78.896 秒完成同规模调用图，随后开始堆写汇总，达到时间上限。
- 本轮同适配器旧策略 120 秒诊断：调用图 62.115 秒，抽象堆对象 **20,271** 个；堆写汇总完成于 89.933 秒，堆读汇总未完成即超时。线程栈分别落在 points-to 集合传播，以及 `ModRef.scanNodeForRef` / SSA IR 构造；不是无输出便推断死锁。
- 新策略仍有 **15,124** 个调用图节点、**5,369** 个抽象堆对象。最新阶段累计时间：调用图 9.010 秒；堆写完成 14.403 秒；堆读完成 20.872 秒；后向切片完成 21.054 秒；边输出完成 21.064 秒。

这些时间是本机具体运行的观测值，不是所有项目的性能保证；旧超时是截尾结果，不能计算一个精确的加速倍数。

## 修正方案与研究影响

新适配器默认显式冻结 `call_graph_policy=zero_one_CFA_smush_v1`，调用 WALA 标准 `makeZeroOneCFABuilder`。它合并字符串、基本类型包装器、Throwable 以及大量同类分配的抽象对象，减少指针集合和堆汇总成本。

**这改变了堆抽象精度，不是同精度、逐节点结果完全等价的优化。** 合并可能增加 may-alias 和切片成员；新实验必须统一冻结该策略，不与旧 vanilla 批次合并成同一种分析配置。本轮检查保住了预设依赖，不证明所有程序都具有相同精度或完整 Java 语义。

未新增 JUnit/JDK 类排除，未手写本例断言摘要；依赖模式仍为 `FULL_data_FULL_control`，反射仍为既有 `NONE`，WALA 默认库/本地方法模型沿用。JUnit 运行中的 8 个 Extension 方法和 15,113 个 Primordial 方法仍在调用图内。节点数相同也不据此宣称所有调用边完全一致。

旧策略可以通过 `--call-graph-policy vanilla_0_1_CFA` 在**新目录**复现；没有超时后自动换策略、自动取消堆/异常依赖或复用失败切片的回退。配置、配置哈希、适配器哈希、依赖 JAR 哈希、阶段日志和失败输出均保存。

### 顺带暴露并修正的序列化问题

JUnit 两参数调用在 raw slice 中为 `assertEquals(long,long)`，ICDG 中则为 `assertEquals(long;long)`。已核对上游 `StatementInstance.java`：序列化时将逗号改为分号；此前直接比较文本导致四视图汇总拒绝。

新适配器在事件 ID、线程、类、源行全部一致的前提下，按已知 wire format 核对分隔符，同时保存 `raw_unit` 与图中 `unit`，校验所有切片成员，不只校验种子。错误实参、错误线程、重复/缺失事件仍拒绝。引号内的逗号/分号在上游格式中可能有损，当前明确拒绝，不猜测原字符串。此限制需要在真实项目覆盖检查中记录。

第一次汇总拒绝及其部分输出位于 v2/acceptance，保留；未修改旧回答、切片或历史工具 JAR。

## 实际验收

| 开发程序 | 最新静态秒数 | 静态节点 / 边 | 同准则与语义检查 |
| --- | ---: | ---: | --- |
| JUnitFixture | 21.2324 | 15 / 21 | 精确 `fails()V → Assert.assertEquals(JJ)V`；跨方法 seed、分支计算保留；PHI 保留未执行备选常量；无关行排除；真实失败一致 |
| BranchFixture | 0.8786 | 30 / 40 | 跨方法、控制和数据依赖；静态保留备选分支；动态排除未执行分支 |
| MemoryFixture | 0.9337 | 30 / 47 | 字段别名、数组传播、循环和累加依赖；无关语句排除 |

JUnit 源码 SHA-256：`e6f1503ec953947e46c0751ad449cc08e6926d7bb525f32ffa6634569fdf025b`。
旧 240 秒尝试与新复验的 `JUnitFixture.class` 字节完全一致，SHA-256：`b53b8b28969a45bf62cad11db59a50124d0722711b4dfa890f0a8ec39fc2cd24`。未换简单用例或改失败点。

分析运行时为 `D:/Java` 的 Java 25；目标字节码为 Java 8；动态工具和目标失败运行使用已下载 Java 8。静态/动态工具的库模型和运行时差异仍须披露。

## 代码与原始记录

- `03_experiments/prototypes/tool_adapters/WalaSlice.java`：策略选择、全堆/全控制切片、分阶段计时、30 秒主线程诊断、堆对象及 loader 计数。
- `wala.py`：新默认策略显式写入配置，未知策略拒绝，禁止自动回退，结果与冻结策略一致性检查。
- `run_j_paired_smoke.py`、`prepare_j_real_case_v2.py`、`j_runtime_v2.example.json`：新调用入口统一使用明确策略。微型程序静态上限为 90 秒，没有放宽旧 240 秒上限。
- `j_criterion.py`、`slicer4j.py`：已知序列化格式对齐，原始文本保留，所有成员身份检查。
- `test_wala_policy.py`：新增 7 项策略/失败保护和 4 项 wire format 负向检查；合计 73 项单元测试。
- `collect_j_acceptance_v2.py`：从保存记录生成状态，不再硬编码 JUnit 超时；真实项目验收和正式导出仍为关闭。

机器可读汇总与三份四视图：[本轮验收目录](../../03_experiments/results/junit_static_timeout_fix_2026-10-07/summary.json)。原始运行目录 `90_local_only/adapter_checks_20261007/junit_timeout_fix_v3/`。诊断目录为 `junit_timeout_fix_v1/profile_full`、`profile_smush` 及 `junit_timeout_fix_v2/legacy_profile`；先前 240 秒记录为 `j_acceptance_v4/junit/static/result.json`。

复验入口（输出必须是新目录）：

```powershell
python 03_experiments/prototypes/tool_adapters/run_j_paired_smoke.py --fixture JUnitFixture --output 90_local_only/adapter_checks_20261007/junit_new --cache 90_local_only/third_party_tools/m2 --build-root 90_local_only/adapter_builds_20261006/compat_overlay_v3 --java-home 90_local_only/adapter_builds_20261006/java8/jdk8u504-b01 --java D:/Java/bin/java.exe --javac D:/Java/bin/javac.exe
```

本机沙盒测试仍需为当前进程设置可写的项目内 TEMP/TMP，未修改系统 PATH、凭据或认证权限。没有启动虚拟机实验或任何模型 API。
