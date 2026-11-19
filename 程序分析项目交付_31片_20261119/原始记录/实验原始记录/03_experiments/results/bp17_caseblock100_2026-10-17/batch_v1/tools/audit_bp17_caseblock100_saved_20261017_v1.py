"""Saved-byte audit for the new 100 blocks; never compiles or executes C."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import run_bp17_v3_experiment as r
import bp17_operational_bridge_v2 as bridge


def audit(batch, plan):
    from bp17_caseblock100_20261017_v1 import PIN, CHECKER, CHECKER_SHA, BATCH_ID
    r.need(r.sha(CHECKER) == CHECKER_SHA, 'frozen_byte_checker_identity')
    spec = importlib.util.spec_from_file_location('frozen_saved_byte_checker', CHECKER)
    checker = importlib.util.module_from_spec(spec); spec.loader.exec_module(checker)
    numeric, classification, candidate = r.remote_imports(batch)
    jobs = {v['job_id']:v for v in plan['jobs']}; rows = {v['anonymous_id']:v for v in plan['rows']}
    seen = set(); counts = Counter(); response_ids = set(); scores = []
    for path in sorted((batch/'cohorts').glob('*/*/*/*/scored.json')):
        score = r.read(path); job = jobs[score['job_id']]; row = rows[job['case_id']]; directory = path.parent
        r.resource_guard(batch)
        r.need(score['job_id'] not in seen, 'duplicate_scored_job'); seen.add(score['job_id'])
        r.need(all(score[k] == job[k] for k in ('case_id','group','task','request_sha256')) and
               all(score[k] == row[k] for k in ('cohort','cluster_root','understanding_kind')), 'saved_score_binding')
        response = r.read(directory/'response.json'); r.identity(response, PIN)
        r.need(response['response_id'] not in response_ids, 'duplicate_response'); response_ids.add(response['response_id'])
        r.need(all(response[k] == job[k] for k in ('job_id','case_id','group','task','request_sha256')), 'saved_response_binding')
        case = job['case_id']; private = r.REMOTE_ROOT/'all_target_v3'/case
        for name, expected in plan['private_hashes'][case].items():
            r.need(r.sha(private/name) == expected, 'private_record_identity')
        if job['task'] == 'understanding':
            recomputed = numeric.score(response['content'], r.read(private/'answers_private.json'))
            r.need(recomputed == score['score'], 'understanding_score_recompute')
            counts['understanding_recomputed'] += 1
        else:
            native = r.NATIVE/'runs/cases'/row['private_case_id']/'result.json'
            r.need(r.sha(native) == plan['native_result_hashes'][case], 'native_identity')
            record = r.read(native); output = directory/'candidate'; evaluation = r.read(output/'evaluation.json')
            r.need(r.sha(output/'evaluation.json') == score['evaluation_sha256'], 'saved_candidate_summary_sha')
            original = Path(record['metadata']['buggy'])
            r.need(r.sha(original) == record['metadata']['source_hashes']['buggy'], 'buggy_source_identity')
            valid_source = None
            try:
                submitted = numeric.strict_json(response['content'])
                r.need(isinstance(submitted, dict) and set(submitted) == {'source'} and isinstance(submitted['source'], str), 'strict_source_JSON')
                candidate.scope(submitted['source'], original.read_text(encoding='utf-8'))
                valid_source = submitted['source']
            except (ValueError, TypeError, KeyError):
                r.need(evaluation['status'] == 'rejected' and not evaluation['candidate_tests'], 'scope_rejection_consistency')
            compilation_path = output/'compilation.json'
            if valid_source is not None:
                compilation = r.read(compilation_path)
                r.need((output/'build'/original.name).read_bytes() == valid_source.encode('utf-8') and
                       compilation['source_sha256'] == r.sha(output/'build'/original.name), 'candidate_exact_model_source')
                for stage, expected in [('compile', ['/usr/bin/gcc', *record['recipe']['cflags'], '-c', original.name, '-o', 'program.o']),
                                        ('link', ['/usr/bin/gcc', 'program.o', '-o', 'program', *record['recipe']['ldflags']])]:
                    observation = compilation[stage]
                    if observation is None:
                        r.need(stage == 'link' and evaluation['status'] == 'rejected', 'missing_compilation_stage'); continue
                    command = observation['command']; boundary = command.index('--')
                    r.need(command[boundary+1:] == expected, 'original_compiler_flags')
                    for stream in ('stdout', 'stderr'):
                        r.need(r.sha(output/stage/(stream+'.bin')) == observation[stream+'_sha256'], 'compiler_saved_bytes')
                counts['candidate_sources_bound'] += 1
            specifications = {(suite, t['id']):t for suite, values in record['metadata']['suites'].items() for t in values}
            tested = evaluation['candidate_tests']; keys = [(t['suite'], t['id']) for t in tested]
            r.need(len(keys) == len(set(keys)) and set(keys) <= set(specifications), 'test_identity_scope')
            if evaluation['status'] in ('all_tests_passed', 'test_failed'):
                r.need(set(keys) == set(specifications), 'complete_original_test_sets')
                r.need(valid_source is not None and compilation['link'] is not None and
                       all(not compilation[s]['timeout'] and not compilation[s]['output_limited'] and not compilation[s]['resource_stop'] and compilation[s]['returncode'] == 0 for s in ('compile','link')), 'successful_original_compile_and_link')
            for test in tested:
                item = specifications[(test['suite'], test['id'])]
                for key in ('input', 'expected'):
                    r.need(r.sha(Path(item[key])) == item[key+'_sha256'], 'original_test_or_oracle_changed')
                folder = output/('test_'+test['suite']+'_'+test['id']); observation = test['execute']
                raw = (folder/'stdout.bin').read_bytes(); err = (folder/'stderr.bin').read_bytes()
                r.need(hashlib.sha256(raw).hexdigest() == observation['stdout_sha256'] and raw.hex() == observation['stdout_hex'] and
                       len(raw) == observation['stdout_bytes'] and hashlib.sha256(err).hexdigest() == observation['stderr_sha256'], 'candidate_saved_test_bytes')
                profile = record['recipe']['suites'][test['suite']]['normalizer']
                normalized = checker.normalize_bytes(raw, profile)
                equal = checker.portable_equal(raw, Path(item['expected']).read_bytes(), profile)
                comparison = test['comparison']
                r.need(comparison['valid'] and comparison['profile'] == profile and comparison['equal'] == equal and
                       hashlib.sha256(normalized).hexdigest() == comparison['normalized_sha256'] == r.sha(folder/'normalized_stdout'), 'independent_portable_judge')
                status = candidate.observation_status(observation, dict(valid=True, equal=equal))
                r.need(test['status'] == status and test['pass'] == (status == 'pass') and not observation['resource_stop'], 'candidate_test_status_recompute')
                counts['candidate_tests_recomputed'] += 1
                counts['candidate_'+test['suite']+'_tests_recomputed'] += 1
            classified = bridge.classify(evaluation, output, record)
            r.need(all(score[k] == v for k,v in classified.items()) and score['status'] != 'infrastructure_failure', 'candidate_score_recompute')
            counts['repair_recomputed'] += 1
        scores.append(score)
    r.need(seen == set(jobs) and len(seen) == 800 and counts['understanding_recomputed'] == counts['repair_recomputed'] == 400, 'all_800_exact_audit_scope')
    for case in rows:
        r.need(len([v for v in scores if v['case_id'] == case]) == 8, 'all_100_eight_task_cases')
    return dict(batch_id=BATCH_ID, **{'pass':True}, errors=[], scope='all_100_case_blocks', audited_jobs=800,
                complete_cases=100, counts=dict(counts), checker_sha256=CHECKER_SHA, auditor_sha256=r.sha(Path(__file__)),
                model_calls=0, candidate_C_reexecutions=0, original_tests_judge_changed=False, rows=scores)
