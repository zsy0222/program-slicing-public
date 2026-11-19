# Codeflaws 全库启动条件核对与断点恢复

2026-10-11北京时间18:59:35最终共同验收通过：全部3,903冻结唯一ID/1,284簇均有可解析且receipt匹配的终态，无缺失、额外或身份矛盾；完整独立保存字节审计scope=complete、pass=true、errors为空、audited/planned 3,903、pending 0。独立配对复现3,258对/1,130簇；reference_failed 484、incomplete_tests 21、buggy_resource_failure_only 68、repair_not_reproduced 52、protocol_unsupported 13、identical_pair 7。保存双侧repair/heldout真实观测370,956份（历史新执行来源360,868、历史复用10,088），completion-only恢复和验收新增C/模型均0；这只是buggy/reference原生基线，不是LLM成绩或全库FC形式化准入，不自动开启新实验。

原完成包装器18:10:55正常结束，root/finish session completion字节一致SHA `f7ee3c24a7abcc90926babf93e6c1455cc197e0c0b84085a72f73255f7bcde37`。18:59的17项全量终态/receipt/原工具输入/保全检查和9项单次流式归档共同验收全部通过：7,806份终态/receipt与5,306旧保全映射共9,836唯一文件无改变/缺失，原3,276/2,974终态、1,967部分attempt和8份隔离原字节不变。归档精确1,358,010载荷成员及2个内嵌map全部逐成员SHA及范围核验通过，压缩2,373,448,993字节，整包SHA `f9342b33ab92e17808056ecb8d31ccafe5d7725c232d530d2b81c5e16a1fd550`；gzip完整性、prepared/runs/units/audit/prior_context/frozen_tools及35,536历史来源均通过。payload_manifest SHA `9cad475600cbc62e22cb684fde15afde72c72ae83b8b74db8d019a48d529f025`，path-map SHA `686290e801fd9a52166396c46235cb13ad9817c0a78f1b4c7a2117b82b269889`。completion在归档后写入，单独取回，归档progress是历史快照；未整包载入内存、改VM/认证/冻结协议/数据或删除记录。最低观察MemAvailable 3.519 GiB，磁盘81.88 GiB，保护线保留。

证据：[最终共同验收](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/joint_final_20261011_v1/joint_acceptance.json)、[独立完整summary](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/joint_final_20261011_v1/summary.json)、[全量终态receipt与保全](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/joint_final_20261011_v1/terminal_receipt_preservation_20261011T105933Z.json)、[流式整包及每个成员验收](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/joint_final_20261011_v1/archive_stream_verification.json)、[最终验收报告](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/joint_final_20261011_v1/final_report.md)。科研证据审查使本轮分别确认终态、独立终审与完整归档后才反馈；下文未完成、活动PID和等待开机/许可均为当时历史。

2026-10-11北京时间15:48:34启动后核对：新completion-only会话已于15:46:49建立identity，PID2923为唯一工作进程，boot/工具/manifest身份匹配，已进入`independent_saved_byte_audit`。保存全部3,903对的7,806份终态/receipt哈希快照（文件SHA-256 `1427be57cc0f2b9dfe0dc5d13bfc2aacdb3572712984b55a496f1f521b1614d8`），并保存5,306份旧终态、部分attempt、隔离原字节与旧会话/审计/日志的保全哈希映射（文件SHA `fae5c51a2eafb1b39e850f14cf10c68f32185e16d7cb50f7dd0e18bbbc5729db`）。从15:46:29到15:48:34进程rchar从28.07增加到44.65 GB、read_bytes从11.89增加到24.75 GB，stderr为空，磁盘84.58 GiB/MemAvailable4.10 GiB。summary及归档仍缺失，root/session completion未形成；不是终审通过或归档完成。本机启动记录SHA与客机一致`e821c2bfffc867e640272a7efebdce1b7d4e8531d56463fc4db710cc7e39677c`。30分钟跟踪仅复用该既有任务，不另开审计、重启或调用模型。证据：[启动后身份、读取活动和资源](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/finish_observed_20261011T074834Z.json)。下段15:46时会话尚未建立为较早启动核验时点。

2026-10-11北京时间15:20–15:46仅终审及归档恢复：用户明确“允许”恢复保存字节独立审计及无删除归档，不包含C重跑、模型调用或VM变更。Ubuntu由用户开启后SSH可读，boot为`0da6a295-884a-4288-873a-cc1f5779cbe8`；旧`resume_20261010_v2`任务已中断，最终审计目录为空，root/session completion与归档均未形成，原PID3229的活动只是历史。重新逐一核对3,903个冻结唯一ID均有可解析且receipt哈希匹配的终态，缺失及身份错误为0；原3,276/2,974份终态与1,967份部分尝试、8份隔离原字节、原工具及输入身份均未变。这只是保存记录完整性门槛，不代替完整独立终审。

运行器记录仍为配对复现3,258对/1,130簇、reference_failed 484、incomplete_tests 21、buggy_resource_failure_only 68、repair_not_reproduced 52、protocol_unsupported 13、identical_pair 7；尚待完整独立审计结论。保存的双侧repair/heldout实际观测共370,956份（新执行来源360,868/历史来源10,088），不是本轮新增执行。历史已通过独立审计仍是1,638对/1,369配对复现/472簇。全库原生检测在2026-10-10 21:30:33已经结束，不重启原运行器或重做隔离。

另存completion-only恢复入口与离线保护测试，本机及Ubuntu各15项检查全部通过、无失败/错误/跳过。冻结审计器与归档器源文件未改变：恢复入口只调用原v2保存字节审计与原pack；归档SHA-256改用等价的1 MiB分块读取运行时绑定，避免6 GiB VM一次性载入整个tar.gz，成员、manifest、判题、数据及资源保护线不变，并在finally恢复原绑定。入口SHA-256为`6fea77d64f085f4c35aa031c7f00dee17ad012a5f441a1e6bce04712dc4ccd69`。启动前check在既有job/runner双锁下再次核对全部7,806份终态/receipt及旧记录保全并通过。

15:45:10依新许可仅启动一次`/home/vboxuser/cfb2/finish_20261011_v1`恢复包装器PID2923，启动记录及intent、stdout/stderr独立保存，新许可已使用。15:46:29进程身份与boot匹配，正在创建会话前重核保全（rchar约28.07 GB、read_bytes约11.89 GB）；stderr为空，磁盘84.58 GiB/MemAvailable4.41 GiB。此时新session尚未生成、终审summary与归档缺失，不解释为完成或异常消失，不启动第二个进程。该入口通过重核后将建立新会话并自动执行完整scope审计，再归档至`archive_finish_20261011_v1`；旧会话、审计、日志和attempt全部保留。15 GiB磁盘/2 GiB可用内存保护不变，失败保留记录且不自行重启。只有新root/session completion、完整独立summary、唯一ID/实际观测/旧记录保全及归档manifest/SHA与成员共同验收后才反馈完成。未调用模型，这不是LLM成绩或全库FC准入；科研证据审查使本轮区分保存终态、部分审计和全库终审，拒绝把旧PID或3,903计数当作完成。

证据：[全量保存记录预检](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/finish_preflight_observed_20261011T072512Z.json)、[两端15项离线保护检查](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/finish_offline_gates_20261011_v1.json)、[启动前check](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/finish_check_pass_20261011_v1.json)、[唯一completion-only启动](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/finish_launch_20261011_v1.json)。下文旧PID3229活动、VM关机或等待许可均为历史。

2026-10-10北京时间16:27–16:50独立审计通过并按新许可续跑：`audit_partial_20261010_v2`的保存字节审计已结束，scope=partial、pass=true、errors为空，覆盖全部1,638对有效终态，尚余2,265对；配对复现1,369对、至少一对复现的簇472个，完整终态覆盖簇541个。另有reference_failed 196、incomplete_tests 18、buggy_resource_failure_only 24、repair_not_reproduced 23、protocol_unsupported 6、identical_pair 2。审计复核148,920份新执行来源及4,230份历史来源原生观测，复用历史程序对47个；这些是已保存观测的来源计数，不是本轮重新执行。审计未重跑C、未调用模型。审计摘要本机取回SHA-256与客机一致：`541481f4327f1ff5303fe2fe8a69a11d9adc0a6160b558ef7bcf70c7fe50e11b`；rows身份`e029f5dd13ecb2a4cc37d56d9c5982b5925f129a15f1e6bf9f6b1bd2cf5df0e1`，且1,638个唯一rows ID与当前有效终态严格一致。`recovery_audit_preservation.json`有效，全部3,276份终态/receipt、原2,974份终态和1,967份部分尝试核验未变；8份隔离原字节保留，审计stderr为空。此为部分基线通过，绝不是全库完成、LLM修复成绩或FC全库准入。

16:44启动前26项范围、原工具、输入、工具链、结果保全、隔离、审计、资源及无重复进程/锁的安全门均通过。依据本次“允许”的一次性新许可，16:46:05只启动`/home/vboxuser/cfb2/resume_20261010_v2`，PID3229；此许可已经使用，不得重复启动、重启旧v1或再开会话。16:50:34核验唯一进程、boot/identity和冻结工具一致，保存1,638对/3,276份旧终态哈希快照，规范SHA为`c738edff4607b08891d91d24fb2bb4ebcdb6d46e8147987eea89331a4596cc53`。当前仍重核并跳过旧结果，实际终态1,638/剩余2,265；runs/progress的288只为已重核计划前缀，不是新增执行或全部终态。没有为已有有效程序对创建新attempt；stderr为空、无stop/completion，最终完整审计与归档尚未开始。磁盘100.35 GiB、MemAvailable4.02 GiB安全；单次进程D状态可为磁盘等待，不能据此断言停滞或OOM。所有旧有效结果、部分尝试及隔离备份哈希继续一致；后续4对原路径可随新的合法attempt产生新终态，但不能改动隔离原字节。

30分钟跟踪继续复用唯一v2会话，保留原3,903对/1,284簇、原资源与判题协议、单进程锁和无删除归档；不改VM/认证或调用模型。若本次再失败，只读诊断并保留报告，不自行重启。全库检测后仍必须共同核对完整scope审计、全部唯一ID及双侧实际测试、旧记录保全和归档manifest/SHA后才反馈完成。科研证据审查使本轮先审计全部有效终态、核对保全和身份再续跑，并区分前缀重核、实际终态与模型成绩。证据：[本机校验的部分审计摘要](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/partial_audit_pass_20261010_v2/summary.json)、[审计后的保全记录](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/partial_audit_pass_20261010_v2/preservation.json)、[26项安全门](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/pre_resume_pass_20261010_v2.json)、[唯一v2启动](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/resume_launch_20261010_v2.json)、[启动后身份和实际进度](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/resume_observed_20261010T085034Z.json)。下文审计进行中、新v2未启动及旧v1状态均为历史记录。

2026-10-10北京时间16:03–16:06按用户明确“允许”恢复：新许可包括保留隔离4对空终态、独立审计有效数据、通过后按原协议补跑。另存恢复辅助工具，未改变原冻结运行器、判题、源码、测试或资源限制；本机和Ubuntu的6项隔离保护检查均通过（本机首次检查遇临时目录权限错误，改用项目内自建临时目录后通过，不涉及真实实验数据）。16:03:28只将上述4对的result.json及receipt.json共8个0字节文件移到`/home/vboxuser/cfb2/runs/quarantine_empty_terminals_20261010_v1`，保留精确原路径、文件身份、移动计划及完成记录。所有attempt仍在原位置；1,638对有效终态/receipt共3,276份，以及4对异常和352-A中断案例的1,967份部分尝试文件均保存哈希并重核不变；原1,487对/2,974份文件也保持一致。没有删除、补写结果或重跑C。隔离目录位于runs下，会由既有无删除归档包含；空记录和重新尝试不得增加程序对分母。

16:05:50启动唯一独立保存字节审计PID2882，输出`/home/vboxuser/cfb2/audit_partial_20261010_v2`；恢复辅助工具的audit模式持有job/runner锁，调用不变的审计器v2，审查当前全部1,638对。16:06:52仍活动、stderr为空、summary尚缺失，不能称为审计通过；磁盘100.35 GiB、MemAvailable4.22 GiB，高于15/2 GiB保护线。8份隔离文件哈希、全部3,276有效终态和1,967部分尝试再次核对通过。仍有2,265对未形成有效完整终态，包含4对空记录；记录标记的1,369对复现仍不能全部当作已独立审计通过。新续跑会话`resume_20261010_v2`尚未创建。审计通过且范围、身份、保全、资源及无重复进程门槛全部满足后，依本次许可仅启动一次该新会话，使用既有冻结编排跳过有效结果、保留旧attempt并另开未完成尝试；不重启旧v1会话。若新审计或续跑再失败，保留记录报告，不自行再开批次。30分钟跟踪已更新此授权和实际状态，审计进行中正常等待；最终仍须全库独立审计与归档共同验收。

本轮新增C执行与模型调用均0，不是LLM成绩或FC准入。科研证据审查要求使本轮保留异常原字节、先审计再补跑，而不是补写空终态或重复有效案例。证据：[隔离与保护检查](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/recovery_isolation_20261010_v1.json)、[新审计启动身份](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/audit_launch_20261010_v2.json)、[活动审计与保全核对](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/recovery_audit_observed_20261010T080652Z.json)。下文等待许可和开机前状态均为历史记录。

2026-10-10北京时间15:44–15:50用户告知已开机后只读核对：SSH恢复，新boot为`9f8789b7-2c64-41d2-81cc-2177e0089f54`，与续跑身份不同；无活动运行器或审计进程，job/runner锁均未持有，原PID2616不再活动，旧progress的running不是当前状态。磁盘约100.35 GiB、MemAvailable4.69 GiB高于保护线，7份原工具/3份续跑工具、manifest/inventory/split/protocol及部分审计身份不变；旧1,487对结果与receipt共2,974份哈希全部保持一致。

实际有1,642份result文件，但新增155份中4对的result.json与receipt.json均为0字节，不能当作完整终态：`350-A-bug-13069733-13069761`、`350-A-bug-13284533-13284599`、`350-B-bug-4632118-4632388`、`350-B-bug-4632248-4632388`。读取新增JSON的初次只读探针因此报解析异常，随后逐文件诊断定位范围，未改原工具或数据。剩余可解析1,638对结果均有匹配receipt和冻结ID，其中1,369对记录标记配对复现、196参考失败、18测试不全、24仅buggy资源故障、23repair未复现、6协议不支持、2identical_pair；这些新增分类尚不是独立终审结论。相对原已审计1,487对，151份新增可解析终态的37,846份引用原始文件哈希全部一致（复现121、参考失败19、repair未复现4、资源5、测试不全2），仍需独立保存字节/判题审计。按可解析记录计算，未有完整可解析终态至少2,265对，含这4对空记录；不能沿用旧progress的剩余2,261。

中断案例`352-A-bug-12464382-12464395`保留attempt_001及200份部分文件，尚无result；计划repair 7/heldout 31，已存在26个test.json文件（并不代表26项完整有效，部分亦为空），最后文件在14:38:12附近。stderr仍空、session无stop/completion、root及全库审计无completion，不能确定关机或空文件根因、补写结果或宣称全库结束。当前4份空终态会使冻结续跑器拒绝读取，直接续跑不安全；一次性启动授权已使用，本轮未启动新审计/实验、删除/移动文件、改认证/VM/源码/测试/协议或调用模型。请求用户允许保留并隔离异常记录、审计有效数据和处理安全断点后按原协议继续，不重复有效终态。科研证据审查流程使本轮把“文件存在”“可解析且载荷哈希一致”“独立审计通过”分开，并阻止未过完整性门槛的启动。原始证据：[开机后完整性核对](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/post_boot_integrity_20261010T075020Z.json)、[保存的初次JSON诊断异常](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/post_boot_metadata_probe_error_20261010T0745Z.json)。下文关机状态已是历史；30分钟跟踪只读检查，不因连接恢复自动启动。

2026-10-10北京时间15:28–15:29只读核对确认Ubuntu2204已为`poweroff`、6 GiB，状态变更时间UTC06:52:36（北京时间14:52:36），运行虚拟机列表为空；SSH在banner阶段连接被拒绝。主机可用6.755 GiB，虚拟机日志确认PoweredOff，但不能据此确定关机发起者、OOM或原因。本轮未读取客机当前终态、stop/completion、最终审计或归档；14:18:31的1,487终态/剩余2,416及前缀681仅为历史快照。依科研证据审查要求不把关机当作完成证据；代理未关闭或启动VM、重启运行器、修改数据/认证/协议、删除文件或调用模型。需用户开启Ubuntu并告知，以便先核对保存记录、中断状态及旧哈希；一次性续跑授权已经使用，不因恢复连接自动重启或另开会话。30分钟只读跟踪保留，相同关机状态无变化时不重复提醒。原始证据：[本轮关机与连接核对](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/monitor_vm_poweroff_20261010T072844Z.json)。下文VM运行与SSH超时为较早历史状态。

2026-10-10北京时间14:47–14:49完成跟踪再次连接异常：SSH经10/15/20秒三个有界尝试均在banner阶段超时，当前客机进度、唯一续跑PID2616是否活动、资源及completion/审计/归档不可读。本机只读报告VM仍为running、6 GiB，主机可用3.92 GiB；VBox日志新增Guest seems to be unresponsive。这些不是OOM、进程崩溃或根因的证据。最近成功客机快照14:18:31确认实际终态1,487/剩余2,416、已重核前缀681、旧2,974份终态和工具哈希未变、stderr为空、资源安全；这些仅是历史值，不作本轮实时数值。按科研证据审查要求保留不确定性，未重复启动任务、改变VM/认证/协议、删文件或调用模型。需用户检查Ubuntu窗口是否响应及手动SSH能否连接，避免强制关机或重启可能仍活动的实验；30分钟跟踪继续，连接恢复先核对原会话，不自行重启，同一故障无新信息时不重复通知。 原始证据：[本轮连接失败与主机诊断](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/monitor_check_failed_20261010T064954Z.json)。下文14:00–14:18正常运行是较早快照，不代表当前可读或已完成。

日期：2026-10-09。本轮针对“全库全部可以开始实验了”核对实际状态；不把全库盘点、基线复现、FC准入和模型成绩混为一谈。

2026-10-10北京时间14:00–14:08恢复并安全续跑：用户再次要求`continue`后，SSH恢复；新客机boot身份已核对，代理未启动或改变VM。既有独立保存字节审计已完成并通过，0错误，范围partial为全部1,487对终态/剩余2,416对；其中配对复现1,248对、覆盖430簇，参考失败177、测试不全16、仅buggy资源故障19、repair未复现19、协议不支持6、identical_pair 2。双侧原生观测中新执行来源138,744、历史来源4,140，均为此前累积来源，审计未重跑C或调用模型。

续跑安全门全部通过：审计rows的1,487个唯一ID与实际终态完全一致，receipt与result哈希一致，原996份历史终态文件保持不变，7份原冻结工具和3份续跑/审计工具、manifest/inventory及启动前另核对的split/protocol身份未变，gcc/sed/diff版本一致，资源约101.09 GiB磁盘/4.94 GiB可用内存，无活动重复工作进程或完成标志。此前一条只读环境诊断错误假设`version`字段而中止；按实际冻结`stdout`首行读取后安全门通过，不改原工具、协议或结果，诊断错误单独保留。

依已获一次性授权，14:07:34仅启动新会话`/home/vboxuser/cfb2/resume_20261010_v1`，唯一PID2616，沿用冻结运行器/原资源限制及单进程锁；旧会话、审计、所有attempt和结果保留，不再另开会话或重复启动。14:08:43启动核验确认身份与工具正确，已保存全部1,487对结果/receipt共2,974份哈希快照且与安全门一致，stderr为空，无stop或completion，根分区约101.09 GiB、MemAvailable4.79 GiB。当前仍在校验并跳过既有记录：`runs/progress.json`前缀计数81不是实际总终态数，实际文件数仍1,487、实际剩余2,416；日志旧记录的`origin=new_execution`是其历史来源标签，不是本轮重复C执行。后续新增结果须以实际保存终态及新attempt核对，不把前缀重走当作样本增长。

继续复用该唯一会话；运行结束后现有编排执行全库独立审计及无删除归档，再核对root/session completion、3,903对终态、最终summary/manifest与SHA-256，完成前不宣布全库结束。此处1,248对只是已审计部分的buggy/reference基线复现，不是LLM修复成绩，也不证明FC全库准入。模型调用0，30分钟完成跟踪保持启用，正常过程安静，失败/资源风险或最终完成才通知。下文SSH不可读与等待审计/启动为较早历史状态，不作当前执行指令。

本轮证据：[通过的独立审计摘要](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/partial_audit_pass_20261010_v1/summary.json)（本机SHA与客机一致）、[全部安全门](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/pre_resume_pass_20261010T060526Z.json)、[诊断字段错误记录](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/pre_resume_probe_error_20261010T0603Z.json)、[唯一续跑启动记录](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/resume_launch_20261010_v1.json)、[启动身份与旧记录保全核验](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/resume_observed_20261010T060843Z.json)。科研证据审查流程使本轮先核对完整部分审计与身份，再续跑，并明确区分实际终态、前缀校验进度和模型成绩。

2026-10-10北京时间12:28–12:30继续核对：用户再次要求“继续”，但普通用户SSH经10/15/20秒三个有界连接尝试仍在banner阶段超时。VM仍显示运行、6 GiB，主机可用内存约4.00 GiB；VirtualBox近期日志同时保存客机无响应与随后alive、较长时钟滞后记录，不能据此确定故障根因或断言审计崩溃/OOM。未读取到当前客机summary、进度或资源；最近10:57:12的1,487对终态、剩余2,416对和PID2787活动只是历史快照。依科研证据审查流程保存不确定性，不重复启动审计或提前续跑，请用户确认Ubuntu窗口能否操作及手动SSH能否连接，避免强制关机/重启尚可能活动的审计。30分钟跟踪保留；本轮未改变VM、认证、协议或数据，新增C执行和模型调用均0。证据：[继续核对与连接诊断](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/monitor_check_failed_20261010T043032Z.json)。

2026-10-10北京时间11:19–11:24再次连接异常：普通用户SSH连续3次在banner阶段超时，未取得客机审计summary、进度或资源；本机VirtualBox仍显示Ubuntu2204为`running`、6 GiB，主机可用内存约2.96 GiB，日志尾部再次出现多条约60秒时钟追赶滞后。这些线索不足以判定内存耗尽、审计崩溃或根因。最近成功客机快照仍为10:57:12的唯一审计PID2787持续读取、stderr为空、summary缺失、1,487对终态/剩余2,416对及新续跑会话不存在；均为历史状态，不作11:24实时数值。依科研证据审查要求保留不确定性，审计通过前不启动续跑；请用户确认Ubuntu窗口能否响应，并尽可能关闭闲置主机应用，不强制关机或重启可能仍在活动的审计。本轮未改认证、VM、协议或数据，没有新增进程、C执行或模型调用。证据：[本轮再次超时与主机资源诊断](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/monitor_check_failed_20261010T032413Z.json)。下文10:56–10:57连接恢复为此前时点，不代表当前客机可读。

2026-10-10北京时间10:56–10:57连接恢复：用户再次要求“继续”后，普通用户SSH已可正常读取。原审计PID2787仍是唯一活动任务，读取字节及次数比10:20快照继续增加，stderr为空，尚无summary；只读看到它正在读取冻结数据集`230-A-bug-17823508-17823623`的保存测试文件，这不代表所有此前案例已完成审计。实际result文件数仍为1,487，与停止进度一致，剩余2,416对；新会话`resume_20261010_v1`仍不存在。根分区可用101.71 GiB、MemAvailable4.32 GiB，高于保护线。继续复用既有审计，不重复审计、重跑已完成案例或提前启动基线；通过后依已授权安全门续跑。此次未改变VM、认证、协议或数据，没有新增C执行或模型调用。证据：[连接恢复与活动审计快照](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/audit_progress_20261010T025712Z.json)。下文10:52客机不可读是此前时点，当前连接已恢复但审计仍未完成。

2026-10-10北京时间10:49–10:52监测异常：普通用户SSH连续3次在banner阶段超时；本机VirtualBox仍报告Ubuntu2204为`running`、配置6 GiB，不能据此证明客机可响应。最近虚拟机日志反复出现约60秒的时钟追赶滞后（尾部24条），主机可用内存约4.0 GiB；这些只是只读线索，尚不能确定SSH故障原因，更不能认定审计崩溃或内存耗尽。未取得本轮客机进度、审计summary或资源。最近成功读取仍为10:20:56：唯一审计PID2787有持续读取活动、stderr为空、summary缺失，终态1,487对/剩余2,416对，新续跑会话不存在；这些为历史快照，不是10:52实时数值。请用户检查Ubuntu窗口是否响应并反馈，先不要强制关机或重启，以免中断尚可能活动的审计。本轮未启动任何进程、改变VM/认证、删除数据或调用模型；审计未验证通过前不续跑。证据：[SSH持续超时与主机日志诊断](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/monitor_check_failed_20261010T025235Z.json)。

2026-10-10北京时间10:06–10:16恢复核对：用户再次要求“继续”，Ubuntu2204已运行且普通用户SSH恢复。实际保存结果仍为1,487/3,903对、剩余2,416对，运行器标记1,248对配对复现；无活动基线运行器，原996份结果/receipt、7份原冻结工具、3份续跑/审计工具及输入manifest哈希均符合此前身份，gcc/sed/diff版本未变。根分区可用约102 GiB、MemAvailable约4.4 GiB，高于保护线。已于10:08启动唯一独立保存字节审计PID2787，输出另存`/home/vboxuser/cfb2/audit_partial_20261010_v1`；截至10:16仍有正常读取活动、stderr为空，尚无summary，因此不能宣称1,487对已全部审计通过。此次审计不重跑C、不调用模型；已完成案例不重复执行。

本次“继续”用于恢复既有原生基线流程：新审计通过后允许一次以既有冻结续跑编排启动新会话`/home/vboxuser/cfb2/resume_20261010_v1`，不改协议、VM、工具、源码、测试或资源线。必须先核对partial审计通过、范围与当前全部终态一致、工具身份、资源及无重复运行器；沿用现有编排的终态哈希快照与单进程锁，跳过有效终态，保留未完成`attempt_001`并由冻结运行器另开尝试。若新审计失败或续跑再次失败，保留记录并报告，不自行再次重启。检测结束仍须完整独立审计及归档，不能以部分审计替代全库完成。

本轮证据：[SSH恢复及终态预检](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/preflight_20261010T020637Z.json)、[工具与环境身份](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/resume_tools_preflight_20261010_v1.json)、[独立审计启动](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/audit_launch_20261010_v1.json)、[审计进行中快照](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/audit_progress_20261010T021337Z.json)。下文关机与等待授权说明是此前历史时点，不作为当前连接或权限状态。

2026-10-10北京时间07:47监测：SSH连接被拒绝，本机只读核对Ubuntu2204为`poweroff`、无运行虚拟机，配置仍为6 GiB；本轮未读取客机实时进度或资源。最后成功读取为2026-10-09 21:33:48的1,487对终态、2,416对待处理及比较器异常停止，这些仅是历史快照，不作本轮实时结果。未启动或更改虚拟机、重启基线、修改认证、删除数据或调用模型；需要用户开启Ubuntu恢复只读核对。连接恢复不等于基线自动续跑。证据：[本轮连接失败及主机诊断](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/monitor_check_failed_20261009T234716Z.json)。

最新状态（北京时间12:29核对、12:30只读诊断）：原续跑进程已于12:27自动停止，原因`comparator_infrastructure_failure`，停在`329-B-bug-6006442-6006450`的heldout-input-pos7；无活动基线进程。本批已保存1,487对终态、剩余2,416对，运行器标记1,248对配对复现；最终独立审计和归档未完成。恢复前498对已独立审计（432对复现）；新增989对待终审。原996份终态文件与7份冻结工具哈希未变，磁盘可用102.24 GiB、可用内存4.43 GiB，并非当前资源保护线触发。仅用保留文件复核比较器已正常返回相等，但原始失败diff细节未落盘，不能确定最初超时/返回码/环境原因。**全部记录保留，未重启运行器；等待用户允许先审计并按原协议断点续跑。**本轮模型调用0，此前快照继续保留。

## 1. 核对发现

原批次`/home/vboxuser/cfb2`冻结3,903程序对/1,284簇，输入准备已完成，114对历史完整原生记录通过复用核验；其中仅13对已进入当前终态汇总，不能把114全部当成已处理。

UTC 02:00核对原PID67981已不存在，无替代基线进程；虚拟机处于新的启动会话。旧日志最后保存498对终态、剩余3,405对，原中断没有留下异常说明，不能诊断为内存耗尽。当前磁盘约108 GiB、可用内存约4.7 GiB，资源保护线不变。

已保存状态：配对复现432、参考失败44、测试不全7、仅错误程序资源故障8、repair未检出3、协议不支持4，共498对。这是原生基线状态，不是模型修复结果，完整全库基线尚未完成。

## 2. 独立审计发现与修正

原冻结审计器复核497对通过，`147-A-bug-1116758-1116767`出现比较不一致。逐一检查其10份相关保存输出，原GNU判题与重新比较保存字节均返回不等；错误来自独立portable检查器：末尾只有空格且没有LF的行被sed变为空字节后，它错误保留了一个空行。没有重新执行该C程序，没有改变其结果或标签。

另存通用字节检查器及审计器v2；完整保留原审计器和失败审计记录。修正适用于所有案例和三种原始规范化规则，不逐案例特判。Windows19项中15通过/4项原生检查跳过；Ubuntu19/19通过，包含636份GNU比较器通用字节对照及一个真实合成程序的恢复→不重复已完成案例→完整审计→归档检查。合成验证不增加Codeflaws样本量。

原冻结运行器、程序、测试、原始GNU比较器、资源限制和输入清单不变；修正的是独立审计实现，不放宽实验纳入或判题规则。新增续跑编排只调用原运行器的断点入口；完整旧终态先核对源码、结果、receipt及原始载荷哈希，再跳过；未完成尝试保留，另开尝试号。单进程锁仍有效。

恢复门槛已满足：新审计完整复核498对记录、55,056份原始双侧测试观测（本次新执行来源53,630、历史来源1,426），通过且0错误，状态计数与原运行器一致；其中432对配对复现，覆盖133簇。审计没有重新执行C。原批次恢复后先核验并跳过498对终态，已开始真正执行新增案例，原中断尝试保留。最终全库终态仍须经新审计器完整复核并归档；审计失败停止，不输出完成结论。已确认恢复前498对终态结果与receipt共996份哈希未变。

## 3. 为什么不能宣布全库FC模型就绪

能在gcc和原始测试下复现，不代表FC解析器、解释器、内部反向条件及理解任务均支持。当前FC v4新增留出样本仍为8例，已完成其64次调用；旧5例开发样本单列。完整源码可能含超出当前工具范围的多函数、宏、非int32、较大数组或复杂I/O，不能把它们伪装成相同形式化对照。

本轮新增API0，既有224/2,000次Codeflaws调用不变。原生基线可覆盖全库；正式FC模型实验只能在完整准入、隔离输入、冻结评分及剩余授权预算下运行。基线观察可用于覆盖诊断，不自动成为未调试确认性样本；旧30分钟归档监测仍暂停。

## 4. 证据与实现

- [本轮核对记录](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/preflight_v1.json)。
- [保留的原失败审计](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/audit_partial_v1/summary.json)、[498对通过审计](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/audit_partial_v2/summary.json)、[恢复启动记录](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/resume_start_v1/resume_launch_20261009_v1.json)、[恢复后进度及旧哈希核对](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/observed_resume_v1.json)。
- [原启动报告](codeflaws_independent_baseline_start_2026-10-08.md)、[原冻结协议](../workflow/codeflaws_independent_baseline_protocol_2026-10-08_v2.md)。
- [通用字节检查](../../03_experiments/prototypes/tool_adapters/codeflaws_byte_comparison_v2.py)、[审计修正版](../../03_experiments/prototypes/tool_adapters/audit_codeflaws_baseline_v2.py)、[续跑编排](../../03_experiments/prototypes/tool_adapters/resume_codeflaws_baseline_job.py)。

本轮使用“实验与结论审查”技能核对真实终态、原始字节和不同统计单位；因此发现审计问题时先阻止续跑，且没有把基线复现率当作FC模型表现。

## 5. 全库基线进度快照（北京时间2026-10-09 10:26）

唯一原生运行器PID6153正常运行：3,903对计划中，550对已有终态、剩余3,353对；运行器标记477对配对复现，覆盖144簇。550对是已处理记录数，不等于成功复现数；恢复前498对已独立审计，其中432对配对复现，恢复后的新增52对尚待最终独立审计，不把477对说成全部已终审。

标准错误日志为空，根分区可用107.23 GiB、可用内存4.14 GiB；恢复前498对结果与receipt共996份哈希、7份原冻结工具哈希全部未变。未发现全库完成标志，本轮模型调用0。继续原任务，不启动重复运行器；全库结束后由现有续跑编排执行完整独立审计和归档，失败时停止并保留记录。

可核验原始记录：[10:26进度快照](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/progress_20261009T022626Z.json)。这些统计仅是官方buggy/reference程序的原生基线检测，不是LLM修复成绩，也不代表全部程序已通过FC形式化准入。

## 6. 完成跟踪快照（北京时间2026-10-09 11:04）

本轮只读核对：与10:26快照相比新增361对终态，当前911/3,903对，剩余2,992对；其中运行器标记配对复现769、参考失败102、测试不全13、仅buggy资源故障12、repair未复现9、协议不支持6。配对复现覆盖267簇，306簇的全部成员已有终态；簇数不等于独立根因数。当前终态引用历史完整记录26对、本批新处理885对；累计观测中新执行来源95,340、历史来源2,856，均不是本轮重新执行次数。

PID6153仍为唯一续跑进程；实际result文件数911，与进度一致。原996份终态结果/receipt及7份冻结工具哈希均未变，stderr为空，无停止标志或最终完成标志，磁盘和内存高于保护线。已独立审计的范围仍为恢复前498对；本轮没有重跑案例、另启运行器、改变协议或调用模型。全库检测继续，结束后等待现有编排执行最终独立审计及归档。

原始证据：[11:04进度快照](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/progress_20261009T030435Z.json)。按用户要求仅结束或异常时反馈，本轮正常运行不发送例行进度通知。

## 7. 完成跟踪快照（北京时间2026-10-09 11:34:59）

只读核对相比上次新增359对终态，当前1,270/3,903对、剩余2,633对；运行器分类为配对复现1,073、参考失败140、测试不全16、仅buggy资源故障15、repair未复现18、协议不支持6、identical_pair 2，合计1,270。配对复现覆盖368簇，419簇全部成员已有终态；未将簇数当作独立根因数。累计历史完整记录复用38对，本批新处理1,232对；新执行来源观测120,510、历史来源3,652，均是累计来源分类，不是本轮执行次数。

实际result文件数1,270，与运行器进度一致。唯一PID6153正常，日志与进度均在更新，stderr为空，磁盘及内存高于15 GiB/2 GiB保护线。原996份终态文件与7份冻结工具哈希未变；根目录和续跑会话均无completion，最终审计summary及停止标志均不存在。独立审计范围仍为恢复前498对，其后的772对待终审。本轮未重跑程序、启动重复任务、改变判题/环境或调用模型API，继续等待原运行器自动完成检测、最终审计与归档。

原始证据：[11:34:59进度快照](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/progress_20261009T033459Z.json)。按用户要求，本轮正常运行不发送例行结果通知。

## 8. 比较器基础设施停止及只读诊断（北京时间2026-10-09 12:29–12:30）

12:29只读核对发现原PID6153已退出，job/runs/session进度均为stopped，session/stop.json记录12:27停止及`comparator_infrastructure_failure`。截至停止共有1,487对终态、剩余2,416对；运行器分类为配对复现1,248、参考失败177、测试不全16、仅buggy资源故障19、repair未复现19、协议不支持6、identical_pair 2，总计1,487；配对复现覆盖430簇，492簇全成员终态。历史完整记录复用45对、本批新处理1,442对，累计新执行来源观测138,744、历史来源4,140。实际result文件数与进度一致；恢复前996份结果/receipt和7份工具哈希均未变。磁盘102.24 GiB、MemAvailable4.43 GiB，均高于保护线；不能诊断为磁盘或内存不足。

停止案例`329-B-bug-6006442-6006450`的attempt_001及所有部分文件保留，尚无该案例的result.json；两侧编译和链接均成功。堆栈定位原冻结codeflaws_baseline.py的compare函数：diff运行基础设施错误、15秒超时或返回码非0/1均会触发该异常；函数抛异常前没有保存这次diff记录，因此无法从已存日志区分三种原因，不能把它当作普通输出不匹配或模型失败。

12:30仅对保存输出只读复核，不重跑C程序：该案例heldout-input-pos7/buggy的stdout.bin及normalized_stdout均为3字节，SHA-256与冻结标准输出相同；标准文件仍存在且哈希符合冻结清单。对这两个已存文件再次运行GNU diff返回0，耗时0.0176秒、无stderr，当前比较工具可工作。此证据不证明该案例完整通过，也不足以确定原始故障为何发生；参考侧及剩余测试未完成的记录不得补写为通过。

全库未完成，根目录/会话completion及最终audit summary均不存在；已独立审计范围仍仅恢复前498对，新增989对待审计。依完成跟踪约束，未清理、修改工具/判题/资源或自行重启；报告失败并请求是否允许先审计当前终态，再用原冻结协议断点续跑，不重复有效终态。正常完成跟踪保持有效，后续无变化不重复提醒。

原始证据：[停止快照](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/progress_20261009T042925Z.json)、[只读比较器诊断](../../03_experiments/results/codeflaws_baseline_resume_2026-10-09/comparator_failure_diagnostic_20261009T043054Z.json)。
