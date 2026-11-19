# BP17 候选评价更正续行 v38

2026-11-17 09:27 客机重启把 BP17-1477 的 2 个任务（BP2/repair、BP3/repair）的候选评价写坏：candidate/evaluation.json、compilation.json 与全部 test 输出均 0 字节，但 wave 5860 已按 test_failed 记分。用户批准重跑这 2 个任务的候选评价。

v38 在补封 shard 30 前：把 2 个损坏任务目录改名为 `*__corrupt_eval_20261117` 保留，用已保存的 2 份回答重新评价（2 次 C 执行，无模型调用），更新 wave 5860 与案例回执（原件另存于会话），然后封 30、继续 1,264 条、封 31/32、shard 13、remote_finish。
