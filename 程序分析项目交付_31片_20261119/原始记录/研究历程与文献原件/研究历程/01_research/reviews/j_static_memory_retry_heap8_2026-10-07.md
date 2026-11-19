# J3 资源复测第二步：12 GiB 虚拟机 / 8 GiB Java 堆

日期：2026-10-07。这是已授权的 **Lang-1 开发诊断**，不是模型修复实验。此前[8 GiB VM / 6 GiB 堆记录](j_static_memory_retry_2026-10-07.md)与所有原始记录保留。

结论：**扩容及复测已完成，静态切片仍未通过。** Ubuntu2204 已从8192调整至12288 MiB；同一显式Java 8标准库、FULL依赖分析在240.4562秒达到超时上限，stderr未报告OOM，但没有产生完成的静态切片。不能将“本次未见OOM”解释为内存一定充足或算法已能完成。正式J3样本、完整开发配对、候选回归与本轮模型调用均为0；FC未改动。

## 1. 实际资源及配置

- 精确VM：Ubuntu2204，UUID `7d5fbdba-3592-4084-9042-6b3fb7df47b5`。用户完成操作后的首次核对发现19:43曾重新启动，仍为8 GiB；随后正常ACPI关机成功，确认`poweroff`后才调整。未强制断电、未关闭其他应用、未改认证。
- 启动保护：实测Windows可用15.795 GiB，高于12 GiB VM加3 GiB主机预留的15 GiB门槛。实际guest识别11962 MiB，无swap；根分区可用111.954 GiB，高于15 GiB磁盘线。分析结束guest可用11196 MiB，无遗留WalaSlice进程，VM保持运行。
- CPU仍为2；配置前后比对的硬件子节点只有Memory和运行时GuestProperties不同，存储控制器一致。GuestProperties中的时间戳/来宾信息随关机更新，不应声称整个XML只改一个文本字段。
- 分析中guest每秒采样最低可用2784.5 MiB。Windows的离散快照约11.830、6.631、5.766 GiB，完成后4.503 GiB；这不是连续峰值监测或长期安全保证。当前余量不支持直接继续增加到16 GiB。

## 2. 与上一尝试的受控比较

比较对象只取前次显式Java 8标准库尝试，**不与默认Java 17标准库尝试混算**。

| 项目 | 前次 | 本次 |
| --- | --- | --- |
| VM / 最大Java堆 | 8 / 6 GiB | 12 / 8 GiB |
| 静态配置差异 | 基准配置 | 仅`max_heap_mb` 6144→8192 |
| 实测结果 | 206.6007秒，Java heap space OOM | 240.4562秒，timeout；未报告OOM |
| 完成静态切片 / 完整开发配对 | 0 / 0 | 0 / 0 |

收集器核对WALA Python/Java适配器源码、WALA依赖JAR、Java 8 `rt.jar`、调用图策略、FULL数据/控制依赖、reflection NONE及空排除列表均与6 GiB比较对象一致；原源码、字节码、动态结果和基线记录运行前后及收集时哈希一致。两次均采用240秒上限，无自动降级、重选准则或逐例修补证据。VM内存和堆预算同时调整，不据此隔离两者各自因果贡献。

本次调用图8187节点、抽象堆实例3216；约24.54秒完成调用图。结束前诊断栈仍在`SDG.addPDGStatementNodes`、`SDG$Edges.getPredNodes`及后向IFDS切片路径中。日志支持“依赖图/后向分析未在预算内完成”，不证明死循环、内存泄漏或所需最终堆大小。返回码-9来自本次240秒超时保护，不是据此认定Ubuntu OOM killer。

## 3. 审计与保存

- 只读复核保存的官方buggy测试：trigger完成1项、full完成2291个不同身份，失败身份符合buggy预期；本次没有重跑测试，也不是修复通过。
- 本次新增1个静态尝试，仍只有1个已暴露的独立开发bug。原动态25节点仅复用；正式队列保持关闭。真正双向chop、统一token预算、真实候选全量演练与未暴露确认集仍待完成。
- Ubuntu离线检查113/113通过；Windows发现113项，111通过、2项Linux资源检查跳过。新增6项保护检查覆盖配置仅改堆、原记录不变、资源门槛及输出范围。单元测试不替代真实切片验收。
- [机器汇总](../../03_experiments/results/j_static_memory_retry_heap8_2026-10-07/audit_v1/summary.json)、[成员清单](../../03_experiments/results/j_static_memory_retry_heap8_2026-10-07/audit_v1/artifact_manifest.json)、[归档校验](../../03_experiments/results/j_static_memory_retry_heap8_2026-10-07/audit_v1/archive_identity.json)、[实际资源记录](../../03_experiments/results/j_static_memory_retry_heap8_2026-10-07/resource_verification_v1.json)。较早的`plan.json`保留当时待关机状态，不改写为事后结果。
- 本机证据包：`90_local_only/adapter_checks_20261007/vm_memory12_heap8_v1/j3_memory_retry_heap8_evidence_v1.tar.gz`，320581字节，SHA-256 `f66d987bb150a2e461c08f36c9d28caef593ce7d436321800e727f31e9a2f870`；164个数据成员、2个audit成员逐项验证，13个源码文件本机/VM相同。VM原目录与配置前后备份均保留，无数据删除。

新入口为`resize_j_vm_memory12_20261007.ps1`、`retry_j_static_memory8_20261007.py`、`collect_j_memory8_retry_20261007.py`，未覆盖上一版。下一步应有上限地诊断惰性PDG/SDG的图规模和耗时；若更换库摘要或分析抽象，须另开协议并重新验收。此次不自行增加内存、延长时间或启动模型调用。
