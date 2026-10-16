#!/usr/bin/env python3
"""Execute the raw BF Android compiler seed and native self-compilation witnesses."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'bootstrap'), str(ROOT / 'tests'), str(ROOT / 'tools')]
from transport import encode_source, extract_artifact
from source_check import check_source
from reference import execute


def sha(data): return hashlib.sha256(data).hexdigest()


def inspect(image, commands):
    size = 208 + 64 * commands
    assert image[:8] == b'\x7fELF\x02\x01\x01\0' and len(image) == size
    assert struct.unpack_from('<HHIQQ', image, 16) == (3, 183, 1, 176, 64)
    assert struct.unpack_from('<HHH', image, 52) == (64, 56, 2)
    assert struct.unpack_from('<IIQQQQQQ', image, 64) == (1, 5, 0, 0, 0, size, size, 0x4000)
    assert struct.unpack_from('<IIQQQQQQ', image, 120) == (1, 6, 0, 0x200000, 0x200000, 0, 65536, 0x4000)
    assert image[176:196] == struct.pack('<IIIII', 0x90001014, 0xaa1403f3, 0x91404295, 0xd503201f, 0xd503201f)
    stack = []; matches = {}
    for i, c in enumerate(commands if isinstance(commands, bytes) else b''):
        if c == 91: stack.append(i)
        if c == 93:
            start = stack.pop(); matches[start] = i; matches[i] = start
    return size


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--adb', default=r'D:\Android\platform-tools\adb.exe')
    parser.add_argument('--serial', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists() and any(out.iterdir()): parser.error('output must be absent or empty')
    out.mkdir(parents=True, exist_ok=True)
    source_path = ROOT / 'compiler/android_core.bf'
    source = source_path.read_bytes(); code = check_source(source)
    assert len(code) <= 16128
    wire = encode_source(source); (out / 'source.wire').write_bytes(wire)
    seeds = []
    for name in ('seed', 'seed_alt'):
        start = time.perf_counter()
        result = subprocess.run([str(ROOT / f'build/android_optimization/{name}.exe'), str(source_path), '10000000000'],
                                input=wire, capture_output=True, check=True, timeout=180)
        (out / (name + '.stderr')).write_bytes(result.stderr)
        image = extract_artifact(result.stdout); inspect(image, len(code))
        (out / (name + '.elf')).write_bytes(image)
        seeds.append(image)
        print(f'{name}: {len(image)} bytes, {time.perf_counter()-start:.3f}s', flush=True)
    assert seeds[0] == seeds[1]
    (out / 'stage0.elf').write_bytes(seeds[0])
    adb = [args.adb, '-s', args.serial]
    remote = '/data/local/tmp/bfc_native_selfhost'
    def run(command):
        return subprocess.run([str(c) for c in command], capture_output=True, check=True, timeout=180)
    def shell(command): return run(adb + ['shell', '-T', command])
    def push(path, name=None):
        name = name or path.name
        run(adb + ['push', path, remote + '/' + name])
        assert shell(f'sha256sum {remote}/{name}').stdout.decode().split()[0] == sha(path.read_bytes())
    props = {key: shell('getprop ' + key).stdout.decode().strip() for key in
             ('ro.product.model', 'ro.product.cpu.abi', 'ro.build.version.release', 'ro.build.version.sdk', 'ro.build.fingerprint')}
    assert props['ro.product.cpu.abi'] == 'arm64-v8a'
    shell('mkdir -p ' + remote); push(out / 'source.wire'); push(out / 'stage0.elf', 'stage0')
    shell('chmod 700 ' + remote + '/stage0')
    stages = []
    for index in range(1, 4):
        result = shell(f'/system/bin/time -p {remote}/stage{index-1} < {remote}/source.wire > {remote}/stage{index}.stream')
        (out / f'stage{index}.timing.stderr').write_bytes(result.stderr)
        run(adb + ['pull', f'{remote}/stage{index}.stream', out / f'stage{index}.stream'])
        stream = (out / f'stage{index}.stream').read_bytes()
        image = extract_artifact(stream); inspect(image, len(code)); assert image == seeds[0]
        path = out / f'stage{index}.elf'; path.write_bytes(image); push(path, f'stage{index}')
        shell(f'chmod 700 {remote}/stage{index}')
        stages.append({'stage': index, 'sha256': sha(image), 'bytes': len(image),
                       'native_android_executed': True, 'timing': result.stderr.decode().strip()})
        print(f'Android Stage {index}: byte-identical', flush=True)
    def native_compile(data, label, stage=2):
        path = out / (label + '.wire'); path.write_bytes(data); push(path, 'input.wire')
        result = shell(f'{remote}/stage{stage} < {remote}/input.wire > {remote}/program.stream')
        assert not result.stderr
        path = out / (label + '.stream'); run(adb + ['pull', remote + '/program.stream', path])
        return path.read_bytes()
    cases = [(b'', b''), (b'+.', b''), (b'-.', b''), (b',.,.,.', b'\0\xff\x7f'),
             (b',.', b''), (b'++[>++[>+<-]<-]>>.', b''), (b'<', b''), (b'+[>+]', b''),
             (b'['*255+b']'*255, b''), (b'+'*255+b'[->+<]>.', b''),
             (b'comment\x00\xff ignored +.', b''), (b',[>+<-]>.', b'\xff'),
             ((ROOT / 'examples/android_2000_loop_demo.bf').read_bytes(), b''),
             (b'['+b'+'*16126+b']', b'')]
    corpus = []
    for index, (program, data) in enumerate(cases):
        label = f'case{index}'
        stream = native_compile(encode_source(program), label)
        image = extract_artifact(stream); ops = bytes(c for c in program if c in b'><+-.,[]')
        inspect(image, len(ops))
        # Independent seed witness, including the bracket words and file bytes.
        seed = subprocess.run([str(ROOT/'build/android_optimization/seed_alt.exe'), str(source_path), '10000000000'],
                              input=encode_source(program), capture_output=True, check=True, timeout=60)
        assert stream == seed.stdout
        for position, char in enumerate(ops):
            if char not in b'[]': continue
            depth = 1; direction = 1 if char == 91 else -1; target = position
            while depth:
                target += direction
                if ops[target] == char: depth += 1
                elif ops[target] in b'[]': depth -= 1
            distance = (target + 1 - position) * 16 - 1
            word = (0x34000009 if char == 91 else 0x35000009) | ((distance & 0x7ffff) << 5)
            assert struct.unpack_from('<I', image, 196 + position * 64 + 4)[0] == word
        p = out / (label + '.elf'); p.write_bytes(image); push(p, 'program')
        p = out / (label + '.stdin'); p.write_bytes(data); push(p, 'input.stdin')
        shell(f'chmod 700 {remote}/program; {remote}/program < {remote}/input.stdin > {remote}/program.stdout 2> {remote}/program.stderr; echo $? > {remote}/program.exitcode')
        for ext in ('stdout', 'stderr', 'exitcode'):
            run(adb + ['pull', f'{remote}/program.{ext}', out / (label + '.' + ext)])
        try: expected, _ = execute(program, data, max_steps=400000); status = 0
        except IndexError: expected, status = b'', 2
        assert (out / (label + '.stdout')).read_bytes() == expected
        assert int((out / (label + '.exitcode')).read_text()) == status
        assert (out / (label + '.stderr')).read_bytes() == b''
        corpus.append({'source_hex': program.hex(), 'input_hex': data.hex(), 'stdout_hex': expected.hex(),
                       'status': status, 'elf_sha256': sha(image), 'seed_matches_native': True})
    rejections = []
    for index, data in enumerate([b'[', b']', b'['*256+b']'*256, b'+'*16129, b'\xff', b'\xff\x03', b'['*255+b'\xff']):
        stream = native_compile(data, f'reject{index}')
        assert stream and stream[-1] != 0
        rejections.append({'input_sha256': sha(data), 'status': stream[-1], 'output_bytes': len(stream)})
    optional_artifacts = {}
    for name, path in [('optimizer', ROOT/'experiments/android_compact_optimize.bf'),
                       ('scanner', ROOT/'experiments/android_source_scan.bf')]:
        image = extract_artifact(native_compile(encode_source(path.read_bytes()), name))
        inspect(image, len(check_source(path.read_bytes())))
        (out / (name + '.elf')).write_bytes(image)
        optional_artifacts[name] = {'elf_sha256': sha(image),
                                    'stream_sha256': sha((out/(name+'.stream')).read_bytes())}
    report = {'date': datetime.now(timezone(timedelta(hours=8))).date().isoformat(),
              'classification': 'ANDROID_NATIVE_S2_EXECUTED_BOUNDED_BF_COMPILER',
              'source': 'compiler/android_core.bf', 'source_sha256': sha(source), 'filtered_sha256': sha(code),
              'source_bytes': len(source), 'bf_instructions': len(code), 'source_cap_commands': 16128,
              'nesting_cap': 255, 'generated_program_tape_cells': 65536, 'generated_slot_bytes': 64,
              'compiler_elf_sha256': sha(seeds[0]), 'compiler_elf_bytes': len(seeds[0]),
              'independent_seeds_identical': True, 'native_stage0_1_2_3_identical': True,
              'device_properties': props, 'stages': stages, 'corpus': corpus, 'rejections': rejections,
              'optional_stage_sources': {name: sha((ROOT/path).read_bytes()) for name, path in
                                        [('optimizer','experiments/android_compact_optimize.bf'),('scanner','experiments/android_source_scan.bf')]},
              'optional_stage_artifacts': optional_artifacts,
              'test_harness_sha256': sha(Path(__file__).read_bytes()),
              'limitations': ['Single Pixel 8 Pro/API37 with 4KiB pages', 'Bounded 16128-command compiler, not 300000 commands',
                              'Fixed 64-byte slots; optional compact optimizer is separate', 'No complete compiler tape proof',
                              'Linux canonical source unchanged; Linux full release gates not executable without Linux here']}
    (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'PASS: native Android S2 plus Stage 3, {len(corpus)} corpus executions, {len(rejections)} rejections', flush=True)


if __name__ == '__main__': main()
