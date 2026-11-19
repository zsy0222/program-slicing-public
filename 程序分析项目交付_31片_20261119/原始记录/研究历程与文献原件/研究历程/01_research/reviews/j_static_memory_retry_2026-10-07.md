# J3 静态切片：8 GiB 虚拟机 / 6 GiB 堆复测

日期：2026-10-07。性质：用户批准的资源调整及 **Lang-1 开发诊断**，不是正式模型实验。此前[增量验收](experiment_preflight_v3_2026-10-07.md)与所有失败记录保留。

结论：**内存配置调整完成，但真实静态切片仍未通过。** Ubuntu2204 从4096调整为8192 MiB；同一Lang-1分别得到240秒超时和6 GiB Java堆耗尽。不能将开机成功、增加预算或单元测试通过称为切片成功。正式J3样本仍为0，本轮模型API调用0；FC未重跑、状态不变。

## 1. 配置变更及安全边界

- 精确目标：Ubuntu2204，UUID `7d5fbdba-3592-4084-9042-6b3fb7df47b5`。先备份配置、发送正常ACPI关机请求，确认`poweroff`后仅执行内存配置变更；CPU仍为2，不改磁盘、网络或认证，不关闭其他应用。
- 启动前Windows实测可用13.713 GiB，高于8 GiB虚拟机加3 GiB主机预留的11 GiB门槛。虚拟机以无新交互窗口方式启动，实际识别7942 MiB物理内存、无swap。分析后Ubuntu可用7282 MiB，根分区可用约112 GiB；没有遗留Java分析进程。
- 两次分析均明确冻结`max_heap_mb=6144`、240秒上限、15 GiB磁盘停止线。1秒采样的最低guest可用内存分别为788.77与771.69 MiB。Windows离散状态快照分析期间及结束时仍有约5.4 GiB以上可用；这不是连续主机峰值监测，也不是无限安全余量保证。
- 配置备份、启动/停止/状态的机器记录在`90_local_only/adapter_checks_20261007/vm_memory8_heap6_v1/`。新脚本只针对上述UUID，拒绝强制断电、复用旧输出或主机余量不足时启动。

## 2. 两次独立记录的实际结果

共同不变项：WALA 1.8.0，VM Java 17.0.20.1运行分析器，`zero_one_CFA_smush_v1`，FULL数据/FULL控制依赖，reflection NONE，无库排除、无自动降级。沿用原生产/测试字节码、依赖JAR、测试入口及精确准则，不重编译、不重跑动态切片或完整基线。

| 新目录 | 与旧静态配置的差异 | 实测 | 可支持的判断 |
| --- | --- | --- | --- |
| `j3_Lang1_static_heap6_v1` | 仅增加堆上限；仍用默认Java 17标准库范围 | 240.8917秒；`timeout`；stderr无`OutOfMemoryError`；超时保护结束本次子进程 | 在该时间预算内未完成；不能称为6 GiB堆已足够或内存问题已解决 |
| `j3_Lang1_static_heap6_java8_v1` | 同一6 GiB堆，另显式加载动态端Java 8的`rt.jar`及WALA模型 | 206.6007秒；`out_of_memory`；`Java heap space` | 标准库对齐后仍未完成；属于单独范围诊断，不覆盖前一结果 |

当前适配器源码含显式标准库、堆配置及诊断支持，与最早VM 2 GiB失败尝试的源码哈希不同。表中的“仅增加”指**配置字段**，不是声称所有实现字节完全相同。两次新尝试使用相同适配器哈希；标准库范围不同，因此也不合并为同一冻结配置的成功/失败统计。

显式Java 8尝试的调用图8187个节点、3216个抽象堆实例；约18.57秒进入后向切片，最终在`PDG.addParamPassingStatements` / `PDG.populate`的参数传递依赖构造中耗尽Java堆。调用图规模不是最终切片大小，提前打印“SDG complete”也不表示惰性构造的全部PDG及后向切片已完成。日志支持故障阶段定位；没有堆对象统计或heap dump，不能据此断言内存泄漏、唯一占用方法或所需最低堆大小。

## 3. 复核、计数与结论边界

- 两次均重新只读审计保存的原生buggy基线：trigger完成1项、full完成2291个不同测试身份，实际失败身份符合官方buggy预期；未重新运行测试，更不是修复通过。
- 原源码包、字节码、依赖、动态结果、基线及适配器逐文件哈希在运行前后及收集时一致。重复诊断仍只有**1个已暴露开发bug**，静态成功0、完整静态—动态配对0、候选回归0、正式样本0。
- Ubuntu相关离线检查107/107通过、0跳过；Windows发现107项，实际105项通过、2项Linux资源保护检查跳过。首次Windows沙盒临时目录权限错误未当作代码通过，普通用户上下文复验与独立机器记录另存。单元通过不替代真实工具验收。
- 本轮按科研证据审查分别保留资源配置成功、超时和OOM，未修改历史结果、未运行模型、未清理数据，也没有恢复已暂停的定时任务。

## 4. 保存及下一步

[机器汇总](../../03_experiments/results/j_static_memory_retry_2026-10-07/summary.json)、[逐文件清单](../../03_experiments/results/j_static_memory_retry_2026-10-07/artifact_manifest.json)、[本机/VM源码身份](../../03_experiments/results/j_static_memory_retry_2026-10-07/source_identity.json)、[归档校验](../../03_experiments/results/j_static_memory_retry_2026-10-07/archive_identity.json)、[Ubuntu检查](../../03_experiments/results/j_static_memory_retry_2026-10-07/unit_vm_v1.json)、[Windows检查](../../03_experiments/results/j_static_memory_retry_2026-10-07/unit_host_v1.json)。

本机包：`90_local_only/adapter_checks_20261007/vm_memory8_heap6_v1/j3_memory_retry_evidence_v1.tar.gz`，315982字节，SHA-256 `54e5fd6e42c2307c734e33e70915a3fb8b028192ca63814001450dd1f3bba190`；160个数据成员、2个audit成员逐项验证，9个源码文件本机/VM相同。原VM目录和前后配置备份全部保留。

运行入口：`resize_j_vm_memory_20261007.ps1`负责资源保护；`retry_j_static_memory_20261007.py`只复验冻结输入并运行静态分析；`collect_j_memory_retry_20261007.py`只读收集与校验。旧输出存在时拒绝重跑。

下一步应针对参数/堆依赖构造做有上限的对象/图规模诊断，或在**新协议**中明确采用库摘要/不同分析抽象并重新做语义验收；不得暗中改成NO_HEAP、删库、关闭异常/控制依赖或只挑成功案例。8 GiB虚拟机内不继续将堆盲目提高到8 GiB，也不把超时上限无限延长。真正双向chop、共同输入token预算、真实候选完整回归与未暴露确认集仍未完成。资源方案已经执行，但它没有打通剩余准备条件。
