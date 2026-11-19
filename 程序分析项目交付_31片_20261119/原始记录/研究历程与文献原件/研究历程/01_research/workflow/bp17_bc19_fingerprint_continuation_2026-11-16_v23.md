# BP17 402 恢复续行 v23

v22 的客机准备完整通过，随后主机在构造 `saved_answer_selection` 时对 4 个 402 失败任务查 `answers[k]` 抛 KeyError——这 4 个任务没有保存回答，选择集本应为空。

v23 只把该选择集从 `reserved-set(scores)` 改为 `set(answers)-set(scores)`（当前为空），其余与 v22 相同。v22 客机结果与全部记录保留；授权与预算不变。
