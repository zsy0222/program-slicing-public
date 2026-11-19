# BP17 bc19 队列 runtime 段续行 v25

2026-11-17 07:55 客机被 unattended-upgrades 自动安装 libc6 2.35-0ubuntu3.15（libc.so.6 与 ld-linux 哈希变化；gcc/sed/diff/内核未变）。v24 准备在旧绑定上被守卫以 `runtime_changed` 拒绝，未发任何请求。已有 23,324 份评分全部产生于升级前；升级发生在 v23 停止（03:22）之后。

用户选择接受新 runtime 作为独立最后段。v25 建立新的 runtime 绑定：新 guard 仅把环境基准换成本次 libc/ld 哈希，保留对 v5/v7/v13 绑定、journal、boot 和科学 manifest 的全部链式校验；新请求仍为 1,938 条（2 次传输恢复 + 1,936 条未发）。BP17-0787 首个 wave 在旧 libc 下评分、第二个 wave 在新 libc 下，标记为跨 runtime 混合案例并从比较中排除。

现有 23,324 评分不重跑；新评分单列为 post-libc 段。不修改客机系统（未禁用自动更新），任何后续环境变化由守卫再次拦截。
