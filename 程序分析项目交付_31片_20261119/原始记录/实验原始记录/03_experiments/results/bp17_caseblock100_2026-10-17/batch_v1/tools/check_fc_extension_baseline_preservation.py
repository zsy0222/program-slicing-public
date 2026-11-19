"""Read frozen baseline bytes; write only one fresh out-of-baseline journal."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil


def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()


def check(root, output):
    root=root.resolve();output=output.resolve()
    if root!=Path('/home/vboxuser/cfb2') or output.is_relative_to(root) or output.exists():raise ValueError('exact_baseline_and_fresh_separate_journal_required')
    snapshots=[('before_terminal_hashes.json','1427be57cc0f2b9dfe0dc5d13bfc2aacdb3572712984b55a496f1f521b1614d8'),
        ('before_context_and_old_hashes.json','fae5c51a2eafb1b39e850f14cf10c68f32185e16d7cb50f7dd0e18bbbc5729db')]
    combined={};sizes=[]
    for name,expected in snapshots:
        p=root/'finish_20261011_v1'/name
        if sha(p)!=expected:raise ValueError('snapshot_identity_changed')
        rows=json.loads(p.read_text());sizes.append(len(rows))
        for n,h in rows.items():
            if n in combined and combined[n]!=h:raise ValueError('snapshot_conflict')
            combined[n]=h
    changed=[];missing=[]
    for name,h in combined.items():
        p=(root/name).resolve()
        if not p.is_relative_to(root):raise ValueError('snapshot_path_escape')
        if not p.is_file():missing.append(name)
        elif sha(p)!=h:changed.append(name)
    result_files={str(p.relative_to(root)) for p in (root/'runs/cases').glob('*/result.json')}
    snapshot_results={n for n in combined if n.startswith('runs/cases/') and n.endswith('/result.json')}
    mem=next(int(l.split()[1])*1024 for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:'))
    free=shutil.disk_usage(root).free
    result={'schema':'FC-extension-baseline-preservation-20261015-r1','time_utc':datetime.now(timezone.utc).isoformat(),
        'pass':not changed and not missing and result_files==snapshot_results and len(result_files)==3903,
        'snapshots_entries':sizes,'unique_files_checked':len(combined),'changed':changed,'missing':missing,
        'terminal_pairs':len(result_files),'exact_original_result_range':result_files==snapshot_results,
        'disk_free_bytes':free,'MemAvailable_bytes':mem,'resource_protection_pass':mem>=2*1024**3 and free>=15*1024**3,
        'baseline_C_reexecutions':0,'model_calls':0,'baseline_writes':0,'checker_sha256':sha(__file__)}
    with output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=check(a.root,a.output);print(json.dumps(r));raise SystemExit(0 if r['pass'] and r['resource_protection_pass'] else 1)
