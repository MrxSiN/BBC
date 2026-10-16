#!/usr/bin/env python3
"""Independent cross-linker acceptance of BF-produced ELF dynsym and hash.

Cross-linking is NOT Android dlopen or execution. It checks that an unrelated
AArch64 object can import the BF-created bfc_call_v1 symbol without repair.
"""
import json
from pathlib import Path
import subprocess
import tempfile
from bootstrap.android_dynamic_callable58 import ROOT

def main():
    policy=ROOT/'build/iteration59_dynamic/twitter_action.so'
    if not policy.exists():raise RuntimeError('run 59 policy compilation gate first')
    with tempfile.TemporaryDirectory(prefix='bf59-crosslink-') as temp:
        d=Path(temp)
        (d/'consumer.s').write_text('.text\n.globl invoke_bfp1\n'
                        '.type invoke_bfp1, %function\ninvoke_bfp1:\n'
                        ' bl bfc_call_v1\n ret\n')
        subprocess.run(['clang','-target','aarch64-linux-gnu','-c',
                        str(d/'consumer.s'),'-o',str(d/'consumer.o')],check=True)
        subprocess.run(['ld.lld','-m','aarch64elf','-shared','--no-undefined',
                        '-o',str(d/'consumer.so'),str(d/'consumer.o'),str(policy)],check=True)
        relocs=subprocess.run(['readelf','-Wr','-d',str(d/'consumer.so')],
                              check=True,text=True,capture_output=True).stdout
        assert 'bfc_call_v1' in relocs and 'NEEDED' in relocs
    record={'iteration':59,'classification':'CROSS_LINKER_STRUCTURAL_ONLY',
      'producer':'standard_BF_AArch64_dynamic_callable_DSO',
      'consumer':'independent_AArch64_assembler_and_lld',
      'external_compiler_role':'TEST_ONLY_ABI_LINKER_VERIFICATION',
      'aarch64_link_succeeded':True,'symbol_imported':'bfc_call_v1',
      'android_device_executed':False,'jni_device_executed':False}
    (ROOT/'evidence/iteration59_dso_crosslink.json').write_text(json.dumps(record,indent=2)+'\n')
    print('PASS independent AArch64 cross-linker imported BF DSO bfc_call_v1')
if __name__=='__main__':main()
