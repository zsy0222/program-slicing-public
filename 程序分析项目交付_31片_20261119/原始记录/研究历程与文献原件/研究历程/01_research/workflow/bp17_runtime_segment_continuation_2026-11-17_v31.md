# BP17 部分评价清理续行 v31

v30 误用 deploy（v29 绑定已存在），在 `fresh_runtime_binding` 处立即失败，未发模型请求。v31 改为复用 v29 绑定（boot 01f11f4d，binding 5df0041a）并通过 status 校验；其余与 v30 相同：把 4 个 pending 残留目录改名保留，评价 wave 5861，继续 1,824 条未发送，封 30–32 片，shard 13 混合恢复，remote_finish。
