# BP17 收尾续行 v35

v34 的客机准备在 `waved_receipts_through_5860` 处被拒：GUEST 的 wave 回执边界仍是 v29 时的 5860/5861，而当前已到 6001。v35 只更新该边界为 6001/6002，其余与 v34 相同：复用 v29 绑定、补封 shard 30、从案例 3001 继续 1,264 条、封 31/32、shard 13 混合恢复、remote_finish。
