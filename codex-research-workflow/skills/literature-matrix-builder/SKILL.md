---
name: literature-matrix-builder
description: 当用户要求"整理文献矩阵""批量读论文""生成综述素材包"时，从 PDF、BibTeX 或 DOI 列表提取文献信息，输出文献矩阵、证据地图和研究缺口报告。
---

# Literature Matrix Builder

## 输入

- 默认读取 `data/raw-pdfs/`
- 可选读取 `data/references/*.bib`
- 可选读取 `matrix/seed_references.csv`

## 输出

- `matrix/literature_matrix.xlsx`
- `matrix/literature_matrix.csv`
- `reports/evidence_map.md`
- `reports/research_gaps.md`
- `reports/literature_review_brief.md`

## 字段

| 字段 | 必填 | 说明 |
|------|------|------|
| citation_key | 是 | 引用键，与 BibTeX 一致 |
| title | 是 | 论文标题 |
| authors | 是 | 作者列表 |
| year | 是 | 出版年份 |
| venue | 是 | 期刊/会议/预印本 |
| doi | 是 | 数字对象标识符 |
| research_question | 是 | 研究问题 |
| method | 是 | 研究方法 |
| data_source | 否 | 数据来源 |
| sample | 否 | 样本或案例 |
| theory_or_framework | 否 | 理论框架 |
| key_findings | 是 | 关键发现 |
| limitations | 否 | 研究局限 |
| relevance_to_my_review | 是 | 与本综述的相关性 |
| useful_quote | 否 | 可引用的原文句子 |
| page_or_section | 否 | 页码或章节位置 |
| confidence | 是 | 置信度 |
| manual_check_needed | 是 | 是否需要人工复核 |

## 规则

- 不覆盖原始 PDF
- 不编造引用、页码、DOI
- 缺失信息标记 `unknown`
- 批量处理前先跑 3 篇样例
- 输出前检查 Excel、CSV 和 Markdown 是否生成成功
- 从 `.env.local` 读取 API Key
- 不出现在代码、日志、README 中泄露凭据

## 元数据补全来源优先级

1. Crossref（适合补全标题、作者、年份、期刊）
2. OpenAlex（适合补全摘要、研究领域、引用关系）
3. Semantic Scholar（适合补全引用统计、TLDR 摘要）

## 处理流程

1. 读取输入，确认文件是否存在
2. 如无现有矩阵，创建新矩阵；如有，确认是否覆盖
3. 先处理 3 篇样例，输出样例矩阵供审查
4. 审查通过后批量处理其余文献
5. 输出文献矩阵、证据地图、研究缺口报告
6. 运行质量检查，生成问题清单
