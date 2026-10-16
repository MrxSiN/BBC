#!/usr/bin/env python3
"""Rebuild the three locally preserved original policy BF sources in the new lane.

The other eight pinned original source files are not in this repository copy.
Outputs are structurally verified, not executed through JNI or on Android.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile

from bootstrap.android_dynamic_callable58 import compile_callable, ROOT

CASES={
 'gmail_row':'evidence/gm_native_20261014_v4/GM/brainfuck/src/row.bf',
 'gmail_scope':'evidence/gm_native_20261014_v4/GM/brainfuck/src/scope.bf',
 'twitter_action':'tests/fixtures/real_apps/twitter_action_filtered.bf',
}


def main():
    saved=json.loads((ROOT/'evidence/iteration58_original_policy_compiles.json').read_text())
    manifest=json.loads((ROOT/'status/ANDROID_APPLICATION_GATES.json').read_text())
    pinned={p['name']:p for app in manifest['mandatory_products'] for p in app['programs']}
    with tempfile.TemporaryDirectory(prefix='bf58-policies-') as folder:
        for name,filename in CASES.items():
            src=ROOT/filename
            digest=hashlib.sha256(src.read_bytes()).hexdigest()
            assert digest==saved[name]['source_sha256']
            pinned_name=name.split('_',1)[1]
            assert sum(byte in b'><+-.,[]' for byte in src.read_bytes())==pinned[pinned_name]['filtered_commands']
            destination=Path(folder)/(name+'.elf')
            info=compile_callable(src,destination)
            for key in ('source_bytes','source_sha256','elf_bytes','elf_sha256',
                        'bracket_pairs','maximum_nesting_depth','wide_relocation_patches'):
                assert info[key]==saved[name][key],(name,key,info[key],saved[name][key])
            subprocess.run(['readelf','-Wl',str(destination)],capture_output=True,check=True)
            print('PASS',name,'native ELF bytes',info['elf_bytes'],
                  'pairs',info['bracket_pairs'],flush=True)
    print('PASS all 3 locally archived policies; 8 original policy sources not provided')

if __name__=='__main__':main()
