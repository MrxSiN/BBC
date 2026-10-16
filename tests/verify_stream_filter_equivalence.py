#!/usr/bin/env python3
"""Compare optimized and previous standard BF filters as independent native binaries.

Both programs are genuine Brainfuck. The bootstrap compiler emits both ELFs;
Python supplies test bytes and checks behavior, not machine code or filtering.
"""
import hashlib
import json
import pathlib
import random
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bootstrap'))
from transport import encode_source, extract_artifact
sys.path.insert(0, str(ROOT / 'tools'))
from source_check import check_source

OLD = ROOT / 'evidence/history/iteration15/stream_filter.bf'
NEW = ROOT / 'experiments/stream_filter.bf'
COMPILER = ROOT / 'build/compiler_x86_64_linux.elf'
INSTALLED = ROOT / 'build/stream_filter_x86_64_linux.elf'
EVIDENCE = ROOT / 'evidence/stream_filter_equivalence.json'
COMMANDS = frozenset(b'><+-.,[]')


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def compile_filter(source):
    proc = subprocess.run([str(COMPILER)], input=encode_source(source),
                          capture_output=True, timeout=45, check=True)
    return extract_artifact(proc.stdout)


def run(binary, payload, timeout=20):
    proc = subprocess.run([str(binary)], input=payload, capture_output=True,
                          timeout=timeout, check=True)
    return proc.stdout


def main():
    old_source, new_source = OLD.read_bytes(), NEW.read_bytes()
    assert len(check_source(old_source)) == 1031
    assert len(check_source(new_source)) == 816
    rng = random.Random(160026)
    raw_cases = [('empty', b''), ('all_bytes', bytes(range(256))),
                 ('reversed_bytes', bytes(reversed(range(256)))),
                 ('compiler_source', (ROOT / 'compiler/core.bf').read_bytes()),
                 ('long_ignored', b'ignored source text '*1500 + b'+[->+<].'),
                 ('command_heavy', b'><+-.,[]'*1000)]
    raw_cases.extend((f'single_{x:02x}', bytes([x])) for x in range(256))
    # Random test streams include all possible literal byte values after stuffing.
    for i in range(128):
        raw_cases.append((f'random_{i:03d}', rng.randbytes(rng.randrange(1, 1024))))
    invalid = [b'\xff', b'\xff\x00', b'\xff\x03', b'\xff\xff',
               b'+\xff\x03', b'++\xff\x02\xff', b'\xff\x01\xff\x09',
               b'\xff\x03+++', b'\xff\x01\xff\x00', b'abc\xff\xfe']
    with tempfile.TemporaryDirectory(prefix='bf-filter-equivalence-') as td:
        work = pathlib.Path(td)
        old_binary = work / 'old.elf'
        new_binary = work / 'new.elf'
        old_elf = compile_filter(old_source)
        new_elf = compile_filter(new_source)
        assert new_elf == INSTALLED.read_bytes(), 'optimized installed filter is stale'
        assert len(old_elf) == 215 + 32 * len(check_source(old_source))
        assert len(new_elf) == 215 + 32 * len(check_source(new_source))
        for path, artifact in ((old_binary, old_elf), (new_binary, new_elf)):
            path.write_bytes(artifact)
            path.chmod(0o700)
        for name, raw in raw_cases:
            payload = encode_source(raw)
            previous = run(old_binary, payload)
            optimized = run(new_binary, payload)
            expected = bytes(x for x in raw if x in COMMANDS) + b'\x00'
            assert previous == optimized == expected, (name, 'filter semantic divergence')
        for payload in invalid:
            before = run(old_binary, payload)
            after = run(new_binary, payload)
            assert before == after and before[-1:] == b'\x01', (payload, 'framing divergence')
        # Non-gating runtime evidence: same hardware/input, interleaved runs.
        # Interpreter/optimizer claims are deliberately excluded.
        perf = []
        workloads = [('ignored_24k', b'prose token '*2000),
                     ('mixed_12k', b'x+y-z,[.] <> '*1000)]
        for label, raw in workloads:
            payload = encode_source(raw)
            assert run(old_binary, payload) == run(new_binary, payload)
            samples = {'previous': [], 'optimized': []}
            for repetition in range(9):
                order = ['previous', 'optimized'] if repetition % 2 == 0 else ['optimized', 'previous']
                for key in order:
                    binary = old_binary if key == 'previous' else new_binary
                    started = time.perf_counter_ns()
                    run(binary, payload)
                    samples[key].append((time.perf_counter_ns() - started) / 1e6)
            perf.append({'workload': label, 'raw_bytes': len(raw),
                         'samples_ms': samples,
                         'median_previous_ms': statistics.median(samples['previous']),
                         'median_optimized_ms': statistics.median(samples['optimized'])})
    report = {
        'date': '2026-10-12',
        'classification': 'EXECUTED equivalence between historical and smaller Brainfuck-only streaming filters',
        'old_source_sha256': sha(old_source),
        'new_source_sha256': sha(new_source),
        'compiler_sha256': sha(COMPILER.read_bytes()),
        'old_commands': 1031, 'new_commands': 816,
        'old_elf_sha256': sha(old_elf), 'new_elf_sha256': sha(new_elf),
        'old_elf_bytes': len(old_elf), 'new_elf_bytes': len(new_elf),
        'valid_cases_passed': len(raw_cases),
        'invalid_cases_rejected': len(invalid),
        'exact_output_equivalence': True,
        'performance': perf,
        'limitations': ['Historical comparison is executable testing, not formal equivalence',
                        'Runtime microbenchmarks are filter-to-filter, not C or Rust algorithm baselines',
                        'Filter is still separate from authoritative compiler/core.bf'],
    }
    EVIDENCE.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS {len(raw_cases)} valid and {len(invalid)} malformed inputs against both BF filters; '
          f'{len(old_elf)} -> {len(new_elf)} ELF bytes')
    for item in perf:
        print(f"  {item['workload']}: old median {item['median_previous_ms']:.3f} ms, "
              f"new median {item['median_optimized_ms']:.3f} ms")


if __name__ == '__main__':
    main()
