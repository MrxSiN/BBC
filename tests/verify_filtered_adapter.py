#!/usr/bin/env python3
"""Integration checks for the optional two-native-BF-executable adapter.

The adapter itself is only transport; lexical filtering is owned by BF source.
"""
import hashlib
import json
import pathlib
import random
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bootstrap'))
from transport import encode_source, extract_artifact
from run_filtered_compiler import compile_source, verify_installed, CORE_ELF, FILTER_ELF
sys.path.insert(0, str(ROOT / 'tests'))
from reference import execute

ADAPTER = ROOT / 'bootstrap/run_filtered_compiler.py'
CORE = ROOT / 'compiler/core.bf'
EVIDENCE = ROOT / 'evidence/filtered_adapter.json'
OPS = b'><+-.,[]'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(source, binary, timeout=30):
    proc = subprocess.run([str(binary)], input=encode_source(source), capture_output=True, timeout=timeout)
    assert proc.returncode == 0, (binary, proc.returncode, proc.stderr[-200:])
    return extract_artifact(proc.stdout)


def main():
    verify_installed()
    # Deliberately use a wide, completely source-agnostic test distribution.
    # The reference interpreter below computes expected output, never the
    # actual filter byte stream or native program bytes.
    cases = [
        ('empty', b'', b''),
        ('all_ignored', b'not brainfuck ' * 2200 + b'\0\xff', b''),
        ('large_comments', b'prose ' * 4000 + b'+++++.', b'\x05'),
        ('comment_with_escaped_bytes', b'prose\0\xff+ prose ++.', b'\x03'),
        ('echo', b'comment\0\xff,.,.', b'A\0'),
        ('nested', b'++[>++[>+++<-]<-]>>.', b''),
        ('loop_transfer', b'+++++[->+++++<]>.', b''),
        ('capacity', b'+' * 16127 + b'.', b''),
    ]
    # Nonsemantic byte-noise stress without loops that can run forever.
    rng = random.Random(140026)
    ignored = bytes(x for x in range(256) if x not in OPS)
    for i in range(20):
        count = rng.randrange(0, 25000)
        garbage = bytes(ignored[rng.randrange(len(ignored))] for _ in range(count))
        cases.append((f'noise_{i:02d}', garbage + b'++++.', b''))
    records = []
    with tempfile.TemporaryDirectory(prefix='bf-filter-adapter-') as td:
        work = pathlib.Path(td)
        for i, (name, source, data) in enumerate(cases):
            artifact = compile_source(source)
            commands = bytes(c for c in source if c in OPS)  # TEST ORACLE only
            baseline = run(commands, CORE_ELF, 90)
            assert artifact == baseline, (name, 'different ELF after source filtering')
            exe = work / f'case{i}.elf'
            exe.write_bytes(artifact)
            exe.chmod(0o700)
            result = subprocess.run([str(exe)], input=data, capture_output=True, timeout=10)
            expected, _ = execute(commands, data, max_steps=2_000_000)
            assert result.returncode == 0 and result.stdout == expected, (name, result)
            assert len(artifact) == 215 + 32*len(commands), name
            records.append({'name':name, 'source_bytes':len(source), 'command_bytes':len(commands),
                            'artifact_sha256':sha(artifact)})

        source_file = work / 'comment_heavy.bf'
        output_file = work / 'out.elf'
        source_file.write_bytes(b'notes ' * 5000 + b'+++++.')
        cli = subprocess.run([sys.executable, str(ADAPTER), str(source_file), str(output_file)],
                             capture_output=True, timeout=90)
        assert cli.returncode == 0, cli.stderr
        assert output_file.read_bytes() == run(b'+++++.', CORE_ELF)

        # Reject bad BF source before replacing a previous successful artifact.
        prior = output_file.read_bytes()
        for invalid in (b']', b'[[', b'+' * 16129, b'ignored'*5000+b']'):
            source_file.write_bytes(invalid)
            rejected = subprocess.run([sys.executable, str(ADAPTER), str(source_file), str(output_file)],
                                      capture_output=True, timeout=90)
            assert rejected.returncode != 0 and output_file.read_bytes() == prior, invalid[:30]

        # The adapter has its own raw-file resource ceiling. It must reject
        # before running either BF executable and leave the last output intact.
        from run_filtered_compiler import MAX_RAW_BYTES
        source_file.write_bytes(b'ignored ' * (MAX_RAW_BYTES // 8 + 1))
        too_large = subprocess.run([sys.executable, str(ADAPTER), str(source_file), str(output_file)],
                                   capture_output=True, timeout=30)
        assert too_large.returncode != 0 and output_file.read_bytes() == prior
        assert b'adapter limit' in too_large.stderr

        # A tampered filter, even if otherwise executable, is not accepted.
        # Avoid modifying the checked-in ELF: monkeypatch the module path.
        import run_filtered_compiler as adapter
        original = adapter.FILTER_ELF
        tampered = work / 'tampered.elf'
        corrupted = bytearray(original.read_bytes()); corrupted[-1] ^= 1
        tampered.write_bytes(corrupted)
        adapter.FILTER_ELF = tampered
        try:
            try:
                adapter.verify_installed()
            except ValueError:
                pass
            else:
                raise AssertionError('tampered native BF filter accepted')
        finally:
            adapter.FILTER_ELF = original

        # The optional adapter must not interpret or weaken the native backend's
        # own bracket validation. A failed compilation produces no new file.
        output_file.unlink()
        source_file.write_bytes(b']')
        failed = subprocess.run([sys.executable, str(ADAPTER), str(source_file), str(output_file)],
                                capture_output=True, timeout=90)
        assert failed.returncode and not output_file.exists()

        # Full annotated compiler, with ample added ignored source prose;
        # this fails the raw-byte limit without BF-owned filtering.
        expanded_core = CORE.read_bytes() + b'ignored text ' * 2000
        stage = compile_source(expanded_core)
        stage_source = bytes(c for c in expanded_core if c in OPS)
        assert stage == run(stage_source, CORE_ELF, 90)
        staged = work / 'selfhost_filtered.elf'
        staged.write_bytes(stage)
        staged.chmod(0o700)
        assert run(stage_source, staged, 90) == stage

    EVIDENCE.write_text(json.dumps({
        'date':'2026-10-12',
        'classification':'EXECUTED opt-in two-BF-executable file adapter; single compiler integration UNIMPLEMENTED',
        'compiler_source_sha256':sha(CORE.read_bytes()),
        'compiler_elf_sha256':sha(CORE_ELF.read_bytes()),
        'filter_source_sha256':sha((ROOT/'experiments/stream_filter.bf').read_bytes()),
        'filter_elf_sha256':sha(FILTER_ELF.read_bytes()),
        'cases_passed':len(records),
        'cli_success':True,
        'cli_negative_cases_rejected':5,
        'existing_artifact_preserved_on_failure':True,
        'modified_filter_binary_rejected':True,
        'expanded_annotated_compiler_selfhost_identical':True,
        'compiler_decoder_modified':False,
        'limitations':[
            'Two separate native BF executables and a Python byte-transport adapter are used',
            'Authoritative core.bf still has a raw-decoded-byte ceiling and comment-size dependence',
            'Filtered BF command count must fit the backend raw limit of 16128',
            'These tests are not a compiler-internal memory safety proof',
        ],
        'cases':records,
    }, indent=2)+'\n')
    print(f'PASS {len(records)} native filtered-adapter comparisons; CLI output atomic; '
          '4 rejection cases; modified executable rejected; filtered self-host repeated')


if __name__ == '__main__':
    main()
