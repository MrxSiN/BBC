#!/usr/bin/env python3
"""Linux-hosted BF-owned AArch64 compact loop relocation, not an ELF writer.

The host frames opaque BF-stage input/output and performs generic indexed
4-byte storage. BF stages own 64-bit offset subtraction, branch arithmetic,
reach checks, and +2 native-word relocation indices. No Python branch encoder
is called in the production pipeline. The original output is never replaced
unless all stages and every patch pass validation.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,struct,subprocess,tempfile,zipfile
from pathlib import Path
try:from .android_compact_reloc_stream import make_bundle
except ImportError:from android_compact_reloc_stream import make_bundle
ROOT=Path(__file__).resolve().parents[1]
SPAN=ROOT/'build/android_compact_span64_52_x86_64_linux.elf'
BRANCH=ROOT/'build/android_compact_branch_words52_x86_64_linux.elf'
INDEX=ROOT/'build/android_compact_patch_indices52_x86_64_linux.elf'
PLACEHOLDER=bytes.fromhex('00000014')

def exact(f,n):
 b=f.read(n)
 if len(b)!=n:raise ValueError('incomplete Brainfuck relocation record')
 return b

def run_bf_stage(stage,stdin,stdout):
 stdin.seek(0)
 p=subprocess.run([str(stage)],stdin=stdin,stdout=stdout,stderr=subprocess.PIPE,timeout=240)
 if p.returncode!=0:raise RuntimeError(f'BF relocation stage failed {stage.name}: {p.stderr[:200]!r}')
 stdout.flush();stdout.seek(0)

def check_framed(file,payload,tag=b'\1'):
 file.seek(0,os.SEEK_END);n=file.tell()
 if n<2 or (n-2)%(payload+1):raise ValueError('BF relocation output size mismatch')
 file.seek(n-2)
 if file.read(2)!=b'\0\0':raise ValueError('BF relocation stage rejected source or span')
 file.seek(0)
 for _ in range((n-2)//(payload+1)):
  if exact(file,1)!=tag:raise ValueError('BF relocation stage record tag mismatch')
  yield exact(file,payload)

def compile_relocated(source:Path,target:Path,*,max_native_bytes=None,max_pairs=None,
                       span_stage=SPAN,branch_stage=BRANCH,index_stage=INDEX):
 target.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='.bf52-reloc-',dir=target.parent) as folder:
  d=Path(folder);bundle=d/'unrelocated.zip';code=d/'code.bin';pairs=d/'pairs.bin'
  srcinfo=make_bundle(source,bundle,max_native_bytes=max_native_bytes,max_pairs=max_pairs)
  with zipfile.ZipFile(bundle) as archive:
   with archive.open('code.bin') as src,code.open('wb') as dest:shutil.copyfileobj(src,dest)
   with archive.open('pairs.bin') as src,pairs.open('wb') as dest:shutil.copyfileobj(src,dest)
  count=srcinfo['matched_pairs']
  # All input streams are opaque bytes; only BF stages compute native offsets.
  with tempfile.TemporaryFile('w+b') as wirespan, tempfile.TemporaryFile('w+b') as span:
   with pairs.open('rb') as f:
    for _ in range(count):
     if exact(f,1)!=b']':raise ValueError('pair record tag mismatch')
     wirespan.write(b'\1'+exact(f,16))
    if f.read(1):raise ValueError('trailing pair records')
   wirespan.write(b'\0')
   run_bf_stage(span_stage,wirespan,span)
   with tempfile.TemporaryFile('w+b') as wirebranch, tempfile.TemporaryFile('w+b') as branches:
    for record in check_framed(span,24):wirebranch.write(b'\1'+record[16:24])
    wirebranch.write(b'\0')
    run_bf_stage(branch_stage,wirebranch,branches)
    with tempfile.TemporaryFile('w+b') as wireindex, tempfile.TemporaryFile('w+b') as patched:
     pair_records=check_framed(span,24)
     branch_records=check_framed(branches,8)
     for pair_data,branch_data in zip(pair_records,branch_records,strict=True):
      wireindex.write(b'\1'+pair_data[:16]+branch_data)
     wireindex.write(b'\0')
     run_bf_stage(index_stage,wireindex,patched)
     relocs=d/'relocations.bin';patch_count=0;locations=set()
     code_len=code.stat().st_size
     with code.open('r+b') as f,relocs.open('wb') as log:
      for rec in check_framed(patched,12,tag=b'P'):
       position=int.from_bytes(rec[:8],'little')
       if position >= code_len//4:raise ValueError('patch outside generated native image')
       if position in locations:raise ValueError('duplicate native word patch location')
       locations.add(position)
       # This is an opaque index into fixed-width 4-byte machine words.
       f.seek(position*4)
       if exact(f,4)!=PLACEHOLDER:raise ValueError('patch overwrote a non-placeholder instruction')
       f.seek(position*4);f.write(rec[8:12]);log.write(b'P'+rec)
       patch_count+=1
      f.flush();os.fsync(f.fileno())
     if patch_count!=2*count:raise ValueError('incomplete branch relocation stream')
  sha=lambda x:hashlib.file_digest(x.open('rb'),'sha256').hexdigest()
  manifest={'iteration':52,'format':'BF_AARCH64_COMPACT_RELOCATED_RAW_CODE_V1',
   'artifact_kind':'RELOCATED_RAW_CODE_NOT_ANDROID_ELF',
   'source_sha256':srcinfo['raw_source_sha256'],
   'source_bytes':srcinfo['raw_source_bytes'],
   'native_instruction_records':srcinfo['native_instruction_records'],
   'native_code_bytes':srcinfo['native_code_bytes'],
   'native_word_count':srcinfo['native_word_count'],
   'bracket_pairs':count,'maximum_nesting_depth':srcinfo['maximum_observed_depth'],
   'patches_applied':patch_count,'code_sha256':sha(code),'relocations_sha256':sha(relocs),
   'native_word_encoding':'STANDARD_BRAINFUCK',
   'native_patch_positions':'STANDARD_BRAINFUCK',
   'bracket_pairing':'STANDARD_BRAINFUCK_FILE_BACKED_STACK',
   'host':'OPAQUE_4_BYTE_WORD_INDEXED_FILE_STORAGE_AND_STREAM_TRANSPORT',
   'direct_branch_reach_enforced':True,'long_branch_veneer':False,
   'elf_generated':False,'device_executed':False,
   'original_android_policy_compiled':False}
  (d/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  dest=d/'final.zip'
  with zipfile.ZipFile(dest,'w',compression=zipfile.ZIP_STORED) as z:
   for item in (code,pairs,relocs,d/'manifest.json'):z.write(item,item.name)
  dest.replace(target)
  return manifest

def main():
 parser=argparse.ArgumentParser(description='BF-owned compact AArch64 loop relocation; raw code, not ELF')
 parser.add_argument('source',type=Path);parser.add_argument('-o','--output',type=Path,required=True)
 parser.add_argument('--max-native-bytes',type=int);parser.add_argument('--max-pairs',type=int)
 a=parser.parse_args();print(json.dumps(compile_relocated(a.source,a.output,max_native_bytes=a.max_native_bytes,max_pairs=a.max_pairs),indent=2))
if __name__=='__main__':main()
