# BP17 kernel runtime 段续行 v27

v26 已成功建立新 boot（3ea7d465）的 runtime 绑定并通过 status（binding `c9f827ab…`），随后客机准备在 `exact9872_evaluated_guest_tasks` 处被拒：v25 在 wave 5861 评价中途随客机重启，客机留下了部分任务目录（含 wave 5861 的 4 个待评价任务），与 23,436 份已评分集合不等。

v27 复用 v26 绑定与 guard（不再部署），只在客机准备里把 4 个 pending 任务的目录排除出精确集合、允许其残留；评价 wave 5861 时桥会覆盖这些目录。其余与 v26 相同：评价 4 份已保存回答，继续 1,824 条未发送，封 30–32 片，shard 13 混合恢复，remote_finish。旧 v26 记录保留；无新请求额度变化。
