# J 组验收补充：实施与剩余阻塞

同日VM最新验收见[准备与验收报告](vm_preparation_acceptance_2026-10-07.md)：原生XML sidecar已在新的工具副本接入，11例真实开发案例的开始/完成测试身份交叉核对通过；固定12例全部检查结束，完整切片准入0/12，真实候选演练0。Windows/Ubuntu各84项单元检查通过，VM微型配对及同源四视图3/3。旧报告中的未连接、缺XML及较早测试数是当时状态，不作为最新结论；新拒绝原因和模型调用0详见新记录。

后续修正：同日已解决本文记录的 JUnit 静态超时；新策略下同一个用例最新静态 21.2 秒，3/3 开发微型程序配对及四视图检查通过，73 项单元测试通过。见[超时修正与复验](junit_static_timeout_fix_2026-10-07.md)。下文保留最初阶段的实际状态和失败记录；真实 Defects4J 验收与原生 Formatter 完成事件集成仍未完成。

日期：2026-10-07。范围：本机开发代码、离线负向测试与真实工具微型程序；模型调用 0。历史实验输入、回答、补丁、VM 批次均未修改。本报告依 research-evidence-audit 区分“实现”“实际运行”“研究验收”，不把开发测试解释成模型收益。

## 1. 本轮结论

已实施第一阶段工具链补充，但**还不能启动新的正式 J 组对照**。

| 验收层次 | 实际结果 |
| --- | --- |
| 适配器及输入/验证器单元测试 | 62/62 通过，其中新增 J 验收测试 36 项；包括模拟候选流程，不是 62 个真实 bug |
| 分支微型程序静态＋动态同准则语义验收 | 通过：跨方法输入、分支控制、相关计算；无关语句排除；静态保留未执行备选分支常量，动态排除未执行分支 |
| 字段别名/数组/循环微型程序同准则验收 | 通过：别名写入、字段读取、数组传播、循环控制、累加；无关语句排除 |
| JUnit4 断言微型程序 | 真实运行恰好 1 个失败测试；动态切片成功，精确事件对应 `fails()V` 中 `Assert.assertEquals(JJ)V`；WALA 在 90 秒及独立 240 秒尝试中超时，联合验收不通过 |
| 同源四视图生成 | 上述两个通过配对的微型程序通过；各组源码/失败信息/编辑范围完全相同 |
| 新真实 Defects4J 案例、真实候选完整回归 | 0；本机未发现可用检出/CLI，已尝试只读 SSH，VM 连接被拒绝 |
| 新模型实验 | 未启动；`formal_model_ready=false`、`model_jobs_exportable=false` |

重复运行同一个微型程序不增加独立样本数。这里共检查 3 个不同微型程序，2 个通过联合验收；不与历史 854 个官方基线或 43 个 J 模型案例相加。

## 2. 已落地代码

目录：`03_experiments/prototypes/tool_adapters/`。

### 真实案例接入：`prepare_j_real_case_v2.py`

新建输出目录、buggy 检出和编译，固定 Java 11、时区/locale及可选 PERL5LIB；每一步保存原始命令及输出。磁盘低于 15 GiB 停止，不做清理。仅允许以下 **12 个开发候选**，不按结果替换：Lang-1/10/20、Math-1/5/10、Chart-1/5、Closure-1/10、Time-1、Gson-1。清单已写入代码，不代表已运行，也不是未暴露确认集。

触发测试按测试标识排序选第一个。先取得严格触发/全量执行证据，再冻结全部生产 Java 源码及目标测试源码；共同源码包上限 1 MiB，超过则拒绝，不根据切片结果截取或补回。全部生产文件统一可编辑；目标测试只读。源码非 UTF-8、无可核对测试记录等均保留拒绝原因。

应用 JAR 包含生产/测试字节码及编译目录资源，冲突拒绝；字节码版本不得超过 Java 8。依赖路径显式解析，资源目录不得含未插桩类。静态与动态工具的 JDK、模型仍不同，不能据此声称两者只有“静态/动态”一个差异。

### 同一失败指令：`resolve_j_criterion_v2.py`、`j_criterion.py`

准则来源只允许 buggy 栈帧、应用类清单及对应 javap 输出，不读 fixed 源码或参考补丁。选择首个应用失败帧，保留内部类 `$`、精确 JVM 描述符、源行、字节码偏移和被调用方法。一行多个调用、重复动态事件、非调用型异常指令均拒绝；不默认选择最后一次，不扫描更容易成功的后续栈帧。

WALA 现输出静态种子的实际调用目标。配对检查同时核对所有静态上下文种子、动态事件和准则身份，不能只凭相同行号通过。字段轨迹中的 `FIELD` 元数据单独保留，不再混入语句文本；投影时还核对原始 ICDG 的 SHA-256。

JUnit4 入口修复了缺少 `entry_class` 时的提前索引错误，以及 Windows CRLF 的计数误判。新 CheckedRunner 输出目标测试、运行/失败/忽略数量，要求恰好 1 个未忽略失败测试。插桩前后失败类型及目标帧均须一致。

直接测试方法入口不等价于完整 JUnit 生命周期。目前遇到 Before/After/Rule/RunWith、继承测试基类、构造副作用、expected/timeout 注解等均拒绝；不静默省略这些行为。

### 公平输入：`build_j_marked_views_v2.py`

新开发编号避免覆盖旧分组含义：

| 新编号 | 共同源码之外的内容 |
| --- | --- |
| J2-Base | 无成员标记 |
| J2-Static | WALA 静态后向成员行 ID |
| J2-Dynamic | 同准则失败执行动态后向成员行 ID |
| J2-Executed | 所记录执行事件的覆盖行 ID |

Executed 是“被执行过”的对照，**不是双向切片**；本轮没有实现前后向 chop。四组共享相同完整源码、失败信息和编辑范围，只改变成员标记。代码拒绝额外隐藏字段、不同源码/权限、重复或越界行 ID、切片事件不在实际执行中的情况；库节点、包外节点、无源行 SSA/PHI 单列投影损失，不伪造源行。

全部组拿到相同源码，也意味着这是“切片标记的增量帮助”研究，不是“只给切片是否足够”的旧 J-C 实验。没有区分度的标记集合会被记录，不自动当作有效消融。

### 候选验证：`validate_j_candidate_v2.py`、`j_test_evidence_v2.py`

候选只进入新 buggy 检出；先核对冻结生产/测试源码哈希，再机械应用统一行编辑。拒绝测试文件、配置文件、额外字段、重复编辑和越界行号。编译通过后逐一验证触发，再运行不带 `-r/-t/-s` 的完整套件。全量执行测试 ID 集须与基线一致；缺失、重复、跳过、陈旧或损坏 XML、数量不一致、失败身份不同均不算通过。只通过触发不算完整回归成功。

已用合成桩验证“成功候选”“触发通过但回归缺失”“触发失败立即停止”等控制流程；**真实 Defects4J 候选验证仍为 0**。

## 3. 不能掩盖的兼容缺口

Defects4J 官方默认测试目标使用自定义 Formatter，没有声明 XML formatter，因此新 XML 采集器不能被写成已适配原生 Defects4J 的完整验证器。[官方 build 定义](https://raw.githubusercontent.com/rjust/defects4j/master/framework/projects/defects4j.build.xml)

只读核对官方 `Formatter.java`：`all_tests` 写入发生在 `startTest`，`endTest` / `endTestSuite` 不写完成记录。故本轮没有将 all_tests 的非空列表直接升级为完成证明。[官方 Formatter 源码](https://raw.githubusercontent.com/rjust/defects4j/master/framework/lib/formatter/src/edu/washington/cs/mut/testrunner/Formatter.java)

下一步需在独立开发批次接入完整的开始/结束/失败/忽略事件采集，或经验证的 XML sidecar；不得改旧基线记录。新增准入器在原生环境没有 XML 时会明确拒绝，这是未完成集成，不是数据集没有测试工具。Defects4J 默认运行开发者完整套件，`-r` 才缩小为 relevant 子集。[官方测试命令说明](https://raw.githubusercontent.com/rjust/defects4j/master/framework/bin/d4j/d4j-test)

JUnit WALA 超时的具体热点尚未定位；本轮没有通过省略断言库、换简单失败点或手写逐例证据来制造通过。后续应先保存线程/调用图诊断，再统一冻结库摘要/分析边界；如改变配置另开版本。解决这些之后才可做 12 例真实开发验收及无模型完整验证演练。

## 4. 运行入口

在有真实 Defects4J 的主机配置 `j_runtime_v2.example.json` 中路径；它是模板，不含已核验安装路径或凭据。以下均只生成新目录，不调用模型：

```text
python 03_experiments/prototypes/tool_adapters/prepare_j_real_case_v2.py --case Lang-1 --runtime /path/to/runtime.json --output /path/to/new-j2-dev/Lang-1

python 03_experiments/prototypes/tool_adapters/validate_j_candidate_v2.py --case-directory /path/to/new-j2-dev/Lang-1 --candidate /path/to/candidate.json --runtime /path/to/runtime.json --output /path/to/new-candidate-run
```

本机单元测试：

```text
D:/Anaconda/python.exe 03_experiments/prototypes/tool_adapters/verify_adapters.py --output 90_local_only/adapter_checks_20261007/new-unit-record.json
```

Windows 沙盒默认临时目录本轮出现写权限错误；实际复验仅为当前测试进程设置 workspace 内 TEMP/TMP，不更改系统环境或认证权限。默认 Oracle javapath 启动器还出现编译超时，真实复验使用 `D:/Java/bin/java.exe` / `javac.exe`；所有失败尝试均保留。

## 5. 原始记录与结论边界

- 单元测试：`90_local_only/adapter_checks_20261007/j_acceptance_unit_v5.json`，62 项通过。
- 最新分支/内存工具运行：`90_local_only/adapter_checks_20261007/j_acceptance_v6/branch/`、`memory/`。
- JUnit 静态超时与动态成功联合记录：`90_local_only/adapter_checks_20261007/j_acceptance_v4/junit/summary.json`。
- JUnit 最新动态复验：`90_local_only/adapter_checks_20261007/j_acceptance_v6/junit_dynamic/result.json`。
- 只读汇总和四视图：`90_local_only/adapter_checks_20261007/j2_acceptance_summary_v4/`。
- 早先运行、临时目录权限失败、WALA 90/240 秒超时和第一次字段投影拒绝均保留，不覆盖。

这组证据只支持已列范围内的开发可用性及负向保护有效性，不支持“切片帮助模型修复”的结论，也不改变历史 J/F 成绩。FC 内部状态后端与 C 切片不在本轮实施范围。
