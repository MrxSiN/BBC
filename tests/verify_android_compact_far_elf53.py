#!/usr/bin/env python3
"""Linux-hosted BF-owned PC-relative signed-64 loop-branch verification.

The AArch64 emulator below is instruction-level only, NOT an Android device.
"""
from pathlib import Path
import hashlib,json,random,struct,subprocess,tempfile,time,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from bootstrap.android_compact_dynamic_far_elf53 import compile_elf
from bootstrap.android_compact_dynamic_elf52 import compile_elf as old_compile
from tests.verify_android_aarch64_subset import emulate
from tests.reference import execute
from tools.source_check import check_source
from bootstrap.transport import encode_source,extract_artifact
STAGES=['android_compact_far_slots53','android_compact_far_ledger53',
        'android_compact_far_position53','android_compact_far_delta53']

def native(name,wire):
 p=subprocess.run([str(ROOT/'build'/f'{name}_x86_64_linux.elf')],input=wire,
                  capture_output=True,check=True,timeout=35)
 return p.stdout

def math_checks():
 checks=0;old_short_limit=1<<25
 for pos in (0,1,254,255,65534,(1<<32)-1,1<<32,1<<48,1<<63,(1<<64)-7):
  actual=native('android_compact_far_position53',b'\1'+pos.to_bytes(8,'little')+b'\0')
  assert actual==b'P'+(pos+6).to_bytes(8,'little')+b'\0';checks+=1
 for delta in (3,5,255,256,1<<16,old_short_limit-1,old_short_limit,
               old_short_limit+123,1<<32,1<<40,1<<60,1<<63,(1<<64)-8):
  for mode in (0,1):
   actual=native('android_compact_far_delta53',b'\1'+bytes([mode])+delta.to_bytes(8,'little')+b'\0')
   expected=delta+6 if mode==0 else (-delta-2)%(1<<64)
   assert actual==b'D'+expected.to_bytes(8,'little')+b'\0',(delta,mode)
   checks+=1
 for stage,wire in [('android_compact_far_position53',b'\1'+((1<<64)-5).to_bytes(8,'little')+b'\0'),
                    ('android_compact_far_delta53',b'\1\0'+((1<<64)-5).to_bytes(8,'little')+b'\0'),
                    ('android_compact_far_delta53',b'\1\1'+((1<<64)-1).to_bytes(8,'little')+b'\0')]:
  assert native(stage,wire)[-1]==1
 return checks

def main():
 begun=time.monotonic()
 integrity=[]
 for stage in STAGES:
  src=ROOT/'experiments'/f'{stage}.bf';binary=ROOT/'build'/f'{stage}_x86_64_linux.elf'
  source_bytes=src.read_bytes();code=check_source(source_bytes)
  assert len(code)<=16128 and binary.is_file()
  rebuild=subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],input=encode_source(source_bytes),capture_output=True,check=True,timeout=120)
  assert extract_artifact(rebuild.stdout)==binary.read_bytes()
  integrity.append(dict(stage=stage,bf_commands=len(code),
    source_sha256=hashlib.sha256(source_bytes).hexdigest(),
    linux_native_bytes=binary.stat().st_size,
    linux_native_sha256=hashlib.sha256(binary.read_bytes()).hexdigest()))
 from tests.reference import execute as bf_reference
 interpreter_cases=0
 for stage,wire in [('android_compact_far_position53',b'\1'+(12).to_bytes(8,'little')+b'\0'),
                    ('android_compact_far_delta53',b'\1\1'+(8).to_bytes(8,'little')+b'\0')]:
  interpreted,_=bf_reference((ROOT/'experiments'/f'{stage}.bf').read_bytes(),wire,max_steps=5000000)
  assert interpreted==native(stage,wire)
  interpreter_cases+=1
 arithmetic=math_checks()
 cases=[(b'',b''),(b'+.',b''),(b'-.',b''),(b'<',b''),
        (b'+[->+<]>.',b''),(b'+++[>++[>+<-]<-]>>.',b''),
        (b',.,.',b'\x00\xff'),(b'+,.',b''),
        (b'[[]]',b''),(b'['*300+b']'*300,b''),(b'['*1025+b']'*1025,b''),
        (b'+'*3200+b'[->+<]>.',b''),(b'+'*100+b'[-][[]]',b'')]
 rng=random.Random(53)
 for _ in range(44):
  prefix=bytes(rng.choice(b'+-<>.,') for _ in range(rng.randrange(1,44)))
  cases.append((prefix+b'[-][[]]',bytes(rng.randrange(256) for _ in range(11))))
 simulations=0;traps=0;matched=0;maximum=0;parity=0;good=0
 with tempfile.TemporaryDirectory(prefix='bf53-far-tests-') as t:
  d=Path(t);src=d/'source.bf';out=d/'aarch64.elf';other=d/'previous.elf'
  for text,input_bytes in cases:
   src.write_bytes(text);info=compile_elf(src,out);image=out.read_bytes()
   assert info['elf_bytes']==len(image)
   assert not info['direct_AARCH64_branch_reach_limit']
   assert struct.unpack_from('<Q',image,208)[0]==len(image)-0x20000
   subprocess.run(['readelf','-Wl',str(out)],stdout=subprocess.DEVNULL,check=True)
   try:expected,_=execute(text,input_bytes,max_steps=500000);status=0
   except IndexError:expected=None;status=2;traps+=1
   for bias in (0,0x40000000):
    observed,exit_code,_=emulate(image,bias,tape_base_rva=0x4000,
      code_start_rva=0x20000,code_limit=len(image),input_bytes=input_bytes,max_steps=500000)
    assert exit_code==status and (expected is None or observed==expected),(text[:50],exit_code,observed,expected)
    simulations+=1
   if not any(c in text for c in b'[]'):
    old_compile(src,other)
    assert other.read_bytes()==image
    parity+=1
   matched+=info['bracket_pairs_relocated'];maximum=max(maximum,info['bf_native_instructions']);good+=1
  bad=[(b'[',{}),(b']',{}),(b'[]',{'max_pairs':0}),(b'+'*20,{'max_native_bytes':24})]
  for source,kw in bad:
   src.write_bytes(source);out.write_bytes(b'KEEP')
   try:compile_elf(src,out,**kw)
   except (ValueError,RuntimeError):pass
   else:raise AssertionError('invalid source accepted')
   assert out.read_bytes()==b'KEEP'
  # Structural large source: no CPU claim for the lengthy body.
  big=b'['+b'+'*50000+b']';src.write_bytes(big)
  biginfo=compile_elf(src,out)
  subprocess.run(['readelf','-Wl',str(out)],stdout=subprocess.DEVNULL,check=True)
  assert biginfo['bf_native_instructions']==50002 and biginfo['bracket_pairs_relocated']==1
  # Check patch literals at the exact BF-emitted template positions.
  with out.open('rb') as f:
   f.seek(0x20000+16+6*4);forward=int.from_bytes(f.read(8),'little')
   assert forward==biginfo['native_compact_code_bytes']//4-2
  biginfo['structural_only_not_simulated']=True
 report={'iteration':53,'classification':'BF_OWNED_PC_RELATIVE_64BIT_ELF_LINUX_SIMULATED_NOT_ANDROID_LOADER',
  'bf_stages':integrity,'wide_arithmetic_cases_passed':arithmetic,'independent_bf_interpreter_comparisons':interpreter_cases,
  'fresh_stage_rebuilds_identical':len(integrity),
  'small_program_cases_passed':good,'aarch64_simulator_runs':simulations,
  'expected_pointer_traps':traps,'bracket_pairs_checked':matched,
  'max_small_source_commands':maximum,'bracket_free_byte_identical_elf_parity':parity,
  'atomic_invalid_source_rejections':len(bad),
  'large_structural_source_commands':biginfo['bf_native_instructions'],
  'large_structural_elf_bytes':biginfo['elf_bytes'],
  'above_old_AARCH64_imm26_reach_arithmetic_tested':True,
  'large_reach_actual_elf_executed':False,
  'real_android_loader_execution':False,'real_app_policy_compilations':0,
  'elapsed_seconds':round(time.monotonic()-begun,2)}
 (ROOT/'evidence/iteration53_android_far_elf_tests.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
