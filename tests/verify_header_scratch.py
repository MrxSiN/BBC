#!/usr/bin/env python3
"""Conditional source-level proof for the native ELF header writer's scratch cell.

This reads standard Brainfuck source as a verification subject; it does not
compile source programs or emit native code. The proof assumes the header block
starts at tape cell 60 with cell 61 cleared. Those entry conditions are checked
by independent BF interpreter instrumentation on executed inputs.
"""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'compiler/core.bf'
NOTES = ROOT / 'compiler/core.bf.notes.md'
EVIDENCE = ROOT / 'evidence/header_scratch_safety.json'
OPS = b'><+-.,[]'
BEGIN, END = 2848, 4277


def check_header(code: bytes):
    block = code[BEGIN:END]
    if len(block) != END - BEGIN or b',' in block:
        raise AssertionError('invalid header region or unexpected input')
    stack = []
    pointer = 60
    lowest = highest = pointer
    positions = {}
    matches = {}
    write_cells = set()
    for offset, op in enumerate(block):
        pc = BEGIN + offset
        positions[pc] = pointer
        if op == ord('['):
            stack.append((pc, pointer))
        elif op == ord(']'):
            if not stack:
                raise AssertionError('unmatched header close')
            opening, old_pointer = stack.pop()
            if pointer != old_pointer:
                raise AssertionError(f'loop at {opening} moves the pointer across iterations')
            matches[opening] = pc
        elif op in b'+-,':
            write_cells.add(pointer)
        if op == ord('>'):
            pointer += 1
        elif op == ord('<'):
            pointer -= 1
        lowest = min(lowest, pointer)
        highest = max(highest, pointer)
    if stack or pointer != 60 or (lowest, highest) != (60, 71):
        raise AssertionError('header escapes its fixed 60..71 cell range')
    if write_cells != {60, 61, 69, 70, 71}:
        raise AssertionError('header accesses undocumented arithmetic lanes')

    # Abstract execution independent of the value in cell 60 and the length of
    # source being compiled. Cell 61 is known zero at entry. Each scratch loop
    # must decrement a known counter and only update the unknown output cell.
    pc = BEGIN
    counter = 0
    multiply_loops = 0
    clear_loops = 0
    while pc < END:
        op = code[pc]
        at = positions[pc]
        if op == ord('['):
            close = matches[pc]
            body = code[pc + 1:close]
            if at == 61:
                if not (1 <= counter <= 255 and
                        re.fullmatch(rb'<[+-]+>-', body)):
                    raise AssertionError(f'noncanonical header scratch loop at {pc}')
                # The loop runs exactly counter times since it subtracts one
                # from cell 61 every iteration in unsigned 8-bit arithmetic.
                # No operation in the body can touch any cell except 60/61.
                counter = 0
                multiply_loops += 1
            elif at in (60, 69, 70, 71):
                if body != b'-':
                    raise AssertionError(f'noncanonical header clear loop at {pc}')
                clear_loops += 1
            else:
                raise AssertionError(f'loop condition uses unexpected cell {at}')
            pc = close + 1
            continue
        if op == ord(']'):
            raise AssertionError('unexpected isolated closing bracket')
        if at == 61 and op == ord('+'):
            counter = (counter + 1) % 256
        elif at == 61 and op == ord('-'):
            counter = (counter - 1) % 256
        pc += 1
    if counter != 0 or multiply_loops != 39 or clear_loops != 6:
        raise AssertionError('header scratch not cleared, or expected header loops changed')
    return {
        'source_block_start': BEGIN, 'source_block_end': END,
        'entry_pointer_precondition': 60, 'scratch_cell': 61,
        'scratch_entry_precondition': 0, 'scratch_exit_postcondition': 0,
        'minimum_pointer': lowest, 'maximum_pointer': highest,
        'cells_written': sorted(write_cells), 'loop_count': len(matches),
        'verified_scratch_multiplication_loops': multiply_loops,
        'verified_cell_clear_loops': clear_loops,
        'header_bf_sha256': hashlib.sha256(block).hexdigest(),
    }


def main():
    source = SOURCE.read_bytes()
    instructions = bytes(c for c in source if c in OPS)
    notes = NOTES.read_text()
    if f'Source SHA-256: `{hashlib.sha256(source).hexdigest()}`' not in notes:
        raise AssertionError('annotation source revision mismatch')
    ranges = [(int(a), int(b)) for a, b in re.findall(r'^\| `(\d+):(\d+)` \|', notes, re.M)]
    if (BEGIN, END) not in ranges:
        raise AssertionError('header region offsets no longer match the maintained notes')
    result = check_header(instructions)
    # Reject mutants in the header loop protocol and pointer excursion. This
    # guards against a checker accidentally accepting anything with 45 loops.
    mutations = [
        (instructions.index(b'[<+++++++++>-]', BEGIN, END) + 12, ord('+')),
        (BEGIN + 1, ord('>')),
        (instructions.index(b'[<+++++++++>-]', BEGIN, END) + 2, ord('>')),
        (END - 1, ord('+')),
    ]
    rejected = 0
    for offset, replacement in mutations:
        mutated = bytearray(instructions)
        assert mutated[offset] != replacement
        mutated[offset] = replacement
        try:
            check_header(mutated)
        except (AssertionError, KeyError):
            rejected += 1
        else:
            raise AssertionError(f'header mutation at {offset} was not rejected')
    audit = json.loads((ROOT / 'evidence/compiler_tape_audit.json').read_text())
    if (audit['source_sha256'] != hashlib.sha256(source).hexdigest() or
            audit.get('header_scratch_audit', {}).get('cases_with_clean_entry_exit') != 8):
        raise AssertionError('missing or stale executed header scratch precondition evidence')
    report = {
        'date': '2026-10-12',
        'classification': 'CONDITIONAL STATIC PROOF for isolated BF header block; EXECUTED entry preconditions on eight cases',
        'source_sha256': hashlib.sha256(source).hexdigest(),
        'method': 'Static pointer trace and 8-bit symbolic scratch counter interpretation of all header loops',
        'preconditions': [
            'Program counter enters BF offset 2848 once with tape pointer at 60',
            'Tape cell 61 holds zero before execution of the header block',
            'Original eight-instruction Brainfuck semantics with unsigned wrapping cells',
        ],
        'conclusion': 'Within the header block, every pointer stays in 60..71; all loops restore pointer, all 39 scratch loops terminate and clear cell 61; the block returns at pointer 60 with cell 61 zero, independently of the other initial tape values.',
        'checked_mutations_rejected': rejected,
        'runtime_entry_exit_witnesses': audit['header_scratch_audit']['cases_with_clean_entry_exit'],
        'limitations': [
            'Header entry preconditions are dynamically witnessed, not proven for every possible parser input',
            'This does not establish compiler-wide source-buffer and scratch ownership',
            'This does not prove native machine-code semantics or the correctness of emitted bytes',
        ],
        **result,
    }
    EVIDENCE.write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS conditional static header scratch proof: {result["verified_scratch_multiplication_loops"]} loops, '
          f'{rejected} mutants rejected, {report["runtime_entry_exit_witnesses"]} runtime precondition witnesses')


if __name__ == '__main__':
    main()
