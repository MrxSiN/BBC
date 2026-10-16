#!/usr/bin/env python3
"""Transport-only composition of Brainfuck-native AArch64 compiler stages.

Source filtering, bracket matching, branch encoding, slot selection, ELF
construction, and relocation application are all native Brainfuck programs.
This adapter performs byte transport, status checks, provenance checks, and
atomic file placement only. This is not an Android-executed compiler.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from transport import encode_source

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence/android_loop_pipeline.json'
SCAN_EVIDENCE = ROOT / 'evidence/iteration27_source_scan.json'
SCAN_STAGE = ('experiments/android_source_scan.bf', 'build/android_source_scan_x86_64_linux.elf')
WIDE_STAGES = {
    'wide_metadata': ('experiments/android_wide_bracket_metadata.bf', 'build/android_wide_bracket_metadata_x86_64_linux.elf'),
    'wide_pairs': ('experiments/android_wide_bracket_pairs.bf', 'build/android_wide_bracket_pairs_x86_64_linux.elf'),
    'wide_encode': ('experiments/android_wide_branch_encoding.bf', 'build/android_wide_branch_encoding_x86_64_linux.elf'),
}
WIDE_EVIDENCE = ROOT / 'evidence/iteration28_wide_brackets.json'
WIDE_ENCODE_EVIDENCE = ROOT / 'evidence/iteration28_wide_branch_encoding.json'
STAGES = {
    'filter': ('experiments/stream_filter.bf', 'build/stream_filter_x86_64_linux.elf'),
    'resolve': ('experiments/android_bracket_relocations.bf', 'build/android_bracket_relocations_x86_64_linux.elf'),
    'encode': ('experiments/android_branch_encoding.bf', 'build/android_branch_encoding_x86_64_linux.elf'),
    'mask': ('experiments/android_branch_mask.bf', 'build/android_branch_mask_x86_64_linux.elf'),
    'emit': ('experiments/android_aarch64_pie_subset.bf', 'build/android_pie_emitter_linux_x86_64.elf'),
    'apply': ('experiments/android_branch_apply.bf', 'build/android_branch_apply_x86_64_linux.elf'),
}


def run_stage(stage, payload):
    target = SCAN_STAGE if stage == 'scan' else (WIDE_STAGES[stage] if stage in WIDE_STAGES else STAGES[stage])
    process = subprocess.run([str(ROOT / target[1])], input=payload,
                             capture_output=True, timeout=30, check=True)
    if process.stderr:
        raise ValueError(f'{stage}: unexpected stderr')
    return process.stdout


def compile_source(source, check_hashes=True, stage_runner=run_stage, source_filter='filter', wide_brackets=False, wide_branches=False):
    if source_filter not in ('filter', 'scan'):
        raise ValueError('unknown Brainfuck source scanner mode')
    if len(source) > 1_048_576:
        raise ValueError('experimental transport limit is 1 MiB')
    if check_hashes:
        data = json.loads(EVIDENCE.read_text())
        for name, (src, binary) in STAGES.items():
            for label, path in (('source_sha256', src), ('elf_sha256', binary)):
                actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                if actual != data['stages'][name][label]:
                    raise ValueError(f'{name}: source or native executable hash mismatch')
    if source_filter == 'scan' and check_hashes:
        evidence = json.loads(SCAN_EVIDENCE.read_text())
        for path, expected in ((SCAN_STAGE[0], evidence['source_sha256']),
                               (SCAN_STAGE[1], evidence['native_linux_elf_sha256'])):
            if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != expected:
                raise ValueError('BF source scanner hash mismatch')
    filtered = stage_runner(source_filter, encode_source(source))
    if source_filter == 'scan':
        if len(filtered) < 4 or filtered[-1] != 0:
            raise ValueError('Brainfuck source scanner rejected input')
        commands = filtered[:-4]  # BF already filtered and counted commands.
        if int.from_bytes(filtered[-4:-1], 'little') != len(commands):
            raise ValueError('Brainfuck scanner output frame is inconsistent')
    else:
        if not filtered or filtered[-1] != 0:
            raise ValueError('Brainfuck source filter rejected input')
        commands = filtered[:-1]
    if wide_brackets or wide_branches:
        if check_hashes:
            evidence = json.loads(WIDE_EVIDENCE.read_text())
            for name in ('wide_metadata', 'wide_pairs'):
                src, binary = WIDE_STAGES[name]
                record = evidence['stages'][name]
                for label, path in (('source_sha256', src), ('linux_native_elf_sha256', binary)):
                    if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != record[label]:
                        raise ValueError(f'{name}: BF source or native executable hash mismatch')
        metadata = stage_runner('wide_metadata', commands)
        if len(metadata) < 2 or metadata[-2:] != b'\0\0':
            raise ValueError('wide Brainfuck metadata stage rejected source')
        pair_records = stage_runner('wide_pairs', metadata)
        if len(pair_records) < 2 or pair_records[-2:] != b'\0\0':
            raise ValueError('wide Brainfuck bracket pairing rejected source')
        # These optional records are BF-owned diagnostics only. The old
        # ten-slot relocation still constructs the emitted Android image.
        if wide_branches:
            if check_hashes:
                evidence = json.loads(WIDE_ENCODE_EVIDENCE.read_text())
                src, native = WIDE_STAGES['wide_encode']
                for file, label in ((src, 'source_sha256'), (native, 'linux_native_elf_sha256')):
                    if hashlib.sha256((ROOT / file).read_bytes()).hexdigest() != evidence[label]:
                        raise ValueError('BF wide branch encoding provenance mismatch')
            wide_encoded = stage_runner('wide_encode', pair_records)
            expected_length = ((len(pair_records) - 2) // 7) * 15 + 2
            if (len(wide_encoded) != expected_length or wide_encoded[-2:] != b'\x00\x00'):
                raise ValueError('wide Brainfuck AArch64 branch encoding rejected source')
    relocated = stage_runner('resolve', commands)
    if len(relocated) < 2 or relocated[-2:] != b'\0\0':
        raise ValueError('Brainfuck bracket resolver rejected source')
    words = stage_runner('encode', relocated)
    if len(words) < 2 or words[-2:] != b'\0\0':
        raise ValueError('Brainfuck branch encoder rejected source')
    masked = stage_runner('mask', commands)
    base = stage_runner('emit', masked)
    if len(base) != 4193 or base[-1] != 0:
        raise ValueError('Brainfuck AArch64 emitter rejected source')
    image = stage_runner('apply', words + base[:-1])
    if len(image) != 4193 or image[-1] != 0 or image[:4] != b'\x7fELF':
        raise ValueError('Brainfuck relocation applicator rejected image')
    return image[:-1]


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Experimental BF owned Android code pipeline')
    parser.add_argument('source')
    parser.add_argument('image')
    parser.add_argument('--scanner', action='store_true')
    parser.add_argument('--wide-brackets', action='store_true')
    parser.add_argument('--wide-branches', action='store_true',
                        help='verify BF-owned 26-bit AArch64 veneer records; legacy ten-slot image unchanged')
    args = parser.parse_args()
    try:
        mode = 'scan' if args.scanner else 'filter'
        image = compile_source(Path(args.source).read_bytes(), source_filter=mode,
                               wide_brackets=args.wide_brackets, wide_branches=args.wide_branches)
    except (OSError, ValueError, subprocess.SubprocessError) as e:
        raise SystemExit(f'experimental Android compilation failed: {e}') from e
    dst = Path(args.image);dst.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.android-branch-', dir=dst.parent)
    try:
        with os.fdopen(fd,'wb') as out:
            out.write(image);out.flush();os.fsync(out.fileno())
        os.chmod(tmp,0o700)
        os.replace(tmp,dst)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print(f'Experimental loop-capable AArch64 ELF by Brainfuck: {dst} ({len(image)} bytes)')


if __name__ == '__main__':
    main()
