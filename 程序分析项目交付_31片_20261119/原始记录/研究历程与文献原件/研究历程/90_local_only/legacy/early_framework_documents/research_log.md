# 程序切片科研过程记录

> 项目：基于双向程序切片（Program Chop）与 LLM 结合的自动化调试研究
> 实际开始：2026年初（论文阅读与方向确定）
> 记录开始：2026-05-20（正式搭建实验环境与工具开发）
> 最后更新：2026-06-06

---

## 0. 前期论文阅读（2026年初 — 2026-05-19）

研究方向的确立经过了大量的论文阅读和工具调研。核心脉络如下：

### 初始方向：程序切片在调试中的应用
- 了解程序切片的基本概念：后向切片、前向切片
- 阅读经典论文：Weiser (1984) 原始切片定义，Ferrante et al. (1987) PDG 构建

### 发现 Chop（双向切片）
- 阅读 Jackson & Rollins (1994) "Chopping: A Generalization of Slicing"
- 理解 Chop 的核心：PDG 上从 source 到 sink 的受限可达性问题
- 理解传统 PDG 的缺陷：前向∩后向可能包含无关路径上的节点

### 确立研究方向：Chop + LLM
- 思考将 Chop 与大模型结合做自动化调试
- 调研现有工具：WALA (Java), dg (LLVM/C), giri (动态切片), Slicer4J (benchmark)
- 收集最新论文：Assertion-based Slicing (2026), Multi-Stage Slicing (ISSTA 2026)

### 下载与搭建的工具
- WALA：IBM Java 程序分析框架
- dg：LLVM 程序依赖图工具
- giri：LLVM 动态切片工具
- Slicer4J：Java 切片 benchmark 数据集
- CodeQL：代码查询与静态分析

---

## 1. 研究背景与动机

### 核心问题
动态后向切片沿数据依赖和控制依赖向后追溯，结果是依赖关系的传递闭包，无法在"找到 bug 处"自动停止。Chop（双向切片）通过引入 source 和 sink 两个锚点，在 PDG 上做受限可达性计算，只保留恰好连接两者的语句链。

### 研究目标
探索 Chop 与 LLM 的结合：用切片缩小代码范围后交给 LLM 分析，对比直接丢完整代码给 LLM 的效果。

---

## 2. 文献调研

### 核心论文
- **Chopping: A Generalization of Slicing** (Jackson & Rollins, 1994) — Chop 的原始定义
- **Assertion-based Slicing and Slice Graphs** (Jorge Sousa Pinto, 2026) — 基于断言的双向切片
- **Multi-Stage On-Demand Program Slicing** (ISSTA '26, 2026) — 多线程程序的按需切片

### 参考工具论文
- **CodeLLM-Devkit** (ICSE 2025, IBM) — 程序分析结果→LLM 的桥梁框架

---

## 3. 现有工具调研 (2026-06-06)

### 程序切片工具
| 工具 | 语言 | 底层引擎 | 状态 |
|------|------|---------|------|
| **WALA** | Java | 自研 IR + 指针分析 | IBM 维护，成熟 |
| **dg** | C/C++ | LLVM IR | 学术项目 |
| **giri** | C/C++ | LLVM (动态) | 学术项目 |
| **Slicer4J** | Java | WALA | Benchmark 数据集 |

### "代码→LLM"工具
| 工具 | Stars | 做什么 | 可借鉴 |
|------|-------|--------|--------|
| **code2prompt** | 7.3k | 代码库→LLM 提示词 | Handlebars 模板系统 |
| **GitIngest** | 4k+ | Git 仓库→文本摘要 | 极简 API 设计 |
| **IBM CLDK** | ~16 | 程序分析→LLM 桥梁 | WALA 封装 + 统一 API |

### 关键发现

1. **CLDK 已有 `program_dependency_graph` 分析层级**，但后端还未实现，目前只返回调用图。这恰好是你的切入点。

2. **CLDK 的 `TreesitterSanitizer`** 实现了基于调用图的代码裁剪（保留焦点方法+被调用者），是一种粗粒度的"正向切片"，但缺少真正的 PDG 级别数据依赖和控制依赖。

3. **所有代码→LLM 工具都是"全量转提示词"**，没有做依赖分析过滤。你的工具是第一个在"代码→LLM"流程中插入 PDG 级别切片的。

---

## 4. 自建工具：Chop4LLM

### 架构设计

```
Chop4LLM
├── 借来的设计模式
│   ├── API 设计 → 借鉴 GitIngest（chop_method() 一行调用）
│   ├── 模板系统 → 借鉴 code2prompt（Handlebars 风格模板）
│   └── PDG 理论 → 标准程序分析文献（Ferrante 1987 等）
│
└── 自己的核心
    ├── PDG 构建器（数据依赖 + 控制依赖，基于 javalang AST）
    ├── Chop 算法（受限可达性：forward ∩ backward(in forward subgraph)）
    ├── 切片→LLM 模板（标注每条语句的依赖类型和原因）
    └── 对比实验框架（backward-only vs Chop vs full-code）
```

### 技术实现

**PDG 构建**：
- 解析：javalang（Java AST）→ 提取语句 + 定义/使用变量
- 控制依赖：CFG + 后支配分析（迭代不动点算法）
- 数据依赖：到达定值分析（GEN/KILL + 迭代不动点）
- 分支追踪：if-else 语句的 skip_next 机制保证正确 CFG

**Chop 算法**（Jackson & Rollins 1994）：
```
Phase 1: F = forward_slice(PDG, source_nodes)
Phase 2: Chop = backward_slice(restrict(PDG, F), sink_nodes)
```
不是简单的前向∩后向，而是先限制到前向可达子图再做后向切片。

### 测试结果 (2026-06-06)

| 测试用例 | 原始 | 后向切片 | Chop | 说明 |
|---------|------|---------|------|------|
| Discount Bug | 8 stmts | 6 (25%↓) | 3 (62.5%↓) | Chop 从 source→sink 精准裁剪 |
| 线性链 | 4 stmts | 4 (0%↓) | N/A | 每句都有依赖 |
| if-else | 5 stmts | 4 (20%↓) | N/A | 正确包含两个分支 |
| 无bug案例 | 5 stmts | 5 (0%↓) | N/A | 全部语句相关 |

**关键验证**：
- ✅ 控制依赖正确（if 条件 → 被控语句）
- ✅ 数据依赖正确（def-use 链，非变量名匹配）
- ✅ if-else 两个分支正确保留
- ✅ KILL 机制工作（被重定义的变量不再依赖旧定义）
- ✅ Chop 比纯后向切片更精准

---

## 5. 下一步计划

### 短期
- [ ] 添加 Python 支持（ast 模块）
- [ ] 处理 while/for 循环的后向边
- [ ] 改进 source 自动选取策略
- [ ] 用 Slicer4J benchmark 做正式评估

### 中期
- [ ] 接入 WALA 后端（通过 CLDK），获得跨过程 PDG
- [ ] 设计 LLM 对比实验（全代码 vs 切片后）
- [ ] 定义评估指标（bug 定位精度、token 节省率、LLM 输出聚焦度）

### 长期
- [ ] 自动化 source 候选点生成
- [ ] 结合 SBFL 做多维度定位
- [ ] 发表论文

---

## 6. 关键洞察

1. **切片的价值不在于"删代码"**，而在于告诉 LLM "这些语句之间有逻辑依赖关系"——带标注的切片比完整代码更有信息量。

2. **PDG 构建远比预想复杂**：变量名匹配是假切片，真正的逻辑依赖需要到达定值分析+控制依赖分析。这就是为什么草草写一个工具是不够的。

3. **CLDK 留了 PDG 的空位**：它的 `get_system_dependency_graph()` 只返回调用图并标注 "not yet implemented"。你的 Chop 恰好填补这个空缺。
