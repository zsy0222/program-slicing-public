# Defects4J Gson-6b：真实缺陷动态切片实验记录

日期：2026-08-27  
状态：已完成可复现实验闭环

## 目标

验证工作流能否在真实 Java 缺陷上完成：官方失败测试触发 → 运行轨迹 → 动态语义切片 → 错误不变量 → 修复对照 → 完整回归。

## 实验对象与环境

- 数据集：Defects4J 3.0.1，Gson-6b / Gson-6f。
- 漏洞提交：`67bd3a2cf6f9c9c6e7f615969b1918f68e03932d`。
- 固定提交：`dea305503ad8827121e8212248c271f1f2f90048`。
- 运行时：OpenJDK 8u502，Ubuntu 22.04。
- 切片工具：Slicer4J（动态后向切片）。

## 失败行为

Defects4J 补充测试 `JsonAdapterNullSafeTest` 的两个场景均在漏洞版本报出 `NullPointerException`：

- `testNullSafeBugDeserialize`
- `testNullSafeBugSerialize`

异常位置为 `JsonAdapterAnnotationTypeAdapterFactory.getTypeAdapter` 第 68 行。

## 动态切片结果

以 `com.google.gson.internal.bind.JsonAdapterAnnotationTypeAdapterFactory:68` 为切片准则，使用反序列化触发测试执行。

- 源代码级切片：218 条。
- 原始动态依赖节点：712 条。
- 带依赖关系节点：678 条。
- 根因链关键行：43、44、47、61、62、68。

关键链路为：递归 `TypeAdapterFactory.create(...)` 在第 62 行可返回 `null`，但第 68 行对 `typeAdapter` 无条件调用 `nullSafe()`，导致空指针。

## 自动导出的错误不变量

> 若 `typeAdapter == null`，不得调用 `typeAdapter.nullSafe()`；方法应保留并返回该空值。

该不变量与官方固定版本的语义完全一致：仅当 `typeAdapter != null` 时调用 `nullSafe()`，否则直接返回 `null`。

## 验证结果

| 版本 | 完整模块测试 | 触发测试 |
| --- | ---: | --- |
| Gson-6b（漏洞） | 986 项：0 failures，2 errors | 两项均因 NPE 失败 |
| Gson-6f（固定对照） | 986 项：0 failures，0 errors | 两项均通过 |

## 结论与边界

该案例支持：动态切片能够把真实失败路径收敛到与官方修复一致的局部数据依赖链，并给出可检验的空值不变量。它是一个真实案例的可行性证据，不足以单独证明对所有缺陷类型均有效。

另：Gson-5b 的日期解析测试在现代 JDK 8u502 中不再触发，属于运行时版本敏感案例，未纳入本轮效果统计。
