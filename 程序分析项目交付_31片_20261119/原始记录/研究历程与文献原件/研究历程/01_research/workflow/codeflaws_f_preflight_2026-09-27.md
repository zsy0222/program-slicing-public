# Codeflaws 用于 F 形式化证据实验：预检记录

日期：2026-09-27  
状态：数据已取得，离线兼容性预检未通过；未构造正式批次，未进行模型 API 调用。  
适用范围：评估 Codeflaws 能否承载本项目 F0–F3 形式化证据对照。此记录不改写既有 F-development 结果。

## 1. 预检结论

当前 F 管线不能直接用于 Codeflaws。Codeflaws 的每个对象是一个独立 C 竞赛程序，buggy/reference 程序通过 stdin/stdout 与测试脚本交互；F-development 管线的语义切片和 Error Invariant 则来自本项目分析器对含断言的小型 C 程序的分析。两者之间缺少经验证的语义适配层。

已完成的首个固定开发试例 `71-A-bug-18359456-18359477` 中，原始 buggy 文件被 Error Invariant 分析器拒绝：解析错误位于 `int main(int argc, char *argv[])`。只在试验副本中将该签名改为无参数形式后，分析器又在局部数组声明处报解析错误。第二个预先指定的简单签名试例 `374-B-bug-5489458-5489463` 使用无参数 `main()`，分析器仍在全局数组声明处报解析错误。对清单中所有 6 个无参数 `main()` buggy 源码做了 20 秒限时探测，6/6 均在解析阶段退出，未生成 Map 或切片。以上试例均未修改 Codeflaws 原始数据。

全数据离线盘点进一步发现：本次官方压缩包内的缺陷清单有 3,903 行，3,903 行都能映射到 buggy C 源文件；清单描述字段含 defect 标签。3,903 个 buggy 源文件中未发现 C `assert(...)`。其中 3,847 个使用 `int main(int argc, char *argv[])` 签名。运行器 `run_seeded_suite.py` 的 `runtime_check` 会直接执行编译产物且不提供 Codeflaws 测试输入，因此也不能用于 Codeflaws 的 buggy/reference 基线。

清单首例 `71-A-bug-18359456-18359477` 还暴露了数据对的可复现性问题：本地快照中的 buggy 与 accepted 源码 SHA-256 完全相同（`5c00128143e58cf239d3d1264f57bbd07ac7ef32bdb2ab5e10e3dacf3b26392c`）；两者均通过 2 个 repair 输入，并均通过 10 个 held-out 输入。该条不能计为本项目的可复现 buggy/fixed 缺陷。该目录 `test-valid.sh` 为空，因此 held-out 输入/输出需要由自己的确定性 runner 执行，不能假定随包脚本完整。

## 2. 数据快照与来源

- 官方主页：<https://codeflaws.github.io/>，介绍页记载 3,902 个缺陷、7,436 个程序，并说明有 repair 与 held-out 测试。
- 官方仓库：<https://github.com/codeflaws/codeflaws>。README 描述每个缺陷目录包含 buggy 与 accepted C 文件、repair/validation 测试脚本、输入和预期输出，以及编译 Makefile；仓库当前 README 又称 4,085 个缺陷。
- 本次从官方主页提供的压缩包地址下载：<https://www.comp.nus.edu.sg/~release/codeflaws/codeflaws.tar.gz>。
- 本机 Ubuntu 路径：`/home/vboxuser/codeflaws_exp_20260927/codeflaws.tar.gz`；压缩包 SHA-256：`2673fc16fa05590c5c1171f5b633594713ae9207346a3d0ba4c4d8b2eea82b11`。`gzip -t` 和 `tar -tzf` 均成功。
- 解压后 `codeflaws/codeflaws-defect-detail-info.txt` 共 3,903 行；本次快照逐行检查均有对应 buggy 源文件。主页、仓库 README 与下载快照的缺陷数不一致，正式研究记录须报告本次快照的实测分母和来源版本，不能把网页数字当作当前清单计数。
- ICSE-C 2017 poster 将 Codeflaws 描述为 7,436 个程序、3,902 个缺陷，并报告 repair test suite 为 2–8 个、held-out suite 为 5–350 个（平均 40 个）：<https://codeflaws.github.io/icseposter.pdf>。这些是论文/海报中的数据集描述，不是本项目实测统计。

## 3. 与 F0–F3 的映射条件

若后续能构造并验证适配器，F 组的计划对照应保持原有增量：

| 条件 | 计划输入 | 必须保持的比较关系 |
|---|---|---|
| F0 | buggy 源码 + 固定 repair 测试上的统一失败摘要 | 基线 |
| F1 | F0 + 同一分析器实际生成的语义切片 | F0/F1 只差切片证据 |
| F2 | F1 + 最终轮次 EI 原始谓词及必要分区元数据 | F1/F2 只增加形式化状态证据 |
| F3 | F1 + 对 F2 同一谓词的确定性受控自然语言表示 | F2/F3 只差表达形式 |

Codeflaws 的 accepted 源码、developer diff、held-out 输入与输出、参考答案及标签只用于独立评估，不进入任何模型任务。理解与修复任务分别构造、相互无历史上下文。分析器只由工具运行；不使用 GPT 对逐案例源码或分析产物进行解释、补全、筛选或打分。若适配器无法产生与原 F 含义一致的语义切片及 EI，则不得将替代的动态切片、测试轨迹或人工规则称为 F1/F2/F3。

## 4. 批次规模与调用预算（仅为适配成功后的计划）

目标总规模暂按 50 个独立缺陷设计，其中 5 个仅用于离线管线/提示词开发，另外 45 个作为未参与开发的确认性案例。每个案例 × 4 条件 × 2 个独立任务 × 3 次重复，完整计划为 1,200 次请求（开发 120 次、确认性 1,080 次）。硬上限为 2,000 次，API 错误和重试也计入上限；运行器必须在预算耗尽时停止。未经新一轮预检与协议冻结，不对同一开发集追加调用，不用确认性结果调提示词。

用户已明确授权将筛选入组的 Codeflaws 数据发送给 DeepSeek，硬上限为 2,000 次；当前实际调用数为 0。只有当下述兼容性门槛通过、逐案例输入审计完成并冻结批次后，才开始这项已授权范围内的调用。

## 5. 解除阻塞所需的离线工作

1. 为候选案例建立不依赖模型结果的统一执行器：按官方 Makefile/CFLAGS 编译 buggy 与 accepted 程序；使用官方 repair tests 检查 buggy 确有失败、accepted 全通过；单独使用官方 validation/held-out 脚本核对 accepted，并保存实际执行数、退出码、失败/错误/跳过数和输出比较结果。
2. 检查分析器源代码和语法支持，确定它能否通过保真转换或受控 harness 分析实际 Codeflaws 逻辑。转换不得静默删掉输入、数组、循环、函数参数或控制流；每项改写须有语义等价证据与源位置映射。
3. 为分析器构造失败性质的方式必须预先定义。不能仅把一个测试期望值硬编码成模型可见的“答案”，也不能将测试输出断言误称为原分析器语义切片或 EI。若必须注入断言，应证明它对测试输入和被分析状态的约束、证明 buggy/reference 双侧运行行为可解释，并把该协议单独命名为新的 F-Codeflaws 版本。
4. 在 5 个开发案例上检验转换、分析终止、完整最终 Map、切片产物、行号映射与 F2/F3 谓词往返；逐例保留失败。达到预先设定的覆盖阈值后，再用确定性、分层且不看模型结果的规则选出 45 个确认性案例，提交最终候选清单哈希与排除原因。
5. 冻结任务 JSON、提示词、API 模型配置、重试规则、理解评分、补丁应用规则、repair tests 与 held-out 验证命令后，再执行发送前泄漏审计和预算审计。

若第 2 或第 3 步不能保持原 F 的操作定义，应停止 Codeflaws 上的正式 F0–F3 试验，改选适合原分析器的 C 数据，或明确提出独立的 F-Codeflaws 新研究问题与新协议；不能为了得到 50 个样本而降低证据有效性标准。

## 6. 本次执行记录

- Ubuntu 工具链：GCC 11.4.0、Python 3.10.12、GNU make 4.3；可找到 `z3`。已有 Error Invariant 程序为 `/home/vboxuser/error-invariants-work/error_inv/Main.native`。
- 官方压缩包：253 MB；下载哈希如上，gzip 完整性通过。
- 解压目录：`/home/vboxuser/codeflaws_exp_20260927/codeflaws/`。
- 兼容性试例：`71-A-bug-18359456-18359477`，清单首例，作为开发试例。
- 原始源代码分析结果：解析错误，`main(argc, argv)` 不被该工具当前解析器接受。
- 仅对试验副本修改 `main` 签名后：继续在数组声明处解析失败；未获得最终 EI Map/语义切片。
- 第二试例 `374-B-bug-5489458-5489463`：无参数 `main()` 仍因全局数组声明解析失败；不是只需规范化入口函数签名即可解决。
- 其余无参数入口源码的有界覆盖探测：6/6 解析失败；最终 Map=0、语义切片=0、`the_end : true`=0。
- 首例两份源码逐字节相同；buggy/reference 均通过 2 个 repair 和 10 个 held-out 输入输出对。`test-valid.sh` 文件为空；held-out 检查需单独的确定性 runner。
- 全数据断言扫描：3,903/3,903 个 buggy 源文件均无 `assert(...)`。
- 模型 API 请求：0。

## 7. 参考文献

Tan, S. H., Yi, J., Yulis, Mechtaev, S., & Roychoudhury, A. *Codeflaws: A Programming Competition Benchmark for Evaluating Automated Program Repair Tools*. 2017 IEEE/ACM 39th International Conference on Software Engineering Companion, 180–182. 官方仓库提供 BibTeX：<https://github.com/codeflaws/codeflaws>。
