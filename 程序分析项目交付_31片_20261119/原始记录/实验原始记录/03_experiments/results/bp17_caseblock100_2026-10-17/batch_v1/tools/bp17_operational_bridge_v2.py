"""Operational status fix only; frozen request, scope, scorer and tests unchanged.

The original evaluator already rejects a changed preprocessor directive. The
old orchestration's substring 'changed' incorrectly called this infrastructure.
Only known candidate-scope rejection labels are classified as such here.
"""
import argparse
import copy
import json
import os
from pathlib import Path
import sys
import run_bp17_v3_experiment as r

VERSION='BP17-operational-bridge-v2'
SCOPE_REJECTIONS=frozenset(('candidate_source_bound','preprocessor_directives_changed','new_external_access_or_assembly',
                           'strict_source_JSON','duplicate_JSON_key'))


def classify(value,output,record):
    out=r.summarize_candidate(value,output,record)
    if value['status']=='rejected' and value.get('reason') in SCOPE_REJECTIONS:
        out['status']='rejected'
    return out


def corrected_saved_score(old,evaluation):
    out=copy.deepcopy(old)
    if old['status']=='infrastructure_failure' and evaluation['status']=='rejected' and evaluation.get('reason') in SCOPE_REJECTIONS:
        r.need(not evaluation['candidate_tests'] and old['repair_pass'] is False and old['heldout_pass'] is False,
               'scope_rejection_has_no_candidate_execution')
        out['status']='rejected'
        out['operational_correction']=dict(version=VERSION,original_status=old['status'],
            reason='candidate scope rejection is not infrastructure failure',underlying_candidate_evaluation_unchanged=True,
            candidate_reexecutions=0,model_retries=0)
    r.need(out['status']!='infrastructure_failure','real_infrastructure_failure_still_stops')
    return out


def status(batch):
    value=r.remote_status(batch)
    value.update(operational_bridge_version=VERSION,operational_bridge_sha256=r.sha(Path(__file__)))
    return value


def evaluate(batch,payload,reconcile=False):
    import fcntl
    status(batch)
    lock=(batch.parent/'bp17_candidate_evaluation.lock').open('a+b')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    numeric,classification,candidate=r.remote_imports(batch)
    plan=r.read(batch/'plan.json');rows={x['anonymous_id']:x for x in plan['rows']};jobs={x['job_id']:x for x in plan['jobs']}
    answers=payload['responses'];result=[]
    r.need(0<len(answers)<=4 and len({v['job_id'] for v in answers})==len(answers),'exact_small_wave')
    for response in answers:
        r.resource_guard(batch);r.identity(response,payload['model_identity'])
        j=jobs[response['job_id']];case=rows[j['case_id']]
        r.need(all(response[k]==j[k] for k in ('case_id','group','task','request_sha256')),'saved_response_scope')
        directory=batch/'cohorts'/case['cohort']/j['case_id']/j['group']/j['task']
        if directory.exists():
            r.need(reconcile and (directory/'scored.json').is_file(),'partial_or_duplicate_evaluation_refused')
            r.need(r.read(directory/'response.json')==response,'existing_response_not_identical')
            prior=r.read(directory/'scored.json')
            if prior['status']=='infrastructure_failure':
                evaluation=r.read(directory/'candidate/evaluation.json')
                r.need(r.sha(directory/'candidate/evaluation.json')==prior['evaluation_sha256'],'underlying_rejection_changed')
                row=corrected_saved_score(prior,evaluation)
                row['operational_correction']['original_scored_sha256']=r.sha(directory/'scored.json')
                r.save(directory/'scored_operational_v2.json',row)
            else:
                row=prior
            result.append(row);continue
        directory.mkdir(parents=True)
        r.save(directory/'response.json',response)
        row={k:j[k] for k in ('job_id','case_id','group','task','request_sha256')}
        row.update(cohort=case['cohort'],cluster_root=case['cluster_root'],understanding_kind=case['understanding_kind'],scored_utc=r.now())
        private=r.REMOTE_ROOT/'all_target_v3'/j['case_id']
        for name,h in plan['private_hashes'][j['case_id']].items():
            r.need(r.sha(private/name)==h,'private_frozen_scoring_record_changed')
        if j['task']=='understanding':
            scorer=numeric.score if case['understanding_kind']=='native_behavior_projection' else classification.score
            score=scorer(response['content'],r.read(private/'answers_private.json'))
            row.update(status='scored' if score['valid'] else 'invalid_answer',score=score)
        else:
            path=r.NATIVE/'runs/cases'/case['private_case_id']/'result.json'
            r.need(r.sha(path)==plan['native_result_hashes'][j['case_id']],'native_record_changed')
            record=r.read(path);value=candidate.evaluate(response['content'],record,directory/'candidate')
            row.update(classify(value,directory/'candidate',record))
        row['operational_bridge_version']=VERSION
        r.save(directory/'scored.json',row);result.append(row)
        r.need(row['status']!='infrastructure_failure','candidate_evaluation_infrastructure_failure')
    receipt=dict(**{'pass':True},wave=payload['wave'],rows=result,scored_count=len(result),model_calls=0,
        baseline_C_reexecutions=0,original_tests_judge_changed=False,ended_utc=r.now(),operational_bridge_version=VERSION,
        operational_bridge_sha256=r.sha(Path(__file__)),already_scored_candidates_reexecuted=0)
    name='wave_'+str(payload['wave']).zfill(5)+'.json'
    r.save(batch/'wave_receipts_operational_v2'/name,receipt)
    # New future waves also have a standard receipt for read-only recovery.
    if not (batch/'wave_receipts'/name).exists():r.save(batch/'wave_receipts'/name,receipt)
    lock.close();return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('remote-status','remote-evaluate','remote-reconcile','remote-finish'))
    p.add_argument('--batch',type=Path,required=True);a=p.parse_args()
    try:
        if a.mode=='remote-status':value=status(a.batch)
        elif a.mode=='remote-finish':value=r.remote_finish(a.batch)
        else:value=evaluate(a.batch,json.load(sys.stdin),a.mode=='remote-reconcile')
        print(json.dumps(value,ensure_ascii=False),flush=True)
    except Exception as e:
        print(json.dumps({'pass':False,'error':str(e) if type(e) is ValueError else type(e).__name__}),flush=True)
        raise SystemExit(1)
