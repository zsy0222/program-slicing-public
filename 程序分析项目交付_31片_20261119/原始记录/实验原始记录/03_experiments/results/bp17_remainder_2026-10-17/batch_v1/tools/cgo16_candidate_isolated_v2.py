"""Whole-C candidate evaluator: fixed native recipe, isolated compiler/runtime.

No network transport or model client. Original data and oracle files are never
mounted in a candidate namespace. Bubblewrap alone is not a security proof;
the policy here is explicit and tested separately before any generation.
"""
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time
import ctypes
from common import fresh,save,sha,successful
from cgo16 import need,scope
from codeflaws_baseline import LIMITS,compare,observation_status
from prepare_cgo16 import safety

DENIED=('fork','vfork','clone','clone3','unshare','setns','mount','umount2','ptrace',
    'process_vm_readv','process_vm_writev','bpf','perf_event_open','open_by_handle_at',
    'kexec_load','init_module','finit_module','delete_module','reboot','io_uring_setup',
    'socket','socketpair','connect','accept','accept4','bind','listen','sendto','recvfrom')

def runtime_filter(path):
    lib=ctypes.CDLL('libseccomp.so.2')
    lib.seccomp_init.argtypes=[ctypes.c_uint32];lib.seccomp_init.restype=ctypes.c_void_p
    lib.seccomp_syscall_resolve_name.argtypes=[ctypes.c_char_p];lib.seccomp_syscall_resolve_name.restype=ctypes.c_int
    lib.seccomp_rule_add.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_int,ctypes.c_uint];lib.seccomp_rule_add.restype=ctypes.c_int
    lib.seccomp_export_bpf.argtypes=[ctypes.c_void_p,ctypes.c_int];lib.seccomp_export_bpf.restype=ctypes.c_int
    lib.seccomp_release.argtypes=[ctypes.c_void_p]
    ctx=lib.seccomp_init(0x7fff0000);need(bool(ctx),'seccomp_init_failed')
    try:
        for name in DENIED:
            number=lib.seccomp_syscall_resolve_name(name.encode())
            if number>=0:need(lib.seccomp_rule_add(ctx,0x00050001,number,0)==0,'seccomp_rule_failed:'+name)
        with Path(path).open('xb') as f:need(lib.seccomp_export_bpf(ctx,f.fileno())==0,'seccomp_export_failed')
    finally:lib.seccomp_release(ctx)
    return sha(Path(path))

def command(work,inner,exe=None,compiler=False):
    work=Path(work).resolve()
    cmd=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL',
         '--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64',
         '--dir','/dev','--ro-bind','/dev/null','/dev/null','--dir','/tmp','--bind',str(work),'/work',
         '--clearenv','--setenv','PATH','/usr/bin','--setenv','LC_ALL','C','--setenv','LANG','C']
    if compiler:cmd+=['--proc','/proc','--remount-ro','/proc','--setenv','TMPDIR','/work']
    else:
        need(exe is not None,'runtime_executable_required')
        cmd+=['--ro-bind',str(Path(exe).resolve()),'/program']
    return cmd+['--remount-ro','/','--chdir','/work','--',*inner]

def bounded(cmd,stdin,directory,compiler=False):
    directory=Path(directory);out=directory/'stdout.bin';err=directory/'stderr.bin'
    seconds=LIMITS['compile_seconds'] if compiler else LIMITS['test_seconds']
    memory=LIMITS['compiler_memory_mb'] if compiler else LIMITS['program_memory_mb']
    cap=16*1024**2 if compiler else LIMITS['output_bytes']
    def limit():
        resource.setrlimit(resource.RLIMIT_AS,(memory*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CORE,(0,0))
        if not compiler:resource.setrlimit(resource.RLIMIT_FSIZE,(cap,cap))
    start=time.monotonic();timeout=limited=resource_stop=False
    fd=None;filter_hash=None
    if not compiler:
        policy=directory.parent/(directory.name+'.runtime_filter.bpf');filter_hash=runtime_filter(policy)
        fd=os.open(policy,os.O_RDONLY);i=cmd.index('--');cmd=cmd[:i]+['--seccomp',str(fd)]+cmd[i:]
    with Path(stdin).open('rb') as inp,out.open('xb') as stdout,err.open('xb') as stderr:
        try:
            proc=subprocess.Popen(cmd,stdin=inp,stdout=stdout,stderr=stderr,cwd=directory,
                env={'PATH':'/usr/bin','LC_ALL':'C','LANG':'C'},start_new_session=True,preexec_fn=limit,
                pass_fds=() if fd is None else (fd,))
        finally:
            if fd is not None:os.close(fd)
        while proc.poll() is None:
            timeout=time.monotonic()-start>seconds;limited=out.stat().st_size+err.stat().st_size>=cap
            try:safety(directory)
            except ValueError:resource_stop=True
            if timeout or limited or resource_stop:
                os.killpg(proc.pid,signal.SIGKILL);break
            time.sleep(.01)
        proc.wait(timeout=5)
    limited|=out.stat().st_size+err.stat().st_size>=cap
    return {'command':cmd,'returncode':proc.returncode,'timeout':timeout,'output_limited':limited,
        'resource_stop':resource_stop,'seconds':round(time.monotonic()-start,4),'address_space_mb':memory,
        'runtime_seccomp_sha256':filter_hash,'denied_runtime_syscalls':list(DENIED) if not compiler else [],
        'time_limit_seconds':seconds,'output_limit_bytes':cap,'stdout_sha256':sha(out),'stderr_sha256':sha(err),
        'stdout_bytes':out.stat().st_size,'stderr_bytes':err.stat().st_size,'stdout_hex':out.read_bytes().hex()}

def compile_source(source,filename,recipe,output):
    output=Path(output);build=fresh(output/'build');(build/filename).write_bytes(source)
    ccdir=fresh(output/'compile');lddir=fresh(output/'link')
    empty=output/'empty_stdin';empty.write_bytes(b'')
    inner=['/usr/bin/gcc',*recipe['cflags'],'-c',filename,'-o','program.o']
    cc=bounded(command(build,inner,compiler=True),empty,ccdir,True)
    innerld=['/usr/bin/gcc','program.o','-o','program',*recipe['ldflags']]
    ld=bounded(command(build,innerld,compiler=True),empty,lddir,True) if cc['returncode']==0 and not cc['timeout'] and not cc['output_limited'] and not cc['resource_stop'] else None
    save(output/'compilation.json',{'compile':cc,'link':ld,'native_compile_inner':inner,'native_link_inner':innerld,
        'original_flags_preserved':True,'source_sha256':sha(build/filename),'bwrap_sha256':sha(Path('/usr/bin/bwrap'))})
    need(ld is not None and ld['returncode']==0 and not ld['timeout'] and not ld['output_limited'] and not ld['resource_stop'],'isolated_compilation_failed')
    return build/'program'

def evaluate(response,record,output):
    need(os.name=='posix','Linux_required');output=Path(output).resolve()
    protected=(Path('/home/vboxuser/cfb2'),Path('/home/vboxuser/codeflaws_exp_20260927/codeflaws'))
    need(all(not output.is_relative_to(x) for x in protected),'fresh_separate_evaluation_directory')
    output=fresh(output);safety(output)
    result={'schema':'CGO16-isolated-candidate-v2','model_calls':0,'candidate_tests':[],'status':'rejected',
        'whole_program_correctness_claimed':False,'native_tests_or_judge_changed':False}
    try:
        def pairs(items):
            need(len(items)==len(dict(items)),'duplicate_JSON_key');return dict(items)
        decoded=json.loads(response,object_pairs_hook=pairs)
        need(isinstance(decoded,dict) and set(decoded)=={'source'} and isinstance(decoded['source'],str),'strict_source_JSON')
        meta=record['metadata'];original=Path(meta['buggy']).read_text(encoding='utf-8')
        need(sha(Path(meta['buggy']))==meta['source_hashes']['buggy'],'original_source_changed')
        scope(decoded['source'],original)
        exe=compile_source(decoded['source'].encode(),Path(meta['buggy']).name,record['recipe'],output)
        for suite,items in meta['suites'].items():
            need(suite in ('repair','heldout') and items,'both_nonempty_original_suites')
            for t in items:
                safety(output)
                for n in ('input','expected'):need(sha(Path(t[n]))==t[n+'_sha256'],'original_test_changed')
                d=fresh(output/('test_'+suite+'_'+t['id']))
                ex=bounded(command(d,['/program'],exe),t['input'],d)
                need(not ex['resource_stop'],'resource_protection')
                comparison=compare(bytes.fromhex(ex['stdout_hex']),Path(t['expected']),d,record['recipe']['suites'][suite]['normalizer'])
                status=observation_status(ex,comparison)
                result['candidate_tests'].append({'suite':suite,'id':t['id'],'execute':ex,'comparison':comparison,'status':status,'pass':status=='pass'})
        need(len(result['candidate_tests'])==sum(len(v) for v in meta['suites'].values()),'exact_original_test_count')
        result['status']='all_tests_passed' if all(x['pass'] for x in result['candidate_tests']) else 'test_failed'
    except (ValueError,KeyError,TypeError,OSError,RuntimeError) as e:result['reason']=str(e)
    save(output/'evaluation.json',result);return result
