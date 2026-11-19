# J 静态切片：本机最大安全堆复测

日期：2026-10-07。用户授权：“本机加大到最大（保证安全）”。**已按启动前实测余量，将本机 Java 最大堆由 8 GiB 提高到 11.25 GiB，另批次实际运行一次；Lang-1 仍在 222.7866 秒发生 Java heap space OOM。Windows 最低可用物理内存抽样为 3.971 GiB，没有触发安全停止线。**

这只是一例已暴露开发缺陷的静态工具诊断，不是模型实验，也不是所有静态切片均不可行的证据。

## 本次结果

| 项目 | 已核验结果 |
| --- | --- |
| 独立真实开发缺陷 / 新真实静态尝试 | Lang-1，1 个 / 1 次；不增加确认性样本 |
| Java 堆 | 11520 MiB，即 11.25 GiB；相对旧 8 GiB 增加 40.625% |
| 时间上限 / 实际结束 | 900 秒 / 222.7866 秒 |
| 返回码 / 超时 / 保护终止 | 1 / false / null |
| 失败信息 | `java.lang.OutOfMemoryError: Java heap space` |
| 最终主线程异常位置 | `Arrays.copyOf → ArrayList.grow/add → PDG.createCalleeParams:894`；方法依赖图的被调用者参数节点创建仍耗尽堆 |
| Windows 最低可用物理内存 / 可用提交余量 | 抽样 3.971 GiB / 35.055 GiB；后者不是可供堆使用的额外物理 RAM |
| 进程容器峰值提交 / 硬上限 | 11.734 GiB / 12.25 GiB；未达到该硬上限，不能把本次归因为容器限制终止 |
| 资源抽样数 / 最低磁盘余量 | 882 / 105.123 GiB，未触及 15 GiB 磁盘线 |
| 调用图节点 / 抽象堆对象 | 8187 / 3216；计数与旧尝试一致，不等于证明图完全同构 |
| 完整静态结果 / 真实完整配对 | 0 / 0；空 stdout 不作为“零节点切片成功” |
| 正式样本 / 模型调用 / 新候选完整回归 | 0 / 0 / 0 |

机器证据：[独立汇总](../../03_experiments/results/j_static_native_max_2026-10-07/audit_v1/summary.json)、[哈希清单](../../03_experiments/results/j_static_native_max_2026-10-07/audit_v1/artifact_manifest.json)、[结束后环境核验](../../03_experiments/results/j_static_native_max_2026-10-07/audit_v1/post_environment.json)、[单元测试记录](../../03_experiments/results/j_static_native_max_2026-10-07/unit_host_v1.json)。

原始本机记录另存于 `90_local_only/adapter_checks_20261007/native_static_max_v1/run/`：冻结配置、执行计划、启动前连续测量、进程标识、完整 stdout/stderr、增量资源日志、最终抽样与结果均保留。旧 `native_static_v1/heap8/` 全部文件在前后逐项验证长度及 SHA-256；旧驱动源码未修改。没有删除数据。

## “最大且安全”如何确定

本次测量到 Windows 可见总物理内存约 31.291 GiB（名义 32 GB），不能将总容量全部交给 Java。其他应用继续运行，未替用户关闭应用，也未改变 VM、交换文件或系统设置。

在适配器小规模编译结束后，按 0.5 秒间隔连续测量 9 次；最小可用物理内存为 **15.472 GiB**、最小可用提交余量为 **46.882 GiB**。取两种余量、所有观测中的最小值，减去 **4 GiB**，再向下取 256 MiB 的整倍数：

`heap_MiB = floor((min(物理余量, 提交余量) - 4096 MiB) / 256 MiB) × 256 MiB = 11520 MiB`。

4 GiB 预算包括至少约 3 GiB Windows 余量和 1 GiB Java 原生/驱动余量。下一个堆档 11.5 GiB 需要至少 15.5 GiB 当时可用量，启动前最小观测未达到；12 GiB 需要 16 GiB，也未达到。**11.25 GiB 是本次启动条件和既定安全余量下的最大值，不是这台电脑任何时候的永久极限，也不是成功所需内存的测量值。**

启动前再次检查；若余量下降，不启动、不静默改预算、不自动重试。执行中每约 250 毫秒检查物理及提交余量，任一种低于 3 GiB 即停止本次自有进程树；同时保留 900 秒、15 GiB 磁盘线与输出大小上限。

新增 Windows Job Object 为整个自有进程树限制 **提交量**，上限为堆加 1024 MiB，关闭驱动句柄时清理其子进程；回读确认这些限制已生效。提交量不等于物理驻留量，因此另行监测 Windows 可用物理内存。依据：[Microsoft 内存限制结构](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)、[Job Objects 生命周期说明](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)。

## 不变项与改变项

- 原冻结包 510 个数据/源码文件加 manifest 共 511 个成员逐项重验，拒绝缺失、额外文件或摘要变化。复用完整原生产/测试字节码、全部依赖和相同目标 Java 8 `rt.jar`，不重新编译真实案例。
- WALA 1.8.0、`wala_demand_v1` 三份分析源码、`zero_one_CFA_smush_v1`、FULL 数据/控制依赖、反射 NONE、无库排除与全部匹配上下文准则不变。入口和准则沿用[旧本机报告](j_static_native_retry_2026-10-07.md)，没有用动态覆盖裁剪静态分析范围。
- 同为 Windows Oracle Java 25.0.2，编译适配器仍使用 Java 17 目标；本次直接指定 `D:/Java/bin/java.exe` / `javac.exe`，避免旧 PATH 包装启动器。小规模编译只另限编译器堆 512 MiB，不改变分析源码或真实案例字节码。
- 相对旧本机尝试，分析配置只改堆；执行保护另加进程容器、提交监测、250 毫秒抽样和磁盘停止检查。因此即使耗时变化，也不称为严格的单因素性能基准。
- VM 全程保持 saved，12288 MiB / 2 CPU 配置未改，未自动恢复。结束后确认没有残留 WalaSlice 进程。

## 验证与结论边界

145 项相关检查中 **143 通过、2 项 Linux 专用检查跳过、失败/错误为 0**。新增 8 项检查包括最低时段/物理/提交量预算选择、不可静默降低预算、所有停止条件，以及真实短暂自有进程的 Job 绑定、查询、主动终止和关闭句柄终止。

首轮保护测试对“关闭 Job 后退出码必须非零”的断言失败，发现 Windows 关闭容器可能使用退出码 0；改为验证 30 秒等待的自有子进程在 5 秒内确实退出，并回读确认硬限制。保护测试修正后完整重跑通过，之后才启动真实 Java。没有忽略测试失败或在真实运行中改保护。

此前三个微型程序的同图节点/边验收记录保留，本次没有重跑，也不新增微型样本数。保存的 buggy 触发 1 个、完整回归 2291 个完成测试身份只读复核；**没有重跑动态、原生基线、FC 或任何模型补丁测试**。真正双向 chop、正式确认集及模型导出仍未就绪，Executed 继续仅代表覆盖。

可以支持的结论是：**从 8 GiB 安全提高到 11.25 GiB，仍未完成这一个开发案例的 FULL 静态分析；本次失败是 Java 堆不足，不是 900 秒超时、Windows 全机内存耗尽或安全容器终止。** 不能由此估算 12/16 GiB 必定足够，也不能断言所有真实项目都失败。下一步更有依据的是方法内 PDG 参数节点/表示规模诊断与语义保真的表示优化；这不在本次资源扩容任务中自动实施，且不得删依赖来冒充同协议成功。

## 可复用代码

- `03_experiments/prototypes/tool_adapters/retry_j_static_native_max_20261007.py`：连续测量后冻结一次预算、受保护本机运行、保存全部记录；不修改旧 8/12 GiB 入口。
- `03_experiments/prototypes/tool_adapters/test_retry_j_static_native_max.py`：安全预算及 Windows Job 短进程检查。
- `03_experiments/prototypes/tool_adapters/collect_j_static_native_max_20261007.py`：离线测试留档、只读重核配置/摘要/计数/旧记录和结束后环境。
