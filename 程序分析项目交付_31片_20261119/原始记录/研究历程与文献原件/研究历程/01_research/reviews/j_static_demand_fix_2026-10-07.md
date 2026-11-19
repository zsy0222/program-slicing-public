# 静态切片实现修正：两版开发对照与 Lang-1 复测

日期：2026-10-07。结论：**完成两处实现层修正并通过有限开发等价性检查，但真实静态切片问题尚未解决，不能开始正式 J3 对照。** 第一版 Lang-1 在240.3321秒超时，第二版在225.0906秒 Java heap space OOM。旧代码、失败记录和新版本均保留；本轮模型调用0、正式样本0、完整真实静态—动态配对0。科研审查流程要求另存版本、核对原始记录，因此未用微型程序成功替代真实案例准入。

## 1. 修正了什么，没有改什么

原版 WALA 的 `SDG.addPDGStatementNodes` 会在访问一个方法时，将该方法 PDG 的全部节点登记到全局编号表。原实现已按方法缓存，并非每次访问语句都重复登记。第一版 `DemandSDG` 改为按实际查询登记全局节点，保留方法内 PDG 和依赖边。来源为官方 [WALA v1.8.0 SDG](https://raw.githubusercontent.com/wala/WALA/v1.8.0/core/src/main/java/com/ibm/wala/ipa/slicer/SDG.java)，来源快照 SHA-256 `694baef1a7f784ccf0cc65cb9515868abad736dd7e560be50003fc8990c859d5`。

第一版运行采样还出现 `LocalSummaryEdges → SparseLongIntVector.set → MutableSparseLongSet.add` 热点。原摘要缓存查询一个不存在的入口/出口对时也建立索引；有序稀疏数组插入可能移动数组。第二版增加哈希索引，只对存在摘要的配对建表，空查询仍返回原来的 null/false。逻辑关系、事实传播及求解规则不改。来源为官方 [LocalSummaryEdges v1.8.0](https://raw.githubusercontent.com/wala/WALA/v1.8.0/core/src/main/java/com/ibm/wala/dataflow/IFDS/LocalSummaryEdges.java)，来源快照 SHA-256 `2fa94a495200fdac8128afe087f574b1c23b4ce8c6be48e735b7eae4532fa222`。

第二版显式编译一个同名 `LocalSummaryEdges` 到新输出目录，并将该目录放在原 JAR 前；这是**本地兼容分支/类覆盖**，不能声称仍是未修改的官方二进制。原 JAR 不被写入，EPL 来源头保留，原缓存路径按实例保留用于对照。

两版均保持：

- WALA 1.8.0原依赖、显式Java 8 `rt.jar`，Java 17运行适配器。
- `zero_one_CFA_smush_v1` 调用图策略；FULL 数据/堆/控制依赖，reflection NONE，无库排除。
- 原入口测试、NumberUtils.createInteger 第684行 / bytecode offset 7 / Integer.decode调用及全部操作数准则。
- 原源码、字节码、动态产物及已保存官方buggy基线不改；8 GiB Java堆、240秒上限、12 GiB VM、2 CPU不变。
- 原部分平衡后向IFDS求解器；不是简单图可达遍历、ThinSlicer或删去堆依赖。没有重选故障准则、参考补丁输入、模型调用或自动降级。

## 2. 开发等价性检查

每版均对三个开发程序运行真实 Java/WALA。比较的是**同一进程、同一调用图中的 Statement 身份及切片诱导边**，不是只比节点数量或源码行数。第二版原 SDG 对照使用保留的原摘要缓存路径。

| 开发程序 | 两实现节点数 | 两实现边数 | 第二版总分析时间 | 结果 |
| --- | ---: | ---: | ---: | --- |
| BranchFixture | 30 / 30 | 40 / 40 | 3.2783秒 | 身份、边、分支/无关代码语义检查一致 |
| MemoryFixture | 30 / 30 | 47 / 47 | 3.3063秒 | 身份、边、字段别名/数组/循环检查一致 |
| JUnitFixture | 15 / 15 | 21 / 21 | 21.9366秒 | 身份、边、FULL/JUnit库方法检查一致 |

第二版每个开发运行另含固定随机种子的缓存组件对照：18,000项 contains/正向/反向查询行为比较，含插入、重复、缺失和大编号；60,000次空查询未建立任何摘要配对项。这些重复组件检查不是新的独立程序或缺陷，也不是通用语义证明。三例覆盖仍有限，不能推断任意项目的等价性或速度收益。

Ubuntu相关单元124/124通过；Windows发现124项，122通过、2项Linux资源保护检查跳过。第一版118项检查及其结果也保留。单元与微型程序成功不代替真实准入。

## 3. 真实 Lang-1 结果

仅1个此前已暴露的独立开发bug；本轮新增2个静态尝试，不能计作2个新样本。

| 尝试 | 静态实现 | 结果 | 完成静态节点 |
| --- | --- | --- | ---: |
| 上一轮比较对象 | 原SDG/原摘要缓存，8 GiB堆 | 240.4562秒 timeout | 未产出完成结果 |
| 本轮 v1 | 按需全局编号 | 240.3321秒 timeout，返回-9来自时间保护 | 未产出完成结果 |
| 本轮 v2 | 按需全局编号 + 仅已有摘要哈希索引 | 225.0906秒 Java堆OOM，返回1 | 未产出完成结果 |

两版调用图均8187节点、抽象堆实例3216；约15秒完成调用图，约20秒完成mod/ref摘要，随后进入后向求解。机器记录中的 `static_nodes:0` 是“没有完成切片”的占位值，不是成功计算了空切片。

v2最终OOM栈位于 `PDG.addParamPassingStatements(PDG.java:983)` 的堆参数节点集合扩张，经 `PDG.populate/getNumber → SDGSupergraph.getLocalBlockNumber → TabulationSolver`。它直接支持“当前失败发生在方法内PDG堆参数节点建立/保存阶段”，但不证明这是唯一瓶颈、内存泄漏或死循环。第一版优化只处理全局编号，**没有消除 PDG 自身的批量建图**。不能因为较早进入某阶段或最终出现OOM，宣称整体速度、内存消耗或成功率已改善。

运行前后和收集时冻结输入哈希一致。只读重新核验保存的buggy trigger 1项、full 2291个不同完成测试身份；失败身份符合官方buggy预期。这是基线记录复核，未重跑测试，也不是模型补丁通过。原动态25节点仅复用，未重跑动态分析；FC未改动。

guest每秒采样最低可用内存分别2655.43 / 2634.26 MiB，故Java堆OOM不等于整台虚拟机物理内存用尽。结束后guest可用约11280 MiB、根分区可用112 GiB、无遗留WalaSlice进程。Windows结束快照约4.358 GiB可用；它是离散观测，不是连续峰值保证。本轮未扩容、重启或清理VM。

## 4. 保存与运行入口

- [本机核验汇总](../../03_experiments/results/j_static_demand_fix_2026-10-07/audit_v2/summary.json)、[归档核验](../../03_experiments/results/j_static_demand_fix_2026-10-07/audit_v2/archive_identity.json)、[资源结束快照](../../03_experiments/results/j_static_demand_fix_2026-10-07/resource_after_v2.json)。
- 新代码在 [wala_demand_v2](../../03_experiments/prototypes/tool_adapters/wala_demand_v2/README.md)；显式入口 [run_wala_demand_v2.py](../../03_experiments/prototypes/tool_adapters/run_wala_demand_v2.py)，本轮受控驱动 `retry_j_static_demand2_20261007.py`。配置必须指定 `demand_numbering_hash_summary_v2`；旧实验入口没有被悄悄替换。
- VM新目录为 `/home/vboxuser/program_slicing_preparation_20261007_v1/static_demand_lang1_v1`、`static_demand_lang1_v2`，审计目录 `static_demand_audit_v2`。原 `wala.py` / `WalaSlice.java` 哈希仍为 `2481569126271d33f9d350b1ff498dce27dda85fe998ff60c4955eae2728914b` / `b86468870fe4435a0833c85d7896fae88fc64646a930efc96ce86d2ab1f284d0`。
- 本机包 `90_local_only/adapter_checks_20261007/static_demand_fix_v1/vm_evidence_v2/static_demand_evidence_v2.tar.gz`，622526字节，SHA-256 `b82261752486cd551e219bde6787fd08a4f14974be5f4b2c5e7df67faa806b12`。277个数据成员、2个audit成员逐项核验，32个源码/说明文件本机与VM一致；原目录全部保留，无数据删除。

## 5. 剩余修正边界

下一处应处理**PDG方法内堆参数节点的惰性表示/编号**，先给出每方法、每调用点的节点规模诊断，再验证与原图的接口、入口/出口枚举、局部编号及递归调用求解一致。仅改全局缓存还不够。本轮不把修改范围扩展成未经验证的新PDG、不删库/堆依赖、不无限增加内存或超时。

当前分支仅供继续开发诊断；真正双向chop、共同token预算、真实候选全量演练及未暴露确认集仍待完成。静态切片未完成前，正式模型队列保持关闭；这不是LLM理解或修复成绩。
