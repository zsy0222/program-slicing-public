# 首轮工具复现与试点实验记录

日期：2026-08-09  
目标：验证 Dimovski Error Invariants 原型在 Ubuntu 中可复现，并用三项 SV-COMP 试点检查其 Error Invariant 输出、可扩展性和输入适配边界。

## 可复现环境

- 平台：Ubuntu 22.04（VirtualBox）
- OPAM switch：OCaml 4.14.1
- 数值库：APRON 20160125、MLCUDDIDL 3.0.8、Zarith 1.14、OUnit 2.2.7
- 额外历史依赖：camllib 与 BDDAPRON，均来自原 INRIA/GForge 源的公开镜像；BDDAPRON 在 OPAM 主索引中已下线。
- 构建产物：`/home/vboxuser/error-invariants-work/error_inv/Main.native`

`artifacts/ErrorInvariants.tar.gz` 中的核心 `error_inv` 源码完整可用；可选的 `bug_assist_cmd_linux_64.tar.gz` 成员损坏，因此本实验没有使用该辅助二进制包。

为兼容 OCaml 4.14，历史 `camllib` 的字符串缓冲调用被替换为等价的 `Bytes` 调用，已移除运行时符号以标准库实现替代；BDDAPRON 的一处同类字符串调用也作了等价适配。这些改动只发生在外部历史依赖中，未改动 Error Invariants 算法和任何原始 SV-COMP 基准。

## 原作者样例验证

`tests/program1.c` 成功运行：

- `-single -domain polyhedra`：状态 0，耗时 0.001351 s。
- `-full -domain polyhedra`：状态 0，耗时 0.008418 s；第二轮收敛。
- 输出的 Error Invariant Map 在关键程序点给出 `-x+y == 1`，并删除与错误无关的 `z := z + 1` 语句。

这证明分析器已不仅是“成功编译”，而是能够完成其后向/前向闭环并产生错误不变式与程序切片。

## SV-COMP 试点结果

| 编号 | 原始基准 | 期望性质 | Error Invariants 输入 | 完整分析结果 | 结论 |
|---|---|---|---|---|---|
| SV01 | `loops-crafted-1/Mono5_1.c` | unsafe | `normalized/Mono5_1_errorinv.c` | 状态 0 | 成功定位至断言点 `z == 0`；循环和分支附近给出 `z >= 0` / `z >= 1` 等错误轨迹条件。 |
| SV02 | `loop-invgen/down.c` | safe | `normalized/down_errorinv.c` | 60 s 超时（迭代至第 79 轮） | 未收敛，不能据此给出安全性结论；已保存中间不变式轨迹。 |
| SV03 | `loop-lit/mine2017-ex4.8.c` | safe | `normalized/mine2017_ex4_8_errorinv.c` | 状态 0，0.010788 s | 两个断言点的 Error Invariant 为 `bottom`，与“违规不可达”的安全预期一致。 |

所有原始基准文件保持不变。`normalized/` 下文件只移除了前端不支持的 GCC 属性、头文件和 `__VERIFIER_*` 包装：

- SV01 将包装断言改为原型内置 `assert`，并把不会溢出的无符号常量路径映射为 `int`。
- SV02 把原始任意整数表示为 `main(int n)` 的输入参数。
- SV03 用原型的区间赋值 `b = [0,1]` 模拟每轮新鲜的布尔非确定选择。

## 证据与限制

- 原始运行输出保存在 `../outputs/error_invariants_pilot_2026-08-09/`。
- SV01 是当前可以进入“错误不变式解释和定位”下一阶段的首个真实用例。
- SV02 暴露了该原型在双循环安全证明上的收敛性风险；正式实验必须记录超时，而不能将其计为安全或失败。
- SV03 的归一化保留了断言安全性质，但不应被当作对原始验证器全部语法/位宽语义的完全替代验证。

## 人工确认点

在把这些数据写入论文的正式实验表之前，需要人工确认：是否接受 `benchmarks/pilot/normalized/` 的三项语义保持适配作为 Error Invariants 前端兼容层。建议接受 SV01 和 SV02；SV03 应在论文中明确说明“区间赋值模拟每轮布尔非确定性”。
