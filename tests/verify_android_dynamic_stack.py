#!/usr/bin/env python3
"""Dynamic BF bracket stack with file-backed opaque storage (not ELF codegen)."""
from __future__ import annotations
import hashlib,json,random,struct,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tools')]
from transport import encode_source,extract_artifact
from source_check import check_source
from android_dynamic_stack_transport import pair_events,pair_source_dynamic

STAGES=[
 ('experiments/android_dynamic_stack_pairs.bf','build/android_dynamic_stack_pairs_x86_64_linux.elf'),
 ('experiments/android_pair_event_bridge.bf','build/android_pair_event_bridge_x86_64_linux.elf')]
sha=lambda x:hashlib.sha256(x).hexdigest()

def expected(source:bytes)->bytes|None:
    opens=[];pairs=[];i=0
    for c in source:
        if c not in b'><+-.,[]':continue
        if c==91:opens.append(i)
        elif c==93:
            if not opens:return None
            pairs.append(b']'+struct.pack('<QQ',opens.pop(),i))
        i+=1
    if opens:return None
    return b''.join(pairs)

def records(pairs):
    return b''.join(bytes((tag,))+struct.pack('<Q',pos) for tag,pos in pairs)

def run_stage(binary,wire):
    p=subprocess.run([str(binary)],input=wire,capture_output=True,check=True,timeout=30)
    assert not p.stderr
    return p.stdout

def main():
    begin=time.monotonic();stage_checks={}
    compiler=ROOT/'build/compiler_x86_64_linux.elf'
    for source,binary in STAGES:
        src=(ROOT/source).read_bytes();filtered=check_source(src)
        assert len(filtered)<=16128
        native=extract_artifact(run_stage(compiler,encode_source(src)))
        assert native==(ROOT/binary).read_bytes()
        assert native==extract_artifact(run_stage(compiler,encode_source(filtered)))
        stage_checks[source]={'bf_commands':len(filtered),'source_sha256':sha(src),
                              'linux_native_sha256':sha(native),'linux_native_bytes':len(native)}
    rng=random.Random(2026101350)
    cases=[b'',b'[]',b'[[]]',b'+++[->+<]>.',b'[][]',b'[A\x00[ignored]B]',
           b'['*256+b']'*256,b'['*4096+b']'*4096,
           b'['*1300+b'+'*800+b']'*1300,b'['+b'+'*100000+b']',b']',b'[',b'[]]',b'[[[]']
    for _ in range(90):
        depth=0;buf=bytearray()
        for _ in range(rng.randrange(0,200)):
            op=rng.choice(b'>.<+-, \n[[['+(b']]' if depth else b''))
            if op==91:depth+=1
            if op==93:depth-=1
            buf.append(op)
        buf.extend(b']'*depth)
        cases.append(bytes(buf))
    valid=0;invalid=0;maxdepth=0
    with tempfile.TemporaryDirectory(prefix='bf50-stack-') as folder:
        d=Path(folder);src=d/'source.bf';out=d/'pairs.bin';ev=d/'events.bin'
        for case in cases:
            src.write_bytes(case)
            oracle=expected(case)
            if oracle is None:
                out.write_bytes(b'PRESERVE')
                try:pair_source_dynamic(src,out)
                except ValueError:pass
                else:raise AssertionError('malformed brackets accepted')
                assert out.read_bytes()==b'PRESERVE'
                invalid+=1
            else:
                result=pair_source_dynamic(src,out)
                assert out.read_bytes()==oracle,(case[:90],out.read_bytes()[:100],oracle[:100])
                assert result['matched_pairs']==len(oracle)//17
                maxdepth=max(maxdepth,result['maximum_observed_depth'])
                valid+=1
        # Byte-width in generic LIFO events is eight, independent of 32-bit scan positions.
        large=(1<<40)+7
        ev.write_bytes(records([(1,0),(1,large),(2,large+9),(2,(1<<48)+101)]))
        result=pair_events(ev,out)
        assert result['matched_pairs']==2
        assert out.read_bytes()==b']'+struct.pack('<QQ',large,large+9)+b']'+struct.pack('<QQ',0,(1<<48)+101)
        # Invalid device tag or stack underflow fail closed and preserve destination.
        for bad in (records([(2,45)]),records([(1,45)]),records([(3,45)])):
            ev.write_bytes(bad);out.write_bytes(b'PRESERVE')
            try:pair_events(ev,out)
            except ValueError:pass
            else:raise AssertionError('invalid device request accepted')
            assert out.read_bytes()==b'PRESERVE'
        ev.write_bytes(records([(1,1),(2,5)]));out.write_bytes(b'PRESERVE')
        try:pair_events(ev,out,max_pairs=0)
        except ValueError:pass
        else:raise AssertionError('zero output quota ignored')
        assert out.read_bytes()==b'PRESERVE'
        # Independent C BF interpreter seeds on an input/output transcript.
        seed_checks=0
        p0=(123456789).to_bytes(8,'little');p1=(123456900).to_bytes(8,'little')
        inputs=b'\1'+p0 + b'\2'+p1 + b'\1'+p0 + b'\1'+p0 + b'\0'*9 + b'\0'
        outputs=(b'R'+b'P'+p0+b'R'+b'O'+b'M'+p0+p1+b'R'+b'P'+p0+b'R'+b'E'+b'D'+b'\1')
        # Correct transcript for an extra unmatched open has status error.
        assert run_stage(ROOT/'build/android_dynamic_stack_pairs_x86_64_linux.elf',inputs)==outputs
        for interpreter in ('seed_interpreter.c','seed_interpreter_alt.c'):
            binary=d/interpreter
            subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/interpreter),'-o',str(binary)],
                           check=True,capture_output=True)
            output=subprocess.run([str(binary),str(ROOT/STAGES[0][0]),'30000000'],
                                  input=inputs,capture_output=True,check=True,timeout=30).stdout
            assert output==outputs
            seed_checks+=1
        # The actual 100-million-span proof uses a BF source scanner, not just
        # manually populated large integer records.
        src.write_bytes(b'['+b'+'*100_000_000+b']')
        long_span=pair_source_dynamic(src,out)
        assert out.read_bytes()==b']'+struct.pack('<QQ',0,100_000_001)
        assert long_span['source_raw_bytes']==100_000_002
    evidence={'iteration':50,'classification':'BF_SOURCE_SCANNED_DYNAMIC_FILE_BACKED_BRACKET_STACK_LINUX_EXECUTED',
         'bf_stages':stage_checks,'total_source_cases':len(cases),'valid_cases':valid,
         'invalid_cases':invalid,'verified_nesting_depth':maxdepth,
         'pair_event_offset_bits':64,'scanner_source_offset_bits':32,
         'source_100m_span_verified':True,'source_100m_closing_index':100000001,
         'source_100m_pair_record_count':long_span['matched_pairs'],
         'independent_interpreter_transcripts':seed_checks,
         'generic_device_accepts_large_positions':True,
         'atomic_rejections_and_pair_quota_preservation':4,
         'source_filter_and_stack_decisions_owned_by_standard_bf':True,
         'stack_dynamic_storage':True,'elf_code_generation_integrated':False,
         'android_execution':'NOT_RUN',
         'elapsed_seconds':round(time.monotonic()-begin,3)}
    (ROOT/'evidence/iteration50_android_dynamic_stack.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))
if __name__=='__main__':main()
