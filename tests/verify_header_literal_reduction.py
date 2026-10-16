#!/usr/bin/env python3
"""Validate 39 pure BF header constant reductions and scratch-cell contracts.

The old source is read-only historical evidence; this test NEVER emits ELF code.
The BF compiler itself emits all machine code during bootstrap.
"""
from pathlib import Path
import hashlib,json,re

ROOT = Path(__file__).resolve().parents[1]
OPS=b'><+-.,[]'
OLD=ROOT/'evidence/history/iteration18/core.bf'
NEW=ROOT/'compiler/core.bf'
PATCH=ROOT/'experiments/decoder_compaction_insertion.bf'


def code(path):
    return bytes(b for b in path.read_bytes() if b in OPS)


def shorter(n):
    choices=[]
    for a in range(2,24):
        for b in range(2,24):
            for sign in (1,-1):
                rem=(n-sign*a*b)%256
                if rem>128: rem-=256
                body=b'>'+b'+'*a+b'[<'+(b'+' if sign>0 else b'-')*b+b'>-]<' + ((b'+'*rem) if rem>=0 else b'-'*(-rem))
                choices.append(body)
    return min(choices,key=lambda v:(len(v),v))


def run(program,initial):
    # Tiny independent interpreter only for isolated BF arithmetic snippets.
    tape=[initial,0];ptr=0; stack=[];jump={}
    for i,c in enumerate(program):
        if c==91:stack.append(i)
        if c==93:
            j=stack.pop();jump[i]=j;jump[j]=i
    pc=0;steps=0
    while pc<len(program):
        steps+=1
        assert steps<10000
        c=program[pc]
        if c==62:ptr+=1
        if c==60:ptr-=1
        assert ptr in (0,1),'arithmetic reduced outside its owned cells'
        if c==43:tape[ptr]=(tape[ptr]+1)%256
        if c==45:tape[ptr]=(tape[ptr]-1)%256
        if c==91 and tape[ptr]==0:pc=jump[pc]
        if c==93 and tape[ptr]!=0:pc=jump[pc]
        pc+=1
    assert ptr==0 and tape[1]==0,'scratch must be cleared and pointer restored'
    return tape[0]


def main():
    original=code(OLD);current=code(NEW);patch=code(PATCH)
    assert len(original)==15907 and len(current)==14859 and len(patch)==1045
    assert current[:1145]==original[:1145]
    combined=original[:1145]+patch+original[1145:]
    replacements=[]
    for match in re.finditer(rb'[+\-]{50,}',original):
        start,end=match.span()
        if 1800<=start<5300:
            delta=len(match.group())*(1 if match.group()[0]==ord('+') else -1)
            shorter_code=shorter(delta)
            assert len(shorter_code)<end-start
            replacements.append((start,end,shorter_code,delta))
    assert len(replacements)==39
    saved=sum(b-a-len(x) for a,b,x,d in replacements)
    assert saved==2093
    # Reconstruct original BF program solely as a test oracle, in reverse offset order.
    # Insertion precedes every rewrite site, so compensate for its position.
    for start,end,replacement,_ in reversed(replacements):
        combined=combined[:start+len(patch)]+replacement+combined[end+len(patch):]
    assert combined==current,'authoritative code changed outside the verified two changes'
    # Trace the original source linearly across the literal emission region.
    # Existing bracket bodies return to the same tape pointer; they cannot alter cell61.
    pointer=60
    for c in original[1806:5232]:
        if c==62:pointer+=1
        if c==60:pointer-=1
        assert not (pointer==61 and c in (43,45,44)), 'old header writes scratch cell61'
    assert pointer==60,'old header BF pointer not restored'
    for _,_,replacement,delta in replacements:
        for value in range(256):
            assert run(replacement,value)==(value+delta)%256
    evidence={
        'date':'2026-10-12',
        'classification':'PROVEN conditional isolated 8-bit transformation, EXECUTED bootstrap and scratch witness separately; not full compiler ownership proof',
        'archived_source_sha256':hashlib.sha256(OLD.read_bytes()).hexdigest(),
        'current_source_sha256':hashlib.sha256(NEW.read_bytes()).hexdigest(),
        'replacements':len(replacements), 'source_instructions_saved':saved,
        'patch_instructions':len(patch), 'new_source_instructions':len(current),
        'isolated_arithmetic_cases':len(replacements)*256,
        'scratch_cell':61,
        'scratch_precondition':'scratch initially zero; original header does not write this cell in linear pointer scan at BF offsets 1806..5232',
        'scratch_postcondition':'every replacement restores pointer position and clears the temporary cell',
        'complete_expected_instruction_stream_matches_authoritative':True,
        'limitations':['Scratch zero on entry is a separately checked runtime assumption, not established formally for every possible compiler input.',
                       'This is not a proof of total compiler scratch-region separation.'],
    }
    (ROOT/'evidence/header_literal_reduction.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(f'PASS {len(replacements)} header substitutions, {len(replacements)*256} arithmetic equivalence cases, {saved} instructions saved')


if __name__=='__main__':
    main()
