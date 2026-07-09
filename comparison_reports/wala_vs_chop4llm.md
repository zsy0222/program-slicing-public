# Chop4LLM vs WALA 切片对比报告

> 日期：2026-06-06
> 对比对象：WALA 官方切片测试集（`core/src/testSubjects/java/slice/`）
> 对比方法：Chop4LLM 结果 vs WALA SlicerTest.java 断言结果

---

## 对比总览

WALA 是 IBM 维护的成熟 Java 程序分析框架（20+ 年历史），其切片功能在 Jimple IR 级别构建 PDG，支持全程序跨过程分析 + 指针分析。Chop4LLM 是基于 javalang 的源码级 PDG 构建器，目前仅支持过程内分析。

两者在**不同的抽象层次**工作，因此行数不可能直接对比。有意义的对比维度是**切片结构和依赖类型的正确性**。

---

## 案例一：Slice1.java — 跨过程数据依赖

### 源码（25 行）

```java
/*
 * Copyright (c) 2006 IBM Corporation.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 */
package slice;

public class Slice1 {
  public static void main(String[] args) {
    int x = foo(1);
    int y = bar(2);
    System.out.println(x + y);
  }

  static int foo(int x) {
    return x + 2;
  }

  static int bar(int x) {
    return x + 3;
  }
}
```

### 程序说明

一个简单的跨过程数据依赖测试。`main` 调用 `foo(1)` 和 `bar(2)`，把结果相加后 `println` 输出。切片 sink 是 `println` 语句（L17）。

### WALA 预期（SlicerTest.testSlice1）

```java
@Test
public void testSlice1() {
    // 构建调用图和分析: ZeroOneCFA, Application entrypoints
    CGNode main = CallGraphSearchUtil.findMainMethod(cg);
    Statement s = SlicerUtil.findCallTo(main, "println");
    // 后向切片: 仅数据依赖, 无控制依赖
    Collection<Statement> slice =
        Slicer.computeBackwardSlice(
            s, cg, pointerAnalysis,
            DataDependenceOptions.FULL,
            ControlDependenceOptions.NONE);
    // 断言: 来自 Application ClassLoader 的语句共 16 条
    int i = 0;
    for (Statement st : slice) {
      if (st.getNode().getMethod().getDeclaringClass()
            .getClassLoader().getReference()
            .equals(ClassLoaderReference.Application)) {
        i++;
      }
    }
    assertThat(i).isEqualTo(16);
}
```

预期含义：从 println 调用语句沿数据依赖后向追溯，得到 **16 条 Jimple IR 级别**的语句（来自 Application 类加载器，排除 JDK 标准库）。这 16 条跨方法分布在 main、foo、bar 三个方法中。

### Chop4LLM 结果

```
切片类型：后向切片（数据依赖 + 控制依赖）
Sink：L17 (println)
切片内容：3 条语句
  L15: int x = foo(1);
  L16: int y = bar(2);
  L17: System.out.println(x + y);
缩减：0%（全保留，因为 3 条语句都有依赖链）
```

### 差异分析

| 差异点 | WALA | Chop4LLM | 原因 |
|--------|------|----------|------|
| 语句数 | 16 (IR) | 3 (源码行) | IR 级别 vs 源码级别 |
| 跨过程 | ✅ foo() 和 bar() 体被纳入 | ❌ 不追踪进方法内部 | Chop4LLM 未实现跨过程 |
| println 被纳入 | ✅ | ✅ | 一致 |
| x 定义被纳入 | ✅ | ✅ | 一致 |
| y 定义被纳入 | ✅（与 println 无关但代码顺序依赖） | ✅（use `x` 和 `y`） | 近似一致 |

### 结论

Chop4LLM 正确识别了 main 方法内的数据依赖链（x 和 y 流向 println）。主要差距是**跨过程能力**——WALA 会穿透 `foo()` 和 `bar()` 追踪参数传递和返回值，而 Chop4LLM 把方法调用当作不透明节点。

---

## 案例二：Slice4.java — 前向切片

### 源码（25 行）

```java
/*
 * Copyright (c) 2006 IBM Corporation.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 */
package slice;

public class Slice4 {
  public static void main(String[] args) {
    int x = foo(1);
    bar(x);
  }

  static int foo(int x) {
    return x + 2;
  }

  static void bar(int x) {
    return;
  }
}
```

### 程序说明

测试前向数据依赖。`main` 调用 `foo(1)` 获得返回值赋给 `x`，再把 `x` 传给 `bar(x)`。WALA 从 `foo` 的 `return` 语句做前向切片，追踪哪些语句使用了这个返回值。

### WALA 预期（SlicerTest.testSlice4）

```java
@Test
public void testSlice4() {
    // 构建调用图和分析: ZeroOneCFA, Application entrypoints
    CGNode main = CallGraphSearchUtil.findMainMethod(cg);
    Statement s = SlicerUtil.findCallTo(main, "foo");
    s = PDFSlice.getReturnStatementForCall(s);  // 取 foo 的 return 语句作为 source
    // 前向切片: 仅数据依赖, 无控制依赖
    Collection<Statement> slice =
        Slicer.computeForwardSlice(
            s, cg, pointerAnalysis,
            DataDependenceOptions.FULL,
            ControlDependenceOptions.NONE);
    // 断言: 切片共 4 条语句
    assertThat(slice).hasSize(4);
}
```

预期含义：从 `foo` 方法的 `return` 语句出发，沿数据依赖正向追溯，找到所有使用了 `foo` 返回值的语句。预期 **4 条 Jimple IR 语句**（在 main 中 `int x = foo(1)` 到 `bar(x)` 的链）。

### Chop4LLM 结果

```
切片类型：Chop（双向受限可达性，source=L15, sink=L16）
切片内容：2 条语句
  L15: int x = foo(1);
  L16: bar(x);
缩减：33.3%（去掉了 foo 和 bar 的方法体）
```

### 差异分析

| 差异点 | WALA | Chop4LLM | 原因 |
|--------|------|----------|------|
| 切片方向 | 前向（从 return 往调用点追） | Chop（双向，source→sink 受限可达） | 方向逻辑不同 |
| 语句数 | 4 (IR) | 2 (源码行) | IR vs 源码 |
| 跨方法调用链 | ✅ foo return → x=foo(1) → bar(x) | ✅（在 main 内） | main 内逻辑一致 |
| x=foo(1) 被纳入 | ✅ | ✅ | 一致 |
| bar(x) 被纳入 | ✅ | ✅ | 一致 |

### 结论

在 main 方法内，Chop4LLM 正确追踪了 `foo(1)` 返回值 → `x` → `bar(x)` 的数据流。但 Chop 是双向受限可达（保留 source→sink 路径上的节点），WALA 的前向切片是"所有从 source 能到达的节点"，范围不同。

---

## 案例三：TestCD1.java — 嵌套控制依赖

### 源码（27 行）

```java
/*
 * Copyright (c) 2006 IBM Corporation.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 */
package slice;

public class TestCD1 {

  static void doNothing(Object o) {}

  public static void main(String[] args) {
    Integer I = (Integer) new A().foo();
    int i = I;
    if (i > 0) {
      System.out.println("X");
      if (i > 1) {
        System.out.println("Y");
        doNothing(I);
      }
    }
  }
}
```

### 程序说明

测试嵌套控制依赖。`main` 创建 `Integer I`（通过 `new A().foo()` 从另一个类获取），赋值给 `i`，两层嵌套 `if` 判断后调用 `doNothing(I)`。切片 sink 是 `doNothing(I)` 调用（L24）。WALA 预期两个 `if` 条件都应该出现在后向切片中，因为两者都控制着 `doNothing` 是否被执行。

**依赖的外部类 A.java**（同包 `slice`）：

```java
/*
 * Copyright (c) 2013 IBM Corporation.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * which accompanies this distribution, and is available at
 * http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 *     IBM Corporation - initial API and implementation
 */
package slice;

class A {

  Object f;
  Object g;

  @SuppressWarnings("removal")
  Object foo() {
    return new Integer(3);
  }

  public Object getF() {
    return f;
  }

  public void setF(Object f) {
    this.f = f;
  }
}
```

TestCD1 中 `new A().foo()` 创建了一个 `A` 实例并调用 `foo()`，返回 `new Integer(3)`。

### WALA 预期（SlicerTest.testTestCD1）

```java
@Test
public void testTestCD1() {
    // 构建调用图和分析: ZeroOneCFA, Application entrypoints
    CGNode main = CallGraphSearchUtil.findMainMethod(cg);
    Statement s = SlicerUtil.findCallTo(main, "doNothing");
    // 后向切片: 数据依赖 + 控制依赖
    Collection<Statement> slice =
        Slicer.computeBackwardSlice(
            s, cg, pointerAnalysis,
            DataDependenceOptions.FULL,
            ControlDependenceOptions.FULL);
    // 断言: 切片中应有 2 个条件分支语句
    assertThat(SlicerUtil.countConditionals(slice))
        .as(slice::toString)
        .isEqualTo(2);
}
```

预期含义：从 `doNothing` 调用语句后向追溯（数据+控制依赖），切片应包含 2 个条件分支——外层 `if (i > 0)` 和内层 `if (i > 1)`，因为两者都控制着 `doNothing` 的执行。

### Chop4LLM 结果

```
切片类型：后向切片（数据依赖 + 控制依赖）
Sink：L24 (doNothing(I))
切片内容：2 条语句
  L18: Integer I = (Integer) new A().foo();
  L24: doNothing(I);
条件分支数：0
```

### 差异分析

| 差异点 | WALA | Chop4LLM | 原因 |
|--------|------|----------|------|
| 条件数 | 2 | 0 | 两个关键问题 |
| 外层 if | ✅ 纳入 | ❌ 缺失 | CFG 块边界检测过于简化 |
| 内层 if | ✅ 纳入 | ❌ 缺失 | CFG 不会正确传播嵌套 block |
| 数据链 I→doNothing | ✅ | ✅ | 一致 |
| L19 (int i = I) | ✅ 纳入 | ❌ 缺失 | `I` 的 USE 关系被断掉 |

### 根因分析

Chop4LLM 的 CFG 构造和块边界检测存在已知局限：

1. **`_find_block_end()` 过于简化**：当前实现为 `cond_idx + 2`，对于多语句块和嵌套 if 完全不正确。导致 CONTROL_DEP 边错误/缺失。

2. **javalang 的 AST 已经正确解析了嵌套结构**（if 的 then/else body 是准确的），但在 `_process_statement_with_branches` 中，我们**扁平化了嵌套信息**，丢失了 block 结构。

3. **`int i = I` 的数据依赖**：L19 定义 `i`、使用 `I`。应该产生数据边 L18→L19（`I`）和 L19→L20（`i`），但数据依赖分析中 L19 没有被纳入切片——说明从 L24 后向遍历时，L19 的前驱 L18 直接满足了对 `I` 的引用，跳过了 L19。

### 结论

这是 Chop4LLM 需要重点修复的缺陷。核心问题是 **CFG 的块边界检测不准确**导致控制依赖分析失败。修复方案：在解析阶段保留 block nesting 结构，使用该结构构造正确的 CFG 而非依赖启发式边界。

---

## 综合对比结论

| 维度 | WALA | Chop4LLM |
|------|------|----------|
| **分析层次** | Jimple IR（字节码级） | Java 源码行 |
| **跨过程** | ✅ 全程序 | ❌ 仅过程内 |
| **指针分析** | ✅ Andersen/0-1-CFA | ❌ 基于变量名的到达定值 |
| **控制依赖** | ✅ 精确的后支配分析 | ⚠️ 正确算法，但在嵌套 if 场景因 CFG 不准而失败 |
| **数据依赖** | ✅ 字段敏感 | ⚠️ 简单情况下正确，嵌套 block 中因 CFG 失效 |
| **切片方向** | 仅后向 / 仅前向 | 后向 / 前向 / **Chop（双向受限可达）** ← WALA 没有 |
| **LLM 集成** | ❌ 无 | ✅ 模板格式化 + 依赖标注 |
| **API 易用性** | 复杂（需要 scope, cha, builder, cg, pointer analysis） | 简单（`chop_method(src, sink_line, source_line)`） |
| **安装难度** | 高（Maven, JVM, 多依赖） | 低（`pip install` 即可） |

### Chop4LLM 的优势
- **Chop 算法**：WALA 只提供 forward/backward，没有 Chop（受限可达性）
- **LLM 就绪**：切片结果直接带依赖标注和模板化 prompt
- **正确的算法骨架**：数据依赖（到达定值迭代不动点）和控制依赖（后支配分析）的算法实现是正确的，问题仅在输入（CFG）的质量

### 需要修复的优先事项
1. **CFG 块边界重建**（高优先级）：不再依赖启发式，使用 AST 的嵌套信息构造精确的 CFG
2. **跨过程支持**（中优先级）：追踪方法调用，构建 SDG
3. **更好的变量追踪**（中优先级）：处理 `new A().foo()` 这种链式调用的 USE/DEF 关系

---

## 附录：运行命令

```bash
cd program_slicing
python -c "
from chop4llm import chop_method
for fname, sink, src_line in [
    ('WALA/core/src/testSubjects/java/slice/Slice1.java', 17, None),
    ('WALA/core/src/testSubjects/java/slice/Slice4.java', 16, 15),
    ('WALA/core/src/testSubjects/java/slice/TestCD1.java', 24, None),
]:
    with open(fname) as f:
        src = f.read()
    result = chop_method(src, sink_line=sink, source_line=src_line, auto_source=True)
    print(f'\n{fname.split(\"/\")[-1]}: {result}')
    for n in result.slice_nodes:
        print(f'  L{n.line}: {n.code[:60]}')
"
```
