# BFX fixtures and verification

Each `.request` is exact compiler input. The matching `.bfx` is the complete
expected response, including compiler-error records. Read
[the wire contract](../../docs/BFX_CONTRACT.md) before changing fixture bytes.
BFX magic and binary version are part of the data; the extension alone does
not identify a valid module. Fixture bytes are protected from checkout
line-ending conversion by `.gitattributes`.

## Compiler fixtures

| Fixture | Expected compiler status | Payload count | Purpose |
|---|---|---|---|
| [all-eight](all-eight.request) | 0 | 8 | Preserve all eight instructions |
| [bad-close](bad-close.request) | 2 | None | Reject an unmatched closing bracket |
| [bad-open](bad-open.request) | 2 | None | Reject an unmatched opening bracket |
| [empty](empty.request) | 0 | 0 | Emit a valid seven-byte empty module |
| [nested](nested.request) | 0 | 18 | Preserve nested-loop structure |
| [raw-zero](raw-zero.request) | 0 | 2 | Ignore literal NUL and FF in known-length source |
| [safe-annotations](safe-annotations.request) | 0 | 2 | Ignore annotation text without changing commands |
| [truncated](truncated.request) | 1 | None | Reject a missing final terminator |

Run [the compiler](../../compiler/compiler.bf) with each request under an
independent interpreter implementing [the profile](../../docs/BRAINFUCK_PROFILE.md).
Compare complete stdout byte for byte with the matching `.bfx`. A failed
compilation has no payload; do not import its error response as a decision.
When the frontend is a native decision component, check both the native call
result and the BFX compiler response: they are separate status interfaces.

## Program and bootstrap fixtures

| Program | Input / expected output | What it checks |
|---|---|---|
| [basic.bf](../basic.bf) | [basic.input](basic.input) / [basic.output](basic.output) | Byte wrap, literal zero and EOF after the supplied byte |
| [loops.bf](../loops.bf) | [loops.input](loops.input) / [loops.output](loops.output) | Nested loops and raw byte `04` |
| [decision.bf](../../examples/decision.bf) | [permit.input](permit.input) / [permit.output](permit.output) | Zero flag emits raw `01` |
| [decision.bf](../../examples/decision.bf) | [block.input](block.input) / [block.output](block.output) | Nonzero flag emits raw `00` |
| [bounds.bf](../bounds.bf) | Empty input; required bounds failure | Left move from cell zero |
| [bounds_right.bf](../bounds_right.bf) | Empty input; required bounds failure | Repeated right moves reach the tape boundary |

The [bootstrap fixtures](../bootstrap/) pair `.input` and `.output` files for
[frame_source.bf](../../bootstrap/frame_source.bf): empty, ordinary text and
NUL-terminated text. Compare all emitted bytes. Oversized text emits nothing;
known-length binary compiler input is a separate transport.

## Boundary and integration checks

External verification also covers the 65,535-byte raw-source limit,
3,840-instruction acceptance and 3,841-instruction rejection, 255-level nesting
acceptance and 256-level rejection, interpreted own-source output, and three
native frontend generations on each supported target.

XAX's [393 static decoder cases](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/decoder_cases.json)
contain record bytes, logical lengths, expected validation results and loop
pairs. The decoder and complete importer each execute that corpus on Android
and Windows. Cases include invalid lengths/magic/version, every payload-byte
value, limit cases, random opcode streams, input preservation and canaries.
Native decision checks compare an independent Brainfuck oracle and verify
output/tape effects on success and failure.

The independent interpreter, native-call transports and build drivers remain
outside BBC. They may execute programs, allocate buffers, compare results and
move files; they must not implement production parsing, optimization or BFX
translation. Their identities and hashes are recorded in the evidence reports.

- [Seed and decoder evidence](../../evidence/bfx_migration.json): 21 seed checks and 393 decoder calls per target.
- [Current importer/cycle evidence](../../evidence/bfx_android_importer.json): 393 importer cases per target, 89 Windows decision calls, three generations per target and 24 Android fixture checks.
- [Application evidence](../../evidence/bfx_retirement.json): eight Android Activity cases and canonical backend regressions.

These results describe the recorded source hashes. For any executable change,
rerun the relevant checks before updating [the current status](../../docs/STATUS.md).
