# Codeflaws—Fault_localyzer 兼容层设计（F-Codeflaws 预研）

日期：2026-09-27  
状态：设计与准入条件；尚未实现语义转换器，未运行正式批次，未调用模型 API。  
目的：判断并建立可审计的输入适配路线；不把源文件“改到能解析”误称为语义兼容。

后续增量（2026-10-07）：用户已选择独立 FC 协议，见 [FC-Codeflaws v1](fc_codeflaws_protocol_2026-10-07.md)。原始数据/AST/portable 双侧基线适配及 repair 输出规格绑定已实现；C 切片与内部状态约束分析尚未完成。下文为原设计记录，保留，不将目标接口冒充已实现功能。

## 1. 结论先行

Codeflaws 文件与 Fault_localyzer 的输入不是单纯的格式差异。分析器的 Menhir 语法允许标量 `int`/`unsigned int`、若干控制流、函数和断言；语法没有数组声明符或数组下标表达式。Codeflaws 中数组是常见核心数据结构，现有预检试例正是在数组处失败。删除数组、改写访问或只把 `main(argc, argv)` 改成 `main(void)`，可能改变程序状态空间和错误路径，不能作为兼容方案。

因此采取双层、失败关闭的兼容路线：

1. **F 原协议兼容子集**：只对可经 AST 证明处于分析器已有标量语言内、并且没有改变程序语义的案例做无损规范化。超出子集的一律 `unsupported`，不删特性、不进入正式样本分母的“成功覆盖”。
2. **F-Codeflaws 新协议**：为数组/输入输出型问题扩展分析器或构造测试驱动的抽象程序；必须单独命名、独立预注册和报告，不能把测试失败断言生成的 EI 叫作原始 Fault_localyzer EI，也不能把结果与原 F0–F3 混算。

若目标是尽快得到可解释、可复现的 50 个样本，先开发并评估第 1 路线的真实覆盖率；只有覆盖率不足且确有研究价值，才启动第 2 路线。当前不发起 DeepSeek 请求。

## 2. 分析器实际输入语言边界

根据 VM 中保留的 `error_inv/frontend/Parser.mly`、`Lexer.mll`：

- 可见结构：全局标量声明、少量预处理宏、函数（参数仅标量 int/unsigned int）、块、`if/else`、`while`、简化 `for`、赋值、算术/比较/逻辑、调用、`assert(expr)`。
- 词法器会忽略 `#include`、`extern` 行和部分限定符；忽略行不等于实现相应 C 语义。
- 不支持标准 C 数组声明/下标语法；未见对 Codeflaws stdin/stdout 测试框架的原生执行或规格导入接口。
- 工具接收的是待分析 C 程序并在断言处分析失败状态；Codeflaws 的 oracle 是一组输入—期望输出，不是源代码断言。

兼容工作必须同时解决：解析语言、抽象语义和失败规格来源。只解决第一项不能声称端到端兼容。

## 3. 适配组件及契约

### 3.1 `inventory`：原始输入清点

输入：冻结的 Codeflaws 压缩包、官方缺陷目录、buggy/reference 文件、Makefile、repair/validation 输入输出。  
输出：只读 manifest；每项记录原始路径、SHA-256、编译参数、测试数、入口函数、AST 特性、适配状态和排除原因。原始文件永不就地修改。

样本可复现准入：

- buggy 与 reference 源码哈希不同；
- 编译参数和测试执行方式可重建；
- repair tests：buggy 至少有一个确定失败，reference 全部通过；
- validation/held-out：reference 全部通过；记录执行、失败、错误、超时、跳过数；
- 环境错误与真实失败分开；无法满足者排除且保留原因。

### 3.2 `parse`：完整 C AST，而不是正则改写

采用固定版本 Clang/libclang 或同等完整 C 前端，保存 AST JSON、编译命令、前端版本和诊断。每个节点保留源文件偏移、行列、宏展开来源。禁止仅凭 regex 移除声明或参数。

### 3.3 `lower`：两种显式目标模式

**模式 S（原协议子集）**：只做无损语法规范化，例如统一函数声明写法、移除分析器确实不分析且不会改变被分析逻辑的头文件行；任何丢弃都要有语义论证。要求 lowering 前后在固定 repair 和 held-out 输入上与原始二进制逐输入输出等价；还需 AST 结构审计、变量映射及 source-map。遇到数组、指针、联合体、动态内存、未支持类型/运算/预处理分支即拒绝，不尝试“尽力删掉”。

**模式 E（扩展分析器）**：优先扩展分析器 AST 与抽象域以支持所需数组/内存语义；若范围过大，才研究有限数组标量化。仅当数组长度编译期常量、有界、访问范围可证明、无指针别名、无越界/未定义行为歧义时，可把 `a[0..N-1]` 映射到独立标量，并把常量下标直接映射到相应标量。动态下标须经 AST 生成条件分派，并保留边界条件和副作用顺序；若无法证明与 C 的整数、短路、求值顺序一致，拒绝案例。此映射必须在至少 5 个开发程序上做差分验证；不能只比较最终测试通过率。

所有生成文件附 `source_map.json`：生成范围、原始范围、变换规则编号、是否一对一；模型看到的证据要显示原始文件位置，不能把临时文件行号伪称原始行号。

### 3.4 `failure-spec`：oracle 与 EI 的边界

模式 S 仅在原程序自带且分析器支持的失败断言处生成原 F EI。若目标程序没有断言，原协议 EI 不存在；不得从 `expected-output` 直接复制答案作为断言再把产物称作原论文 EI。

若 F-Codeflaws 要研究测试 oracle 派生的不变量，须另立操作定义：固定 repair 输入 `x` 与期望输出 `y`，构造被测输出关系 `P_x(s) := output(program,s)=y` 或相应的输出差异断言；必须明确这只刻画该输入及选定观察点，不是通用程序规格。buggy/ref 运行必须证明该断言在目标轨迹上的失败/通过对应原测试 oracle；标明测试输入、内部状态抽象、输出观察点和任何 nondeterminism。此条件实验叫“test-oracle-derived constraint”，而不是原 F2 EI。

F-Codeflaws 条件需重新命名以免混淆：

| 新条件 | 模型证据 | 对照含义 |
|---|---|---|
| FC0 | buggy 源码 + 固定失败摘要 | 基线 |
| FC1 | FC0 + 经源映射的静态语义切片 | 仅切片增量 |
| FC2 | FC1 + 分析器产生的 oracle-derived 约束及来源标签 | 测试派生状态证据增量 |
| FC3 | FC1 + FC2 完全相同约束的确定性自然语言渲染 | 表达形式对照 |

FC2 与原论文 Error Invariant 不等价；FC1 的切片也必须注明分析器和扩展版本。

## 4. 程序接口草案

仅为目标接口，尚未实现：

```text
codeflaws-adapt inventory \
  --dataset <immutable-root> --compiler clang-<pinned-version> \
  --out <new-batch>/inventory.jsonl

codeflaws-adapt validate \
  --inventory <inventory.jsonl> --cases <frozen-cases.json> \
  --mode subset|extended --timeout <seconds> \
  --out <new-batch>/compatibility.jsonl

codeflaws-adapt lower \
  --case <case-id> --side buggy|reference --mode subset|extended \
  --out-dir <case-work>/lowered/  # 原始输入只读；输出含 source_map 与审计记录
```

关键断言：输出目录必须全新；数据根只读；每次转换记输入/输出哈希；未知 AST 节点硬失败；生成文件必须能回映原始位置；差分执行有任一不一致即 `semantic_mismatch`，不得送模型。

兼容状态枚举：`supported_semantics_verified`、`unsupported_syntax`、`unsupported_semantics`、`semantic_mismatch`、`compile_error`、`repair_not_reproduced`、`reference_failed`、`timeout`、`infra_error`。只有第一种可进入后续协议。

## 5. 验证闸门

1. **前端闸门**：固定 Clang 版本对 100% 候选得到 AST 或明确诊断；宏、条件编译与实际 Makefile 参数固定。
2. **差分闸门**：buggy 和 reference 的原程序/转换程序在所有 repair 及 held-out 输入上逐输入标准输出、退出码、超时完全一致。另做随机边界测试与 sanitizer 辅助测试；后者不替代等价论证。
3. **分析器闸门**：对至少 5 个预先选定开发案例生成完成的 Map/切片；保存运行日志、完成标记、映射覆盖和谓词。无完成标记不得作为成功。
4. **规格闸门**：预先固定断言构造和模型可见/不可见字段；做 buggy/reference 双侧 oracle 对照。人工只审协议和聚合问题，不逐案例改模型证据。
5. **输入审计闸门**：F0–F3 每组除目标证据外字段完全一致；FC 组在协议中明确新增 oracle-derived 信息。reference、diff、held-out 输出、标签不得进入模型任务。
6. **冻结闸门**：提交开发/确认划分哈希、任务 JSON 哈希、提示词版本、工具/编译器版本、预算重试规则、评分规程和时间戳后才允许 API 阶段。

## 6. 当前能做与不能做

- 可以：继续实现只读 AST 特性盘点、受限子集选择、差分测试框架和 source-map 验证；所有工作均离线。
- 不能声称：已经让 Codeflaws 全库兼容；不能称已获得 50 个可分析 bug；不能把 parser 接受等同语义保真；不能将 test-output 派生断言说成原始 EI。
- 不能开始：模型调用、确认集抽样冻结、F2/F3 评分，直到上述闸门达标。

本设计受项目研究工作流约束；Codeflaws 快照和既有解析失败的证据详见 `codeflaws_f_preflight_2026-09-27.md`。新增适配器、实验协议和结果均应独立版本保存，不覆盖任何历史实验。
