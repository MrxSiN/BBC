#!/usr/bin/env python3
"""End-to-end verification of BF-owned compact code, BF 64-bit offset ledger,
and BF dynamic loop pairing. It explicitly does not verify ELF/relocation words.
"""
from __future__ import annotations
import hashlib,json,os,random,struct,subprocess,sys,tempfile,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tools')]
from transport import encode_source,extract_artifact
from source_check import check_source
from android_compact_reloc_stream import make_bundle

CODE_SRC=ROOT/'experiments/android_streaming_compact_all8.bf'
CODE_ELF=ROOT/'build/android_streaming_compact_all8_x86_64_linux.elf'
LEDGER_SRC=ROOT/'experiments/android_compact_native_offset_ledger51.bf'
LEDGER_ELF=ROOT/'build/android_compact_native_offset_ledger51_x86_64_linux.elf'
OLD_EMITTER=ROOT/'build/android_wide_slot_emitter_x86_64_linux.elf'
OPS=b'+-><.,[]'
NOP=bytes.fromhex('1f2003d5')
WORD_LENGTHS={ord('+'):3,ord('-'):3,ord('>'):7,ord('<'):7,ord('.'):10,ord(','):12,ord('['):3,ord(']'):3}

def digest(data):return hashlib.sha256(data).hexdigest()

def reference(source,templates):
    words=0;code=bytearray();stack=[];pairs=[];count=0;peak=0
    for c in source:
        if c not in OPS:continue
        if c==91:
            stack.append(words);peak=max(peak,len(stack))
        elif c==93:
            if not stack:return None
            pairs.append((stack.pop(),words))
        code.extend(templates[c]);words+=WORD_LENGTHS[c];count+=1
    if stack:return None
    return bytes(code),words,pairs,count,peak

def main():
    start=time.monotonic();compiler=ROOT/'build/compiler_x86_64_linux.elf'
    stages={}
    for src,elf in ((CODE_SRC,CODE_ELF),(LEDGER_SRC,LEDGER_ELF)):
        raw=src.read_bytes();cmd=check_source(raw)
        assert len(cmd)<16128
        for input_source in (raw,cmd):
            p=subprocess.run([str(compiler)],input=encode_source(input_source),
                            capture_output=True,check=True,timeout=90)
            assert extract_artifact(p.stdout)==elf.read_bytes()
        stages[str(src.relative_to(ROOT))]={'bf_commands':len(cmd),
          'source_sha256':digest(raw),'linux_native_sha256':digest(elf.read_bytes()),
          'linux_native_bytes':elf.stat().st_size}
    templates={}
    for c in OPS:
        p=subprocess.run([str(OLD_EMITTER)],input=bytes((c,0)),capture_output=True,check=True)
        t=p.stdout[:48]
        while t.endswith(NOP):t=t[:-4]
        assert len(t)==WORD_LENGTHS[c]*4
        templates[c]=t
    rng=random.Random(2026101351)
    cases=[b'',b'.',b'+',b'[][]',b'+[->+<]>.',b'++[[--]<>]',b'abc\0[]xyz',
           b'['*320+b']'*320,b'['*1025+b']'*1025,
           b'+'*3021+b'[--]'+b'>'*130,
           b'['+b'+'*7500+b']']
    for _ in range(75):
        depth=0;buf=bytearray()
        for _ in range(rng.randrange(1,210)):
            c=rng.choice(OPS+b' noise\x00\xff')
            if c==93 and not depth:c=ord('+')
            if c==91:depth+=1
            elif c==93:depth-=1
            buf.append(c)
        buf.extend(b']'*depth)
        cases.append(bytes(buf))
    accepted=0;max_depth=0;max_commands=0;total_pairs=0
    with tempfile.TemporaryDirectory(prefix='bf51-reloc-') as t:
        d=Path(t);source=d/'source.bf';bundle=d/'reloc.zip'
        for case in cases:
            expected=reference(case,templates)
            assert expected is not None
            source.write_bytes(case)
            metrics=make_bundle(source,bundle)
            with zipfile.ZipFile(bundle) as archive:
                assert archive.testzip() is None
                code=archive.read('code.bin');pairs=archive.read('pairs.bin')
                stored=json.loads(archive.read('manifest.json'))
            expected_code,words,matches,count,depth=expected
            assert code==expected_code,(case[:100],code[:50],expected_code[:50])
            assert pairs==b''.join(b']'+struct.pack('<QQ',a,b) for a,b in matches)
            assert metrics==stored
            assert metrics['native_instruction_records']==count
            assert metrics['native_word_count']==words
            assert metrics['maximum_observed_depth']==depth
            assert metrics['matched_pairs']==len(matches)
            assert metrics['native_code_sha256']==digest(code)
            accepted+=1;max_depth=max(max_depth,depth);max_commands=max(max_commands,count);total_pairs+=len(matches)
        # Atomic bundle replacement: malformed brackets and caller quotas.
        invalids=[(b'[',None,None),(b']',None,None),(b'[[+]',None,None),
                  (b'[]',None,0),(b'++++',47,None)]
        fail_count=0
        for case,max_bytes,max_pairs in invalids:
            source.write_bytes(case);bundle.write_bytes(b'PRESERVE_EXISTING_ARCHIVE')
            try:make_bundle(source,bundle,max_native_bytes=max_bytes,max_pairs=max_pairs)
            except ValueError:pass
            else:raise AssertionError('bad input was accepted')
            assert bundle.read_bytes()==b'PRESERVE_EXISTING_ARCHIVE'
            fail_count+=1
        # Native BF stage runs vs independent seed interpreters, for sample record streams.
        seed_matches=0
        for src,exe,input_raw in ((CODE_SRC,CODE_ELF,b'++[->+<]>.\0'),
                                  (LEDGER_SRC,LEDGER_ELF,b'[->+<]>.\0')):
            wire=b''.join(b'\1'+bytes((c,)) for c in input_raw[:-1])+b'\0'
            actual=subprocess.run([str(exe)],input=wire,capture_output=True,check=True,timeout=10).stdout
            for name in ('seed_interpreter.c','seed_interpreter_alt.c'):
                binary=d/(Path(name).stem+'_51')
                subprocess.run(['cc','-O2','-std=c11',str(ROOT/'bootstrap'/name),'-o',str(binary)],
                               check=True,capture_output=True)
                output=subprocess.run([str(binary),str(src),'30000000'],input=wire,
                                      capture_output=True,check=True,timeout=30).stdout
                assert output==actual
                seed_matches+=1
    evidence={'iteration':51,
        'classification':'BF_OWNED_COMPACT_ALL8_UNRELOCATED_CODE_PLUS_BF_64BIT_WORD_OFFSET_LEDGER_AND_DYNAMIC_PAIRS',
        'stage_integrity':stages,'total_accepted_cases':accepted,
        'maximum_source_commands_tested':max_commands,'maximum_nesting_depth_tested':max_depth,
        'total_bracket_pairs_checked':total_pairs,'expected_atomic_rejections':fail_count,
        'independent_seed_stage_matches':seed_matches,
        'native_slots_compact':True,'all_eight_brainfuck_instructions_recognized':True,
        'native_word_offsets_64bit':True,'dynamic_nested_pair_storage':True,
        'native_branch_words_patched':False,'dynamic_loadable_elf_generated':False,
        'full_android_native_selfhosting':False,'original_eleven_app_policies_compiled':False,
        'android_device_executed':False,'elapsed_seconds':round(time.monotonic()-start,3)}
    (ROOT/'evidence/iteration51_android_compact_relocation_bundle.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(json.dumps(evidence,indent=2))

if __name__=='__main__':main()
