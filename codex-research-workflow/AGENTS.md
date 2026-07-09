# 项目：文献矩阵研究项目

## 背景

我正在准备一篇关于 **[替换为你的研究主题]** 的文献综述，需要把已收集论文整理成可写作的证据矩阵。

## 目标

从 `data/raw-pdfs/` 和 `data/references/` 中整理文献信息，输出：

- `matrix/literature_matrix.xlsx`
- `matrix/literature_matrix.csv`
- `reports/evidence_map.md`
- `reports/research_gaps.md`
- `reports/literature_review_brief.md`

## 约束条件

- 不要删除或覆盖 `data/raw-pdfs/` 下的原始 PDF
- 不要编造 DOI、作者、年份、期刊名和页码
- 无法确认的信息必须标记为 `unknown` 或 `needs_manual_check`
- 引用观点时尽量记录 PDF 页码或章节位置
- 所有自动提取结果都要保留来源文件名
- `.env.local` 不能提交到仓库
- API Key 从 `.env.local` 读取，不写入代码或日志

## 文献矩阵字段

| 字段 | 说明 |
|------|------|
| citation_key | 引用键 |
| title | 论文标题 |
| authors | 作者列表 |
| year | 出版年份 |
| venue | 期刊/会议/预印本 |
| doi | 数字对象标识符 |
| research_question | 研究问题 |
| method | 研究方法 |
| data_source | 数据来源 |
| sample | 样本或案例 |
| theory_or_framework | 理论框架 |
| key_findings | 关键发现 |
| limitations | 研究局限 |
| relevance_to_my_review | 与本综述的相关性 |
| useful_quote | 可引用的原文句子 |
| page_or_section | 页码或章节位置 |
| confidence | 置信度 |
| manual_check_needed | 是否需要人工复核 |

## 工作习惯

- 写脚本前先给出计划
- 批量处理前先跑 3 篇样例论文
- 每一步输出前检查文件是否存在
- 不确定的结论不要写成确定事实
- 修改矩阵结构前先说明影响范围
- 不要一次性处理过多 PDF
- 保持中间文件留痕，方便溯源

## 质量检查

- DOI 和 title 是否明显不匹配
- key_findings 是否过于泛化
- useful_quote 是否缺页码
- manual_check_needed 是否合理
- Excel 是否能正常打开
- 引用 key 和 BibTeX 是否一致
