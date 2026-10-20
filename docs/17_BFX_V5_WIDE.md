# Wide compilation and streaming run optimization

**BFX v5 is a separate bounded wide profile.** It connects native BF chunk
filtering, a canonical XAX coordinator, optional streaming BF run packing,
native defensive import, full graph verification and native packaging. The
original source-request interface and BFX v1-v4 remain unchanged.
The maintained [canonical XAX sources and transaction replay](https://github.com/MrxSiN/XAX/blob/85abd4640439c748374dce79cb54bfecb406cedf/compiler/integration/bfx/wide/README.md)
pin the native coordination and import implementation.

This profile closes the previously reproduced Mandelbrot capacity failure.
The 11,669-byte Brainfry source contains 11,451 instructions. Transparent and
packed stores compile to standalone programs with exact 6,240-byte expected
output on the required targets, as scoped in the execution evidence below.
Packing reduces that source to 5,172 instructions. This is correctness and
coverage evidence; it is not a counterbalanced performance comparison.

## Record and capacities

A successful module is `BFX || 05 || 00 || instruction_count:u32le || payload`.
Its exact length is `9 + instruction_count`. Version five accepts exactly the
v4 opcode set, including CLEAR and arithmetic/movement powers. No target or
unsafe-memory permission is encoded. The importer validates the complete
record independently, including length, status, opcodes and bracket pairing.

The delivered native profile has these explicit budgets:

| Resource | Capacity |
|---|---:|
| Raw source | 1,048,576 bytes |
| Source chunk | 32,768 bytes |
| Instructions before optional packing | 65,536 |
| Valid maximum nesting within that instruction budget | 32,768 |
| Decoder loop-pair entries | 65,536 u32 values |
| Decoder opening-stack entries | 65,536 u32 values |
| Compiled program tape | 65,536 byte cells |

The loop stack uses wide indices; 65,536 unmatched opening brackets fill it
and then fail balance validation. A balanced source cannot nest more deeply
than half its instruction count. Source with 65,537 instructions is rejected
even if packing could later remove most of them. These are implementation
budgets, not unlimited allocation or changes to Brainfuck semantics.

Only successful native termination and a nonzero returned length authorize
publication of a success record. On any error the entire provisional buffer
is discarded. Native coordinator failure is a scalar status, not a portable
BFX error record. The coordinator stops on the first failing chunk; v1's
whole-frame multi-error precedence is not redefined for this separate API.

## Canonical coordinator interfaces

The source coordinator borrows four distinct live initialized views. Each
typed argument is pointer, exact extent-bearing view and memory frontier;
all triples return with their updated frontiers. Raw ABI exports erase proofs.

`compile_source(source_workspace, record, output_workspace, tape_workspace)`

Source, output and tape workspace views each span 1,114,112 bytes. The record
view spans 65,545 bytes. Before calling, place raw source at source-workspace
offset 65,536 and write its u32 byte length into record bytes 0..3. The source
coordinator copies bounded chunks into the first 65,536 workspace bytes and
calls the BF filter. Raw source bytes remain unchanged. BF still uses its
65,536-cell execution tape and resets that entire prefix on each invocation.
The larger typed views do not enlarge BF's pointer or logical I/O limits.

Return is `(record_length << 32) | status`. Zero status succeeds; source/record
budget failures return 3, bracket errors 2 and component/protocol failures 4.
The private filter also retains its framing status 1. No output prefix may be
published after failure. A logical source length above 1 MiB rejects before
source access or BF tape reset.

The private optional packing coordinator exports
`pack_bfx(record, input_workspace, output_workspace, tape_workspace)` with the
same view extents, record first. Its precondition is a complete successful
transparent v5 record from the source coordinator, containing ASCII commands
only. It is not an untrusted module validator and must not repack arbitrary
already-optimized v5 payloads. It calls
[`stream_runs.bf`](../compiler/stream_runs.bf), retaining pending opcode/count
across instruction chunks. It checks cumulative output does not overtake
consumed input before copying into the record in place, then commits the final
header and count. See the [pass contract and proof](../compiler/stream_runs.bf.notes.md).

The wide importer exports the existing four-pointer `import_bfx` shape, using
a 65,545-byte record, 524,288-byte decoder workspace, 536,870,912-byte output/
serialization workspace and 2,048-byte hash scratch aligned to four bytes.
Set the logical record length in decoder-workspace bytes 0..3 before every
call. On success publish only its returned store prefix. The output arena has
expanded serialization regions; the principal graph arena has a 64-MiB
budget, metadata starts at 384 MiB and block mapping at 392 MiB.
The arena is a compiler resource, not the program's tape, and its
extent is not a measured resident-memory claim.

The separate v5 decoder rejects logical lengths outside 9..65,545 before
reading bytes. Error codes retain the decoder meanings: framing 1, version 2,
producer status 3, count/depth resource 4, opcode 5, brackets 6. The old importer
continues accepting only its original versions and budgets.

## Verification, builds and remaining scope

Source coordination passes 398 cases on each target; wide decoding passes
414 cases on each, including all single bytes, 65,536 instructions and wide
loop pairing. Run packing passes 1,796 calls per target, including pending
states, wraparound, complete movement groups and chunk-boundary equivalence.
Independent interpreter checks establish exact BF consumption and peak cell
37 for the packer. Android calls include guards and five pointer alignments.
Exact counts, hashes, bootstrap cycles and complete-program checks are in
[profile evidence](../evidence/wide_profile.json),
[run-packer evidence](../evidence/stream_runs.json) and
[bootstrap evidence](../evidence/wide_bootstrap.json).
[Final audit](../evidence/wide_final_audit.json) confirms that the maintained
private packet coordinator reproduces every verified regression store.

All BF recognition and rewriting execute BF. All coordination, defensive
import and graph emission execute canonical XAX graphs. Unchanged generic
Windows-hosted Python SDK utilities still verify, apply transactions, bind,
lower and package those graphs. This does not complete the native XAX
compiler driver. Android is actual Pixel execution, not cross-compilation
alone. The Windows configuration explicitly inlines the decision and can
emit only the function closure referenced by the resulting lowering view;
the fully verified canonical store is preserved.

The maintained packing coordinator uses a private three-pointer BF core.
Expected-root graph edits specialize its logical input and output extents to
65,536, after compiling the packer's BF source through native v5. Its caller
builds complete frames of at most 32,774 bytes in initialized buffers; the
pass finishes at the counted terminator and produces fewer than 65,536 bytes.
Thus no EOF or output exhaustion is observable within this private contract.
This removes two redundant scalar call arguments and permits the existing
Windows register backend to retain an ordinary direct call. It does not change
the public five-argument decision ABI or its length guards.

Runtime-sized compiler arenas, page growth, file-backed source/spooling,
configurable budgets beyond this specialization, streaming clear/affine/scan
recognition and broad competitive measurements remain open. The 1-MiB source
view and 512-MiB importer arena are fixed extents. Processing chunks and using
wide counters does not by itself implement dynamically growing allocation.
See [scalability](16_SCALABILITY.md) for that distinction and the next steps.
