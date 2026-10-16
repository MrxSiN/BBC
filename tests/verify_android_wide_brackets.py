#!/usr/bin/env python3
"""Differential test BF-owned wide bracket metadata and stack pairing.

Python is an independent oracle and transport only; no Python matching is
used by the opt-in Android compilation pipeline.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from source_check import check_source
sys.path.insert(0, str(ROOT/'bootstrap'))
from transport import encode_source, extract_artifact
from run_android_loops import compile_source

STAGES = {
    'wide_metadata': ('experiments/android_wide_bracket_metadata.bf', 'build/android_wide_bracket_metadata_x86_64_linux.elf'),
    'wide_pairs': ('experiments/android_wide_bracket_pairs.bf', 'build/android_wide_bracket_pairs_x86_64_linux.elf'),
}
ALPHABET=b'><+-.,[]'


def sha(blob): return hashlib.sha256(blob).hexdigest()


def execute(path, data, timeout=80):
    p = subprocess.run([str(ROOT/path)], input=data, capture_output=True, timeout=timeout)
    assert p.returncode == 0 and not p.stderr, (path, p.returncode, p.stderr[:256])
    return p.stdout


def oracle(source):
    depth=0
    metadata=bytearray()
    pairs=bytearray()
    stack=[]
    for pos,c in enumerate(source,1):
        if c not in ALPHABET:
            return None, None, 1
        if pos > 0xffffff:
            return None, None, 2
        if c==ord('['):
            if depth==255:
                return None,None,3
            depth+=1
            stack.append(pos)
            metadata.extend(bytes([c]) + pos.to_bytes(3,'little') + bytes([depth]))
        elif c==ord(']'):
            if not depth:
                return None,None,1
            metadata.extend(bytes([c]) + pos.to_bytes(3,'little') + bytes([depth]))
            opening=stack.pop()
            pairs.extend(b']'+opening.to_bytes(3,'little')+pos.to_bytes(3,'little'))
            depth-=1
    if depth:
        return None,None,1
    return bytes(metadata)+b'\x00\x00',bytes(pairs)+b'\x00\x00',0


def random_program(rng, cap):
    length = rng.randrange(cap+1)
    out=bytearray()
    stack=0
    for i in range(length):
        rem=length-i
        choices=list(b'><+-.,')
        if stack<min(30,rem-1): choices.append(ord('['))
        if stack: choices.append(ord(']'))
        c=rng.choice(choices)
        out.append(c)
        if c==ord('['):stack+=1
        elif c==ord(']'):stack-=1
    out.extend(b']'*stack)
    return bytes(out)


def main():
    begin=time.monotonic()
    stages={}
    for name,(src,elf) in STAGES.items():
        payload=(ROOT/src).read_bytes()
        commands=check_source(payload)
        compiled=extract_artifact(execute('build/compiler_x86_64_linux.elf',encode_source(payload),timeout=35))
        assert compiled[:4]==b'\x7fELF' and len(compiled)==215+len(commands)*32
        (ROOT/elf).write_bytes(compiled)
        (ROOT/elf).chmod(0o700)
        # Ignored comments never change a BF program's executable semantics.
        stripped=bytes(c for c in payload if c in ALPHABET)
        assert compiled==extract_artifact(execute('build/compiler_x86_64_linux.elf',encode_source(stripped),timeout=35))
        stages[name]={
            'bf_source':src,'native_linux_elf':elf,'source_sha256':sha(payload),
            'filtered_sha256':sha(commands),'brainfuck_instructions':len(commands),
            'linux_native_elf_sha256':sha(compiled),'linux_native_elf_bytes':len(compiled),
            'ignored_comment_invariance':True,
        }
    valid=[b'',b'+',b'[]',b'[[]]',b'[+][-]',b'['+b'+'*10+b']',
           b'['*255+b']'*255,b'+'*255+b'[]',
           b'+'*65535+b'[]',b'+'*65536+b'[+]',
           b'['+b'+'*299998+b']',b'+'*300001,
           b'+'*300000+b'[]', b'[]'*7000]
    invalid=[b'[',b']',b'][',b'[[]',b'[]]',b'['*256, b'['*255+b']'*254,
             b'A', b'+++?+', b'+'*300000+b'[']
    rng=random.Random(2026101328)
    for i in range(400):valid.append(random_program(rng,180))
    for i in range(120):
        candidate=bytes(rng.choice(ALPHABET) for _ in range(rng.randrange(1,100)))
        if oracle(candidate)[2]:invalid.append(candidate)
        else:valid.append(candidate)
    test_cases=[]
    for source in valid:
        m,p,status=oracle(source)
        assert status==0,(len(source),source[:200],status)
        observed=execute(STAGES['wide_metadata'][1],source)
        assert observed==m,(source[:50],observed[:80],m[:80])
        paired=execute(STAGES['wide_pairs'][1],observed)
        assert paired==p,(source[:50],paired[:80],p[:80])
        if len(source)>16000:
            test_cases.append({'commands':len(source),'brackets':(len(m)-2)//5,
                               'pairs':(len(p)-2)//7,
                               'metadata_sha256':sha(m),'pairs_sha256':sha(p)})
    for source in invalid:
        _,_,status=oracle(source)
        assert status!=0
        metadata=execute(STAGES['wide_metadata'][1],source)
        assert metadata[-1]==status,(source[:30],metadata[-12:],status)
        pairs=execute(STAGES['wide_pairs'][1],metadata)
        assert pairs[-1]!=0,('invalid source accepted by pairing',source[:20],pairs[-20:])
    # Counter overflow without emitting sixteen million characters.
    with tempfile.TemporaryDirectory(prefix='wide-bracket-overflow-') as folder:
        src=Path(folder)/'instrumented.bf'
        original=check_source((ROOT/STAGES['wide_metadata'][0]).read_bytes())
        init='>'*10 + '-'*3 + '<'*12  # indices 10 to 12 = FF; return to cell 0
        # Move to cell 10, set three bytes, and return to cell 0.
        init='>'*10 + '-' + '>' + '-' + '>' + '-' + '<'*12
        src.write_text(init+original.decode('ascii'))
        image=extract_artifact(execute('build/compiler_x86_64_linux.elf',encode_source(src.read_bytes()),timeout=35))
        binary=Path(folder)/'overflow.elf';binary.write_bytes(image);binary.chmod(0o700)
        output=subprocess.run([str(binary)],input=b'+',capture_output=True,timeout=15,check=True).stdout
        assert output==b'\x00\x02',output.hex()
    # Two independent standard BF seeds must agree with the Linux-native images.
    seed_cases=0
    with tempfile.TemporaryDirectory(prefix='wide-bracket-seeds-') as folder:
        for interpreter in ('seed_interpreter.c','seed_interpreter_alt.c'):
            exe=Path(folder)/interpreter
            subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/interpreter),'-o',str(exe)],check=True,capture_output=True)
            for source in (b'[]',b'[[]]',b'[+][-]',b'['+b'+'*256+b']'):
                records=execute(STAGES['wide_metadata'][1],source)
                for name,payload in (('wide_metadata',source),('wide_pairs',records)):
                    expected=execute(STAGES[name][1],payload)
                    out=subprocess.run([str(exe),str(ROOT/STAGES[name][0]),'30000000'],input=payload,
                                       capture_output=True,timeout=25,check=True)
                    assert out.stdout==expected,(name,interpreter)
                    seed_cases+=1
    # Opt-in wide metadata and pairing must not change the ten-slot emitter.
    parity=[]
    for source in (b'',b'+.',b'[]',b'[[]]',b'++[>+<-]>.',b'++[-].',b'[-][-]',b'+,.,'):
        baseline=compile_source(source,check_hashes=False,source_filter='scan')
        image=compile_source(source,check_hashes=False,source_filter='scan',wide_brackets=True)
        assert baseline==image
        parity.append(sha(image))
    for bad in (b'[',b']',b'+'*11,b'[]'*6):
        try:compile_source(bad,check_hashes=False,source_filter='scan',wide_brackets=True)
        except ValueError:pass
        else:raise AssertionError('rejected case produced an Android ELF')
    # Full CLI exercises real provenance, the scanner and atomic output
    # placement.  This is still the old ten-slot Android executable.
    with tempfile.TemporaryDirectory(prefix='wide-brackets-cli-') as folder:
        src=Path(folder)/'source.bf'; target=Path(folder)/'program.elf'
        target.write_bytes(b'original-artifact')
        cmd=[sys.executable,str(ROOT/'bootstrap/run_android_loops.py'),
             str(src),str(target),'--scanner','--wide-brackets']
        src.write_bytes(b'[[]')
        rejected=subprocess.run(cmd,capture_output=True,timeout=30)
        assert rejected.returncode and target.read_bytes()==b'original-artifact'
        src.write_bytes(b'++[>+<-]>.')
        accepted=subprocess.run(cmd,capture_output=True,timeout=30)
        assert accepted.returncode==0,(accepted.stderr[-400:],accepted.stdout[-400:])
        assert target.read_bytes()==compile_source(src.read_bytes(),wide_brackets=True,source_filter='scan')
    cli_atomic_preservation=True
    report={
        'date':'2026-10-13','iteration':28,
        'classification':'PARTIAL_EXECUTED_LINUX_BF_WIDE_BRACKET_PAIRING_NOT_ANDROID_RELOCATION',
        'stage_order':'scanner followed by wide metadata followed by wide pairs; old ten-slot emitter remains unchanged',
        'stages':stages,'valid_pairing_cases':len(valid),
        'invalid_cases_rejected':len(invalid),
        'large_source_fixtures':test_cases,
        'max_executed_source_commands':max(len(x) for x in valid),
        'tested_nesting_limit':255,
        'rejected_nesting_depth':256,
        'status_on_24bit_counter_overflow':2,
        'seed_equivalence_cases':seed_cases,
        'ten_slot_image_parity':len(parity),
        'cli_wide_brackets_atomic_preservation':cli_atomic_preservation,
        'ten_slot_image_hashes':parity,
        'wall_seconds':round(time.monotonic()-begin,3),
        'native_android_device_execution':'NOT_RERUN',
        'android_compiler_selfhosting':'UNIMPLEMENTED',
        'new_aarch64_relocations':'UNIMPLEMENTED',
        'limits':['BF pair stack reserves depth at most 255; max 24-bit source positions',
                  'both stages run as Linux-native BF executables',
                  'old ten-slot branch encoders and ELF output remain in use',
                  'metadata is not proof that compiler can emit large Android programs'],
    }
    (ROOT/'evidence/iteration28_wide_brackets.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',len(valid),'valid BF bracket pairing cases;',len(invalid),'invalid cases;',
          seed_cases,'independent seed cases;',len(parity),'unchanged Android images;',
          round(report['wall_seconds'],1),'seconds')

if __name__=='__main__':main()
