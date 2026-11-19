"""Collect and independently review completed saved records. No API/C calls.

Never restart the stopped transport; final status lives in a separate review.
"""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[3]/'results/bp17_caseblock100_2026-10-17'
# __file__ is prototypes/research_audit; results is two parents above it.
ROOT=Path(__file__).resolve().parents[2]/'results/bp17_caseblock100_2026-10-17'
BATCH=ROOT/'batch_v1';REVIEW=ROOT/'joint_review_20261017_v1'
SSH=['ssh','-i','C:/Users/chenm/.ssh/codex_ubuntu2204','-p','2222','-o','BatchMode=yes','-o','ConnectTimeout=10','vboxuser@127.0.0.1']
SCP=['scp','-i','C:/Users/chenm/.ssh/codex_ubuntu2204','-P','2222','-o','BatchMode=yes','-o','ConnectTimeout=10']
GUEST='/home/vboxuser/bp17_caseblock100_20261017_v1'
ARCHIVE=GUEST+'_archive_completion_v1'
CONTEXT='/home/vboxuser/bp17_caseblock100_audit_context_20261017_v1'


def run(args):
    print(json.dumps(dict(phase='read_or_collect',operation=args[0],time_utc=datetime.now(timezone.utc).isoformat())),flush=True)
    process=subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
    while True:
        try:out,err=process.communicate(timeout=25);break
        except subprocess.TimeoutExpired:print(json.dumps(dict(phase='awaiting_read_or_export',operation=args[0])),flush=True)
    if process.returncode:raise RuntimeError('read_collect_failed:'+str(process.returncode)+':'+err[-2000:])
    return out


def main():
    spec=importlib.util.spec_from_file_location('host_review',REVIEW/'review_tools/verify_bp17_caseblock100_host_20261017.py')
    a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
    a.need(not (REVIEW/'transfer').exists() and not (REVIEW/'completion.json').exists(),'fresh_joint_review')
    for _ in range(30):
        ready=run(SSH+[f'test -f {GUEST}/completion.json && echo ready || echo pending']).strip()
        if ready=='ready':break
        time.sleep(20)
    else:raise RuntimeError('archive_still_pending_no_restart')
    transfer=REVIEW/'transfer';transfer.mkdir()
    for remote,name in [(GUEST+'/completion.json','guest_completion.json'),(ARCHIVE+'/archive_identity.json','archive_identity.json'),
                        (ARCHIVE+'/payload_manifest.json','payload_manifest.json'),(ARCHIVE+'/intent.json','archive_recovery_intent.json'),
                        (ARCHIVE+'/records.tar.gz','records.tar.gz')]:
        a.need(not (transfer/name).exists(),'fresh_transfer')
        run(SCP+['vboxuser@127.0.0.1:'+remote,str(transfer/name)])
    identity=a.read(transfer/'archive_identity.json');complete=a.read(transfer/'guest_completion.json')
    a.need(complete['pass'] and complete['evaluated']==800 and complete['complete_cases']==100 and complete['archive']==identity,'guest_archive_completion_binding')
    a.need(a.sha(transfer/'records.tar.gz')==identity['sha256'] and (transfer/'records.tar.gz').stat().st_size==identity['bytes'],'whole_archive_SHA256_size')
    a.need(identity['model_calls']==identity['candidate_C_reexecutions']==0 and identity['saved_byte_audit_passed'],'archive_only_not_reexecution')
    print(json.dumps(dict(phase='exporting_private_readonly_audit_context',model_calls=0,C_executions=0)),flush=True)
    result=run(SSH+['env PYTHONDONTWRITEBYTECODE=1 python3 /home/vboxuser/bp17_caseblock100_review_tools_20261017_v1/export_bp17_caseblock_context_20261017_v2.py --output '+CONTEXT])
    a.save(transfer/'context_export_stdout.json',json.loads(result))
    for remote,name in [(CONTEXT+'/context.tar.gz','context.tar.gz'),(CONTEXT+'/manifest.json','context_manifest.json'),(CONTEXT+'/identity.json','context_identity.json')]:
        run(SCP+['vboxuser@127.0.0.1:'+remote,str(transfer/name)])
    ci=a.read(transfer/'context_identity.json')
    a.need(a.sha(transfer/'context.tar.gz')==ci['sha256'] and (transfer/'context.tar.gz').stat().st_size==ci['bytes'],'context_whole_SHA256_size')
    a.need(ci['model_calls']==ci['candidate_C_executions']==0,'context_only_not_execution')
    print(json.dumps(dict(phase='unpacking_and_hashing_all_archive_members',members=identity['payload_members'])),flush=True)
    members=a.unpack(transfer/'records.tar.gz',a.read(transfer/'payload_manifest.json'),REVIEW/'payload')
    a.need(members==identity['payload_members'],'archive_member_denominator')
    print(json.dumps(dict(phase='unpacking_context',members=ci['payload_members'])),flush=True)
    n=a.unpack(transfer/'context.tar.gz',a.read(transfer/'context_manifest.json'),REVIEW/'context')
    a.need(n==ci['payload_members'] and a.read(REVIEW/'context/completion.json')==complete,'context_completion_binding')
    print(json.dumps(dict(phase='independent_800_score_and_test_byte_recomputation')),flush=True)
    accepted=a.verify(BATCH,REVIEW/'payload',REVIEW/'context',REVIEW/'acceptance')
    value=dict(schema='BP17-100-case-joint-completion-after-archive-compatibility-recovery-v1',**{'pass':accepted['pass']},
        cases=100,responses=800,scores=800,confirmation=40,development=60,model_calls_added=0,candidate_C_reexecutions=0,
        original_transport_stop_preserved=str(BATCH/'stop.json'),archive=identity,context=ci,
        acceptance_sha256=a.sha(REVIEW/'acceptance/joint_acceptance.json'),completed_utc=datetime.now(timezone.utc).isoformat())
    a.save(REVIEW/'completion.json',value)
    print(json.dumps({k:accepted[k] for k in ('pass','audited_jobs','complete_cases','counts')}),flush=True)


if __name__=='__main__':main()
