#!/usr/bin/env python3
"""Iteration 37: Android shell acceptance transport. Not a compiler or Android emulator.

Prepare reproducible BF-generated AArch64 executables and precise expected byte
streams. Run them on a user-supplied Android shell device through adb, and audit
actual output without ever treating simulated or fabricated results as device proof.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'bootstrap'), str(ROOT / 'tests')]
from run_android_extended import compile_source
from reference import execute


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fixtures() -> tuple[tuple[str, bytes, bytes], ...]:
    return (
        ('empty', b'', b''),
        ('binary_echo', b',.,.,.', bytes([0, 255, 127])),
        ('eof_zero', b',.', b''),
        ('nested_loops', b'++[>++[>+<-]<-]>>.', b''),
        ('page_331', b'+' * 327 + b'[-].', b''),
        ('page_672', b'+' * 668 + b'[-].', b''),
        ('page_1013', b'+' * 1009 + b'[-].', b''),
        ('page_1355', b'+' * 1351 + b'[-].', b''),
        ('page_1696', b'+' * 1692 + b'[-].', b''),
        ('loop_2000', (ROOT / 'examples/android_2000_loop_demo.bf').read_bytes(), b''),
        ('max_nesting', b'[' * 255 + b']' * 255, b''),
        ('left_trap', b'<', b''),
        ('right_trap', b'+[>+]', b''),
    )


def inspect_elf(image: bytes, count: int) -> dict:
    """Independent structural check. Not a substitute for the Android loader."""
    if len(image) < 0x220 or image[:7] != b'\x7fELF\x02\x01\x01':
        raise ValueError('not a little-endian ELF64 file')
    if struct.unpack_from('<HHI', image, 16)[:2] != (3, 183):
        raise ValueError('not an AArch64 PIE (ET_DYN)')
    entry, phoff = struct.unpack_from('<QQ', image, 24)
    phentsize, phnum = struct.unpack_from('<HH', image, 54)
    if (entry, phoff, phentsize, phnum) != (0x200, 64, 56, 5):
        raise ValueError('unexpected entry point or program-header table')
    ph = [struct.unpack_from('<IIQQQQQQ', image, phoff + i * phentsize)
          for i in range(phnum)]
    if [x[0] for x in ph] != [6, 3, 1, 1, 2]:
        raise ValueError('unexpected ELF program-header layout')
    rx, rw, dynamic = ph[2:]
    size = 0x220 + 48 * count
    aligned = (size + 0x3fff) & ~0x3fff
    if len(image) != aligned + 96:
        raise ValueError('incorrect ELF file size')
    if rx[1] != 5 or rx[2:7] != (0, 0, 0, size, size):
        raise ValueError('incorrect RX segment')
    if rw[1] != 6 or rw[2:7] != (aligned, aligned, aligned, 96, 65632):
        raise ValueError('incorrect RW/tape segment')
    if dynamic[2:7] != (aligned, aligned, aligned, 96, 96):
        raise ValueError('incorrect dynamic segment')
    if rw[3] < rx[3] + rx[6]:
        raise ValueError('RX and RW virtual ranges overlap')
    if any((x[1] & 0x3) == 0x3 for x in (rx, rw)):
        raise ValueError('writable executable segment')
    if any((x[2] % x[7]) != (x[3] % x[7]) for x in (rx, rw)):
        raise ValueError('invalid PT_LOAD congruence')
    if image[0x200:0x204] != struct.pack('<I', 0x90000014 + (aligned // 0x4000) * 32):
        raise ValueError('startup ADRP does not address the tape page')
    if image[size:aligned] != bytes(aligned - size):
        raise ValueError('nonzero code padding')
    if b'/system/bin/linker64\x00' not in image[:0x200]:
        raise ValueError('expected Android linker is missing')
    return {'rx_bytes': size, 'rw_offset': aligned, 'tape_address_rva': aligned + 96,
            'elf_bytes': len(image), 'interpreter': '/system/bin/linker64'}


def expected_behavior(source: bytes, data: bytes) -> tuple[bytes, int]:
    try:
        out, _ = execute(source, data, max_steps=400_000)
        return out, 0
    except IndexError:
        # The trap fixtures do not output before crossing the boundary.
        return b'', 2


def prepare(destination: Path) -> dict:
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('destination must be absent or an empty directory')
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for name, source, data in fixtures():
        out, exitcode = expected_behavior(source, data)
        image = compile_source(source, allow_loops=b'[' in source,
                               multiclass=True, tape_relocated=True)
        info = inspect_elf(image, len(source))
        (destination / (name + '.elf')).write_bytes(image)
        (destination / (name + '.stdin')).write_bytes(data)
        records.append({'id': name, 'command_count': len(source),
                        'source_sha256': digest(source),
                        'elf_sha256': digest(image),
                        'stdin_sha256': digest(data),
                        'expected_stdout_hex': out.hex(),
                        'expected_exit_code': exitcode, **info})
    manifest = {'schema': 1, 'iteration': 37, 'target': 'android-aarch64-shell',
                'evidence_class': 'PREPARED_NOT_EXECUTED',
                'production_codegen': 'standard Brainfuck Linux-native stages',
                'device_execution_claim': False, 'cases': records}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    # Device shell writes output to files so binary zero bytes, stderr and exit
    # statuses remain distinguishable. Paths are fixed identifiers, not input.
    lines = ['#!/system/bin/sh', 'set -u', 'cd "$(dirname "$0")" || exit 90',
             'mkdir -p results || exit 91']
    for record in records:
        name = record['id']
        lines.extend((f'chmod 700 ./{name}.elf',
                      f'./{name}.elf < ./{name}.stdin > ./results/{name}.stdout 2> ./results/{name}.stderr',
                      f'printf "%s\\n" "$?" > ./results/{name}.exitcode'))
    lines.append('printf "TESTS_FINISHED\\n"')
    (destination / 'run.sh').write_text('\n'.join(lines) + '\n')
    (destination / 'run.sh').chmod(0o755)
    return manifest


def audit(manifest: dict, results: Path) -> dict:
    outcomes = []
    for rec in manifest['cases']:
        name = rec['id']
        try:
            status_text = (results / (name + '.exitcode')).read_text().strip()
            if not status_text.isdigit():
                raise ValueError('status not a decimal integer')
            status = int(status_text)
            actual = (results / (name + '.stdout')).read_bytes()
            stderr = (results / (name + '.stderr')).read_bytes()
            valid = status == rec['expected_exit_code'] and actual == bytes.fromhex(rec['expected_stdout_hex'])
            reason = 'match' if valid else 'status or exact stdout mismatch'
        except (OSError, ValueError) as exc:
            status, stderr, actual, valid, reason = None, b'', b'', False, f'missing/invalid evidence: {exc}'
        outcomes.append({'id': name, 'passed': valid, 'actual_status': status,
                         'stdout_sha256': digest(actual) if status is not None else None,
                         'stderr_sha256': digest(stderr) if status is not None else None,
                         'reason': reason})
    return {'evidence_class': 'UNATTESTED_RESULT_FILES',
            'cases': outcomes, 'passed': sum(x['passed'] for x in outcomes),
            'total': len(outcomes), 'all_passed': all(x['passed'] for x in outcomes)}


def run_device(bundle: Path, destination: Path, adb: str, serial: str | None):
    manifest = json.loads((bundle / 'manifest.json').read_text())
    for rec in manifest['cases']:
        name = rec['id']
        for extension, key in (('.elf', 'elf_sha256'), ('.stdin', 'stdin_sha256')):
            if digest((bundle / (name + extension)).read_bytes()) != rec[key]:
                raise ValueError(f'input integrity mismatch for {name}{extension}')
        inspect_elf((bundle / (name + '.elf')).read_bytes(), rec['command_count'])
    if shutil.which(adb) is None and not Path(adb).exists():
        raise RuntimeError('adb unavailable; Android loader execution not performed')
    prefix = [adb] + (['-s', serial] if serial else [])
    def command(args, **kw):
        return subprocess.run(prefix + args, check=True, capture_output=True, **kw)
    props = {}
    for key in ('ro.product.cpu.abi', 'ro.build.version.sdk', 'ro.build.fingerprint'):
        props[key] = command(['shell', 'getprop', key]).stdout.decode('utf-8', 'replace').strip()
    if not props['ro.product.cpu.abi'].startswith('arm64'):
        raise RuntimeError('device is not an arm64 Android shell target')
    remote = '/data/local/tmp/bfc_iteration37'
    command(['shell', 'mkdir', '-p', remote + '/results'])
    for file in sorted(bundle.iterdir()):
        if file.is_file():
            command(['push', str(file), remote + '/' + file.name])
    # Read every uploaded executable and stdin stream back before execution.
    # This prevents a successful adb push from being mistaken for byte parity.
    with tempfile.TemporaryDirectory(prefix='bf_android_remote_verify_') as tmp:
        for rec in manifest['cases']:
            for extension, key in (('.elf', 'elf_sha256'), ('.stdin', 'stdin_sha256')):
                filename = rec['id'] + extension
                command(['pull', remote + '/' + filename, str(Path(tmp) / filename)])
                if digest((Path(tmp) / filename).read_bytes()) != rec[key]:
                    raise RuntimeError(f'Android transfer mismatch: {filename}')
    run = command(['shell', 'sh', remote + '/run.sh'])
    if b'TESTS_FINISHED' not in run.stdout:
        raise RuntimeError('device script did not reach final test marker')
    destination.mkdir(parents=True, exist_ok=True)
    for rec in manifest['cases']:
        for suffix in ('.stdout', '.stderr', '.exitcode'):
            name = rec['id'] + suffix
            command(['pull', remote + '/results/' + name, str(destination / name)])
    report = audit(manifest, destination)
    report.update({'evidence_class': 'ANDROID_DEVICE_EXECUTED',
                   'device_properties': props,
                   'device_shell_command': 'sh ' + remote + '/run.sh',
                   'adb_pushed_files_pulled_and_hash_verified': True,
                   'manifest_sha256': digest((bundle / 'manifest.json').read_bytes())})
    (destination / 'device_verification.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    p = subs.add_parser('prepare'); p.add_argument('bundle', type=Path)
    p = subs.add_parser('run-device'); p.add_argument('bundle', type=Path); p.add_argument('results', type=Path)
    p.add_argument('--adb', default='adb'); p.add_argument('--serial')
    p = subs.add_parser('audit'); p.add_argument('bundle', type=Path); p.add_argument('results', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'prepare':
            report = prepare(args.bundle)
            print(f'Prepared {len(report["cases"])} BF-generated Android ELF cases; NO DEVICE RUN')
        elif args.action == 'run-device':
            report = run_device(args.bundle, args.results, args.adb, args.serial)
            print(json.dumps({'device_executed': True, 'all_passed': report['all_passed'],
                              'passed': report['passed'], 'total': report['total']}))
            if not report['all_passed']:return 1
        else:
            report = audit(json.loads((args.bundle / 'manifest.json').read_text()), args.results)
            print(json.dumps(report, indent=2))
            if not report['all_passed']:return 1
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        print(f'Android acceptance error: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
