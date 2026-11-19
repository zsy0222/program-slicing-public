# BP17恢复连接后的完整前检回执保全 v3

沿用用户2026-10-21新boot/第8片新目录恢复及继续18864未发请求的许可。用户另明确要求断开重连网络，并在控制台报告enp0s3 UP/10.0.2.15后，SSH已实测恢复且授权boot未变。旧PID3400退出、候选锁空闲；其baseline_precheck.json通过，但完整g.precheck回执未通过SSH送达，不能推演补写为完整前检成功。

本版仅对旧保存字节重新读取核验，不重跑C、旧评分或模型，不重封前7片。新日志另存preparation_resume_20261021_v3与客机manual_restart_20261021_v5/durable_precheck_20261021_v3。直接调用冻结g.precheck，全部科学检查不变；只将其原生保全检查的输出重定向到本次新日志路径（原检查函数逐字不改，finally还原模块绑定），避免覆盖旧baseline_precheck.json。原marker与baseline文件核验前后SHA一致。

客机将完整result.json与completion.json先以独占创建保存，再向SSH打印；即使打印连接断开，完整回执仍可只读取回，不能重复启动未知活动进程。新marker绑定boot、PID/start ticks、UID、冻结guard SHA。主机从准备开始每15秒检查原2GiB/15GiB线，触线只停止经精确身份核对的本次precheck；原候选锁和主机transport锁保留。

旧6400请求/raw/回答/评分、800案例、79475旧主机文件、7旧归档和全部载荷、第8片87851载荷、3158私有输入/原生receipt与3903原生保全全部通过后，才完成原v5绑定/manifest，并另行单次调用既有冻结v5启动器。原启动器先验证第8片新目录归档，再发原18864未发任务；任何API/指纹/基础设施失败不自动重试，预算、源码、原测试/评分、资源线、开发/暴露扩展/40既有确认界限完全不变。
