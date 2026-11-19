# OpenAI 官方指南对照与工作流更新

核对时间：2026-09-12。这里更新的是 Codex 的科研协作指令和项目技能，未迁移实验模型或改变历史实验提示词。官方指南用于组织代理工作；本项目的研究假设和统计设计由科研问题决定。

## 官方依据与实际采用方式

| 官方来源 | 采用的建议 | 本项目落实 |
| --- | --- | --- |
| [Rethinking skills and prompts for GPT-6 Astra，2026-09-11](https://learn.chatgpt.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) | 审查旧提示、减少冗余，准确限定 skill 适用范围，按任务加载细节 | 清理过时 Phase 和未证明保证；两项技能分工明确，不在每个任务强制加载全部研究资料 |
| [AGENTS.md 指南](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | 项目与目录级指令分层，保持规则简短且可执行 | 新增根 AGENTS，paper 层只保留文献写作要求；详细研究内容放在普通文档 |
| [Build skills](https://learn.chatgpt.com/docs/build-skills) | 精准描述与渐进式加载；项目技能可放 `.agents/skills` | 更新文献整理技能，新增实验记录审查技能；避免把庞大研究计划塞进常驻技能描述 |
| [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) | 明确目标、数据和判定，保存记录，对相关环节做任务化评估；自动评分应校准 | 新增离线证据汇总器；区分触发/回归；保留重复、缺失及冲突信息；理解任务需独立评分规则 |
| [当前模型提示指导](https://developers.openai.com/api/docs/guides/latest-model) | 保留任务边界与完成条件，避免多余确认及无关重复测试 | 延续既有授权；先完成可独立推进的工作；日常文档更新不重跑全部基准 |

官方评估页面当前同时提示 Evals 平台的退役安排。本项目采用其评估原则，并继续使用本地、服务商无关的验证记录；本次没有新增托管 Evals 平台依赖。

## 原工作流与 skill 的具体问题

- 根目录此前没有统一科研 AGENTS；paper/AGENTS 固定在 7 月旧 Phase，可能让后续任务回到过时研究目标。
- 文献 skill 的原件在本地历史归档区，项目 `.agents/` 为空。不能因为磁盘中有 SKILL.md，就声称它已经在项目中自动发现并启用。
- 原文献技能默认不存在的 `data/raw-pdfs/`，强制生成 Excel/CSV/多份报告，要求先交三篇再等审批，并预设从 `.env.local` 读密钥。这些固定步骤并不适用于所有文献整理任务。
- 旧科研流程将“静态前向扩展”等计划写作通用既成流程。新入口明确实现状态，保留历史记录。

## 更新后的组织

- 根 `AGENTS.md`：短入口、证据口径、针对性验证和已有授权的使用方式。
- `paper/AGENTS.md`：文献引用、来源区分与历史材料的解释规则。
- `01_research/workflow/research_workflow.md`：按任务查阅的完整科研流程。
- `01_research/claim_evidence_ledger.md`：主张与原始证据对应关系。
- `.agents/skills/literature-matrix-builder/SKILL.md`：现有文献技能的项目适配版。
- `.agents/skills/research-evidence-audit/SKILL.md`：针对实验结果与结论的审查技能。

技能仅在本项目范围内安装；原归档版本和用户全局技能保留。没有添加与本项目无关的插件，也没有把技能更新变成更换 DeepSeek/GLM 的理由。

## 验证与状态

部署完成：两个技能均已通过官方 `quick_validate.py` 检查，安装到项目 `.agents/skills/`，并核对安装文件与已校验版本的 SHA-256 一致。原归档 skill 保留，暂存版本位于 `90_local_only/skill_staging_2026-09-12/`。

人工检查了描述边界：文献对齐、批量阅读应匹配文献技能；实验评价、结论审查应匹配证据技能；SSH 配置、普通格式修改不应仅因发生在科研项目中触发整套审查。此为描述与场景检查，不是独立模型的运行时选用评测。按官方说明 Codex 会检测技能变化；若界面未显示，可重新加载客户端。

科研更新的验收以新旧证据能否对应、文档链接是否可达和相关离线检查为准。审查器测试通过不等于整个历史实验套件通过；已发现的旧解析器路径测试失败见项目审查报告。
