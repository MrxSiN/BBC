#!/usr/bin/env python3
"""Run bounded, independent development checks before recording an S2 release.

The script replaces itself with the shell gate chain. In particular, do not
keep a Python process holding output pipes while test engines spawn children.
Nothing here compiles Brainfuck into native code; that logic lives in core.bf.
"""
import hashlib
import json
import os
import pathlib
import shlex
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GATES = (
    ('annotations', 'tools/annotate.py', '--check'),
    ('source_annotations', 'tests/verify_source_comments.py'),
    ('compiler_tape_audit', 'tests/verify_compiler_tape.py'),
    ('header_scratch_proof', 'tests/verify_header_scratch.py'),
    ('selfhosting', 'tests/verify_selfhost.py'),
    ('semantics', 'tests/verify.py'),
    ('adversarial', 'tests/verify_adversarial.py'),
    ('native_emission', 'tests/verify_emission.py'),
    ('io_faults', 'tests/verify_io_faults.py'),
    ('elf_size_arithmetic', 'tests/verify_elf_size_primitive.py'),
    ('bf_filter_prototype', 'tests/verify_command_filter.py'),
    ('bf_stream_filter_prototype', 'tests/verify_stream_filter.py'),
    ('stream_filter_equivalence', 'tests/verify_stream_filter_equivalence.py'),
    ('bf_filtered_adapter', 'tests/verify_filtered_adapter.py'),
    ('filtered_integration_contract', 'tests/verify_filter_integration_contract.py'),
    ('integrated_source_filter', 'tests/verify_integrated_filter.py'),
    ('header_literal_reduction', 'tests/verify_header_literal_reduction.py'),
    ('tape_safety_audit', 'tests/verify_tape_safety.py'),
    ('android_aarch64_subset', 'tests/verify_android_aarch64_subset.py'),
    ('android_aarch64_legacy_equivalence', 'tests/verify_android_aarch64_legacy_equivalence.py'),
    ('android_bracket_relocations', 'tests/verify_android_bracket_relocations.py'),
    ('android_aarch64_loops', 'tests/verify_android_aarch64_loops.py'),
    ('documentation', 'tools/check_docs.py'),
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def finalize():
    runner = ROOT / 'tools/verify_release.sh'
    shell_commands = [line.removeprefix('python3 ').strip()
                      for line in runner.read_text().splitlines()
                      if line.startswith('python3 ') and '--finalize-after-gates' not in line]
    expected = [' '.join(args) for _, *args in GATES]
    if shell_commands != expected:
        raise RuntimeError('shell release gate sequence differs from the verified gate manifest')
    # Only invoked by the shell after every gate succeeds. sync_status also
    # cross-checks the source, compiler and gate evidence before release.
    source = (ROOT/'compiler/core.bf').read_bytes()
    binary = (ROOT/'build/compiler_x86_64_linux.elf').read_bytes()
    filter_source = (ROOT/'experiments/command_filter.bf').read_bytes()
    report = {
        'date': '2026-10-12',
        'classification': 'EXECUTED: all listed release gates in the current checkout',
        'iteration': 25,
        'gate_execution_note': 'Linux S2 retained; six Linux-native BF stages jointly generate AArch64 PIE loop machine code; simulated only; no Android execution or native target selfhosting',
        'source_sha256': sha(source),
        'native_compiler_sha256': sha(binary),
        'command_filter_sha256': sha(filter_source),
        'stream_filter_sha256': sha((ROOT/'experiments/stream_filter.bf').read_bytes()),
        'android_prototype_source_sha256': sha((ROOT/'experiments/android_aarch64_pie_subset.bf').read_bytes()),
        'android_bracket_relocations_sha256': sha((ROOT/'experiments/android_bracket_relocations.bf').read_bytes()),
        'android_loop_evidence_sha256': sha((ROOT/'evidence/android_loop_pipeline.json').read_bytes()),
        'gates_passed': len(GATES),
        'gates_failed': 0,
        'separation': 'Brainfuck-only compaction is now integrated into core.bf; BF decoder and native code generator self-host together. External stream filter and transport adapter are optional.',
        'gates': [{'gate': key, 'result': 'PASS'} for key, *_ in GATES],
    }
    (ROOT/'evidence/release_gate.json').write_text(json.dumps(report, indent=2)+'\n')
    subprocess.run([sys.executable, 'tools/sync_status.py'], cwd=ROOT, check=True)
    print(f'PASS {len(GATES)} verification gates; status evidence synchronized', flush=True)


def main():
    if sys.argv[1:] == ['--finalize-after-gates']:
        finalize()
        return
    if len(sys.argv) != 1:
        raise SystemExit('usage: python3 tools/verify_release.py')
    statements = ['set -eu', 'cd ' + shlex.quote(str(ROOT))]
    for key, *args in GATES:
        cmd = ' '.join(shlex.quote(x) for x in (sys.executable, *args))
        statements.append(f'printf "[run] {key}\\n"')
        statements.append(cmd)
    statements.append(shlex.quote(sys.executable) + ' tools/verify_release.py --finalize-after-gates')
    # This exec is intentional: the gate chain must not depend on another
    # Python process managing captured stdout/stderr for every native child.
    os.execv('/bin/sh', ['/bin/sh', '-ec', '\n'.join(statements)])


if __name__ == '__main__':
    main()
