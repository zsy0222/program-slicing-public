# BP17 收尾续行 v54

v53 的停止原因不是封片：排除记录 `exclusions/BP17-1477.json` 已在 v49 写入，v53 用独占方式重写时抛 FileExistsError。v54 改为幂等写入（存在则校验后跳过），其余与 v53 相同：复用 v49 绑定、清理残留 shard_0030、按 99 例封 30、继续 1,264 条、封 31/32、shard 13、remote_finish。客机已稳定运行 10 小时以上。
