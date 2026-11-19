# BP17 kernel runtime 段续行 v28

v27 的复用绑定步骤成功写出本地/客机绑定副本，但调用顺序写错（`bounded_process` 少了 command 参数）抛 TypeError；未发模型请求。v28 修正该调用，其余与 v27 相同：复用 v26 绑定与 guard，客机准备允许 4 个 pending 残留目录，评价 wave 5861 的 4 份已保存回答，继续 1,824 条未发送，封 30–32 片，shard 13 混合恢复，remote_finish。
