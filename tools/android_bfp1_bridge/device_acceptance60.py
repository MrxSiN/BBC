#!/usr/bin/env python3
"""Prepare BF-generated Android DSO loader fixtures; optionally execute via ADB.

This is a test/deployment adapter only; production compiler logic stays BF.
No Android execution is claimed unless an actual device run succeeds.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'build/iteration60_android_loader'
SOURCE = ROOT / 'tools/android_bfp1_bridge/device_loader_probe60.c'
PROGRAMS = {
    'empty': b'',
    'io_eof': b',.,.,.',
    'transfer': b'+[->+<]>.',
    'nested': b'+++[>++[>+<-]<-]>>.',
    'pointer_trap': b'>>',
    'output_full': b'+.',
    'gas_trap': b'+[+]',
    'zero_skip': b'[+]',
    'persistent': b'+.',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(build=BUILD):
    from bootstrap.android_dynamic_callable59 import compile_shared
    from tests.verify_android_dynamic_callable58 import reference, emulate_callable
    build.mkdir(parents=True, exist_ok=True)
    cases = {}
    # The fixture program is checked by an independent reference and AArch64
    # instruction simulator before any on-device assertion is relied upon.
    for case, source in PROGRAMS.items():
        bf = build / (case + '.bf')
        dso = build / (case + '.so')
        bf.write_bytes(source)
        result = compile_shared(bf, dso)
        assert result['bracket_pairs'] == source.count(b'[')
        assert result['fixed_source_limit'] is None
        cases[case] = {'bf_sha256':sha(bf),'so_sha256':sha(dso),
                       'so_bytes':dso.stat().st_size,
                       'nested_depth':result['maximum_nesting_depth']}
    # Keep this separate from device evidence: it only compares emulation.
    reference_cases = [
        ('empty', b'\0\xff', 64, 16, 0),
        ('io_eof', b'\0\xff', 64, 16, 0),
        ('transfer', b'\0\xff', 64, 16, 3),
        ('nested', b'\0\xff', 64, 16, 10),
        ('pointer_trap', b'\0\xff', 2, 16, 0),
        ('output_full', b'\0\xff', 64, 0, 0),
        ('gas_trap', b'\0\xff', 64, 16, 2),
        ('zero_skip', b'\0\xff', 64, 16, 0),
        ('persistent', b'\0\xff', 64, 16, 0),
    ]
    for case, inp, cells, cap, gas in reference_cases:
        expected=reference(PROGRAMS[case],inp,cells,cap,gas)
        actual=emulate_callable((build/(case+'.so')).read_bytes(),inp,cells,cap,gas)
        assert (actual[0],actual[1],actual[3],actual[4])==expected,case
    record={'iteration':60,'classification':'STRUCTURAL_AND_SIMULATED_ONLY',
            'generated_BF_DSO_fixtures':len(cases),
            'independent_simulator_comparisons':len(reference_cases),
            'cases':cases,'device_execution':False,'android_loader_dlopen':False,
            'android_jni_execution':False,'android_native_selfhost':False,
            'note':'No device claims from this preparation phase'}
    (build/'manifest.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    return record


def find_ndk_clang(ndk, api):
    if not ndk:
        ndk = os.environ.get('ANDROID_NDK_HOME') or os.environ.get('ANDROID_NDK_ROOT')
    if not ndk:
        raise RuntimeError('Android NDK required for probe build; set ANDROID_NDK_HOME')
    bins = list(Path(ndk).glob('toolchains/llvm/prebuilt/*/bin'))
    if len(bins)!=1:raise RuntimeError('Expected one Android NDK LLVM prebuilt toolchain')
    tool=bins[0]/f'aarch64-linux-android{api}-clang'
    if not tool.is_file():raise RuntimeError(f'NDK compiler not found: {tool}')
    return tool


def run_device(build, adb, serial, ndk, api):
    clang=find_ndk_clang(ndk,api)
    probe=build/'device_loader_probe60'
    subprocess.run([str(clang),'-O2','-Wall','-Wextra','-Werror','-std=c11',
                    str(SOURCE),'-ldl','-o',str(probe)],check=True,timeout=90)
    cmd=[adb]+(['-s',serial] if serial else [])
    devices=subprocess.run([adb,'devices'],text=True,capture_output=True,check=True,timeout=20).stdout
    online=[x.split('\t')[0] for x in devices.splitlines()[1:] if x.endswith('\tdevice')]
    if not serial and len(online)!=1:raise RuntimeError('Specify --serial or attach exactly one authorized device')
    if serial and serial not in online:raise RuntimeError(f'device unavailable: {serial}')
    def adb_run(*args):
        return subprocess.run(cmd+list(args),capture_output=True,text=True,timeout=90,check=True)
    arch=adb_run('shell','getprop ro.product.cpu.abi').stdout.strip()
    sdk=adb_run('shell','getprop ro.build.version.sdk').stdout.strip()
    if arch!='arm64-v8a':raise RuntimeError(f'arm64-v8a required, found {arch}')
    if not sdk.isdecimal() or int(sdk)<api:raise RuntimeError(f'device SDK {sdk} below NDK target {api}')
    remote='/data/local/tmp/bfc60_callable'
    adb_run('shell','mkdir -p '+remote)
    # No shell interpolated paths from user input; all remote paths are fixed.
    adb_run('push',str(probe),remote+'/probe')
    adb_run('shell','chmod 700 '+remote+'/probe')
    results={}
    for case in PROGRAMS:
        artifact=build/(case+'.so')
        dest=remote+'/'+case+'.so'
        adb_run('push',str(artifact),dest)
        remote_sha=adb_run('shell','sha256sum '+dest).stdout.split()[0]
        if remote_sha != sha(artifact):raise RuntimeError(f'On-device payload hash mismatch: {case}')
        call=adb_run('shell','-T',remote+'/probe',case,dest)
        if 'PASS '+case not in call.stdout:raise AssertionError(f'Unexpected probe output {case}: {call.stdout}')
        results[case]={'passed':True,'stdout':call.stdout.strip(),
                       'so_sha256':sha(artifact)}
    record={'iteration':60,'device_execution':True,'android_loader_dlopen':True,
            'android_jni_execution':False,'android_native_selfhost':False,
            'device_abi':arch,'device_sdk':int(sdk),'device_serial':serial or online[0],
            'probe_sha256':sha(probe),'cases':results,
            'evidence_class':'EXECUTED_ANDROID_SHELL_LOADER_NOT_JNI_OR_APK'}
    (build/'device_result.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    return record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device',action='store_true',help='also build NDK loader probe and run on actual Android arm64')
    parser.add_argument('--adb',default='adb');parser.add_argument('--serial')
    parser.add_argument('--ndk');parser.add_argument('--api',type=int,default=28)
    args=parser.parse_args()
    structural=prepare()
    print(f"Prepared {structural['generated_BF_DSO_fixtures']} BF DSOs; simulator parity passed")
    if args.device:
        device=run_device(BUILD,args.adb,args.serial,args.ndk,args.api)
        print(json.dumps(device,indent=2))
    else:
        print('Android loader/JNI: NOT EXECUTED (run with --device and Android NDK + ADB)')

if __name__=='__main__':main()
