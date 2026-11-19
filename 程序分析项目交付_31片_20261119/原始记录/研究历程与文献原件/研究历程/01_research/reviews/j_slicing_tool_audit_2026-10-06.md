# J 组切片工具与历史产物核对（2026-10-06）

状态：**本机只读检查历史 J 输入和归档中的原始切片；最新上游工具独立另存；未部署新工具、未重跑 Defects4J、未调用模型 API。** 这份检查能确认产物来源和结构一致，**不能**据此证明动态依赖语义正确，更不能把静态/动态切片方案视为已通过功能验收。

## 结论先行

1. 历史 J-A–J-D 的 43 个入组缺陷用的是 Slicer4J **动态后向切片**。J-B 是异常帧所在方法的源码，不是 WALA 静态切片；J-D 是 J-B 方法源码加动态切片源码。当前批次没有静态依赖切片组，也没有前后向组合切片组。因此不能用旧 J 结果直接回答“静态、动态、双向谁更好”。
2. 从 `D:\program_slicing_vm_archive_20260927\j_context_full_scale_20260926_v3.tar.zst` **只提取**的 43 份 `raw-slice.log` 和对应 `trace.log`，对照冻结准备记录和模型输入：原始切片 SHA-256、大小、解析节点数、模型切片成员映射、trace 大小及头标记均为 **43/43 一致**；43 例中的模型成员都能追溯到原始节点。共解析 301,925 个原始节点、映射到模型输入的去重源码成员合计 11,184 行；无未解析的非空原始节点行。43/43 能在原始节点找到准则的外层类与行号；40/43 能找到准则类名与行号的精确匹配。其余 Closure-108、Closure-79、Jsoup-84 要进一步检查内部类/事件身份，不能仅凭外层类匹配证明准则选对。
3. 切片“正常”的证据只到**文件与投影一致**。尚无插桩后仍复现**同一失败签名**、准则对应**目标失败执行事件**、trace 完整性、已知依赖小程序的语义冒烟等证明。已有 248 个准备缺陷中只有 43 个 `slice_ready`；184 个在自动生产栈帧阶段退出，21 个切片准备失败。入组选择偏向 `unexpected_exception`，不能外推到断言失败等其他缺陷。
4. 官方最新源码/发行版已另存于本机私有目录，**没有覆盖**旧 WALA、Slicer4J、DynamicSlicingCore、VM 工具、实验输入或日志。Slicer4J 与 DynamicSlicingCore 的本机固定提交已和本次上游 HEAD 快照相同；WALA 新开发提交和 FlowDroid 最新稳定版/开发提交另存。Maven 3.10.0 另存且官方 SHA-512 校验通过。不能把 FlowDroid 2.15.1/2.16.0-SNAPSHOT 直接替换当前 Slicer4J 的旧依赖。
5. 用户在自己的终端已登录 Ubuntu，但本任务进程的非交互 SSH 仍返回 `Permission denied (publickey,password)`；两个终端不共享认证会话。因此**未核验当前虚拟机中**的 Java、工具二进制和新版本功能，也未在虚拟机改动任何文件。

## 复核依据与方法

- 冻结输入：`90_local_only/experiment_runs/j_full_scale_2026-09-26/v3_preparation/accepted.jsonl`、`run_summary.jsonl`、`case_mapping_formal_v1.json`。准备状态 248 = 184 无自动生产帧 + 21 `slice_failed` + 43 `slice_ready`；43 例各有 8 项 J 任务，共 344 项。原有只读审查器 `03_experiments/prototypes/research_audit/audit_j_slice_views.py` 重算组间字段和覆盖情况。
- 原始物：上述本机归档中的 43 份 `raw-slice.log`、43 份相应 `trace.log`；保留原归档，只提取到 `90_local_only/audits/j_slices_20261006/`。新只读脚本 `03_experiments/prototypes/research_audit/audit_j_raw_slices.py` 对每例检验 SHA-256、记录字节数、Slicer4J 节点格式、节点数、模型成员 `file:line` 子集关系、准则类/行及 trace 头。它**不解压整个 trace、不检验实际依赖边**。
- 原始准则核对：43/43 外层类+行号在 raw 中；其中 3 例只有外层类匹配。原包装命令在这 43 例均记录退出码 0、无 timeout，源码哈希与基线 checkout 记录一致。它们是保存的运行记录，不是本次新运行的测试。
- 规模极端值：Closure-125 为 96,620 原始节点 → 3,142 去重源码行；Closure-152 为 32,704 → 1,638；Jsoup-79 为 4 → 2，Lang-39 为 428 → 3。原始节点的大量重复可能来自多次执行；最终源码成员过大或过小需要按预设预算和失败准则审查，不能直接判为工具算错。
- 历史 J 视图将原始节点按源码文件+行号去重、排序，只向模型给源码成员，不提供动态事件顺序、依赖边或运行时值。已保存输入的 J-B/J-D 去掉切片字段后 43/43 相同，但 J-D 在 42/43 例加入了 J-B 方法外的源码；因此它同时改变证据和可见源码量。32/43 例准备记录含未映射原始节点；未映射可能含库/合成节点，不自动等于切片错误。

## 工具版本、存放与兼容性

所有本次新增文件都在被 Git 忽略的 `90_local_only/third_party_tools/upstream_2026-10-06/`，不改变系统 PATH。GitHub 提交号是本次成功取得的上游快照；末次 `git ls-remote` 因 GitHub 连接重置失败，故不保证报告写成后远端没有再前进。稳定发行版信息核对自 [WALA 发布页](https://github.com/wala/WALA/releases)、[FlowDroid 发布页](https://github.com/secure-software-engineering/FlowDroid/releases)、[Maven 官方下载页](https://maven.apache.org/download.cgi)。

| 组件 | 本机原有与本次结果 | 验证边界 |
| --- | --- | --- |
| WALA | 原源码 `bd2e8d1725421f8f3e48f6ba72ffe5fbdf61cbd9` 未动；另存上游 HEAD `1db728d4ea84922c9b3c8c520a180cb40177b6a4` 源码；最新稳定 1.8.0 的 core/util/shrike JAR 已在原私有 Maven 缓存 | 1.8.0 的 `Slicer.class` 在 JAR 内；**没有本项目静态切片适配器或真实案例功能测试**。1.8.0 官方要求 Java 17+ |
| Slicer4J | 原本机仓库 `68f415a3d5cf8731dc2e43a83ffe14af376c887a`，干净；与本次查询的上游 HEAD 相同 | 历史 VM 产物已核对；本机没有新构建或功能冒烟。其脚本要求 sibling `DynamicSlicingCore` 日志器和已构建 `target`，下载源码不等于可运行安装 |
| DynamicSlicingCore | 完整 ZIP 对应上游 HEAD `064a813c8be03bfc7ec634d06657a8533cfeae7f`，原副本保留；旧的不完整 clone 单独保留 | `core/pom.xml` 仍要求 `soot-infoflow:2.10.0-mandoline`，本机原资料未找到对应可构建制品；未将标准 2.10.0 冒充它 |
| FlowDroid | 原 Slicer4J POM 标准 `soot-infoflow:2.10.0`；本次另存稳定 `v2.15.1` 源码与开发 HEAD `9bf10349ec6fdceebbcfda2d261a1f23b9e2e439` 源码（POM `2.16.0-SNAPSHOT`） | 两个新 POM 均编译目标 Java 17；Slicer4J README 写 JRE 8、Soot 插桩到 Java 9。**不得直接替换**旧依赖并声称兼容，需新批次独立构建/冒烟 |
| Apache Maven | 另存当前 3.10.0；二进制 ZIP 的 SHA-512 等于官方 `.sha512`。本机 Java 25.0.2 下 `mvn -version` 通过 | 默认启动在受限环境中查找父目录 `.mvn` 时打印 `Access is denied.`；仅为该进程指定 `MAVEN_BASEDIR` 为项目目录后不再出现，退出码仍为 0。未替换全局 Maven，也未测试工程构建 |

本次下载档案的本机 SHA-256（只作日后复核指纹；GitHub ZIP 无单独官方 SHA 声明）：

| 文件 | SHA-256 |
| --- | --- |
| `downloads/WALA-1db728d4.zip` | `0da4c95f41af8a0bd31b832087ee88a65ca947df34eabfbfbe970193ec96ca25` |
| `downloads/FlowDroid-v2.15.1.zip` | `87c7985e21bf15dfc501d08f15b1ee4a140a755f27217ff4a55b103a65018e8e` |
| `downloads/FlowDroid-9bf10349.zip` | `07f3372190419a20af3c45b03b08e0dee080e66b71bf56eb1fa05f6bc42d7a91` |
| `downloads/apache-maven-3.10.0-bin.zip` | `1f6d9909266510f039f59aa0e13dcd2c66da85f043e56276e41f2918f8bddaff` |

## 未通过验收的切片问题与下一步门槛

1. **准则覆盖**：先支持不产生生产异常栈帧的测试断言，并确保测试准则在被插桩的应用范围里；记录明确的 `unsupported` 原因。现有 184 例不能算 Slicer4J 已运行失败。
2. **同次失败与事件身份**：对插桩前后同一 trigger 的异常类、关键消息/断言和选定失败事件做可核验对照；内部类 3 例须检查二进制类与目标动态事件，而不仅是外层源码行。要求 trace 完整、准则实际执行、过程子命令均成功。
3. **语义小测**：在新工具版本独立构建后，用带已知数据/控制依赖的微型 Java 例子验证字段别名、数组、分支、循环、跨方法返回、异常、内部类、未执行分支。WALA 与 Slicer4J 统一同一失败准则/变量和源码映射，再考虑 Defects4J 冒烟；保存可反例化的预期依赖集合。
4. **对照设计**：下一版把“同一源码上加静态/动态成员标记”与“切片引导的源码抽取”拆开；双向切片明确定义为前后向并集或两个端点的 chop。各组冻结相同可编辑范围，不根据模型结果挑工具或入组例。

本次本机单元测试：`python -m unittest discover -s 03_experiments/prototypes/research_audit -p "test_*.py" -v`，8/8 通过，其中新审查器合成测试 2/2 通过。此测试验证审查器逻辑，不验证 WALA/Slicer4J 的依赖语义。按项目证据审查约定，原始物一致、功能通过和研究结论必须分开陈述。
