#!/usr/bin/env python3
"""Transport for the BF-authored extended bounded Android ELF pipeline.

The Linux-native Brainfuck stages filter source, emit AArch64 instruction
slots and create the complete ELF image. This adapter only checks framing,
provenance and status and places the result atomically. The optional --loops path applies BF-owned wide branch records
inside the selected bounded ELF image layout. The two-byte BF table walker
is reused through 2,000 slots only with multiclass tape relocation.
Neither this transport adapter nor its tests generates branch instructions.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from transport import encode_source
from run_android_loops import SCAN_EVIDENCE, SCAN_STAGE, ROOT, run_stage, WIDE_STAGES, WIDE_EVIDENCE, WIDE_ENCODE_EVIDENCE

SLOT_SOURCE = ROOT / 'experiments/android_wide_slot_emitter.bf'
SLOT_NATIVE = ROOT / 'build/android_wide_slot_emitter_x86_64_linux.elf'
WRAP_SOURCE = ROOT / 'experiments/android_bounded_elf_wrapper.bf'
WRAP_NATIVE = ROOT / 'build/android_bounded_elf_wrapper_x86_64_linux.elf'
EVIDENCE = ROOT / 'evidence/iteration29_extended_slots.json'
PATCH_SOURCE = ROOT / 'experiments/android_wide_slot_patch.bf'
PATCH_NATIVE = ROOT / 'build/android_wide_slot_patch_x86_64_linux.elf'
PATCH_EVIDENCE = ROOT / 'evidence/iteration29_wide_slot_patch.json'
MAX_SOURCE_BYTES = 1_048_576
MAX_COMMANDS = 74
DYNAMIC_SOURCE = ROOT / 'experiments/android_dynamic_elf_wrapper.bf'
DYNAMIC_NATIVE = ROOT / 'build/android_dynamic_elf_wrapper_x86_64_linux.elf'
DYNAMIC_EVIDENCE = ROOT / 'evidence/iteration30_dynamic_elf.json'
MAX_DYNAMIC_COMMANDS = 255
PAGE_CLASS_SOURCE = ROOT / 'experiments/android_page_class_elf_wrapper.bf'
PAGE_CLASS_NATIVE = ROOT / 'build/android_page_class_elf_wrapper_x86_64_linux.elf'
PAGE_CLASS_EVIDENCE = ROOT / 'evidence/iteration31_page_class_elf.json'
MAX_PAGE_CLASS_COMMANDS = 512
MAX_MULTICLASS_COMMANDS = 1024
MAX_TAPE_RELOCATED_COMMANDS = 2719
TAPE_REBASE_SOURCE = ROOT / 'experiments/android_tape_rebase.bf'
TAPE_REBASE_NATIVE = ROOT / 'build/android_tape_rebase_x86_64_linux.elf'
TAPE_REBASE_EVIDENCE = ROOT / 'evidence/iteration35_tape_rebase.json'
MULTICLASS_SOURCE = ROOT / 'experiments/android_multiclass_elf_relayout.bf'
MULTICLASS_NATIVE = ROOT / 'build/android_multiclass_elf_relayout_x86_64_linux.elf'
MULTICLASS_EVIDENCE = ROOT / 'evidence/iteration34_multiclass_elf.json'
WIDE_255_SOURCE = ROOT / 'experiments/android_wide_slot_patch_255.bf'
WIDE_255_NATIVE = ROOT / 'build/android_wide_slot_patch_255_x86_64_linux.elf'
WIDE_255_EVIDENCE = ROOT / 'evidence/iteration32_wide_slot_patch_255.json'
MAX_WIDE_LOOP_COMMANDS = 512
MAX_TAPE_RELOCATED_LOOPS = 2719
EXTENDED_LOOP_EVIDENCE = ROOT / 'evidence/iteration36_wide_loops_2000.json'
CLASS8_SOURCE = ROOT / 'experiments/android_adrp_high_byte_class8.bf'
CLASS8_NATIVE = ROOT / 'build/android_adrp_high_byte_class8_x86_64_linux.elf'
CLASS8_EVIDENCE = ROOT / 'evidence/iteration45_android_class8.json'
WIDE_512_SOURCE = ROOT / 'experiments/android_wide_slot_patch_512.bf'
WIDE_512_NATIVE = ROOT / 'build/android_wide_slot_patch_512_x86_64_linux.elf'
WIDE_512_EVIDENCE = ROOT / 'evidence/iteration33_wide_slot_patch_512.json'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def check_provenance(allow_loops=False, dynamic=False, page_class=False, multiclass=False, tape_relocated=False):
    e = json.loads(EVIDENCE.read_text())
    scanner = json.loads(SCAN_EVIDENCE.read_text())
    for path, expected in ((ROOT / SCAN_STAGE[0], scanner['source_sha256']),
                           (ROOT / SCAN_STAGE[1], scanner['native_linux_elf_sha256']),
                           (SLOT_SOURCE, e['stages']['slots']['source_sha256']),
                           (SLOT_NATIVE, e['stages']['slots']['native_linux_elf_sha256']),
                           (WRAP_SOURCE, e['stages']['elf']['source_sha256']),
                           (WRAP_NATIVE, e['stages']['elf']['native_linux_elf_sha256'])):
        if sha(path.read_bytes()) != expected:
            raise ValueError(f'provenance mismatch: {path.relative_to(ROOT)}')
    if dynamic:
        e30 = json.loads(DYNAMIC_EVIDENCE.read_text())
        for path, key in ((DYNAMIC_SOURCE, 'source_sha256'),
                          (DYNAMIC_NATIVE, 'native_linux_elf_sha256')):
            if sha(path.read_bytes()) != e30['stage'][key]:
                raise ValueError(f'dynamic ELF provenance mismatch: {path.relative_to(ROOT)}')
    if tape_relocated:
        c8 = json.loads(CLASS8_EVIDENCE.read_text())
        for path, key in ((CLASS8_SOURCE, 'source_sha256'), (CLASS8_NATIVE, 'native_linux_elf_sha256')):
            if sha(path.read_bytes()) != c8[key]:
                raise ValueError(f'class-eight ADRP BF provenance mismatch: {path.relative_to(ROOT)}')
        record = json.loads(TAPE_REBASE_EVIDENCE.read_text())
        for path, key in ((TAPE_REBASE_SOURCE, 'source_sha256'),
                          (TAPE_REBASE_NATIVE, 'native_linux_elf_sha256')):
            if sha(path.read_bytes()) != record[key]:
                raise ValueError(f'tape rebase provenance mismatch: {path.relative_to(ROOT)}')
    if multiclass:
        p34 = json.loads(MULTICLASS_EVIDENCE.read_text())
        for path, key in ((MULTICLASS_SOURCE, 'source_sha256'),
                          (MULTICLASS_NATIVE, 'native_linux_elf_sha256')):
            if sha(path.read_bytes()) != p34[key]:
                raise ValueError(f'multiclass BF ELF provenance mismatch: {path.relative_to(ROOT)}')
    if page_class or multiclass:
        p = json.loads(PAGE_CLASS_EVIDENCE.read_text())
        for path, key in ((PAGE_CLASS_SOURCE, 'source_sha256'),
                          (PAGE_CLASS_NATIVE, 'native_linux_elf_sha256')):
            if sha(path.read_bytes()) != p['stage'][key]:
                raise ValueError(f'page class ELF provenance mismatch: {path.relative_to(ROOT)}')
    if allow_loops:
        if tape_relocated:
            proof = json.loads(EXTENDED_LOOP_EVIDENCE.read_text())
            for path, key in ((WIDE_512_SOURCE, 'source_sha256'),
                              (WIDE_512_NATIVE, 'native_linux_elf_sha256')):
                if sha(path.read_bytes()) != proof[key]:
                    raise ValueError(f'wide 2000 BF stage provenance mismatch: {path.relative_to(ROOT)}')
        if page_class or multiclass:
            p512 = json.loads(WIDE_512_EVIDENCE.read_text())
            for path, key in ((WIDE_512_SOURCE, 'source_sha256'),
                              (WIDE_512_NATIVE, 'native_linux_elf_sha256')):
                if sha(path.read_bytes()) != p512[key]:
                    raise ValueError(f'wide 512 patch provenance mismatch: {path.relative_to(ROOT)}')
        p255 = json.loads(WIDE_255_EVIDENCE.read_text())
        for path, key in ((WIDE_255_SOURCE, 'source_sha256'),
                          (WIDE_255_NATIVE, 'native_linux_elf_sha256')):
            if sha(path.read_bytes()) != p255[key]:
                raise ValueError(f'wide 255 patch provenance mismatch: {path.relative_to(ROOT)}')
        p = json.loads(PATCH_EVIDENCE.read_text())
        for path, expected in ((PATCH_SOURCE, p['source_sha256']),
                               (PATCH_NATIVE, p['native_linux_elf_sha256'])):
            if sha(path.read_bytes()) != expected:
                raise ValueError(f'wide patch stage provenance mismatch: {path.relative_to(ROOT)}')
        w = json.loads(WIDE_EVIDENCE.read_text())
        for name in ('wide_metadata', 'wide_pairs'):
            src, native = WIDE_STAGES[name]
            for path, key in ((ROOT/src, 'source_sha256'), (ROOT/native, 'linux_native_elf_sha256')):
                if sha(path.read_bytes()) != w['stages'][name][key]:
                    raise ValueError(f'{name}: wide stage provenance mismatch')
        b = json.loads(WIDE_ENCODE_EVIDENCE.read_text())
        src, native = WIDE_STAGES['wide_encode']
        if (sha((ROOT/src).read_bytes()) != b['source_sha256']
                or sha((ROOT/native).read_bytes()) != b['linux_native_elf_sha256']):
            raise ValueError('wide AArch64 encoding provenance mismatch')


def bf_native(binary, payload, stage):
    result = subprocess.run([str(binary)], input=payload, capture_output=True,
                            timeout=90, check=True)
    if result.stderr:
        raise ValueError(f'{stage}: unexpected stderr from Brainfuck stage')
    return result.stdout


def compile_source(source, check_hashes=True, allow_loops=False, dynamic=False, page_class=False, multiclass=False, tape_relocated=False):
    if sum(map(bool, (dynamic, page_class, multiclass))) > 1:
        raise ValueError('select only one ELF writer')
    if tape_relocated and not multiclass:
        raise ValueError('tape relocation requires the multiclass ELF writer')
    if len(source) > MAX_SOURCE_BYTES:
        raise ValueError('source exceeds the 1 MiB transport limit')
    if check_hashes:
        check_provenance(allow_loops=allow_loops, dynamic=dynamic, page_class=page_class, multiclass=multiclass, tape_relocated=tape_relocated)
    stream = run_stage('scan', encode_source(source))
    if len(stream) < 4 or stream[-1] != 0:
        raise ValueError('BF source scanner rejected input')
    commands = stream[:-4]
    count = int.from_bytes(stream[-4:-1], 'little')
    if count != len(commands):
        raise ValueError('BF scanner count mismatch')
    # The slot stage is still invoked for rejected bracket sources so its
    # own BF status, rather than Python syntax parsing, selects the rejection.
    command_limit = (MAX_TAPE_RELOCATED_COMMANDS if tape_relocated else
                     (MAX_MULTICLASS_COMMANDS if multiclass else
                     (MAX_PAGE_CLASS_COMMANDS if page_class else
                      (MAX_DYNAMIC_COMMANDS if dynamic else MAX_COMMANDS))))
    if count > command_limit:
        raise ValueError(f'extended Android ELF limited to {command_limit} commands')
    slots = bf_native(SLOT_NATIVE, commands, 'slots')
    if len(slots) < 5:
        raise ValueError('BF slot stage returned an incomplete frame')
    actual_count = int.from_bytes(slots[-5:-2], 'little')
    if actual_count != count or len(slots) != count*48 + 5 or slots[-2] != 0:
        raise ValueError('BF slot frame inconsistent with BF scanner count')
    if slots[-1] == 3 and not allow_loops:
        raise ValueError('BF bracket slots need relocation; enable the opt-in loop path')
    if slots[-1] not in ((0, 3) if allow_loops else (0,)):
        raise ValueError(f'BF slot stage rejected input with status {slots[-1]}')
    slot_bytes = slots[:-5]
    if allow_loops and slots[-1] == 3:
        # BF-owned patch tables use one-byte positions through 255 and two
        # bytes above it. Tape-relocated multiclass uses the existing
        # two-byte BF table walk through 2,719 rows. No host relocation.
        loop_limit = (MAX_TAPE_RELOCATED_LOOPS if tape_relocated else
                      (MAX_MULTICLASS_COMMANDS if multiclass else
                      (MAX_WIDE_LOOP_COMMANDS if page_class else
                       (MAX_DYNAMIC_COMMANDS if dynamic else MAX_COMMANDS))))
        if count > loop_limit:
            raise ValueError(f'BF loop relocation limited to {loop_limit} commands for this ELF writer')
        metadata = run_stage('wide_metadata', commands)
        if len(metadata) < 2 or (len(metadata)-2)%5 or metadata[-2:] != b'\0\0':
            raise ValueError('BF wide bracket metadata rejected source')
        pairs = run_stage('wide_pairs', metadata)
        if len(pairs) < 2 or (len(pairs)-2)%7 or pairs[-2:] != b'\0\0':
            raise ValueError('BF wide bracket matcher rejected source')
        encoded = run_stage('wide_encode', pairs)
        if (len(encoded) != (len(pairs)-2)//7*15+2
                or encoded[-2:] != b'\0\0'):
            raise ValueError('BF wide branch word encoder rejected source')
        # Format transport only. No host-created machine words, BF bracket
        # parsing, relocation layout, or rewriting of AArch64 code bytes.
        patch_binary = (WIDE_512_NATIVE if count > MAX_DYNAMIC_COMMANDS else
                        (WIDE_255_NATIVE if count > MAX_COMMANDS else PATCH_NATIVE))
        patch_count = (count.to_bytes(2, 'little') if count > MAX_DYNAMIC_COMMANDS else bytes([count]))
        patched = bf_native(patch_binary, patch_count+encoded+slot_bytes, 'wide-patch')
        if len(patched) != count*48+2 or patched[-2:] != b'\0\0':
            raise ValueError('BF wide slot patcher produced an invalid frame')
        slot_bytes = patched[:-2]
    wrapper_input = (count.to_bytes(2, 'little') if (page_class or multiclass) else bytes([count])) + slot_bytes
    writer = PAGE_CLASS_NATIVE if (page_class or multiclass) else (DYNAMIC_NATIVE if dynamic else WRAP_NATIVE)
    image = bf_native(writer, wrapper_input, 'elf')
    # The legacy page-class stage is reused as a BF-owned intermediate
    # for the third and fourth classes. The new BF stage computes final
    # offsets and page padding. Host code only frames preexisting bytes.
    if multiclass:
        intermediate_size = (len(image)-2 if tape_relocated else
                             (16480 if count <= 330 else (32864 if count <= 671 else 98400)))
        if (len(image) != intermediate_size + 2 or image[-2:] != b'\0\0'
                or image[:4] != b'\x7fELF'):
            raise ValueError('BF intermediate ELF stage returned an invalid frame')
        rx_length = 0x220 + 48 * count
        if rx_length > intermediate_size - 96:
            raise ValueError('BF intermediate ELF code overlaps the tape trailer')
        relayout_input = count.to_bytes(2, 'little') + image[:rx_length] + image[-98:-2]
        image = bf_native(MULTICLASS_NATIVE, relayout_input, 'multiclass-elf')
        expected_length = ((rx_length + 0x3fff) // 0x4000) * 0x4000 + 96
    else:
        expected_length = ((16480 if count <= 330 else 32864) if page_class else
                           (16480 if dynamic else 4192))
    if len(image) != expected_length+2 or image[-2:] != b'\0\0' or image[:4] != b'\x7fELF':
        raise ValueError('BF ELF wrapper rejected input or emitted invalid framing')
    if tape_relocated:
        import struct
        intermediate = image[:-2]
        # Framing copies four bytes already produced by the Brainfuck ELF
        # writer. The BF rebase stage, never Python, computes every modified
        # address, ADRP instruction, and 17-bit RX length.
        rw_offset = struct.unpack_from('<Q', intermediate, 0xf0)[0]
        if (rw_offset != expected_length - 96 or
                intermediate[0x200:0x204] != b'\x94\x00\x00\x90' or
                intermediate[0xf1] != (rw_offset >> 8) & 0xff or
                intermediate[0xf2] != (rw_offset >> 16) & 0xff):
            raise ValueError('BF intermediate ELF offset or startup contract mismatch')
        prefix = bytes(intermediate[i] for i in (0xf1, 0xf2, 0xd0, 0xd1))
        patched = bf_native(TAPE_REBASE_NATIVE, prefix + intermediate, 'tape-rebase')
        if len(patched) != expected_length+2 or patched[-2:] != b'\0\0' or patched[:4] != b'\x7fELF':
            raise ValueError('BF tape rebase output framing mismatch')
        image = patched
        # At the eighth aligned code size class, the BF tape rebase stage
        # writes ADRP immlo, but the immhi carry enters the next byte.
        # The opt-in BF correction stage rewrites that byte.  The host only
        # checks the trusted ELF frame and transports bytes; it never patches
        # AArch64 words. This class ends before RX length reaches 128 KiB.
        if 2379 <= count <= MAX_TAPE_RELOCATED_COMMANDS:
            if (expected_length != 131168 or rw_offset != 0x20000
                    or image[0x200:0x204] != b'\x14\x00\x00\x90'):
                raise ValueError('class-eight BF startup correction precondition failed')
            final = bf_native(CLASS8_NATIVE, image[:-2], 'class8-adrp')
            if (len(final) != expected_length+2 or final[-2:] != b'\0\0'
                    or final[0x200:0x204] != b'\x14\x01\x00\x90'):
                raise ValueError('BF class-eight startup correction failed')
            image = final
    return image[:-2]


def main():
    parser = argparse.ArgumentParser(description='Extended bounded Android ELF from BF native stages')
    parser.add_argument('source')
    parser.add_argument('image')
    parser.add_argument('--loops', action='store_true', help='use BF native wide loop slot patcher')
    writer = parser.add_mutually_exclusive_group()
    writer.add_argument('--dynamic', action='store_true', help='BF variable RX code length stage up to 255 commands')
    writer.add_argument('--page-class', action='store_true', help='BF two size class stage up to 512 commands including loops')
    writer.add_argument('--multiclass', action='store_true', help='BF relayout stage up to 1024 commands; combine with --tape-relocated for eight classes and 2719 commands')
    parser.add_argument('--tape-relocated', action='store_true', help='BF tape startup relocation and corrected ELF lengths for up to 2719 commands, including loops with --loops (requires --multiclass)')
    args = parser.parse_args()
    try:
        image = compile_source(Path(args.source).read_bytes(), allow_loops=args.loops, dynamic=args.dynamic, page_class=args.page_class, multiclass=args.multiclass, tape_relocated=args.tape_relocated)
        dst = Path(args.image)
        dst.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix='.android-extended-', dir=dst.parent)
        try:
            with os.fdopen(fd, 'wb') as fp:
                fp.write(image)
                fp.flush()
                os.fsync(fp.fileno())
            os.chmod(tmp, 0o700)
            os.replace(tmp, dst)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        raise SystemExit(f'extended Android compilation failed: {exc}') from exc
    print(f'Brainfuck-generated Android AArch64 ELF: {dst} ({len(image)} bytes)')


if __name__ == '__main__':
    main()
