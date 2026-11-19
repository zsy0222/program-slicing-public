# Defects4J 全库实验计划与启动状态

用户要求：规划并开始整个数据库实验。按上下文解释为 Defects4J，而非 C 种子集合或 SWE-bench；如用户指定其他数据库需调整。

## 实际状态

**选择性复测完成（2026-09-25）**：独立 v6 批次 `/home/vboxuser/d4j_full_recheck_20260925_v6` 已完成 13 个指定缺陷的 26/26 个 buggy/fixed 修订复测；运行器已退出、`checkout_error` 为 0，根分区剩余约 60.16 GiB。只读配对审计通过 9/13 对；逐测试报告审计为 trigger 62/62 符合判据、完整套件报告结构 26/26 有效，但仅 19/26 修订的完整套件行为符合预期。未通过的四对是 `Compress-19/20/21` 与 `Math-58`，其失败明细见恢复报告“异常配对选择性复测（已完成）”。重测未增加独立缺陷分母，也未覆盖或合并 v5。此为 Defects4J 官方 buggy/fixed 基线的复现诊断，不是 LLM 修复成绩；模型调用仍为 0。全库 J-A 至 J-D 正式模型对照尚未运行。

**最新基线状态（2026-09-25，v5 全库基线已结束并完成只读审计）**：854/854 个冻结库存缺陷均有 buggy/fixed 两侧最终结果，共 1,708 条修订记录；严格成对复现审计通过 841/854 对。逐报告审计：触发步骤 3,556/3,558 符合预期；全量测试报告 1,707/1,708 结构有效，1,694/1,708 符合预期行为。13 个配对未通过审计，3 条修订结果状态为 timeout；另有一个旧的未被最终结果引用的 `Math-103b` 中断 attempt，均不改变 854 的冻结分母。v5 的 `checkout_error` 为 0，运行器已退出，根分区可用约 64 GiB。统计是 Defects4J 官方 buggy/fixed 基线复现质量，不是 LLM 修复成绩。例外明细见恢复记录“续跑完成与最终审计”。

**J-A–J-D 正式队列状态（2026-09-26）**：冻结样本 248 例保持原始分母；全库 buggy-only 准备已终态，43 例切片就绪、184 例不支持、21 例切片失败。就绪的 43 例均通过完整八任务块预检，形成 344 个模型任务，0 例预检排除、无替换；队列 SHA-256 `1987545e743f773be49ba39dc70670e64751dbfcff64625e5ca68494541aa4a0`。用户授权 J 总计不超过 2,000 次，既有 16 次 J 开发调用已计入，因此正式批次最多 1,984 次；此队列至多请求 344 次。协议冻结后、首次请求前正式 API 计数仍为 0。请求别名沿用 `deepseek-v4-flash`，DeepSeek 官方文档说明该旧别名会路由到 `DeepSeek-V4.1-Flash`；每条原始响应将保存服务返回的实际模型名。该实验的正式输入只含 buggy 源码、冻结失败证据和切片，不含 fixed 代码、参考补丁或通过结果。细节和哈希见 `03_experiments/reports/j_full_scale_readiness_2026-09-26.md`。

**J 正式调用与修复验证状态（2026-09-26）**：冻结队列 344/344 次 DeepSeek 请求均返回 `completed`，服务实际模型名一致为 `deepseek-flash`，finish_reason 均为 `stop`；API 错误 0、重试 0。连同此前 16 次 J 开发调用，已消耗 J 授权上限 360/2,000 次；正式批次没有扩样。原始响应及逐请求持久账本均已保存，正式请求 token usage 合计 3,310,889。冻结 buggy-only 验证器已完成 172/172 修复候选（43 个独立案例 × 4 组各 1 次）：J-A/J-B/J-C/J-D 全模块回归通过分别为 10/43、8/43、8/43、7/43；总计完整回归通过 33/172、完整回归失败 4/172、trigger 失败 92/172、编译失败 37/172、无效补丁 6/172。完整回归只在 trigger 通过后运行；所以只有 37 个进入全模块回归，其中 33 个通过。完整报告和结果位置见 `03_experiments/reports/j_full_scale_readiness_2026-09-26.md`。这只是一次调用下的描述性 repair 验证，不能替代理解评分，也不足以宣称组间优越性。248 例冻结意向分母保持不变：43 例进入模型批次，205 例准备阶段不支持/失败。

**异常案例选择性复测（2026-09-25，已完成）**：按用户要求，对最终审计中未符合预期的 13 个独立缺陷（`Compress-19/20/21`、`JacksonDatabind-44`、`Lang-27/44`、`Math-58/67`、`Mockito-4/8/20/22/24`）重新运行 buggy/fixed 两侧，共 26 个修订。新批次 `/home/vboxuser/d4j_full_recheck_20260925_v6`，不覆盖或合并 v5；沿用已校验 SHA256 的冻结运行器、Java 11、PERL5LIB、单命令 30 分钟上限和 15 GiB 空间停止线。运行器已退出，日志 `/home/vboxuser/d4j_full_recheck_20260925_v6/resume_20260925_retry1.log`；26/26 条 `result.json` 均为 `executed_needs_test_report_audit`，没有 `checkout_error`。剩余磁盘约 60.16 GiB。首次启动因 PATH 参数引用错误未执行测试、结果数为 0，该失败启动保留在 `resume_20260925.log`；修正后的 retry1 批次完整运行。v5 原始结果保持只读，模型调用数为 0。

**2026-09-25 续跑前停止点快照（历史，只读）**：续跑前 786 个缺陷至少有一版结果、778 对通过；68 个没有最终结果。当时的 3,165/3,166 trigger 和 1,562/1,572 完整套件统计已被续跑后的最终审计替代，不能作为最终值。原快照及其例外仍保留在恢复报告“续跑前停止后测试报告逐项核验”。

**2026-09-24 停止时状态（用户要求终止并保存）**：v5 全库基线停止，虚拟机内结果、检出、attempt 和日志均保留；未删除数据。配对审计为 786/854 个缺陷至少有一版记录、778 对通过成对复现核对；v5 的 `checkout_error` 数为 0。根分区 158 GiB、停止后可用约 76 GiB。停止时正在处理 `Math-103b` 的 buggy 修订：`steps.json` 和 checkout 保留，但该 attempt 没有 `result.json`，按中断/未完成处理；修复版与该案例的完整配对未运行，全库余项未完成。成对复现不等同于全库触发测试和完整回归的汇总通过率。详细停止记录见恢复报告。

**2026-09-24 v5 启动与历史环境问题**：旧批次 v4 曾因缺少 `PERL5LIB=/home/vboxuser/perl5/lib/perl5` 产生 710 条环境性 `checkout_error`（355 个缺陷的 b/f 修订）；已停止并完整保留，不计入有效基线。为隔离记录，v5 `/home/vboxuser/d4j_full_screen_20260924_v5` 复制冻结清单，只导入 v4 审计通过的 658 个逐修订结果，不复制或覆盖原始 attempt。v5 使用 Java 11、上述 PERL5LIB 和 15 GiB 安全线；启动后无新增 checkout_error。原始执行及扩容细节见恢复报告。

**2026-09-24 存储扩容**：用户授权将 Ubuntu2204 虚拟盘容量翻倍。已确认无快照、动态 VDI 原容量 82,369 MiB，D: 盘扩容前约有 274.9 GB 可用；虚拟机正常关机后，将 `D:\Ubantu2204\Ubuntu2204\Ubuntu2204.vdi` 扩至 164,738 MiB。用户随后在 Ubuntu 扩展了 `/dev/sda3` 和 ext4；复核显示 `/` 总量约 158 GiB、可用约 91 GiB。根分区容量问题已解决；基线恢复及 v4 环境错误、v5 续跑状态见本节第一条和恢复报告。模型 J 组未启动。

**2026-09-24 磁盘保护暂停**：冻结全库基线运行器已因磁盘安全线停止；进程 3579 已结束，日志明确写明停止且未删除数据。剩余 16,065,851,392 字节（约 14.96 GiB）。暂停时 334/854 个缺陷有记录，327 个成对复现核对通过；7 项待核对/未配对为 Cli-23、Closure-21、Closure-22、Compress-19/20/21、Csv-2。继续前需要确定存储或归档方向并检查磁盘。全库模型调用仍为 0；详细位置见基线恢复记录。

**2026-09-23 约 30% 检查点**：256/854 个缺陷已有结果，253 个通过错误版/官方修复版成对复现核对。当前运行到 Codec-18b，PID 3579 仍活动，磁盘剩余约 20 GiB。Cli-23、Closure-21、Closure-22 为三项持续覆盖异常。该实验是全库基线，模型调用数为 0；详见全库基线恢复记录。

**2026-09-23 约 25% 检查点**：213/854 个缺陷已有基线记录，209 个成对复现核对通过。当前 `Closure-150f` 正在测试，PID 3579 活动，剩余磁盘约 23 GiB。四个未配对项中，三项是旧覆盖异常（Cli-23、Closure-21、Closure-22），另一个为正在执行的 Closure-150。全库 J 组模型调用仍为 0。详情见基线恢复记录。

**2026-09-23 200 例检查点**：854 个库存缺陷中，200 个至少有一版基线结果，196 个完成成对复现核对。运行到 `Closure-137`，PID 3579 仍活动，剩余磁盘约 24 GiB。三项既有覆盖异常（Cli-23、Closure-21、Closure-22）仍保留；Closure-137f 尚在执行。详见 `03_experiments/reports/defects4j/full_database_baseline_resume_2026-09-23.md`。这是基线覆盖，不是模型修复率。

**2026-09-23 约 20% 进度复查**：同一全库基线已有 174/854 个独立缺陷至少一版结果，其中 170 个成对复现核对通过；`Closure-111f` 正在测试，另外三个旧覆盖异常保留。PID 3579 仍运行，磁盘约 27 GiB。仅为基线，不是模型修复成绩；详见 `03_experiments/reports/defects4j/full_database_baseline_resume_2026-09-23.md`。全库 J 组付费模型对照仍未启动。

**2026-09-23 授权后的最新状态**：J-A 至 J-D 已在 Gson-11b/12b 两个复用的开发缺陷上完成 16 次 DeepSeek 单次调用（每组理解、修复各一项）。8 个修复候选已完成隔离验证：J-A 0/2、J-B 1/2、J-C 1/2、J-D 0/2 完整回归通过。Gson-12 的开发输入与官方新检出仅有两行缩进差异，验证在单独的冻结源码重放批次完成，不能等同于正式留出集实验。详见 `03_experiments/reports/defects4j/j_context_development_2026-09-23.md`。全库基线仍独立运行：854 个库存缺陷中 119 个有至少一版记录、115 个成对复现通过，进行到 `Closure-54f`，剩余磁盘约 31 GiB。这些基线数字不是模型修复成绩；全库 J 组模型调用尚未获批也尚未执行。下文带日期的旧状态保留为历史阶段记录。

**2026-09-23 后续检查**：基线进程 PID 3579 仍运行，推进到 `Closure-49f`；114 个缺陷已有至少一版结果记录，110 个成对复现通过，3 个旧超时案例保留，`Closure-49f` 正在测试，磁盘剩余约 32GiB。J 组已离线准备 16 份开发任务输入与独立验证器；新增 DeepSeek 调用被自动审批拒绝，尚无模型响应。细节见下方及 `03_experiments/reports/defects4j/j_context_development_2026-09-23.md`。

**J 组开发检查（2026-09-23）**：已实现 J-A/J-B/J-C/J-D 的离线输入构造原型，并在已有 Gson-11b/12b 开发案例上生成各 8 份理解/修复输入。J-C 没有完整方法字段，J-B/J-D 方法源码相同；随后已用 Java 11 JDK 语法树重新识别方法边界并保留 v3 独立输入。正式模型对照仍未启动。详见 `03_experiments/reports/defects4j/j_context_development_2026-09-23.md`。

**2026-09-23 恢复后状态**：Ubuntu2204 已连通。v4 冻结运行器哈希与本地一致（SHA256 `4929d9690d5c1613d1751ef030e11a22cfa2300940c566c46bf1c89faecb840d`），854 个缺陷的冻结清单与环境检查通过。中断前有 213 份完整 `result.json`，另有 `Closure-42f` 的 0 字节结果；后者已在同目录改名为 `result.interrupted_20260923.json` 保留，原 attempt/steps 未删除。原批次后台续跑 PID 3579，日志 `/home/vboxuser/d4j_full_screen_20260922_v4/resume_20260923.log`；`Closure-42f` 重跑完成并进入 `Closure-43b`。最新核对 107 个有记录的独立缺陷，104 个成对复现通过；`Cli-23f`、`Closure-21f`、`Closure-22b` 是保留的超时记录，当时磁盘剩余约 33GiB。此数字是基线复现，不是模型修复成绩；J-A 至 J-D 尚未运行。详见 `03_experiments/reports/defects4j/full_database_baseline_resume_2026-09-23.md`。

**最新检查（2026-09-23 08:34后）**：SSH连接被拒绝；本机2222无监听，VirtualBox运行中虚拟机列表为空，旧会话55705已不可用。当前无法读取远端最新结果。最后本地已核验快照为Chart-1至21成对复现成功，不能据此推断全库完成。详见 `03_experiments/reports/defects4j/heartbeat_2026-09-23_0834.md`。未改认证、未重启或重复启动实验；等待恢复虚拟机后先检查进程再续跑。下文为历史阶段记录。

已实现全库基线筛查程序 screen_defects4j_database.py，清单解析测试 5/5 通过。尚未在 Ubuntu 执行；不宣称全库已启动。两种执行环境的 SSH 检查均失败，正常用户环境仍显示临时私钥 Permission denied。全库模型调用数为 0。

## 冻结范围

### 本轮启动更新

### 持续跟进记录（下载后实际运行）

Gradle两个包均已下载并校验，第二个包通过Windows续传后传入。用户级Perl模块需在进程中设置PERL5LIB=/home/vboxuser/perl5/lib/perl5，官方CLI已可运行。

初批遇到诊断输出混入trigger名称，已分离stdout/stderr，新增回归测试；6项离线测试通过。v2实际运行Chart-1，错误版trigger失败1项、修复版0项；两版全量均额外出现MonthTests::testParseMonth失败。v3改C区域设置后该额外失败消失，Chart-5、6修复版全量均零失败，但Chart-1至4出现US-ASCII无法编码错误。因此v4统一C.UTF-8以及Java英文语言、UTF-8，并冻结脚本哈希和环境；这些是环境开发批次，不能混为同一正式结果。

当前执行会话96663，远端目录/home/vboxuser/d4j_full_screen_20260922_v4，首批10例。记录all_tests与failing_tests，不能仅凭进程退出码0判断通过。未运行模型调用。旧批次与错误记录保留，不自动删除。

### 首批验收与全库扩展

续跑核对：Chart-1至21已完成42份错误版/官方修复版验证，21/21成对复现成功；占854个全库缺陷约2.46%。快照位于03_experiments/outputs/defects4j_full_screen_20260922/audit_chart_1_21.json。进程PID38666仍运行，磁盘剩余约37GiB。该数字仅为基线复现，新增LLM调用仍为0；未重复启动进程。

首批10例已完成并通过成对核对，详见03_experiments/reports/defects4j/full_database_baseline_first10_2026-09-22.md。全库执行已从同一批次续跑，limit=0，会话55705；截至启动后检查已推进Chart-12。首批原始日志包已下载，本机SHA256为8FEB3080FB21C8F2CD12F166ECE4B5291367E05E087E62AF1E6A2362D27C58E6。

用户要求不中断跟进，已在本对话建立每15分钟心跳检查，automationId=defects4j，ACTIVE。无变化不提醒，只报告显著进度、故障或需人工事项；不启动新API调用、不自动删除文件。全库基线结束且核对完成后停止该自动化。

SSH已恢复：生成密钥时双引号误作口令，现已修正且取得VM_READY。虚拟机安装版本实测3.0.1，使用现有Java11。官方active-bugs元数据实测17项目854缺陷，原始清单保存于03_experiments/outputs/defects4j_full_screen_20260922/metadata_inventory.json。

已校验并非覆盖补齐仓库包、安装Major3.0.1。bootstrap_d4j_20260922.sh 已在虚拟机实际执行，正在下载缺失Gradle包；完成校验后依次运行官方CLI清单和首批10例（每例buggy/fixed）。本轮目前仍为依赖准备，不是854例基线完成，更不是模型实验完成。执行会话49678；远端结果目录/home/vboxuser/d4j_full_screen_20260922。此前“尚未在Ubuntu执行”指早期状态，以本更新为准。

使用本地安装版本的 defects4j pids/bids 生成有效缺陷清单；记录安装路径、Git版本、CLI哈希、Java版本和时区。不用在线当前版本数量替代本地清单。官方当前 README 为 3.0.1，854个有效缺陷，要求Java11；历史2.x要求Java8。不得无记录升级已有环境。

来源：https://github.com/rjust/defects4j

## 执行顺序

1. 全库清单：只生成 inventory.json，不调用模型。
2. 前10例环境试运行：buggy/fixed独立检出，编译，逐一运行官方trigger，再执行完整测试。顺序由项目名、数字缺陷ID决定，不按结果选取。检查报告中的测试数、跳过、失败类型，再决定是否扩大。
3. 全库基线：通过相同清单扩展所有案例；记录检出失败、编译失败、超时、复现异常。串行、每命令30分钟上限、剩余15GiB暂停。保存检出与日志，不自动清理目录；空间不足需另定归档方案。
4. 自动输入准备：实现并审查J-A完整相关文件、J-B完整方法、J-C纯动态切片、J-D方法+切片。旧C附带完整方法，不能作为新J-C。统计异常/断言、跨方法和切片失败覆盖；全库分母不因工具不支持而消失。
5. 模型对照：先单次、固定同一模型与统一编辑接口；理解与修复独立会话。N个可用案例四组两任务为8N次调用，三次重复为24N次；不含反馈。开始大规模付费调用前明确调用及费用上限、模型版本和数据发送范围。按预先冻结的开发/留出划分，禁止看留出结果后调提示或规则。
6. 验证与汇总：干净候选源码编译、trigger、完整回归，报告独立缺陷数与尝试数；理解评分与修复率分开。Java自动局部规则不是原论文EI，F0–F3仍为独立研究线。

## 当前脚本边界

仅负责基线执行与记录，不生成切片、不调用模型、不评价模型补丁。完整测试的退出码不能单独作为通过，脚本状态为 executed_needs_test_report_audit。已落盘的失败结果续跑时保留；重新尝试失败需新批次，不能覆盖失败。中断未完成的案例在新attempt子目录重新检出。

Ubuntu用法（需先将脚本传入虚拟机并核对安装路径）：

```bash
python3 screen_defects4j_database.py --defects4j-root /home/vboxuser/benchmarks/defects4j --output /home/vboxuser/d4j_full_screen_20260922
python3 screen_defects4j_database.py --defects4j-root /home/vboxuser/benchmarks/defects4j --output /home/vboxuser/d4j_full_screen_20260922 --execute --limit 10
# 前10例验收后，同一清单扩至全库：
python3 screen_defects4j_database.py --defects4j-root /home/vboxuser/benchmarks/defects4j --output /home/vboxuser/d4j_full_screen_20260922 --execute --limit 0
```
