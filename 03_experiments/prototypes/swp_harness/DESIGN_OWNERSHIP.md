# 个人设计部分说明

以下严格区分：已有工作（需引用）、你的核心思路、助手（Claude）设计的内容。
你在论文中应据此判断哪些可声明为自己的贡献。

---

## 你的核心思路（论文中最核心的 contribution）

这些是你在这个项目开始前就已确立的方向，在 research_log.md 中有记录：

1. **让 LLM 本身成为切片引擎**
   - 不给 LLM 传统 PDG 算法的结果，而是让 LLM 自己去推理哪些语句有依赖关系
   - 这是你整个研究的出发点

2. **设计一套"工作流范式"指导 LLM**
   - 类比思维链——给 LLM 一个按步骤推理的操作手册
   - 范式是通用的，适用于不同 LLM，目标是获得好的切片代码

3. **Chop（双向切片）作为核心差异化**
   - 不仅做后向切片，更关注 source→sink 的受限可达性
   - 结合 LLM 做自动化调试

---

## Claude（助手）设计的具体内容

以下是我在本次对话中设计并实现的内容，**你在论文中需要自行判断、修改、声明**：

### A. 5 阶段范式的具体分解

| 阶段 | 我的设计 |
|------|---------|
| S1: 代码理解 | 要求 LLM 列出语句清单、分类（ASSIGN/CONDITION/CALL/...）、标注 DEF/USE |
| S2: 数据依赖追溯 | 递归追溯到达定值、KILL 规则、终止条件（参数/常量/source） |
| S3: 控制依赖分析 | 检查嵌套控制结构、将条件语句及其数据依赖加入切片 |
| S4: Chop 约束 | forward-from-source → 限制到前向可达子图 → backward within restricted graph |
| S5: 验证与输出 | 包含验证 + 排除验证 + 结构化标记格式 |

### B. 结构化输出格式 `<<<SLICE_RESULT>>>`

```
<<<SLICE_RESULT>>>
TYPE: backward | forward | chop
INCLUDED:
L5 | int x = foo(a) | DATA_DEF:x | depends_on:L2(a)
L8 | if (x > 0)      | CONTROL    | depends_on:L5(x)
...
EXCLUDED:
L6 | int y = bar(b)  | IRRELEVANT: y not reaching sink
...
<<<END_SLICE_RESULT>>>
```

这个格式的设计目标：可被正则自动解析，提取行号 → 与 ground truth 对比计算 Precision/Recall。

### C. 每阶段的输入/输出规范

- S1 输出格式：`L行号 | 代码 | 类型 | DEF:变量 | USE:变量`
- S2 输出格式：`DATA_DEP_CHAINS` + `DATA_SLICE_STATEMENTS` + `STATEMENTS_OUTSIDE_DATA_SLICE`
- S3 输出格式：`CONTROL_DEPS` + `ADDED_CONDITIONS` + `EXTENDED_SLICE`
- S4 输出格式：`FORWARD_REACHABLE` + `REMOVED_BY_CHOP` + `CHOP_SLICE`
- S5：自检机制（自我验证包含/排除的合理性）

### D. 实验设计

- **6 个 LLM 类别**（Claude/GPT/Gemini/DeepSeek/Qwen/Llama）
- **4 个 baseline**（全代码 / Zero-shot / WALA PDG / SWP）
- **5 个消融变体**（去掉验证/控制依赖/few-shot/分阶段）
- **评估指标**：Precision / Recall / F1 / Exact Match / Token Reduction / Parse Rate
- **统计设计**：每组 3 次重复，均值 ± 标准差，配对 t-test

### E. 软件架构

```
swp_harness/
├── paradigm/    # 范式 prompt 模板
├── ground_truth/ # 统一数据集加载器
├── llm/         # API 客户端 + 输出解析 + 运行器
├── eval/        # 指标计算 + 对比 + 消融
└── reports/     # 报告生成 + 可视化
```

---

## 论文 Contribution 建议写法

以下是我建议的 contribution 表述。凡标注 **[我的设计]** 的部分，你需要在论文中用自己的语言重新表述并确认是否声明为你的贡献：

1. **SWP 范式** — 将程序切片形式化为 LLM 可执行的 5 阶段推理工作流，每阶段有显式的中间输出格式。**[你的核心思路 + 我设计的阶段划分和格式]**

2. **结构化输出格式** — 设计了一套可机器解析的切片输出标记语言，使得 LLM 切片结果可自动评估。**[我设计的格式]**

3. **跨模型实验** — 在 40+ 个 benchmark 上对比 N 个 LLM 的切片质量，包含 baseline 对比和消融分析。**[我设计的实验方案]**

4. **SWP-Harness 工具** — 可扩展的 LLM 切片评估框架，含 ground truth 数据集。**[我编写的代码]**
