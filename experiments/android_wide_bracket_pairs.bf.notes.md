# BF wide bracket pairing — Iteration 28 experimental stage

**Source:** [`android_wide_bracket_pairs.bf`](android_wide_bracket_pairs.bf)  
**Source SHA-256:** `8b567cacefe8b500ea790ce6adde7287c254dd782c77f0eb3e2c00261953cd3c`  
**Filtered instruction SHA-256:** `24f029c671c408fdda6a659dc530f78dee0fac89b42592b481f9f9391b23be66`  
**Instruction count:** 1707  
**Linux native ELF:** [`../build/android_wide_bracket_pairs_x86_64_linux.elf`](../build/android_wide_bracket_pairs_x86_64_linux.elf)  
**Native ELF SHA-256:** `381e3bd03b051be2dc5f5abf8bb9671273c7d31c2570ef86b94e6af243b7d8f1`

This pass consumes **five-byte bracket metadata records** produced by
`android_wide_bracket_metadata.bf`. Each record starts with `5B` for opening
or `5D` for closing and contains a three-byte one-based command position and
one depth byte. The source stage ends with `00` plus one status byte. Input
records are trusted as emitted by the first BF stage; this module is not a
standalone hostile-record validator and does **not independently recheck**
record depths, position monotonicity or truncated fields.

For each closing bracket it writes **seven bytes**: `5D`, the opening position
as unsigned 24-bit little-endian, and the closing position in the same form.
It appends `00` and a final status byte. Nonzero statuses invalidate any
previous records. Encountered underflow/unclosed brackets are status `01`;
stack overflow is `03`. A nonzero upstream status is forwarded.

Cells 0–17 store input tag, run flag, error, comparison scratch, closing
position and active nesting. A tape stack starts at cell 32 with **five cells
per frame**: occupied flag; three source-position bytes; and the depth byte.
The sentinel at cell 27 stays zero. Stack depth 255 occupies through cell
1306, inside the standard V0 65,536-cell tape. BF instructions walk occupied
frames in steps of five, read incoming opening positions directly into the
current frame, and walk backward to the sentinel after push/pop. Closing
records pop their matching opening position from the stack; **no host code
performs bracket matching**. The implementation does not claim a whole-tape
formal safety proof, just this local bounded stack invariant and execution
checks.

## Execution evidence and scope

See [`../evidence/iteration28_wide_brackets.json`](../evidence/iteration28_wide_brackets.json) and [`../tests/verify_android_wide_brackets.py`](../tests/verify_android_wide_brackets.py). Stages were compiled from ordinary commented Brainfuck by the existing Linux-native BF compiler. Independent Python pairing is test-oracle-only, not in the production stage or adapter. These records have not been consumed by a general AArch64 displacement encoder. The Android emitter still accepts only ten commands; Android-native compiler and self-hosting are absent.
