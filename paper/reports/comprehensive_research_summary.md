# 程序切片 × 大语言模型：研究全记录与前沿方案

> 研究起始: 2026年初 | 最后更新: 2026-07-18
> 论文阅读: 30+ 篇 | 涵盖: 经典切片、动态切片/故障定位、LLM切片、断言/不变式、抽象解释、工具
> 当前方案: LLM 深度阅读抽象解释中间表示 (Dimovski Error Invariant 轨迹)

---

## 一、研究演进概览

```
Phase 1: Chop4LLM (2026年5-6月)
  传统PDG切片工具 + LLM分析
  ↓ (问题: 两个步骤割裂, PDG构建成本高, 与LLM结合浅)

Phase 2: SWP 范式 (2026年6月底-7月初)
  LLM自身作为切片引擎, 结构化推理范式
  ↓ (问题: 与SliceMate重叠, 差异化不足)

Phase 3: 级联混合切片 (2026年7月中)
  断言引导: 动态后向源点定位 + 静态前向路径验证
  ↓ (问题: 断言依赖脆弱, Dimovski已做了同一范式且更优)

Phase 4: LLM × 抽象解释 (2026年7月18日-当前) ★
  Dimovski Error Invariant 轨迹 → LLM 深度语义阅读
  LLM不是切片引擎, 不是后分类器, 而是抽象解释中间表示的语义理解者
```

---

## 二、论文阅读体系

### 2.1 经典程序切片 (Foundational)

| 论文 | 年份 | 核心贡献 | 与研究关系 |
|------|------|---------|-----------|
| Weiser — Program Slicing | 1984 | 切片原始定义, slicing criterion ⟨l,V⟩ | 领域起源 |
| Ferrante et al. — PDG | 1987 | 程序依赖图, 后支配形式化控制依赖 | PDG理论基础 |
| Korel & Laski — Dynamic Slicing | 1988 | 首个动态切片 | 动态切片起源 |
| Horwitz et al. — SDG | 1990 | 系统依赖图, 跨过程切片 | 跨过程基础 |
| **Jackson & Rollins — Chop** | **1994** | **双向切片, 受限可达性** | **Chop4LLM算法来源** |

### 2.2 动态切片与故障定位

| 论文 | 年份 | 核心贡献 | 与研究关系 |
|------|------|---------|-----------|
| **Zhang et al. — MPS** | **2007** | **三切片交集 (BwS∩FwS∩BiS), DDG 100-1000×减速** | **核心baseline** |
| Cleve & Zeller — Cause Transitions | 2005 | 通过/失败trace状态对比, Delta Debugging | 阶段1灵感来源 |
| Wong et al. — Fault Localization Survey | 2016 | 178+论文分类综述 | FL全景 |

### 2.3 LLM驱动的程序切片

| 论文 | 年份 | 核心贡献 | 与研究关系 |
|------|------|---------|-----------|
| **Shahandashti et al.** | **2025** | **裸调GPT-4o切片仅60.8%, 证明LLM直接切片不可靠** | **关键证据** |
| **Chang et al. — SliceMate** | **2025** | **三Agent切片, +22%准确率, SliceBench** | **最直接竞品** |
| He et al. — SLICEFORMER | 2026 | Seq2seq+DFG预训练 | 训练路线SOTA |
| He et al. — SLICET5 | 2025 | Copy Mechanism+约束解码 | 关键技术 |
| Yadavally et al. — NS-Slicer | 2024 | 首个神经静态切片, F1=97.41% | 神经路线baseline |

### 2.4 断言、不变式与规约

| 论文 | 年份 | 核心贡献 | 与研究关系 |
|------|------|---------|-----------|
| Barros et al. — Assertion-based Slicing | 2010 | 公理语义切片, Slice Graph | 断言切片先驱 |
| Jalili et al. — ASSERTIFY | 2024 | LLM生成Java断言 | 原方案Phase0工具 |

### 2.5 抽象解释 (当前方案基础设施)

| 论文 | 年份 | 核心贡献 | 与研究关系 |
|------|------|---------|-----------|
| **Dimovski — SAS 2023** | **2023** | **Error Invariant 概念首次提出** | **2024版前身** |
| **Dimovski — COLA 2024** | **2024** | **迭代后向-前向抽象解释, BDD精化, 语句级语义切片** | **当前方案核心基础设施** |
| **Dimovski — SLE 2025** | **2025** | **扩展到软件产品线 (SPL)** | **证明方法可扩展性** |

---

## 三、当前方案：LLM 深度阅读 Error Invariant 轨迹

### 3.1 为什么选择 Dimovski

在所有故障定位/切片工具中，**Dimovski 是唯一产出结构化中间表示的工具**：

- Ochiai/Tarantula → 输出数字分数 → LLM 读不懂
- Zhang 2007 MPS → 输出行号列表 → 和读代码没区别
- SliceMate → 输出行号列表 (黑盒) → 无中间过程
- **Dimovski → 输出 Error Invariant 序列** → 数学约束 + 语义可读 + 位置排列

Error Invariant 的三个关键属性使其成为 LLM-形式方法接口的理想语言：
1. 数学上精确定义 (可被形式方法操作)
2. 人类可解释 (`[y = x + 1, x ≥ 5]` 可直接理解)
3. 沿程序位置排列成演化轨迹 (可追踪错误传播)

### 3.2 Error Invariant 中被 Dimovski 浪费的信息

Dimovski 目前只做了一件事：对比相邻位置的 invariant **是否相同** → 确定语句相关/无关。

但 invariant 内部包含丰富的传播语义，全部未被利用：
- **变量进入/退出**: 哪个变量首次出现在 invariant 中？哪个消失了？
- **关系演变**: `x ≥ 5` → `z = 2*x` — 约束如何转化？
- **强度变化**: 约束变紧还是变松？何时突然扩大？
- **质变点**: invariant 不仅"变了"，而是从一类条件变为另一类

### 3.3 LLM 从 Invariant 轨迹中的五项能力

| 能力 | 说明 | Dimovski 能做吗? |
|------|------|:---:|
| ① 语义翻译 | `[y=x+1, x≥5]` → "y比x大1，且x至少为5" | ❌ |
| ② 质变检测 | 发现 invariant 从"线性约束"变为"区间约束"的转折 | ❌ |
| ③ 缺失推断 | "这里缺少关于 input 值的约束，建议补充" | ❌ |
| ④ 因果链重构 | "错误起源于Y的计算，经Z的传播，最终在assert处失败" | ❌ |
| ⑤ 谓词反馈 | 建议 Dimovski 自己无法发现的精化谓词 → 重新分析 | ❌ |

### 3.4 四阶段架构

```
INPUT: 源码 + 错误位置
  │
  ▼
PHASE 1: Dimovski 确定性骨干
  → Error Invariant 序列 + 初始切片
  │
  ▼
PHASE 2: LLM 深度阅读 Invariant 轨迹 ★
  ① 语义翻译  ② 质变检测  ③ 缺失推断
  │
  ▼
PHASE 3: 双向反馈精化 (循环)
  LLM建议谓词 → 加入ℙ → Dimovski重新BDD精化
  │
  ▼
PHASE 4: 因果链重构 + 可读输出
  错误起源 + 传播路径 + 修复建议 + 置信度
```

### 3.5 与之前方案的本质差异

| | 断言混合 (Phase 3) | 当前方案 (Phase 4) |
|---|---|---|
| LLM 角色 | 分类器 (打标签) | **语义理解者** |
| LLM-分析关系 | 单向 (Dimovski→LLM) | **双向** (LLM反馈精化) |
| LLM 阅读什么 | 源代码 + 切片结果 | **Error Invariant 数学轨迹** |
| 创新深度 | 引入LLM分类 | **首次让LLM读懂形式分析内部过程** |

### 3.6 理论贡献

1. **Error Invariant 作为半形式化语义接口**: 首次提出将抽象解释的中间表示作为 LLM 与形式方法之间的共享语言

2. **LLM 驱动的谓词发现**: LLM 不再是被动分类器，而是主动引导精化过程的"语义顾问"

3. **双向反馈架构**: 形式分析保证 soundness，LLM 提升 precision 和可解释性

4. **从不变量序列到因果叙事**: LLM 解释的是 invariant 的演变轨迹，而非原始代码

---

## 四、实验设计框架

### 实验 1: 语义翻译准确性
LLM 将 invariant 翻译为自然语言因果描述，人工评估忠实度

### 实验 2: 质变点定位 (核心)
LLM 从 invariant 轨迹定位错误起源点，对比 Ochiai/Cause Transitions/Dimovski 原生

### 实验 3: 谓词建议有效性 (核心)
LLM 建议的补充谓词是否真的帮助 Dimovski 精化，对比切片缩减率

### 实验 4: 因果链叙事正确性
LLM 因果叙事与真实修复 commit 的一致性评分

### 实验 5: 消融实验
Binary/NoPosition/NoTrace/CodeOnly 配置比较

### 实验 6: 用户研究
开发者使用不同工具的找 bug 时间和准确率

---

## 五、后续工作计划

- [ ] 在 Defects4J 上建立 Dimovski 分析结果数据库
- [ ] 设计 LLM 阅读 invariant 轨迹的 prompt 模板
- [ ] 原型实现 Phase 2 (LLM invariant 阅读器)
- [ ] 实现 Phase 3 反馈循环
- [ ] 运行实验 2 (质变点定位) 初步验证核心假设

---

## 附录：关键对比数据

### Zhang 2007 MPS 开销
- DDG 构建: 执行 2500万指令 → 139秒，正常执行 < 0.1秒
- 减速比: 100×–1000× (2-3 数量级)
- DDG 内存: 数百KB–数百MB

### Shahandashti 2025 LLM切片
- GPT-4o: 60.84% 静态 / 59.69% 动态
- 优化上限: Prompt Crafting +4%, Iterative +3.9%

### SliceMate 2025
- 准确率 +22%, F1 +28% vs baseline
- 成本: ~$0.15/次 (GPT-4o)
- 仅后向切片，不做 Chop

### Dimovski 2024
- 零运行时开销
- Polyhedra 域在高维时最坏指数复杂度
- BDD 域节点数随谓词数指数增长 (最坏)
- 实际基准: TCAS/SV-COMP 中小型C程序
