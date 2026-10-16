#!/usr/bin/env python3
"""Independent native-word oracle, differential semantics and Android witnesses."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'bootstrap'), str(ROOT / 'tools'), str(ROOT / 'tests')]
from android_device import DeviceRunner, BUILD, REMOTE
from local_seed import LocalSeedRunner
from run_android_loops import compile_source
from run_android_optimized import OPTIMIZERS, compile_optimized_source
from source_check import check_source
from transport import encode_source
from reference import execute
from verify_android_aarch64_subset import check_elf, emulate, NOP

PATTERNS = {b'[-]': 1, b'[+]': 1, b'[>+<-]': 2, b'[->+<]': 3,
            b'[<+>-]': 4, b'[-<+>]': 5}


def oracle(base, source):
    image = bytearray(base)
    image[120:124] = bytes(4)
    for index in range(len(source)):
        for pattern, kind in PATTERNS.items():
            if not source[index:].startswith(pattern):
                continue
            if kind == 1:
                words = [0x3900027f, 0x14000023] + [NOP] * 10
            else:
                left = kind >= 4
                words = [0x39400269, 0x340008e9, 0xd100066a if left else 0x9100066a,
                         0xcb14014a, 0xf140415f,
                         0x54000162 if kind in (2, 4) else 0x540002e2,
                         0x385ff26a if left else 0x3940066a, 0x0b09014a,
                         0x381ff26a if left else 0x3900066a, 0x3900027f,
                         0x1400003e, NOP]
            start = 0x210 + index * 48
            image[start:start + 48] = struct.pack('<12I', *words)
    recognized = {index for index in range(len(source))
                  if any(source[index:].startswith(pattern) for pattern in PATTERNS)}
    bounded = all(char != 91 or index in recognized for index, char in enumerate(source))
    if bounded:
        image[232:236] = bytes(4)
        image[288:292] = bytes(4)
        struct.pack_into('<4I', image, 512, 0xd10043ff, 0x910003f4, 0xaa1403f3, 0xa9007fff)
        for index, char in enumerate(source):
            if char == 62:
                struct.pack_into('<2I', image, 0x210 + 48 * index, 0x91000673, 0x1400000b)
    if source.startswith((b',[>+<-]', b',[->+<]')):
        struct.pack_into('<12I', image, 0x240, 0x39400269, 0x39000669,
                         0x3900027f, 0x14000045, *([NOP] * 8))
    for index in range(len(source), 10):
        struct.pack_into('<I', image, 0x210 + 48 * index, 0x14000000 | (12 * (10-index)))
    return bytes(image)


def main():
    runner = LocalSeedRunner()
    for source, _ in OPTIMIZERS.values():
        assert len(check_source((ROOT / source).read_bytes())) <= 16128
    programs = [b'', b'+', b'-', b'.', b'<', b'>', b'+++.', b'[]',
                b'[-]', b'[+]', b'+[-].', b'-[+].', b',[-].', b',[+].',
                b',[>+<-]>.', b',[->+<]>.', b'>,[-<+>]<.', b'>,[<+>-]<.',
                b',[->+<].', b'>,[-<+>].', b'>+<+[->+<]', b'>+<[->+<]',
                b',[[-]].', b',[+][-].', b'[-][-][-]', b'+++++++[-]', b'[[][]]',
                b'+[+]', b',[.-]', b'>[-]<.', b',.,.', b'+[->+<]>.', b'[>][->+<]',
                b'>>>>>>>>>>', b'<<<<<<<<<', b',[->+<][>]', b'>+<,[->+<]']
    count = 0
    seed_checks = 0
    improvement = {}
    for program in programs:
        base = compile_source(program, stage_runner=runner)
        if program in (b'', b'[]', b',[>+<-]>.'):
            image = compile_optimized_source(program, stage_runner=runner, check_hashes=False)
        else:
            result = runner('optimize', program + b'\0' + base)
            assert len(result) == 4193 and result[-1] == 0
            result = runner('resources', program + b'\0' + result[:-1])
            assert len(result) == 4193 and result[-1] == 0
            image = result[:-1]
        assert image == oracle(base, program), program
        check_elf(image, static=True, tape_on_stack=image[232:236] == bytes(4))
        runner.seed = 'seed_alt'
        second = runner('optimize', program + b'\0' + base)
        assert second[-1] == 0 and len(second) == 4193
        second = runner('resources', program + b'\0' + second[:-1])
        runner.seed = 'seed'
        assert second == image + b'\0', program
        seed_checks += 1
        for data in (b'', b'\0', b'\1', b'\xad', b'\xff', b'\x80\xff'):
            reference_tape = bytearray()
            try:
                expected, _ = execute(program, data, max_steps=100000, tape_snapshot=reference_tape)
                status = 0
            except IndexError:
                expected, status = b'', 2
            for bias in (0, 0x40000000):
                actual_tape = bytearray()
                actual, exit_code, steps = emulate(image, bias, input_bytes=data, max_steps=100000,
                                                   tape_snapshot=actual_tape)
                assert (actual, exit_code) == (expected, status), (program, data, actual, exit_code)
                if status == 0:assert actual_tape == reference_tape, (program, data)
                count += 1
            if program == b',[>+<-]>.' and data == b'\xff':
                _, _, old_steps = emulate(base, 0, input_bytes=data, max_steps=100000)
                improvement = {'input_hex': data.hex(), 'old_instructions': old_steps,
                               'optimized_instructions': steps, 'ratio': old_steps / steps}
        # Force write/read faults independently of ordinary byte comparisons.
        if b'.' in program and program != b'<':
            _, code, _ = emulate(image, 0, input_bytes=b'\1', fail_write=True, max_steps=100000)
            assert code in (2, 3), program
        if b',' in program:
            _, code, _ = emulate(image, 0, fail_read=True, max_steps=100000)
            assert code == 4, program
    print(f'PASS {count} simulated comparisons, {seed_checks} independent BF seed images', flush=True)

    # Bounds remain conditional: zero skips the original body, nonzero traps.
    boundary_checks = 0
    for program, initial in [(b'+,[->+<]', 65535), (b',[-<+>]', 0),
                             (b'+,[>+<-]', 65535), (b',[<+>-]', 0)]:
        image = compile_optimized_source(program, stage_runner=runner, check_hashes=False)
        for value in (0, 1, 255):
            for bias in (0, 0x40000000):
                out, code, _ = emulate(image, bias, initial_pointer=initial,
                                       input_bytes=bytes([value]), max_steps=100000)
                assert out == b'' and code == (2 if value else 0)
                boundary_checks += 1

    device = DeviceRunner()
    native_checks = 0
    for index, program in enumerate([b',[>+<-]>.', b',[->+<]>.', b'>,[-<+>]<.', b'>,[<+>-]<.']):
        image = compile_optimized_source(program, stage_runner=runner, check_hashes=False)
        path = BUILD / f'transfer{index}'
        path.write_bytes(image)
        device.push(path, path.name)
        device.shell(f'chmod 700 {REMOTE}/{path.name}')
        # Device-local batches exercise every byte, including binary newlines.
        result = device.shell(f'for v in $(seq 0 255); do '
                              f'/data/local/tmp/brainfuck-bench/sample "$v" {REMOTE}/{path.name} || exit; done')
        assert len(result.stdout.splitlines()) == 256
        device.shell(f'/data/local/tmp/brainfuck-bench/sample -1 {REMOTE}/{path.name}')
        native_checks += 257
    for label, program, code in [('empty', b'', 0), ('nested', b'[[]]', 0),
                                 ('left', b'<', 2), ('right', b'+[>+]', 2)]:
        path = BUILD / label
        path.write_bytes(compile_optimized_source(program, stage_runner=runner, check_hashes=False))
        device.push(path, label)
        device.shell(f'chmod 700 {REMOTE}/{label}')
        result = subprocess.run(device.adb + ['shell', '-T', f'{REMOTE}/{label}'],
                                capture_output=True, timeout=30)
        assert (result.returncode, result.stdout) == (code, b''), label
        native_checks += 1
    print(f'PASS {native_checks} Android executions and {boundary_checks} simulated edge cases', flush=True)

    # Both independent BF interpreters execute core.bf to compile the optimizer.
    optimizers = {}
    for name, (source, binary) in OPTIMIZERS.items():
        source_path = ROOT / source
        commands = check_source(source_path.read_bytes())
        binaries = []
        for seed in ('seed', 'seed_alt'):
            runner.seed = seed
            output = runner('core', encode_source(source_path.read_bytes()))
            assert output[-1] == 0 and output[:4] == b'\x7fELF'
            binaries.append(output[:-1])
            print(f'PASS {seed}: core.bf compiled {name} to Linux ELF', flush=True)
        assert binaries[0] == binaries[1] and len(binaries[0]) == 215 + 32 * len(commands)
        (ROOT / binary).write_bytes(binaries[0])
        optimizers[name] = {'source_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
                            'source_instructions': len(commands),
                            'linux_optimizer_sha256': hashlib.sha256(binaries[0]).hexdigest(),
                            'linux_optimizer_bytes': len(binaries[0])}
    report = {'date': '2026-10-12',
              'classification': 'EXECUTED native optimized static PIE on Android; Linux optimizer ELF cross-built, not executed here',
              'compiler_source_sha256': hashlib.sha256((ROOT / 'compiler/core.bf').read_bytes()).hexdigest(),
              'seed_execution_host': 'Windows x86-64, MSVC /O2 independent BF interpreters',
              'seed_source_sha256': {name: hashlib.sha256((ROOT / 'bootstrap' / name).read_bytes()).hexdigest()
                                     for name in ('seed_interpreter.c', 'seed_interpreter_alt.c')},
              'native_image_sha256': {name: hashlib.sha256((BUILD / name).read_bytes()).hexdigest()
                                      for name in ['transfer0', 'transfer1', 'transfer2', 'transfer3',
                                                   'empty', 'nested', 'left', 'right']},
              'optimizers': optimizers, 'independent_seed_images': seed_checks,
              'simulated_comparisons': count, 'simulated_boundary_checks': boundary_checks,
              'android_executions': native_checks, 'transfer_instruction_reduction': improvement,
              'static_pie_loader_executed': True, 'source_limit_commands': 10,
              'limitations': ['Bounded prototype, no general affine analysis or Android compiler selfhosting',
                              'Upstream BF validation supplies ten-command source and complete trusted images',
                              'Linux release gates unavailable on this Windows host; production core.bf unchanged']}
    (ROOT / 'evidence/android_native_optimization.json').write_text(json.dumps(report, indent=2) + '\n')
    print('PASS optimizer purity, ELF byte oracle, error semantics, seed bootstrap and device execution')


if __name__ == '__main__':
    main()
