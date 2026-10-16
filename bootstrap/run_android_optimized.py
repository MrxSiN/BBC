#!/usr/bin/env python3
"""Transport for the BF-owned Android native optimizer; no native encoding here."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from run_android_loops import ROOT, compile_source, run_stage
from transport import encode_source

OPTIMIZER = ('experiments/android_native_optimize.bf', 'build/android_native_optimize_x86_64_linux.elf')
RESOURCE_OPTIMIZER = ('experiments/android_resource_optimize.bf', 'build/android_resource_optimize_x86_64_linux.elf')
OPTIMIZERS = {'optimize': OPTIMIZER, 'resources': RESOURCE_OPTIMIZER}


def optimized_stage(stage, payload):
    if os.name == 'nt':
        from local_seed import LocalSeedRunner
        return LocalSeedRunner()(stage, payload)
    if stage not in OPTIMIZERS:
        return run_stage(stage, payload)
    return subprocess.run([str(ROOT / OPTIMIZERS[stage][1])], input=payload, capture_output=True,
                          timeout=30, check=True).stdout


def compile_optimized_source(source, stage_runner=optimized_stage, check_hashes=True):
    if check_hashes:
        evidence = json.loads((ROOT / 'evidence/android_native_optimization.json').read_text())
        for name, spec in OPTIMIZERS.items():
            for path, label in zip(spec, ('source_sha256', 'linux_optimizer_sha256')):
                if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != evidence['optimizers'][name][label]:
                    raise ValueError('optimizer source or native executable differs from evidence')
    image = compile_source(source, stage_runner=stage_runner, check_hashes=check_hashes)
    filtered = stage_runner('filter', encode_source(source))
    if not filtered or filtered[-1]:
        raise ValueError('Brainfuck source filter rejected input')
    for name in OPTIMIZERS:
        result = stage_runner(name, filtered[:-1] + b'\0' + image)
        if len(result) != 4193 or result[-1] or result[:4] != b'\x7fELF':
            raise ValueError(f'Brainfuck {name} optimizer rejected image')
        image = result[:-1]
    return image


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: python3 bootstrap/run_android_optimized.py source.bf image.elf')
    image = compile_optimized_source(Path(sys.argv[1]).read_bytes())
    target = Path(sys.argv[2])
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.android-optimized-', dir=target.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(image)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temp, target)
        os.chmod(target, 0o700)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)
    print(f'BF optimized Android static PIE: {target} ({len(image)} bytes)')


if __name__ == '__main__':
    main()
