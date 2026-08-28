# Defects4J Gson-7b：数值 Token 解析动态切片实验记录

日期：2026-08-27  
状态：已完成可复现实验闭环

## 实验对象

- 数据集：Defects4J 3.0.1，Gson-7b / Gson-7f。
- 漏洞提交：`a02f575797d9295bff8fb92d266b0f9724e42098`。
- 固定提交：`2b08c88c09d14e0b1a68a982bab0bb18206df76b`。
- 环境：Ubuntu 22.04，OpenJDK 8u502，Slicer4J。

## 失败行为

未加引号的整数和长整数 JSON Map 键被解释为 `STRING`，导致 `JsonReader.nextLong` 第 965 行抛出 `IllegalStateException`。

官方触发测试：`MapTest::testMapDeserializationWithUnquotedLongKeys`。同一根因还触发未加引号整数键测试。

## 动态切片

切片准则：`com.google.gson.stream.JsonReader:965`，执行长整数键触发测试。

- 源代码级切片：150 条。
- 原始动态依赖节点：305 条。
- 依赖关系节点：428 条。
- 关键源代码行：940、945、951、954、965。

核心依赖链为：token 类型 `p` 未满足第 954 行的 quoted-token 条件，控制流进入第 965 行异常分支；但该输入本身是合法的未加引号数值。

## 错误不变量

> 对可解析的未加引号数值 token，`nextLong()` / `nextInt()` 必须进入数值解析路径，而不能进入“token 类型错误”的异常分支。

官方固定版本通过将 `PEEKED_UNQUOTED` 纳入可解析分支满足该不变量。

## 验证结果

| 版本 | 完整模块测试 |
| --- | ---: |
| Gson-7b（漏洞） | 989 项：0 failures，3 errors |
| Gson-7f（固定对照） | 989 项：0 failures，0 errors |

结论：第二个不同类型的真实缺陷同样表明，动态切片能够将失败测试收敛到与官方修复一致的局部控制/数据依赖条件。
