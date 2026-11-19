# 方案二：FULL依赖图按需堆节点存储

日期：2026-10-07。本轮单独开发方法内PDG存储分支，保留旧失败、原图算法及原始输入；不改变切片问题来绕过失败。

状态：四个开发程序与原版FULL切片对照通过，150项离线单元通过、2项Linux专用检查跳过。Lang-1在新目录进行一次8GiB/900秒受控重试；完成结果待核对，不能把启动或中途资源观测写成成功。

## 1. 实现选择

过去仅改全局编号未消除PDG批量保存堆参数：本机8GiB与11.25GiB均OOM。新分支将调用点的完整mod/ref堆位置保留为OrdinalSet，惰性生成参数/返回Statement；实际查询时分配稳定编号，按堆位置建立依赖。原HeapReachingDefs、控制依赖规则、SSA def-use、部分平衡IFDS求解和原摘要缓存均保留。没有改为NO_HEAP/Thin、库排除、仅执行路径或简单图可达遍历。

来源为[WALA v1.8.0官方PDG源码](https://raw.githubusercontent.com/wala/WALA/v1.8.0/core/src/main/java/com/ibm/wala/ipa/slicer/PDG.java)，冻结SHA-256 `fb555959506a51990bc0a2321c04857453e7c8aa804fdd3fe6ef7c76f3bef079`。新代码为[确定性生成器](../../03_experiments/prototypes/tool_adapters/wala_compact_v3/build.py)、[惰性节点实现](../../03_experiments/prototypes/tool_adapters/wala_compact_v3/CompactPDG.members.java.inc)、[独立图核验器](../../03_experiments/prototypes/tool_adapters/wala_compact_v3/CompactPDGCheck.java)及[有界驱动](../../03_experiments/prototypes/tool_adapters/wala_compact_v3/driver.py)。新类继承原PDG但使用独立存储，原JAR留作对照；这是本地兼容分支，不是未改的官方二进制。

全图枚举接口仍产生完整节点集合；入口/出口数组完整返回，但不永久保留所有堆对象；调用接口为惰性只读Set。对求解器的只读查询行为验证，不声称兼容外部修改集合的副作用或适用于任意WALA客户端。生成转换要求固定源哈希、每个锚点唯一；漂移拒绝。

## 2. 开发检查

最终闸门原始记录：`90_local_only/adapter_checks_20261007/compact_pdg_v3/micros_v5/summary.json`。下面是开发程序而非真实独立bug。

| 程序 | 原版/新版切片节点 | 诱导边 | 完整fixture PDG节点/编号往返 | PDG边核验 |
| --- | ---: | ---: | ---: | --- |
| BranchFixture | 30/30 | 40/40 | 43 | 4方法穷举 |
| MemoryFixture | 30/30 | 47/47 | 46 | 3方法穷举 |
| RecursiveExceptionFixture | 93/93 | 161/161 | 147 | 9方法穷举 |
| JUnitFixture | 15/15 | 21/21 | 39,110 | 2方法穷举；1大方法固定32堆位置及全部scalar节点 |

切片比较在同一调用图/指针分析上使用Statement身份及诱导边，包含切片到达的库方法；不是仅比源码行或数量。PDG接口核对入口/出口数组、调用参数/返回、逻辑membership、完整节点枚举、stream及编号稳定/往返。总19方法的完整节点39,346个；18方法穷举边，1方法明示固定抽查。有限检查不是任意程序等价证明，JUnit的抽查数不代表其全部边数。

保留开发失败：micros_v1中的异常对象未用于输出，要求捕获对象节点进入切片的检查失败；原版/新版切片本身一致。随后让捕获对象实际影响输出并按新源码哈希复验。micros_v2/v3的JUnit新增全图检查触发20,000节点保护线；实际fixture节点为39,110。最终独立核验范围明确为小图穷举、大图完整节点/接口加固定堆边抽查，未裁剪真实分析的节点或依赖。这些修改发生在开发阶段，不用于确认集调参。

离线单元记录：[152项发现，150通过、2跳过](../../03_experiments/results/j_static_compact_pdg_2026-10-07_unit_v2.json)。新增版本、策略漂移、缺失等价检查、无效计数、生成锚点及源码漂移等负向检查。不重跑整个Defects4J、动态切片或C/FC实验。

## 3. 真实重试的冻结条件

仅复用已暴露开发缺陷Lang-1，原字节码、依赖、Java8分析库、测试入口和故障指令准则不变。callgraph仍8187节点、抽象堆实例3216。新模式`compact_pdg_v3`明确区别旧`demand_numbering_v1`；Java25本机执行，新增显式断言检查，不能将不同批次耗时解释为纯内存因果基准。

8GiB堆，900秒；VM保持saved；自有进程树9GiB提交硬上限、启动预留4GiB、运行中3GiB主机余量及15GiB磁盘线，每250ms采样。不启动第二进程、不自动加堆/重试、不清理数据、不发送模型请求。原8GiB与最大安全堆运行目录在前后逐文件核对。

真实结果暂不填写，待`lang1_v1/result.json`完成及独立收集器核验。源码包、已保存动态25节点与官方buggy trigger 1/full 2291个完成测试身份仅复用；不计作本次重跑或模型补丁测试。

## 4. 计数与剩余门槛

本轮真实独立开发bug 1、静态尝试1；正式样本、模型调用、候选完整回归均0。真正双向chop、共同token预算、候选完整回归演练及独立未暴露确认集不因工具开发通过而自动完成。

用户追问的Codeflaws形式化组FC独立于J：依据[最新FC/J3机器记录](../../03_experiments/results/experiment_preflight_v3_2026-10-07/summary_with_host.json)，已有同题两对提交74次包装差分和1例CBMC有界输出反例；内部源映射状态约束0，`formal_model_ready=false`。仍缺工具导出的带类型反向状态条件、完整source-map、真实内部谓词AST↔中文同义校验、至少5个独立开发程序验收及未暴露确认集。不能将输出规格/常量轨迹改名为EI；J静态工具修好也不解除FC闸门。FC本轮未修改、未调用模型。

本轮使用科研证据审查流程保留负结果、限定核验范围、区分开发程序与独立bug、官方基线与模型成绩；不以微型检查替代真实准入。
