"""One finite BP17 v3 run. Host owns API key; Linux scores isolated candidates.

New orchestration only: frozen requests, scorers, evaluator and native tests are
not changed. Reservations are durable before POST, never retried on interruption.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import threading
import time
import urllib.error
import urllib.request

ID = 'BP17-behavior-plus-uninitialized-classification-20261016-v3'
BATCH_ID = 'BP17-model-20261016-v1'
ENDPOINT = 'https://api.deepseek.com/chat/completions'
PARAMS = dict(model='deepseek-flash', temperature=0.0,
              thinking={'type':'disabled'}, max_tokens=4096,
              response_format={'type':'json_object'}, stream=False)
JOINT_SHA = '22cf2af95d1b2af0a05119fcde171c58ce1ff0b2194b007061a81e3ef0ceb9c2'
PREP_SHA = '7385814793821aa1d3e777aefd7c83430099cb5ee701d80d90bfb3c121bf10ca'
INDEX_SHA = '1fdf4db7f2c15b848492be51e96d0cbf14325d178d44eea01b5ea579c4d34ee0'
ARCHIVE_SHA = 'e8e08b517c657ccade340a8dc985bbae828b3bd13ff58673635ffef95b17117a'
FREEZE_SHA = '6d79f4cce5717462f07a2060463bef8c12c00da06400012ee79c347503414c1f'
SUMMARY_SHA = 'f1cb91cb03a3dcd139f8a8e96e5b0e95d50a6fadeb421fecd3a2c03f34822e22'
HISTORY_SHA = '9508562f0eb4bdad2a1e3a8f659ffc1435f12aadfee556ca1475d86d930ad132'
CANDIDATE_SHA = 'e2d08ebb11e7f6b03edf7950db7f72c539101656ae19da8a349010d0748769f9'
REMOTE_ROOT = Path('/home/vboxuser/bp17_full_target_20261016_v1')
REMOTE_OUT = '/home/vboxuser/bp17_model_20261016_v1'
NATIVE = Path('/home/vboxuser/cfb2')
HERE = Path(__file__).resolve().parent
COHORTS = ('exposed_exploratory', 'previously_unexposed')
GROUPS = ('BP0', 'BP1', 'BP2', 'BP3')
TASKS = ('understanding', 'repair')


def need(ok, why):
    if not ok:
        raise ValueError(why)


def now():
    return datetime.now(timezone.utc).isoformat()


def canonical(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(1024**2), b''):
            h.update(part)
    return h.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())


def progress(path, value):
    """Only this new run's live progress is replaceable; journals are append-only."""
    path = Path(path)
    temp = path.with_suffix('.tmp.' + str(os.getpid()))
    save(temp, value)
    os.replace(temp, path)


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


def validate_jobs(jobs, rows):
    need(len(rows) == 3258 and len({r['anonymous_id'] for r in rows}) == 3258, 'exact_case_scope')
    need(Counter(r['cohort'] for r in rows) == Counter(dict(zip(COHORTS, (1858,1400)))), 'cohort_counts')
    clusters = [{r['cluster_root'] for r in rows if r['cohort'] == c} for c in COHORTS]
    need(not clusters[0] & clusters[1] and list(map(len,clusters)) == [569,561], 'cluster_separation')
    cases = {r['anonymous_id'] for r in rows}
    wanted = {(c,g,t) for c in cases for g in GROUPS for t in TASKS}
    need(len(jobs) == 26064 and len({j['job_id'] for j in jobs}) == 26064, 'exact_unique_slots')
    need({(j['case_id'],j['group'],j['task']) for j in jobs} == wanted, 'complete_four_group_blocks')
    for j in jobs:
        need(j['protocol_id'] == ID and j['repetition'] == 1 and j['status'] == 'NOT_SENT', 'frozen_job_contract')
        need(j['job_id'] == '/'.join((ID,j['case_id'],j['group'],j['task'],'1')), 'job_key')
    return sorted(jobs, key=lambda j:hashlib.sha256((BATCH_ID+'/pre-response-order/'+j['job_id']).encode()).hexdigest())


def validate_request(j):
    r = j['request']
    need(digest(r) == j['request_sha256'], 'serialized_request_changed')
    need({k:v for k,v in r.items() if k != 'messages'} == PARAMS, 'parameters_changed')
    need(len(r['messages']) == 2 and [x['role'] for x in r['messages']] == ['system','user'], 'messages_changed')
    need(len(canonical(r)) <= 240000, 'request_size')


def history_check(history):
    need(history['pass'] and history['historical_calls'] == 464 and history['cap'] is None, 'history_contract')
    ids = set()
    for e in history['evidence']:
        p = Path(e['path'])
        need(sha(p) == e['sha256'], 'historical_ledger_changed')
        lines = [json.loads(s) for s in p.read_text(encoding='utf-8').splitlines() if s.strip()]
        need(len(lines) == len({r['job_id'] for r in lines}) == e['calls'], 'historical_count')
        responses = list((p.parent/'responses').rglob('raw_response.json'))
        need(len(responses) == e['calls'], 'historical_response_count')
        for r in responses:
            response_id = read(r)['id']
            need(isinstance(response_id,str) and response_id and response_id not in ids, 'historical_response_collision')
            ids.add(response_id)
    need(len(ids) == 464, 'historical_464_unique_responses')
    return ids


def resource_guard(path):
    free = shutil.disk_usage(path).free
    if os.name == 'posix':
        mem = next(int(s.split()[1])*1024 for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:'))
    else:
        class Memory(ctypes.Structure):
            _fields_ = [('length',ctypes.c_ulong),('load',ctypes.c_ulong), *[(n,ctypes.c_ulonglong) for n in ('total','available','page_total','page_available','virtual_total','virtual_available','extended')]]
        m = Memory(); m.length = ctypes.sizeof(m)
        need(bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))), 'host_memory_query')
        mem = m.available
    need(free >= 15*1024**3 and mem >= 2*1024**3, 'resource_protection')
    return {'disk_free_bytes':free,'MemAvailable_bytes':mem,'checked_utc':now()}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise urllib.error.URLError('redirect_refused')


def listing(key):
    req = urllib.request.Request('https://api.deepseek.com/models', headers={'Authorization':'Bearer '+key})
    with urllib.request.build_opener(NoRedirect()).open(req,timeout=30) as f:
        raw = f.read(1024**2+1)
    need(len(raw) <= 1024**2, 'listing_size')
    models = [x['id'] for x in json.loads(raw)['data']]
    need(PARAMS['model'] in models, 'configured_model_not_listed')
    return {'checked_utc':now(),'model_ids':models,'endpoint':'https://api.deepseek.com/models','chat_calls':0}


def identity(r, pinned=None):
    need(r.get('status') == 'completed' and isinstance(r.get('response_id'),str) and r['response_id'], 'API_failure_stop_no_retry')
    need(r.get('model_returned') == PARAMS['model'], 'returned_model_changed')
    need(isinstance(r.get('system_fingerprint'),str) and r['system_fingerprint'].strip(), 'missing_model_fingerprint')
    value = {k:r[k] for k in ('model_returned','system_fingerprint')}
    need(pinned is None or value == pinned, 'model_identity_changed')
    return value


def send(job, key, folder):
    folder.mkdir(parents=True, exist_ok=False)
    validate_request(job)
    with (folder/'request.json').open('xb') as f:
        f.write(canonical(job['request'])); f.flush(); os.fsync(f.fileno())
    r = {k:job[k] for k in ('job_id','case_id','group','task','request_sha256')}
    r.update(started_utc=now(),request_model=PARAMS['model'])
    save(folder/'network_attempt.json',r)
    started = time.monotonic()
    try:
        req = urllib.request.Request(ENDPOINT,data=canonical(job['request']),method='POST',
               headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=120) as f:
            raw = f.read(8*1024**2+1)
        with (folder/'raw_response.json').open('xb') as f:
            f.write(raw); f.flush(); os.fsync(f.fileno())
        need(len(raw) <= 8*1024**2, 'response_size')
        obj = json.loads(raw); choices = obj['choices']
        need(len(choices) == 1 and choices[0].get('index') == 0, 'response_choice_count')
        choice = choices[0]
        need(isinstance(choice['message'].get('content'),str), 'response_content_not_string')
        r.update(status='completed',response_id=obj['id'],model_returned=obj['model'],
                 system_fingerprint=obj.get('system_fingerprint'),content=choice['message']['content'],
                 finish_reason=choice.get('finish_reason'),usage=obj.get('usage'),raw_sha256=sha(folder/'raw_response.json'))
    except urllib.error.HTTPError as e:
        (folder/'http_error.bin').write_bytes(e.read(1024**2))
        r.update(status='api_error',http_status=e.code)
    except (urllib.error.URLError,TimeoutError,OSError,KeyError,IndexError,ValueError,TypeError) as e:
        # Never persist exception text: a proxy might echo authentication data.
        r.update(status='transport_or_response_error',error_type=type(e).__name__)
    r.update(ended_utc=now(),elapsed_seconds=round(time.monotonic()-started,4))
    save(folder/'result.json',r)
    return r


def reserve(path, jobs, reserved, planned=26064):
    need(len(reserved)+len(jobs) <= planned, 'finite_budget_exhausted')
    need(len({j['job_id'] for j in jobs}) == len(jobs) and not reserved & {j['job_id'] for j in jobs}, 'duplicate_reservation')
    with Path(path).open('a',encoding='utf-8',newline='\n') as f:
        for j in jobs:
            row = {k:j[k] for k in ('job_id','case_id','group','task','request_sha256')}
            row.update(ordinal=len(reserved)+1,cumulative_ordinal=465+len(reserved),
                       status='reserved_before_network',reserved_utc=now())
            f.write(json.dumps(row)+'\n'); f.flush(); os.fsync(f.fileno())
            reserved.add(j['job_id'])


def prepare(project, output):
    base = project/'03_experiments/results/bp17_behavior_primary_2026-10-16'
    joint = base/'joint_v3'; archive = project/'90_local_only/bp17_transfer_20261016_v3/records.tar.gz'
    for path,h in [(joint/'joint_acceptance.json',JOINT_SHA),(joint/'prepared_execution_manifest.json',PREP_SHA),
                   (joint/'request_index_NOT_SENT.json',INDEX_SHA),(base/'history_reconciled_v3.json',HISTORY_SHA),
                   (archive,ARCHIVE_SHA),(HERE/'cgo16_candidate_isolated_v2.py',CANDIDATE_SHA)]:
        need(sha(path) == h, 'accepted_preparation_identity:'+path.name)
    j = read(joint/'joint_acceptance.json')
    need(j['pass'] and j['all_primary_preparation_checks_passed'] and len(j['gate_checks']) == 17 and all(j['gate_checks'].values()), 'all_preparation_gates')
    hist = read(base/'history_reconciled_v3.json'); history_check(hist)
    resource_guard(output.parent)
    output.mkdir(parents=True,exist_ok=False)
    for name,src in [('joint_acceptance.json',joint/'joint_acceptance.json'),('prepared_execution_manifest.json',joint/'prepared_execution_manifest.json'),
                     ('request_index_NOT_SENT.json',joint/'request_index_NOT_SENT.json'),('history.json',base/'history_reconciled_v3.json'),
                     ('protocol.md',project/'01_research/workflow/bp17_behavior_classification_protocol_2026-10-16_v3.md'),
                     ('analysis_plan.md',project/'01_research/workflow/bp17_analysis_plan_2026-10-16.md')]:
        shutil.copy2(src,output/name)
    index = read(output/'request_index_NOT_SENT.json'); expected = {j['job_id']:j for j in index}
    jobs = []; rows = []; input_hashes = {}
    # Select regular public request and row files only; never extract tar paths.
    with tarfile.open(archive,'r|gz') as t:
        for member in t:
            parts = member.name.split('/')
            if len(parts) != 3 or parts[0] != 'all_target_v3' or parts[2] not in ('group_requests_NOT_SENT.json','row.json'):
                continue
            need(member.isfile() and len(parts[1]) == 9 and parts[1].startswith('BP17-') and parts[1][5:].isdigit(), 'safe_case_member')
            need(member.size <= 2*1024**2, 'bounded_public_case')
            raw = t.extractfile(member).read(); value = json.loads(raw)
            path = output/'inputs'/parts[1]/parts[2]; path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as f:f.write(raw)
            input_hashes[path.relative_to(output).as_posix()] = sha(path)
            if parts[2] == 'row.json':
                rows.append(value)
            else:
                need(len(value) == 8, 'eight_requests_per_case')
                for item in value:
                    validate_request(item)
                    entry = {k:item[k] for k in expected[item['job_id']]}
                    need(entry == expected[item['job_id']], 'accepted_index_mismatch')
                    jobs.append(entry)
    jobs = validate_jobs(jobs,rows)
    save(output/'jobs.json',jobs); save(output/'rows.json',rows)
    for name in ('run_bp17_v3_experiment.py','test_run_bp17_v3_experiment.py','cgo16_candidate_isolated_v2.py','check_fc_extension_baseline_preservation.py'):
        dest = output/'tools'/name; dest.parent.mkdir(exist_ok=True); shutil.copy2(HERE/name,dest)
    # All imported scoring/evaluation dependencies are frozen, not working-tree modules.
    freeze = project/'90_local_only/bp17_transfer_20261016_v3/frozen_v3'
    need(sha(freeze/'manifest.json') == FREEZE_SHA, 'local_frozen_v3_identity')
    shutil.copytree(freeze/'tools',output/'frozen_dependencies/tools')
    shutil.copytree(freeze/'deps',output/'frozen_dependencies/deps',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    manifest = dict(schema='BP17-v3-live-execution-v1',batch_id=BATCH_ID,frozen_utc=now(),
        planned_pairs=3258,planned_calls=26064,historical_calls=464,cumulative_max_slots=26528,
        cumulative_cap=None,repetitions=1,automatic_retry=0,feedback_rounds=0,max_parallel=4,
        order='SHA256(batch_id/pre-response-order/frozen_job_id)',request_parameters=PARAMS,
        endpoint=ENDPOINT,remote_output=REMOTE_OUT,first_planned_call_is_identity_gate=True,
        cohorts=dict(zip(COHORTS,(1858,1400))),candidate_executor_sha256=CANDIDATE_SHA,
        preparation_sha256=JOINT_SHA,original_tests_and_judge_changed=False,
        request_socket_timeout_seconds=120,local_and_guest_resource_guards=dict(disk_GiB=15,memory_GiB=2),
        inputs=input_hashes,jobs_sha256=sha(output/'jobs.json'),rows_sha256=sha(output/'rows.json'),
        frozen_files={p.relative_to(output).as_posix():sha(p) for d in (output/'tools',output/'frozen_dependencies') for p in d.rglob('*') if p.is_file()})
    save(output/'execution_manifest.json',manifest)
    return {k:v for k,v in manifest.items() if k not in ('inputs','frozen_files')}


def verify_local(batch):
    m = read(batch/'execution_manifest.json')
    need(m['batch_id'] == BATCH_ID and m['planned_calls'] == 26064 and m['automatic_retry'] == m['feedback_rounds'] == 0, 'execution_contract')
    need(sha(batch/'jobs.json') == m['jobs_sha256'] and sha(batch/'rows.json') == m['rows_sha256'], 'job_rows_changed')
    need(sha(batch/'joint_acceptance.json') == JOINT_SHA and sha(batch/'history.json') == HISTORY_SHA, 'acceptance_or_history_changed')
    for name,h in {**m['inputs'],**m['frozen_files']}.items():
        need(sha(batch/name) == h, 'frozen_execution_file_changed:'+name)
    need(sha(Path(__file__)) == m['frozen_files']['tools/run_bp17_v3_experiment.py'], 'executing_wrong_runner')
    jobs = validate_jobs(read(batch/'jobs.json'),read(batch/'rows.json'))
    need(jobs == read(batch/'jobs.json'), 'queue_order_changed')
    history_check(read(batch/'history.json'))
    need(m['request_parameters'] == PARAMS and m['endpoint'] == ENDPOINT and m['cumulative_cap'] is None, 'frozen_transport_policy')
    return m,jobs


def ssh_command(batch, mode):
    cfg = read(batch/'ssh_config.json')
    return ['ssh','-i',cfg['identity_file'],'-p','2222','-o','BatchMode=yes','-o','ConnectTimeout=10',
            '-o','ServerAliveInterval=15','-o','ServerAliveCountMax=4','vboxuser@127.0.0.1',
            'env PYTHONDONTWRITEBYTECODE=1 python3 '+cfg['remote_script']+' '+mode+' --batch '+REMOTE_OUT]


def remote_call(batch, mode, payload=None, label=None):
    target = batch/'remote_receipts'/(label or (mode+'_'+str(time.time_ns())))
    target.mkdir(parents=True,exist_ok=False)
    with (target/'stdout.json').open('xb') as out,(target/'stderr.log').open('xb') as err:
        p = subprocess.Popen(ssh_command(batch,mode),stdin=subprocess.PIPE,stdout=out,stderr=err)
        if payload is not None:
            p.stdin.write(canonical(payload));p.stdin.flush()
        p.stdin.close()
        started = time.monotonic()
        while p.poll() is None:
            # Never terminate an evaluating candidate on a host resource event;
            # guest owns candidate kill/records. Stop future API waves instead.
            if time.monotonic()-started > (21600 if mode == 'remote-evaluate' else 180):
                p.terminate();p.wait(timeout=10);raise ValueError('remote_command_timeout_records_preserved')
            time.sleep(.25)
    need(p.returncode == 0, 'remote_operation_failed:'+mode)
    result = read(target/'stdout.json')
    need(result.get('pass') is True, 'remote_gate_or_evaluation_failed')
    return result


def result_folder(batch, row, job):
    return batch/'cohorts'/row['cohort']/'responses'/job['case_id']/job['group']/job['task']


def run(batch):
    m,jobs = verify_local(batch)
    need(not (batch/'one_shot.started.json').exists() and not (batch/'attempt_ledger.jsonl').exists(), 'already_started_never_retry')
    key = os.environ.get('DEEPSEEK_API_KEY'); need(bool(key),'missing_API_key')
    for name in ('unit_local.json','unit_guest.json'):
        unit = read(batch/name)
        need(unit['pass'] and unit['failures'] == unit['errors'] == unit['skipped'] == 0 and unit['tests'] >= 18,
             'two_platform_runner_tests_required')
        need(unit['runner_sha256'] == sha(Path(__file__)), 'tested_runner_identity')
    # A process-held global lock, plus a durable one-shot marker for this batch.
    lock = (batch.parent/'bp17_live_transport.lock').open('a+b')
    if os.name == 'nt':
        import msvcrt
        if lock.tell() == 0:lock.write(b'0');lock.flush()
        lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    else:
        import fcntl
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    reserved = set(); seen = history_check(read(batch/'history.json')); pin = None
    counters = Counter(); status = 'stopped'; reason = None; active = None
    rowmap = {r['anonymous_id']:r for r in read(batch/'rows.json')}
    stop = threading.Event(); watchdog_errors = []
    def watch():
        while not stop.wait(15):
            try:resource_guard(batch)
            except Exception as e:watchdog_errors.append(type(e).__name__);return
    monitor = threading.Thread(target=watch,daemon=True)
    def snapshot(phase):
        value = dict(batch_id=BATCH_ID,phase=phase,updated_utc=now(),pid=os.getpid(),
            planned=26064,reserved=len(reserved),not_reserved=26064-len(reserved),historical=464,
            cumulative_reserved=464+len(reserved),counts=dict(counters),model_identity=pin,
            active_wave=active,automatic_retry=0,feedback_rounds=0)
        progress(batch/'progress.json',value);return value
    try:
        resource_guard(batch)
        remote = remote_call(batch,'remote-status')
        need(remote['ready'] and remote['runner_sha256'] == sha(Path(__file__)) and remote['host_manifest_sha256'] == sha(batch/'execution_manifest.json'), 'remote_not_ready')
        save(batch/'provider_listing.json',listing(key))
        save(batch/'one_shot.started.json',dict(pid=os.getpid(),started_utc=now(),manifest_sha256=sha(batch/'execution_manifest.json'),remote_boot=remote['boot_id']))
        monitor.start();snapshot('identity_gate')
        offsets = [jobs[:1]] + [jobs[i:i+4] for i in range(1,len(jobs),4)]
        with ThreadPoolExecutor(max_workers=4) as pool:
            for wave_index,wave_meta in enumerate(offsets,1):
                need(not watchdog_errors, 'host_resource_protection')
                resource_guard(batch)
                resource = remote_call(batch,'remote-status')
                need(resource['boot_id'] == remote['boot_id'] and resource['ready'], 'guest_identity_or_state_changed')
                wave = []
                for entry in wave_meta:
                    items = read(batch/'inputs'/entry['case_id']/'group_requests_NOT_SENT.json')
                    job = next(x for x in items if x['job_id'] == entry['job_id'])
                    validate_request(job); wave.append(job)
                active = dict(wave=wave_index,jobs=[j['job_id'] for j in wave],started_utc=now())
                reserve(batch/'attempt_ledger.jsonl',wave,reserved)
                snapshot('model_calls_inflight')
                received = list(pool.map(lambda j:send(j,key,result_folder(batch,rowmap[j['case_id']],j)),wave))
                for r in received:
                    counters[r['status']] += 1
                # Persist every result before enforcing a changed-backend/failure stop.
                for r in received:
                    current = identity(r,pin)
                    if pin is None:
                        pin = current;save(batch/'model_identity.json',pin)
                    need(r['response_id'] not in seen, 'duplicate_response_identity')
                    seen.add(r['response_id'])
                snapshot('isolated_evaluation')
                evaluated = remote_call(batch,'remote-evaluate',{'wave':wave_index,'responses':received,'model_identity':pin},'wave_'+str(wave_index).zfill(5))
                save(batch/'evaluation_receipts'/('wave_'+str(wave_index).zfill(5)+'.json'),evaluated)
                counters['evaluated'] += len(evaluated['rows'])
                for r in evaluated['rows']:
                    counters['evaluated_'+r['cohort']] += 1
                    counters['scored_'+r['task']] += 1
                snapshot('wave_completed')
                print(json.dumps(dict(time_utc=now(),reserved=len(reserved),evaluated=counters['evaluated'],planned=26064)),flush=True)
        need(counters['completed'] == counters['evaluated'] == len(reserved) == 26064,'complete_exact_slots')
        final = remote_call(batch,'remote-finish')
        save(batch/'remote_completion.json',final);status='completed'
    except Exception as e:
        # Error descriptions from our own gates only; external exceptions reduced to type.
        reason = str(e) if type(e) is ValueError else type(e).__name__
    finally:
        stop.set()
        out = snapshot(status)
        out.update(status=status,reason=reason,ended_utc=now(),all_results_jointly_verified=False)
        save(batch/('completion.json' if status == 'completed' else 'stop.json'),out)
        lock.close()
    return out


def remote_imports(batch):
    need(os.name == 'posix' and not any('API_KEY' in n for n in os.environ), 'guest_without_API_keys')
    sys.path.insert(0,str(REMOTE_ROOT/'frozen_v3/tools'))
    sys.path.insert(0,str(REMOTE_ROOT/'frozen_v3/deps'))
    need(sha(REMOTE_ROOT/'frozen_v3/manifest.json') == FREEZE_SHA,'remote_freeze_identity')
    for name,h in read(REMOTE_ROOT/'frozen_v3/manifest.json')['files'].items():
        need(sha(REMOTE_ROOT/'frozen_v3'/name) == h,'remote_frozen_member_changed')
    need(sha(HERE/'cgo16_candidate_isolated_v2.py') == CANDIDATE_SHA, 'candidate_identity')
    import bp17_v2
    import bp17_classification_v3
    import cgo16_candidate_isolated_v2
    return bp17_v2,bp17_classification_v3,cgo16_candidate_isolated_v2


def remote_init(batch, payload):
    need(str(batch) == REMOTE_OUT and not batch.exists(), 'fresh_exact_guest_batch')
    numeric,classification,candidate = remote_imports(batch)
    need(sha(REMOTE_ROOT/'all_target_v3/summary.json') == SUMMARY_SHA,'remote_summary_identity')
    summary = read(REMOTE_ROOT/'all_target_v3/summary.json');rows = summary['rows']
    jobs = []
    for r in rows:
        values = read(REMOTE_ROOT/'all_target_v3'/r['anonymous_id']/'group_requests_NOT_SENT.json')
        for j in values:
            validate_request(j)
            jobs.append({k:j[k] for k in ('job_id','protocol_id','case_id','group','task','repetition','status','request_sha256')})
    ordered = validate_jobs(jobs,rows)
    need(ordered == payload['jobs'] and rows == payload['rows'], 'two_platform_execution_queue')
    batch.mkdir()
    from check_fc_extension_baseline_preservation import check
    preserved = check(NATIVE,batch/'baseline_before.json')
    need(preserved['pass'] and preserved['resource_protection_pass'],'baseline_preservation')
    # Receipts bind the complete current native records reused by evaluation.
    native_hashes = {}; private_hashes = {}
    for row in rows:
        d = NATIVE/'runs/cases'/row['private_case_id']; result = read(d/'result.json')
        h = sha(d/'result.json')
        need(read(d/'receipt.json')['result_sha256'] == h and result['status'] == 'pair_reproduced' and result['case_id'] == row['private_case_id'],'native_receipt_identity')
        native_hashes[row['anonymous_id']] = h
        d = REMOTE_ROOT/'all_target_v3'/row['anonymous_id']
        private_hashes[row['anonymous_id']] = {n:sha(d/n) for n in ('row.json','answers_private.json','questions_public.json','proof_private.json')}
    save(batch/'plan.json',dict(jobs=ordered,rows=rows,native_result_hashes=native_hashes,
        private_hashes=private_hashes,
        host_manifest_sha256=payload['manifest_sha256'],runner_sha256=sha(Path(__file__)),
        frozen_tool_identity=read(REMOTE_ROOT/'frozen_v3/manifest.json'),candidate_sha256=CANDIDATE_SHA))
    save(batch/'identity.json',dict(batch_id=BATCH_ID,prepared_utc=now(),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        runner_sha256=sha(Path(__file__)),candidate_sha256=CANDIDATE_SHA,planned=26064,model_calls=0,baseline_C_reexecutions=0,
        historical_calls=464,automatic_retry=0,feedback_rounds=0,baseline_writes=0,resource=resource_guard(batch)))
    return {'pass':True,'ready':True,'planned':26064,'candidate_evaluation':'not_started','model_calls':0,'baseline_preserved':True}


def remote_status(batch):
    identity = read(batch/'identity.json');resource = resource_guard(batch)
    boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    need(boot == identity['boot_id'] and identity['runner_sha256'] == sha(Path(__file__)), 'remote_boot_or_runner_changed')
    return dict(ready=not (batch/'completion.json').exists() and not (batch/'stop.json').exists(),
                boot_id=boot,runner_sha256=sha(Path(__file__)),resource=resource,
                host_manifest_sha256=read(batch/'plan.json')['host_manifest_sha256'],**{'pass':True})


def summarize_candidate(value, output, record):
    reason = value.get('reason',''); tests = value['candidate_tests']
    infrastructure = any(x in reason for x in ('infrastructure','resource_protection','original_','changed','exact_original','both_nonempty'))
    if (output/'compilation.json').exists():
        compilation = read(output/'compilation.json')
        infrastructure |= any(x and x.get('resource_stop') for x in (compilation['compile'],compilation['link']))
        for phase in ('compile','link'):
            log = output/phase/'stderr.bin'
            if log.exists() and b'bwrap:' in log.read_bytes():infrastructure=True
    for t in tests:
        p = output/('test_'+t['suite']+'_'+t['id'])/'stderr.bin'
        if p.exists() and b'bwrap:' in p.read_bytes():infrastructure=True
    counts = {s:dict(planned=len(record['metadata']['suites'][s]),executed=sum(t['suite']==s for t in tests),
                    passed=sum(t['suite']==s and t['pass'] for t in tests)) for s in ('repair','heldout')}
    trigger = sorted(t['id'] for t in record['tests'] if t['suite']=='repair' and t['sides']['buggy']['status'] in ('runtime_error','output_mismatch'))[0]
    found = next((t for t in tests if t['suite']=='repair' and t['id']==trigger),None)
    return dict(status='infrastructure_failure' if infrastructure else value['status'],reason=reason or None,
                repair_pass=counts['repair']['executed']==counts['repair']['planned'] and counts['repair']['passed']==counts['repair']['planned'],
                heldout_pass=counts['heldout']['executed']==counts['heldout']['planned'] and counts['heldout']['passed']==counts['heldout']['planned'],
                trigger_pass=None if found is None else found['pass'],suites=counts,
                candidate_failure_statuses=dict(Counter(t['status'] for t in tests)),evaluation_sha256=sha(output/'evaluation.json'))


def remote_evaluate(batch, payload):
    import fcntl
    remote_status(batch)
    lock = (batch.parent/'bp17_candidate_evaluation.lock').open('a+b')
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    numeric,classification,candidate = remote_imports(batch)
    plan = read(batch/'plan.json');rows = {r['anonymous_id']:r for r in plan['rows']}
    wanted = {j['job_id']:j for j in plan['jobs']};responses = payload['responses']
    need(0 < len(responses) <= 4 and len({r['job_id'] for r in responses}) == len(responses), 'wave_scope')
    result_rows = []
    for response in responses:
        resource_guard(batch)
        identity(response,payload['model_identity'])
        j = wanted[response['job_id']];r = rows[j['case_id']]
        need(all(response[k] == j[k] for k in ('case_id','group','task','request_sha256')), 'evaluation_input_identity')
        directory = batch/'cohorts'/r['cohort']/j['case_id']/j['group']/j['task']
        need(not directory.exists(), 'duplicate_evaluation_refused')
        directory.mkdir(parents=True)
        save(directory/'response.json',response)
        row = {k:j[k] for k in ('job_id','case_id','group','task','request_sha256')}
        row.update(cohort=r['cohort'],cluster_root=r['cluster_root'],understanding_kind=r['understanding_kind'],scored_utc=now())
        private = REMOTE_ROOT/'all_target_v3'/j['case_id']
        for name,h in plan['private_hashes'][j['case_id']].items():
            need(sha(private/name) == h, 'private_frozen_scoring_record_changed')
        if j['task'] == 'understanding':
            answer = read(private/'answers_private.json')
            scorer = numeric.score if r['understanding_kind'] == 'native_behavior_projection' else classification.score
            value = scorer(response['content'],answer)
            row.update(status='scored' if value['valid'] else 'invalid_answer',score=value)
        else:
            native_path = NATIVE/'runs/cases'/r['private_case_id']/'result.json'
            need(sha(native_path) == plan['native_result_hashes'][j['case_id']], 'native_record_changed')
            record = read(native_path)
            evaluated = candidate.evaluate(response['content'],record,directory/'candidate')
            row.update(summarize_candidate(evaluated,directory/'candidate',record))
        save(directory/'scored.json',row);result_rows.append(row)
        need(row['status'] != 'infrastructure_failure','candidate_evaluation_infrastructure_failure')
    output = {'pass':True,'wave':payload['wave'],'rows':result_rows,'scored_count':len(result_rows),
              'model_calls':0,'baseline_C_reexecutions':0,'original_tests_judge_changed':False,'ended_utc':now()}
    save(batch/'wave_receipts'/('wave_'+str(payload['wave']).zfill(5)+'.json'),output)
    lock.close()
    return output


def remote_finish(batch):
    remote_status(batch)
    plan = read(batch/'plan.json');seen = set();cohorts = Counter();tasks = Counter();groups = Counter()
    for path in (batch/'cohorts').glob('*/*/*/*/scored.json'):
        row = read(path);need(row['job_id'] not in seen,'duplicate_final_evaluation');seen.add(row['job_id'])
        cohorts[row['cohort']]+=1;tasks[row['task']]+=1;groups[row['group']]+=1
    need(seen == {j['job_id'] for j in plan['jobs']},'final_exact_evaluated_slots')
    from check_fc_extension_baseline_preservation import check
    preserved = check(NATIVE,batch/'baseline_after.json')
    need(preserved['pass'] and preserved['resource_protection_pass'],'final_baseline_preservation')
    out = dict(schema='BP17-v3-execution-completion',batch_id=BATCH_ID,completed_utc=now(),
               evaluated=len(seen),cohorts=dict(cohorts),tasks=dict(tasks),groups=dict(groups),
               all_results_jointly_verified=False,**{'pass':True})
    save(batch/'completion.json',out)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('prepare','run','remote-init','remote-status','remote-evaluate','remote-finish'))
    parser.add_argument('--batch',type=Path);parser.add_argument('--project',type=Path)
    a = parser.parse_args()
    try:
        if a.mode == 'prepare':v = prepare(a.project,a.batch)
        elif a.mode == 'run':v = run(a.batch)
        elif a.mode == 'remote-init':v = remote_init(a.batch,json.load(sys.stdin))
        elif a.mode == 'remote-status':v = remote_status(a.batch)
        elif a.mode == 'remote-evaluate':v = remote_evaluate(a.batch,json.load(sys.stdin))
        else:v = remote_finish(a.batch)
        print(json.dumps(v,ensure_ascii=False),flush=True)
        return int(v.get('pass') is False or v.get('status') == 'stopped')
    except Exception as e:
        print(json.dumps({'pass':False,'error':str(e) if type(e) is ValueError else type(e).__name__}),flush=True)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
