# J 组切片工具准备记录（2026-09-28）

状态：**仅下载和静态校验；未开始 J 组实验、未调用模型 API、未运行 Defects4J 案例。** 本记录不表示切片实现或跨工具兼容性已通过。

后续增量（2026-10-07）：已在新副本完成官方定制依赖构建、WALA 适配器及两个微型程序的同准则功能检查；另发现并在本地兼容分支修正动态循环映射。见[新报告](../reviews/three_compatibility_fixes_2026-10-07.md)。以下内容保留为 9 月 28 日当时的准备状态，不作为当前未完成项清单。

## 已准备的本机私有文件

所有新增文件位于 `90_local_only/third_party_tools/`，该目录被 Git 忽略；原有 WALA 与 Slicer4J 源码副本未更新或覆盖。

| 组件 | 来源与固定版本 | 本机位置 | 检查 |
| --- | --- | --- | --- |
| Apache Maven | [官方归档](https://archive.apache.org/dist/maven/maven-3/3.9.16/binaries/)，3.9.16 | `apache-maven-3.9.16/`；原 ZIP 在 `downloads/` | ZIP 的 SHA-512 与官方 `.sha512` 一致；`mvn -version` 可启动 |
| WALA | [官方发布](https://github.com/wala/WALA/releases/tag/v1.8.0)，1.8.0；Maven Central `com.ibm.wala.core`、`util`、`shrike` | `m2/com/ibm/wala/` | 三个 JAR 的 SHA-1 与 Maven Central 校验文件一致；`Slicer` 类字节码版本 61（Java 17） |
| FlowDroid | Slicer4J POM 所列 `soot-infoflow:2.10.0` | `m2/de/fraunhofer/sit/sse/flowdroid/` | JAR 的 SHA-1 与 Maven Central 校验文件一致；传递依赖已下载 |
| DynamicSlicingCore 源码 | [Slicer4J 官方依赖仓库](https://github.com/resess/DynamicSlicingCore)，提交 `064a813c8be03bfc7ec634d06657a8533cfeae7f` | `DynamicSlicingCore-064a813c8be03bfc7ec634d06657a8533cfeae7f/`；原 ZIP 在 `downloads/` | ZIP 可解压，SHA-256 为 `03a75ed4b5512d3f374b041d9093a63c2bbae11c1330b341176c19e5e7356226` |

原有 Slicer4J 源码固定在 `68f415a3d5cf8731dc2e43a83ffe14af376c887a`，原有 WALA 源码固定在 `bd2e8d1725421f8f3e48f6ba72ffe5fbdf61cbd9`；这两个旧副本没有更新。WALA 1.8.0 是另存于 Maven 缓存的发布包，不代表旧源码副本已升级。新下载的 Maven 与依赖不会更改系统 PATH 或默认 Java。

首次尝试部分克隆 DynamicSlicingCore 时检出未完成，已将该目录单独标为 `DynamicSlicingCore-incomplete-clone/` 保留；上表所用的是随后下载并成功解压的完整 ZIP，不能混用两个目录。

## 未完成的工具验证

- DynamicSlicingCore 当前 POM 还要求 `soot-infoflow:2.10.0-mandoline`，但其 `core/libs` 内没有对应 Maven 仓库制品；`mvn dependency:go-offline` 因此失败。标准 `2.10.0` **不能冒充**定制版本。保留源码及下载缓存，待核对上游定制制品或选择可复现的兼容提交后再构建。
- Slicer4J 原有源码依赖上述核心工程，因此本机**尚未完成新构建或功能冒烟测试**；原有虚拟机工具的运行记录与本次本机准备是不同证据。
- Ubuntu 当前 `127.0.0.1:2222` 连接被拒绝，故未部署到虚拟机，也未核验虚拟机中的 Java 8/17、Maven 和 Slicer4J 可用性。恢复连接后先盘点，不覆盖原实验工具。
- 下一版 J 组的 WALA 静态切片适配器、统一准则/源行映射及 Slicer4J 完整性门槛仍待实现和独立冒烟；工具下载不能替代这些验证。JOANA 不属于本次主实验必需组件，未下载。

遵循 [J 组工具选择审查](../reviews/j_slicing_tool_selection_2026-09-27.md)：WALA 静态后向切片和 Slicer4J 动态后向切片先做开发验证，再冻结版本、配置、运行时和入组规则；不根据模型修复结果挑选工具。
