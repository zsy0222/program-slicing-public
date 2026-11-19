# BP17 guest-reset runtime 段续行 v29

客机在 09:27 内核升级重启后卡死（v28 准备时 SSH banner 超时），10:03 通过 VBoxManage 硬重置恢复，boot 变为 01f11f4d。数据检查点不变：23,440 槽位、23,436 评分、2,929 案例、28 片、1,824 条未发；4 份 wave 5861 回答已保存未评价。

v29 建立新 boot 的 runtime 绑定（previous_v26 链、runtime_segment=post_guest_reset_20261117），复用同一 guard 语义与全部旧绑定/journal 校验；客机准备继续允许 4 个 pending 残留目录；评价 wave 5861 后继续 1,824 条未发送任务，封 30–32 片，shard 13 混合恢复，remote_finish。无新请求额度变化。
