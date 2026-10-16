#!/usr/bin/env python3
"""Verify pinned Android BF application source workloads, never claim compilation."""
import argparse, hashlib, json, sys, copy, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
VALID=set(b'><+-.,[]')
def git_blob_id(data):
    return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def filtered_stats(data):
    n=depth=peak=0
    for c in data:
        if c not in VALID:continue
        n+=1
        if c==ord('['):
            depth+=1;peak=max(peak,depth)
        elif c==ord(']'):
            depth-=1
            if depth<0:raise ValueError('unbalanced closing bracket')
    if depth:raise ValueError('unbalanced opening bracket')
    return n,peak

def verify(workloads,checkouts=None):
    assert workloads['classification'].startswith('SOURCE_AUDIT_VERIFIED')
    assert workloads['observed_backend_capacity_commands']==2719
    assert workloads['separately_recorded_android_native_compiler_input_capacity']==16128
    assert workloads['observed_compilation_result'].startswith('UNIMPLEMENTED')
    assert len(workloads['mandatory_products'])==3
    appcounts={}
    total=0;peak=0;filecount=0
    for app in workloads['mandatory_products']:
        name=app['repo'].split('/')[-1]
        assert name not in appcounts
        assert app['backend_result'].startswith('UNIMPLEMENTED')
        assert app['host_abi_parity']=='UNVERIFIED'
        ptotal=0
        for p in app['programs']:
            assert p['filtered_commands']>workloads['observed_backend_capacity_commands']
            assert p['filtered_commands']>workloads['separately_recorded_android_native_compiler_input_capacity']
            assert p['tape_cells']>0 and 0<=p['persistent_cells']<=p['tape_cells']
            assert len(p['git_blob_sha1'])==40
            ptotal+=p['filtered_commands'];total+=p['filtered_commands']
            peak=max(peak,p['filtered_commands']);filecount+=1
            if checkouts:
                f=checkouts/name/p['path']
                data=f.read_bytes()
                assert len(data)==p['raw_bytes'],f
                assert git_blob_id(data)==p['git_blob_sha1'],f
                assert filtered_stats(data)==(p['filtered_commands'],p['max_loop_depth']),f
        if checkouts:
            gitdir=checkouts/name/'.git'
            if gitdir.exists():
                head=subprocess.check_output(['git','-C',str(checkouts/name),'rev-parse','HEAD'],text=True).strip()
                assert head==app['pinned_commit'], (name,'checkout HEAD not pinned',head)
            conf=json.loads((checkouts/name/'brainfuck/programs.json').read_text())
            spec={x['name']:(x['tape'],x.get('persist',0)) for x in conf['programs']}
            for p in app['programs']:
                assert spec[p['name']]==(p['tape_cells'],p['persistent_cells'])
        assert ptotal==app['total_filtered_commands']
        assert len(app['programs'])==app['program_count']
        appcounts[name]=ptotal
    assert filecount==11
    assert total==1312912==workloads['observed_total_filtered_commands']
    assert peak==296307==workloads['observed_largest_program_commands']
    assert workloads['larger_application_capacity_goal']['per_compilation_unit_commands']>=100000000
    assert workloads['larger_application_capacity_goal']['total_project_commands']>=100000000
    return dict(programs=filecount,command_total=total,largest=peak,by_repository=appcounts,
                verified='PINNED_LOCAL_SOURCE_BYTES' if checkouts else 'METADATA_ONLY',
                compiler_execution='NOT_RUN',apk_execution='NOT_RUN')
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--checkouts',type=Path)
    ap.add_argument('--json',action='store_true')
    args=ap.parse_args()
    data=json.loads((ROOT/'status/ANDROID_APPLICATION_GATES.json').read_text())
    result=verify(data,args.checkouts)
    # The metadata contract must fail closed if any program count is silently altered.
    altered=copy.deepcopy(data)
    altered['mandatory_products'][0]['programs'][0]['filtered_commands']+=1
    try: verify(altered)
    except AssertionError: pass
    else: raise AssertionError('source count mutation escaped validation')
    print(json.dumps(result,sort_keys=True,indent=2) if args.json else f"PASS metadata: {result['programs']} sources, {result['command_total']:,} commands, largest {result['largest']:,}; execution NOT RUN")
if __name__=='__main__':main()
