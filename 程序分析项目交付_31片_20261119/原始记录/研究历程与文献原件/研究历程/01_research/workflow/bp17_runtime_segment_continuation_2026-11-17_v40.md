# BP17 候选评价更正续行 v40

v39 客机准备在核验损坏任务时失败：payload 的 scores 仍包含 2 个已改名的任务（主机端补丁未落到实际 payload 行）。v40 修正 payload：scores 排除 2 个损坏任务、pending 纳入它们，客机断言改为 verified_scores==SCORED-2、pending==2；其余与 v39 相同（更正评价、更新 wave 5860/案例回执、封 30、继续 1,264 条、封 31/32、shard 13、remote_finish）。
