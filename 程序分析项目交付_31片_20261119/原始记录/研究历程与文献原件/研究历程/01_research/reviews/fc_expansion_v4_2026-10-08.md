# FC v4扩样：8个新独立缺陷、64次调用完成

日期：2026-10-08。用户要求加大样本量，本轮另开未暴露簇扩样协议，完成8个新独立缺陷的四组理解/修复实验。旧5个开发缺陷单列，不能将两批合并成13例确认性成绩。**50例目标未达到；主要比较未显示形式证据或中文表达的显著增量收益。**

## 1. 扩样方式与真实样本数

[协议](../workflow/fc_v4_expansion_protocol_2026-10-08.md)先于新原生结果冻结。原Codeflaws快照3,903对、1,284个问题/源码相似性簇；排除已暴露516簇，剩余768簇。对其全部2,344份错误源码只做原解析器支持性检查，不读取参考修复、测试或模型成绩。94份源码受支持，覆盖51个独立簇；每簇按固定哈希选唯一代表，冻结顺序及源码，不在代表准入失败后换另一份。

51例全部完成准入：8通过、43拒绝、待完成0。入组ID：FCV4-008/010/015/016/023/028/034/036。入组者完成676次buggy/reference执行、338次全测试解释器一致性检查、8份自动形式条件和17道新输入预测题验证。两端独立审计还复核了包含拒绝案例在内的3,618份保存的双侧测试观测；这些次数不是独立bug数或模型修复成绩。

| 准入拒绝原因（原始分类） | 数量 |
| --- | ---: |
| full_test_interpreter_differential_failed | 18 |
| no_nonconstant_internal_backward_condition | 5 |
| reference_not_all_tests_pass | 4 |
| expected_output_arity_or_int32 | 4 |
| integer_whitespace_stdio_only | 3 |
| expected_format_not_aligned | 2 |
| unsupported_official_comparator | 2 |
| only_int32_and_fixed_int32_arrays_supported | 1 |
| invalid_or_deep_term | 1 |
| array_bound_256 | 1 |
| unsupported_C_node | 1 |
| unsupported_preprocessor_directive | 1 |

拒绝不等于数据集bug不可复现；特别是解释器不一致、输出/语法不支持和非平凡条件缺失，属于本FC管线的适用范围或一致性门槛。本轮没有放宽分析器、逐案例补证、替换失败代表或按模型成功率筛选。

## 2. 模型输入与执行

完整错误源码、失败信息与编辑权限相同：FC0仅共同信息；FC1增加静态依赖行标记；FC2在FC1上增加固定失败路径后缀形式条件AST；FC3增加同一AST确定性生成的受控中文，不同时提供AST。沿用v4明文输入、完整文件JSON提交及原始测试比较器；分析、提示、评分和候选范围的原工具哈希不变。新代码仅做取样、通用编排与独立审计。

8例×4组×理解/修复2个隔离任务×1次生成＝64次调用，全部返回。模型`deepseek-flash`，指纹`aeb56401ca74e127821c4f9126dcb669`；参数继承v4：temperature 0、thinking disabled、max_tokens 4096、JSON object、不流式。首请求锁定非空指纹，其后最多4并发；API错误、重试、反馈均0。历史160次先独立对账，本轮后累计224/2,000次，224个任务和回答ID均唯一。别名/指纹不保证不可见后端永久不变。

修复不接收理解答案、参考源码、私有预测答案或held-out测试。GPT/Codex仅开发运行通用工具、读取记录和汇总，没有逐案例解题、补写证据、修改模型补丁或使用另一个模型评分。请求内保留旧v4接口标识以锁定字节，新取样与执行身份由本轮独立清单定义，不把旧开发协议的元数据当作新批次分组。

## 3. 结果与限制

每例有1–3道原生核对的新输入题，共17题；主指标为先按缺陷计算准确率再平均，不能把题目数当样本量。

| 组别 | 理解正确题数/计划题数 | 缺陷宏平均准确率 | repair全过/8 | held-out全过/8 | 两套全部通过/8 |
| --- | ---: | ---: | ---: | ---: | ---: |
| FC0：源码及失败 | 9/17 | 50.0% | 2 | 2 | 2 |
| FC1：增加依赖行标记 | 5/17 | 33.3% | 3 | 3 | 3 |
| FC2：增加形式AST | 4/17 | 20.8% | 2 | 2 | 2 |
| FC3：同义受控中文 | 4/17 | 20.8% | 2 | 2 | 2 |

32份理解回答均通过格式检查；评分只核对原错误程序的完整整数输出序列，不评价解释或因果理解。32份修复中1份范围拒绝、未编译/测试；其余31份编译后执行全部指定repair与held-out，共1,313次候选测试（repair 211、held-out 1,102），没有遇首个失败即停。拒绝仍保留在每组8次计划分母。

9份候选全部原始测试通过，但仅涉及3/8个不同缺陷（FCV4-028/034/036）。18份候选词法token未实质改变且测试失败，4份已改动但测试失败，另1份范围拒绝；没有编译失败、缺失回答或基础设施失败。词法未改动不是一般语义等价证明，测试全部通过也不是全输入正确性证明。

预定主要比较FC2−FC1：理解宏平均及修复率均下降12.5个百分点，均为0个簇正向、1个负向、7个持平，双侧精确符号检验p=1。FC3−FC2两指标均8个簇持平，p=1。四项主要比较Holm校正后均p=1。次要FC1−FC0理解下降16.7个百分点（p=0.5），修复提高12.5个百分点（p=1）。因此不能根据3比2声称切片显著有效，也不能从8例证明形式方法普遍无效。

实际新样本8例，较旧5例开发试跑扩大了单批独立样本，但仍远少于50例；项目v4覆盖13个不同缺陷仅是覆盖数，不是可合并的确认性统计。结论仅适用于当前int32/有限数组/单main/stdio及完整FC准入子总体，不是原论文Error Invariant、全部Codeflaws、其他模型或J组结果。若继续追求50例，需要另开工具覆盖扩展的开发协议，不能重判本批或用重复调用充样本。

## 4. 验证、保存与实现入口

源码筛选/准入工具75项检查在两端通过；最终运行保护69项检查在两端通过（日志中的模拟停止不是实际API故障）。Ubuntu与本机独立审计的51例准入、64项模型任务、全部1,313测试及统计JSON完全一致，错误0。归档13,201份准入载荷、5,512份评价载荷全部SHA-256核验。旧v3的20,061份记录、旧v4试跑223份记录及其5,394份原生载荷未变。

Windows首次准入解包受沙盒路径校验权限限制，原失败目录`90_local_only/fc4x1`保留；正常用户上下文在新短路径`90_local_only/fc4xa1`解包同一归档，未改ACL、认证或数据，没有重跑C或API。末次Ubuntu约111GiB磁盘、4.5GiB内存可用，无扩样运行残留进程；旧批次、检出、日志、归档均保留。

- [完成清单](../../03_experiments/results/fc_expansion_v4_2026-10-08/completion_v1.json)、[本机模型审计及统计](../../03_experiments/results/fc_expansion_v4_2026-10-08/local_model_audit_v1/summary.json)、[逐项结果](../../03_experiments/results/fc_expansion_v4_2026-10-08/local_model_audit_v1/rows.json)。
- [执行冻结清单](../../03_experiments/results/fc_expansion_v4_2026-10-08/batch_v1/execution_manifest.json)、[调用台账](../../03_experiments/results/fc_expansion_v4_2026-10-08/batch_v1/attempt_ledger.jsonl)、[累计调用复核](../../03_experiments/results/fc_expansion_v4_2026-10-08/call_reconciliation_final_v1.json)。
- [本机准入审计](../../03_experiments/results/fc_expansion_v4_2026-10-08/local_admission_audit_v1/summary.json)、[准入原始记录](../../90_local_only/fc4xa1/records/admission_v1/summary.json)、[原生评价](../../90_local_only/fc4xe1/records/summary.json)、[Ubuntu模型审计](../../90_local_only/fc4xe1/records/independent_audit_v1/summary.json)。
- [源码冻结](../../90_local_only/fc4xf1/manifest.json)、[取样及准入实现](../../03_experiments/prototypes/tool_adapters/expand_fc_v4.py)、[准入审计](../../03_experiments/prototypes/tool_adapters/audit_fc_expand_v4.py)、[通用运行器](../../03_experiments/prototypes/tool_adapters/run_fc_expansion_v4.py)、[模型独立审计](../../03_experiments/prototypes/tool_adapters/audit_fc_expansion_model_v4.py)、[保护测试](../../03_experiments/prototypes/tool_adapters/test_run_fc_expansion_v4.py)。

模型队列SHA-256：`49622b4b2d1236c6365dc13bd80dd98ef5d52d77bc7d55be04c857154bdd35f6`。
准入归档：`45a65a8cd4a8b3327af3fdada51954a5a5b3d5ecbd2ba6a0eec21b71344f9364`。
评价归档：`20d44291916ba27a34f77a1f7d5a86d20560ef6ad345fa7d32156d81f92d6d96`。
本轮usage为输入84,610、输出10,285、合计94,895 token；没有扩展授权预算或估计费用。
