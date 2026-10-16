#!/usr/bin/env python3
"""Independent assembler oracle for BF-emitted compact templates; never codegen."""
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bootstrap'))
from transport import encode_source, extract_artifact


def assembly(stream):
    pointer='0' if stream else '1'
    check='ldrb w9, [x1]\ncbz w9, normal' if stream else ''
    eof='eof' if stream else 'write'
    again='b read\neof:\nstrb wzr, [x1]' if stream else ''
    return f''' .text
.global start
start:
sub sp, sp, #16
stp xzr, xzr, [sp]
add x1, sp, #{pointer}
mov x2, #1
read:
mov x0, #0
mov x8, #63
svc #0
cmn x0, #4
b.eq read
cbz x0, {eof}
cmp x0, #1
b.ne read_fail
{check}
write:
mov x0, #1
mov x8, #64
svc #0
cmn x0, #4
b.eq write
cmp x0, #1
b.ne write_fail
{again}
normal:
mov x0, #0
exit:
mov x8, #93
svc #0
read_fail:
mov x0, #4
b exit
write_fail:
mov x0, #3
b exit
'''


def main():
    sdk=Path(os.environ['LOCALAPPDATA'])/'Android/Sdk/ndk'
    ndk=max((p for p in sdk.iterdir() if p.is_dir()),key=lambda p:tuple(int(x) for x in p.name.split('.')))
    clang=ndk/'toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
    objcopy=clang.with_name('llvm-objcopy.exe')
    records=[]
    with tempfile.TemporaryDirectory(prefix='bfc_compact_oracle_') as td:
        folder=Path(td)
        for stream in (False,True):
            asm=folder/'oracle.S';asm.write_text(assembly(stream))
            subprocess.run([str(clang),'--target=aarch64-linux-android26','-c',str(asm),'-o',str(folder/'oracle.o')],check=True,capture_output=True)
            subprocess.run([str(objcopy),'--dump-section','.text='+str(folder/'oracle.bin'),str(folder/'oracle.o')],check=True,capture_output=True)
            expected=(folder/'oracle.bin').read_bytes()
            for source in ([b',[.,]'] if stream else [b',[>+<-]>.',b',[->+<]>.']):
                core=subprocess.run([str(ROOT/'build/android_optimization/seed.exe'),str(ROOT/'compiler/android_core.bf'),'10000000000'],
                                    input=encode_source(source),capture_output=True,check=True,timeout=60)
                payload=source+b'\0'+extract_artifact(core.stdout)+b'\0'
                images=[]
                for seed in ('seed','seed_alt'):
                    result=subprocess.run([str(ROOT/f'build/android_optimization/{seed}.exe'),str(ROOT/'experiments/android_compact_optimize.bf'),'10000000000'],
                                          input=payload,capture_output=True,check=True,timeout=60)
                    image=extract_artifact(result.stdout)
                    assert image[128:]==expected
                    assert len(image)==(248 if stream else 232)
                    assert struct.unpack_from('<IIQQQQQQ',image,64)==(1,5,0,0,0,len(image),len(image),0x4000)
                    images.append(image)
                assert images[0]==images[1]
                records.append({'source_hex':source.hex(),'elf_bytes':len(images[0]),'elf_sha256':hashlib.sha256(images[0]).hexdigest()})
    report={'classification':'INDEPENDENT_LLVM_ASSEMBLER_TEST_ORACLE_ONLY','cases':records,
            'optimizer_source_sha256':hashlib.sha256((ROOT/'experiments/android_compact_optimize.bf').read_bytes()).hexdigest()}
    (ROOT/'evidence/android_compact_encoding_20261013.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: 3 BF patterns, 2 independent seeds each, exact independent assembler code bytes and load headers')


if __name__=='__main__':main()
