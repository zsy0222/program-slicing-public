# J3 / FC 实验准备增量验收

日期：2026-10-07。性质：**工具开发、真实开发案例复测及只读证据审查；不是正式模型实验。** 本轮沿用用户已经选择的共同源码范围和 FC 路线，不恢复暂停的自动化，不删除任何原数据，不启动模型 API。新增模型调用 **0**。

结论：共同源码选择、失败事件绑定和有限 C 输入模型取得进展，但**正式实验前置条件仍未全部满足**。J3 有 1 个真实开发 bug 完成动态切片，完整静态—动态准入仍为 0；FC 有 1 个开发提交的具体输入得到有界输出错误反例，但内部反向状态条件、完整源映射和形式 AST↔中文尚未完成。不能用微型程序通过、输出规格或常量轨迹代替这些验收。

## 1. 本轮完成与未完成

| 检查 | 实测 | 可支持的结论 |
| --- | --- | --- |
| Ubuntu 单元检查 | 103/103 通过，0跳过 | 相关适配器逻辑及 Linux 求解器资源保护检查通过 |
| Windows 单元检查 | 103项发现，101通过，2项 Linux 专用检查跳过 | 不是103项在Windows均实际通过；Linux端另有上述完整记录 |
| 匹配Java 8标准库的静态复验 | Branch、Memory、JUnit 3/3；同准则、已知依赖、无关语句排除均通过 | 微型依赖能力；动态记录重用原有冻结结果，没有重新增加3个真实bug |
| 新J3真实开发案例 | Lang-1：原生trigger/full预期行为闸门通过，full有2291个不同完成身份；动态25个节点，完整配对准入0 | 官方buggy失败行为与工具能力，不是修复成功 |
| WALA资源诊断 | VM 2 GiB、本机4 GiB、本机2 GiB显式Java 8标准库三次均出现 `OutOfMemoryError` | 静态后向切片未完成，不能计为静态切片或配对成功 |
| Codeflaws包装差分检查 | 两对提交、同一10-A题目；24+50=74次包装程序执行全部匹配原生保存观测 | 这37个测试的有限输出/退出码/stderr一致；不是一般stdio等价证明 |
| CBMC有界反例 | 10-A-1998522：110项性质SUCCESS、1项输出oracle FAILURE；unwind=32的展开检查通过 | 在列明输入模型、边界及默认检查下复现错误；不是原EI、内部约束或所有C未定义行为的完整证明 |
| FC内部条件/正式准入 | 0；`source_mapping_verified=false`、`internal_predicate_translation_verified=false` | 正式FC2/FC3队列保持关闭 |

前一份[VM验收报告](vm_preparation_acceptance_2026-10-07.md)的固定12例J2结果仍为0/12，不被本轮覆盖。Lang-1的两次新检出、两次切片续接和三次静态诊断全部属于同一个已暴露开发bug，不能增加独立样本数。历史43例J模型实验、841/854官方基线和旧Seed F实验均不与本轮混算。

## 2. J3：实际修改及限制

### 2.1 共同源码在切片之前确定

新协议 `J3-stack-test-bytecode-whole-files-depth1-v1`：从buggy失败栈、目标测试方法字节码引用确定根类，再进行一层完整类引用扩展；保留命中的**完整生产文件**与完整目标测试文件。所有组共同源码、失败信息和可编辑权限相同，测试只读。规则不读取fixed源码、参考diff或切片结果，不按模型成败补选。

Lang-1从108个生产文件选出2个完整文件：`NumberUtils.java`、`StringUtils.java`，另附只读`NumberUtilsTest.java`。共同源码414,682字节，低于冻结1 MiB上限；没有逐行截断。整个仓库仍用于编译、分析与原生回归。此范围不是语义依赖闭包，也不是全仓库自主定位任务；正式输入还须冻结token预算并记录投影损失。

实现：`03_experiments/prototypes/tool_adapters/prepare_j_real_case_v3.py`；原J2入口增加可选钩子，默认旧行为保留。

### 2.2 从真实异常绑定失败指令和动态事件

先用相邻异常栈帧确定调用目标，再用javap确定字节码指令。针对同一条指令多次执行，仅在**单线程、无嵌套异常、轨迹全局终止事件确实是该调用**且与真实异常栈一致时，使用新 `terminal_uncaught_invocation_v1`。不是任选最后一个匹配事件；正常返回、清理事件、不同线程或栈不符仍拒绝。旧唯一事件策略不变。

Lang-1准则为`NumberUtils.createInteger(String)`第684行、字节码偏移7、调用`Integer.decode(String)`；294个记录事件中绑定event 293，切片25个节点。插桩前后真实失败签名一致。该策略只覆盖已验收的未捕获异常调用情况，不自动解决断言失败、catch/finally、并发或一般重复调用定位。

修正目标测试的注解判断：其他测试方法的`expected/timeout`不再误拒绝当前测试；真实类级生命周期、继承、runner等限制没有取消。工具输出目录允许作为冻结应用JAR的同级新目录，原JAR和旧检出不改写。

实现：`prepare_j_real_case_v3.py`、`j_criterion.py`、`slicer4j.py`、`continue_j_slice_v3.py`。

### 2.3 静态分析：标准库对齐，但真实案例仍耗尽内存

WALA 1.8.0在Java 17运行；动态工具实际运行Java 8。新增显式`primordial_classpath`，可读取动态运行环境的Java 8 `rt.jar`及WALA自身模型，记录路径、哈希和库范围，避免默认读取Java 17标准库而不披露。相同标准库JAR仍不意味着静态模型与真实动态执行具有相同语义精度。

复验保持 `zero_one_CFA_smush_v1`、FULL数据/FULL控制依赖、reflection NONE、无库排除、无自动降级。Java 8标准库下3个微型程序语义检查均通过。Lang-1在VM 2 GiB默认库、本机4 GiB默认库，以及本机2 GiB显式Java 8库下均在后向切片阶段耗尽堆；显式库减少了已记录调用图规模，但没有解决资源问题。主机运行时构建与VM不同，作为诊断分开保存，不替换VM结果。

新增冻结`max_heap_mb`及`out_of_memory`分类。较早VM失败原记录仍写`analysis_error`，本次只从保存stderr补充OOM诊断，不回写旧记录。VM物理内存约3.8 GiB、无swap；检查时主机可用内存约6.1 GiB，没有冒险把VM堆提高到4 GiB或继续无界提高本机堆，也未改变VM内存配置。

实现：`wala.py`、`WalaSlice.java`。当前J3-Executed仍为覆盖标记，**不是双向切片**。双向chop、真实候选完整回归演练、新确认队列尚未完成。

## 3. FC：可执行整数输入模型与有界反例

### 3.1 当前仅支持明确检查的子集

`fc_integer_harness.py`生成独立包装文件，以include保留完整原始C，只重定向受支持的`scanf/printf/main`。当前限制为具体十进制signed 32-bit整数流、空白分隔`%d`读取、单个整数`printf`输出点和单一规范整数oracle；保留`printf`返回长度语义。原始格式参数类型先由GCC核对；未知格式、其他I/O、隐藏假设、使用argv等情况拒绝，而非近似为支持。输入不来自reference或held-out。

这不是通用Codeflaws I/O模型。源码、repair输入和期望输出各有哈希；原源码未改动。模型命名空间冲突及未知预处理形式拒绝。没有把数组、指针或副作用从原程序删除。

### 3.2 差分是有限观测检查

`fc_validate_integer_harness.py`只在开发样本评价阶段读取buggy/reference和repair/held-out；遵循保存的编译链接参数，逐测试比较原始stdout字节、退出码及stderr哈希。

| 开发提交对 | 双侧测试数 | 与原生记录相同 |
| --- | ---: | ---: |
| 10-A-bug-1998522-1998523 | 2×12=24 | 24 |
| 10-A-bug-13543524-13543571 | 2×25=50 | 50 |

原生观测取自前一版本，不重复执行原程序；新增的是74次包装程序执行。两个目录属于同一Codeforces 10-A题目，不能称为两个独立题目。reference/held-out仅用于本地评价，未进入分析输入或任何模型请求。

### 3.3 有界反例不等于已得到内部反向约束

CBMC 6.8.0官方Ubuntu 22.04包独立解压于本轮目录，未安装到系统或改全局PATH。对1998522的repair失败输入，unwind=32、有展开断言、保留默认安全检查；得到110项SUCCESS和1项`FC_output_matches_repair_oracle`失败，保存真实反例、方程与属性列表。输出观察点映射到原`printf`第29行，具体轨迹产生输出整数20551。

但输入被具体化后，当前VC大部分被常量化；它没有给出预期的、带类型与完整源位置绑定的内部失败相关条件。**不能把反例里的变量值、常量等式、输出规格或前向状态改名为最弱前置条件/EI。** `formal_model_ready`、内部谓词翻译和完整source-map仍为false。默认列出的检查通过也不等于已证明所有未定义行为均不发生。

保留取消传播/简化的失败探针：首次进程被终止但无内核证据，原因未确认；第二次在512 MiB地址空间保护下明确返回`Out of memory`，属于资源失败，不是程序反例或证明。新增`common.run_limited`限制求解器地址空间、输出与时间，并保留partial文件；超限不被视为成功。未增大循环界、关闭安全检查或把资源失败当成UNSAT。

## 4. 正式启动还缺哪些条件

1. J：在真实开发bug完成资源可承受的FULL静态切片、同准则配对与共同视图核对；若需改变堆抽象/库模型，另开版本并报告精度变化。若改VM资源，须独立获得配置变更方向。本轮没有该变更。
2. J：实现并验收真正的双向chop；处理测试字节码、重复身份和JUnit生命周期覆盖；完成无模型候选的真实完整回归演练，再冻结实际模型输入与token预算。
3. FC：完成工具导出的有类型、源映射明确的失败相关反向状态条件，前向状态只作辅助；实现同义形式AST↔中文并校验，不由Codex/GPT逐例补写。
4. FC：扩展并明确I/O支持范围、原生语义/界限及source-map，在至少5个独立开发程序验收。当前同题两对提交和5个自建微型程序不能替代该门槛。
5. 两组：另冻结未用于源码、规则、提示词和工具调试的确认集，按缺陷/题目及相似源码去重；参考/held-out保持评价专用，正式输入匿名化。已有DeepSeek授权继续有效，但不提前消费预算。

**正式新样本：J3=0、FC=0。新增模型调用=0。** 这不否认历史已经运行的模型实验；只是本轮新协议的实际准备状态。

## 5. 证据与保存

- [含本机诊断的机器汇总](../../03_experiments/results/experiment_preflight_v3_2026-10-07/summary_with_host.json)、[VM只读汇总](../../03_experiments/results/experiment_preflight_v3_2026-10-07/summary.json)、[逐文件清单](../../03_experiments/results/experiment_preflight_v3_2026-10-07/artifact_manifest.json)、[本机诊断清单](../../03_experiments/results/experiment_preflight_v3_2026-10-07/local_probe_manifest.json)。
- 本机原始包：`90_local_only/adapter_checks_20261007/preflight_evidence_v3.tar.gz`，SHA-256 `7f523cf8569065b2cd02c83a482a5e51e4a37dace53c0175401e1059415eb9dc`，本机/VM相同；包内1,984个数据成员及2个audit成员全部逐项核对。6个大型派生产物只在紧凑包中省略，原件仍在VM，未删除。
- 本机源码快照：`90_local_only/adapter_checks_20261007/adapter_source_preflight_v3.tar`，SHA-256 `e831c186cab6546e771e0c5c02ed552ef8bc52f47a3569192b2da00e737051b8`；逐文件身份见`source_identity.json`。
- VM根目录仍为`/home/vboxuser/program_slicing_preparation_20261007_v1`；新核对目录`preflight_audit_v3`。所有旧版本、检出和失败日志保留。收集时根分区可用112.052 GiB，15 GiB停止线未接近。
- 收集器`collect_preflight_v3.py`只读allowlist内记录、重验已知依赖并打包；`finalize_preflight_v3.py`验证下载及源码身份，不调用编译器、求解器或模型。

本报告依据科研证据审查区分了开发检查、官方buggy基线、工具资源失败、内部约束与模型成绩；没有据此推断切片或形式化证据改善了模型表现。
