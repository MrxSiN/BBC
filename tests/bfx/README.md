# BFX fixtures and verification

These are private bounded seed/reference fixtures. The public interface uses
[tests/compile](../compile/README.md) and u32 source frames.

Each `.request` is exact bounded compiler input. The matching `.bfx` is the complete
expected response, including compiler-error records. Read
[the wire contract](../../docs/02_BFX_CONTRACT.md) before changing fixture bytes.
BFX magic and identifier are part of the data; the extension alone does
not identify a valid module. Fixture bytes are protected from checkout
line-ending conversion by `.gitattributes`.

## Compiler fixtures

| Fixture | Expected compiler status | Payload count | Purpose |
|---|---|---|---|
| [all-eight](all-eight.request) | 0 | 8 | Preserve all eight instructions |
| [bad-close](bad-close.request) | 2 | None | Reject an unmatched closing bracket |
| [bad-open](bad-open.request) | 2 | None | Reject an unmatched opening bracket |
| [empty](empty.request) | 0 | 0 | Emit a valid ten-byte empty module |
| [nested](nested.request) | 0 | 18 | Preserve nested-loop structure |
| [raw-zero](raw-zero.request) | 0 | 2 | Ignore literal NUL and FF in known-length source |
| [safe-annotations](safe-annotations.request) | 0 | 2 | Ignore annotation text without changing commands |
| [truncated](truncated.request) | 1 | None | Reject a missing final terminator |
| [truncated-zero](truncated-zero.request) | 1 | None | Payload ends with NUL but final terminator is absent |
| [invalid-terminator](invalid-terminator.request) | 1 | None | Reject a present nonzero terminator other than one |
| [group-boundary](group-boundary.request) | 0 | 2 | A 257-byte source crosses the initial partial group and retains its final two commands |
| [opcode-bytes](opcode-bytes.request) | 0 | 8 | All 256 raw byte values retain exactly the eight instruction bytes in order |

Run [the compiler](../../compiler/compiler.bf) with each request under an
independent interpreter implementing [the profile](../../docs/01_BRAINFUCK_PROFILE.md).
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

## Current migration checks

All twelve request/response pairs use the canonical BFX signature, identifier
and u32 count. Empty success is ten bytes; failures are six. Both native targets
execute all twelve fixtures, and the independent interpreter agrees.

Static transformation data are [clear-cases.json](clear-cases.json),
[arithmetic-cases.json](arithmetic-cases.json) and
[movement-cases.json](movement-cases.json). They contain 10, 23 and 24 exact
binary input/output pairs, including negative rewrites, maximum counts and
invalid terminators. Each private pass requires a complete validated successful
BFX record of at most 3,840 instructions plus byte `01`. They are not independent
untrusted-record validators. Input and output use the same format.

The single canonical XAX decoder's 1,231 current cases include all identifier
values, payload-byte values, old signatures as rejection cases, framing,
maximum-count/depth, input preservation, guards and alignments. Legacy records
appear only as explicit negative inputs. Current decoder/importer sources and
case data are linked in [integration](../../docs/03_XAX_INTEGRATION.md).
Native program checks compare complete buffers with an independent BF reference.

[Current evidence](../../evidence/canonical_bfx.json) separates native target
execution from unchanged generic Windows-hosted SDK verification/lowering.
Historical reports remain byte-identical with their original source identities;
they are not reruns of the migrated implementation.
