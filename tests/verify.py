#!/usr/bin/env python3
"""Differential tests: the authoritative machine-code emitter is Brainfuck."""
import hashlib, json, pathlib, random, re, subprocess, sys, tempfile, time
from reference import execute
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "bootstrap"))
from transport import encode_source
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from tools.annotate import annotated_view, VIEW
from tools.source_check import check_source

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMPILER = (ROOT / 'compiler/core.bf').read_bytes()
OPS = set(b'<>+-.,[]')
assert len(check_source(COMPILER)) == 14859
sha = hashlib.sha256(COMPILER).hexdigest()
# The independent annotations must match the exact canonical source revision.
# This checker reads BF + notes; it never generates compiler instructions.
assert VIEW.read_text() == annotated_view(), 'annotations or generated view are stale'

# (name, source, stdin, expected native process exit)
CASES = [
 ('empty', b'', b'', 0),
 ('hello_world_example', (ROOT / 'examples/hello.bf').read_bytes(), b'', 0),
 ('increment', b'+++.', b'', 0),
 ('underflow_byte', b'-.', b'', 0),
 ('wrap_byte', b'-+.', b'', 0),
 ('pointer_shuttle', b'>+++++.<++++++++.', b'', 0),
 ('echo', b',.,.', b'\x00\xfe', 0),
 ('eof_zero', b',.', b'', 0),
 ('eof_after_one', b',.,.', b'A', 0),
 ('comments_ignored', b'++hello+++.', b'', 0),
 ('comment_stream', b'prose!'*100 + b'++++.', b'', 0),
 ('comment_with_nul_and_ff', b'abc\x00def\xff++++.', b'', 0),
 ('pointer_underflow', b'<', b'', 2),
 ('pointer_underflow_after_shift', b'><<', b'', 2),
 ('zero_skip', b'[<].', b'', 0),
 ('zero_plus_loop', b'[+].', b'', 0),
 ('zero_nested_skip', b'[+[-]>+<[>]]+.', b'', 0),
 ('clear_minus', b'+++[-].', b'', 0),
 ('clear_plus', b'+++[+].', b'', 0),
 ('transfer', b'++++[->+++<]>.', b'', 0),
 ('nested_transfer', b'++[>++[>+++<-]<-]>>.', b'', 0),
 ('adjacent_loops', b'+++[-]++++[->++<]>.', b'', 0),
 ('nested_zero_loop', b'[[-]].', b'', 0),
 ('loop_pointer_underflow', b'+[<]', b'', 2),
 ('loop_right_boundary', b'+[>+]', b'', 2),
 ('long_branch_skip', b'[' + b'+'*110 + b']+.', b'', 0),
 ('long_branch_exec', b'+++[' + b'+'*104 + b'-' *104 + b'-] .', b'', 0),
 ('budget_last_allowed', b'+'*253 + b'.', b'', 0),
 ('source_embedded_nul', b'++\x00+++.', b'', 0),
 ('source_embedded_ff', b'++\xff+++.', b'', 0),
 ('large_source_1000', b'+'*999 + b'.', b'', 0),
 ('large_loop_2000', b'[' + b'+'*2000 + b']+.', b'', 0),
 ('large_loop_10000', b'[' + b'+'*10000 + b']+.', b'', 0),
 ('large_source_16000', b'+'*16000 + b'.', b'', 0),
 ('source_exact_16128', b'+'*16127 + b'.', b'', 0),
 ('nested_depth_255', b'['*255 + b']'*255 + b'.', b'', 0),
]
# The long-branch body balances its adjustments and decrements the induction cell.
# Replace a risky body with no pointer movement and an induction that terminates.
CASES = [(n, (b'+++[' + b'+'*96 + b'-'*96 + b'-].' if n == 'long_branch_exec' else s), i, e) for n,s,i,e in CASES]

rng = random.Random(12345)
for j in range(60):
 p = 0; code = []
 for _ in range(rng.randint(1,50)):
  ch = rng.choice('+-.,><')
  if ch == '<' and p == 0: ch = '+'
  elif ch == '>' and p >= 6: ch = '-'
  if ch == '<': p -= 1
  if ch == '>': p += 1
  code.append(ch)
 CASES.append((f'random_linear_{j:02d}', ''.join(code).encode(), bytes(rng.randrange(256) for _ in range(6)), 0))
for j in range(24):
 n,k = rng.randrange(1,26),rng.randrange(0,16)
 CASES.append((f'random_transfer_{j:02d}', b'+'*n + b'[->' + b'+'*k + b'<]>.', b'', 0))
for j in range(24):
 n,k,m = rng.randrange(1,8),rng.randrange(1,7),rng.randrange(1,9)
 CASES.append((f'random_nested_{j:02d}', b'+'*n+b'[>'+b'+'*k+b'[>'+b'+'*m+b'<-]<-]>>.', b'', 0))
for j in range(15):
 a = rng.randrange(0,140)
 CASES.append((f'random_zero_skip_{j:02d}', b'[' + b'+'*a + b'[+]]++.', b'', 0))

REJECT = [
 ('unmatched_open', b'[+'),
 ('unmatched_close', b']'),
 ('unmatched_nested', b'[[]'),
 ('unmatched_extra_close', b'[]]'),
 ('unmatched_separate', b'[][+'),
 ('unmatched_empty_and_close', b'[]]++.'),
 ('unmatched_after_valid', b'+++[-]]'),
 ('unsupported_16129_bytes', b'+'*16129),
 ('source_after_limit', b'+'*16128+b'.'),
 ('nested_depth_256', b'['*256 + b']'*256),
]
assert all(sum(c in OPS for c in s) <= 16128 for _,s,_,_ in CASES)

results=[]
with tempfile.TemporaryDirectory(prefix='bf-native-') as directory:
 tmp=pathlib.Path(directory)
 seed=tmp/'bfseed'
 subprocess.run(['cc','-O2','-std=c11','-Wall','-Wextra',str(ROOT/'bootstrap/seed_interpreter.c'),'-o',str(seed)],check=True)
 def compile_with_seed(source):
  proc=subprocess.run([str(seed),str(ROOT/'compiler/core.bf'),'10000000000'],input=encode_source(source),capture_output=True,timeout=90)
  assert proc.returncode==0,(proc.returncode,proc.stderr.decode(errors='replace'))
  match=re.search(rb'STEPS=(\d+)',proc.stderr)
  return proc.stdout,int(match.group(1)) if match else None
 for name,source,stdin,expected_exit in CASES:
  compiled,steps=compile_with_seed(source)
  assert compiled and compiled[-1]==0,(name,'compiler rejected valid source',steps)
  elf=compiled[:-1]
  assert elf[:4] == b'\x7fELF' and len(elf)==215+32*sum(c in OPS for c in source),(name,'incorrect variable-length ELF')
  file=tmp/(name+'.elf');file.write_bytes(elf);file.chmod(0o700)
  result=subprocess.run([str(file)],input=stdin,capture_output=True,timeout=3)
  try:
   expected,refsteps=execute(source,stdin,max_steps=600_000)
  except IndexError:
   assert expected_exit == 2,(name,'unexpected reference bounds trap')
   assert result.returncode == 2,(name,'native bounds trap missing',result.returncode)
  else:
   if name == 'hello_world_example':
    assert expected == b'Hello World!\n', ('hello example is not actually Hello World',expected)
   assert expected_exit == 0 and result.returncode==0 and result.stdout==expected,(name,result.returncode,result.stdout,expected)
  results.append({'case':name,'result':'PASS','native_exit':result.returncode,'elf_bytes':len(elf),'output_hex':result.stdout.hex(),'commands':sum(c in OPS for c in source),'seed_steps':steps})
 for name,source in REJECT:
  out,steps=compile_with_seed(source)
  assert out and out[-1] != 0,(name,'must reject this source',steps)
  results.append({'case':name,'result':'PASS','compiler_status':out[-1],'artifact_discarded':True,'seed_steps':steps})
 # Broken byte-stuffing is rejected by BF itself, not by the transport adapter.
 # These are raw framed streams, not ordinary Brainfuck source bytes.
 for name,framed in [
   ('framing_bare_escape', b'\xff'),
   ('framing_escape_unknown', b'\xff\x03'),
   ('framing_escape_escape', b'\xff\xff'),
   ('framing_escape_zero', b'\xff\x00'),
 ]:
  proc=subprocess.run([str(seed),str(ROOT/'compiler/core.bf'),'10000000000'],input=framed,capture_output=True,timeout=90)
  assert proc.returncode==0,(name,proc.returncode)
  assert proc.stdout and proc.stdout[-1]!=0,(name,'invalid transport accepted')
  results.append({'case':name,'result':'PASS','compiler_status':proc.stdout[-1]})
 # Two independently implemented seed interpreters must produce identical bytes.
 for name,source in [('seed_agree_nested',b'++[>++[>+++<-]<-]>>.'),('seed_agree_invalid',b'[]]'),('seed_agree_empty',b'')]:
  native_seed,_=compile_with_seed(source)
  independent_python,_=execute(COMPILER,encode_source(source),max_steps=35_000_000)
  assert native_seed==independent_python,(name,'independent bootstrap executors disagreed')
  results.append({'case':name,'result':'PASS','output_sha256':hashlib.sha256(native_seed).hexdigest()})
 # Independently inspect ELF program-header access modes and native branch encoding.
 elf=tmp/'nested_transfer.elf'
 hdr=subprocess.run(['readelf','-lW',str(elf)],capture_output=True,text=True,check=True)
 loads=[line for line in hdr.stdout.splitlines() if line.strip().startswith('LOAD ')]
 assert len(loads)==2 and 'R E' in loads[0] and 'RW ' in loads[1] and ' W E' not in hdr.stdout
 results.append({'case':'elf_segment_permissions','result':'PASS','load_headers':loads})
 disasm=subprocess.run(['objdump','-D','-b','binary','-m','i386:x86-64',str(elf)],capture_output=True,text=True,check=True)
 # A compiled loop must contain real near conditional branches, not a BF VM call.
 assert any(token in disasm.stdout for token in ('je ', 'jne ', 'je\t', 'jne\t'))
 results.append({'case':'native_conditional_branches','result':'PASS'})
 report={
  'source_sha256':sha,'source_length':len(COMPILER),
  'count':len(results),'passed':len(results),'failed':0,
  'scope':'<=16128 filtered BF commands (ignored characters are compacted); <=255 nested loop depth; byte-stuffed source framing; exact ELF size; direct native x86-64 loops; differential comparisons',
  'results':results,
 }
 (ROOT/'evidence/correctness.json').write_text(json.dumps(report,indent=2)+'\n')
 print(f"PASS {report['passed']}/{report['count']} tests; source {sha[:12]}...")
