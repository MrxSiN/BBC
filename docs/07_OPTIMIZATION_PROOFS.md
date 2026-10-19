# BBC frontend optimization proofs

This document records proven compiler-implementation changes. P0 reduces
BBC's own execution work while preserving transparent BFX v1 byte for byte.
It does not implement P1/P2 source-program rewrites or change decision semantics.
The [profile](01_BRAINFUCK_PROFILE.md), [wire contract](02_BFX_CONTRACT.md) and
[measurement plan](06_PERFORMANCE_PLAN.md) remain authoritative.

## P0: counted source-byte groups

This section records the preceding counter-only snapshot. The decoder section
below describes the current frontend; its measurements are a separate A/B run.

The baseline frontend copied the low source-length byte twice and the high
byte once on every raw byte. Instrumented independent execution identified
length bookkeeping as 76.3% of work on maximum accepted ignored NUL source
and 68.2% on 4,096 ignored NUL bytes. Opcode comparisons are a separate
bottleneck, especially on FF; this change leaves them intact.

Hypothesis: count one initial partial group followed by groups of 256 bytes,
testing the high counter only at group boundaries. This should reduce work
across ignored, instruction-heavy and own-source inputs without extra tape,
changed acceptance limits or changed compiled modules. The native A/B suite
also includes empty and short decision requests to expose setup regressions.

### State and equivalence

At entry, decode source length as `n = 256 * high + low`. The existing frame
and size checks remain unchanged. If `n == 0`, skip initialization and the
source loop. Otherwise:

- Nonzero low starts a group of `low` bytes and retains `high` later groups.
- Zero low starts a group of 256 bytes and decrements high once.

Within the source loop, let `g` be the current group's remaining byte count
in 1..256 and `h` the number of later groups. Cell 9 holds `g mod 256`, cell
10 holds `h`, and remaining source bytes equal `g + 256 * h`.

Each iteration reads and processes exactly one source byte before decrementing
cell 9. If `g > 1`, the resulting byte is nonzero and execution continues.
If `g == 1`, cell 9 becomes zero: with no later group, clear continuation;
otherwise decrement cell 10 and continue with zero encoding the next group
of 256. The mathematical remaining count therefore decreases by exactly one
until zero. No wrapping high decrement occurs with high zero.

Initialization temporarily saves the nonempty gate in cell 4 and restores
cell 4 to zero before decoding. Counter transitions reuse cells 14 and 15
after bracket processing has consumed their flags. Both scratch cells return
to zero. The gate in cell 13 stays Boolean. Opcode, bracket depth, instruction
count and sticky error cells are preserved. Slot transfer carries the same
live state into the next sixteen-cell slot.

Thus byte order, literal NUL/EOF behavior, framing-error priority, source and
instruction limits, nesting validation, success staging and complete BFX
bytes are unchanged. The terminator is still read only after all declared
source bytes. This is compiler bookkeeping, not a source-level movement,
loop-termination or I/O optimization.

### Resource and verification bounds

The change adds one executable Brainfuck instruction overall and no tape
cells. The working-slot limit remains cell 61,471. It uses one fixed pass over
the source, one low-byte copy/test per byte and a high-byte test per completed
group rather than per raw byte. All counted arithmetic is byte wrapping with
the explicit group invariant above; it encodes no signed BFX offset or safety
annotation. BFX v1 and importer limits remain unchanged, with no expansion of
source-program output. Own-source BFX grows by one byte.

The actual initialization and counter fragments were extracted unchanged
from `compiler.bf` and executed under the independent interpreter for all
65,536 byte pairs each: **131,072 checked states**. Checks cover continuation,
group count, low counter and cleared temporary cells. These finite-state
checks supplement the invariant; they do not replace whole-compiler tests.

Whole-compiler verification includes source lengths around 255/256 and the
maximum accepted frame, truncation ending in NUL, invalid terminators,
source/instruction/nesting error priority, ten exact fixtures, interpreted
own-source agreement and native fixed points on Android and Windows. The
additional 257-byte group-boundary fixture passes the interpreter and both
native targets; 529 native byte/property cases include every single raw byte
and seeded valid, malformed, truncated and boundary requests.

### Measurements and limits

The fixed seven-case interpreter profile compares identical request bytes
and requires identical response hashes. Executed Brainfuck work falls from
136,967,749 to 111,486,478 instructions for compiling the baseline source,
and from 1,204,725,009 to 564,218,799 for maximum ignored NUL input. Peak tape
use is unchanged. Work counts are not native elapsed time.

Native measurements use a separate frozen nine-case suite, three independent
process runs per target and ten paired trials per case/run, with three warmups
per arm. Every timed call includes the full tape reset; complete output is
validated after timing. Android uses an external buffer/call/timing transport;
Windows uses external ctypes calls. These boundaries are reported separately.
Timer and call overhead remain included equally, with no subtraction.

Times below are median milliseconds per complete frontend call, baseline /
candidate. Each ratio compares arms on the same target; do not derive
cross-device ratios from the absolute columns.

| Request | Android ms, baseline / candidate | Ratio | Windows ms, baseline / candidate | Ratio |
|---|---|---|---|---|
| ignored ASCII | 40.5081 / 33.3345 | 1.215 | 203.3132 / 156.1532 | 1.302 |
| ignored NUL | 36.0220 / 28.8962 | 1.247 | 128.8065 / 81.9626 | 1.572 |
| ignored FF | 76.3020 / 69.1082 | 1.104 | 385.6026 / 337.7558 | 1.142 |
| instructions | 30.0789 / 26.6160 | 1.130 | 153.0844 / 127.8416 | 1.197 |
| nested | 8.3096 / 7.4235 | 1.119 | 48.5872 / 42.7689 | 1.136 |
| baseline own source | 59.6207 / 50.4590 | 1.182 | 320.9205 / 258.8189 | 1.240 |
| maximum ignored NUL | 684.4903 / 462.2532 | 1.481 | 2921.1804 / 1317.2786 | 2.218 |
| empty | 0.0811 / 0.0802 | 1.011 | 0.2449 / 0.2446 | 1.001 |
| decision | 2.5232 / 2.2225 | 1.135 | 6.5539 / 5.6346 | 1.163 |

The nine-case geometric means of median ratios are 1.174 on Android and 1.294
on Windows. The empty call has a near-parity point estimate with uncertainty;
its result is inconclusive. The pass is retained for the consistent
nonempty improvements, unchanged 61,471 peak tape cell and unchanged native
compiler library sizes: Android 66,504 bytes and Windows 692,736. Compiler
source shrinks by 26 bytes while own-source BFX grows by one byte; source
program BFX does not grow.

The [raw profile report](../evidence/frontend_counter_profile.json) includes
30 pairs per case/target, IQR, hierarchical paired-log bootstrap intervals and
approximate simultaneous intervals using Bonferroni across all 18 case/target
comparisons. There are only three process clusters. Windows uses Ryzen 7 5800H;
Android uses Pixel 8 Pro/Tensor G3, governor `sched_pixel`, with thermal status
zero at run snapshots. Clocks and thermals were not actively controlled;
these are exploratory local measurements, not a competitive release gate.

The evidence and current native timing results are indexed in
[status](05_STATUS.md). These are local frontend A/B measurements, not full
BBC-plus-XAX compilation, application runtime, RAM, energy or competitor results.
M8 and P1/P2 completion remain unproved.

## P0: single-copy opcode decoding

The measured counter frontend spent 140,722,176 of 160,480,882 instructions
on decoding 4,096 ignored FF bytes, about 88% of total work. It copied and
restored the raw byte eight times. Hypothesis: preserve the raw byte with
one copy and compare the eight distinct opcode values through a bounded
mismatch chain, reducing work without extra cells or changed BFX bytes.

### Match conditions and proof

Cell 1 holds the raw byte. Entry requires zero scratch cells 2 and 3, command
flag 4 and bracket flags 14 and 15; the main-loop and counter invariants
already establish these conditions. Other state is unrestricted.

Copy the raw byte into cell 2 using cell 3 for restoration. Set command flag
4, then subtract the first opcode value, 43. Nested nonzero branches subtract
the successive gaps 1, 1, 1, 14, 2, 29 and 2. The tested cumulative values
are exactly 43, 44, 45, 46, 60, 62, 91 and 93. Each is distinct modulo 256.
A zero therefore matches exactly one permitted byte and skips later tests.

When reaching the opening-bracket test, set flag 14; clear it on mismatch.
Set closing flag 15 only at the final test, clearing both that flag and the
command flag on the final mismatch. That mismatch also clears comparison
cell 2. Matching paths already have comparison value zero. Every path thus
unwinds once, preserving the raw byte, clearing scratch and returning the
exact command/open/close flags. It performs no input or output.

The actual fragment was executed for every byte at both the first and last
legal working slots: **512 states**. All other 65,536 tape cells were checked
against their entry values, including nonzero live state. Worst observed
decoder work across the complete finite byte domain is **4,381 dispatched
instructions**. The movement range stays within the existing working slot.

Whole-compiler verification adds a fixture containing every raw byte in
ascending order. Its payload is exactly the original eight commands in that
order, including balanced brackets. The current source passes 42 independent
interpreter checks, 530 native byte/property cases, 393 unchanged importer
cases, and three native rebuild generations on each required target. Android
passes all twelve fixtures in every generation and seven boundary cases.

### Resource and measured-work effects

Relative to the preceding counter frontend, compiler source shrinks by 602
bytes and 615 instructions. Current source is 4,355 bytes / 2,110 commands;
own-source BFX is 2,117 bytes. No tape cells or BFX feature/version are added.
All source, instruction, nesting, input-view and output limits are unchanged.
The existing capacity and grouped-byte-counter logic is retained, with its
131,072-state regression rerun against this source.

On the identical baseline compiler-source request, total interpreter work
falls from 110,765,503 to 65,029,967 commands. On 4,096 ignored FF bytes it
falls from 160,480,882 to 37,703,282. Every fixed-profile request and response
hash matches between arms. Bracket errors, framing priority, literal NUL/EOF,
staged success emission and native failure-prefix behavior remain unchanged.

The compiled frontend library shrinks from 66,504 to 50,120 bytes on Android
and from 692,736 to 549,888 bytes on Windows. These are compiler components;
they are not smaller application decision modules, whose BFX is unchanged.
Peak compiler tape use remains cell 61,471. Process RAM and full BBC-plus-XAX
latency are not inferred from these source and artifact counts.

The current native A/B results, raw samples, confidence intervals and limits
are published in [filter profile evidence](../evidence/frontend_filter_profile.json)
and [status](05_STATUS.md). They compare against the immediately preceding
counter frontend using a separately frozen nine-case suite. Do not multiply
ratios across the two experiments. These A/B experiments establish no
competitor result; [the separate pilot](08_BENCHMARKS.md) has its own corpus,
boundaries and evidence.

| Request | Android ms, baseline / candidate | Ratio | Windows ms, baseline / candidate | Ratio |
|---|---|---|---|---|
| ignored ASCII | 33.4100 / 12.1489 | 2.750 | 160.3650 / 59.3942 | 2.700 |
| ignored NUL | 28.9232 / 11.2023 | 2.582 | 84.3736 / 49.0827 | 1.719 |
| ignored FF | 69.3615 / 16.3172 | 4.251 | 349.9876 / 82.5366 | 4.240 |
| instructions | 26.6487 / 13.6804 | 1.948 | 138.1827 / 89.7840 | 1.539 |
| nested | 8.0867 / 5.3677 | 1.507 | 43.5408 / 29.5943 | 1.471 |
| baseline own source | 50.2788 / 25.0239 | 2.009 | 279.6262 / 158.0639 | 1.769 |
| maximum ignored NUL | 463.3038 / 179.1568 | 2.586 | 1345.0767 / 783.0098 | 1.718 |
| empty | 0.0764 / 0.0764 | 1.000 | 0.2489 / 0.2486 | 1.001 |
| decision | 3.1340 / 1.0743 | 2.917 | 5.8072 / 1.9793 | 2.934 |

The nine-case geometric means of median ratios are 2.226 on Android and 1.945
on Windows. The empty-call result remains near parity and is inconclusive.
The experiment retains the same three-run/ten-pair protocol, platform call
boundaries and bootstrap interval method as the earlier counter experiment.
Clocks and thermals were not actively controlled; thermal snapshots reported
status zero. These A/B runs do not measure full pipeline timing, process RAM,
energy or application runtime. Retain the decoder for its consistent nonempty frontend
improvements, reduced compiler source/IR/native size and unchanged tape bound.

## XAX: eight-byte tape reset

The current [canonical importer](https://github.com/MrxSiN/XAX/blob/7761cf24218472c459c3491dcf7570263bc3b373/compiler/integration/bfx/import_bfx.xax) initializes the complete
65,536-byte tape with checked eight-byte zero stores at alignment one. This is
a generic initialization change in XAX; BBC source, BFX v1 and source-program
lowering stay unchanged. [Its exact transaction](https://github.com/MrxSiN/XAX/blob/7761cf24218472c459c3491dcf7570263bc3b373/compiler/integration/bfx/wide_reset.edit) and
[XAX proof](https://github.com/MrxSiN/XAX/blob/7761cf24218472c459c3491dcf7570263bc3b373/compiler/integration/bfx/WIDE_RESET.md) identify the authoritative graph.

The unchanged length guards reject before reset. For a valid call, reset
iteration `k` writes bytes `8k` through `8k + 7`, with `0 <= k < 8192`.
The final write ends at 65,535; the counter then reaches 65,536 and exits.
Every byte is cleared exactly once. The stride is the existing 32-bit one
rotated right by 29, giving eight; the store uses the existing 64-bit zero.
No counter wraps or new constant-table entry is needed. Alignment stays one,
and memory frontiers and checked bounds remain explicit. Every other generated
block is identical, preserving I/O, intermediate movement traps and loop entry.

[Execution evidence](../evidence/wide_tape_reset.json) records 393 importer
cases per arm/target, 380 full-tape/output interpreter comparisons per
arm/target, five pointer alignments, dirty tapes, wrapping, EOF, nested/skipped
loops and failure behavior. Three frontend generations per target each pass
twenty checks and reproduce BFX, stores and native libraries. A native-only
Windows replay covers 1,606 calls; Android children also require native
execution. Bootstrap verification/lowering remain disclosed Python utilities.

The fixed twelve-source A/B has three runs, ten pairs per run and sixteen
calls per observation. Each timed call includes the entire reset; output/status
checks follow every call outside the timer. There are 11,520 timed calls per
target. The arithmetic averages of workload medians of batch means are:

| Native-call boundary | Before (ms) | After (ms) | Less time (ms) |
|---|---:|---:|---:|
| Windows x86-64 | 6.168 | 5.624 | 0.544 |
| Android ARM64 | 1.360 | 1.302 | 0.058 |

Exploratory paired bootstrap intervals for less time are 0.140 to 0.796 ms
on Windows and 0.055 to 0.081 ms on Android. Only three process clusters exist;
clocks, affinity and thermals were uncontrolled. Windows includes ctypes
overhead; Android times the direct call. These are separate from earlier
compiler-stage and startup measurements, with no cross-device speed claim.

The twelve measured native files keep the same sizes. A separate empty-program
Windows test DLL grows from 2,560 to 3,072 bytes at a PE padding boundary; the
Windows importer also grows by 512 bytes. No smaller-file or RAM result follows.
Fresh [Android process comparisons](08_BENCHMARKS.md#eight-byte-tape-reset)
still favor Awib and brainfry. No comparator is surpassed, and M8 remains unmet.
