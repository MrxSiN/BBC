#!/usr/bin/env python3
"""x86_64 Linux real JVM JNI transport smoke; NOT Android BF device execution.

The test-only x86 fixture is NOT a Brainfuck interpreter, compiler or policy.
It validates that JNI dlopen/dlsym and byte/tape exchange are wired correctly.
"""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
def main():
    javac=shutil.which('javac');java=shutil.which('java');clang=shutil.which('clang')
    if not all((javac,java,clang)):raise RuntimeError('clang, java, javac are required')
    include=Path(javac).resolve().parents[1]/'include'
    if not (include/'jni.h').exists():raise RuntimeError(f'JNI headers unavailable: {include}')
    with tempfile.TemporaryDirectory(prefix='jni59-host-') as td:
        path=Path(td)
        subprocess.run([clang,'-shared','-fPIC','-std=c11','-Wall','-Wextra','-Werror',
                  '-I'+str(include),'-I'+str(include/'linux'),
                  str(ROOT/'tools/android_bfp1_bridge/bfp1_jni_bridge.c'),
                  '-ldl','-o',str(path/'libbrainfuckcc_bridge.so')],check=True)
        subprocess.run([clang,'-shared','-fPIC','-std=c11','-Wall','-Wextra','-Werror',
                  str(ROOT/'tests/fixtures/bfp1_host_transport_stub.c'),
                  '-o',str(path/'libbfp1_transport_stub.so')],check=True)
        sources=ROOT/'tools/android_bfp1_bridge/org/brainfuckcc'
        subprocess.run([javac,'-d',str(path),str(sources/'Bfp1Bridge.java'),
                        str(sources/'Bfp1BridgeSmoke.java')],check=True)
        run=subprocess.run([java,'-Djava.library.path='+str(path),'-cp',str(path),
                            'org.brainfuckcc.Bfp1BridgeSmoke',
                            str(path/'libbfp1_transport_stub.so')],check=True,
                           text=True,capture_output=True,timeout=30)
        assert 'PASS host JVM JNI bridge' in run.stdout
    evidence={'iteration':59,'host_platform':'Linux x86_64 JVM',
              'jni_transport_execution':'PASS_TEST_ONLY_NATIVE_STUB',
              'BF_AARCH64_ELF_EXECUTION':False,'android_loader_execution':False,
              'native_DSO_under_test':'C_TEST_ONLY_HOST_STUB_NOT_BF_COMPILER',
              'checks':['dlopen','dlsym','input/output arrays','tape reuse',
                        'output full status','invalid path','negative budget']}
    (ROOT/'evidence/iteration59_jni_host_smoke.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(run.stdout.strip())
if __name__=='__main__':main()
