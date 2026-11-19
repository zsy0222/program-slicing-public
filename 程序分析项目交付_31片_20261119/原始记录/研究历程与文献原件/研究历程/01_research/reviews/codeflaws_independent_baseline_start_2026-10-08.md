# Codeflaws 全库独立基线已启动，尚未完成

日期：2026-10-08。用户在“独立运行基线，再检查FC兼容性”的解释后授权开始。**本批不是模型实验；不把形式化不支持记为bug不可复现。**

## 范围与当前状态

执行身份`Codeflaws-independent-native-baseline-20261008-v2`。使用既有清单3,903对原始C错误/参考程序，按1,284个问题/源码相似性簇汇总；包括已暴露开发簇，不因此宣称新增未调试确认样本。目录中另外1个非清单案例`369-C-bug-5354958-5359647`保留但不纳入。

正常用户密钥SSH已验证，未输出密钥、修改认证、VM资源或数据；没有同类旧运行进程。Ubuntu约6 GiB内存，启动后核对约111 GiB磁盘、4.4 GiB可用内存。新批次`/home/vboxuser/cfb2`，PID67981，UTC启动时间2026-10-08T13:34:17.979797+00:00。

首次状态核对：正在冻结全库输入，700/3,903对完成清单检查，其中20对完整旧记录通过核验可复用。**这不是700例原生复现或20例新增成功；全库复现总数仍待运行和独立审计。**准备完成后同一任务自动执行其余案例、审计与归档，无需再次启动进程。

后续只读核对（UTC 13:46:53对应进度）：PID67981存活，已检查2,800/3,903对输入，83对历史完整记录通过复用核验；仍在准备阶段，尚无`runs/progress.json`。错误日志为空，磁盘约110 GiB可用、内存4,517 MiB可用。该计数仍不是新执行或复现成功数。[保存的进度快照](../../03_experiments/results/codeflaws_baseline_2026-10-08_v2/observed_progress_20261008T134653Z.json)。

## 与原FC流程的区别

运行器不导入FC解析器、解释器或模型客户端。整数/数组/宏/多函数等以真实gcc编译与测试为准，不先按FC语言范围剔除。repair和held-out使用各自原始脚本的输出规则，不采用整数token比较，也不运行包含清理操作的原shell脚本。

两侧分别编译，成功编译侧执行全部原始两套测试；错误输出、运行错误、编译失败、参考失败、超时/输出限制、缺失测试及协议不支持分别保存。仅资源故障不计为语义配对复现。逐程序对与簇覆盖分别统计，重复执行不是新bug。

旧记录仅在源码、完整测试、编译参数、两套比较规则及原始观测一致时引用复用；原始数据不覆盖。旧记录缺编译器版本时注明信息不完整，不冒充本次新执行。冲突不择优。最终独立审计从原始字节和清单重算，不运行模型或再次执行C。

## 判题规则盘点与验收

本机24项检查中22通过、2项Linux原生检查跳过；Ubuntu24/24全部通过，包括宏、多函数、300元素数组真实编译、四份双侧测试及篡改检测。真实FCV4-008历史原生记录的86份测试观测通过新复用核验；这只是开发核验，不增加样本。

全库3,903例原脚本盘点：3,869例可同时读取两套比较规则；34例缺可识别完整输出管道，保留清单，待结合完整测试清单区分缺失测试或协议不可用，不称复现失败。repair有3,752例删除空行/行首空白、115例仅删除空行、2例删除空行/两端空白；held-out有3,868例删除空行/行首空白、1例删除空行/两端空白。两套规则各自冻结，不能相互替代。

## v1准备问题与保留

v1合成检查未覆盖真实脚本的Tab缩进；准备核对发现错误转义导致规则误拒绝。核对PID67523、`preparing_inventory`状态且不存在`runs`目录后停止。真实Codeflaws案例执行0，旧目录`/home/vboxuser/cfb1`、工具包和日志全部保留，新增停止说明；不得将该不完整准备批次解释为数据集失败。

v2仅在sed管道内部处理字符类Tab，增加缩进回归检查，真实全库脚本盘点后新开批次，未静默覆盖v1。没有改变原始程序、测试、判定规则或既有FC结果。

## 入口与完成条件

- [当前协议](../workflow/codeflaws_independent_baseline_protocol_2026-10-08_v2.md)、[完整初版方案](../workflow/codeflaws_independent_baseline_protocol_2026-10-08.md)。
- [启动原始记录](../../03_experiments/results/codeflaws_baseline_2026-10-08_v2/observed_start_v1/launch.json)、[Ubuntu验收](../../03_experiments/results/codeflaws_baseline_2026-10-08_v2/observed_start_v1/native_unit.json)、[全库脚本盘点](../../03_experiments/results/codeflaws_baseline_2026-10-08_v2/observed_start_v1/real_script_census.json)、[输入包身份](../../03_experiments/results/codeflaws_baseline_2026-10-08_v2/bundle_identity.json)。
- [基线运行器](../../03_experiments/prototypes/tool_adapters/codeflaws_baseline.py)、[独立审计](../../03_experiments/prototypes/tool_adapters/audit_codeflaws_baseline.py)、[串行任务编排](../../03_experiments/prototypes/tool_adapters/run_codeflaws_baseline_job.py)、[合成检查](../../03_experiments/prototypes/tool_adapters/test_codeflaws_baseline.py)。

客机`job_progress.json`区分准备、运行、审计、归档；逐例进度位于`prepared/progress.json`及`runs/progress.json`。执行结束必须核对3,903个计划终态、原始观测、簇覆盖和新执行/复用数，审计通过才称完整基线完成。资源保护15 GiB磁盘/2 GiB可用内存，不自行清理数据；旧记录不删除。

新增模型调用0；Codeflaws此前224/2,000次调用未改变。旧30分钟归档监测仍保持暂停，本轮未擅自重启自动化。研究范围和统计约定由“实验与结论审查”技能约束：保留失败分母，复现、形式化准入及模型成绩分开。
