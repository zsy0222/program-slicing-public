# BP17 收尾：排除 BP17-1477，按 99 例封 shard 30

用户选择不重跑 2 个损坏任务的 C 评价，改为排除 BP17-1477：该案例 8 个任务中 6 个有效、2 个（BP2/repair、BP3/repair）因 09:27 重启截断而无效。v45 写排除记录 `batch_v1/exclusions/BP17-1477.json`，shard 30 按 99 例封存（`excluded_cases`/`complete_cases=99`），随后继续 1,264 条未发送、封 31/32、shard 13、remote_finish。分析时 BP17-1477 与 BP17-0431、BP17-0787 一样单独标注。
