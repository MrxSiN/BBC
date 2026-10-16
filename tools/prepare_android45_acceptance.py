#!/usr/bin/env python3
"""Prepare only; never claim Android device execution without adb evidence."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tools')]
from run_android_extended import compile_source
from android_device_acceptance import digest, expected_behavior, inspect_elf

CASES=(
 ('page_2378',b'+'*(2378-4)+b'[-].',b''),
 ('page_2379',b'+'*(2379-4)+b'[-].',b''),
 ('nested_2400',b'+'*(2400-21)+b'[-]++[>++[>+<-]<-]>>.',b''),
 ('loop_2719',b'+'*(2719-4)+b'[-].',b''),
 ('binary_2719',b'+'*(2719-4)+b',.,.',bytes((0,255))),
 ('eof_2719',b'+'*(2719-2)+b',.',b''),
 ('trap_2719',b'<'+b'+'*2718,b''),
)

def prepare(dest):
    if dest.exists() and any(dest.iterdir()):
        raise ValueError('destination must be absent or empty')
    dest.mkdir(parents=True, exist_ok=True)
    items=[]
    for name,src,stdin in CASES:
        assert len(src)<=2719
        output,status=expected_behavior(src,stdin)
        image=compile_source(src,allow_loops=b'[' in src,multiclass=True,tape_relocated=True)
        elf=inspect_elf(image,len(src))
        (dest/(name+'.elf')).write_bytes(image)
        (dest/(name+'.stdin')).write_bytes(stdin)
        items.append({'id':name,'command_count':len(src),'elf_sha256':digest(image),
            'source_sha256':digest(src),'stdin_sha256':digest(stdin),
            'expected_stdout_hex':output.hex(),'expected_exit_code':status,**elf})
    manifest={'schema':1,'iteration':45,'target':'android-aarch64-shell',
              'evidence_class':'PREPARED_NOT_EXECUTED',
              'device_execution_claim':False,'production_codegen':'standard Brainfuck Linux-native stages',
              'cases':items}
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    lines=['#!/system/bin/sh','set -u','cd "$(dirname "$0")" || exit 90',
        'mkdir -p results || exit 91']
    for item in items:
        n=item['id']
        lines += [f'chmod 700 ./{n}.elf',
              f'./{n}.elf < ./{n}.stdin > ./results/{n}.stdout 2> ./results/{n}.stderr',
              f'printf "%s\\n" "$?" > ./results/{n}.exitcode']
    lines.append('printf "TESTS_FINISHED\\n"')
    p=dest/'run.sh';p.write_text('\n'.join(lines)+'\n');p.chmod(0o755)
    return manifest

if __name__=='__main__':
    dst=Path(sys.argv[1]) if len(sys.argv)==2 else ROOT/'build/android45_acceptance'
    result=prepare(dst)
    print(f"Prepared {len(result['cases'])} Android images, device execution NOT RUN")
