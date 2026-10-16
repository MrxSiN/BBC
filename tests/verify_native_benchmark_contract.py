#!/usr/bin/env python3
"""Verify the benchmark's C baseline computes the same byte results as native BF.

This is an executable differential test, not a performance guarantee.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
cc=shutil.which('cc')
if cc is None:
    raise SystemExit('UNVERIFIED: cc is required for C benchmark oracle')
for name,a,b in [('nested_affine',15,17), ('nested_affine_stress',100,101)]:
    with tempfile.TemporaryDirectory() as tmp:
        tmp=pathlib.Path(tmp)
        bf=tmp/'benchmark_bf.elf'
        c=tmp/'benchmark_c'
        subprocess.run([sys.executable,str(ROOT/'bootstrap/run_compiler.py'),
                        str(ROOT/f'benchmarks/programs/{name}.bf'),str(bf)],
                       check=True,capture_output=True,timeout=120)
        subprocess.run([cc,'-O3',f'-DINNER_A={a}',f'-DINNER_B={b}',
                        '-o',str(c),str(ROOT/'benchmarks/baselines/nested_affine.c')],
                       check=True,capture_output=True,timeout=30)
        for input_bytes in [b'',b'\0',b'\1',b'\xad',b'\xff']:
            expected=bytes([(input_bytes[0]*a*b)%256 if input_bytes else 0])
            for program in (bf,c):
                output=subprocess.run([str(program)],input=input_bytes,check=True,
                                      capture_output=True,timeout=15)
                assert output.stdout==expected,(name,input_bytes,program,output.stdout,expected)
print('PASS 2 algorithms, 5 byte inputs each, both BF-native and optimized C: 20 checks')
