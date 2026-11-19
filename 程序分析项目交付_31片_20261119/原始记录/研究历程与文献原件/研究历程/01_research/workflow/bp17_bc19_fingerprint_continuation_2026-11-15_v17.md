# BP17 bc19 队列续行与 shard 13 混合身份封片 v17

v16 在完成前 1,300 个案例后、封存 shard 13 时停止：客机字节审计对 BP17-0431 的 4 份 bc19 回答仍按冻结的 e72d pin 校验，返回 `model_identity_changed`。该案例的 4 份 e72d 保存回答与 4 份 bc19 首次回答均已评分并标记为混合案例；失败发生在审计阶段，未写入 completion，客机只留下 `shard_0013/intent.json`（SHA `ae84e37d…`）和空归档目录。

本协议续行：从案例 1300（序号 1301）继续发送剩余 1,858 个案例、14,864 条 first_attempt；shard 14–32 按原规则封存。shard 13 在队列完成后单独以“混合身份恢复封片”处理：保留失败 intent 为 `intent_v16_failed.json`，写入新 intent，仅在字节审计的身份比较中允许 BP17-0431 的 4 个已知 bc19 任务使用 bc19 pin，其余 796 个任务仍要求 e72d；归档内容与 completion 结构保持原格式，并显式记录混合例外。之后执行原 `remote_finish` 与最终保全。

身份、绑定与 guard 沿用 v13（boot `ecaef714…`）；科学条件、bc19 授权、pin、预算、混合案例排除政策不变。v16 会话、账本与客机现场全部保留。任何失败停止并保留，不自动重试。
