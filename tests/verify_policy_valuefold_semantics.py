#!/usr/bin/env python3
"""Independent functional IR differential: archived GM vs BF valuefold images.

This is an IR semantics test, NOT an Android device run or machine-code CPU
emulation.  Code bytes are independently validated in verify_policy_valuefold.
"""
from pathlib import Path
import random
import struct
import sys
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tests.verify_policy_ir import oneshot
from tests.verify_policy_valuefold import run_elf


def execute(ir, wire, maximum=500000):
    count=int.from_bytes(ir[:2],'little')
    records=[struct.unpack_from('<BBHHB',ir,7+7*i) for i in range(count)]
    stack=[];pairs={}
    for i,(op,*_) in enumerate(records):
        if op in b'[I':stack.append(i)
        elif op in b']E':
            if not stack:raise AssertionError('invalid IR loops')
            start=stack.pop();pairs[i]=start;pairs[start]=i
    assert not stack
    tape=bytearray(256);out=bytearray();head=0;source_value=0;pc=0;steps=0
    while pc<count:
        steps+=1
        if steps>maximum:return None
        op,amount,span,ptr,cost=records[pc]
        assert ptr<256, (ptr, pc)
        if op==ord('+'):tape[ptr]=(tape[ptr]+amount)&255
        elif op==ord('-'):tape[ptr]=(tape[ptr]-amount)&255
        elif op==ord('0'):tape[ptr]=0
        elif op==ord('K'):tape[ptr]=amount
        elif op==ord(','):
            tape[ptr]=wire[head] if head<len(wire) else 0
            if head<len(wire):head+=1
        elif op==ord('.'):
            if len(out)>2048:return None
            out.append(tape[ptr])
        elif op==ord('F'):source_value=tape[ptr]
        elif op==ord('A'):tape[ptr]=(tape[ptr]+source_value*amount)&255
        elif op in b'[I':
            if tape[ptr]==0:pc=pairs[pc]
        elif op==ord(']'):
            if tape[ptr]:pc=pairs[pc]
        elif op in b'<>NE':pass
        else:raise AssertionError(('unknown IR operation',op,pc))
        pc+=1
    return bytes(out),bytes(tape),head


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick', action='store_true', help='Run a short smoke subset without overwriting full evidence')
    args = parser.parse_args()
    samples = 24 if args.quick else 240
    rng=random.Random(20261014)
    record={}
    passed=0;timeouts=0
    for name in ('row','scope'):
        fused=(ROOT/'build/policy_native'/(name+'.fused')).read_bytes()
        original=oneshot(fused)
        optimized=run_elf('policy_oneshot55',run_elf('policy_valuefold55',fused))
        fixture=ROOT/'build/policy_native'/('row_miss.stdin' if name=='row' else 'scope_yes.stdin')
        base=fixture.read_bytes()
        assert execute(original,base)==execute(optimized,base)
        count=0
        for i in range(samples):
            payload=bytearray(base)
            # Mutate only the variable request payload; preserve ABI header.
            for j in range(rng.randint(0,min(7,max(len(base)-8,0)))):
                pos=rng.randrange(8,len(base));payload[pos]=rng.randrange(256)
            if i%5==0:payload=payload[:rng.randrange(8,len(payload)+1)]
            if i%13==0:payload += bytes(rng.getrandbits(8) for _ in range(i%14))
            left=execute(original,payload);right=execute(optimized,payload)
            if left is None or right is None:
                assert left is None and right is None,(name,i,left,right)
                timeouts+=1
            else:
                assert left==right,(name,i,left,right)
                count+=1
        record[name]={'functionally_equal_completed_frames':count,
                       'bounded_nonterminating_cases':samples-count,
                       'fixture_source_sha256':hashlib.sha256(base).hexdigest()}
        passed+=count
    evidence=ROOT/'evidence/iteration55_policy_semantics.json'
    if not args.quick: evidence.write_text(json.dumps({'classification':'LINUX_PYTHON_INDEPENDENT_IR_ORACLE',
         'original_vs_valuefold_frames_completed_equal':passed,
         'bounded_ir_step_limit':500000,
         'android_native_execution':False,'cases':record},indent=2)+'\n')
    print('PASS',passed,'completed original-Gmail IR differential cases',timeouts,'bounded timeouts')

if __name__=='__main__':main()
