"""Finite 3158-case continuation. Frozen inputs/scorers; no API/C retries.

The independently accepted 100-case prefix is read-only, not reissued. Shards
are sealed every100 cases to bound archive memory. No new confirmation claim.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time
import unittest
import run_bp17_v3_experiment as r
import bp17_operational_bridge_v2 as bridge
import bp17_caseblock100_20261017_v1 as base
from recover_bp17_archive_only_20261017_v1 import stream_pack, check_archive

HERE=Path(__file__).resolve().parent
EXEC_ID='BP17-caseblocked-remainder-20261017-v1'
BATCH_ID='BP17-remainder-model-20261017-v1'
REMOTE='/home/vboxuser/bp17_remainder_20261017_v1'
REMOTE_TOOLS='/home/vboxuser/bp17_remainder_tools_20261017_v1'
SEED=base.SEED;PIN=base.PIN;CHECKER=base.CHECKER;CHECKER_SHA=base.CHECKER_SHA
PAIRS=3158;CALLS=PAIRS*8;CUMULATIVE_BEFORE=6493
PREFIX_ACCEPTANCE_SHA='a5ff40eef7c65091d260653c9af2f7d0a4850cb287033ee729ab8b24ac1de85c'
PREFIX_MANIFEST_SHA='16e5e8094a2a2dae0241a218f47b647eaeb105970e704795c142ef895a3c08a8'
FILES=('bp17_caseblocked_remainder_20261017_v1.py','test_bp17_caseblocked_remainder_20261017_v1.py',
       'audit_bp17_remainder_saved_20261017_v1.py','recover_bp17_archive_only_20261017_v1.py',
       'bp17_caseblock100_20261017_v1.py','run_bp17_v3_experiment.py','bp17_operational_bridge_v2.py',
       'cgo16_candidate_isolated_v2.py','check_fc_extension_baseline_preservation.py')


def metadata(job): return {k:v for k,v in job.items() if k!='request'}


def case_jobs(row,frozen):
    r.need(len(frozen)==8,'eight_source_jobs');result=[]
    for source in frozen:
        r.validate_request(source);r.need(source['case_id']==row['anonymous_id'],'source_case_binding')
        job=dict(source,source_job_id=source['job_id'],scientific_protocol_id=source['protocol_id'],protocol_id=EXEC_ID,
                 job_id='/'.join((EXEC_ID,row['anonymous_id'],source['group'],source['task'],'1')))
        result.append(job)
    r.need({(x['group'],x['task']) for x in result}=={(g,t) for g in r.GROUPS for t in r.TASKS},'complete_four_group_tasks')
    return sorted(result,key=lambda x:base.hashed(SEED+'/within-case/'+x['group']+'/'+x['task']+'/'+x['case_id']))


def validate_blocks(rows,jobs,prefix_ids,expected=PAIRS):
    ids={x['anonymous_id'] for x in rows}
    r.need(len(rows)==len(ids)==expected and not ids & set(prefix_ids),'unique_remaining_no_prefix_reissue')
    r.need(len(jobs)==len({x['job_id'] for x in jobs})==8*expected,'finite_unique_slots')
    for i,row in enumerate(rows):
        r.need(row['cohort'] in r.COHORTS and row['understanding_kind'] in ('native_behavior_projection','uninitialized_read_classification'),'frozen_cohort_and_kind')
        block=jobs[i*8:i*8+8]
        r.need({j['case_id'] for j in block}=={row['anonymous_id']} and
               {(j['group'],j['task']) for j in block}=={(g,t) for g in r.GROUPS for t in r.TASKS},'complete_contiguous_block')
        for j in block:
            r.need(j['protocol_id']==EXEC_ID and j['job_id']=='/'.join((EXEC_ID,j['case_id'],j['group'],j['task'],'1')),'new_job_identity')
            r.need(j['source_job_id']=='/'.join((r.ID,j['case_id'],j['group'],j['task'],'1')) and j['scientific_protocol_id']==r.ID,'unchanged_scientific_protocol')
    return True


def prepare(project,batch):
    project=project.resolve();batch=batch.resolve()
    source=project/'03_experiments/results/bp17_model_2026-10-16/batch_v1'
    prefix_root=project/'03_experiments/results/bp17_caseblock100_2026-10-17';prefix=prefix_root/'batch_v1'
    r.need(not batch.exists() and not batch.is_relative_to(source.parent) and not batch.is_relative_to(prefix_root),'fresh_separate_remainder')
    r.need(r.sha(source/'execution_manifest.json')==base.SOURCE_MANIFEST_SHA and r.sha(prefix/'execution_manifest.json')==PREFIX_MANIFEST_SHA,'original_frozen_manifests')
    acceptance=prefix_root/'joint_review_20261017_v1/acceptance/joint_acceptance.json'
    r.need(r.sha(acceptance)==PREFIX_ACCEPTANCE_SHA and r.read(acceptance)['pass'] and r.read(prefix_root/'joint_review_20261017_v1/completion.json')['pass'],'accepted_100_prefix')
    with base.global_lock(source.parent/'bp17_live_transport.lock'):
        original,_=r.verify_local(source)
        all_rows=r.read(source/'rows.json');old_rows={v['anonymous_id']:v for v in all_rows};completed=r.read(prefix/'rows.json');done={v['anonymous_id'] for v in completed}
        r.need(len(done)==100 and all(old_rows[v['anonymous_id']]==v for v in completed),'exact_frozen_prefix_rows')
        rows=sorted([v for v in all_rows if v['anonymous_id'] not in done],key=lambda x:base.hashed(SEED+'/case-order/'+x['anonymous_id']))
        jobs=[];input_hashes={}
        for row in rows:
            path=source/'inputs'/row['anonymous_id']/'group_requests_NOT_SENT.json'
            r.need(r.sha(path)==original['inputs'][path.relative_to(source).as_posix()],'frozen_remaining_request')
            input_hashes[str(path)]=r.sha(path);jobs.extend(metadata(j) for j in case_jobs(row,r.read(path)))
        validate_blocks(rows,jobs,done)
        r.need(Counter(v['cohort'] for v in rows)==Counter(exposed_exploratory=1798,previously_unexposed=1360),'remaining_cohorts')
        r.need(Counter(v['understanding_kind'] for v in rows)==Counter(native_behavior_projection=3145,uninitialized_read_classification=13),'remaining_P1_U1')
        old_ledger=[json.loads(v) for v in (source/'attempt_ledger.jsonl').read_text().splitlines() if v]
        called={old_rows[v['case_id']]['cluster_root'] for v in old_ledger};prefix_clusters={v['cluster_root'] for v in completed}
        exposure={v['anonymous_id']:dict(original_cohort=v['cohort'],cluster_root=v['cluster_root'],
            prior_old_batch_call=v['cluster_root'] in called,prefix100_cluster_call=v['cluster_root'] in prefix_clusters,
            new_independent_confirmation_eligible=v['cohort']=='previously_unexposed' and v['cluster_root'] not in called|prefix_clusters) for v in rows}
        r.need(not any(v['new_independent_confirmation_eligible'] for v in exposure.values()),'no_new_confirmation_claim')
        prior=r.read(prefix/'before_old_files.json')['files'].copy()
        for p in prefix_root.rglob('*'):
            if p.is_file() and p.suffix!='.lock' and '__pycache__' not in p.parts and not any(x in p.parts for x in ('payload','context')):
                prior[str(p)]=r.sha(p)
        old_ids=set(r.read(prefix/'prior_response_ids.json'))
        for p in (prefix/'cohorts').glob('*/*/*/*/*/result.json'):
            v=r.read(p);r.need(v['status']=='completed' and v['response_id'] not in old_ids,'prefix_actual_unique_response');old_ids.add(v['response_id'])
        r.need(len(old_ids)==6491,'prior_6491_actual_answers')
        batch.parent.mkdir(parents=True,exist_ok=True);r.resource_guard(batch.parent);batch.mkdir()
        for name in FILES:(batch/'tools').mkdir(exist_ok=True);shutil.copy2(HERE/name,batch/'tools'/name)
        r.save(batch/'rows.json',rows);r.save(batch/'jobs.json',jobs);r.save(batch/'exposure.json',exposure)
        r.save(batch/'before_old_files.json',dict(files=prior,count=len(prior),decompressed_duplicate_copies_excluded=True))
        r.save(batch/'prior_response_ids.json',sorted(old_ids))
        r.save(batch/'prefix100.json',dict(prefix_root=str(prefix_root),case_ids=sorted(done),manifest_sha256=PREFIX_MANIFEST_SHA,acceptance_sha256=PREFIX_ACCEPTANCE_SHA,
            accepted_response_count=800,accepted_score_count=800,no_reissue=True))
        r.save(batch/'authorization.json',dict(user_instruction='继续跑剩余的',clarified_scope='3158 remaining pairs,25264 new tasks; accepted100 not reissued',
            authorized_calls=CALLS,endpoint=r.ENDPOINT,data_scope='unchanged frozen buggy C,visible failure diagnostics,compiler evidence,public P1/U1',
            private_answers_reference_patches_hidden_tests_excluded=True,automatic_retries=0))
        shutil.copy2(project/'01_research/workflow/bp17_caseblocked_remainder_protocol_2026-10-17_v1.md',batch/'protocol.md')
        hashes={name:r.sha(batch/name) for name in ('rows.json','jobs.json','exposure.json','before_old_files.json','prior_response_ids.json','prefix100.json','authorization.json','protocol.md')}
        manifest=dict(schema=EXEC_ID,batch_id=BATCH_ID,frozen_utc=r.now(),planned_pairs=PAIRS,planned_calls=CALLS,model_identity=PIN,
            request_parameters=r.PARAMS,endpoint=r.ENDPOINT,source_batch=str(source),remote_output=REMOTE,remote_tools=REMOTE_TOOLS,
            identity_file='C:/Users/chenm/.ssh/codex_ubuntu2204',source_manifest_sha256=base.SOURCE_MANIFEST_SHA,
            prefix_acceptance_sha256=PREFIX_ACCEPTANCE_SHA,source_inputs=input_hashes,metadata_hashes=hashes,
            files={n:r.sha(batch/'tools'/n) for n in FILES},old_reserved_calls=CUMULATIVE_BEFORE,cumulative_max_slots=CUMULATIVE_BEFORE+CALLS,
            automatic_retries=0,feedback_rounds=0,original_cohorts_preserved=True,new_confirmation_cases=0,
            original_cohort_counts=dict(Counter(x['cohort'] for x in rows)),understanding_kinds=dict(Counter(x['understanding_kind'] for x in rows)))
        r.save(batch/'execution_manifest.json',manifest)
        return dict(**{'pass':True},cases=PAIRS,calls=CALLS,prefix100_not_reissued=True,preserved_files=len(prior),manifest_sha256=r.sha(batch/'execution_manifest.json'))


def verified(batch):
    m=r.read(batch/'execution_manifest.json')
    r.need(m['batch_id']==BATCH_ID and m['planned_calls']==CALLS and m['model_identity']==PIN and m['request_parameters']==r.PARAMS,'finite_frozen_contract')
    for n,h in m['metadata_hashes'].items():r.need(r.sha(batch/n)==h,'frozen_metadata_changed:'+n)
    for n,h in m['files'].items():r.need(r.sha(HERE/n)==h,'frozen_tool_changed:'+n)
    rows=r.read(batch/'rows.json');jobs=r.read(batch/'jobs.json');validate_blocks(rows,jobs,r.read(batch/'prefix100.json')['case_ids'])
    return m,rows,jobs


def command(batch,mode):
    m=r.read(batch/'execution_manifest.json')
    return ['ssh','-i',m['identity_file'],'-p','2222','-o','BatchMode=yes','-o','ConnectTimeout=10',
        '-o','ServerAliveInterval=15','-o','ServerAliveCountMax=4','vboxuser@127.0.0.1',
        'env PYTHONDONTWRITEBYTECODE=1 python3 '+REMOTE_TOOLS+'/'+Path(__file__).name+' '+mode+' --batch '+REMOTE]


def call(batch,mode,payload=None,label=None):
    folder=batch/'remote_receipts'/(label or mode+'_'+str(time.time_ns()));folder.mkdir(parents=True)
    with (folder/'stdout.json').open('xb') as out,(folder/'stderr.log').open('xb') as err:
        p=subprocess.Popen(command(batch,mode),stdin=subprocess.PIPE,stdout=out,stderr=err)
        if payload is not None:p.stdin.write(r.canonical(payload));p.stdin.flush()
        p.stdin.close();start=time.monotonic()
        while p.poll() is None:
            if time.monotonic()-start>(21600 if mode in ('remote-evaluate','remote-seal','remote-finish','remote-init') else 180):
                p.terminate();p.wait(timeout=10);raise ValueError('SSH_timeout_no_reexecution')
            time.sleep(.25)
    r.need(p.returncode==0,'SSH_operation_failed:'+mode);value=r.read(folder/'stdout.json');r.need(value.get('pass') is True,'remote_gate_failed');return value


def remote_check(batch):
    identity=r.read(batch/'identity.json')
    r.need(str(batch)==REMOTE and identity['batch_id']==BATCH_ID and identity['wrapper_sha256']==r.sha(Path(__file__)),'guest_wrapper_identity')
    r.need(identity['bridge_sha256']==r.sha(Path(bridge.__file__))==base.BRIDGE_SHA,'guest_bridge_identity')
    out=bridge.status(batch);out.update(batch_id=BATCH_ID,wrapper_sha256=r.sha(Path(__file__)));return out


def remote_init(batch,payload):
    r.need(str(batch)==REMOTE and not batch.exists(),'fresh_exact_guest_batch');r.remote_imports(batch)
    old=r.read(Path('/home/vboxuser/bp17_model_20261016_v1/plan.json'));wanted={v['anonymous_id']:v for v in old['rows']}
    rows=payload['rows'];jobs=payload['jobs'];validate_blocks(rows,jobs,payload['prefix_ids'])
    native={};private={}
    for i,row in enumerate(rows):
        case=row['anonymous_id'];r.need(row==wanted[case],'unchanged_original_row')
        frozen=r.read(r.REMOTE_ROOT/'all_target_v3'/case/'group_requests_NOT_SENT.json')
        r.need([metadata(j) for j in case_jobs(row,frozen)]==jobs[8*i:8*i+8],'two_endpoint_actual_requests')
        for n,h in old['private_hashes'][case].items():r.need(r.sha(r.REMOTE_ROOT/'all_target_v3'/case/n)==h,'private_frozen_record')
        d=r.NATIVE/'runs/cases'/row['private_case_id'];h=r.sha(d/'result.json');v=r.read(d/'result.json')
        r.need(h==old['native_result_hashes'][case]==r.read(d/'receipt.json')['result_sha256'] and v['status']=='pair_reproduced','native_receipt')
        native[case]=h;private[case]=old['private_hashes'][case]
    batch.mkdir();from check_fc_extension_baseline_preservation import check
    baseline=check(r.NATIVE,batch/'baseline_before.json');r.need(baseline['pass'] and baseline['resource_protection_pass'],'native_preservation')
    r.save(batch/'plan.json',dict(rows=rows,jobs=jobs,native_result_hashes=native,private_hashes=private,host_manifest_sha256=payload['manifest_sha256'],model_identity=PIN))
    r.save(batch/'identity.json',dict(batch_id=BATCH_ID,planned=CALLS,prepared_utc=r.now(),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        runner_sha256=r.sha(Path(r.__file__)),wrapper_sha256=r.sha(Path(__file__)),bridge_sha256=r.sha(Path(bridge.__file__)),model_identity=PIN))
    return remote_check(batch)


def readonly_receipt(batch,remote_path,label):
    target=batch/'readonly_receipts'/label;target.parent.mkdir(exist_ok=True);m=r.read(batch/'execution_manifest.json')
    result=subprocess.run(['scp','-i',m['identity_file'],'-P','2222','-o','BatchMode=yes','-o','ConnectTimeout=10',
        'vboxuser@127.0.0.1:'+REMOTE+'/'+remote_path,str(target)],capture_output=True,timeout=45)
    r.need(result.returncode==0 and target.is_file(),'no_committed_receipt_stop_no_rerun');return r.read(target)


def reserve(batch,jobs,reserved):
    r.need(len(reserved)+len(jobs)<=CALLS and len({j['job_id'] for j in jobs})==len(jobs) and not reserved & {j['job_id'] for j in jobs},'finite_unique_reservation')
    with (batch/'attempt_ledger.jsonl').open('a',encoding='utf-8',newline='\n') as f:
        for j in jobs:
            v={k:j[k] for k in ('job_id','case_id','group','task','request_sha256')};v.update(ordinal=len(reserved)+1,
                cumulative_ordinal=CUMULATIVE_BEFORE+len(reserved)+1,reserved_utc=r.now(),status='reserved_before_network')
            f.write(json.dumps(v)+'\n');f.flush();os.fsync(f.fileno());reserved.add(j['job_id'])


def remote_seal(batch,payload):
    remote_check(batch);plan=r.read(batch/'plan.json');index=payload['index'];start=(index-1)*100
    ids=[v['anonymous_id'] for v in plan['rows'][start:start+100]]
    r.need(1<=index<=32 and ids==payload['case_ids'] and ids,'exact_next_shard_scope')
    name='shard_'+str(index).zfill(4);directory=batch/'shards'/name
    archive=batch.parent/(batch.name+'_archives')/name
    r.need(not directory.exists() and not archive.exists(),'one_shot_shard_no_restart');directory.mkdir(parents=True);archive.mkdir(parents=True)
    r.save(directory/'intent.json',dict(case_ids=ids,index=index,model_calls=0,C_executions=0))
    from audit_bp17_remainder_saved_20261017_v1 import audit
    result=audit(batch,plan,ids);r.save(directory/'saved_byte_audit.json',result)
    chosen=set(ids);small=dict(rows=[v for v in plan['rows'] if v['anonymous_id'] in chosen],jobs=[v for v in plan['jobs'] if v['case_id'] in chosen],
        private_hashes={k:v for k,v in plan['private_hashes'].items() if k in chosen},native_result_hashes={k:v for k,v in plan['native_result_hashes'].items() if k in chosen},
        host_manifest_sha256=plan['host_manifest_sha256'],root_plan_sha256=r.sha(batch/'plan.json'))
    r.save(directory/'plan.json',small)
    paths=[p for row in small['rows'] for p in (batch/'cohorts'/row['cohort']/row['anonymous_id']).rglob('*') if p.is_file()]
    paths += [directory/'intent.json',directory/'plan.json',directory/'saved_byte_audit.json',batch/'identity.json']
    files={p.relative_to(batch).as_posix():r.sha(p) for p in paths};r.save(archive/'payload_manifest.json',files)
    stream_pack(archive/'records.tar.gz',batch,files,lambda:r.resource_guard(batch));n=check_archive(archive/'records.tar.gz',files,lambda:r.resource_guard(batch))
    identity=dict(payload_members=n,sha256=r.sha(archive/'records.tar.gz'),bytes=(archive/'records.tar.gz').stat().st_size,case_ids=ids,index=index,
        saved_byte_audit_sha256=r.sha(directory/'saved_byte_audit.json'),model_calls=0,candidate_C_reexecutions=0)
    r.save(archive/'archive_identity.json',identity)
    value=dict(**{'pass':True},index=index,case_ids=ids,complete_cases=len(ids),audited_jobs=8*len(ids),archive=identity,ended_utc=r.now())
    r.save(directory/'completion.json',value);return value


def remote_finish(batch):
    remote_check(batch);plan=r.read(batch/'plan.json');expected={v['anonymous_id'] for v in plan['rows']};seen=set();identities=[]
    for i in range(1,33):
        name='shard_'+str(i).zfill(4);v=r.read(batch/'shards'/name/'completion.json');ids=set(v['case_ids'])
        r.need(v['pass'] and not seen & ids,'all_shards_unique_pass');seen|=ids
        archive=batch.parent/(batch.name+'_archives')/name
        r.need(r.read(archive/'archive_identity.json')==v['archive'] and r.sha(archive/'records.tar.gz')==v['archive']['sha256'],'sealed_archive_unchanged')
        for j,(path,h) in enumerate(r.read(archive/'payload_manifest.json').items()):
            if j%500==0:r.resource_guard(batch)
            r.need(r.sha(batch/path)==h,'sealed_payload_unchanged')
        identities.append(v['archive'])
    r.need(seen==expected and len(seen)==PAIRS,'full_remainder_shard_range')
    from check_fc_extension_baseline_preservation import check
    baseline=check(r.NATIVE,batch/'baseline_after.json');r.need(baseline['pass'] and baseline['resource_protection_pass'],'native_baseline_after')
    value=dict(**{'pass':True},batch_id=BATCH_ID,complete_cases=PAIRS,audited_jobs=CALLS,archives=identities,model_calls=0,candidate_C_reexecutions=0,completed_utc=r.now())
    r.save(batch/'completion.json',value);return value


def run(batch):
    m,rows,jobs=verified(batch);rowmap={v['anonymous_id']:v for v in rows}
    r.need(not any((batch/n).exists() for n in ('one_shot.started.json','attempt_ledger.jsonl','stop.json','completion.json')),'one_shot_no_retry')
    units=[r.read(batch/n) for n in ('unit_local.json','unit_guest.json')]
    r.need(all(v['pass'] and v['tests']>=20 and v['failures']==v['errors']==v['skipped']==0 and v['controller_sha256']==r.sha(Path(__file__)) for v in units),'two_platform_controls')
    key=os.environ.get('DEEPSEEK_API_KEY');r.need(bool(key),'host_key_required')
    reserved=set();seen=set(r.read(batch/'prior_response_ids.json'));counts=Counter();active=None;unsafe=[];stop=threading.Event();phase='stopped';reason=None
    def watch():
        while not stop.wait(15):
            try:r.resource_guard(batch)
            except Exception:unsafe.append(True);return
    def snapshot(label):
        value=dict(batch_id=BATCH_ID,pid=os.getpid(),phase=label,updated_utc=r.now(),planned=CALLS,reserved=len(reserved),remaining=CALLS-len(reserved),
            counts=dict(counts),active=active,completed_prefix_cases=100,overall_target_pairs=3258,model_identity=PIN,automatic_retries=0,new_confirmation_cases=0,
            cumulative_reserved=CUMULATIVE_BEFORE+len(reserved),old_scores_not_merged=True)
        r.progress(batch/'progress.json',value);return value
    with base.global_lock(Path(m['source_batch']).parent/'bp17_live_transport.lock'):
        try:
            r.resource_guard(batch);base.preserve(r.read(batch/'before_old_files.json')['files'])
            initial=call(batch,'remote-status');r.need(initial['ready'] and initial['host_manifest_sha256']==r.sha(batch/'execution_manifest.json'),'guest_ready_binding')
            r.save(batch/'one_shot.started.json',dict(pid=os.getpid(),started_utc=r.now(),guest_boot=initial['boot_id'],manifest_sha256=r.sha(batch/'execution_manifest.json')))
            r.save(batch/'model_identity.json',PIN);threading.Thread(target=watch,daemon=True).start();wave_number=0;snapshot('identity_gate')
            with ThreadPoolExecutor(max_workers=4) as pool:
                for i,row in enumerate(rows):
                    path=Path(m['source_batch'])/'inputs'/row['anonymous_id']/'group_requests_NOT_SENT.json'
                    r.need(r.sha(path)==m['source_inputs'][str(path)],'frozen_actual_inputs')
                    full=case_jobs(row,r.read(path));block=jobs[8*i:8*i+8];r.need([metadata(j) for j in full]==block,'actual_request_binding');scored={}
                    for wave in base.waves(full,first=i==0):
                        r.need(not unsafe,'host_resource_protection');r.resource_guard(batch);health=call(batch,'remote-status')
                        r.need(health['ready'] and health['boot_id']==initial['boot_id'],'guest_boot_or_state_changed')
                        wave_number+=1;active=dict(case_ordinal=i+1,case_id=row['anonymous_id'],wave=wave_number,jobs=[v['job_id'] for v in wave])
                        reserve(batch,wave,reserved);snapshot('model_calls_inflight')
                        returned=list(pool.map(lambda j:r.send(j,key,r.result_folder(batch,row,j)),wave))
                        for value in returned:counts[value['status']]+=1
                        for value in returned:r.identity(value,PIN);r.need(value['response_id'] not in seen,'unique_new_response');seen.add(value['response_id'])
                        snapshot('isolated_evaluation')
                        try:receipt=call(batch,'remote-evaluate',dict(wave=wave_number,responses=returned,model_identity=PIN),'wave_'+str(wave_number).zfill(5))
                        except ValueError as error:
                            if str(error)!='SSH_operation_failed:remote-evaluate':raise
                            name='wave_'+str(wave_number).zfill(5)+'.json';receipt=readonly_receipt(batch,'wave_receipts/'+name,name)
                        base.gate_receipt(receipt,wave,rowmap);r.save(batch/'evaluation_receipts'/('wave_'+str(wave_number).zfill(5)+'.json'),receipt)
                        for value in receipt['rows']:scored[value['job_id']]=value;counts['scored_'+value['task']]+=1;counts['scored_'+value['cohort']]+=1
                        counts['evaluated']+=len(receipt['rows']);snapshot('wave_completed')
                    base.block_gate(block,scored);r.save(batch/'case_receipts'/(row['anonymous_id']+'.json'),dict(case_id=row['anonymous_id'],cohort=row['cohort'],evaluated=8,rows=list(scored.values()),**{'pass':True}))
                    counts['completed_cases']+=1;snapshot('case_completed');print(json.dumps(dict(time_utc=r.now(),completed_cases=i+1,remaining_cases=PAIRS-i-1,evaluated=counts['evaluated'])),flush=True)
                    if (i+1)%100==0 or i+1==PAIRS:
                        index=i//100+1;ids=[x['anonymous_id'] for x in rows[(index-1)*100:i+1]];snapshot('saved_byte_shard_audit_and_archive')
                        try:sealed=call(batch,'remote-seal',dict(index=index,case_ids=ids),'seal_'+str(index).zfill(4))
                        except ValueError as error:
                            if str(error)!='SSH_operation_failed:remote-seal':raise
                            name='shard_'+str(index).zfill(4);sealed=readonly_receipt(batch,'shards/'+name+'/completion.json',name+'.json')
                        r.need(sealed['pass'] and sealed['case_ids']==ids,'sealed_exact_cases');r.save(batch/'sealed_shards'/('shard_'+str(index).zfill(4)+'.json'),sealed);counts['sealed_shards']+=1
            r.need(counts['completed_cases']==PAIRS and counts['evaluated']==counts['completed']==len(reserved)==CALLS,'all_3158_cases_25264_scores')
            snapshot('final_preservation_and_archive_check');r.save(batch/'remote_completion.json',call(batch,'remote-finish'))
            base.preserve(r.read(batch/'before_old_files.json')['files']);phase='pipeline_completed_pending_independent_host_review'
        except Exception as error:reason=str(error) if type(error) is ValueError else type(error).__name__
        finally:
            stop.set();value=snapshot(phase);value.update(reason=reason,ended_utc=r.now(),all_results_jointly_verified=False)
            r.save(batch/('completion.json' if phase!='stopped' else 'stop.json'),value)
    return value


def controls(output):
    suite=unittest.defaultTestLoader.discover(str(HERE),pattern='test_bp17_caseblocked_remainder_20261017_v1.py')
    result=unittest.TextTestRunner(verbosity=2).run(suite);value=dict(**{'pass':result.wasSuccessful() and not result.skipped},tests=result.testsRun,
        failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),controller_sha256=r.sha(Path(__file__)),model_calls=0,candidate_executions=0)
    r.save(output,value);return value


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('prepare','units','run','remote-init','remote-status','remote-evaluate','remote-seal','remote-finish'))
    p.add_argument('--project',type=Path);p.add_argument('--batch',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
    try:
        if a.mode=='prepare':v=prepare(a.project,a.batch)
        elif a.mode=='units':v=controls(a.output)
        elif a.mode=='run':v=run(a.batch)
        elif a.mode=='remote-init':v=remote_init(a.batch,json.load(sys.stdin))
        elif a.mode=='remote-status':v=remote_check(a.batch)
        elif a.mode=='remote-seal':v=remote_seal(a.batch,json.load(sys.stdin))
        elif a.mode=='remote-finish':v=remote_finish(a.batch)
        else:remote_check(a.batch);v=bridge.evaluate(a.batch,json.load(sys.stdin))
        print(json.dumps(v,ensure_ascii=False),flush=True);raise SystemExit(v.get('pass') is False or v.get('phase')=='stopped')
    except Exception as e:
        print(json.dumps({'pass':False,'error':str(e) if type(e) is ValueError else type(e).__name__}),flush=True);raise SystemExit(1)
