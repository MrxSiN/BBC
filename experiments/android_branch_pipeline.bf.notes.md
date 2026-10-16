# Android branch pipeline tape and byte protocols

The authoritative machine encoding for this experiment is implemented in the
raw Brainfuck sources in this directory, not in the Python transport tool.
All six stage executables are compiled from standard Brainfuck by the Linux
self-hosted compiler. They are **not** merged into `compiler/core.bf`.

## Byte sequence

1. `stream_filter.bf` receives byte-stuffed source and emits ordinary commands
   plus a final status byte. Transport drops only the status, after checking
   zero. Input NUL and FF are escaped at the transport layer.
2. `android_bracket_relocations.bf` receives the filtered command stream
   and emits `(span, one-based closing index)` records, `00 00` on success.
   It rejects unmatched and more than ten commands.
3. `android_branch_encoding.bf` receives those pairs and emits records of
   `(one-based opening index, one-based closing index, forward branch word
   little endian 4 bytes, backward branch word little endian 4 bytes)`.
   It terminates with `00 00` on success or a nonzero status.
4. `android_branch_mask.bf` receives command-only source and substitutes
   `+` for brackets. This is compiler logic in Brainfuck: the host never
   converts source characters.
5. `android_aarch64_pie_subset.bf` receives the masked command stream and
   creates a 4,192-byte ELF64 PIE followed by a status byte.
6. `android_branch_apply.bf` receives the encoded relocation records
   followed by exactly the 4,192 image bytes. It outputs the patched ELF
   followed by a status byte. Nonzero means reject all output.

## Encoding and source limits

A bracket slot has 12 AArch64 instructions. The first is `LDRB W9, [X19]`,
then `CBZ` or `CBNZ` with a signed imm19 branch, followed by ten NOPs.
With inclusive loop span `s`, opening displacement is `12*s - 1`, closing
is `12*(2-s) - 1`, measured in 4-byte instruction units from the branch.
All displacement bytes are calculated by Brainfuck. An independent test oracle
checks these formulas and instruction words.

`android_branch_encoding.bf` uses tape cells 0 through 14. Cell 0 is span,
1 is close index, 2 is loop count, 3 is open index, 4 and 5 are the branch
second bytes, 6 is the common low byte, 7 and 8 are parity flags, and 9 is
copy scratch. It clears the open-index cell before each record: otherwise
nested and sequential loops produce incorrect accumulated indexes.

`android_branch_apply.bf` uses cells 100 onward as a ten-entry relocation
table. Each entry is nine cells: a reverse-walk sentinel, a moving count,
kind, four branch bytes, input scratch and a flag. An indexed traversal
consumes one-based slot indexes entirely in standard Brainfuck. The first
sentinel is zero, all later sentinels are one. The patcher copies 528 ELF
header/code prefix bytes, handles ten 48-byte slots and copies 3,184 suffix
bytes. Only bracket slots are rewritten. It trusts the previous BF resolver
to provide bounded, valid records and trusts the original BF emitter to
supply a complete base image; the transport checks both statuses and size.

No production build step uses the temporary development-time script that
helped arrange the raw Brainfuck source. The raw `.bf` files are the stored,
inspectable executable implementation.

## Evidence boundary

`tests/verify_android_aarch64_loops.py` runs reference interpretation,
AArch64 instruction simulation at two distinct load addresses, exhaustive
balanced bracket-only programs of length at most ten, negative cases,
independent BF seed comparisons and full-image byte checks. It writes
`evidence/android_loop_pipeline.json` with each source and ELF hash.

This is an experimental multi-process Linux-hosted compiler. It is not a
single native Android compiler, not a device-executed executable, not a
formal memory-safety proof, and not evidence that the generated PIE passes
Android's dynamic loader requirements.
