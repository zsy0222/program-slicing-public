# BP17 收尾续行 v37

v36 的 shard 30 封存被客机拒绝：v32 中断留下的 `shard_0030` 意图目录/归档已存在（`one_shot_shard_no_restart`），且客机审计发现 `duplicate_scored_job`——v32 保留的 `*__partial_5861` 目录仍在 cohorts 树内，被审计扫描到与新区块重复。

v37 在客机准备阶段把 `*__partial_5861` 目录移到 cohorts 树外的 `bp17_partial_5861_preserved_20261117`，并把空的 `shard_0030` 目录/归档改名为 `*__failed_v32_20261117` 保留；随后补封 30、继续 1,264 条、封 31/32、shard 13 混合恢复、remote_finish。无请求额度变化。
