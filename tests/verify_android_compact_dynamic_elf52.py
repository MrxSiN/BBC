#!/usr/bin/env python3
"""BF-owned compact AArch64 ELF regression; Linux simulation, not Android loading."""
from pathlib import Path
import hashlib,json,random,struct,subprocess,tempfile,time,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from bootstrap.android_compact_dynamic_elf52 import compile_elf
from bootstrap.android_compact_relocated_stream52 import compile_relocated
from tests.verify_android_aarch64_subset import emulate
from tests.reference import execute
from tools.source_check import check_source
from bootstrap.transport import encode_source,extract_artifact
ROOT=Path(__file__).resolve().parents[1]
STAGES=['android_compact_span64_52','android_compact_branch_words52','android_compact_patch_indices52',
 'android_compact_elf_word_plus7_52','android_compact_elf_words_to_bytes52','android_compact_elf_header52']

def native(stage,body):
 return subprocess.run([str(ROOT/'build'/f'{stage}_x86_64_linux.elf')],input=body,capture_output=True,check=True,timeout=30).stdout

def main():
 begin=time.monotonic();details=[]
 for stage in STAGES:
  s=ROOT/'experiments'/f'{stage}.bf';b=check_source(s.read_bytes())
  assert len(b)<=16128,(stage,len(b))
  image=(ROOT/'build'/f'{stage}_x86_64_linux.elf').read_bytes()
  for source in (s.read_bytes(),b):
   got=subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],input=encode_source(source),capture_output=True,check=True,timeout=90)
   assert extract_artifact(got.stdout)==image
  details.append({'stage':stage,'bf_commands':len(b),'source_sha256':hashlib.sha256(s.read_bytes()).hexdigest(),'linux_native_bytes':len(image),'linux_native_sha256':hashlib.sha256(image).hexdigest()})
 mathcases=0;reach_rejected=0
 for a,c in ((0,3),(1,1024),(2**32-1,2**32+4),(2**56,2**56+100),(2**48,2**48+2**25-2),(2**48,2**48+2**25-1),(2**50,2**50-1)):
  enc=native('android_compact_span64_52',b'\1'+a.to_bytes(8,'little')+c.to_bytes(8,'little')+b'\0')
  assert int.from_bytes(enc[17:25],'little')==(c-a)%(2**64)
  assert enc[-1]==int(c<a)
  if c>a:
   delta=c-a
   word=native('android_compact_branch_words52',b'\1'+delta.to_bytes(8,'little')+b'\0')
   status=int(delta+1>=2**25)
   assert word[-1]==status
   if status:reach_rejected+=1
   else:
    assert int.from_bytes(word[1:5],'little')==0x14000000|((delta+1)&0x3ffffff)
    assert int.from_bytes(word[5:9],'little')==0x14000000|((1-delta)&0x3ffffff)
  mathcases+=1
 for count in (0,1,7,255,65535,2**24,2**32,2**60,2**62,2**64-1):
  added=native('android_compact_elf_word_plus7_52',count.to_bytes(8,'little'))
  bytecount=native('android_compact_elf_words_to_bytes52',added[:8])
  hdr=native('android_compact_elf_header52',bytecount[:8])
  assert len(added)==9 and len(bytecount)==9 and len(hdr)==261
  assert added[:8]==((count+7)%(2**64)).to_bytes(8,'little')
  assert bytecount[:8]==(((count+7)*4)%(2**64)).to_bytes(8,'little')
  assert added[-1]==int(count+7>=2**64)
  if added[-1]==0:assert bytecount[-1]==int((count+7)*4>=2**64)
  assert hdr[208:216]==bytecount[:8]==hdr[216:224]
 cases=[(b'',b''),(b'+.',b''),(b'+[->+<]>.',b''),(b',.,.',b'\0\xff'),
  (b'+++[>++[>+<-]<-]>>.',b''),(b'<',b''),(b'>+<+.',b''),
  (b'['*1025+b']'*1025,b''),(b'+'*3020+b'[->+<]>.',b''),
  (b'+'*7500+b'[--]',b'')]
 rng=random.Random(52)
 for _ in range(45):
  prefix=b''.join(rng.choice((b'+',b'-',b'>',b'<',b'.',b',',b'ignored')) for _ in range(rng.randrange(1,50)))
  cases.append((prefix+b'[-][[]]',bytes(rng.randrange(256) for _ in range(17))))
 passed=0;simulated=0;traps=0;pair_count=0;max_commands=0
 with tempfile.TemporaryDirectory(prefix='bfc52-verify-') as td:
  d=Path(td);source=d/'input.bf';elf=d/'output.elf'
  for text,input_data in cases:
   source.write_bytes(text);info=compile_elf(source,elf)
   image=elf.read_bytes()
   assert info['elf_bytes']==len(image)
   assert struct.unpack_from('<Q',image,208)[0]==len(image)-0x20000
   assert struct.unpack_from('<Q',image,216)[0]==len(image)-0x20000
   subprocess.run(['readelf','-Wl',str(elf)],check=True,stdout=subprocess.DEVNULL)
   try:expected,_=execute(text,input_data,max_steps=500000);exit_code=0
   except IndexError:expected=None;exit_code=2;traps+=1
   for bias in (0,0x40000000):
    obs,code,_=emulate(image,bias,tape_base_rva=0x4000,code_start_rva=0x20000,
                        code_limit=len(image),input_bytes=input_data,max_steps=500000)
    assert (code==exit_code and (expected is None or obs==expected)),(text[:50],bias,obs,code,expected,exit_code)
    simulated+=1
   pair_count+=info['bracket_pairs_relocated'];max_commands=max(max_commands,info['bf_native_instructions']);passed+=1
  failures=[(b'[',{}),(b']',{}),(b'[]',{'max_pairs':0}),(b'++++',{'max_native_bytes':8})]
  for text,kw in failures:
   source.write_bytes(text);elf.write_bytes(b'UNCHANGED')
   try:compile_elf(source,elf,**kw)
   except (ValueError,RuntimeError):pass
   else:raise AssertionError('invalid request was accepted')
   assert elf.read_bytes()==b'UNCHANGED'
 report={'iteration':52,'classification':'LUX_HOSTED_BF_OWNED_DYNAMIC_COMPACT_AARCH64_ELF_SIMULATED',
  'bf_stages':details,'program_cases_passed':passed,'simulator_runs_at_two_load_biases':simulated,
  'pointer_traps_verified':traps,'bracket_pairs_verified':pair_count,
  'largest_small_source_commands':max_commands,'atomic_output_rejections':len(failures),
  'wide_position_and_branch_arithmetic_cases':mathcases,'branch_reach_rejections':reach_rejected,
  'readelf_structure_passed':True,'android_loader_executed':False,'real_application_policies_compiled':False,
  'elapsed_seconds':round(time.monotonic()-begin,2)}
 (ROOT/'evidence/iteration52_android_dynamic_elf_tests.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
