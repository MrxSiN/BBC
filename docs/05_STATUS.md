# BBC and BFX status

Evidence: **2026-10-19** frontend/platform runs; **2026-10-20** Windows native
driver prototype, tape-reset optimization and standalone Android/Windows processes. Format: **BFX v1**, magic `42 46 58`, binary
version `01`. The [contract](02_BFX_CONTRACT.md) and
[execution profile](01_BRAINFUCK_PROFILE.md) define the shared behavior.

## Executed support

| Component | Android ARM64 | Windows x86-64 | Evidence |
|---|---|---|---|
| Standalone executable | EXECUTED: 23 native programs; fragmented/binary I/O, size and failure checks | EXECUTED: 23 native programs and 28 host checks; kernel32-only PE | Direct verified decisions; separate target-specific build configurations and evidence |
| Current BBC frontend | EXECUTED | EXECUTED | Current cycles reproduce the seed on both required targets |
| XAX native driver prototype | No new execution | EXECUTED with bounded coverage: 78 valid stores accept, 130 malformed stores reject, four decline; one diagnostic differs | Native PE build/edit/resolve fixtures pass; corrected self-store and DLL packaging decline |
| Standalone XAX hashing host | No new execution | EXECUTED: 139 successful streams and five failure cases | Separate native helper process; not yet used by the compiler loader |
| Canonical XAX decoder | EXECUTED: 393 cases | EXECUTED: 393 cases | Length, magic, version, opcode, bracket and resource limits |
| Canonical XAX importer | EXECUTED: current reset importer passes 393 cases and compiler imports | EXECUTED: current reset importer passes 393 cases | Each version produces identical Android/Windows stores; input and four buffer guards preserved |
| Generated decision components | EXECUTED: 380 checks across 20 modules per importer version | EXECUTED: 380 checks across 20 modules per importer version | Full output and tape agree with an independent interpreter; no source-program optimization |
| Frontend rebuild cycle | EXECUTED for current frontend: identical BFX/store/ELF across three generations; twenty checks per generation | EXECUTED for current frontend: identical BFX/store/DLL across three generations; twenty checks per generation | Android stores also match Windows stores; native lowering occurs on Windows |
| Decision application | EXECUTED: eight fixed bounded Activity cases | UNVERIFIED: XAX application caller beyond native component tests | Pixel 8 Pro, Android 17/API 37; Windows GUI is not required |

The decoder and complete-importer case counts are separate runs of the same
393-case corpus. The eight Activity cases are separate from frontend checks.
The current native cycles each use twelve exact fixtures, own source and
seven boundary checks: twenty checks per generation on each target, including
the group boundary and all-byte opcode fixtures. None of these correctness counts is
a timing measurement.

The current frontend is 4,355 source bytes and 2,110 executable instructions.
It accepts 65,533 raw source bytes, 3,840 instructions and 255 nested loops.
The source limit keeps a complete request within the native 65,536-byte input
view. It passed 42 independent-interpreter checks and 47 Windows native
checks plus 530 byte/property cases
plus three native rebuild generations. Android passed three current frontend
generations, 36 exact fixture checks and seven separate boundary checks.
In that frontend-only iteration, the canonical XAX importer was unchanged,
rebuilt byte-identically and passed its 393 record cases again. The current
reset importer has the separate 2026-10-20 report below.

P0 grouped-byte bookkeeping and single-copy opcode decoding are implemented
entirely in ordinary Brainfuck.
It adds no tape cells, preserves source consumption and framing-error priority,
and leaves BFX v1 unchanged. Its initialization and transition fragments pass
131,072 exhaustive state checks. The decoder passes all 512 byte/slot states,
preserving the raw byte and every unrelated cell. Relative to the counter
frontend, native compiler libraries shrink from 66,504 to 50,120 bytes on
Android and from 692,736 to 549,888 on Windows. Peak tape use is unchanged.
All earlier reports retain their original bytes and hashes. Android evidence
for the earlier frontend must not be attributed to the changed instruction
stream. Earlier capacity reports retain their original source identities.

## Local frontend measurements

The fixed nine-case suite has three independent runs and ten paired trials
per case/run on each target. It includes ignored ASCII/NUL/FF, instruction-heavy
and nested source, baseline own source, maximum ignored NUL, empty source and
the decision example. Raw samples, dispersion and bootstrap intervals are
published in [filter profile evidence](../evidence/frontend_filter_profile.json).

| Scope | Android ARM64 | Windows x86-64 |
|---|---|---|
| Geometric mean of per-case native frontend median speedups | 2.226x | 1.945x |
| Same baseline compiler-source request | 2.009x | 1.769x |
| Ignored FF request | 4.251x | 4.240x |

These compare BBC against its preceding frontend on each target's own device
and call boundary. They do not measure full BBC-plus-XAX compilation or
application execution. Clocks were not pinned and thermal control was not
active; Android reported thermal status zero at the recorded run snapshots.
Treat the confidence estimates as exploratory. The empty-call result is near
parity; no material regression is established. [Proofs and all case medians](07_OPTIMIZATION_PROOFS.md)
record the scope and trade-offs. Separate
[competitor measurements](08_BENCHMARKS.md) now cover a twelve-source pilot;
they do not change the scope of these frontend A/B results.

## Competitor pilot

The [first competitor results](08_BENCHMARKS.md) pin all eight projects and
execute Awib C and brainfry AOT on Android ARM64 and Windows x86-64. Twelve
sources have three independent runs and ten paired trials per run: 2,520
timed native process invocations and 2,160 timed test-pipeline builds.
Every timed native process has an output and exit-status check. Final Android
rebuilds match all 36 initially executed native artifacts byte for byte.

In the original pilot, all four target/comparator aggregates favor the baseline for process time,
test-build time and standalone test artifact bytes. These pilot boundaries
are REGRESSION. That pilot did not measure steady-state runtime, RAM or full
applications; the later follow-up below supplies scoped RAM results. The outer compilation figure retains
common measurement-CLI overhead, with inner intervals published separately.
It is not the final compiler victory boundary. No competitor is SURPASSED.
Graph verification accounts for a median 75.5%/81.6% of instrumented BBC
Android-target/Windows-target build time on the Windows host.
The label included reader/helper startup as well as graph verification.
[The follow-up diagnosis](08_BENCHMARKS.md#verification-cost-diagnosis) measures
these phases separately. Existing local ProofCache reuse improves a separate
three-source warm XAX stage by geometric means of 1.166x/1.187x for
Android-target/Windows-target builds, with identical emitted bytes and seven
cache tests passing. This is an external prototype; no executable source,
XAX graph or original competitor result changes. Cold builds remain a
separate gate, with Windows native-helper execution still unavailable through
the current helper loader. A [standalone Windows hashing host](03_XAX_INTEGRATION.md#windows-native-hashing-host)
now executes the existing BLAKE3 graph with XAX-owned buffers and Windows I/O.
Its 139 successful cases and five failure cases are a native component result;
the compiler does not automatically use this process. No competitor score or
full-pipeline compilation timing changes.

The [native Windows driver prototype](03_XAX_INTEGRATION.md#windows-native-driver-prototype)
now executes the existing verifier chain through an explicit CLI. Its 212-case
corpus and PE/edit/resolve fixtures are separate from the earlier frontend and
competitor evidence. Diagnostic parity, corrected self-store verification,
large-edit replay, DLL packaging and common-loader migration remain unmet.
A [separate CLI experiment](08_BENCHMARKS.md#windows-native-verification-cli)
measures fresh-process verification only; it does not re-score the pilot.

## Eight-byte tape reset

The current canonical importer clears eight bytes per checked store instead
of one, preserving the full 65,536-byte reset. Twenty programs pass 19 checks
per version/target (1,520 calls overall). A separate native-only Windows replay
covers 1,606 calls, including importer and frontend cycles, with explicit native
authority. The [proof](07_OPTIMIZATION_PROOFS.md#xax-eight-byte-tape-reset) and
[timings](08_BENCHMARKS.md#eight-byte-tape-reset) are separate from prior reports.
The twelve-program native-call average falls from 6.168 to 5.624 ms on Windows
and 1.360 to 1.302 ms on Android. New Android process aggregates still favor
Awib and brainfry for the shared-library package; no full-build or RAM victory
follows. The later standalone package below has its own process comparison.

## Standalone Android process

A canonical XAX host now calls the existing checked decision directly from
a static executable, removing the fixed shared-library test host. The fixed
twelve-program follow-up averages 13.441 ms for BBC versus 31.076 ms for Awib,
and 12.501 ms for BBC versus 7.473 ms for brainfry, retaining each separate
paired population. Three runs of ten randomized pairs check every output and
exit status. This is an advantage over the pinned Awib configuration on the
tested Android process boundary; brainfry remains faster.

The [package and native replay](03_XAX_INTEGRATION.md#standalone-android-process)
preserve full tape reset, bounds and failed-output discard. Twenty-three
programs run natively; additional checks cover binary/fragmented input,
maximum/excess input, closed descriptors and large file/pipe output. No
unrestricted comparator is SURPASSED. That snapshot left Windows, compiler
latency and RAM unmeasured; the later follow-up below measures them on the
twelve-source corpus. Best-mode, broader-profile and application gates remain
open; M8 is not achieved.

## Fresh builds, memory and Windows comparisons

The [new comparison](08_BENCHMARKS.md#build-latency-ram-and-windows-standalone)
measures complete source-to-standalone builds for both targets, compiler
process-tree memory, runtime resident memory on both targets and standalone
Windows process execution. It retains the original twelve sources and
holdouts: 2,160 timed builds, 864 separately profiled builds, 1,080 timed
Windows processes and 1,080 Android peak-RSS runs. Additional Windows memory
trials are recorded separately. All build outputs reproduce validated hashes;
all runtime outputs and statuses are checked.

Compiler resident peaks are sampled lower bounds; kernel peak commit is a
distinct metric. Native BBC filtering/import is followed by unchanged generic
Python verification and lowering on Windows. This does not complete the
native compiler driver, best-mode coverage, real applications or M8.

## Evidence index

| Report | What it establishes |
|---|---|
| [build_runtime_resources.json](../evidence/build_runtime_resources.json) | Fresh complete-build latency, compiler/runtime memory, Windows standalone comparisons, raw samples, calibrations, excluded launcher probe and explicit scope |
| [standalone_windows.json](../evidence/standalone_windows.json) | Canonical Windows host and public hello transaction; 23 native programs, 28 host checks, native binding replay/verify/stale rejection and exact empty/hello rebuilds; explicit unchanged generic inlining configuration |
| [standalone_android.json](../evidence/standalone_android.json) | Static Android process host and binding, correctness/artifact hashes, primary raw process timings against pinned Awib/brainfry, size summaries, retained excluded concurrent-validation probe |
| [standalone_native_replay.json](../evidence/standalone_native_replay.json) | Native-only replay of 23 Android programs; exact native authority; Windows driver binding replay, verification and stale-root rejection |
| [wide_tape_reset.json](../evidence/wide_tape_reset.json) | Current canonical importer transaction; 393 cases per version/target, 380 decision checks per version/target, three twenty-check frontend generations per target, native-call A/B and fresh Android process comparisons |
| [windows_native_driver.json](../evidence/windows_native_driver.json) | Bounded Windows native CLI: 212 verification cases with explicit declines/diagnostic gap, PE/resolve/edit fixtures, 31 adapter checks and 256 flag-regression inputs; no native corrected self-store verification |
| [windows_native_verification_profile.json](../evidence/windows_native_verification_profile.json) | Three separate runs, ten randomized pairs per case/run for Python versus native verification CLI; raw samples on the current Windows host; no full-build or competitor result |
| [windows_hash_host.json](../evidence/windows_hash_host.json) | Standalone canonical Windows hashing host: 139 successful streams, five failure cases, explicit error-state transaction and byte-identical PE rebuild; no compiler-loader integration |
| [graph_verification_profile.json](../evidence/graph_verification_profile.json) | Cold reader/check decomposition, Python fallback authority, repeated type-hash trace, existing proof-cache tests and warm XAX-stage A/B; no new competitor verdict |
| [competition_pilot.json](../evidence/competition_pilot.json) | Pinned Awib/brainfry native process, test-pipeline compile and artifact-size pilot on both required targets; all eight projects remain visible; no sweep |
| [frontend_filter_windows.json](../evidence/frontend_filter_windows.json) | Current BBC source with the preceding importer: 42 seed checks, 393 importer cases, 47 native checks and three Windows generations |
| [frontend_filter_android.json](../evidence/frontend_filter_android.json) | Current BBC source with the preceding importer: three generations, twelve fixtures per generation and seven boundary checks |
| [frontend_filter_profile.json](../evidence/frontend_filter_profile.json) | Decoder and counter proofs, 530 native property cases and raw paired native frontend measurements |
| [format_cleanup.json](../evidence/format_cleanup.json) | Eight retired-format reports removed and 95 obsolete generated files moved outside the repository; reusable framer and fixtures retained |
| [frontend_counter_windows.json](../evidence/frontend_counter_windows.json) | Preceding counter identity, 40 seed regressions, 393 importer cases, 41 native checks and three Windows generations |
| [frontend_counter_android.json](../evidence/frontend_counter_android.json) | Preceding counter identity, three generations, ten fixtures per generation and seven boundary checks |
| [frontend_counter_profile.json](../evidence/frontend_counter_profile.json) | Counter state proof, 529 seeded byte/property cases, extra boundary fixture and raw paired native frontend measurements |
| [source_capacity.json](../evidence/source_capacity.json) | Preceding capacity-checked frontend, 40 seed checks, 393 importer cases, 41 native checks and three Windows generations |
| [source_capacity_android.json](../evidence/source_capacity_android.json) | Capacity-checked frontend on Android, ten fixtures per generation, seven boundary checks and eight unchanged-app Activity cases |
| [bfx_android_importer.json](../evidence/bfx_android_importer.json) | Pre-reset importer source and transaction; Android/Windows execution, native decisions, both rebuild cycles and reproducible artifacts |
| [bfx_migration.json](../evidence/bfx_migration.json) | Frontend/decoder hashes, 21 seed checks and 393 decoder calls on each target |
| [bfx_retirement.json](../evidence/bfx_retirement.json) | Canonical application hashes, eight Activity cases, 36 arithmetic checks and a 128 KiB stack probe |

Reports are immutable execution snapshots. Use the report for the component
and source hash being assessed; a report is not a continuously updated support
matrix. [XAX integration](03_XAX_INTEGRATION.md) pins the maintained source revision.

## Build host and boundaries

The importer and compiled Brainfuck frontend execute natively on Android and
Windows. Canonical verification, native lowering and Android packaging for
the recorded BBC cycles run on Windows through unchanged generic XAX Python
bootstrap utilities. The separate
native driver prototype covers the explicitly tested CLI operations above; it
does not replace that complete build path.
`XAX_REQUIRE_NATIVE` was unset; no Android-hosted XAX compiler claim is made.
The Android app embeds a compiled decision, without an importer or Brainfuck
interpreter. All BBC executable source remains `.bf`; XAX integration source
is canonical semantic graphs in the separate repository.

## Remaining work

- General potentially unbounded Android decisions need an executed off-main
  worker path with verified lifetimes and UI result delivery. The current
  app embeds a bounded decision and calls it synchronously in lifecycle/UI flow.
  Existing XAX managed callbacks and pthread contracts are enabling facilities,
  not evidence that this integration has been implemented.
- After P0 decoding, slot transfer dominates accepted-instruction work and
  grouped length bookkeeping dominates ignored NUL input. Profile those
  remaining costs before extending the frontend. P1/P2 source-program folding and
  loop optimization are UNIMPLEMENTED and need independent equivalence proofs,
  safe bounds/error ordering, BFX design and native cost evidence.
- Linux execution is UNIMPLEMENTED in this integration; no Linux execution
  host is available. Cross-compilation alone will not establish support.
- Native XAX compiler-host execution on Android is UNIMPLEMENTED in this cycle.
- The general ARM64 large-composite return-copy defect remains open as
  [XAX OI-49](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/XAX_OPEN_ISSUES.md#oi-49--android-arm64-large-composite-return-copy).
  The importer uses checked scratch outputs and mixing results of at most
  16 bytes, so it avoids that operation and executes successfully.
- M4 is incomplete: frontend profiling, two P0 improvements and the first
  [competitor test-pipeline pilot](08_BENCHMARKS.md) are MEASURED. P1/P2,
  steady-state comparisons, broader compiler/deployment boundaries,
  broader compiler/runtime RAM coverage and full application coverage remain.
  The new twelve-source follow-up supplies scoped build/RAM measurements. XAX graph
  verification bucket includes cold helper setup. The follow-up identifies
  local proof-cache reuse, repeated checked-access type hashing and the
  missing Windows native-helper host path. Reuse existing APIs for the cache;
  any new helper integration must be canonical XAX graph work. The standalone
  hashing host covers hashing and stream transport. The separate native driver
  prototype executes the store/graph/CFG/type/verifier chain on tested stores;
  full diagnostic/large-store coverage, common-loader migration and BBC DLL
  packaging remain outstanding. Frontend tuning does not
  address these backend costs. M8 is NOT YET ACHIEVED; follow
  [the measurement and coverage plan](06_PERFORMANCE_PLAN.md).
- No stable release or performance superiority is claimed. Android and Windows
  are required; Linux implementation and benchmarking are optional and non-gating.
