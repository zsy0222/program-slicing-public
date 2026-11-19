# BP17 收尾续行 v55

v54 的 FileExistsError 定位到排除块：`r.save(BATCH/'exclusions'/'BP17-1477.json', ...)` 仍是无条件独占写入，而该文件已在 v49 存在。v55 改为只读校验（`exclusion_record_present`），不再写；其余与 v54 相同：复用 v49 绑定、按 99 例封 30、继续 1,264 条、封 31/32、shard 13、remote_finish。
