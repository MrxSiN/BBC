#!/usr/bin/env python3
"""Reproduce native Brainfuck compiler stages; C executes BF but never compiles it.

Stage 0: independent C BF interpreter runs canonical BF compiler source.
Stage 1: generated native compiler compiles the identical BF source.
Stage 2: regenerated native compiler compiles that source again.
Only an exact three-stage match is allowed to update the installed native ELF.
"""
import hashlib
from datetime import date
import json
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bootstrap'))
sys.path.insert(0, str(ROOT / 'tests'))
from transport import encode_source, extract_artifact
from reference import execute
sys.path.insert(0, str(ROOT / 'tools'))
from source_check import check_source

CORE = ROOT / 'compiler/core.bf'
BUILD = ROOT / 'build/compiler_x86_64_linux.elf'
DIGEST = ROOT / 'build/COMPILER_SOURCE_SHA256.txt'
EVIDENCE = ROOT / 'evidence/selfhost.json'


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def run(arguments, *, source, timeout):
    started = time.monotonic()
    result = subprocess.run(arguments, input=encode_source(source), capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f'{arguments[0]} exited {result.returncode}: {result.stderr[-300:]!r}')
    return result, round(time.monotonic() - started, 3)


def validate_elf(artifact: bytes) -> None:
    if (len(artifact) < 65_536 or artifact[:5] != b'\x7fELF\x02' or
        artifact[5] != 1 or artifact[18:20] != b'\x3e\x00'):
        raise RuntimeError('compiler output is not a supported x86-64 ELF')


def verify_compilation_behavior(binary: pathlib.Path, directory: pathlib.Path) -> int:
    cases = [
        (b'', b''),
        (b'+++++[->+++++++++++++<]>.', b''),
        (b'++[>++[>+++<-]<-]>>.', b''),
        (b',.,.', b'\0\xff'),
        (b'++\0+++.', b''),
        (b'+[>+]', b''),  # pointer trap on the right tape boundary
    ]
    for index, (source, stdin) in enumerate(cases):
        compiled, _ = run([str(binary)], source=source, timeout=30)
        executable = directory / f'probe_{index}.elf'
        executable.write_bytes(extract_artifact(compiled.stdout))
        executable.chmod(0o700)
        observed = subprocess.run([str(executable)], input=stdin, capture_output=True, timeout=10)
        try:
            expected, _ = execute(source, stdin, max_steps=500_000)
        except IndexError:
            if observed.returncode != 2:
                raise RuntimeError(f'case {index}: expected native bounds trap')
        else:
            if observed.returncode != 0 or observed.stdout != expected:
                raise RuntimeError(f'case {index}: native/reference mismatch')
    rejected, _ = run([str(binary)], source=b'[]]', timeout=30)
    if not rejected.stdout or rejected.stdout[-1] == 0:
        raise RuntimeError('native compiler accepted unmatched closing bracket')
    return len(cases) + 1


def main() -> None:
    if platform.system() != 'Linux' or platform.machine() not in ('x86_64', 'AMD64'):
        raise RuntimeError('native bootstrap execution requires Linux x86-64')
    source = CORE.read_bytes()
    commands = check_source(source)
    if len(commands) != 14859:
        raise RuntimeError('filtered compiler instruction stream changed unexpectedly')
    with tempfile.TemporaryDirectory(prefix='bf-selfhost-') as name:
        temp = pathlib.Path(name)
        seed = temp / 'seed'
        subprocess.run(['cc', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        str(ROOT / 'bootstrap/seed_interpreter.c'), '-o', str(seed)], check=True)
        # The alternate seed retains unfiltered source bytes and resolves loops
        # through scans instead of a preprocessing stack. It performs BF execution
        # only. Prefer a different C toolchain where one is available.
        alternate_seed = temp / 'alternate_seed'
        alternate_toolchain = shutil.which('clang') or shutil.which('cc')
        subprocess.run([alternate_toolchain, '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        str(ROOT / 'bootstrap/seed_interpreter_alt.c'), '-o', str(alternate_seed)], check=True)
        alternate_result, alternate_elapsed = run(
            [str(alternate_seed), str(CORE), '100000000000'], source=source, timeout=240)
        alternate_artifact = extract_artifact(alternate_result.stdout)
        validate_elf(alternate_artifact)
        print(f"Alternate seed: {len(alternate_artifact)} ELF bytes; SHA-256 {sha256(alternate_artifact)}; {alternate_elapsed}s", flush=True)
        stages = []
        reports = []
        for number in range(3):
            executable = str(seed) if number == 0 else str(stages[-1])
            args = [executable, str(CORE), '100000000000'] if number == 0 else [executable]
            result, elapsed = run(args, source=source, timeout=240 if number == 0 else 90)
            artifact = extract_artifact(result.stdout)
            validate_elf(artifact)
            path = temp / f'stage{number}.elf'
            path.write_bytes(artifact)
            path.chmod(0o700)
            steps = re.search(rb'STEPS=(\d+)', result.stderr) if number == 0 else None
            reports.append({
                'stage': number,
                'compiler_engine': 'independent C Brainfuck interpreter' if number == 0 else 'native compiler generated by previous stage',
                'input_source_sha256': sha256(source),
                'output_elf_sha256': sha256(artifact),
                'output_stream_sha256': sha256(result.stdout),
                'elf_bytes': len(artifact),
                'transport_status': result.stdout[-1],
                'seed_bf_steps': int(steps.group(1)) if steps else None,
                'elapsed_wall_seconds': elapsed,
            })
            stages.append(path)
            print(f"Stage {number}: {len(artifact)} ELF bytes; SHA-256 {sha256(artifact)}; {elapsed}s", flush=True)
        first = stages[0].read_bytes()
        if alternate_result.stdout != first + b'\x00':
            raise RuntimeError('alternate independent BF seed disagrees with Stage 0')
        if any(stage.read_bytes() != first for stage in stages[1:]):
            raise RuntimeError('self-host stages differ: do not promote native compiler')
        probes = verify_compilation_behavior(stages[-1], temp)
        report = {
            'date': date.today().isoformat(),
            'status': 'EXECUTED: 3 stages byte-identical on Linux x86-64',
            'source_command_bytes': len(commands),
            'source_sha256': sha256(source),
            'artifact_elf_sha256': sha256(first),
            'stage_equivalence': 'exact bytes; no normalization',
            'stages': reports,
            'native_behavior_probes_passed': probes,
            'independent_seed_agreement': {
                'status': 'EXECUTED: alternate implementation emits byte-identical Stage 0',
                'implementation': 'bootstrap/seed_interpreter_alt.c; raw source and scanning bracket resolution',
                'toolchain': alternate_toolchain,
                'output_elf_sha256': sha256(alternate_artifact),
                'output_stream_sha256': sha256(alternate_result.stdout),
                'elapsed_wall_seconds': alternate_elapsed,
                'same_output_bytes': True,
                'independence_limit': 'both seeds are C programs; one compiler toolchain may still be shared',
            },
            'seed_role': 'Both seeds execute BF only; neither parses or generates native code for source inputs',
            'external_tools': ['cc for primary cold-bootstrap seed',
                               f'{alternate_toolchain} for independent alternate BF seed',
                               'Python for transport and checks'],
            'claims_excluded': ['formal proof of memory safety', 'optimized C/Rust performance parity', 'bootstrap seed trust'],
        }
        BUILD.parent.mkdir(parents=True, exist_ok=True)
        replacement = BUILD.with_suffix('.elf.verified.tmp')
        shutil.copyfile(stages[-1], replacement)
        replacement.chmod(0o700)
        os.replace(replacement, BUILD)
        DIGEST.write_text(sha256(source) + '\n')
        EVIDENCE.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS: Stage 0 == Stage 1 == Stage 2; {probes} runtime probes; installed native compiler')


if __name__ == '__main__':
    main()
