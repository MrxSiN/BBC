#!/usr/bin/env python3
"""Audit the bounded tape-safety invariant for the *current* fixed-slot ELF backend.

The independent verifier checks literal x86-64 code bytes and branch targets.
This gate then checks the state invariant those templates are designed to
preserve and executes boundary witnesses. It does not prove the BF compiler's
own scratch-tape bookkeeping or future backends correct.
"""
import hashlib
import json
import pathlib
import struct
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'bootstrap'))
from transport import encode_source, extract_artifact
from verify_emission import verify_elf, TEMPLATES, START, STARTUP, SLOT

SOURCE = ROOT/'compiler/core.bf'
COMPILER = ROOT/'build/compiler_x86_64_linux.elf'
TAPE_BASE = 0x600000
TAPE_COUNT = 65536
TAPE_END = TAPE_BASE + TAPE_COUNT


def check_static_templates():
    # These are the complete native bytes allowed for the instructions which
    # modify the pointer or access the current cell. A changed opcode must
    # result in a failed gate, not an updated assumption without review.
    assert TEMPLATES[ord('>')] == bytes.fromhex('49ffc44d39f4720cb83c000000bf020000000f05')
    assert TEMPLATES[ord('<')] == bytes.fromhex('49ffcc4d39ec730cb83c000000bf020000000f05')
    assert TEMPLATES[ord('+')] == bytes.fromhex('41fe0424')
    assert TEMPLATES[ord('-')] == bytes.fromhex('41fe0c24')
    assert TEMPLATES[ord('.')] == bytes.fromhex('6a01586a015f4c89e66a015a0f0583f8fc74ed85c07f086a035f6a3c580f0590')
    assert TEMPLATES[ord(',')] == bytes.fromhex('41c604240031c031ff4c89e60f0583f8fc74f285c079086a045f6a3c580f0590')
    assert STARTUP == bytes.fromhex('49bc000060000000000049bd00006000000000004d8db5000001006a015a')
    # The code template's dereferences use r12, and neither template writes
    # r13 or r14. I/O passes r12 to read/write with exactly one byte.
    # Intel x86-64: inc r12; cmp r12,r14; jb +0c; exit(2) on the other path.
    # Intel x86-64: dec r12; cmp r12,r13; jae +0c; exit(2) on the other path.
    for template in TEMPLATES.values():
        assert len(template) <= SLOT
    return 6


def check_all_pointer_positions():
    # This is an exhaustive finite-state check of the *abstract* tape-index
    # rules, conditional on the exact machine byte encodings above.
    checked = 0
    traps = 0
    for index in range(TAPE_COUNT):
        old = TAPE_BASE + index
        plus = old + 1
        minus = old - 1
        if plus >= TAPE_END:
            assert index == TAPE_COUNT - 1
            traps += 1
        else:
            assert TAPE_BASE <= plus < TAPE_END
        if minus < TAPE_BASE:
            assert index == 0
            traps += 1
        else:
            assert TAPE_BASE <= minus < TAPE_END
        checked += 2
    assert traps == 2
    return checked, traps


def artifact_for(source):
    result = subprocess.run([str(COMPILER)],input=encode_source(source),
                            capture_output=True,check=True,timeout=90)
    elf = extract_artifact(result.stdout)
    return elf, verify_elf(source, elf)


def main():
    count = check_static_templates()
    positions, traps = check_all_pointer_positions()
    core = SOURCE.read_bytes()
    native_compiler = COMPILER.read_bytes()
    verified_compiler = verify_elf(core, native_compiler)
    assert verified_compiler['native_bounds_checks'] == sum(b in b'<>' for b in core)
    witnesses = [
        ('left_immediate', b'<', b'', 2, b''),
        ('left_after_right', b'><<', b'', 2, b''),
        ('left_in_loop', b'+[<]', b'', 2, b''),
        ('right_at_tape_end', b'+[>+]', b'', 2, b''),
        ('valid_pointer_shuttle', b'++[>+<-]>.', b'', 0, b'\x02'),
        ('zero_cell_skip', b'[<].', b'', 0, b'\x00'),
        ('input_output_cell', b',.,.', b'\xff', 0, b'\xff\x00'),
        ('nested_loop_branches', b'++[>++[>+++<-]<-]>>.', b'', 0, b'\x0c'),
        ('large_valid_source', b'+'*16128, b'', 0, b''),
    ]
    records=[]
    with tempfile.TemporaryDirectory(prefix='bf-tape-safety-') as tmp:
        target=pathlib.Path(tmp)/'case.elf'
        for name, source, stdin, exit_code, out in witnesses:
            artifact, structure=artifact_for(source)
            assert structure['writable_executable_segments'] == 0
            assert structure['tape_bytes'] == 65536
            target.write_bytes(artifact)
            target.chmod(0o700)
            run = subprocess.run([str(target)], input=stdin, capture_output=True, timeout=12)
            assert run.returncode == exit_code, (name, run.returncode, exit_code)
            assert run.stdout == out, (name,run.stdout,out)
            records.append({'case':name, 'native_exit':run.returncode,
                            'output_hex':run.stdout.hex(),'verified_slots':structure['verified_slots']})
        # All template changes that would remove a safety guard or alter the
        # segment mapping must fail the *read-only* machine-code verifier.
        source=b'><+-.,[]'
        artifact, _ = artifact_for(source)
        changes = [
            ('right_cmp', START+3),
            ('right_branch', START+7),
            ('left_cmp', START+SLOT+3),
            ('left_branch', START+SLOT+7),
            ('inc_cell_address', START+SLOT*2+2),
            ('dec_cell_address', START+SLOT*3+2),
            ('read_cell_address', START+SLOT*5+2),
            ('startup_tape_base', 0xb0+2),
            ('rx_segment_permission', 64+4),
            ('rw_segment_permission', 64+56+4),
        ]
        rejected=0
        for label, offset in changes:
            altered=bytearray(artifact)
            altered[offset] ^= 1
            try:
                verify_elf(source, bytes(altered))
            except ValueError:
                rejected+=1
            else:
                raise AssertionError(f'unsafe mutation accepted: {label}')
        assert rejected==len(changes)
    evidence={
        'date':'2026-10-12',
        'classification':'STRUCTURAL template-invariant audit + EXECUTED boundary witnesses; not a formal proof of the whole compiler',
        'core_sha256':hashlib.sha256(core).hexdigest(),
        'native_compiler_sha256':hashlib.sha256(native_compiler).hexdigest(),
        'profile':'Unsigned wrapping 8-bit cells; 65,536-cell fixed tape; pointer movement traps at both boundaries',
        'static_templates_checked':count,
        'abstract_guard_transitions_checked':positions,
        'abstract_invalid_boundary_transitions':traps,
        'native_witnesses_passed':len(records),
        'negative_mutations_rejected':rejected,
        'compiler_self_slots_checked':verified_compiler['verified_slots'],
        'compiler_self_branches_checked':verified_compiler['verified_branches'],
        'claims_excluded':['No proof of compiler-internal tape region separation','No proof for alternate or future backends','Assumes Linux x86-64 instruction and syscall semantics','No proof against malicious host or kernel'],
        'witnesses':records,
    }
    (ROOT/'evidence/tape_safety_audit.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(f'PASS {positions} abstract guarded pointer transitions, {len(records)} native witnesses, {rejected} unsafe template mutations rejected')


if __name__=='__main__':
    main()
