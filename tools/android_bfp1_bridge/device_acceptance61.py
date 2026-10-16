#!/usr/bin/env python3
"""Run Android shell ELF + ART/JNI acceptance on actual BF-generated AArch64 DSOs.

Preparation alone is structural/simulated evidence. An NDK, SDK build-tools
(d8), ADB and an authorized arm64 Android device are required for --device.
No C/JNI/Java source in this transport package compiles Brainfuck.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

from tools.android_bfp1_bridge.device_acceptance60 import (
    BUILD as FIXTURES, PROGRAMS, prepare, run_device as run_shell_probe,
    find_ndk_clang,
)

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'build/iteration61_android_jni'
JAVA = ROOT / 'tools/android_bfp1_bridge/org/brainfuckcc'
BRIDGE = ROOT / 'tools/android_bfp1_bridge/bfp1_jni_bridge.c'
REMOTE = '/data/local/tmp/bfc61_jni'
CASES = tuple(PROGRAMS.keys())


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def find_d8(sdk=None, explicit=None):
    if explicit:
        exe=Path(explicit)
        if not exe.is_file():raise RuntimeError(f'd8 not found: {exe}')
        return exe
    sdk=sdk or os.environ.get('ANDROID_SDK_ROOT') or os.environ.get('ANDROID_HOME')
    if not sdk:raise RuntimeError('Android SDK required: set --sdk or ANDROID_SDK_ROOT')
    options=list((Path(sdk)/'build-tools').glob('*/d8'))
    if not options:raise RuntimeError(f'No Android SDK build-tools d8 under {sdk}')
    def vkey(path):
        return tuple(int(x) for x in re.findall(r'\d+',path.parent.name))
    return max(options,key=vkey)


def build_art_harness(ndk, sdk, d8, api, javac=None):
    """Build host JNI glue (NDK) and executable ART test classes (javac+d8)."""
    BUILD.mkdir(parents=True,exist_ok=True)
    clang=find_ndk_clang(ndk,api)
    bridge=BUILD/'libbrainfuckcc_bridge.so'
    subprocess.run([str(clang),'-shared','-fPIC','-O2','-Wall','-Wextra',
                    '-Werror','-std=c11',str(BRIDGE),'-ldl','-o',str(bridge)],
                   check=True,timeout=90)
    javac=javac or shutil.which('javac')
    if not javac:raise RuntimeError('A host Java JDK with javac is required')
    cls=BUILD/'classes'
    cls.mkdir(exist_ok=True)
    subprocess.run([str(javac),'-source','8','-target','8','-d',str(cls),
                    str(JAVA/'Bfp1Bridge.java'),str(JAVA/'Bfp1AndroidDeviceTest.java')],
                   check=True,timeout=60)
    dex=BUILD/'dex'
    dex.mkdir(exist_ok=True)
    sdk=sdk or os.environ.get('ANDROID_SDK_ROOT') or os.environ.get('ANDROID_HOME')
    command=[str(find_d8(sdk,d8)),'--min-api',str(api),'--output',str(dex)]
    if sdk:
        jar=Path(sdk)/'platforms'/f'android-{api}'/'android.jar'
        if jar.is_file():command+=['--lib',str(jar)]
    command+=sorted(str(path) for path in cls.rglob('*.class'))
    subprocess.run(command,check=True,timeout=90)
    classes_dex=dex/'classes.dex'
    if not classes_dex.is_file():raise RuntimeError('d8 produced no classes.dex')
    jar=BUILD/'bfc61_jni_acceptance.jar'
    with zipfile.ZipFile(jar,'w',compression=zipfile.ZIP_STORED) as output:
        output.write(classes_dex,'classes.dex')
    return bridge,jar


def run_android_jni(adb, serial, bridge, jar):
    """Execute Android ART app_process, not desktop Java or a C policy stub."""
    cmd=[adb]+(['-s',serial] if serial else [])
    def adb_run(*args,timeout=120):
        return subprocess.run(cmd+list(args),capture_output=True,text=True,
                              timeout=timeout,check=True)
    adb_run('shell','mkdir -p '+REMOTE)
    artifacts={case:FIXTURES/(case+'.so') for case in CASES}
    artifacts.update({'bridge':bridge,'dex_jar':jar})
    remote_map={case:REMOTE+'/'+file.name for case,file in artifacts.items()}
    for name,path in artifacts.items():
        if not path.is_file():raise RuntimeError(f'missing artifact {path}')
        adb_run('push',str(path),remote_map[name])
        check=adb_run('shell','sha256sum '+remote_map[name]).stdout.split()
        if not check or check[0]!=digest(path):
            raise RuntimeError(f'Android SHA-256 mismatch for {name}')
    # Shell ART loads BF-produced AArch64 libraries through JNI dlopen/dlsym.
    # Paths are fixed, with no user-controlled shell metacharacters.
    script=(f'CLASSPATH={remote_map["dex_jar"]} '
            f'/system/bin/app_process /system/bin '
            f'org.brainfuckcc.Bfp1AndroidDeviceTest '
            f'{remote_map["bridge"]} {REMOTE}')
    call=adb_run('shell','-T',script,timeout=180)
    expected={f'PASS JNI {case}' for case in CASES}
    expected.add('PASS JNI transport_guards')
    expected.add('PASS JNI suite 9 policy fixtures')
    got=set(call.stdout.splitlines())
    if got!=expected:raise AssertionError(f'Android JNI stdout mismatch: {got ^ expected}')
    return {'jni_art_device_execution':True,'BF_generated_AArch64_policy_execution':True,
            'app_linker_namespace_verified':False,'apk_execution_verified':False,
            'passed_policy_cases':list(CASES),'stdout':call.stdout.strip().splitlines(),
            'artifact_sha256':{key:digest(file) for key,file in artifacts.items()}}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device',action='store_true',help='run on real Android via NDK SDK and ADB')
    parser.add_argument('--ndk');parser.add_argument('--sdk');parser.add_argument('--d8')
    parser.add_argument('--adb',default='adb');parser.add_argument('--serial')
    parser.add_argument('--api',type=int,default=28)
    args=parser.parse_args()
    baseline=prepare()
    print(f'PASS prepared {baseline["generated_BF_DSO_fixtures"]} BF-produced DSOs with simulator parity')
    if not args.device:
        print('Android shell/ART/JNI: NOT EXECUTED (pass --device with NDK, SDK, ADB)')
        return
    # This deliberately executes BOTH distinct device gates. An ART result
    # cannot silently substitute for the native loader test (or vice versa).
    shell=run_shell_probe(FIXTURES,args.adb,args.serial,args.ndk,args.api)
    bridge,jar=build_art_harness(args.ndk,args.sdk,args.d8,args.api)
    jni=run_android_jni(args.adb,args.serial or shell['device_serial'],bridge,jar)
    record={'iteration':61,'classification':'EXECUTED_ANDROID_SHELL_ART_JNI',
            'device_serial':shell['device_serial'],'device_sdk':shell['device_sdk'],
            'device_abi':shell['device_abi'],'shell_loader_cases':len(shell['cases']),
            'jni':jni,'apk_namespace_execution':False,
            'compiler_android_native_selfhost':False}
    BUILD.mkdir(parents=True,exist_ok=True)
    (BUILD/'device_result61.json').write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
    print(json.dumps(record,sort_keys=True,indent=2))

if __name__=='__main__':main()
