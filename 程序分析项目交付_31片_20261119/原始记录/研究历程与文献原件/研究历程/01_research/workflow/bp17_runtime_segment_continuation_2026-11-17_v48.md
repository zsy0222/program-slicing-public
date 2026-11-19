# BP17 第二次重置后续行 v48

v47 准备期间客机再次卡死（SSH banner 超时），VBoxManage 重置无效，最终 poweroff + 冷启动恢复，boot 变为 5f6e20c4。数据完整（24,000 评分、3,000 案例、28 片、1,264 未发；BP17-1477 排除记录与 99 例封存方案已定）。

v48 为冷启动后的新 boot 建立 runtime 绑定（previous_v29 链、runtime_segment=post_guest_reset2_20261117），其余沿用 v47：排除 BP17-1477、shard 30 按 99 例封存（封存脚本支持 exclude）、继续 1,264 条、封 31/32、shard 13、remote_finish。
