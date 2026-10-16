#!/usr/bin/env python3
"""Execute the iteration-61 ART assertion logic on Linux JVM with C TEST stubs.

This verifies JNI transport and the Java assertion harness, not Android loader
acceptance or Brainfuck-generated AArch64 execution. Both require a device.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
CASES=('empty','io_eof','transfer','nested','pointer_trap',
       'output_full','gas_trap','zero_skip','persistent')
SOURCE=ROOT/'tools/android_bfp1_bridge/org/brainfuckcc'


def execute():
    javac=shutil.which('javac'); java=shutil.which('java');clang=shutil.which('clang')
    if not (javac and java and clang):raise RuntimeError('host javac, java, clang required')
    jni=Path(javac).resolve().parents[1]/'include'
    if not (jni/'jni.h').exists():raise RuntimeError(f'missing JNI headers: {jni}')
    with tempfile.TemporaryDirectory(prefix='bfc61-jni-host-') as td:
        work=Path(td)
        subprocess.run([clang,'-std=c11','-fPIC','-shared','-Wall','-Wextra',
                        '-Werror','-I'+str(jni),'-I'+str(jni/'linux'),
                        str(ROOT/'tools/android_bfp1_bridge/bfp1_jni_bridge.c'),
                        '-ldl','-o',str(work/'libbrainfuckcc_bridge.so')],check=True,timeout=30)
        stub=ROOT/'tests/fixtures/bfp1_host_device_cases61.c'
        def make_stub(index,output):
            subprocess.run([clang,'-std=c11','-fPIC','-shared','-Wall','-Wextra',
                            '-Werror',f'-DCASE_ID={index}',str(stub),'-o',str(output)],
                            check=True,timeout=20)
        for index,case in enumerate(CASES):make_stub(index,work/(case+'.so'))
        classes=work/'classes'
        classes.mkdir()
        subprocess.run([javac,'-source','8','-target','8','-d',str(classes),
                        str(SOURCE/'Bfp1Bridge.java'),str(SOURCE/'Bfp1AndroidDeviceTest.java')],
                        check=True,timeout=30,capture_output=True,text=True)
        command=[java,'-cp',str(classes),'org.brainfuckcc.Bfp1AndroidDeviceTest',
                 str(work/'libbrainfuckcc_bridge.so'),str(work)]
        run=subprocess.run(command,capture_output=True,text=True,timeout=30)
        if run.returncode:raise AssertionError(f'host JNI harness failed\n{run.stdout}\n{run.stderr}')
        expected={f'PASS JNI {case}' for case in CASES}
        expected.add('PASS JNI transport_guards')
        expected.add('PASS JNI suite 9 policy fixtures')
        actual=set(run.stdout.splitlines())
        if actual!=expected:raise AssertionError(f'host JNI output mismatch: {actual ^ expected}')
        # Mutation test: a false policy result must fail the Java gate.
        make_stub(0,work/'nested.so')
        bad=subprocess.run(command,capture_output=True,text=True,timeout=30)
        if bad.returncode==0 or 'nested:' not in bad.stderr:
            raise AssertionError('corrupted fixture unexpectedly passed JNI assertions')
        return {'iteration':61,'host_jvm_art_test_assertion_parity':'PASS_TEST_ONLY_C_STUBS',
                'jni_fixture_calls_passed':len(CASES),'transport_guards_passed':True,
                'mutation_test_rejected_wrong_output':True,
                'android_art_executed':False,'BF_generated_AArch64_executed':False,
                'java_main_sha256':hashlib.sha256((SOURCE/'Bfp1AndroidDeviceTest.java').read_bytes()).hexdigest(),
                'stdout':run.stdout.strip().splitlines()}


def main():
    record=execute()
    file=ROOT/'evidence/iteration61_jni_host_acceptance.json'
    file.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print('PASS host JVM JNI: 9 C stubs, transport guards, mutated-policy rejection')

if __name__=='__main__':main()
