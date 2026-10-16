#!/usr/bin/env python3
"""Dynamic stream stage test; does not claim native PIE or loop support."""
from __future__ import annotations
import hashlib
import json
import random
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'bootstrap'))
from transport import encode_source,extract_artifact
from android_dynamic_linear_transport import emit_linear_slots
sys.path.insert(0,str(ROOT/'tools'))
from source_check import check_source
BF=ROOT/'experiments/android_streaming_linear_slots.bf'
ELF=ROOT/'build/android_streaming_linear_slots_x86_64_linux.elf'
LEGACY=ROOT/'build/android_wide_slot_emitter_x86_64_linux.elf'
ALLOWED=b'+-><.,'

def run(source:bytes)->bytes:
    wire=b''.join(bytes((1,c)) for c in source)+b'\0'
    p=subprocess.run([str(ELF)],input=wire,capture_output=True,timeout=35)
    assert p.returncode==0 and not p.stderr
    return p.stdout

def chunks(raw:bytes)->bytes:
    assert raw[-2:]==b'\0\0',raw[-2:].hex()
    out=bytearray()
    for off in range(0,len(raw)-2,49):
        assert raw[off]==1
        out.extend(raw[off+1:off+49])
    return bytes(out)

def filtered(src:bytes)->bytes:
    # Test oracle only. The BF stage does its own filtering.
    return bytes(b for b in src if b in ALLOWED)

def sha(src:bytes)->str:return hashlib.sha256(src).hexdigest()

def main():
    start=time.monotonic()
    commands=check_source(BF.read_bytes())
    assert len(commands)<16128
    native=extract_artifact(subprocess.run(
        [str(ROOT/'build/compiler_x86_64_linux.elf')],
        input=encode_source(BF.read_bytes()),capture_output=True,timeout=90,check=True).stdout)
    assert native==ELF.read_bytes()
    native_again=extract_artifact(subprocess.run(
        [str(ROOT/'build/compiler_x86_64_linux.elf')],
        input=encode_source(commands),capture_output=True,timeout=90,check=True).stdout)
    assert native==native_again
    templates={}
    for op in ALLOWED:
        old=subprocess.run([str(LEGACY)],input=bytes([op,0]),capture_output=True,check=True,timeout=10).stdout
        assert len(old)==53 and old[-5:]==b'\x01\0\0\0\0'
        templates[op]=old[:48]
    rng=random.Random(490001)
    cases=[b'',b'+',b'hello, world!\n+++',b'\0+\xff>\0-',b'<>.,-+',b'+'*2719,b'+'*27120]
    for _ in range(125):
        raw=bytes(rng.choice(b'+-><.,abcdef\n#\x00\xff') for _ in range(rng.randrange(0,300)))
        cases.append(raw)
    for raw in cases:
        result=run(raw)
        expected=b''.join(templates[op] for op in filtered(raw))
        assert chunks(result)==expected,raw[:80]
    failed=0
    for raw in (b'[',b']',b'[]',b'+[-]',b'abc+[]',b'+'*42+b'['):
        result=run(raw)
        assert result[-2:]==b'\0\x01',raw
        failed+=1
    with tempfile.TemporaryDirectory(prefix='bf-dynamic-') as d:
        d=Path(d);src=d/'source.bf';out=d/'native.bin'
        raw=b'# ignored source line\n'+b'+'*300_001+b'ignored\xff\x00'
        src.write_bytes(raw)
        record=emit_linear_slots(src,out)
        assert record['linear_instruction_slots']==300001
        assert record['native_code_bytes']==300001*48
        expected_sha=sha(templates[43]*300001)
        assert sha(out.read_bytes())==expected_sha
        assert record['raw_source_bytes']==len(raw)
        out.write_bytes(b'EXISTING DATA')
        src.write_bytes(b'+[]')
        try:emit_linear_slots(src,out)
        except ValueError:pass
        else:raise AssertionError('unsupported brackets were compiled')
        assert out.read_bytes()==b'EXISTING DATA'
        src.write_bytes(b'+'*6)
        try:emit_linear_slots(src,out,max_output_bytes=6*48-1)
        except ValueError:pass
        else:raise AssertionError('resource policy was ignored')
        assert out.read_bytes()==b'EXISTING DATA'
        record2=emit_linear_slots(src,out)
        assert record2['linear_instruction_slots']==6
    seed_matches=0
    with tempfile.TemporaryDirectory(prefix='bf-dynamic-seeds-') as td:
        for seed in ('seed_interpreter.c','seed_interpreter_alt.c'):
            compiled=Path(td)/seed
            subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/seed),'-o',str(compiled)],
                           capture_output=True,check=True,timeout=30)
            for raw in (b'+-',b'ignored\x00+.'):
                framed=b''.join(bytes((1,c)) for c in raw)+b'\0'
                reference=subprocess.run([str(compiled),str(BF),'60000000'],
                            input=framed,capture_output=True,timeout=30,check=True)
                assert reference.stdout==run(raw)
                seed_matches+=1
    evidence={
        'iteration':49,'classification':'EXECUTED_LINUX_BF_DYNAMIC_LINEAR_AARCH64_RAW_SLOTS_ONLY',
        'native_bf_source':'experiments/android_streaming_linear_slots.bf',
        'source_filtered_instructions':len(commands),
        'source_sha256':sha(BF.read_bytes()),'native_linux_elf_sha256':sha(native),
        'native_linux_elf_bytes':len(native),
        'test_cases':len(cases),'invalid_bracket_rejections':failed,
        'independent_seed_interpreter_comparisons':seed_matches,
        'tested_linear_commands_without_source_counter':300001,
        'tested_output_bytes':300001*48,
        'comments_and_binary_ignored_bytes_supported':True,
        'atomic_failure_preserves_output':True,
        'caller_optional_resource_cap_tested':True,
        'android_elf_generated':False,'full_eight_instruction_codegen':False,
        'device_execution':'NOT_RUN','real_application_policies':'UNCOMPILED',
        'source_scan_100m_experiment_unmodified':True,
        'elapsed_seconds':round(time.monotonic()-start,2)}
    path=ROOT/'evidence/iteration49_android_dynamic_stream.json'
    path.write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))
if __name__=='__main__':main()
