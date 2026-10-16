#!/usr/bin/env python3
"""Verify the BF-owned 255-slot loop patcher against independent oracles.

Only transport and tests use Python; BF code generation/relocation is native BF.
"""
from __future__ import annotations
import hashlib
import json
import random
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'bootstrap'), str(ROOT / 'tests'), str(ROOT / 'tools')]
from transport import encode_source, extract_artifact
from source_check import check_source
from run_android_extended import (compile_source, bf_native, WIDE_255_SOURCE,
        WIDE_255_NATIVE, WIDE_255_EVIDENCE, SLOT_NATIVE, check_provenance)
from run_android_loops import run_stage
from verify_android_aarch64_subset import emulate
from reference import execute


def sha(b):
    return hashlib.sha256(b).hexdigest()


def loop_pairs(program):
    stack = []
    found = []
    for n, command in enumerate(program, 1):
        if command == ord('['):
            stack.append(n)
        elif command == ord(']'):
            assert stack
            found.append((stack.pop(), n))
    assert not stack
    return found


def verify_branch_words(program, image):
    for left, right in loop_pairs(program):
        span = right-left
        words = ((left, 0x14000000 | ((12*span+10) & 0x3ffffff)),
                 (right, 0x14000000 | ((10-12*span) & 0x3ffffff)))
        for position, value in words:
            offset = 0x210+48*(position-1)
            assert image[offset+8:offset+12] == struct.pack('<I', value), (len(program), position)
    return len(loop_pairs(program))


def main():
    start = time.monotonic()
    source = WIDE_255_SOURCE.read_bytes()
    filtered = check_source(source)
    assert len(filtered) <= 16128 and len(filtered) > 2389
    original = WIDE_255_NATIVE.read_bytes()
    compiler = ROOT / 'build/compiler_x86_64_linux.elf'
    for candidate in (source, filtered):
        result = subprocess.run([str(compiler)], input=encode_source(candidate),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, timeout=80)
        assert extract_artifact(result.stdout) == original
    check_provenance(allow_loops=True, page_class=True)
    cases = [b'', b'[]', b'+'*74+b'[-]>.', b'+'*100+b'[->+<]>.',
             b'+'*248+b'[-].', b'+'*250+b'[-][]', b'+'*251+b'[-].',
             b'+'*249+b'[>+<-]', b'[]'*127+b'.', b'['*127+b']'*127,
             b'+'*240+b'[-]'+b'[]'*6, b'+[-]'*50, b'+[>+<-]'*35,
             b'+'*100+b'[>+<-]'*20+b'.', b'+'*112+b'[>+<-]',
             b'<' + b'+'*80 + b'[-]', b','*90+b'[->+<]>.',
             b'+'*255, b'+'*74, b'+'*512]
    rng = random.Random(2026101332)
    segments = (b'+[-]', b'[-]', b'[-][]', b'+++', b'[-][-]',
                b'+[>+<-]', b'++[->+<]', b'+-.', b'[-][[]]', b'>+<')
    for _ in range(48):
        buf = bytearray()
        while len(buf) < rng.randint(70, 255):
            item = rng.choice(segments)
            if len(buf)+len(item) > 255:
                break
            buf.extend(item)
        cases.append(bytes(buf))
    verified = 0; checked_pairs = 0; simulations = 0; parity = 0; traps = 0
    for program in cases:
        if len(program) > 255 and b'[' in program:
            continue
        image = compile_source(program, allow_loops=(b'[' in program), page_class=True)
        if b'[' in program:
            checked_pairs += verify_branch_words(program, image)
        else:
            assert image == compile_source(program, page_class=True)
            parity += 1
        if len(program) <= 74:
            old = compile_source(program, allow_loops=(b'[' in program))
            new = compile_source(program, allow_loops=(b'[' in program), page_class=True)
            # Different ELF layouts, same emitted 48-byte slots.
            assert old[0x210:0x210+48*len(program)] == new[0x210:0x210+48*len(program)]
        input_bytes = bytes((n*39+15) % 256 for n in range(512))
        try:
            expected, _ = execute(program, input_bytes, max_steps=60000)
            trap = False
        except IndexError:
            expected = None; trap = True; traps += 1
        for bias in (0, 0x40000000):
            output, status, _ = emulate(image, bias, tape_base_rva=0x10060,
                   code_limit=0x220+48*len(program), input_bytes=input_bytes,
                   max_steps=60000)
            if trap:
                assert status == 2, (program[:80], status)
            else:
                assert (output, status) == (expected, 0), (len(program), output, status, expected)
            simulations += 1
        verified += 1
    rejects = 0
    for program in (b'['+b'+'*511+b']', b'+'*511+b'[]', b'+'*512+b'[]',
                    b'['+b'+'*252, b']'+b'+'*100):
        try:
            compile_source(program, allow_loops=True, page_class=True)
        except ValueError:
            rejects += 1
        else:
            raise AssertionError('out-of-limit or unbalanced loops accepted')
    # Atomicity on rejected source, and CLI success on the largest nested program.
    with tempfile.TemporaryDirectory() as folder:
        base = Path(folder); source_path = base/'program.bf'; target = base/'output.elf'
        source_path.write_bytes(b'+'*511+b'[]'); target.write_bytes(b'unmodified')
        args = [sys.executable, str(ROOT/'bootstrap/run_android_extended.py'),
                str(source_path), str(target), '--page-class', '--loops']
        r = subprocess.run(args, capture_output=True, timeout=80)
        assert r.returncode and target.read_bytes() == b'unmodified'
        source_path.write_bytes(b'[]'*127+b'.')
        r = subprocess.run(args, capture_output=True, timeout=80)
        assert r.returncode == 0, r.stderr
        assert target.read_bytes() == compile_source(source_path.read_bytes(),
                                                allow_loops=True, page_class=True)
        if shutil.which('readelf'):
            r = subprocess.run(['readelf','-Wl',str(target)], check=True,
                               capture_output=True, text=True)
            assert 'Requesting program interpreter: /system/bin/linker64' in r.stdout
    seed_comparisons = 0
    if shutil.which('cc'):
        with tempfile.TemporaryDirectory() as folder:
            for interpreter in ('seed_interpreter.c', 'seed_interpreter_alt.c'):
                target = Path(folder)/interpreter
                subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/interpreter),
                                '-o',str(target)], check=True, capture_output=True)
                for program in (b'+'*90+b'[-].', b'[]'*45+b'.'):
                    slots = bf_native(SLOT_NATIVE, program, 'slots')[:-5]
                    records = run_stage('wide_encode', run_stage('wide_pairs',
                                     run_stage('wide_metadata', program)))
                    payload = bytes([len(program)])+records+slots
                    interpreted = subprocess.run([str(target),str(WIDE_255_SOURCE),'75000000'],
                            input=payload, capture_output=True, timeout=50, check=True)
                    native = bf_native(WIDE_255_NATIVE, payload, 'patch')
                    assert interpreted.stdout == native
                    seed_comparisons += 1
    evidence = json.loads(WIDE_255_EVIDENCE.read_text())
    evidence.update({'classification':'EXECUTED_LINUX_NATIVE_BF_PATCH_SIMULATED_AARCH64',
        'source_variants_compiled_identically':2,'programs_checked':verified,
        'matched_bracket_pairs_checked':checked_pairs,'aarch64_simulator_runs':simulations,
        'linear_parity_cases':parity,'pointer_traps':traps,'rejections':rejects,
        'independent_seed_matches':seed_comparisons, 'cli_atomic_rejection':True,
        'readelf_checked':bool(shutil.which('readelf')),
        'elapsed_seconds':round(time.monotonic()-start,3),
        'android_device_executed':False,'android_native_selfhosting':False})
    WIDE_255_EVIDENCE.write_text(json.dumps(evidence,indent=2)+'\n')
    print(f'BF 255-slot patch: {verified} programs, {checked_pairs} loop pairs, '
          f'{simulations} simulations, {rejects} rejections, {seed_comparisons} seed matches')

if __name__ == '__main__':
    main()
