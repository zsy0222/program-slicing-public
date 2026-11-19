"""New finite case-block experiment; delegates unchanged transport and scorers.

Old batches are read-only. Credentials stay on host. One case has all eight
scores before a later case is issued. No model/candidate execution retries.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tarfile
import threading
import time
import unittest
import run_bp17_v3_experiment as r
import bp17_operational_bridge_v2 as bridge

EXEC_ID = 'BP17-caseblocked-100-newfingerprint-20261017-v1'
BATCH_ID = 'BP17-caseblock100-model-20261017-v1'
SEED = 'BP17-block100-20261017-v1'
REMOTE = '/home/vboxuser/bp17_caseblock100_20261017_v1'
REMOTE_TOOLS = '/home/vboxuser/bp17_caseblock100_tools_20261017_v1'
PIN = dict(model_returned='deepseek-flash', system_fingerprint='e72d3c7f663d3e1383b00b3884cb4501')
SOURCE_MANIFEST_SHA = 'b16c3c19c3cdbacc81d4fccde2bab97ce78368f77724eed810a9cbe2616fffad'
SOURCE_RUNNER_SHA = 'b8a94646b3ef567d2820fce8bdb008b1c10d0357ccbdb5d8f8df9dfe7930fc13'
BRIDGE_SHA = '1f51d55be86c5b3c1bbb70160ea0982ec1857547cecf1cb797b7be173caf1033'
CHECKER = Path('/home/vboxuser/cfb2_resume_tools_20261009_v3/codeflaws_byte_comparison_v2.py')
CHECKER_SHA = 'f2b005c8e7f9c9a28df125411b4d357e79e3e045c576da1b474230d225f9bdd5'
HERE = Path(__file__).resolve().parent
FILES = ('bp17_caseblock100_20261017_v1.py', 'test_bp17_caseblock100_20261017_v1.py',
         'run_bp17_v3_experiment.py', 'bp17_operational_bridge_v2.py',
         'cgo16_candidate_isolated_v2.py', 'check_fc_extension_baseline_preservation.py',
         'audit_bp17_caseblock100_saved_20261017_v1.py')
PRIMARY = (('BP2', 'BP1'), ('BP3', 'BP2'), ('BP1', 'BP0'))


def hashed(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def select_cases(rows, ledger):
    r.need(len({x['anonymous_id'] for x in rows}) == len(rows), 'unique_source_cases')
    lookup = {x['anonymous_id']: x for x in rows}
    r.need(all(x['case_id'] in lookup for x in ledger), 'known_prior_exposure')
    called_clusters = {lookup[x['case_id']]['cluster_root'] for x in ledger}
    chosen = []
    for cohort, target in (('exposed_exploratory', 60), ('previously_unexposed', 40)):
        clusters = defaultdict(list)
        for row in rows:
            if row['cohort'] != cohort or row['understanding_kind'] != 'native_behavior_projection':
                continue
            if cohort == 'previously_unexposed' and row['cluster_root'] in called_clusters:
                continue
            clusters[row['cluster_root']].append(row)
        r.need(len(clusters) >= target, 'insufficient_eligible_clusters')
        for cluster in sorted(clusters, key=lambda c: hashed(SEED+'/selection/'+cohort+'/'+c))[:target]:
            chosen.append(min(clusters[cluster], key=lambda x: hashed(SEED+'/representative/'+x['anonymous_id'])))
    r.need(len(chosen) == len({x['cluster_root'] for x in chosen}) == 100, '100_disjoint_case_clusters')
    return sorted(chosen, key=lambda x: hashed(SEED+'/case-order/'+x['anonymous_id']))


def case_jobs(row, frozen):
    r.need(len(frozen) == 8, 'eight_source_jobs')
    result = []
    for source in frozen:
        r.validate_request(source)
        r.need(source['case_id'] == row['anonymous_id'], 'source_case_binding')
        job = dict(source)
        job.update(source_job_id=source['job_id'], scientific_protocol_id=source['protocol_id'],
                   protocol_id=EXEC_ID, job_id='/'.join((EXEC_ID, row['anonymous_id'], source['group'], source['task'], '1')))
        result.append(job)
    r.need({(x['group'], x['task']) for x in result} == {(g, t) for g in r.GROUPS for t in r.TASKS}, 'complete_four_group_tasks')
    return sorted(result, key=lambda x: hashed(SEED+'/within-case/'+x['group']+'/'+x['task']+'/'+x['case_id']))


def validate_blocks(rows, jobs):
    r.need(len(rows) == len({x['anonymous_id'] for x in rows}) == len({x['cluster_root'] for x in rows}) == 100, '100_unique_case_clusters')
    r.need(Counter(x['cohort'] for x in rows) == Counter(exposed_exploratory=60, previously_unexposed=40), 'frozen_cohort_counts')
    r.need(all(x['understanding_kind'] == 'native_behavior_projection' for x in rows), 'P1_only')
    r.need(len(jobs) == len({x['job_id'] for x in jobs}) == 800, '800_unique_slots')
    for index, row in enumerate(rows):
        block = jobs[8*index:8*index+8]
        r.need({x['case_id'] for x in block} == {row['anonymous_id']}, 'contiguous_case_block')
        r.need({(x['group'], x['task']) for x in block} == {(g, t) for g in r.GROUPS for t in r.TASKS}, 'block_complete_tasks')
        for job in block:
            r.need(job['protocol_id'] == EXEC_ID and job['job_id'] == '/'.join((EXEC_ID, row['anonymous_id'], job['group'], job['task'], '1')), 'new_batch_job_identity')
            r.validate_request(job)
    return True


def waves(block, first=False):
    return [block[:1], block[1:4], block[4:]] if first else [block[:4], block[4:]]


def gate_receipt(receipt, jobs, rows):
    r.need(receipt.get('pass') is True and receipt['scored_count'] == len(jobs), 'complete_wave_receipt')
    actual = {v['job_id']: v for v in receipt['rows']}
    r.need(len(receipt['rows']) == len(actual) == len(jobs) and set(actual) == {j['job_id'] for j in jobs}, 'exact_wave_scores')
    for job in jobs:
        value = actual[job['job_id']]
        r.need(all(value[k] == job[k] for k in ('case_id', 'group', 'task', 'request_sha256')), 'score_job_identity')
        r.need(all(value[k] == rows[job['case_id']][k] for k in ('cohort', 'cluster_root', 'understanding_kind')), 'score_cohort_identity')
        r.need(value['status'] != 'infrastructure_failure', 'true_infrastructure_failure')
    return receipt


def block_gate(block, scores):
    r.need(len(block) == 8 and len({j['case_id'] for j in block}) == 1, 'one_full_case')
    r.need(set(scores) == {j['job_id'] for j in block}, 'case_must_complete_before_next')


@contextmanager
def global_lock(path):
    handle = Path(path).open('a+b')
    try:
        if os.name == 'nt':
            import msvcrt
            if handle.tell() == 0:
                handle.write(b'0'); handle.flush()
            handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        handle.close()


def preserve(mapping):
    for name, expected in mapping.items():
        r.need(Path(name).is_file() and r.sha(name) == expected, 'old_evidence_changed:'+Path(name).name)


def prepare(project, batch):
    project = project.resolve(); batch = batch.resolve()
    source = project/'03_experiments/results/bp17_model_2026-10-16/batch_v1'
    r.need(not batch.exists() and not batch.is_relative_to(source.parent), 'fresh_separate_new_batch')
    r.need(r.sha(source/'execution_manifest.json') == SOURCE_MANIFEST_SHA and r.sha(Path(r.__file__)) == SOURCE_RUNNER_SHA and r.sha(Path(bridge.__file__)) == BRIDGE_SHA, 'unchanged_original_tools')
    with global_lock(source.parent/'bp17_live_transport.lock'):
        original, original_jobs = r.verify_local(source)
        ledger = [json.loads(s) for s in (source/'attempt_ledger.jsonl').read_text(encoding='utf-8').splitlines() if s]
        r.need(len(ledger) == 5229 and [x['job_id'] for x in ledger] == [j['job_id'] for j in original_jobs[:5229]], 'unchanged_prior_5229_prefix')
        rows = select_cases(r.read(source/'rows.json'), ledger)
        jobs = []; selected_sources = {}
        for row in rows:
            case = row['anonymous_id']; path = source/'inputs'/case/'group_requests_NOT_SENT.json'
            r.need(r.sha(path) == original['inputs'][path.relative_to(source).as_posix()], 'selected_original_input_identity')
            selected_sources[str(path)] = r.sha(path)
            jobs.extend(case_jobs(row, r.read(path)))
        validate_blocks(rows, jobs)
        old_hashes = {str(p): r.sha(p) for p in source.parent.rglob('*') if p.is_file() and
                      p.suffix != '.lock' and '__pycache__' not in p.parts}
        batch.parent.mkdir(parents=True, exist_ok=True)
        r.resource_guard(batch.parent)
        batch.mkdir(parents=True)
        for name in FILES:
            dest = batch/'tools'/name; dest.parent.mkdir(exist_ok=True)
            shutil.copy2(HERE/name, dest)
        r.save(batch/'rows.json', rows); r.save(batch/'jobs.json', jobs)
        r.save(batch/'before_old_files.json', dict(files=old_hashes, count=len(old_hashes), original_batch_read_only=True))
        protocol = project/'01_research/workflow/bp17_caseblocked_100_protocol_2026-10-17_v1.md'
        shutil.copy2(protocol, batch/'protocol.md')
        old_ids = r.history_check(r.read(source/'history.json'))
        for path in (source/'cohorts').glob('*/*/*/*/*/result.json'):
            value = r.read(path)
            if value['status'] == 'completed':
                r.need(value['response_id'] not in old_ids, 'old_response_id_collision')
                old_ids.add(value['response_id'])
        r.need(len(old_ids) == 5691, 'old_actual_5691_responses')
        r.save(batch/'prior_response_ids.json', sorted(old_ids))
        r.save(batch/'authorization.json', dict(user_instruction='允许另存新执行协议，按案例成组、组内随机完成四组理解和修复；新模型指纹单独开批次，旧结果保留且不混算，开发和独立确认结果分开记录，继续实验。现有的先做100组共同案例。并进行对比',
            destination=r.ENDPOINT, data_scope='same frozen C source, visible diagnostics, compiler evidence and public questions only',
            private_answers_reference_patches_hidden_tests_excluded=True, authorized_calls=800, automatic_retries=0))
        manifest = dict(schema=EXEC_ID, batch_id=BATCH_ID, frozen_utc=r.now(), planned_pairs=100, planned_calls=800,
            cohorts=dict(exposed_exploratory=60, previously_unexposed=40), clusters=100, seed=SEED,
            model_identity=PIN, request_parameters=r.PARAMS, endpoint=r.ENDPOINT, remote_output=REMOTE,
            remote_tools=REMOTE_TOOLS, old_reserved_calls=5693, cumulative_max_slots=6493,
            source_batch=str(source), source_manifest_sha256=SOURCE_MANIFEST_SHA,
            source_ledger_sha256=r.sha(source/'attempt_ledger.jsonl'), source_selected_inputs=selected_sources,
            old_preservation_sha256=r.sha(batch/'before_old_files.json'), protocol_sha256=r.sha(batch/'protocol.md'),
            rows_sha256=r.sha(batch/'rows.json'), jobs_sha256=r.sha(batch/'jobs.json'),
            files={name: r.sha(batch/'tools'/name) for name in FILES},
            prior_response_ids_sha256=r.sha(batch/'prior_response_ids.json'), authorization_sha256=r.sha(batch/'authorization.json'),
            identity_file='C:/Users/chenm/.ssh/codex_ubuntu2204', automatic_retries=0, feedback_rounds=0,
            old_answers_reused_as_new_scores=0, native_baseline_reexecutions=0, old_scores_not_merged=True)
        r.save(batch/'execution_manifest.json', manifest)
        return dict(**{'pass': True}, planned=800, cases=100, confirmation_clusters=40, development_clusters=60,
                    preserved_old_files=len(old_hashes), manifest_sha256=r.sha(batch/'execution_manifest.json'))


def verified(batch):
    manifest = r.read(batch/'execution_manifest.json')
    r.need(manifest['batch_id'] == BATCH_ID and manifest['model_identity'] == PIN and manifest['planned_calls'] == 800 and manifest['request_parameters'] == r.PARAMS, 'new_batch_contract')
    for name, expected in manifest['files'].items():
        r.need(r.sha(HERE/name) == expected, 'frozen_new_tool_changed:'+name)
    for name, key in [('rows.json', 'rows_sha256'), ('jobs.json', 'jobs_sha256'), ('protocol.md', 'protocol_sha256'),
                      ('authorization.json', 'authorization_sha256'), ('before_old_files.json', 'old_preservation_sha256'),
                      ('prior_response_ids.json', 'prior_response_ids_sha256')]:
        r.need(r.sha(batch/name) == manifest[key], 'new_frozen_metadata_changed:'+name)
    rows = r.read(batch/'rows.json'); jobs = r.read(batch/'jobs.json'); validate_blocks(rows, jobs)
    return manifest, rows, jobs


def command(batch, mode):
    manifest = r.read(batch/'execution_manifest.json')
    return ['ssh', '-i', manifest['identity_file'], '-p', '2222', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
            '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=4', 'vboxuser@127.0.0.1',
            'env PYTHONDONTWRITEBYTECODE=1 python3 '+REMOTE_TOOLS+'/'+Path(__file__).name+' '+mode+' --batch '+REMOTE]


def call(batch, mode, payload=None, label=None):
    folder = batch/'remote_receipts'/(label or mode+'_'+str(time.time_ns()))
    folder.mkdir(parents=True, exist_ok=False)
    with (folder/'stdout.json').open('xb') as out, (folder/'stderr.log').open('xb') as err:
        proc = subprocess.Popen(command(batch, mode), stdin=subprocess.PIPE, stdout=out, stderr=err)
        if payload is not None:
            proc.stdin.write(r.canonical(payload)); proc.stdin.flush()
        proc.stdin.close(); started = time.monotonic()
        while proc.poll() is None:
            if time.monotonic()-started > (21600 if mode in ('remote-evaluate', 'remote-finish') else 180):
                proc.terminate(); proc.wait(timeout=10)
                raise ValueError('SSH_timeout_no_reexecution')
            time.sleep(.25)
    r.need(proc.returncode == 0, 'SSH_operation_failed:'+mode)
    value = r.read(folder/'stdout.json'); r.need(value.get('pass') is True, 'remote_gate_failed')
    return value


def remote_check(batch):
    identity = r.read(batch/'identity.json')
    r.need(str(batch) == REMOTE and identity['batch_id'] == BATCH_ID and identity['wrapper_sha256'] == r.sha(Path(__file__)), 'guest_wrapper_identity')
    r.need(identity['bridge_sha256'] == r.sha(Path(bridge.__file__)) == BRIDGE_SHA, 'guest_bridge_identity')
    result = bridge.status(batch)
    result.update(batch_id=BATCH_ID, wrapper_sha256=r.sha(Path(__file__)))
    return result


def remote_init(batch, payload):
    r.need(str(batch) == REMOTE and not batch.exists(), 'fresh_exact_guest_batch')
    numeric, classification, candidate = r.remote_imports(batch)
    old = r.read(Path('/home/vboxuser/bp17_model_20261016_v1/plan.json'))
    wanted = {v['anonymous_id']: v for v in old['rows']}
    rows = payload['rows']; jobs = payload['jobs']; validate_blocks(rows, jobs)
    native = {}; private_hashes = {}
    for index, row in enumerate(rows):
        case = row['anonymous_id']; r.need(row == wanted[case], 'original_row_changed')
        frozen = r.read(r.REMOTE_ROOT/'all_target_v3'/case/'group_requests_NOT_SENT.json')
        r.need(case_jobs(row, frozen) == jobs[8*index:8*index+8], 'guest_actual_request_regeneration')
        for name, expected in old['private_hashes'][case].items():
            r.need(r.sha(r.REMOTE_ROOT/'all_target_v3'/case/name) == expected, 'private_input_changed')
        directory = r.NATIVE/'runs/cases'/row['private_case_id']
        h = r.sha(directory/'result.json'); record = r.read(directory/'result.json')
        r.need(h == old['native_result_hashes'][case] == r.read(directory/'receipt.json')['result_sha256'] and record['status'] == 'pair_reproduced', 'native_receipt_changed')
        native[case] = h; private_hashes[case] = old['private_hashes'][case]
    batch.mkdir()
    from check_fc_extension_baseline_preservation import check
    baseline = check(r.NATIVE, batch/'baseline_before.json')
    r.need(baseline['pass'] and baseline['resource_protection_pass'], 'baseline_before')
    plan = dict(rows=rows, jobs=jobs, native_result_hashes=native, private_hashes=private_hashes,
                host_manifest_sha256=payload['manifest_sha256'], model_identity=PIN)
    r.save(batch/'plan.json', plan)
    r.save(batch/'identity.json', dict(batch_id=BATCH_ID, planned=800, prepared_utc=r.now(),
        boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(), runner_sha256=r.sha(Path(r.__file__)),
        wrapper_sha256=r.sha(Path(__file__)), bridge_sha256=r.sha(Path(bridge.__file__)), model_identity=PIN))
    return remote_check(batch)


def readonly_receipt(batch, wave):
    name = 'wave_'+str(wave).zfill(5)+'.json'
    target = batch/'readonly_receipts'/name; target.parent.mkdir(exist_ok=True)
    cfg = r.read(batch/'execution_manifest.json')
    result = subprocess.run(['scp', '-i', cfg['identity_file'], '-P', '2222', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10',
                             'vboxuser@127.0.0.1:'+REMOTE+'/wave_receipts/'+name, str(target)], capture_output=True, timeout=45)
    r.need(result.returncode == 0 and target.is_file(), 'no_committed_receipt_stop_no_rerun')
    return r.read(target)


def reserve(batch, jobs, reserved):
    r.need(len(reserved)+len(jobs) <= 800 and len({j['job_id'] for j in jobs}) == len(jobs) and
           not reserved & {j['job_id'] for j in jobs}, 'finite_unique_reservation')
    with (batch/'attempt_ledger.jsonl').open('a', encoding='utf-8', newline='\n') as stream:
        for job in jobs:
            row = {k: job[k] for k in ('job_id', 'case_id', 'group', 'task', 'request_sha256')}
            row.update(ordinal=len(reserved)+1, cumulative_ordinal=5694+len(reserved), reserved_utc=r.now(), status='reserved_before_network')
            stream.write(json.dumps(row)+'\n'); stream.flush(); os.fsync(stream.fileno()); reserved.add(job['job_id'])


def run(batch):
    manifest, rows, jobs = verified(batch); rowmap = {v['anonymous_id']: v for v in rows}
    r.need(not (batch/'one_shot.started.json').exists() and not (batch/'attempt_ledger.jsonl').exists(), 'already_started_do_not_retry')
    unit = [r.read(batch/name) for name in ('unit_local.json', 'unit_guest.json')]
    r.need(all(v['pass'] and v['tests'] >= 20 and v['failures'] == v['errors'] == v['skipped'] == 0 and
               v['controller_sha256'] == r.sha(Path(__file__)) for v in unit), 'two_platform_controls_required')
    key = os.environ.get('DEEPSEEK_API_KEY'); r.need(bool(key), 'missing_API_key')
    reserved = set(); seen = set(r.read(batch/'prior_response_ids.json')); counts = Counter(); active = None
    stop = threading.Event(); unsafe = []; phase = 'stopped'; reason = None
    def watch():
        while not stop.wait(15):
            try: r.resource_guard(batch)
            except Exception: unsafe.append(True); return
    def snapshot(label):
        value = dict(batch_id=BATCH_ID, pid=os.getpid(), phase=label, updated_utc=r.now(), planned=800,
            reserved=len(reserved), remaining=800-len(reserved), counts=dict(counts), active=active,
            cumulative_reserved=5693+len(reserved), model_identity=PIN, cases_planned=100,
            independent_confirmation_cases=40, development_cases=60, automatic_retries=0, old_results_not_merged=True)
        r.progress(batch/'progress.json', value); return value
    with global_lock(Path(manifest['source_batch']).parent/'bp17_live_transport.lock'):
        try:
            r.resource_guard(batch); preserve(r.read(batch/'before_old_files.json')['files'])
            initial = call(batch, 'remote-status'); r.need(initial['ready'] and initial['host_manifest_sha256'] == r.sha(batch/'execution_manifest.json'), 'guest_not_ready')
            r.save(batch/'provider_listing.json', r.listing(key))
            r.save(batch/'one_shot.started.json', dict(pid=os.getpid(), started_utc=r.now(), manifest_sha256=r.sha(batch/'execution_manifest.json'), guest_boot=initial['boot_id']))
            r.save(batch/'model_identity.json', PIN)
            threading.Thread(target=watch, daemon=True).start(); snapshot('identity_gate')
            wave_number = 0
            with ThreadPoolExecutor(max_workers=4) as pool:
                for index, case in enumerate(rows):
                    block = jobs[8*index:8*index+8]; scored_block = {}
                    for wave in waves(block, first=index == 0):
                        r.need(not unsafe, 'host_resource_protection'); r.resource_guard(batch)
                        health = call(batch, 'remote-status')
                        r.need(health['ready'] and health['boot_id'] == initial['boot_id'], 'guest_changed')
                        wave_number += 1
                        active = dict(case_ordinal=index+1, case_id=case['anonymous_id'], cohort=case['cohort'], wave=wave_number, jobs=[j['job_id'] for j in wave])
                        reserve(batch, wave, reserved); snapshot('model_calls_inflight')
                        returned = list(pool.map(lambda j: r.send(j, key, r.result_folder(batch, case, j)), wave))
                        for value in returned: counts[value['status']] += 1
                        for value in returned:
                            r.identity(value, PIN); r.need(value['response_id'] not in seen, 'response_id_collision'); seen.add(value['response_id'])
                        snapshot('isolated_evaluation')
                        try:
                            receipt = call(batch, 'remote-evaluate', dict(wave=wave_number, responses=returned, model_identity=PIN), 'wave_'+str(wave_number).zfill(5))
                        except ValueError as error:
                            if str(error) != 'SSH_operation_failed:remote-evaluate': raise
                            receipt = readonly_receipt(batch, wave_number)
                        gate_receipt(receipt, wave, rowmap)
                        r.save(batch/'evaluation_receipts'/('wave_'+str(wave_number).zfill(5)+'.json'), receipt)
                        for value in receipt['rows']:
                            scored_block[value['job_id']] = value
                            counts['scored_'+value['task']] += 1; counts['scored_'+value['cohort']] += 1
                        counts['evaluated'] += len(receipt['rows']); snapshot('wave_completed')
                    block_gate(block, scored_block)
                    r.save(batch/'case_receipts'/(case['anonymous_id']+'.json'), dict(case_id=case['anonymous_id'], cohort=case['cohort'], cluster_root=case['cluster_root'], evaluated=8, rows=list(scored_block.values()), **{'pass':True}))
                    counts['completed_cases'] += 1; counts['completed_cases_'+case['cohort']] += 1
                    snapshot('case_completed')
                    print(json.dumps(dict(time_utc=r.now(), complete_cases=counts['completed_cases'], confirmation=counts['completed_cases_previously_unexposed'], development=counts['completed_cases_exposed_exploratory'], evaluated=counts['evaluated'], planned=800)), flush=True)
            r.need(len(reserved) == counts['completed'] == counts['evaluated'] == 800 and counts['completed_cases'] == 100, 'all_100_blocks_required')
            snapshot('saved_byte_audit_and_archive')
            r.save(batch/'remote_completion.json', call(batch, 'remote-finish'))
            preserve(r.read(batch/'before_old_files.json')['files'])
            r.save(batch/'comparison.json', compare_scores(batch, rows, jobs))
            phase = 'completed'
        except Exception as error:
            reason = str(error) if type(error) is ValueError else type(error).__name__
        finally:
            stop.set(); value = snapshot(phase); value.update(reason=reason, ended_utc=r.now(), all_results_jointly_verified=False)
            r.save(batch/('completion.json' if phase == 'completed' else 'stop.json'), value)
    return value


def compare_scores(batch, rows, jobs):
    from statistics import mean
    scores = [v for path in sorted((batch/'evaluation_receipts').glob('wave_*.json')) for v in r.read(path)['rows']]
    r.need(len(scores) == len({v['job_id'] for v in scores}) == 800 and {v['job_id'] for v in scores} == {j['job_id'] for j in jobs}, 'exact_800_comparison_scope')
    def win(v):
        return v['score']['correct'] if v['task'] == 'understanding' else int(v['status'] == 'all_tests_passed' and v['repair_pass'] and v['heldout_pass'])
    out = dict(batch_id=BATCH_ID, model_identity=PIN, old_scores_merged=False, cohorts={})
    for cohort, n in (('exposed_exploratory', 60), ('previously_unexposed', 40)):
        out['cohorts'][cohort] = {}
        for task in r.TASKS:
            maps = {g:{v['case_id']:v for v in scores if v['cohort'] == cohort and v['task'] == task and v['group'] == g} for g in r.GROUPS}
            common = sorted(set.intersection(*(set(m) for m in maps.values())))
            r.need(len(common) == n, 'all_four_exact_common_cases')
            item = dict(cases=n, clusters=n, groups={g:dict(successes=sum(win(maps[g][k]) for k in common), n=n, rate=mean(win(maps[g][k]) for k in common)) for g in r.GROUPS}, comparisons={})
            for a, b in PRIMARY:
                differences = [win(maps[a][k])-win(maps[b][k]) for k in common]
                wins = differences.count(1); losses = differences.count(-1)
                value = dict(cases=n, clusters=n, left_successes=item['groups'][a]['successes'], right_successes=item['groups'][b]['successes'], left_only=wins, right_only=losses, paired_difference=mean(differences))
                if cohort == 'previously_unexposed':
                    rng = random.Random(20261017)
                    samples = sorted(sum(differences[rng.randrange(n)] for _ in range(n))/n for _ in range(10000))
                    value['bootstrap_95_percentile'] = [samples[249], samples[9749]]
                    discordant = wins+losses
                    value['exact_p'] = min(1, 2*sum(math.comb(discordant, k) for k in range(min(wins, losses)+1))/2**discordant) if discordant else 1
                item['comparisons'][a+'-'+b] = value
            if cohort == 'previously_unexposed':
                running = 0
                ordered = sorted(item['comparisons'].values(), key=lambda v:v['exact_p'])
                for index, value in enumerate(ordered):
                    running = max(running, min(1, (3-index)*value['exact_p'])); value['holm_p'] = running
            out['cohorts'][cohort][task] = item
    return out


def remote_finish(batch):
    remote_check(batch); plan = r.read(batch/'plan.json')
    from audit_bp17_caseblock100_saved_20261017_v1 import audit
    result = audit(batch, plan)
    r.save(batch/'saved_byte_audit.json', result)
    from check_fc_extension_baseline_preservation import check
    baseline = check(r.NATIVE, batch/'baseline_after.json')
    r.need(baseline['pass'] and baseline['resource_protection_pass'], 'baseline_after')
    archive = batch.parent/(batch.name+'_archive'); archive.mkdir()
    files = {p.relative_to(batch).as_posix(): r.sha(p) for p in batch.rglob('*') if p.is_file()}
    r.save(archive/'payload_manifest.json', files)
    with tarfile.open(archive/'records.tar.gz', 'w|gz') as tar:
        for index, name in enumerate(sorted(files)):
            if index % 1000 == 0: r.resource_guard(batch)
            tar.add(batch/name, arcname=name, recursive=False)
    verify_archive(archive/'records.tar.gz', files)
    identity = dict(payload_members=len(files), sha256=r.sha(archive/'records.tar.gz'), bytes=(archive/'records.tar.gz').stat().st_size, saved_byte_audit_passed=True, model_calls=0, candidate_C_reexecutions=0)
    r.save(archive/'archive_identity.json', identity)
    value = dict(batch_id=BATCH_ID, evaluated=800, complete_cases=100, audit=result, archive=identity, completed_utc=r.now(), **{'pass':True})
    r.save(batch/'completion.json', value); return value


def verify_archive(path, files):
    checked = set()
    with tarfile.open(path, 'r|gz') as tar:
        for member in tar:
            r.need(member.isfile() and member.name in files and member.name not in checked, 'archive_exact_safe_members')
            h = hashlib.sha256(); stream = tar.extractfile(member)
            for data in iter(lambda:stream.read(1024**2), b''):
                h.update(data)
            r.need(h.hexdigest() == files[member.name], 'archive_member_sha')
            checked.add(member.name)
    r.need(checked == set(files), 'archive_all_members')


def test_controls(output):
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern='test_bp17_caseblock100_20261017_v1.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    value = dict(**{'pass':result.wasSuccessful() and not result.skipped}, tests=result.testsRun, failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
                 controller_sha256=r.sha(Path(__file__)), model_calls=0, candidate_executions=0)
    r.save(output, value); return value


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('mode', choices=('prepare', 'run', 'units', 'remote-init', 'remote-status', 'remote-evaluate', 'remote-finish'))
    p.add_argument('--project', type=Path); p.add_argument('--batch', type=Path); p.add_argument('--output', type=Path); a = p.parse_args()
    try:
        if a.mode == 'prepare': value = prepare(a.project, a.batch)
        elif a.mode == 'units': value = test_controls(a.output)
        elif a.mode == 'run': value = run(a.batch)
        elif a.mode == 'remote-init': value = remote_init(a.batch, json.load(sys.stdin))
        elif a.mode == 'remote-status': value = remote_check(a.batch)
        elif a.mode == 'remote-evaluate':
            remote_check(a.batch); value = bridge.evaluate(a.batch, json.load(sys.stdin))
        else: value = remote_finish(a.batch)
        print(json.dumps(value, ensure_ascii=False), flush=True)
        raise SystemExit(value.get('pass') is False or value.get('phase') == 'stopped')
    except Exception as error:
        print(json.dumps({'pass':False, 'error':str(error) if type(error) is ValueError else type(error).__name__}), flush=True)
        raise SystemExit(1)
