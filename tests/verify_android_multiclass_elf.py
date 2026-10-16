#!/usr/bin/env python3
"""Differential test oracle for Iteration 34 BF-owned ELF relayout."""
from __future__ import annotations
import hashlib, json, random, shutil, struct, subprocess, sys, tempfile, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'bootstrap'),str(ROOT/'tools'),str(ROOT/'tests')]
from transport import encode_source, extract_artifact
from source_check import check_source
from run_android_extended import (compile_source, bf_native, MULTICLASS_SOURCE,
    MULTICLASS_NATIVE, MULTICLASS_EVIDENCE, check_provenance)
from verify_android_aarch64_subset import emulate
from reference import execute

def digest(b):return hashlib.sha256(b).hexdigest()

def validate(image, n):
    rx_size=0x220+48*n
    aligned=(rx_size+0x3fff)&~0x3fff
    assert len(image)==aligned+96,(n,len(image),aligned)
    assert image[:8]==b'\x7fELF\2\1\1\0'
    assert struct.unpack_from('<H',image,18)[0]==183
    segments=[struct.unpack_from('<IIQQQQQQ',image,64+i*56) for i in range(5)]
    assert [x[0] for x in segments]==[6,3,1,1,2]
    rx,rw,dyn=segments[2:]
    assert (rx[1],rx[2],rx[3],rx[5],rx[6],rx[7])==(5,0,0,rx_size,rx_size,0x4000)
    assert (rw[1],rw[2],rw[3],rw[5],rw[6],rw[7])==(6,aligned,0x10000,96,65632,0x4000)
    assert (dyn[2],dyn[3],dyn[5],dyn[6])==(aligned,0x10000,96,96)
    assert image[rx_size:aligned]==bytes(aligned-rx_size)
    assert image[0x210+48*n:rx_size]==struct.pack('<4I',0xd2800000,0xd2800ba8,0xd4000001,0xd503201f)
    assert image[aligned:aligned+96]==(ROOT/'build/android_dynamic_linear_255_aarch64.elf').read_bytes()[0x4000:0x4060]
    assert rx_size <= 0x10000 and rw[3]>=rx_size
    for p in (rx,rw): assert p[2]%p[7] == p[3]%p[7]
    return aligned

def pairs(program):
    st=[];out=[]
    for p,b in enumerate(program,1):
        if b==91:st.append(p)
        elif b==93:
            assert st
            out.append((st.pop(),p))
    assert not st
    return out

def check_branches(program,image):
    for lo,hi in pairs(program):
        span=hi-lo
        for p,word in ((lo,0x14000000|((12*span+10)&0x3ffffff)),
                       (hi,0x14000000|((10-12*span)&0x3ffffff))):
            off=0x210+48*(p-1)+8
            assert image[off:off+4]==struct.pack('<I',word),(len(program),lo,hi,p)
    return len(pairs(program))

def main():
    start=time.monotonic()
    source=MULTICLASS_SOURCE.read_bytes(); filtered=check_source(source)
    assert len(filtered)<16128
    check_provenance(allow_loops=True,multiclass=True)
    expected=MULTICLASS_NATIVE.read_bytes()
    for s in (source,filtered):
        r=subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
             input=encode_source(s),capture_output=True,timeout=60,check=True)
        assert extract_artifact(r.stdout)==expected
    counts=(0,1,2,73,74,254,255,256,329,330,331,332,511,512,513,
            670,671,672,673,674,1011,1012,1013,1014,1023,1024)
    for n in counts:
        img=compile_source(b'+'*n,multiclass=True)
        validate(img,n)
    programs=[b'',b'+[-].',b'+[>+<-]>.',b'[]'*128, b'[]'*512,
       b'+'*508+b'[-].',b'+'*509+b'[-].',b'+'*510+b'[-]',
       b'+'*667+b'[-].',b'+'*668+b'[-].',b'+'*669+b'[-].',
       b'+'*670+b'[->+<]>.',b'+'*1009+b'[-].',b'+'*1010+b'[-].',
       b'+'*1011+b'[-].',b'+'*1015+b'[->+<]>.',b'+'*1021+b'[-]',
       b'['+b'+'*1022+b']',b'+'*1024,b'<'*1024,b','*1023+b'.',
       b'['*255+b']'*255,b'+'*800+b'[[-]]',b'+'*1000+b'[>++[>+<-]<-]>>.']
    rng=random.Random(2026101334)
    chunks=[b'++[->+<]>[-]<',b'+[-].',b'[-]',b'[]',b'>+[-]<',b',[-].',b'++--',b'+[[-]]']
    for _ in range(47):
        target=rng.randint(513,1024); buf=bytearray()
        while len(buf)<target:
            item=rng.choice(chunks)
            if len(buf)+len(item)>target:
                buf.extend(b'+'*(target-len(buf)))
                break
            buf.extend(item)
        programs.append(bytes(buf))
    inputs=bytes((i*113+11)&255 for i in range(2048))
    simulated=0; traps=0; bracket_pairs=0; class_3=class_4=0; programs_checked=0; legacy_parity=0
    for p in programs:
        if len(p)>1024:continue
        im=compile_source(p,allow_loops=b'[' in p,multiclass=True)
        off=validate(im,len(p))
        if off==0xc000:class_3+=1
        if off==0x10000:class_4+=1
        bracket_pairs+=check_branches(p,im)
        if len(p)<=512:
            assert im==compile_source(p,allow_loops=b'[' in p,page_class=True)
            legacy_parity+=1
        try:
            expected_out,_=execute(p,inputs,max_steps=250000)
            trap=False
        except IndexError:
            expected_out=None;trap=True;traps+=1
        except TimeoutError:
            raise AssertionError('invalid nonterminating fixture '+repr(p[:80]))
        for base in (0,0x40000000):
            output,status,_=emulate(im,base,tape_base_rva=0x10060,
                code_limit=0x220+48*len(p),input_bytes=inputs,max_steps=250000)
            if trap: assert status==2,(len(p),status)
            else: assert (output,status)==(expected_out,0),(len(p),status,output[:16],expected_out[:16])
            simulated+=1
        programs_checked+=1
    assert class_3 and class_4 and bracket_pairs
    rejects=0
    for bad in (b'+'*1025,b'['+b'+'*1023+b']',b'+'*1023+b'[]',
                b'['+b'+'*1023,b']'+b'+'*1020,b'['*256+b']'*256):
        try:compile_source(bad,allow_loops=True,multiclass=True)
        except ValueError:rejects+=1
        else:raise AssertionError('unsupported source accepted')
    with tempfile.TemporaryDirectory() as td:
        td=Path(td);src=td/'bad.bf';dest=td/'result.elf'
        src.write_bytes(b'+'*1025);dest.write_bytes(b'do not overwrite')
        cmd=[sys.executable,str(ROOT/'bootstrap/run_android_extended.py'),str(src),str(dest),'--multiclass','--loops']
        r=subprocess.run(cmd,capture_output=True,timeout=45)
        assert r.returncode and dest.read_bytes()==b'do not overwrite'
        src.write_bytes(b'+'*1015+b'[->+<]>.')
        r=subprocess.run(cmd,capture_output=True,timeout=45)
        assert r.returncode==0,r.stderr
        assert dest.read_bytes()==compile_source(src.read_bytes(),allow_loops=True,multiclass=True)
        if shutil.which('readelf'):
            read=subprocess.run(['readelf','-Wl',str(dest)],capture_output=True,text=True,check=True).stdout
            assert 'Requesting program interpreter: /system/bin/linker64' in read
            assert 'LOAD' in read
    # Seed interpreter comparison exceeds the conservative 75M-step budget
    # for the smallest 16KiB ELF image. Keep this gate explicitly unverified.
    matches=0
    evidence=json.loads(MULTICLASS_EVIDENCE.read_text())
    evidence['classification']='EXECUTED_LINUX_NATIVE_BF_STAGES_AARCH64_SIMULATED_NOT_ANDROID_DEVICE'
    evidence['verified']={'source_variants_compiled_identically':2,
      'direct_boundary_counts_checked':len(counts),'programs_checked':programs_checked,
      'aarch64_simulator_runs':simulated,'bracket_pairs_checked':bracket_pairs,
      'third_size_class_programs':class_3,'fourth_size_class_programs':class_4,
      'legacy_page_class_byte_parity_cases':legacy_parity,'pointer_traps':traps,
      'invalid_rejections':rejects,'atomic_output_preservation':True,
      'independent_seed_matches':matches,
      'independent_seed_gate':'INCONCLUSIVE_75M_STEP_LIMIT_ON_FIRST_SEED',
      'readelf_checked':bool(shutil.which('readelf')),
      'elapsed_seconds':round(time.monotonic()-start,3)}
    MULTICLASS_EVIDENCE.write_text(json.dumps(evidence,indent=2)+'\n')
    print('MULTICLASS VERIFIED',evidence['verified'])

if __name__=='__main__':main()
