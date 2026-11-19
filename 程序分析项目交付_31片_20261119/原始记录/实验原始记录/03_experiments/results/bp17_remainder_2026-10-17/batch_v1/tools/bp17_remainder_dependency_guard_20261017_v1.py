"""Operational outer guard: hash-gate every frozen dependency at both endpoints.

The prepared v1 controller, requests, scorers and candidate evaluator stay
byte-for-byte unchanged. Only remote command routing uses this guarded entry.
"""
import argparse
import json
from pathlib import Path
import sys
import bp17_caseblocked_remainder_20261017_v1 as b

HERE=Path(__file__).resolve().parent


def verify_guard(expected):
    path=HERE/'dependency_guard_manifest.json'
    b.r.need(b.r.sha(path)==expected,'dependency_guard_manifest_changed')
    guard=b.r.read(path)
    b.r.need(guard['execution_manifest_sha256']=='779e1c04740538d0510f1e9c99d9f9f0e3a4ba7db90d1efeb7ac174dbbe25472','guard_original_execution_binding')
    for name,h in guard['files'].items():b.r.need(b.r.sha(HERE/name)==h,'frozen_dependency_changed:'+name)
    return guard


def execute(mode,batch,expected):
    guard=verify_guard(expected)
    if mode=='run':
        original=b.command
        def command(folder,remote_mode):
            result=original(folder,remote_mode)
            old=b.REMOTE_TOOLS+'/'+Path(b.__file__).name
            new=b.REMOTE_TOOLS+'/'+Path(__file__).name
            result[-1]=result[-1].replace(old,new,1)+' --guard-sha '+expected
            return result
        b.command=command
        try:value=b.run(batch)
        finally:b.command=original
    elif mode=='remote-status':value=b.remote_check(batch)
    elif mode=='remote-evaluate':b.remote_check(batch);value=b.bridge.evaluate(batch,json.load(sys.stdin))
    elif mode=='remote-seal':value=b.remote_seal(batch,json.load(sys.stdin))
    elif mode=='remote-finish':value=b.remote_finish(batch)
    else:raise ValueError('only_prepared_guarded_operations')
    verify_guard(expected)
    value['dependency_guard_sha256']=expected
    value['operative_guard_entry_sha256']=b.r.sha(Path(__file__))
    return value


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=('run','remote-status','remote-evaluate','remote-seal','remote-finish'))
    p.add_argument('--batch',type=Path,required=True);p.add_argument('--guard-sha',required=True);a=p.parse_args()
    try:
        value=execute(a.mode,a.batch,a.guard_sha);print(json.dumps(value,ensure_ascii=False),flush=True)
        raise SystemExit(value.get('pass') is False or value.get('phase')=='stopped')
    except Exception as e:
        print(json.dumps({'pass':False,'error':str(e) if type(e) is ValueError else type(e).__name__}),flush=True);raise SystemExit(1)
