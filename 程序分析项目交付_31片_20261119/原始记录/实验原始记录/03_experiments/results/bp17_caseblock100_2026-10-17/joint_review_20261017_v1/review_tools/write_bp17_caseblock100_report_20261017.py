"""Render verified case-level outcomes. No model calls or program execution."""
import argparse
from collections import Counter
import json
from pathlib import Path
from verify_bp17_caseblock100_host_20261017 import read, save, need, sha

GROUPS=('BP0','BP1','BP2','BP3')


def render(batch,acceptance,report,data_path):
    joint=read(acceptance);comparison=joint['comparison']
    need(joint['pass'] and joint['audited_jobs']==800 and joint['complete_cases']==100 and not joint['old_results_merged'],'fully_verified_new_batch')
    need(not report.exists() and not data_path.exists(),'fresh_report_and_data')
    records=[r for path in sorted((batch/'case_receipts').glob('*.json')) for r in read(path)['rows']]
    need(len(records)==800 and len({r['job_id'] for r in records})==800,'exact_case_receipt_scope')
    rows=read(batch/'rows.json');case_data=[]
    for row in rows:
        results={g:{t:next(v for v in records if v['case_id']==row['anonymous_id'] and v['group']==g and v['task']==t) for t in ('understanding','repair')} for g in GROUPS}
        case_data.append(dict(case_id=row['anonymous_id'],private_case_id=row['private_case_id'],cluster_root=row['cluster_root'],cohort=row['cohort'],groups=results))
    save(data_path,dict(schema='BP17-caseblock100-joint-verified-case-data-v1',model_identity=joint['model_identity'],
                       acceptance_sha256=sha(acceptance),old_scores_merged=False,cases=case_data))
    lines=['# BP17新指纹100例：同案例四组理解与修复结果','',
           '状态：本批100例/100簇、800次实际回答及800份评分全部完成，并通过Ubuntu保存字节审计、主机独立重算和旧文件保全检查。',
           '开发60例与整簇此前无模型请求的40例新独立确认分别统计。每个案例四组理解及修复均齐全，不与旧指纹结果混算；原始模型回答及候选没有人工改写。','',
           '新独立确认是相对本项目既往调试和模型调用的留出，不保证服务商预训练未见过公开题目或代码。40簇来自剩余未调用池，不能当作全3,258对的无条件代表性估计。','',
           'BP0为完整源码和共同失败信息；BP1再加编译器入口可达行索引；BP2再加结构化函数内CFG证书；BP3用同证书受控中文替代结构化表达。行索引不称语义切片，CFG不称Error Invariant或原FC形式条件。','',
           '理解为P1退出类别、stdout字节数和前64字节同时正确；修复为范围/构建合规且完整原repair与heldout两套均通过。无效模型答案计0，不把触发通过当完整修复。','']
    data={c['case_id']:c for c in case_data}
    for cohort,n,title in [('previously_unexposed',40,'新独立确认'),('exposed_exploratory',60,'开发探索')]:
        scope=[v for v in records if v['cohort']==cohort]
        lines.extend(['## '+title,'',f'共同案例{n}个、独立簇{n}个；理解与修复均采用完全相同的{n}例，各组各一次。','',
                      '| 组 | 理解正确 | 理解正确率 | 无效理解回答 | 完整测试修复 | 修复率 |',
                      '| --- | ---: | ---: | ---: | ---: | ---: |'])
        for g in GROUPS:
            u=comparison['cohorts'][cohort]['understanding']['groups'][g];r=comparison['cohorts'][cohort]['repair']['groups'][g]
            invalid=sum(v['task']=='understanding' and v['group']==g and not v['score']['valid'] for v in scope)
            lines.append(f"| {g} | {u['successes']}/{n} | {u['rate']:.2%} | {invalid} | {r['successes']}/{n} | {r['rate']:.2%} |")
        lines.extend(['','### 预设主要配对比较','',
                      '| 任务 | 左组−右组 | 仅左组成功 | 仅右组成功 | 配对差（百分点） | 95%簇区间（百分点） | Holm校正p |',
                      '| --- | --- | ---: | ---: | ---: | --- | ---: |'])
        for task,label in [('understanding','理解'),('repair','修复')]:
            for contrast,v in comparison['cohorts'][cohort][task]['comparisons'].items():
                ci=v.get('bootstrap_95_percentile');interval=f"[{100*ci[0]:.2f}, {100*ci[1]:.2f}]" if ci else '开发集不作确认推断'
                p=f"{v['holm_p']:.6g}" if 'holm_p' in v else '—'
                lines.append(f"| {label} | {contrast} | {v['left_only']} | {v['right_only']} | {100*v['paired_difference']:+.2f} | {interval} | {p} |")
        lines.extend(['','### 每例四组结果','',
                      'U/R分别为理解正确、完整修复通过，1成功、0失败。所有案例均有真实回答及评分，不用0代填缺失。','',
                      '| 案例 | 原程序对 | BP0 U/R | BP1 U/R | BP2 U/R | BP3 U/R |',
                      '| --- | --- | --- | --- | --- | --- |'])
        for row in rows:
            if row['cohort']!=cohort:continue
            v=data[row['anonymous_id']]
            cells=[]
            for group in GROUPS:
                u=v['groups'][group]['understanding']['score']['correct'];r=int(v['groups'][group]['repair']['status']=='all_tests_passed')
                cells.append(str(u)+'/'+str(r))
            lines.append('| '+' | '.join([row['anonymous_id'],row['private_case_id']]+cells)+' |')
        lines.append('')
    repair=[v for v in records if v['task']=='repair'];success=[v for v in repair if v['status']=='all_tests_passed']
    totals={suite:{key:sum(v['suites'][suite][key] for v in repair) for key in ('planned','executed','passed')} for suite in ('repair','heldout')}
    lines.extend(['## 失败、执行与验证范围','',
                  f"400份候选状态：{json.dumps(dict(Counter(v['status'] for v in repair)),ensure_ascii=False)}。",
                  f"完整通过候选{len(success)}份，涉及{len({v['case_id'] for v in success})}个不同程序对；不能把四组重复成功当不同缺陷。",
                  f"repair测试实际执行{totals['repair']['executed']}次、通过{totals['repair']['passed']}次；heldout实际执行{totals['heldout']['executed']}次、通过{totals['heldout']['passed']}次。",'',
                  '确认集按40独立簇、seed20261017、10,000次同索引重采样报告百分位区间；每种任务内三项主要比较作Holm校正。开发仅描述，不以开发显著性代替确认。','',
                  '主机独立复核实际模型输入/原响应及唯一ID、P1私有真值、候选与原始模型源码相同、原GCC参数、每条保存测试输入/期望/原始输出/正常化和原判题、原终态及旧文件保全；未重跑模型或C。',
                  f"独立审计重算：{json.dumps(joint['counts'],ensure_ascii=False)}。",'',
                  '本结果限于本次任务、模型服务身份和适用样本；行为预测不等于因果故障理解，测试充分修复不等于所有输入语义正确。理解与修复独立请求，不证明理解改善导致修复改善。新旧指纹不合并，不能把跨时间批次差异归因为纯权重升级。', '',
                  f"独立验收SHA256：`{sha(acceptance)}`。",f"同案例数据SHA256：`{sha(data_path)}`。",''])
    report.parent.mkdir(parents=True,exist_ok=True)
    with report.open('x',encoding='utf-8') as f:f.write('\n'.join(lines))
    return dict(report=str(report),data=str(data_path),cases=100,scored=800,old_scores_merged=False)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',type=Path,required=True);p.add_argument('--acceptance',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True);p.add_argument('--data',type=Path,required=True);a=p.parse_args()
    print(json.dumps(render(a.batch,a.acceptance,a.report,a.data)),flush=True)
