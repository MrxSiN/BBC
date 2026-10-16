#!/usr/bin/env python3
"""Iteration 64 BFP1 native stream/relocation structural acceptance tests."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import tempfile
import zipfile
from unittest.mock import patch

from bootstrap.android_callable_code_validate64 import validate_code
from bootstrap.android_callable_elf_validate63 import validate_dso
from bootstrap.android_dynamic_callable59 import compile_shared
from bootstrap.android_dynamic_callable58 import ROOT
from tests.verify_android_dynamic_callable58 import reference, emulate_callable


def verify():
    rng = random.Random(64)
    result = {
        'iteration':64,
        'evidence_classification':'LOCAL_BF_NATIVE_DSO_STRUCTURE_AND_AARCH64_SIMULATOR',
        'authoritative_bf_source_modified':False,
        'native_structural_validator':'BFP1_TEMPLATE_WHITELIST_AND_MATCHED_RELOCATION_TARGETS',
        'BF_generated_compiles':0,'simulated_reference_comparisons':0,
        'corrupt_native_rejections':0,'atomic_corrupt_opcode_rejected':False,
        'atomic_corrupt_relocation_rejected':False,
        'old_policy_images_validated':0,
        'android_device_executed':False,
        'android_native_compiler_selfhosted':False,
    }
    root = ROOT
    with tempfile.TemporaryDirectory(prefix='bfc64-') as td:
        d = Path(td)
        src = d/'sample.bf'; dst = d/'compiled.so'
        # Includes all operations, nested loops, zero cell skips and long nesting.
        cases = [b'',b'+',b'-',b'>',b'<',b',',b'.',b'[]',
                 b'++[>++[>+<-]<-]>>.',b'+[->+<]>.',b',[->+<].',
                 b'['*1030 + b']'*1030]
        for _ in range(40):
            # Bounded loops with source ignoring non-BF bytes.
            block = bytes(rng.choice(b'+-<>.,') for _ in range(rng.randrange(20)))
            cases.append(block + b'[->+<][-] # not executable 1234\n')
        for program in cases:
            src.write_bytes(program)
            meta = compile_shared(src, dst)
            native = validate_code(dst)
            assert native['bracket_pairs'] == meta['bracket_pairs']
            assert native['maximum_nesting_depth'] == meta['maximum_nesting_depth']
            assert native['native_code_bytes'] == meta['native_code_bytes']
            assert validate_dso(dst)['bytes'] == meta['elf_bytes']
            content = dst.read_bytes()
            for _ in range(2):
                input_data = rng.randbytes(rng.randrange(4))
                tape_size = rng.choice((1,2,8,32))
                output_cap = rng.randrange(5)
                budget = rng.randrange(4)
                expected = reference(program,input_data,tape_size,output_cap,budget)
                got = emulate_callable(content,input_data,tape_size,output_cap,budget)
                assert (got[0],got[1],got[3],got[4]) == expected,program
                result['simulated_reference_comparisons'] += 1
            result['BF_generated_compiles'] += 1

        # A nontrivial image supplies a meaningful opened and closed veneer.
        src.write_bytes(b'++[>++[>+<-]<-]>>.')
        compile_shared(src,dst)
        good = dst.read_bytes()
        body = good[1024:]
        # Target real bytes in prologue, plus, forward/backward literal, and epilogue.
        open_veneer = bytes.fromhex('69014039e900003511000010')
        close_veneer = bytes.fromhex('69014039e900003411000010')
        opening = body.find(open_veneer)
        closing = body.find(close_veneer)
        assert opening > 0 and closing > 0
        for offset in (1024, 1024+32, 1024+opening+24,
                       1024+closing+24, len(good)-1):
            bad = bytearray(good);bad[offset] ^= 1
            target = d/'corrupt.so';target.write_bytes(bad)
            try:validate_code(target)
            except ValueError:result['corrupt_native_rejections'] += 1
            else:raise AssertionError(f'corrupted native code accepted at {offset}')
        # A mutation in loop offset that stays in range but points to a different
        # instruction is an independent relocation integrity failure.
        for offset in (1024+opening+24,1024+closing+24):
            bad=bytearray(good);bad[offset] += 1
            target=d/'wrong_target.so';target.write_bytes(bad)
            try:validate_code(target)
            except ValueError:result['corrupt_native_rejections'] += 1
            else:raise AssertionError('wrong relocation accepted')

        # Reproduce an after-codegen corruption without implementing an alternate
        # compiler: test-only mutation of the generated BF wrapper or ZIP payload.
        from bootstrap import android_dynamic_callable58 as backend
        original_stage = backend._native_stage
        src.write_bytes(b'++[->+<]>.')
        dst.write_bytes(b'PRIOR_OUTPUT')
        def bad_wrapper(name, incoming, outgoing, timeout):
            original_stage(name, incoming, outgoing, timeout)
            if name == 'android_callable_linear57':
                with outgoing.open('r+b') as f:
                    f.seek(0)
                    value=f.read(1)
                    f.seek(0);f.write(bytes([value[0]^1]))
        with patch.object(backend, '_native_stage', bad_wrapper):
            try:compile_shared(src,dst)
            except ValueError as exc:
                assert 'prologue' in str(exc)
            else:raise AssertionError('corrupt BF wrapper accepted')
        assert dst.read_bytes() == b'PRIOR_OUTPUT'
        result['atomic_corrupt_opcode_rejected']=True

        original_compile=backend.compile_relocated
        def bad_relocation(source, target, **opts):
            meta=original_compile(source,target,**opts)
            with zipfile.ZipFile(target,'r') as z:
                entries={name:z.read(name) for name in z.namelist()}
            code=bytearray(entries['code.bin'])
            seq=bytes.fromhex('69014039e900003511000010')
            loc=code.find(seq)
            assert loc>=0
            code[loc+24] ^= 1
            entries['code.bin']=bytes(code)
            with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_STORED) as z:
                for name,raw in entries.items():z.writestr(name,raw)
            return meta
        with patch.object(backend,'compile_relocated',bad_relocation):
            try:compile_shared(src,dst)
            except ValueError as exc:
                assert 'relocation' in str(exc) or 'veneer' in str(exc)
            else:raise AssertionError('corrupt BF relocation accepted')
        assert dst.read_bytes() == b'PRIOR_OUTPUT'
        result['atomic_corrupt_relocation_rejected']=True

        for p in list((root/'build/iteration59_dynamic').glob('*.so')) + list((root/'build/iteration60_android_loader').glob('*.so')):
            assert validate_code(p)['native_code_bytes'] + 1024 == p.stat().st_size
            result['old_policy_images_validated']+=1

    result['compiler_bf_hashes']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (root/'compiler/core.bf',root/'experiments/android_callable_slots58.bf',
                  root/'experiments/android_callable_ledger58.bf',
                  root/'experiments/android_callable_dso_header59.bf')}
    return result


def main():
    result=verify()
    target=ROOT/'evidence/iteration64_dynamic_callable_native_integrity.json'
    target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':main()
