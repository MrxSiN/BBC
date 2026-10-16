#!/usr/bin/env python3
"""Transport-only Linux host adapter for the experimental BF AArch64 emitter.

The executable named below is a Brainfuck program compiled by the self-hosted
Linux compiler. This adapter performs no Brainfuck parsing or native encoding.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if len(sys.argv) != 3:
    raise SystemExit('usage: python3 bootstrap/run_android_subset.py source.bf out.elf')
source_path = Path(sys.argv[1])
target = Path(sys.argv[2])
source = source_path.read_bytes()
if len(source) > 1_048_576:
    raise SystemExit('experimental adapter refuses input larger than 1 MiB')
if b'\0' in source:
    raise SystemExit('experimental emitter treats NUL as EOF; refusing lossy input')
report = json.loads((ROOT / 'evidence/android_aarch64_subset.json').read_text())
emitter_source = ROOT / 'experiments/android_aarch64_pie_subset.bf'
emitter_binary = ROOT / 'build/android_pie_emitter_linux_x86_64.elf'
for path,key in ((emitter_source,'source_sha256'),(emitter_binary,'host_emitter_sha256')):
    if hashlib.sha256(path.read_bytes()).hexdigest() != report[key]:
        raise SystemExit('emitter hash differs from verified evidence; rerun tests')
result = subprocess.run([str(emitter_binary)], input=source, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, timeout=30, check=True)
if len(result.stdout) != 4193 or result.stdout[-1] != 0:
    raise SystemExit('experimental Brainfuck Android backend rejected the source; output was not installed')
image = result.stdout[:-1]
if image[:4] != b'\x7fELF':
    raise SystemExit('backend produced a non-ELF artifact')
target.parent.mkdir(parents=True, exist_ok=True)
fd,tmp = tempfile.mkstemp(prefix='.android-proto-', dir=target.parent)
try:
    with os.fdopen(fd,'wb') as fp:
        fp.write(image)
        fp.flush()
        os.fsync(fp.fileno())
    os.chmod(tmp,0o700)
    os.replace(tmp,target)
finally:
    if os.path.exists(tmp):os.unlink(tmp)
print(f'Experimental Android AArch64 PIE emitted by Brainfuck: {target} ({len(image)} bytes)')
