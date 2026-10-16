#!/usr/bin/env python3
"""Fast native S1/S2 self-compilation equivalence; not a cold-seed replay."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from bootstrap.transport import encode_source, extract_artifact

ROOT=Path(__file__).resolve().parents[1]

def main():
    bf=(ROOT/'compiler/core.bf').read_bytes()
    installed=ROOT/'build/compiler_x86_64_linux.elf'
    expected=hashlib.sha256(installed.read_bytes()).hexdigest()
    rounds=[]
    with tempfile.TemporaryDirectory(prefix='bfc60-native-s2-') as tmp:
        entry=installed
        for number in (1,2):
            run=subprocess.run([str(entry)],input=encode_source(bf),
                               check=True,capture_output=True,timeout=45)
            image=extract_artifact(run.stdout)
            digest=hashlib.sha256(image).hexdigest()
            assert digest==expected,(number,digest,expected)
            entry=Path(tmp)/('stage'+str(number)+'.elf')
            entry.write_bytes(image)
            entry.chmod(0o700)
            rounds.append({'round':number,'sha256':digest,'elf_bytes':len(image)})
    record={'iteration':60,'native_stage1_stage2_byte_identical':True,
            'rounds':rounds,'compiler_source_sha256':hashlib.sha256(bf).hexdigest(),
            'installed_compiler_sha256':expected,
            'cold_seed_rerun_complete':False,
            'qualification':'NATIVE_SELF_COMPILATION_ONLY_NOT_NEW_COLD_BOOTSTRAP',
            'android_native_selfhosting':False}
    (ROOT/'evidence/iteration60_native_selfcompile.json').write_text(json.dumps(record,indent=2)+'\n')
    print('PASS two native compiler generations byte-identical to installed Linux compiler')

if __name__=='__main__':main()
