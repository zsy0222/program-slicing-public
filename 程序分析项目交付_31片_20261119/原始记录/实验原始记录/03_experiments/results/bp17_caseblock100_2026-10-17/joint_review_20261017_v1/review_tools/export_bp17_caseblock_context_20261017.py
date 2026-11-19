"""Export an immutable completed guest's audit context. No C or model calls."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

BATCH = Path('/home/vboxuser/bp17_caseblock100_20261017_v1')
PREP = Path('/home/vboxuser/bp17_full_target_20261016_v1/all_target_v3')
NATIVE = Path('/home/vboxuser/cfb2/runs/cases')
CHECKER = Path('/home/vboxuser/cfb2_resume_tools_20261009_v3/codeflaws_byte_comparison_v2.py')
CHECKER_SHA = 'f2b005c8e7f9c9a28df125411b4d357e79e3e045c576da1b474230d225f9bdd5'


def need(ok, why):
    if not ok: raise ValueError(why)


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2), b''): h.update(chunk)
    return h.hexdigest()


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f: json.dump(value, f, ensure_ascii=False, indent=2)


def export(output):
    need(not output.exists() and output.parent == BATCH.parent and output.name.startswith('bp17_caseblock100_audit_context_'), 'fresh_separate_context')
    complete = read(BATCH/'completion.json'); plan = read(BATCH/'plan.json')
    need(complete['pass'] and complete['evaluated'] == 800 and complete['audit']['pass'] and len(plan['rows']) == 100, 'completed_audited_batch_required')
    need(sha(CHECKER) == CHECKER_SHA, 'frozen_checker_sha')
    output.mkdir(); payload = output/'payload'; payload.mkdir()
    shutil.copy2(BATCH/'plan.json', payload/'plan.json')
    shutil.copy2(BATCH/'completion.json', payload/'completion.json')
    shutil.copy2(CHECKER, payload/'codeflaws_byte_comparison_v2.py')
    expected_tests = 0
    for row in plan['rows']:
        case = row['anonymous_id']; need(case.startswith('BP17-') and len(case) == 9 and case[5:].isdigit(), 'safe_case')
        dest = payload/'cases'/case; dest.mkdir(parents=True)
        src = PREP/case/'answers_private.json'
        need(sha(src) == plan['private_hashes'][case]['answers_private.json'], 'frozen_private_answer')
        shutil.copy2(src, dest/'answers_private.json')
        native = NATIVE/row['private_case_id']
        need(sha(native/'result.json') == plan['native_result_hashes'][case] == read(native/'receipt.json')['result_sha256'], 'original_native_receipt')
        shutil.copy2(native/'result.json', dest/'native_result.json')
        shutil.copy2(native/'receipt.json', dest/'native_receipt.json')
        record = read(native/'result.json'); source = Path(record['metadata']['buggy'])
        need(sha(source) == record['metadata']['source_hashes']['buggy'] == row['source_sha256'], 'original_buggy_source')
        shutil.copy2(source, dest/'buggy.c'); index = []
        for suite, tests in record['metadata']['suites'].items():
            need(suite in ('repair','heldout') and bool(tests), 'both_original_suites')
            for test in tests:
                key = suite+'/'+hashlib.sha256(test['id'].encode()).hexdigest()
                item = dict(suite=suite, id=test['id'])
                for role in ('input','expected'):
                    file = Path(test[role]); need(sha(file) == test[role+'_sha256'], 'original_test_changed')
                    target = dest/'tests'/key/(role+'.bin'); target.parent.mkdir(parents=True, exist_ok=True)
                    need(not target.exists(), 'no_duplicate_test'); shutil.copy2(file, target)
                    item[role] = target.relative_to(dest).as_posix(); item[role+'_sha256'] = sha(target)
                index.append(item); expected_tests += 1
        save(dest/'test_index.json', index)
    files = {p.relative_to(payload).as_posix():sha(p) for p in payload.rglob('*') if p.is_file()}
    save(output/'manifest.json', files)
    with tarfile.open(output/'context.tar.gz','w|gz') as tar:
        for name in sorted(files): tar.add(payload/name, arcname=name, recursive=False)
    identity = dict(schema='BP17-readonly-completed-context-v1', sha256=sha(output/'context.tar.gz'),
                    bytes=(output/'context.tar.gz').stat().st_size, payload_members=len(files), original_tests=expected_tests,
                    checker_sha256=CHECKER_SHA, exporter_sha256=sha(Path(__file__)), model_calls=0, candidate_C_executions=0)
    save(output/'identity.json', identity); return identity


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path, required=True); args = parser.parse_args()
    print(json.dumps(export(args.output)), flush=True)
