# Unified public compilation

**IMPLEMENTED and EXECUTED, 2026-10-21.** One canonical XAX `compile_bfx`
entry invokes BBC's standard Brainfuck algorithms for all supported source
sizes. There is one [BFX format](02_BFX_CONTRACT.md), with magic `BFX` plus
NUL and identifier `01`. This phase changes no BFX opcode or accepted identifier.
[Execution evidence](../evidence/unified_compilation.json) records exact stores,
transactions, images, native calls and external test tools.

## Use

The native Windows executable is built from XAX `compiler/integration/bfx/compile_windows.xax`.
The [generic bootstrap recipe](https://github.com/MrxSiN/XAX/blob/d320babab5bb9fe61a9d29f1f14942a847bf83a7/compiler/integration/bfx/COMPILE.md)
uses the unchanged Windows-hosted XAX Python SDK once to build the command.
Copy its `bbc.exe` to BBC's ignored `build/` directory. The tested local copy
is available there. From a Windows command prompt:

```text
build\bbc.exe emit-bfx -O0 < program.bf > program.bfx
build\bbc.exe emit-bfx -O1 < program.bf > program.bfx
build\bbc.exe check < program.bf
build\bbc.exe info < program.bfx
```

In PowerShell, wrap each redirection command with `cmd /d /c "..."` to preserve
binary bytes. Source stdin is raw binary, with no manual framing. O1 is the
default for emit; O0 and O1 are the only implemented levels. O2/O3 reject with
exit 4. `check` validates source; `info` strictly validates BFX and prints its
instruction count. A nonzero exit requires discarding redirected output.

Exits are 0 success, 1 invalid source/BFX, 2 resource capacity, 3 I/O failure,
4 usage/unsupported level. Errors go to stderr. `emit-bfx`, `check` and `info`
execute without Python. Full native `bbc compile`, filesystem target options,
DLL packaging and Android compiler-host execution remain NOT IMPLEMENTED.
Native-code generation still uses the external XAX importer, verified binding
and generic SDK lowering/packaging described in [integration](03_XAX_INTEGRATION.md).

## One typed source API

The public core uses four distinct initialized writable borrowed views:
source/work 1,114,112 bytes, record 65,546, output/work 1,114,112,
tape/work 1,114,112. The canonical XAX caller supplies the pointer, view and
memory tokens for each; foreign pointers do not establish ownership proofs.

In source/work, store u32 actual frame length at offset 0 and u32 level at
4. At offset 65,531 place `source_length:u32le || binary_source || 01`.
Actual length must equal declared length plus five. This interface accepts
0 through 1,048,576 raw bytes and at most 65,536 pre-optimization commands.
Balanced nesting can reach 32,768. These fixed budgets are not dynamic growth.
The program tape remains 65,536 bytes under the execution profile.

The result is `(record_length << 32) | status`: 0 success, 1 framing,
2 unmatched brackets, 3 capacity, 4 unsupported level/internal component
failure. Failure length is zero. Discard all provisional output on failure.
Frame/configuration errors are checked before any buffer mutation. The check
order is physical frame range, declared source capacity, exact frame length,
terminator, level, command capacity and bracket validity. A bracket error in
an early chunk cannot hide a later command-capacity error. Other component
failures remain immediate. The source coordinator writes success magic only
after complete validation. Native CLI publication and import additionally use
the same strict canonical decoder; no legacy negotiation is present.

## Ownership and optimization

`compiler/stream_chunks.bf` owns public filtering and bracket validation.
`compiler/stream_runs.bf` owns arithmetic and monotone movement packing.
`compiler/optimize.bf` owns clear-loop recognition. Canonical XAX coordinates
their private packets, framing, buffers, OS I/O and native packaging. No BF
instruction stream changes in this phase, and no foreign compiler algorithm
is added to BBC. `compiler/compiler.bf` and the text framer remain private
bounded bootstrap/reference components; their old u16 requests are not a
second public source interface.

O0 emits primitive operations. O1 packs equal arithmetic runs modulo 256 and
monotone movement runs, then applies the existing clear pass if packed count
is at most 3,840. Larger modules conservatively retain clear loops. Opposite
moves are never cancelled. Even-step loops remain loops. Affine, scan and
offset optimizations are not implemented by this phase; scan-shaped loops
in the tests establish preserved behavior, not a new native scan opcode.

## Executed verification and scope

- 1,074 frontend cases on each target; Android checks five alignments and guards.
- Eleven Windows frame/configuration rejections leave every buffer unchanged.
- 1,899 Windows CLI checks, including malformed BFX, binary fragments,
  capacity, unsupported levels and closed-output-pipe failure.
- Thirty-nine generated program/level pairs, six whole-buffer vectors each
  per target: **468 native calls**, checked against an independent interpreter.
  Output, scalar status, complete tape, input and untouched guards agree.
- Three final frontend generations reproduce own-source BFX, imported store,
  embedded BF core and target native-image bytes. Each Android generation
  executes all 1,074 cases and natively imports the own-source record.
- Mandelbrot O0/O1 produce exact pre-existing record/store identities; native
  images are reused only after hash identity and re-executed on both targets.
  No fresh lower/package measurement is inferred from that reuse.

The three maximum-command O0 full-lowering cases were excluded from the new
whole-buffer suite to avoid huge primitive graphs; frontend count validation
is covered at both levels. One exploratory primitive graph build was stopped
before a result and is not counted as passing. The current importer arena is
still fixed and large; reducing it belongs to later memory/backend work.

These results establish the public entry point and frontend integration.
They do not complete the native compiler-driver, semantic-optimization,
performance or full-application milestones. All earlier evidence is preserved.

## Native build finding and priorities

The existing native Windows driver accepts a prepared Android build snapshot,
packages a 5,880-byte hello executable and produces exact output on Pixel 8 Pro.
Snapshot preparation still uses generic bootstrap APIs. The equivalent Windows
build rejects with `XAX.NATIVE.BITS`, rule `NATIVE-BITS-SUPPORTED`, actual 1,
expected 32/64. This is a backend coverage gap, not a reason to weaken verification.
Self-store and multiple resource-callee coverage, libraries and common-loader
migration also remain open. The full normal build is still Python-dependent.

[The frozen baseline](20_MODERNIZATION.md) measures BBC at 1.46–1.58 s versus
Brainfry at 23–24 ms for three workloads. No complete-build speedup is claimed
for this interface phase. Next priorities are native driver/backend coverage,
content-bound proof reuse and type identity reuse, then semantic loop
optimizations with failure-trace proofs. Frontend integration alone does not
address the dominant measured SDK/startup/verification/binding costs.

The later [native backend follow-up](19_NATIVE_DRIVER_FOLLOWUP.md#native-frame-bitwise-extension)
records the response to the one-bit rejection found above. Its prepared-build
results do not change this interface phase's frozen benchmark or bootstrap hashes.

[Subsequent lowering](22_NATIVE_LOWERING.md) builds all six original prepared
target snapshots and records the broader Android deep-nesting decline.

[Android interval allocation](23_ANDROID_NATIVE_LOWERING.md) subsequently fixes
that decline while preserving all 20 previously successful Android artifacts.
The public frontend and its single BFX format remain unchanged.
