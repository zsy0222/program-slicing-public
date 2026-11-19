"""Archive-only continuation of 800 completed scores. No C/API/evaluator calls.

Keep the failed runner, zero-byte archive, original manifest and stop intact.
Python 3.10 streaming gzip needs a string filename, not pathlib.Path.
"""
import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile

BATCH = Path('/home/vboxuser/bp17_caseblock100_20261017_v1')
FAILED = Path('/home/vboxuser/bp17_caseblock100_20261017_v1_archive')
OUTPUT = Path('/home/vboxuser/bp17_caseblock100_20261017_v1_archive_completion_v1')


def need(ok, why):
    if not ok: raise ValueError(why)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024**2), b''): h.update(b)
    return h.hexdigest()


def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def save(path, value):
    with Path(path).open('x', encoding='utf-8') as f: json.dump(value, f, ensure_ascii=False, indent=2)


def guard(path):
    free = shutil.disk_usage(path).free
    mem = next(int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:'))
    need(free >= 15*1024**3 and mem >= 2*1024**3, 'original_15GiB_2GiB_protection')
    return dict(disk_free_bytes=free, MemAvailable_bytes=mem)


def stream_pack(path, root, files, callback=lambda:None):
    # Explicit str conversion is the only library-compatibility change.
    with tarfile.open(str(path), 'w|gz') as tar:
        tar.dereference = True
        for i, name in enumerate(sorted(files)):
            if i % 500 == 0: callback()
            tar.add(root/name, arcname=name, recursive=False)


def check_archive(path, files, callback=lambda:None):
    seen = set()
    with tarfile.open(str(path), 'r|gz') as tar:
        for i, member in enumerate(tar):
            if i % 500 == 0: callback()
            need(member.isfile() and member.name in files and member.name not in seen, 'exact_regular_unique_archive_members')
            h = hashlib.sha256(); source = tar.extractfile(member)
            for b in iter(lambda:source.read(1024**2), b''): h.update(b)
            need(h.hexdigest() == files[member.name], 'member_SHA256')
            seen.add(member.name)
    need(seen == set(files), 'all_manifest_members')
    with gzip.open(path, 'rb') as f:
        for _ in iter(lambda:f.read(1024**2), b''): pass
    return len(seen)


def controls():
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp);(root/'data.bin').write_bytes(b'x'*10001)
        files={'data.bin':sha(root/'data.bin')};dest=root/'test.tar.gz'
        stream_pack(dest,root,files);need(check_archive(dest,files)==1,'roundtrip')
        try: check_archive(dest,{'data.bin':'0'*64})
        except ValueError: pass
        else: raise ValueError('wrong_hash_not_refused')
    return dict(pass_controls=True, roundtrip=True, wrong_hash_refused=True, model_calls=0, C_executions=0)


def finish():
    need(not OUTPUT.exists() and not (BATCH/'completion.json').exists(), 'fresh_one_shot_archive_continuation')
    need((FAILED/'records.tar.gz').stat().st_size == 0 and not (FAILED/'archive_identity.json').exists(), 'exact_failed_archive_state')
    audit=read(BATCH/'saved_byte_audit.json');baseline=read(BATCH/'baseline_after.json')
    need(audit['pass'] and not audit['errors'] and audit['audited_jobs']==800 and audit['complete_cases']==100,
         'all_800_saved_scores_already_audited')
    need(baseline['pass'] and baseline['resource_protection_pass'], 'completed_baseline_preservation')
    files=read(FAILED/'payload_manifest.json')
    need(set(files)=={p.relative_to(BATCH).as_posix() for p in BATCH.rglob('*') if p.is_file()},'exact_saved_payload_range')
    resources=guard(BATCH);OUTPUT.mkdir()
    save(OUTPUT/'intent.json',dict(schema='archive-only-compatibility-completion-v1',
         helper_sha256=sha(__file__), prior_manifest_sha256=sha(FAILED/'payload_manifest.json'),
         original_failure='Python3.10 tarfile streaming gzip PosixPath.endswith AttributeError',
         original_failed_archive_preserved=True, original_runner_not_restarted=True,
         C_executions=0, model_calls=0, resources=resources))
    for i,(name,expected) in enumerate(files.items()):
        if i%500==0: guard(BATCH)
        need(sha(BATCH/name)==expected,'saved_payload_unchanged')
    save(OUTPUT/'payload_manifest.json',files)
    print(json.dumps(dict(phase='packing_saved_records',members=len(files))),flush=True)
    archive=OUTPUT/'records.tar.gz';stream_pack(archive,BATCH,files,lambda:guard(BATCH))
    members=check_archive(archive,files,lambda:guard(BATCH))
    identity=dict(payload_members=members,sha256=sha(archive),bytes=archive.stat().st_size,
        saved_byte_audit_passed=True,model_calls=0,candidate_C_reexecutions=0,
        archive_only_recovery=True,helper_sha256=sha(__file__),failed_archive_preserved=str(FAILED))
    save(OUTPUT/'archive_identity.json',identity)
    for i,(name,expected) in enumerate(files.items()):
        if i%500==0:guard(BATCH)
        need(sha(BATCH/name)==expected,'payload_unchanged_after_archive')
    value=dict(batch_id='BP17-caseblock100-model-20261017-v1',evaluated=800,complete_cases=100,
        audit=audit,archive=identity,archive_directory=str(OUTPUT),completed_utc=datetime.now(timezone.utc).isoformat(),
        **{'pass':True},original_runner_stop_preserved=True)
    save(BATCH/'completion.json',value)
    return {k:value[k] for k in ('batch_id','pass','evaluated','complete_cases','archive_directory')}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');a=p.parse_args()
    print(json.dumps(controls() if a.controls else finish()),flush=True)
