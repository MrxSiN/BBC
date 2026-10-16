#!/usr/bin/env python3
"""Rebuild standard-Brainfuck callable stages with the verified native BF compiler.

The builder is a transport and reproducibility tool, not a source parser,
optimizer or AArch64 code generator. All native outputs come from compiled BF.
"""
from pathlib import Path
import hashlib
import os
import subprocess
import tempfile

from bootstrap.transport import encode_source,extract_artifact
from bootstrap.android_dynamic_callable58 import ROOT,STAGES
from tools.source_check import check_source

STAGE_NAMES=('android_callable_slots58','android_callable_ledger58',
             'android_callable_linear57','android_callable_header57',
             'android_callable_dso_header59')


def main():
    STAGES.mkdir(parents=True,exist_ok=True)
    for name in STAGE_NAMES:
        src=ROOT/'experiments'/f'{name}.bf'
        commands=check_source(src.read_bytes())
        if not commands or len(commands)>16128:
            raise RuntimeError(f'Brainfuck source size exceeds verified Linux compiler: {name}')
        p=subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
              input=encode_source(src.read_bytes()),capture_output=True,check=True,timeout=120)
        executable=extract_artifact(p.stdout)
        target=STAGES/(name+'.elf')
        with tempfile.NamedTemporaryFile(dir=STAGES,prefix='.'+name+'.',delete=False) as tmp:
            tmp.write(executable);tmp.flush();os.fsync(tmp.fileno());temp=Path(tmp.name)
        try:
            temp.chmod(0o755)
            if target.exists() and target.read_bytes()!=executable:
                raise ValueError(f'native BF stage differs from pinned release: {name}')
            temp.replace(target)
        finally:
            temp.unlink(missing_ok=True)
        print(name, len(commands),'BF commands',len(executable),'native bytes',
              hashlib.sha256(executable).hexdigest(),flush=True)

if __name__=='__main__':main()
