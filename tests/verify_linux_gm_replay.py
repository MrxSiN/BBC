#!/usr/bin/env python3
"""Reproduce archived Android-GM policy images with BF executed on Linux.

Two independent trust levels: Linux-native BF stage runs for scanner/RLE/
resolver/base optimizer; a separate cold C BF interpreter for full compilation.
The host does not translate policy BF into AArch64 instructions or patch ELFs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bootstrap.run_policy_native import PolicyCompiler
from bootstrap.linux_policy_native import LinuxPolicyNative
from bootstrap.transport import encode_source


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(out):
    evidence = ROOT / 'evidence/gm_native_20261014_v4'
    archived_build = json.loads((evidence/'build.json').read_text())
    src = evidence/'GM/brainfuck/src'
    out.mkdir(parents=True, exist_ok=True)
    report = {
        'classification':'LINUX_EXECUTED_BF_COMPILER_REPLAY_MATCHES_ARCHIVED_ANDROID_IMAGES',
        'device_executed_in_this_run': False,
        'compiler_algorithms_implemented_by':'unchanged_standard_brainfuck_policy_stages',
        'linux_seed_role':'C interpreter executes BF stage instructions, does not translate BF to machine code',
        'linux_native_stage_role':'self-hosted Linux BF compiler compiles stage BF to Linux ELF, which then executes',
        'archived_device_build_evidence':'evidence/gm_native_20261014_v4/build.json',
        'archived_device_execution_evidence':'evidence/gm_native_device_20261014_v4/report.json',
        'original_policy_images': {}, 'native_stage_parity': {},
    }
    # Full compilation on the independent, run-accelerated cold BF interpreter.
    engine = PolicyCompiler(out/'full', backend='linux-seed')
    for name in ('row','scope'):
        raw = (src/(name+'.bf')).read_bytes()
        assert sha(raw) == archived_build['sources'][name]['source_sha256']
        began = time.monotonic()
        image = engine.compile(raw, affine=True)
        assert image == (evidence/(name+'.elf')).read_bytes(), f'{name} Android output mismatch'
        assert sha(image) == archived_build['sources'][name]['elf_sha256']
        path = out/(name+'.elf');path.write_bytes(image)
        print(f'BF replay {name} complete',flush=True)
        report['original_policy_images'][name] = {
            'source_commands':sum(raw.count(bytes([c])) for c in b'><+-.,[]'),
            'source_sha256':sha(raw),'elf_sha256':sha(image),
            'elf_bytes':len(image),'exact_android_image_match':True,
            'linux_cold_interpreter_wall_s':round(time.monotonic()-began,3)}
    report['native_stage_parity'] = '3 early native stages verified separately by tests/verify_linux_policy_stages.py'
    report['independent_seed_differentials'] = 'independently verified by tests/verify_policy_seed_runs.py'
    report['linux_elf_compiler_sha256'] = sha((ROOT/'build/compiler_x86_64_linux.elf').read_bytes())
    report['original_gm_apk_rebuilt_on_linux'] = False
    report['android_device_runtime_performance_retested'] = False
    report['twitter_threads_compiled'] = False
    report['hundred_million_command_native_compilation'] = False
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-output', type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='iteration54_gm_') as temp:
        report = run(Path(temp))
    if args.evidence_output:
        args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
        args.evidence_output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS both original GM policy images match the archived Android images exactly')

if __name__ == '__main__':main()
