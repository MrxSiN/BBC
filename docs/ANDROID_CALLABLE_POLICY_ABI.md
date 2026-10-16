# Callable Android policy ABI

The [device-verified GM path](ANDROID_GM_NATIVE_20261014.md) uses saved standard
BF programs for every compiler transformation. The internal records described
here are compiler data, not source-language syntax. Raw source still has exactly
eight executable instructions.

## Wire stages

| Stage | Input | Output and responsibility |
|---|---|---|
| scanner | Raw source with `00 -> FF01`, `FF -> FF02` transport escapes | Filtered commands, three-byte command count, status |
| policy_rle | Filtered commands; EOF zero | `(opcode, byte run count)` records, zero record and status |
| policy_clear56 (opt-in) | RLE records | BF-owned streaming replacement of exact clear-loop triples with a private `0` (count 0) record; other records byte-preserved |
| policy_resolve | RLE records | Two-byte record count, four-byte records with bracket spans, zero record and status |
| policy_optimize | Resolved records | Seven-byte header and seven-byte records; static pointer proof, clear folds, native word costs |
| policy_affine | Optimized records | Same format; proven decrement loops become capture/multiply-add/clear records |
| policy_oneshot | Affine records | Same format; proven source clears remove repeating backedges |
| policy_operands | Final records | Five-byte header, six encoded prelude bytes, 25-byte instruction records, zero record and status |
| policy_codegen | Encoded operands | Five metadata bytes, native code, trailing status |
| policy_elf | Metadata plus native code/status | Complete callable ELF and trailing status |

The seven-byte IR header is little-endian record count (2), native body word
count (2), bounded/static proof (1), required tape cells (2). A record is opcode
(1), run amount/coefficient (1), branch word span (2), static pointer (2), native
word cost (1). Code positions include only emitted native words, including zero
cost records. Brackets use signed immediate branches within this bounded format.

Private IR kinds include `N` (no emitted code), `0` (clear), `F` (capture the
affine source byte), `A` (multiply-add), `I` (conditional body with no backedge)
and `E` (eliminated closing edge). These are never recognized in raw BF source.

## BF working tape

Resolver/optimizer stages use 15-cell records starting at compiler cell 128.
Within a record, source/IR fields use lanes 0–3 and 6–8. Lanes 4–5 and 9–14 are
carried state, counters and phase-specific scratch. The zero sentinel immediately
before the first record supports rewind. Record count/error outputs occupy global
cells 20–22; the optimized input header occupies 32–38. A 4,096-record ceiling
keeps storage within the 65,536-cell compiler tape. The Iteration 56 optional
`policy_clear56` prepass can shrink selected real source programs below that
limit, but it does not remove the ceiling; see [the Twitter action gate](ITERATION56_TWITTER_ACTION_CLEAR.md).

For the new single-iteration pass, lane 14 marks the opening record, lane 4
carries its static pointer, lane 5 carries the guaranteed-clear fact and lane 10
carries nesting depth. Every nested boundary invalidates the fact; a direct
source clear establishes it; other direct source writes invalidate it. The pass
rewinds to its marker before changing the opening record. It temporarily maps
`I/E` back to ordinary bracket records, using lane 1 to preserve their kind while
the existing BF matcher recalculates spans. Lane 1 returns to zero afterward.

This is an ownership description, not a complete compiler-tape safety proof.
The affine coefficient ledger has different scratch ownership; consult the saved
BF implementation and its authoring helper rather than reusing a lane blindly.

## Native call

```c
struct result { uint64_t status, ticks; };
result entry(const uint8_t *input, size_t input_length,
             uint8_t *output, size_t output_capacity,
             uint8_t *zeroed_tape, size_t tape_cells,
             uint64_t loop_budget, size_t *output_length);
```

Arguments use AArch64 X0–X7. Status/ticks return in X0/X1. X8–X17 are scratch;
callee-saved registers are untouched. Byte cells wrap; reads past input yield
zero. Output remains bounded. Static tape proof is checked against the supplied
tape size at entry; the generic path checks pointer movement. Status 1 means
loop budget exhausted, 2 output overflow, 3 pointer/tape bounds failure. The caller discards partial
output on failure. Budget accounting applies to remaining potentially repeating
loops after optimization.

The ELF is ET_DYN/AArch64 with one RX `PT_LOAD`, entry 128, and 16 KiB alignment.
Bytes 120–127 contain `BFP1`, required tape cells (little-endian 2), static-proof
flag and zero. The entry is a **callable function**, not a standalone process
entry. GM's generic platform linker embeds the image unchanged into executable
text; its new JNI adapter calls the symbol plus 128. There is no runtime writable
executable mapping or BF code repair. This does not make the standalone file an
Android `dlopen` library with exports/dynamic metadata.
