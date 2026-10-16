#!/usr/bin/env python3
"""Verify iteration 60 device-loader fixtures without claiming Android runs."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from tools.android_bfp1_bridge.device_acceptance60 import prepare, BUILD, SOURCE, ROOT


def main():
    compiler=shutil.which('clang') or shutil.which('gcc')
    if not compiler:raise RuntimeError('C compiler required for test-only host loader smoke')
    record=prepare()
    assert record['generated_BF_DSO_fixtures']==9
    assert record['independent_simulator_comparisons']==9
    assert not record['device_execution']
    with tempfile.TemporaryDirectory(prefix='loader60-smoke-') as tmp:
        p=Path(tmp)
        loader=p/'loader'
        stub=p/'libstub.so'
        subprocess.run([compiler,'-Wall','-Wextra','-Werror','-std=c11',str(SOURCE),
                        '-ldl','-o',str(loader)],check=True,timeout=30)
        subprocess.run([compiler,'-shared','-fPIC','-Wall','-Wextra','-Werror','-std=c11',
                        str(ROOT/'tests/fixtures/bfp1_host_transport_stub.c'),
                        '-o',str(stub)],check=True,timeout=30)
        good=subprocess.run([str(loader),'host_stub',str(stub)],text=True,
                            capture_output=True,timeout=10,check=True)
        assert 'PASS host_stub' in good.stdout
        bad=subprocess.run([str(loader),'host_stub',str(p/'absent.so')],text=True,
                           capture_output=True,timeout=10)
        assert bad.returncode==65 and 'FAIL dlopen:' in bad.stderr
    for case, fields in record['cases'].items():
        name=BUILD/(case+'.so')
        assert hashlib.sha256(name.read_bytes()).hexdigest()==fields['so_sha256']
        assert name.read_bytes()[:4]==b'\x7fELF'
        elf=subprocess.run(['readelf','-Wl','-Ws','-d',str(name)],text=True,
                           capture_output=True,check=True,timeout=10).stdout
        assert 'bfc_call_v1' in elf and 'DYNAMIC' in elf
    record.update({'host_test_stub_dlopen_dlsym':'PASS',
                   'host_missing_library_error':'PASS',
                   'readelf_library_checks':9,
                   'device_probe_source':str(SOURCE.relative_to(ROOT)),
                   'android_loader_dlopen':False,
                   'jni_device_execution':False})
    evidence=ROOT/'evidence/iteration60_loader_readiness.json'
    evidence.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print('PASS 9 BF DSO fixtures, 9 simulator comparisons, 9 ELF inspections, host dlopen+error')

if __name__=='__main__':main()
