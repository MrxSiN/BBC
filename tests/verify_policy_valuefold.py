#!/usr/bin/env python3
"""Verify BF-owned zero-derived constant stores and native AArch64 encoding.

This oracle independently models the 7-byte policy IR. No Python result is
fed back as compiled code, and archived Gmail images are never overwritten.
"""
import hashlib
import json
import random
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tests.verify_policy_ir import rle, resolve, optimize, fuse, oneshot, native_oracle
from bootstrap.linux_policy_native import LinuxPolicyNative
from bootstrap.transport import encode_source, extract_artifact
from tools.source_check import check_source

BUILD = ROOT / 'build/iteration55_linux/stages'


def hash_bytes(b):
    return hashlib.sha256(b).hexdigest()


def reference(ir):
    count = int.from_bytes(ir[:2], 'little')
    assert len(ir) == 7+count*7+2
    proof = ir[4]
    known = None
    records = []
    for i in range(count):
        op, amount, span, ptr, cost = struct.unpack_from('<BBHHB', ir, 7+7*i)
        if op in b'[I]E':
            known = None
        elif proof and op == ord('0'):
            known = (ptr, 0)
        elif proof and op in b'+-':
            if known is not None and ptr == known[0]:
                value = (known[1] + (amount if op == ord('+') else -amount)) & 255
                known = (ptr, value)
                amount = value
                if value == 0: op, cost = ord('0'), 1
                else: op, cost = ord('K'), 2
        elif op in b',A':
            if known is not None and ptr == known[0]:
                known = None
        records.append((op, amount, span, ptr, cost))
    return ir[:7] + b''.join(struct.pack('<BBHHB', *r) for r in records) + b'\0\0'


def run_elf(name, payload):
    p = subprocess.run([str(BUILD/(name+'.elf'))], input=payload,
                       capture_output=True, check=True, timeout=45)
    return p.stdout


def verify_case(source, check_full=True):
    # Source here has already been filtered to standard instructions. A source
    # with unproved absolute pointers must never be constant-folded.
    resolved = resolve(rle(source))
    if resolved is None: return False, 0, 0
    optimized = optimize(resolved)
    fused = fuse(optimized)
    folded = run_elf('policy_valuefold55', fused)
    assert folded == reference(fused), (source, folded[:18], reference(fused)[:18])
    n = folded.count(b'K')  # count candidate only, not an IR field count
    conditional = run_elf('policy_oneshot55', folded)
    assert conditional == oneshot(folded)
    if check_full:
        # Validate the entire BF-produced AArch64 native code, including
        # new literal stores, against a separately written word encoder.
        from tests.verify_policy_ir import stage
        expanded = stage('policy_operands', conditional)
        encoded = run_elf('policy_codegen55', expanded)
        image = stage('policy_elf', encoded)[:-1]
        assert image == native_oracle(conditional), source
    return True, sum(folded[7+7*i] == ord('K') for i in range(int.from_bytes(folded[:2], 'little'))), len(folded)


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    rebuilt = []
    for name in ('policy_valuefold55', 'policy_oneshot55', 'policy_codegen55'):
        src = (ROOT/'experiments'/(name+'.bf')).read_bytes()
        code = check_source(src)
        assert 0 < len(code) <= 16128
        raw = subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
                             input=encode_source(src), capture_output=True,
                             check=True, timeout=120)
        image = extract_artifact(raw.stdout)
        target = BUILD/(name+'.elf')
        assert image == target.read_bytes(), name
        target.chmod(0o755)
        rebuilt.append({'stage': name,'source_commands':len(code),
                        'source_sha256':hash_bytes(src),'elf_sha256':hash_bytes(image),
                        'elf_bytes':len(image)})
    rng = random.Random(55)
    cases = [b'', b'+', b'[-]++++', b'[-]+[-]++++', b'[-]+++>+<++++.',
             b',[-]+++.', b'++++[->+<]>.', b'<+.',b',[->+<]>.',
             b'[-]+[-]+[-]+[-]++++++++', b'[-]++[->+<]>[-]++++.']
    alphabet = b'++--<<>>.,[]'
    # Balanced but varied loop nestings, safe independent reference.
    for _ in range(98):
        a = bytearray()
        for j in range(rng.randint(1, 65)):
            a.append(rng.choice(b'++--<<>>.,'))
        if rng.getrandbits(1):
            a.extend(b'[-]')
        if rng.getrandbits(1):
            a.extend(b'++++[-]+++')
        cases.append(bytes(a))
    successes = transformed = 0
    for s in cases:
        passed, count, size = verify_case(s, check_full=True)
        successes += passed; transformed += count
    from tests.verify_policy_ir import stage
    gmail = {}
    for name in ('row', 'scope'):
        ir = (ROOT/'build/policy_native'/(name+'.fused')).read_bytes()
        folded = run_elf('policy_valuefold55', ir)
        assert folded == reference(ir)
        conditional = run_elf('policy_oneshot55', folded)
        assert conditional == oneshot(folded)
        expanded = stage('policy_operands', conditional)
        encoded = run_elf('policy_codegen55', expanded)
        new_img = stage('policy_elf', encoded)[:-1]
        assert new_img == native_oracle(conditional)
        old_img = (ROOT/'evidence/gm_native_20261014_v4'/(name+'.elf')).read_bytes()
        count = int.from_bytes(folded[:2], 'little')
        folded_count = sum(folded[7+7*i] == ord('K') for i in range(count))
        assert folded_count > 0
        out = ROOT/'build/iteration55_linux/gmail'/f'{name}.elf'
        out.parent.mkdir(exist_ok=True, parents=True)
        out.write_bytes(new_img)
        gmail[name] = {'original_sha256':hash_bytes(old_img), 'new_sha256':hash_bytes(new_img),
                       'original_bytes':len(old_img),'new_bytes':len(new_img),
                       'direct_constant_stores':folded_count, 'not_android_executed':True}
    from tests.reference import execute as interpret_bf
    interpret_cases = 0
    for sample in (b'[-]++++.', b'[-]+[-]+.'):
        resolved = resolve(rle(sample))
        small_ir = fuse(optimize(resolved))
        interpreted, _ = interpret_bf((ROOT/'experiments/policy_valuefold55.bf').read_bytes(),
                                      small_ir, max_steps=7000000)
        assert interpreted == reference(small_ir) == run_elf('policy_valuefold55', small_ir)
        interpret_cases += 1
    # Complete source-to-ELF replay: opt-in builds change; the original
    # archived Android compiler path must remain bit-for-bit unchanged.
    from bootstrap.run_policy_native import PolicyCompiler
    cp = PolicyCompiler(ROOT/'build/iteration55_linux/full_replay_test', backend='linux-seed')
    for name in ('row','scope'):
        raw = (ROOT/'evidence/gm_native_20261014_v4/GM/brainfuck/src'/(name+'.bf')).read_bytes()
        assert cp.compile(raw, affine=True, valuefold=True) == (ROOT/'build/iteration55_linux/gmail'/(name+'.elf')).read_bytes()
        assert cp.compile(raw, affine=True) == (ROOT/'evidence/gm_native_20261014_v4'/(name+'.elf')).read_bytes()
    report = {'classification':'LINUX_BF_STAGE_EXECUTION_AND_INDEPENDENT_AARCH64_BYTE_ORACLE',
              'device_executed':False,'tests_passed':successes,'constant_store_instances_in_cases':transformed,
              'stages':rebuilt,'gmail':gmail,'independent_bf_interpreter_cases':interpret_cases,
              'full_original_gmail_source_to_native_images':2,
              'performance_improvement_verified':False,'apk_parity_rerun':False,
              'baseline_gmail_images_remain_unchanged':True,
              'source_algorithm':'BF-owned record analysis policy_valuefold.bf'}
    evidence = ROOT/'evidence/iteration55_policy_valuefold.json'
    evidence.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',successes,'BF valuefold differential cases and Gmail image byte oracles')
    for n,row in gmail.items():print(n,row)

if __name__=='__main__':main()
