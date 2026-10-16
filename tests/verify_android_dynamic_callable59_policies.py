#!/usr/bin/env python3
"""Produce traceable BF-owned shared policy objects from three local real sources."""
import hashlib
import json
import subprocess
from pathlib import Path
from bootstrap.android_dynamic_callable59 import compile_shared
from bootstrap.android_dynamic_callable58 import ROOT
from tests.verify_android_dynamic_callable58_policies import CASES
from tests.verify_android_dynamic_callable59 import verify_elf


def main():
    previous=json.loads((ROOT/'evidence/iteration58_original_policy_compiles.json').read_text())
    out=ROOT/'build/iteration59_dynamic';out.mkdir(parents=True,exist_ok=True)
    evidence={'iteration':59,'classification':'BF_OWNED_ELF_DSO_STRUCTURAL_NOT_ANDROID_EXECUTED',
              'android_dlopen_verified':False,'original_policy_count':3,
              'remaining_original_source_count':8,'policies':{}}
    for name,filename in CASES.items():
        source=ROOT/filename
        checksum=hashlib.sha256(source.read_bytes()).hexdigest()
        assert checksum==previous[name]['source_sha256']
        target=out/(name+'.so')
        info=compile_shared(source,target)
        assert info['source_sha256']==checksum
        assert info['bracket_pairs']==previous[name]['bracket_pairs']
        verify_elf(target.read_bytes(),info['native_code_bytes'])
        listing=subprocess.run(['readelf','-Wl','-Ws','-d',str(target)],
                         text=True,capture_output=True,check=True).stdout
        assert 'bfc_call_v1' in listing and 'GLOBAL' in listing
        evidence['policies'][name]={'source_sha256':checksum,
          'filtered_commands':sum(x in b'><+-.,[]' for x in source.read_bytes()),
          'native_code_bytes':info['native_code_bytes'], 'dso_bytes':info['elf_bytes'],
          'dso_sha256':info['elf_sha256'], 'bracket_pairs':info['bracket_pairs'],
          'symbol':'bfc_call_v1','readelf_validated':True,
          'android_device_executed':False}
        print('PASS',name,info['elf_bytes'],'DSO bytes',flush=True)
    (ROOT/'evidence/iteration59_original_policy_dsos.json').write_text(
        json.dumps(evidence,indent=2,sort_keys=True)+'\n')
    print('PASS 3 local policy DSOs; Android JNI/dlopen and 8 other sources remain open')

if __name__=='__main__':main()
