#!/usr/bin/env python3
"""Test-only Windows PE acceptance fixture preparation, no production compilation logic."""
import hashlib, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'bootstrap'),str(ROOT/'tests')]
from run_windows_full192 import compile_source
from reference import execute

CASES=[
 ('empty',b'',b''),
 ('binary_eof',b',.,.',b'\xff'),
 ('binary_zero',b',.',b'\x00'),
 ('wraparound',b'-.',b''),
 ('linear_192',b'+'*191+b'.',b''),
 ('bracket_last_192',b'['+b'+'*190+b']',b''),
 ('transfer_192',b'+'*184+b'[->+<]>.',b''),
 ('nested_192',b'['*96+b']'*96,b''),
 ('sequential_192',b'[]'*96,b''),
 ('big_clear',b'+'*188+b'[-].',b''),
 ('long_io',b',.'*96,bytes(range(96))),
 ('loop_145',b'+'*137+b'[->+<]>.',b''),
 ('pointer_trap',b'+'*191+b'<',b''),
 ('input_loop',b',[-].',b'\xff'),
]

def main():
    directory=ROOT/'build/windows44_acceptance';directory.mkdir(parents=True,exist_ok=True)
    cases=[]
    for name,source,stdin in CASES:
        commands=bytes(c for c in source if c in b'<>+-.,[]')
        assert len(commands)<=192
        image=compile_source(source)
        try:stdout,_=execute(source,stdin,max_steps=500000);exit_code='zero'
        except IndexError:stdout=b'';exit_code='nonzero'
        (directory/f'{name}.bf').write_bytes(source)
        (directory/f'{name}.exe').write_bytes(image)
        cases.append({'name':name,'source':f'{name}.bf','executable':f'{name}.exe',
          'commands':len(commands),'stdin_hex':stdin.hex(),
          'expected_stdout_hex':stdout.hex(),'expected_exit':exit_code,
          'sha256':hashlib.sha256(image).hexdigest()})
        run=subprocess.run([str(ROOT/'build/windows_pe_linux_x64_shim_192'),str(directory/f'{name}.exe')],input=stdin,capture_output=True,timeout=4)
        assert (run.returncode==0 and run.stdout==stdout) if exit_code=='zero' else run.returncode==99
    manifest={'iteration':44,'profile':'windows-x86_64-PE32+-192slots',
      'platform':'native Windows x64 required for acceptance',
      'Linux_CPU_shim_cases_passed':len(cases),'Windows_execution':'NOT_RUN',
      'cases':cases}
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    previous=(ROOT/'build/windows43_acceptance/verify_windows43.ps1').read_text()
    script=previous.replace('iteration=43','iteration=44').replace('device_results_windows43.json','device_results_windows44.json')
    (directory/'verify_windows44.ps1').write_text(script)
    print(f"prepared {len(cases)} PE files; all passed test-only Linux x64 shim")
if __name__=='__main__':main()
