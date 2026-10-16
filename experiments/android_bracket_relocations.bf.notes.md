# Android bracket-span resolver — Iteration 24

`android_bracket_relocations.bf` is a separate ordinary Brainfuck program. It is
not the Android compiler backend. It resolves matching nested brackets for a
**prefiltered command-only stream of at most ten commands**. No C or Python
parser executes in the resolution path. The existing Linux self-hosted BF
compiler compiles this source directly to a native Linux executable.

## Protocol

Input: at most ten ASCII bytes from `><+-.,[]`, followed by host EOF (which the
selected Brainfuck execution profile converts to zero). NUL also terminates
input; a containing transport must reject embedded NUL. Input length and
encoding must be validated by the caller; this is not a general-purpose
unbounded source parser. Ignored comments should be removed by the already
verified Brainfuck source filter before this stage.

Output: for each encountered **closing** bracket, write two raw bytes:

- `span`: one-based inclusive distance from its matching opening bracket
- `close`: one-based command position of the closing bracket

Then write a zero record terminator and one final status byte. Zero status
means valid balanced input within the ten-command capacity; any nonzero
status means failure. Output before a nonzero status is not a valid artifact.
Examples:

| Input | Output bytes (decimal) |
|---|---|
| `[]` | `2 2 0 0` |
| `[[]]` | `2 3 4 4 0 0` |
| `[+][-]` | `3 3 3 6 0 0` |
| `[` | `0 1` |

## Tape usage

The program uses cells 0–8 for the byte, one-based command index, equality
scratch and cumulative error status. Cell 19 is a temporary underflow marker,
20 is the zero sentinel, and cells 21 and above form the bounded stack. Each
stack entry stores the inclusive distance since the opening bracket, not a
source offset. On each new instruction the program increments all occupied
entries. Opening brackets push age 1; closing brackets pop and emit the age.
This makes nested and sequential loops straightforward without an indexed
memory primitive.

At most ten stack entries are needed for valid input. The proof is local to
the stated input contract; the source does not safely process arbitrary
unbounded streams. All command comparisons and bracket-stack operations are
implemented by the eight Brainfuck instructions.

## Relocation contract for future integration

The existing AArch64 prototype uses 48-byte command slots. Suppose its two
loop templates contain a cell load at offset 0 and a conditional branch at
offset 4. For a recorded span `s`:

- opening `CBZ` displacement in 4-byte words is `12*s - 1`
- closing `CBNZ` displacement in 4-byte words is `12*(2-s) - 1`
- opening slot position is `close - s + 1`

Both displacements are representable in signed AArch64 `imm19` for any valid
input within the ten-command bound. The tests verify that arithmetic as an
**independent oracle**; the Brainfuck Android ELF emitter does **not yet apply
these relocations**. The remaining work is to buffer source and relocation
records and emit patched native slots in command order, then execute the
result on an Android AArch64 target. The resolver itself is not a full
source-to-native compiler.

## Evidence

`python3 tests/verify_android_bracket_relocations.py` runs exhaustive
bracket-only streams of length up to ten, randomized mixed instruction
streams, malformed inputs and two independent standard Brainfuck interpreters.
The generated Linux-native executable is in
`build/android_bracket_relocations_x86_64_linux.elf`; results and hashes are in
`evidence/android_bracket_relocations.json`. This is **EXECUTED on Linux**,
not Android execution, target self-hosting or compiler-internal memory proof.
EOF and NUL semantics are the same as the existing experiments.
