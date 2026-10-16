#!/usr/bin/env python3
"""Regression: source framing and optional native stages stay bound to evidence."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'bootstrap'), str(ROOT/'tools')]
import run_android_native as native
from source_check import check_source


class NoDevice(native.NativeAndroidCompiler):
    def shell(self, command): return SimpleNamespace(stdout=b'', stderr=b'')
    def push(self, path, name): pass


def main():
    android = check_source((ROOT/'compiler/android_core.bf').read_bytes())
    linux = check_source((ROOT/'compiler/core.bf').read_bytes())
    assert android[:2462] == linux[:2462]
    original = native.PROOF
    with tempfile.TemporaryDirectory(prefix='bfc_native_manifest_') as td:
        proof = Path(td)/'proof'; proof.mkdir()
        for name in ('report.json','stage2.elf','optimizer.elf','optimizer.stream','scanner.elf','scanner.stream'):
            shutil.copyfile(original/name, proof/name)
        native.PROOF = proof
        NoDevice('unused',Path(td)/'work')
        # Mutating both file and its agreeing stream used to bypass provenance.
        image = bytearray((proof/'optimizer.elf').read_bytes()); image[196] ^= 1
        (proof/'optimizer.elf').write_bytes(image)
        (proof/'optimizer.stream').write_bytes(image+b'\0')
        try: NoDevice('unused',Path(td)/'rejected')
        except ValueError as error: assert 'native build manifest' in str(error)
        else: raise AssertionError('unbound optimizer byte patch accepted')
    native.PROOF = original
    compiler = object.__new__(NoDevice)
    calls=[]
    def stage(name, payload):
        calls.append(name)
        if name == 'compiler': return b'opaque artifact\0'
        if name == 'scanner': return b'+\x02\0\0\0'
        raise AssertionError('optimizer executed after scanner framing failure')
    compiler.stage=stage
    try: compiler.compile(b'+')
    except ValueError as error: assert 'framing mismatch' in str(error)
    else: raise AssertionError('bad scanner count accepted')
    assert calls == ['compiler','scanner']
    print('PASS: canonical BF decoder reuse, paired artifact/stream tamper rejection, scanner framing rejection')


if __name__=='__main__': main()
