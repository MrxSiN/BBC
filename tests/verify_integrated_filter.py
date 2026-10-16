#!/usr/bin/env python3
"""Verify integrated BF source compaction against the archived native S2 baseline.

This is a native-output differential oracle. Filtering of the independent
expected source is test logic only; the authoritative compiler filters in BF.
"""
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tests'), str(ROOT/'bootstrap')]
from transport import encode_source, extract_artifact
from verify_decoder_compaction_prototype import programs
from verify_emission import verify_elf

OPS = b'><+-.,[]'
CURRENT = ROOT/'build/compiler_x86_64_linux.elf'
BASELINE = ROOT/'evidence/history/iteration18/compiler_x86_64_linux.elf'
CORE = ROOT/'compiler/core.bf'
REPORT = ROOT/'evidence/integrated_filter.json'


def run(executable, source, timeout=60):
    res = subprocess.run([str(executable)],input=encode_source(source),capture_output=True,timeout=timeout)
    assert res.returncode == 0, (executable,res.returncode,res.stderr[-160:])
    assert res.stdout and res.stdout[-1] in (0,1), (executable,res.stdout[-12:])
    return res.stdout


def main():
    cases = list(programs())
    cases.extend([
        ('integrated_compiler_self_source',CORE.read_bytes(),b''),
        ('huge_ignored_source',b'ignored source text '*4000+b'+.',b''),
        ('huge_ignored_binary',b'\0\xff '*12000+b'[+].',b''),
        ('maximum_commands_with_ignored_bytes',b'+'*16127+b' ignore me '*100+b'.',b''),
        ('overflow_with_ignored_bytes',b'+'*16128+b' ignore me '*100+b'.',b''),
        ('nested_interleaved',b'+++[>comment++[>ignore+++<-]<-]>>.',b''),
    ])
    success = 0
    reject = 0
    records = []
    for name,raw,_ in cases:
        filtered = bytes(ch for ch in raw if ch in OPS)
        observed = run(CURRENT,raw)
        expected = run(BASELINE,filtered)
        assert observed==expected,(name,len(observed),len(expected),observed[-1],expected[-1])
        if observed[-1] == 0:
            verify_elf(raw,extract_artifact(observed))
            success+=1
        else:
            reject+=1
        records.append({'case':name,'source_bytes':len(raw),'commands':len(filtered),
                        'status':observed[-1], 'output_sha256':hashlib.sha256(observed).hexdigest()})
    # Compaction must not mask malformed byte transport or manufacture an ELF.
    invalid = [b'\xff',b'\xff\x03',b'\xff\xff',b'\xff\x00',b'+\xff\x03']
    for wire in invalid:
        a=subprocess.run([str(CURRENT)],input=wire,capture_output=True,timeout=30)
        b=subprocess.run([str(BASELINE)],input=wire,capture_output=True,timeout=30)
        assert a.returncode==b.returncode==0 and a.stdout==b.stdout and a.stdout[-1]!=0
    assert any(c['source_bytes']>65536 and c['status']==0 for c in records), 'long comments not verified'
    assert any(c['commands']==16128 and c['status']==0 for c in records), 'limit missing'
    assert any(c['commands']==16129 and c['status']!=0 for c in records), 'limit overflow missing'
    evidence = {
        'date':'2026-10-12',
        'classification':'EXECUTED: in-core Brainfuck filtering, native ELF byte identity against archived native compiler',
        'authoritative_source_sha256':hashlib.sha256(CORE.read_bytes()).hexdigest(),
        'integrated_native_elf_sha256':hashlib.sha256(CURRENT.read_bytes()).hexdigest(),
        'independent_archived_native_elf_sha256':hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
        'cases_passed':len(cases), 'accepted':success,'rejected':reject,
        'malformed_transport_rejections':len(invalid),
        'byte_identical_outputs':True,
        'limitations':['Baseline already shares the earlier x86-64 BF code emitter; this test does not independently prove every native template.',
                       'These executions do not establish formal compiler scratch-lane nonoverlap.'],
        'cases':records,
    }
    REPORT.write_text(json.dumps(evidence,indent=2)+'\n')
    print(f'PASS {len(cases)} integrated-native vs archived-native comparisons, {len(invalid)} malformed inputs rejected')


if __name__=='__main__':
    main()
