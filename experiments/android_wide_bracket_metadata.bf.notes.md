# BF wide bracket metadata — Iteration 28 experimental stage

**Source:** [`android_wide_bracket_metadata.bf`](android_wide_bracket_metadata.bf)  
**Source SHA-256:** `8e710936277ed825b8f25934d30432e2a05e414c858b7eeb7fed6bb4972b227d`  
**Filtered instruction SHA-256:** `dd1d810a78a748d157cd6fdaedece9319b32ea0cc67e7c6ac1da34e00ed897d1`  
**Instruction count:** 2524  
**Linux native ELF:** [`../build/android_wide_bracket_metadata_x86_64_linux.elf`](../build/android_wide_bracket_metadata_x86_64_linux.elf)  
**Native ELF SHA-256:** `03e8c6ab7652f8589f6a8ba57c61744683a9768df89e9b58d1e22c23a4fecf01`

This pass takes **prefiltered executable BF instruction bytes** ending at physical EOF.
It does not parse the byte-stuffed `FF01`/`FF02` protocol: run the existing BF scanner first.
All eight input instruction bytes are checked in BF. Other bytes cause status `01`.
For each bracket it writes five bytes: opening (`5B`) or closing (`5D`)
tag; **one-based 24-bit little-endian command position**; and nesting depth
from `01` to `FF`. A closing bracket records the depth *before* it pops.
Finally it writes `00` record terminator and one status byte.
`00` means balanced, `01` invalid byte/unbalanced bracket, `02` position counter
overflow, `03` nesting beyond 255. Output preceding a nonzero final status
must be thrown away.

Cells 0–9 handle input, loop flag, status, record tag and comparison scratch.
Cells 10–12 are the little-endian command index; cell 13 is active depth.
No source command buffer or dynamic stack is used at this stage. On each
instruction, the index increments with explicit byte carries. The deepest
accepted loop is 255 levels; a 256th opening bracket is rejected. Pointer
positions of this BF program remain in cells 0–13. The raw-source scanner's
independent 1 MiB transport cap is unrelated to this pass.

## Execution evidence and scope

See [`../evidence/iteration28_wide_brackets.json`](../evidence/iteration28_wide_brackets.json) and [`../tests/verify_android_wide_brackets.py`](../tests/verify_android_wide_brackets.py). Stages were compiled from ordinary commented Brainfuck by the existing Linux-native BF compiler. Independent Python pairing is test-oracle-only, not in the production stage or adapter. These records have not been consumed by a general AArch64 displacement encoder. The Android emitter still accepts only ten commands; Android-native compiler and self-hosting are absent.
