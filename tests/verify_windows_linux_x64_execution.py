#!/usr/bin/env python3
"""Execute real BF-generated Windows x64 code on Linux with test-only API shims.

This is x64 CPU execution, NOT the Windows PE loader or Win32 API. It cannot
qualify the target-native Windows gate. Production compilation remains BF-only.
"""
from pathlib import Path
import hashlib
import json
import random
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tests')]
from run_windows_full64 import compile_source
from reference import execute

HARNESS_SOURCE=ROOT/'tests/windows_pe_linux_x64_shim.c'
HARNESS=ROOT/'build/windows_pe_linux_x64_shim'

def native(image:Path, payload:bytes, timeout=3):
    p=subprocess.run([str(HARNESS),str(image)],input=payload,capture_output=True,timeout=timeout)
    return p.returncode,p.stdout,p.stderr

def corpus():
    fixed=[
        b'',b'.',b'+.',b'-.',b'+++++.',b'-.+.',b',.',b',,.',
        b',>,.<.',b',[-].',b',+.',b'+,.-.',b'++[->+<]>.',
        b'+++[->+<]>.',b'+++[>+<-]>.',b'++[>++[>+<-]<-]>>.',
        b'++++[->+++<]>.',b'++++[-].',b'++++[+].',b'[+].',
        b'[[-]]',b'++[[-]]',b'++[>+<-]>.',b'[-]',b'[+]',
        b'[]',b'[[]]',b'['+b'+'*62+b']',b'+'*64,
        b'.'*64,b',.'*32,b'[+]'*21,b'[]'*32,
        b'<' ,b'+[<]',b'>'*63+b'<',b'>'*64,
        b'>'*31+b'.'+b'<'*31+b'.',
        b'+'*63+b'.',b'>+<.',b',[-].',b'++[->+<]>[-].',
        b'\0ignored \xff\x01 bf\x02'.replace(b'bf',b'xy')+b'+.'
    ]
    cases=[(x,b'') for x in fixed]
    cases += [(b',.',b'\0'),(b',.',b'\xff'),(b',.',b'\0\xff'),
              (b',.,.',b'\xff'),(b',.,.',b'\0\xff'),
              (b',>,.<.',b'\x00\xff'),(b',>,.<.',b'\xff\x00'),
              (b',[.-]',b'\x03'),(b',[.-]',b'\0'),
              (b',[.-]',b'\xff'),(b',[-].',b'\xff')]
    rng=random.Random(420042)
    fragments=(b'+',b'-',b'.',b',',b'[-]',b'[+]',b'[->+<]',b'[->++<]',b'>',b'<')
    for _ in range(110):
        source=b''; ptr=0
        while len(source)<64:
            candidates=[v for v in fragments if len(source)+len(v)<=64 and
                        not (v.startswith(b'<') and ptr==0) and
                        not (v.startswith(b'>') and ptr>=4) and
                        not (v.startswith(b'[') and v in (b'[->+<]',b'[->++<]') and ptr>=4)]
            if not candidates: break
            choice=rng.choice(candidates)
            if rng.random()<0.20:break
            source+=choice
            if choice==b'>':ptr+=1
            if choice==b'<':ptr-=1
        stdin=bytes(rng.randrange(256) for _ in range(rng.randrange(0,5)))
        cases.append((source,stdin))
    return cases

def main():
    compile_command=['gcc','-O2','-std=c11','-Wall','-Wextra','-Werror',
        '-fno-omit-frame-pointer','-o',str(HARNESS),str(HARNESS_SOURCE)]
    subprocess.run(compile_command,check=True,capture_output=True)
    counts={'success':0,'expected_traps':0,'source_cases':0,'output_bytes':0,'max_commands':0,
            'binary_inputs':0,'malformed_rejections':0,'archived_windows41_smoke':0}
    started=time.monotonic()
    # Execute the exact previous iteration's 11 archived target-side fixtures
    # under the test shim. This does not change their Windows-native status.
    fixture_dir=ROOT/'build/windows41_acceptance'
    manifest=json.loads((fixture_dir/'manifest.json').read_text())
    for fixture in manifest['programs']:
        image=fixture_dir/fixture['executable']
        assert hashlib.sha256(image.read_bytes()).hexdigest()==fixture['sha256']
        rc,out,err=native(image,bytes.fromhex(fixture['stdin_hex']))
        expectation=fixture['expected_exit']
        assert rc==(0 if expectation=='zero' else 99),(fixture['name'],rc,err)
        assert out==bytes.fromhex(fixture['expected_stdout_hex']),fixture['name']
        counts['archived_windows41_smoke']+=1
    with tempfile.TemporaryDirectory() as temp:
        dst=Path(temp)/'program.exe'
        for n,(source,inp) in enumerate(corpus()):
            # Reference is a development-only Brainfuck interpreter, not a compiler.
            try:
                expected,_steps=execute(source,stdin=inp,max_steps=200_000)
                trap=False
            except IndexError:
                expected=b'';trap=True
            except TimeoutError:
                # Nontermination is not evidence of code-generation equivalence.
                continue
            image=compile_source(source)
            assert len(image)==2048
            dst.write_bytes(image)
            status,out,stderr=native(dst,inp)
            if trap:
                assert status==99,('trap',n,source,status,out,stderr)
                counts['expected_traps']+=1
            else:
                assert status==0,('exit',n,source,status,stderr)
                assert out==expected,('output',n,source,inp,out,expected)
                counts['success']+=1
                counts['output_bytes']+=len(out)
            counts['source_cases']+=1
            counts['max_commands']=max(counts['max_commands'],len(bytes(c for c in source if c in b'<>+-.,[]')))
            counts['binary_inputs']+=bool(inp)
        # Offline loader negative testing must fail closed, not execute corrupt PE bytes.
        source=compile_source(b'+++[->+<]>.')
        for corrupt in (source[:0x80]+b'X'+source[0x81:], source[:-1],b'INVALID',source+b'EXTRA'):
            dst.write_bytes(corrupt)
            status,out,stderr=native(dst,b'')
            assert status==98 and not out,(status,out,stderr)
            counts['malformed_rejections']+=1
        # A former failed compilation must not delete the previous destination.
        preserved=compile_source(b'++[->+<]>.')
        for bad in (b'[',b']',b'+'*65,b'[+'*64+b']'*64):
            dst.write_bytes(preserved)
            try:compile_source(bad)
            except ValueError:pass
            else:raise AssertionError('malformed program accepted')
            assert dst.read_bytes()==preserved
    counts.update({
        'iteration':42,'cpu_arch':'x86_64','execution_host':'Linux x86-64 native CPU + test-only Win32 API shim',
        'windows_loader':'NOT_RUN','windows_native_S2':'UNIMPLEMENTED',
        'production_BF_modules_modified':False,
        'harness_source_sha256':hashlib.sha256(HARNESS_SOURCE.read_bytes()).hexdigest(),
        'harness_binary_sha256':hashlib.sha256(HARNESS.read_bytes()).hexdigest(),
        'harness_runtime_sec':round(time.monotonic()-started,3),
    })
    path=ROOT/'evidence/iteration42_windows_x64_cpu_shim.json'
    path.write_text(json.dumps(counts,indent=2)+'\n')
    print(json.dumps(counts,indent=2))

if __name__=='__main__':main()
