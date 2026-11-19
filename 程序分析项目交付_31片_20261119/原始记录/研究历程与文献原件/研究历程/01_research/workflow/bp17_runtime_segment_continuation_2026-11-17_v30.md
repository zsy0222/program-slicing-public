# BP17 部分评价清理续行 v30

v29 的保存回答评价被桥以 `partial_or_duplicate_evaluation_refused` 拒绝：客机仍留有 v25 中断时的部分任务目录（wave 5861 的 4 个 pending）。v30 在客机准备阶段把这 4 个 pending 目录改名为 `*__partial_5861_20261117` 保留（不删除、不覆盖），并把 `__partial_5861` 排除出精确目录集合；随后正常评价 wave 5861 的 4 份已保存回答，继续 1,824 条未发送，封 30–32 片，shard 13 混合恢复，remote_finish。绑定/guard/额度不变。
