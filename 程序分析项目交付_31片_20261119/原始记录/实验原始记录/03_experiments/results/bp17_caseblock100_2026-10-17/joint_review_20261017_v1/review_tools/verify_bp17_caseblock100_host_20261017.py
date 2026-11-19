"""Independent host record/byte audit and paired result table. No execution/API."""
from collections import Counter
import gzip
import hashlib
import importlib.util
import json
import math
from pathlib import Path, PurePosixPath
import random
import re
import shutil
import sys
import tarfile

PIN = dict(model_returned='deepseek-flash',system_fingerprint='e72d3c7f663d3e1383b00b3884cb4501')
CHECKER_SHA='f2b005c8e7f9c9a28df125411b4d357e79e3e045c576da1b474230d225f9bdd5'
MANIFEST_SHA='16e5e8094a2a2dae0241a218f47b647eaeb105970e704795c142ef895a3c08a8'


def need(ok, why):
    if not ok: raise ValueError(why)


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()


def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))


def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')


def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)


def unpack(archive, manifest, output):
    need(not output.exists(),'fresh_unpack_directory');output.mkdir(parents=True)
    seen=set()
    with tarfile.open(archive,'r|gz') as tar:
        for member in tar:
            parts=PurePosixPath(member.name)
            need(member.isfile() and not parts.is_absolute() and all(p not in ('..','.') for p in parts.parts) and
                 '\\' not in member.name and ':' not in member.name and member.name in manifest and member.name not in seen,'safe_unique_archive_member')
            need(member.size <= 256*1024**2,'bounded_archive_member')
            target=output.joinpath(*parts.parts);need(target.resolve().is_relative_to(output.resolve()),'archive_path_inside_root')
            target.parent.mkdir(parents=True,exist_ok=True);h=hashlib.sha256();stream=tar.extractfile(member);size=0
            with target.open('xb') as dest:
                for chunk in iter(lambda:stream.read(1024**2),b''):dest.write(chunk);h.update(chunk);size+=len(chunk)
            need(size==member.size and h.hexdigest()==manifest[member.name],'archive_member_bytes')
            seen.add(member.name)
    need(seen==set(manifest),'archive_exact_members')
    with gzip.open(archive,'rb') as stream:
        for _ in iter(lambda:stream.read(1024**2),b''):pass
    return len(seen)


def strict_json(text):
    def pairs(items):
        need(len(items)==len(dict(items)),'duplicate_JSON_key');return dict(items)
    return json.loads(text,object_pairs_hook=pairs)


def score_p1(text,truth):
    result=dict(valid=False,correct=0,total=1,components_correct=0,components_total=3)
    try:
        obj=strict_json(text);need(isinstance(obj,dict) and set(obj)=={'answers'} and isinstance(obj['answers'],list) and len(obj['answers'])==1,'answer_schema')
        value=obj['answers'][0]
        need(isinstance(value,dict) and set(value)=={'id','exit_class','stdout_bytes','stdout_prefix_hex'} and value['id']=='P1','answer_fields')
        need(value['exit_class'] in ('normal_exit','runtime_error') and type(value['stdout_bytes']) is int and 0<=value['stdout_bytes']<1024**2,'behavior_fields')
        h=value['stdout_prefix_hex'];need(isinstance(h,str) and re.fullmatch('[0-9a-f]*',h) is not None and len(h)==2*min(64,value['stdout_bytes']),'hex_prefix')
        n=sum(value[k]==truth[k] for k in ('exit_class','stdout_bytes','stdout_prefix_hex'))
        result.update(valid=True,correct=int(n==3),components_correct=n)
    except (ValueError,TypeError,KeyError):pass
    return result


def observation_status(execution,equal):
    if execution.get('infra_error'):return 'infra_error'
    if execution['timeout']:return 'timeout'
    if execution['output_limited']:return 'output_limited'
    if execution['returncode']!=0:return 'runtime_error'
    return 'pass' if equal else 'output_mismatch'


def scope(source,original):
    need(isinstance(source,str) and len(source.encode())<=240000,'candidate_source_bound')
    directives=lambda x:re.findall(r'^\s*#.*(?:\\\n[^\n]*)*',x,re.M)
    need(directives(source)==directives(original),'preprocessor_directives_changed')
    denied=r'\b(?:system|popen|exec\w*|fork|socket|connect|dlopen|dlsym|mprotect|__asm__|asm)\b'
    need(set(re.findall(denied,source))<=set(re.findall(denied,original)),'new_external_access_or_assembly')


def verify(batch,payload,context,output):
    need(not output.exists(),'fresh_verification_output')
    need(sha(batch/'execution_manifest.json')==MANIFEST_SHA,'execution_manifest')
    manifest=read(batch/'execution_manifest.json');rows=read(batch/'rows.json');jobs=read(batch/'jobs.json')
    need(sha(batch/'jobs.json')==manifest['jobs_sha256'] and sha(batch/'rows.json')==manifest['rows_sha256'],'host_frozen_jobs_rows')
    need(sha(batch/'before_old_files.json')==manifest['old_preservation_sha256'],'old_preservation_map_identity')
    need(sha(batch/'prior_response_ids.json')==manifest['prior_response_ids_sha256'],'prior_response_identity_map')
    prior_ids=set(read(batch/'prior_response_ids.json'))
    old_batch=Path(manifest['source_batch']);old_rows=read(old_batch/'rows.json')
    need(sha(old_batch/'attempt_ledger.jsonl')==manifest['source_ledger_sha256'],'original_exposure_ledger_unchanged')
    old_ledger=[json.loads(x) for x in (old_batch/'attempt_ledger.jsonl').read_text().splitlines() if x]
    old_map={v['anonymous_id']:v for v in old_rows};exposed_clusters={old_map[v['case_id']]['cluster_root'] for v in old_ledger}
    selected=[];seed='BP17-block100-20261017-v1';rank=lambda text:hashlib.sha256(text.encode()).hexdigest()
    for cohort,n in [('exposed_exploratory',60),('previously_unexposed',40)]:
        clusters={}
        for row in old_rows:
            if row['cohort']==cohort and row['understanding_kind']=='native_behavior_projection' and not (cohort=='previously_unexposed' and row['cluster_root'] in exposed_clusters):
                clusters.setdefault(row['cluster_root'],[]).append(row)
        for cluster in sorted(clusters,key=lambda c:rank(seed+'/selection/'+cohort+'/'+c))[:n]:
            selected.append(min(clusters[cluster],key=lambda r:rank(seed+'/representative/'+r['anonymous_id'])))
    selected.sort(key=lambda row:rank(seed+'/case-order/'+row['anonymous_id']))
    need(rows==selected and len({r['cluster_root'] for r in rows})==100,'independent_frozen_selection_and_no_cross_cohort_clusters')
    plan=read(context/'plan.json');need(plan['jobs']==jobs and plan['rows']==rows and plan['host_manifest_sha256']==MANIFEST_SHA,'cross_endpoint_plan')
    checker_path=context/'codeflaws_byte_comparison_v2.py';need(sha(checker_path)==CHECKER_SHA,'portable_checker_identity')
    spec=importlib.util.spec_from_file_location('portable_independent_checker',checker_path);checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    rowmap={v['anonymous_id']:v for v in rows};scoremap={};receipts=[]
    for path in sorted((batch/'evaluation_receipts').glob('wave_*.json')):
        receipt=read(path);need(receipt['pass'] and receipt['scored_count']==len(receipt['rows']),'wave_receipt')
        for score in receipt['rows']:
            need(score['job_id'] not in scoremap,'duplicate_host_score');scoremap[score['job_id']]=score
    need(len(scoremap)==800 and set(scoremap)=={j['job_id'] for j in jobs},'exact_800_scores')
    ledger=[json.loads(x) for x in (batch/'attempt_ledger.jsonl').read_text().splitlines() if x]
    need([v['job_id'] for v in ledger]==[j['job_id'] for j in jobs] and [v['cumulative_ordinal'] for v in ledger]==list(range(5694,6494)),'exact_once_ledger')
    response_ids=set();counts=Counter();evidence={};evaluated=[]
    for job in jobs:
        row=rowmap[job['case_id']];case=job['case_id'];score=scoremap[job['job_id']]
        host=batch/'cohorts'/row['cohort']/'responses'/case/job['group']/job['task']
        guest=payload/'cohorts'/row['cohort']/case/job['group']/job['task']
        response=read(host/'result.json');raw=read(host/'raw_response.json');request=read(host/'request.json')
        need(response['status']=='completed' and all(response[k]==v for k,v in PIN.items()),'one_new_model_identity')
        need(all(response[k]==job[k] for k in ('job_id','case_id','group','task','request_sha256')) and
             all(score[k]==job[k] for k in ('job_id','case_id','group','task','request_sha256')),'saved_job_binding')
        need(all(score[k]==row[k] for k in ('cohort','cluster_root','understanding_kind')),'independent_score_cohort_binding')
        need(hashlib.sha256(canonical(request)).hexdigest()==job['request_sha256'] and request==job['request'],'exact_actual_model_input')
        need(sha(host/'raw_response.json')==response['raw_sha256'] and raw['id']==response['response_id'] and
             raw['model']==PIN['model_returned'] and raw['system_fingerprint']==PIN['system_fingerprint'] and
             raw['choices'][0]['message']['content']==response['content'],'raw_API_projection')
        need(response['response_id'] not in response_ids,'unique_response_ID');response_ids.add(response['response_id'])
        need(response['response_id'] not in prior_ids,'no_old_answer_reused_in_new_batch')
        need(read(guest/'response.json')==response and read(guest/'scored.json')==score,'cross_endpoint_response_score')
        source_context=context/'cases'/case;truth=read(source_context/'answers_private.json')
        need(sha(source_context/'answers_private.json')==plan['private_hashes'][case]['answers_private.json'],'private_truth_identity')
        if job['task']=='understanding':
            need(score_p1(response['content'],truth)==score['score'],'independent_P1_score')
            need(score['status']==('scored' if score['score']['valid'] else 'invalid_answer'),'P1_invalid_status')
            counts['understanding_recomputed']+=1
        else:
            record=read(source_context/'native_result.json');native_hash=sha(source_context/'native_result.json')
            need(native_hash==plan['native_result_hashes'][case]==read(source_context/'native_receipt.json')['result_sha256'],'native_receipt_identity')
            need(record['status']=='pair_reproduced' and record['case_id']==row['private_case_id'] and
                 sha(source_context/'buggy.c')==row['source_sha256']==record['metadata']['source_hashes']['buggy'],'original_source_identity')
            candidate=guest/'candidate';evaluation=read(candidate/'evaluation.json')
            need(sha(candidate/'evaluation.json')==score['evaluation_sha256'],'candidate_evaluation_identity')
            valid_source=None
            try:
                obj=strict_json(response['content']);need(isinstance(obj,dict) and set(obj)=={'source'} and isinstance(obj['source'],str),'strict_source_JSON')
                scope(obj['source'],(source_context/'buggy.c').read_text(encoding='utf-8'))
                valid_source=obj['source']
            except (ValueError,TypeError,KeyError):
                need(evaluation['status']=='rejected' and not evaluation['candidate_tests'],'independent_scope_rejection')
            if valid_source is not None:
                comp=read(candidate/'compilation.json');filename=Path(record['metadata']['buggy']).name
                need((candidate/'build'/filename).read_bytes()==valid_source.encode('utf-8') and
                     sha(candidate/'build'/filename)==comp['source_sha256'],'untouched_model_candidate')
                for stage,expected in [('compile',['/usr/bin/gcc',*record['recipe']['cflags'],'-c',filename,'-o','program.o']),('link',['/usr/bin/gcc','program.o','-o','program',*record['recipe']['ldflags']])]:
                    obs=comp[stage]
                    if obs is None:need(stage=='link' and evaluation['status']=='rejected','missing_compile_stage');continue
                    need(obs['command'][obs['command'].index('--')+1:]==expected,'exact_original_build_flags')
                    for stream in ('stdout','stderr'):need(sha(candidate/stage/(stream+'.bin'))==obs[stream+'_sha256'],'compiler_log_bytes')
                counts['candidate_sources_bound']+=1
            index={(x['suite'],x['id']):x for x in read(source_context/'test_index.json')}
            expected={(suite,t['id']):t for suite,ts in record['metadata']['suites'].items() for t in ts}
            need(set(index)==set(expected),'original_full_test_index')
            tests=evaluation['candidate_tests'];keys=[(t['suite'],t['id']) for t in tests]
            need(len(keys)==len(set(keys)) and set(keys)<=set(expected),'unique_native_test_ids')
            if evaluation['status'] in ('all_tests_passed','test_failed'):
                need(set(keys)==set(expected),'all_original_tests_executed')
                need(valid_source is not None and all(comp[s] is not None and comp[s]['returncode']==0 and not any(comp[s][k] for k in ('timeout','output_limited','resource_stop')) for s in ('compile','link')),'both_build_stages_pass')
            suite_counts={s:dict(planned=len(ts),executed=0,passed=0) for s,ts in record['metadata']['suites'].items()}
            statuses=Counter()
            for test in tests:
                key=(test['suite'],test['id']);item=index[key];original=expected[key]
                for role in ('input','expected'):need(sha(source_context/item[role])==item[role+'_sha256']==original[role+'_sha256'],'original_test_bytes')
                folder=candidate/('test_'+test['suite']+'_'+test['id']);obs=test['execute'];output_bytes=(folder/'stdout.bin').read_bytes()
                need(hashlib.sha256(output_bytes).hexdigest()==obs['stdout_sha256'] and output_bytes.hex()==obs['stdout_hex'] and len(output_bytes)==obs['stdout_bytes'] and
                     sha(folder/'stderr.bin')==obs['stderr_sha256'] and not obs['resource_stop'],'actual_saved_test_output')
                profile=record['recipe']['suites'][test['suite']]['normalizer'];normalized=checker.normalize_bytes(output_bytes,profile)
                equal=checker.portable_equal(output_bytes,(source_context/item['expected']).read_bytes(),profile)
                need(test['comparison']['valid'] and test['comparison']['equal']==equal and test['comparison']['profile']==profile and
                     hashlib.sha256(normalized).hexdigest()==test['comparison']['normalized_sha256']==sha(folder/'normalized_stdout'),'independent_original_judge')
                status=observation_status(obs,equal);need(status==test['status'] and test['pass']==(status=='pass'),'test_status_recomputed')
                suite_counts[test['suite']]['executed']+=1;suite_counts[test['suite']]['passed']+=int(status=='pass');statuses[status]+=1
                counts['candidate_tests_recomputed']+=1;counts['candidate_'+test['suite']+'_tests_recomputed']+=1
            need(score['suites']==suite_counts and score['candidate_failure_statuses']==dict(statuses),'score_test_totals')
            trigger=sorted(t['id'] for t in record['tests'] if t['suite']=='repair' and t['sides']['buggy']['status'] in ('runtime_error','output_mismatch'))[0]
            trigger_test=next((t for t in tests if t['suite']=='repair' and t['id']==trigger),None)
            need(score['trigger_pass']==(None if trigger_test is None else trigger_test['pass']),'trigger_pass_recomputed')
            for suite in ('repair','heldout'):
                v=suite_counts[suite];full=v['planned']>0 and v['planned']==v['executed']==v['passed']
                need(score[suite+'_pass']==full,'strict_full_suite_pass')
            need(score['status']==evaluation['status'] and score['status']!='infrastructure_failure','candidate_terminal_classification')
            need((score['status']=='all_tests_passed')==(score['repair_pass'] and score['heldout_pass']),'full_test_success_not_trigger_only')
            counts['repair_recomputed']+=1
        evidence[job['job_id']]=dict(result_sha256=sha(host/'result.json'),request_sha256=sha(host/'request.json'),raw_sha256=sha(host/'raw_response.json'))
        evaluated.append(score)
    need(counts['understanding_recomputed']==counts['repair_recomputed']==400,'all_800_recomputed')
    for row in rows:need(sum(v['case_id']==row['anonymous_id'] for v in evaluated)==8,'all_cases_eight_complete')
    for name,expected in read(batch/'before_old_files.json')['files'].items():need(sha(Path(name))==expected,'old_file_preservation')
    comparison=read(batch/'comparison.json');need(comparison['model_identity']==PIN and not comparison['old_scores_merged'],'new_only_comparison')
    for cohort,n in [('exposed_exploratory',60),('previously_unexposed',40)]:
        for task in ('understanding','repair'):
            grouped={}
            for group in ('BP0','BP1','BP2','BP3'):
                subset=[v for v in evaluated if v['cohort']==cohort and v['task']==task and v['group']==group]
                grouped[group]={v['case_id']:(v['score']['correct'] if task=='understanding' else int(v['status']=='all_tests_passed')) for v in subset}
                success=sum(v['score']['correct'] if task=='understanding' else v['status']=='all_tests_passed' for v in subset)
                value=comparison['cohorts'][cohort][task]['groups'][group]
                need(len(subset)==n and value['n']==n and value['successes']==success and value['rate']==success/n,'independent_group_totals')
            common=sorted(set.intersection(*(set(v) for v in grouped.values())))
            need(len(common)==n,'independent_all_four_common_cases')
            p_values={}
            for left,right in [('BP2','BP1'),('BP3','BP2'),('BP1','BP0')]:
                key=left+'-'+right;v=comparison['cohorts'][cohort][task]['comparisons'][key]
                diffs=[grouped[left][case]-grouped[right][case] for case in common]
                wins=diffs.count(1);losses=diffs.count(-1)
                need(v['cases']==v['clusters']==n and v['left_only']==wins and v['right_only']==losses and
                     v['paired_difference']==sum(diffs)/n and v['left_successes']==sum(grouped[left].values()) and
                     v['right_successes']==sum(grouped[right].values()),'independent_paired_counts')
                if cohort=='previously_unexposed':
                    discordant=wins+losses
                    p_values[key]=min(1,2*sum(math.comb(discordant,k) for k in range(min(wins,losses)+1))/2**discordant) if discordant else 1
                    need(v['exact_p']==p_values[key],'independent_exact_p')
                    rng=random.Random(20261017)
                    samples=sorted(sum(diffs[rng.randrange(n)] for _ in range(n))/n for _ in range(10000))
                    need(v['bootstrap_95_percentile']==[samples[249],samples[9749]],'independent_cluster_interval')
            running=0
            for position,key in enumerate(sorted(p_values,key=p_values.get)):
                running=max(running,min(1,(3-position)*p_values[key]))
                need(comparison['cohorts'][cohort][task]['comparisons'][key]['holm_p']==running,'independent_Holm_adjustment')
    result=dict(schema='BP17-caseblock100-independent-host-saved-byte-audit-v1',**{'pass':True},errors=[],audited_jobs=800,complete_cases=100,
                counts=dict(counts),model_identity=PIN,old_results_merged=False,model_calls=0,candidate_C_reexecutions=0,
                auditor_sha256=sha(Path(__file__)),checked_response_records=evidence,comparison=comparison)
    output.mkdir(parents=True);save(output/'joint_acceptance.json',result);return result


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--batch',type=Path,required=True);p.add_argument('--payload',type=Path,required=True);p.add_argument('--context',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    value=verify(a.batch,a.payload,a.context,a.output);print(json.dumps({k:value[k] for k in ('pass','audited_jobs','complete_cases','counts','model_calls','candidate_C_reexecutions')}),flush=True)
