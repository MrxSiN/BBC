#!/usr/bin/env python3
"""Emit a BF-owned AArch64 ELF DSO exporting the versioned BFP1 entry.

Only raw file assembly/transport is performed by Python. The generated ELF
header, exported symbol, dynamic table and code all originate from executed
standard-Brainfuck stages. This is NOT a JNI library on its own: an Android
host adapter must dlopen the policy DSO and resolve bfc_call_v1.
"""
import argparse
import json
from pathlib import Path
from .android_dynamic_callable58 import compile_callable

def compile_shared(source:Path, output:Path, *,max_code_bytes:int|None=None,
                   max_pairs:int|None=None, timeout:int=300)->dict:
    return compile_callable(source,output,max_code_bytes=max_code_bytes,
                            max_pairs=max_pairs,timeout=timeout,shared_library=True)

def main():
    p=argparse.ArgumentParser(description='BF-authored AArch64 callable ELF shared object')
    p.add_argument('source',type=Path)
    p.add_argument('-o','--output',required=True,type=Path)
    p.add_argument('--max-code-bytes',type=int)
    p.add_argument('--max-pairs',type=int)
    a=p.parse_args()
    print(json.dumps(compile_shared(a.source,a.output,max_code_bytes=a.max_code_bytes,
                                    max_pairs=a.max_pairs),indent=2))

if __name__=='__main__':main()
