#!/usr/bin/env python3
"""Independent, read-only verification of the variable-length ELF x86-64 backend.

Decodes generated ELF structure and matches every instruction to the allowed
machine-code template for its input Brainfuck command. This is not a compiler:
it never emits/patches executables, and accepts only the current backend layout.
"""
import hashlib
import json
import pathlib
import random
import struct
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bootstrap'))
from transport import encode_source, extract_artifact

OPS = set(b'><+-.,[]')
SLOT = 32
START = 0xce
STARTUP = bytes.fromhex('49bc000060000000000049bd00006000000000004d8db5000001006a015a')
STOP = bytes.fromhex('b83c00000031ff0f05')
# Even the maximum 16,128-command program must fit inside the 512-KiB RX map.
assert START + 16128*SLOT + len(STOP) <= 524288
TEMPLATES = {
    ord('>'): bytes.fromhex('49ffc44d39f4720cb83c000000bf020000000f05'),
    ord('<'): bytes.fromhex('49ffcc4d39ec730cb83c000000bf020000000f05'),
    ord('+'): bytes.fromhex('41fe0424'),
    ord('-'): bytes.fromhex('41fe0c24'),
    ord('.'): bytes.fromhex('6a01586a015f4c89e66a015a0f0583f8fc74ed85c07f086a035f6a3c580f0590'),
    ord(','): bytes.fromhex('41c604240031c031ff4c89e60f0583f8fc74f285c079086a045f6a3c580f0590'),
}


def verify_elf(source: bytes, binary: bytes) -> dict:
    """Raise ValueError on unexpected ELF, instruction, or branch encoding."""
    # The in-core BF decoder discards ignored source bytes.
    program = bytes(byte for byte in source if byte in OPS)
    n = len(program)
    if n > 16128:
        raise ValueError('source exceeds current filtered-command capacity')
    minimum = START + n * SLOT + len(STOP)
    if len(binary) != minimum:
        raise ValueError(f'unexpected ELF file length: {len(binary)} != {minimum}')
    header = struct.unpack_from('<16sHHIQQQIHHHHHH', binary)
    ident, kind, machine, version, entry, phoff, shoff, flags, ehsize, phsize, phnum, *rest = header
    if (ident[:7] != b'\x7fELF\x02\x01\x01' or kind != 2 or machine != 62 or
        version != 1 or entry != 0x4000b0 or phoff != 64 or shoff != 0 or
        flags != 0 or ehsize != 64 or phsize != 56 or phnum != 2):
        raise ValueError('incorrect ELF64 header or entry point')
    phdrs = [struct.unpack_from('<IIQQQQQQ', binary, 64 + 56 * i) for i in range(2)]
    code, tape = phdrs
    if (code != (1,5,0,0x400000,0x400000,minimum,524288,4096) or
        tape != (1,6,0,0x600000,0x600000,0,65536,4096)):
        raise ValueError('executable or tape segment mapping changed')
    if len(binary) < code[5]:
        raise ValueError('RX PT_LOAD p_filesz exceeds actual ELF file length')
    if minimum > code[5]:
        raise ValueError('native entry, program and termination must be mapped executable')
    if binary[0xb0:START] != STARTUP:
        raise ValueError('unexpected native startup or tape-address setup')
    jump = {}
    stack = []
    for i, command in enumerate(program):
        if command == ord('['):
            stack.append(i)
        elif command == ord(']'):
            if not stack: raise ValueError('unmatched closing source bracket')
            opening = stack.pop()
            jump[opening] = i
            jump[i] = opening
    if stack: raise ValueError('unmatched opening source bracket')
    template_checks = 0
    branch_checks = 0
    for i, command in enumerate(program):
        slot = binary[START+i*SLOT:START+(i+1)*SLOT]
        if command in TEMPLATES:
            template = TEMPLATES[command]
        elif command in (ord('['), ord(']')):
            # Native Jcc displacement is calculated relative to next RIP.
            opcode = b'\x0f\x84' if command == ord('[') else b'\x0f\x85'
            dest = jump[i]+1 if command == ord('[') else jump[i]
            displacement = (dest-i)*SLOT-11
            template = b'\x41\x80\x3c\x24\x00' + opcode + struct.pack('<i', displacement)
            branch_checks += 1
        else:
            template = b''  # Noncommand: an executable no-op slot, not a new BF instruction
        expected = template + b'\x90'*(SLOT-len(template))
        if slot != expected:
            mismatch = next((j for j,(a,b) in enumerate(zip(slot, expected)) if a != b), 0)
            raise ValueError(f'opcode/branch mismatch: instruction {i} ({chr(command)}), slot byte {mismatch}')
        template_checks += 1
    if binary[START+n*SLOT:minimum] != STOP:
        raise ValueError('missing native exit(0)')
    return {
        'source_bytes': n,
        'decoded_commands': sum(b in OPS for b in program),
        'noncommand_nop_slots': sum(b not in OPS for b in program),
        'verified_slots': template_checks,
        'verified_branches': branch_checks,
        'tape_bytes': 65536,
        'rx_segment_bytes': code[5],
        'rw_segment_bytes': tape[6],
        'writable_executable_segments': 0,
        'native_bounds_checks': sum(b in (ord('<'),ord('>')) for b in program),
        'native_padding_bytes': 0,
        'elf_file_bytes': len(binary),
        'unbacked_rx_file_bytes': max(0, code[5]-len(binary)),
    }


def main():
    compiled = (ROOT / 'build/compiler_x86_64_linux.elf').read_bytes()
    core = (ROOT / 'compiler/core.bf').read_bytes()
    checks=[]
    first = verify_elf(core, compiled)
    checks.append({'case':'native_compiler_self', **first})
    examples = [b'', b'><+-.,[]', b'++[>++[>+++<-]<-]>>.', b'+'*16000+b'.', b'['*255+b']'*255+b'.', b'abc\x00\xff++.', b'+[comment<-]>.']
    rng = random.Random(40016)
    for _ in range(24):
        count = rng.randrange(1,120)
        body = bytes(rng.choice(tuple(b'><+-.,')) for _ in range(count))
        examples.append(b'[[]]' + body + b'[[-]]')
    for index,source in enumerate(examples):
        result = subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
                                input=encode_source(source),capture_output=True,check=True,timeout=60)
        elf=extract_artifact(result.stdout)
        analyzed=verify_elf(source,elf)
        checks.append({'case':f'compile_{index}',**analyzed})
    assert all(r['unbacked_rx_file_bytes'] == 0 for r in checks), 'short RX file discrepancy was not fixed'
    # Mutations must be rejected without executing potentially malicious code.
    sample=examples[2]
    result=subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
                          input=encode_source(sample),capture_output=True,check=True,timeout=30)
    actual=extract_artifact(result.stdout)
    for label,at in [('ELF permissions',64+4), ('startup read length', 0xb0+27), ('pointer guard', START+3*32),
                     ('loop branch', START+2*32+7), ('missing termination',START+len(sample)*32)]:
        tampered=bytearray(actual)
        tampered[at]^=1
        try:
            verify_elf(sample,tampered)
        except ValueError:
            pass
        else:
            raise AssertionError(f'verifier failed to catch corrupted {label}')
    # Truncated ELF backing and incorrect p_filesz must both fail.
    for label, mutated in [('truncated file', actual[:-1]),
                           ('wrong p_filesz', actual[:96] + b'\x00' + actual[97:])]:
        try:
            verify_elf(sample, mutated)
        except ValueError:
            pass
        else:
            raise AssertionError(f'verifier missed {label}')
    for cmd, label, jcc_delta in [(b'.', 'write failure check', 21), (b'.', 'write EINTR retry branch', 18), (b',', 'read failure check', 21), (b',', 'read EINTR retry branch', 18)]:
        result = subprocess.run([str(ROOT/'build/compiler_x86_64_linux.elf')],
                                input=encode_source(cmd), capture_output=True, check=True, timeout=30)
        artifact = extract_artifact(result.stdout)
        tampered = bytearray(artifact)
        tampered[START+jcc_delta] ^= 1
        try:
            verify_elf(cmd, tampered)
        except ValueError:
            pass
        else:
            raise AssertionError(f'verifier missed mutated {label}')
    report = {
        'date':'2026-10-12',
        'verification_class':'STRUCTURAL + EXECUTED: tested artifacts and negative mutations; not formal proof',
        'source_sha256':hashlib.sha256(core).hexdigest(),
        'native_compiler_sha256':hashlib.sha256(compiled).hexdigest(),
        'artifacts_verified':len(checks),
        'templates_verified':sum(r['verified_slots'] for r in checks),
        'branch_displacements_verified':sum(r['verified_branches'] for r in checks),
        'negative_mutations_rejected':11,
        'artifacts_with_short_rx_file':sum(r['unbacked_rx_file_bytes'] > 0 for r in checks),
        'limitations':'Only V1 fixed-slot instruction templates are checked. RX p_filesz equals exact ELF bytes; p_memsz stays 512 KiB. In-core comments are discarded; no formal memory safety proof.',
        'checks':checks,
    }
    (ROOT/'evidence/native_emission.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"PASS {len(checks)} native ELF structures, {report['templates_verified']} instructions, {report['branch_displacements_verified']} branches, 11 corruption checks")


if __name__ == '__main__':
    main()
