#!/usr/bin/env python3
"""Resource-scaled Android AArch64 freestanding ELF from standard-BF stages.

BF produces source code bytes, 64-bit word offsets, loop pairs, branch words,
word-index positions and ELF segment metadata/startup. Python is the generic
file/record transport. This experimental PIE is NOT device-loader verified.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,struct,subprocess,tempfile,zipfile
from pathlib import Path
try:from .android_compact_far_relocated53 import compile_relocated
except ImportError:from android_compact_far_relocated53 import compile_relocated
ROOT=Path(__file__).resolve().parents[1]
LENGTH=ROOT/'build/android_compact_elf_word_plus7_52_x86_64_linux.elf'
SHIFT=ROOT/'build/android_compact_elf_words_to_bytes52_x86_64_linux.elf'
HEADER=ROOT/'build/android_compact_elf_header52_x86_64_linux.elf'
CODE_FILE_OFFSET=0x20000
HEADER_SIZE=232
START_SIZE=16
EXIT_SIZE=12

def bf_size_stage(exe,raw,expected_bytes):
 p=subprocess.run([str(exe)],input=raw,capture_output=True,timeout=60,check=True)
 if len(p.stdout)!=expected_bytes+1 or p.stdout[-1]!=0:
  raise ValueError(f'Brainfuck ELF layout stage rejected input: {exe.name}')
 return p.stdout[:-1]

def compile_elf(source:Path,destination:Path,*,max_native_bytes=None,max_pairs=None):
 destination.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='.bf53-elf-',dir=destination.parent) as folder:
  d=Path(folder);raw_bundle=d/'relocated.zip';code=d/'code.bin'
  meta=compile_relocated(source,raw_bundle,max_native_bytes=max_native_bytes,max_pairs=max_pairs)
  with zipfile.ZipFile(raw_bundle) as archive:
   with archive.open('code.bin') as s,code.open('wb') as t:shutil.copyfileobj(s,t)
  # Native code word count originates from the 64-bit BF ledger. Only framing here.
  bf_words=int(meta['native_word_count']).to_bytes(8,'little')
  bf_words_with_start_exit=bf_size_stage(LENGTH,bf_words,8)
  bf_code_segment_size=bf_size_stage(SHIFT,bf_words_with_start_exit,8)
  elf_parts=bf_size_stage(HEADER,bf_code_segment_size,HEADER_SIZE+START_SIZE+EXIT_SIZE)
  hdr=elf_parts[:HEADER_SIZE];start=elf_parts[HEADER_SIZE:HEADER_SIZE+START_SIZE]
  finish=elf_parts[HEADER_SIZE+START_SIZE:]
  if hdr[:4]!=b'\x7fELF' or len(finish)!=EXIT_SIZE:raise ValueError('BF output not an ELF header')
  if struct.unpack_from('<Q',hdr,208)[0]!=code.stat().st_size+START_SIZE+EXIT_SIZE:
   raise ValueError('BF ELF size and BF native code output disagree')
  # Atomically stream the BF-generated parts; padding is fixed-layout raw zero data.
  image=d/'image.elf'
  with image.open('wb') as f:
   f.write(hdr);f.write(bytes(CODE_FILE_OFFSET-len(hdr)))
   f.write(start)
   with code.open('rb') as c:shutil.copyfileobj(c,f,1<<20)
   f.write(finish);f.flush();os.fsync(f.fileno())
  image.chmod(0o755)
  digest=hashlib.sha256()
  with image.open('rb') as f:
   while chunk:=f.read(1<<20):digest.update(chunk)
  result={'iteration':53,'format':'BF_AARCH64_DYNAMIC_FREESTANDING_PIE_FAR_JUMPS_V1',
   'source_bytes':meta['source_bytes'],'source_sha256':meta['source_sha256'],
   'bf_native_instructions':meta['native_instruction_records'],
   'native_compact_code_bytes':meta['native_code_bytes'],
   'bracket_pairs_relocated':meta['bracket_pairs'],
   'maximum_nesting_depth':meta['maximum_nesting_depth'],
   'native_loop_patches':meta['patches_applied'],
   'elf_bytes':image.stat().st_size,'elf_sha256':digest.hexdigest(),
   'elf_type':'ET_DYN_FREESTANDING_AARCH64',
   'code_file_offset':CODE_FILE_OFFSET,'tape_virtual_rva':0x4000,
   'code_virtual_rva':0x20000,'tape_cells':65536,
   'fixed_source_command_limit_in_new_pipeline':None,
   'direct_AARCH64_branch_reach_limit':False,
   'branch_reach':'SIGNED64_RELATIVE_WORD_DISPLACEMENT_PC_INDEPENDENT',
   'source_word_offset_encoder':'STANDARD_BRAINFUCK',
   'loop_pairing':'STANDARD_BRAINFUCK_FILE_BACKED',
   'branch_encoding':'STANDARD_BRAINFUCK',
   'patch_positions':'STANDARD_BRAINFUCK',
   'elf_layout':'STANDARD_BRAINFUCK_STAGES',
   'host_role':'OPAQUE_FILE_FRAMES_WORD_PATCH_STORAGE_AND_FIXED_GAP_PADDING',
   'android_loader_executed':False,
   'original_app_policies_compiled':False,'android_native_selfhosted':False}
  image.replace(destination)
  return result

def main():
 p=argparse.ArgumentParser(description='Experimental dynamically growing BF-owned AArch64 far-jump ELF compiler')
 p.add_argument('source',type=Path);p.add_argument('-o','--output',type=Path,required=True)
 p.add_argument('--max-native-bytes',type=int);p.add_argument('--max-pairs',type=int)
 a=p.parse_args()
 print(json.dumps(compile_elf(a.source,a.output,max_native_bytes=a.max_native_bytes,max_pairs=a.max_pairs),indent=2))
if __name__=='__main__':main()
