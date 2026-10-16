#!/usr/bin/env python3
"""Independent RLE clear-fold differential oracle for native standard-BF stage.

The Python reference below is only a test oracle. In actual compilation,
policy_clear56.bf performs every record decision and writes the output.
"""
import hashlib
import json
import struct
import random
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tests.verify_policy_ir import rle
from bootstrap.transport import encode_source, extract_artifact
from tools.source_check import check_source

STAGE=ROOT/'experiments/policy_clear56.bf'
NATIVE=ROOT/'build/iteration56_linux/stages/policy_clear56.elf'


def ref(payload):
    assert len(payload) % 2 == 0 and payload[-2:] == b'\0\0'
    records=[tuple(payload[i:i+2]) for i in range(0,len(payload)-2,2)]
    out=[];i=0
    while i<len(records):
        if records[i:i+3] == [(91,0),(45,1),(93,0)]:
            out.extend((48,0));i+=3
        else:
            out.extend(records[i]);i+=1
    return bytes(out)+b'\0\0'


def run(payload):
    return subprocess.run([str(NATIVE)],input=payload,capture_output=True,
                          check=True,timeout=90).stdout


def source_input(source):
    return b''.join(bytes((op,run)) for op,run in rle(source))+b'\0\0'


def main():
    src=STAGE.read_bytes()
    assert len(check_source(src))<=16128
    elf=extract_artifact(subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
                    input=encode_source(src),capture_output=True,check=True,
                    timeout=120).stdout)
    assert elf == NATIVE.read_bytes()
    NATIVE.chmod(0o700)
    rng=random.Random(56)
    programs=[b'',b'[-]',b'[-][-]',b'++[->+<]>.',b'[[-]]',
              b'[-]+'*12,b'['*30+b'-'+b']'*30,b'[-]'*452+b'.'*3367]
    for _ in range(128):
        s=bytearray()
        for _ in range(rng.randrange(0,180)):
            s.extend(rng.choice((b'+',b'-',b'>',b'<',b'.',b',',b'[-]',b'[->+<]',b'[]')))
        programs.append(bytes(s))
    checks=0
    for program in programs:
        payload=source_input(program)
        got=run(payload)
        expected=ref(payload)
        assert got==expected,(program,got[:30],expected[:30]);checks+=1
    twitter_shape=programs[7]
    raw=source_input(twitter_shape)
    folded=run(raw)
    orig_count=(len(raw)-2)//2; reduced_count=(len(folded)-2)//2
    assert orig_count==4723 and reduced_count==3819
    # Independent interpreter seeds run unmodified standard-BF source.
    from tests.reference import execute
    bf_interpreter=0
    for program in (b'[-]',b'[[-]]',b'[-]+.',b'++[->+<]>.'):
        payload=source_input(program)
        result,_=execute(src,payload,max_steps=25000000)
        assert result==ref(payload)
        bf_interpreter+=1
    # End-to-end resolver must accept a formerly oversized stream once the
    # BF stage has canonicalized clear loops (not a genuine universal fix).
    resolver=ROOT/'build/iteration54_linux/stages/policy_resolve.elf'
    resolver.chmod(0o700)
    resolved=subprocess.run([str(resolver)],input=folded,capture_output=True,
                            check=True,timeout=180).stdout
    assert resolved[-2:]==b'\0\0'
    assert int.from_bytes(resolved[:2],'little')==3819
    # Exact effective eight-instruction stream extracted from the GitHub
    # version of MrxSiN/TwitterHideAds/brainfuck/src/action.bf. Comment text
    # has been filtered; this is NOT a modified source language.
    twitter_src=(ROOT/'tests/fixtures/real_apps/twitter_action_filtered.bf').read_bytes()
    assert len(twitter_src)==24616
    assert hashlib.sha256(twitter_src).hexdigest()==('a422986cc484115f489d1e8caec5adf4'
             '39f06346e3c82a4f8e61a3c332e54d24')
    actual_in=source_input(twitter_src)
    actual_out=run(actual_in)
    assert actual_out==ref(actual_in)
    actual_before=(len(actual_in)-2)//2
    actual_after=(len(actual_out)-2)//2
    assert actual_before==4723 and actual_after==3819
    from bootstrap.run_policy_native import PolicyCompiler
    from tests.verify_policy_ir import native_oracle
    from tests.verify_policy_valuefold_semantics import execute as execute_ir
    original=PolicyCompiler(ROOT/'build/iteration56_linux/twitter_action',backend='linux-seed')
    native=original.compile(twitter_src,affine=True,canonical_clears=True)
    image=ROOT/'build/iteration56_linux/twitter_action/action.elf'
    image.write_bytes(native)
    assert len(native)==15300
    assert hashlib.sha256(native).hexdigest()==('09e5e737f8bdb4531f081577f8d2b845'
             '0ce5e5b71a8f55b1e0298d0316a575fc')
    ir=(ROOT/'build/iteration56_linux/twitter_action/policy_oneshot.output').read_bytes()
    assert native==native_oracle(ir)
    subprocess.run(['readelf','-h',str(image)],check=True,capture_output=True,timeout=10)
    subprocess.run(['readelf','-l',str(image)],check=True,capture_output=True,timeout=10)
    action_letters={'#':1,'P':2,'r':3,'o':4,'m':5,'t':6,'e':7,
                    'd':8,'D':9,'i':10,'s':11,'A':12,'I':13,
                    'n':14,'f':15,'R':16,'p':17}
    def frame(names):
        payload=bytes([len(names)])
        for name,is_enum,is_action in names:
            codes=bytes(action_letters.get(x,0) for x in name)
            payload+=bytes((is_enum,is_action,len(codes)))+codes+b'\0'
        return struct.pack('<BBBBHH',1,0,32,0,len(payload),0x1234)+payload
    samples=[[],[('PromotedDismissAd',1,0)], [('PromotedAdsInfo',1,0)],
       [('PromotedReportAd',1,0)], [('Enum#PromotedDismissAd',0,0)],
       [('xyzPromotedAdsInfo',0,1)], [('not-a-match',1,0)],
       [('promotedReportAd',0,1)], [('Prefix#PromotedReportAd',0,0)],
       [('PromotedDismissAd',0,0),('wrong',1,1),('PromotedAdsInfo',1,0)]]
    seed=original.linux.seed
    ir_cases=0
    for names in samples:
        payload=frame(names)
        replay=subprocess.run([str(seed),str(ROOT/'tests/fixtures/real_apps/twitter_action_filtered.bf'),
                        '50000000'],input=payload,capture_output=True,timeout=30,check=True)
        expected=execute_ir(ir,payload,maximum=3000000)
        assert expected is not None and replay.stdout==expected[0],names
        ir_cases+=1
    # Default (noncanonical) path remains intentionally capacity-limited.
    try:
        original.compile(twitter_src,affine=True)
    except ValueError:
        pass
    else:
        raise AssertionError('legacy 4096-record limit silently changed')
    gmail={}
    for name in ('row','scope'):
        source=(ROOT/'evidence/gm_native_20261014_v4/GM/brainfuck/src'/(name+'.bf')).read_bytes()
        baseline=original.compile(source,affine=True,canonical_clears=True)
        valuefold=original.compile(source,affine=True,valuefold=True,canonical_clears=True)
        assert baseline==(ROOT/'evidence/gm_native_20261014_v4'/(name+'.elf')).read_bytes()
        assert valuefold==(ROOT/'build/iteration55_linux/gmail'/(name+'.elf')).read_bytes()
        gmail[name]={'previous_android_image_byte_identical':True,
                     'iteration55_optimized_image_byte_identical':True,
                     'baseline_sha256':hashlib.sha256(baseline).hexdigest(),
                     'valuefold_sha256':hashlib.sha256(valuefold).hexdigest()}
    twitter={'original_repo':'https://github.com/MrxSiN/TwitterHideAds',
        'upstream_path':'brainfuck/src/action.bf',
        'github_blob_sha':'7bf2eb045cace0fad460ad879bbc72f04c823df0',
        'effective_source_sha256':hashlib.sha256(twitter_src).hexdigest(),
        'effective_source_commands':len(twitter_src),
        'original_rle_records':actual_before,
        'canonical_rle_records':actual_after,
        'compiled_aarch64_elf_bytes':len(native),
        'compiled_aarch64_sha256':hashlib.sha256(native).hexdigest(),
        'independent_native_byte_oracle':True,
        'independent_source_bf_vs_optimized_ir_frame_parity':ir_cases,
        'real_android_loader_executed':False,
        'android_jni_or_apk_tested':False}
    report={'classification':'LINUX_NATIVE_BF_CANONICAL_CLEAR_RLE_PREPASS',
            'source_commands':len(check_source(src)),
            'source_sha256':hashlib.sha256(src).hexdigest(),
            'native_elf_bytes':len(elf),
            'native_elf_sha256':hashlib.sha256(elf).hexdigest(),
            'differential_cases':checks,
            'independent_bf_interpreter_cases':bf_interpreter,
            'large_shape_records_before':orig_count,
            'large_shape_records_after':reduced_count,
            'large_shape_resolver_accepted':True,
            'twitter_action':twitter,
            'gmail_regression':gmail,
            'actual_twitter_source_compiled':True,
            'device_executed':False}
    target=ROOT/'evidence/iteration56_policy_clear.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',checks,'BF/native RLE differential cases; Twitter action compiled 4723 -> 3819; IR parity',ir_cases)

if __name__=='__main__':main()
