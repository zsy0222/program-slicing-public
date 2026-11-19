# J 静态切片：Windows 本机独占运行诊断

日期：2026-10-07。用户授权：尝试“静态分析在 Windows 本机运行，Ubuntu 与其错峰”的方案一。**本机运行适配及三个开发用例检查完成；真实 Lang-1 在 8 GiB 堆下仍然 OOM，没有打通完整配对。**

## 实际执行与结果

| 项目 | 本次观测 |
| --- | --- |
| 独立真实开发缺陷 | 1：已暴露的 Lang-1；不是新确认样本 |
| 新真实静态尝试 | 1 次；另有 3 个微型程序静态开发检查，不能增加缺陷数 |
| Java 最大堆 / 时间上限 | 8192 MiB / 900 秒 |
| 实际结束 | 162.1008 秒，返回码 1，`timeout:false`，`stop_reason:null` |
| 失败类型 | `java.lang.OutOfMemoryError: Java heap space` |
| 最终异常栈 | `PDG.createReturnStatements:871 → AbstractGraph.addNode → MutableMapping.add`；仍是方法依赖图节点构造/登记，不是最终切片源码文本过大 |
| 完整静态切片 / 真实完整配对 | 0 / 0；失败时没有可接受的完整切片，不把空输出当作零节点切片 |
| Windows 最低可用物理内存 | 约 7.010 GiB；没有触发 3 GiB 主机运行余量停止线 |
| 调用图 / 抽象堆对象 | 8187 / 3216，与保存的 Ubuntu 尝试计数相同；仅计数一致不证明图完全同构 |
| 正式样本 / 模型调用 / 新候选全量回归 | 0 / 0 / 0 |

机器记录：[独立核验汇总](../../03_experiments/results/j_static_native_2026-10-07/audit_v1/summary.json)、[产物哈希清单](../../03_experiments/results/j_static_native_2026-10-07/audit_v1/artifact_manifest.json)、[单元测试](../../03_experiments/results/j_static_native_2026-10-07/unit_host_v1.json)。

原始输入与进程记录保存在项目私有目录 `90_local_only/adapter_checks_20261007/native_static_v1/`；`heap8/` 包含冻结配置、执行计划、进程标识、完整 stderr、stdout、资源抽样及结果。旧 VM 检出、源码、适配器和失败记录未覆盖或删除。

## 如何保持可比性

1. 从上次 900 秒尝试的冻结清单重新验证旧输入，再单独打包需要的完整生产/测试字节码目录、依赖 JAR、标准库、适配器源码以及保存的源码/动态证据。未重新编译真实案例。
2. 输入包共 **511 个成员**，包括 510 个数据/源码文件和一份 manifest；传输后逐一检查类型、路径、长度及 SHA-256，解压前拒绝非普通文件和重复/越界路径。最终审计重新核对全部文件，检查没有未登记输入文件。
3. 归档为 29,066,991 字节，SHA-256：`2ae4811e588ec734a891f2711cb423c95ad444884107c4f01fc76b377fd91e44`。不包含 SSH 凭据。
4. WALA 1.8.0 及其依赖 JAR、`wala_demand_v1` 三份源码、目标 Java 8 `rt.jar` 保持字节身份。目标标准库 SHA-256 为 `8f20323f5d69f9d46a6a9ef67621a01d7a2704ad9b79afc7fb4f97192f600e6b`。
5. FULL 数据依赖、FULL 控制依赖、`zero_one_CFA_smush_v1`、反射 NONE、无库排除、全部匹配静态上下文准则保持不变；只重定位文件路径。入口仍为 `NumberUtilsTest.TestLang747()V`，准则仍为 `NumberUtils.createInteger` 源行 684、字节码偏移 7 的 `Integer.decode` 调用，全部使用操作数。
6. **分析运行器有变化：Ubuntu OpenJDK 17.0.20.1 → Windows Oracle Java 25.0.2。** 编译适配器仍指定 Java 17 字节码，目标分析库仍为同一 Java 8 JAR。该变化显式记录，不能把两次结束时间差归因为操作系统或称为严格性能提升。

## 虚拟机与安全预算

只读确认 VM 中没有运行中的实验后，先完成输入复制和校验，再请求正常关机。普通 ACPI 请求未使其退出；免交互 `sudo systemctl poweroff` 因需要密码未执行成功。随后使用 VirtualBox **保存状态**退出，保留现场，没有强制断电、删除数据或改变 VM 的 12288 MiB / 2 CPU 配置。

保存退出后 Windows 可用物理内存约 15.8 GiB。新本机入口要求启动时“最大堆 + 4 GiB”物理及提交余量，运行时保留至少 3 GiB 主机余量；磁盘停止线仍为 15 GiB。

本轮仅实际执行 8 GiB 堆。**12 GiB 堆没有运行**：它需要至少 16 GiB 当时可用物理内存，而结束后的离散检查仍约 15.8 GiB；没有降低安全线、关闭其他程序或假定交换文件等于物理内存。虚拟机保持 `saved`，未自动恢复与静态分析并行。

## 验证与计数边界

- Windows 单元测试总计 137 项：135 通过、2 项 Linux 专用资源限制检查跳过，失败/错误为 0。最初沙盒中 Anaconda 无法写其临时测试目录，未将该权限错误当作分析失败；正常用户环境完整重跑并保存通过记录。
- 三个本机微型程序在同一调用图中比较 demand-v1 与原版 WALA，节点身份及诱导边一致：Branch 30 节点/40 边、Memory 30/47、JUnit 15/21；各自要求的依赖保留、无关语句排除等开发检查通过。这只支持有限实现验收，不是所有真实程序的等价证明。
- 保存的 buggy 基线审计仍为触发 1 个、完整回归 2291 个完成测试身份；此次仅复制和核对该记录，**没有重跑基线或动态分析**。这些是官方 buggy 失败复现证据，不是模型补丁通过数。
- 未调用模型、未生成/验证新补丁、未执行 FC；真正双向 chop、候选全量演练及确认集仍未完成。J3-Executed 继续是执行覆盖，不是双向切片。

## 可以支持的结论与下一步

本机独占运行释放了虚拟机占用，当前适配能在 Windows 正常开展分析；但它**没有解决 8 GiB 堆下 Lang-1 的依赖图节点构造内存需求**。主机最低仍有约 7 GiB 可用而 Java 堆 OOM，不能称为整台电脑物理内存耗尽，也不能从此推断 12 GiB 必然足够或所有静态切片不可行。

下一步可在达到安全余量后另批次提高堆；或针对方法内 PDG 节点/参数表示做语义保真优化及同图开发验收。未经新协议不得通过删除堆/控制依赖、动态覆盖裁剪静态分析范围来替代 FULL。此次任务到本机试跑与审计为止，不自动开启另一条优化路线或模型实验。

## 可复用入口

- `03_experiments/prototypes/tool_adapters/retry_j_static_native_20261007.py`：VM 冻结输入导出、逐项校验解压、本机独立静态诊断；旧适配器的 8 GiB 上限未改。12 GiB 是显式可选预算，不自动重试或扩大。
- `03_experiments/prototypes/tool_adapters/collect_j_static_native_20261007.py`：本机微型等价检查与已保存记录审计。
- `03_experiments/prototypes/tool_adapters/test_retry_j_static_native.py`：转移篡改、归档路径/类型/重复成员、不可隐式扩大预算等负向检查。

后续命令应直接指定实际 JDK 可执行文件（本机为 `D:/Java/bin/java.exe` 与 `D:/Java/bin/javac.exe`），避免 PATH 中 `javapath` 启动器包装。此次真实尝试自然 OOM 结束，已确认无残留 Java 进程；未触发包装器的超时/资源终止路径。
