# BP17 402 恢复续行 v21

v20 准备已完整通过客机核验并写出 guest result/completion：16,592 评分、12 归档、959,291 载荷、3,158 原生对、3,903 基线；但主机断言仍要求 `pending_never_evaluated==0`，而当前 pending 是 4 个 402 失败任务（客机目录确实不存在），guest 返回 4，主机因此拒绝并写了 preparation_stop。数据与客机结果无误。

v21 只把该断言改为 4（与 payload 的 4 个待恢复任务一致），另存会话与准备目录；v20 的 guest result/completion 和全部记录保留。其余与 v20 完全相同：4 次 402 恢复、wave 4151、案例 2076–3158、21–32 片、shard 13 混合恢复、remote_finish。授权与预算（8,672）不变。
