#!/usr/bin/env python3
"""BF-owned, file-backed AArch64 callable compiler, including nested loops.

Native templates, source filtering, offset arithmetic, bracket pairing, wide
branch displacements, ELF headers and prologue/epilogue code all originate from
executed standard Brainfuck stages. Python supplies transactional file storage,
byte framing, stage execution and generic opaque indexed patch transport only.
This is an ELF callable image, not a JNI-exporting Android .so.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import subprocess
import zipfile

try:
    from .android_compact_far_relocated53 import compile_relocated
    from .android_dynamic_callable57 import ROOT
except ImportError:
    from android_compact_far_relocated53 import compile_relocated
    from android_dynamic_callable57 import ROOT

STAGES=ROOT/'build'/'iteration58_dynamic'
SLOT=STAGES/'android_callable_slots58.elf'
LEDGER=STAGES/'android_callable_ledger58.elf'


def _native_stage(name: str, incoming: Path, outgoing: Path, timeout: int) -> None:
    """Generic file-backed execution of an independently self-hosted BF stage."""
    native=STAGES/(name+'.elf')
    if not native.is_file():
        raise FileNotFoundError(f'missing compiled BF stage: {native}')
    with incoming.open('rb') as src, outgoing.open('w+b') as dest:
        subprocess.run([str(native)],stdin=src,stdout=dest,
                       stderr=subprocess.PIPE,check=True,timeout=timeout)
        dest.flush()


def compile_callable(source:Path, output:Path, *,max_code_bytes:int|None=None,
                     max_pairs:int|None=None,timeout:int=300,
                     shared_library:bool=False)->dict:
    source=Path(source);output=Path(output)
    if max_code_bytes is not None and max_code_bytes<68:
        raise ValueError('caller code quota cannot hold callable prologue and epilogue')
    if max_pairs is not None and max_pairs<0:
        raise ValueError('negative caller bracket pair quota')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.callable58-',dir=output.parent) as folder:
        d=Path(folder)
        raw_bundle=d/'relocated.zip'
        result=compile_relocated(source,raw_bundle,
                   max_native_bytes=None if max_code_bytes is None else max_code_bytes-68,
                   max_pairs=max_pairs,code_stage=SLOT,ledger_stage=LEDGER)
        # BF generates the ABI entry and return code even when source is empty.
        # These are fixed-size transport fields; Python does not generate words.
        empty=d/'empty.frame';empty.write_bytes(b'\0')
        wrapper=d/'wrapper.bin'
        _native_stage('android_callable_linear57',empty,wrapper,timeout)
        with wrapper.open('rb') as w:
            wrapper_data=w.read()
        if len(wrapper_data)!=69 or wrapper_data[-1]!=0:
            raise ValueError('BF callable entry/return stage rejected empty source')
        code_bytes=result['native_code_bytes']+68
        if max_code_bytes is not None and code_bytes>max_code_bytes:
            raise ValueError('BF emitted code exceeds caller quota')
        if code_bytes>(1<<64)-1-(1024 if shared_library else 128):
            raise ValueError('ELF 64-bit total byte length overflow')
        length=d/'length.bin';length.write_bytes(code_bytes.to_bytes(8,'little'))
        header=d/'header.bin'
        _native_stage('android_callable_dso_header59' if shared_library else 'android_callable_header57',
                      length,header,timeout)
        h=header.read_bytes()
        header_size=1024 if shared_library else 128
        marker_offset=0x180 if shared_library else 120
        if (len(h)!=header_size+1 or h[-1] or h[:4]!=b'\x7fELF'
            or h[marker_offset:marker_offset+4]!=b'BFP1'
            or h[96:104]!=(code_bytes+header_size).to_bytes(8,'little')
            or h[96:104]!=h[104:112]):
            raise ValueError('BF callable ELF header validation failed')
        if shared_library and (h[0x108:0x110]!=code_bytes.to_bytes(8,'little')
                               or h[0x360:0x368]!=code_bytes.to_bytes(8,'little')
                               or h[0x180:0x188]!=b'BFP1\x01\x00\x00\x00'):
            raise ValueError('BF DSO exported function size or ABI version mismatch')
        provisional=d/'image.elf'
        digest=hashlib.sha256()
        with provisional.open('wb') as f:
            for part in (h[:-1],wrapper_data[:32]):
                f.write(part);digest.update(part)
            with zipfile.ZipFile(raw_bundle) as z, z.open('code.bin') as stage_code:
                while chunk:=stage_code.read(1<<20):
                    f.write(chunk);digest.update(chunk)
            f.write(wrapper_data[32:-1]);digest.update(wrapper_data[32:-1])
            f.flush();os.fsync(f.fileno())
        if provisional.stat().st_size!=code_bytes+header_size:
            raise ValueError('native code size and BF ELF layout mismatch')
        # Fail closed before exposing a malformed BF-generated DSO. This is
        # independent transport validation, not Python ELF construction.
        if shared_library:
            try:
                from .android_callable_elf_validate63 import validate_dso
            except ImportError:
                from android_callable_elf_validate63 import validate_dso
            validate_dso(provisional)
            # Independently verify the exact BFP1 native instruction contract
            # and every BF-emitted loop target before the atomic publication.
            try:
                from .android_callable_code_validate64 import validate_code
            except ImportError:
                from android_callable_code_validate64 import validate_code
            verified = validate_code(provisional)
            if verified['bracket_pairs'] != result['bracket_pairs']:
                raise ValueError('BF native bracket count disagrees with compilation ledger')
        provisional.chmod(0o755)
        provisional.replace(output)
        return {'iteration':59 if shared_library else 58,
                'format':'AARCH64_ELF64_DSO_EXPORTED_BFP1' if shared_library else 'AARCH64_ET_DYN_CALLABLE_BFP1',
                'mode':'DYNAMIC_ALL_EIGHT_WITH_64_BIT_PC_RELATIVE_LOOPS',
                'source_bytes':result['source_bytes'],'source_sha256':result['source_sha256'],
                'native_code_bytes':code_bytes,'elf_bytes':code_bytes+header_size,
                'elf_sha256':digest.hexdigest(),
                'bracket_pairs':result['bracket_pairs'],
                'maximum_nesting_depth':result['maximum_nesting_depth'],
                'wide_relocation_patches':result['patches_applied'],
                'fixed_source_limit':None,'fixed_record_limit':None,
                'fixed_bracket_depth_limit':None,
                'BF_native_code':'STANDARD_BRAINFUCK',
                'BF_bracket_pairing':'STANDARD_BRAINFUCK_FILE_BACKED_STACK',
                'BF_loop_offsets_and_signed64_displacements':'STANDARD_BRAINFUCK',
                'BF_header_and_ABI_wrapper':'STANDARD_BRAINFUCK',
                'dso_dynamic_symbol':'bfc_call_v1' if shared_library else None,
                'jni_exports':False,'android_dlopen_verified':False,
                'transport_role':'OPAQUE_FRAMES_INDEXED_PATCH_STORAGE_ATOMIC_COMMIT',
                'android_device_executed':False,'jni_shared_object':False,
                'android_native_selfhosted':False,
                'execution_evidence':'PENDING'}


def main():
    p=argparse.ArgumentParser(description='BF-owned growing AArch64 callable compiler with loops')
    p.add_argument('source',type=Path)
    p.add_argument('-o','--output',required=True,type=Path)
    p.add_argument('--max-code-bytes',type=int)
    p.add_argument('--max-pairs',type=int)
    a=p.parse_args()
    print(json.dumps(compile_callable(a.source,a.output,max_code_bytes=a.max_code_bytes,
                                      max_pairs=a.max_pairs),indent=2))

if __name__=='__main__':main()
