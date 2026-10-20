# BBC and BFX status

Evidence: **2026-10-19** frontend/platform runs; **2026-10-20** Windows native
driver prototype, tape-reset and capacity-flag optimizations, Brainfly SDK
follow-up, semantic optimization and standalone Android/Windows processes.
Formats: transparent **BFX v1**, optional [**v2 CLEAR**](10_BFX_V2_CLEAR.md),
[**v3 arithmetic powers**](12_BFX_V3_ARITHMETIC.md)
and [**v4 movement powers**](14_BFX_V4_MOVEMENT.md),
magic `42 46 58`, explicit binary version. The [v1 contract](02_BFX_CONTRACT.md) and
[execution profile](01_BRAINFUCK_PROFILE.md) define the shared behavior.
The separate [**v5 wide profile**](17_BFX_V5_WIDE.md) uses a u32 count and its
own fixed budgets; it does not reinterpret any earlier format.

## Executed support

| Component | Android ARM64 | Windows x86-64 | Evidence |
|---|---|---|---|
| Standalone executable | EXECUTED: 23 native programs; fragmented/binary I/O, size and failure checks | EXECUTED: 23 native programs and 28 host checks; kernel32-only PE | Direct verified decisions; separate target-specific build configurations and evidence |
| Current BBC frontend | EXECUTED: three identical capacity-flag generations | EXECUTED: three identical capacity-flag generations | Native Android and Windows stores match |
| XAX native driver prototype | No new execution | EXECUTED with bounded coverage: current 160-case semantic replay has 63 accepts, 97 rejects and exact full diagnostics; 110 helper checks pass | Known mismatch fixed; full original corpus not rerun. Self-store, large edit and DLL gates remain open |
| Standalone XAX hashing host | No new execution | EXECUTED: 139 successful streams and five failure cases | Separate native helper process; not yet used by the compiler loader |
| Canonical XAX decoder | EXECUTED: 393 cases | EXECUTED: 393 cases | Length, magic, version, opcode, bracket and resource limits |
| Canonical XAX importer | EXECUTED: v1/v2/v3/v4 importer passes 1,164 cases | EXECUTED: all four versions and strict v1/v2/v3 compatibility | Exact Android/Windows agreement; input and four buffer guards preserved |
| Optional BF optimizer | EXECUTED: three identical optimized generations | EXECUTED: three identical optimized generations, 359 properties and 71 independent seed cases | Exact clears/full arithmetic wraps; no record expansion |
| Private chunk frontend | EXECUTED: 632 chunk calls, five alignments and guards | EXECUTED: 588 scalar properties and 44 stream chunks | 59-cell filter/validator; v5 now supplies separate module coordination and import |
| V5 wide compilation | EXECUTED: Mandelbrot and larger-source regressions; 398 source and 414 decoder cases | EXECUTED: the same source/decoder cases and native programs | 1-MiB source, 65,536 pre-pack instructions; fixed views, not runtime arena growth |
| Streaming run packer | EXECUTED: 1,796 native calls plus independent checks | EXECUTED: the same 1,796 calls | Carries runs across chunks; full buffer regressions and native bootstrap replay are separate evidence |
| Arithmetic packer | EXECUTED: three identical native generations | EXECUTED: three identical native generations, 432 native properties and 72 independent cases | 3,639-instruction standard BF producer; all fourteen arithmetic powers |
| Arithmetic decision components | EXECUTED: 5,530 checks across 42 modules per arm | EXECUTED: 5,530 checks across 42 modules per arm | Complete buffers and guards agree with an independent interpreter; 22,120 calls total |
| Frontend rebuild cycle | EXECUTED for current 2,192-instruction frontend: identical BFX/store/ELF across three generations; twelve fixtures each | EXECUTED for current 2,192-instruction frontend: identical BFX/store/DLL across three generations; twelve fixtures each | Native lowering occurs on Windows |
| Decision application | EXECUTED: eight fixed bounded Activity cases | UNVERIFIED: XAX application caller beyond native component tests | Pixel 8 Pro, Android 17/API 37; Windows GUI is not required |

The current frontend has 4,537 source bytes and 2,192 instructions; its raw
SHA-256 is `d8170d895449cf00e971a052b6d5415d2c5f86585d982f826fa70c5127850d6e`.
It moves the count-high comparison to carry events, preserves exact BFX v1 output
and uses no extra tape. [Capacity-gate evidence](../evidence/frontend_capacity_gate.json)
records 42 independent seed checks, all 7,682 reachable count/command states,
785 Windows byte/property cases, 393 current-importer cases and three Windows
fixed-point generations. Android subsequently passed 393 importer cases,
three current native generations, twelve fixtures each and twelve boundary
checks; canonical stores agree with Windows. The device became available
after the initial Windows-only snapshot. The following filter-cycle counts and timings retain their
preceding source identities.

The optional [`optimize.bf`](../compiler/optimize.bf) adds source-program
rewriting under a [separate v2 contract](10_BFX_V2_CLEAR.md). Its 2,931
instructions fold exact unit-step clear loops and remove full 256-command
same-direction arithmetic groups. Raw source validation and transparent v1
output remain authoritative. The pass requires a complete validated successful
v1 record plus byte `01`; it is not an independent record validator.

[Optimization evidence](../evidence/bfx_v2_optimization.json) records native
and independent checks, count/bounds failures and three identical optimized
frontend/helper generations per target. The compiler source stays unchanged;
its v1 records and twelve fixtures remain exact through the v2 route. Every
v1 accepted store retains its bytes. The standalone decoder stays v1-only;
the extended importer validates both versions. All 96 new standalone artifacts
build and all 48 per-target executions pass exact output/status checks.
The installed demo application remains tied to its previous evidence.
The [v2 benchmark report](11_V2_BENCHMARKS.md) separates complete builds,
process execution, memory, full executable bytes and native calls. The
competitive objective remains unmet; older measurements retain their hashes.

The [v3 packer](12_BFX_V3_ARITHMETIC.md) now packs seven powers per direction.
It requires validated v2 plus byte `01`, never expands a record and uses no
extra tape. Both targets pass three identical generations of all three BF
components. Current native frontend v3 IR contains 1,910 operations; the
unchanged source still has 2,192 instructions and emits exact transparent v1.
Clear and arithmetic helpers have 2,513 and 3,258 optimized operations.
[V3 correctness evidence](../evidence/bfx_v3_arithmetic.json) is separate from
the v2 measurements. The [new v3 measurements](13_V3_BENCHMARKS.md) report
complete native-call geometric-mean median ratios of 1.432x on Android and
1.236x on Windows against v2, including full reset. Fresh complete-build
ratios are 1.093x and 1.136x; process ratios are 1.077x and 1.009x. Three run
clusters limit inference. Seven Windows and six Android files shrink; Android
hello grows by 16.7%. Brainfry retains much faster builds and smaller files.

The [v4 movement packer](14_BFX_V4_MOVEMENT.md) adds identical-direction
power groups without cancelling opposite moves. It has 3,719 instructions /
5,347 bytes and observes peak cell 61,469. Its [separate correctness evidence](../evidence/bfx_v4_movement.json)
records 432 native properties, 72 independent cases and 9,592 complete-buffer
calls over both targets. All four BF components reach three native fixed
points per target; frontend/clear/arithmetic/movement v4 operation counts are
812/901/1,057/1,063. The unchanged frontend still emits exact transparent v1.
[New matched measurements](15_V4_BENCHMARKS.md) retain the same sixteen
workloads and all earlier snapshots; no overall competitor sweep is achieved. Full-build
geometric-mean median ratios against v3 are about 1.020x on each target;
seven Android/four Windows executable files shrink and none grow. The new
Windows frontend DLL is 218,624 bytes versus v3's 502,784. Native-call ratios
are 0.930x Android / 1.005x Windows; no runtime or RAM victory is established.
[Post-primary controls](../evidence/bfx_v4_call_controls.json) record variability
with identical code and the same function address; primary scores stay intact.

The [scalable frontend prototype](16_SCALABILITY.md) now filters and validates
source incrementally with 59 cells and a u64 bracket-depth counter. Both targets
process Mandelbrot, a 1 MiB binary source and 140,000 instructions at nesting
70,000, with cross-chunk errors retained. Tokens are provisional until final
success. The filter alone emits private packets. The separate
[v5 coordinator and importer](17_BFX_V5_WIDE.md) now turn them into complete
modules and compiled larger programs under explicit fixed budgets. The
[capacity audit](../evidence/scalability_capacity_audit.json) still reproduces
the original interface's rejection of 11,451-instruction Mandelbrot; the new
profile compiles it on both targets. Runtime arena growth remains open.

The retained capacity-flag change has ten-case native-call median-ratio
geometric means of 1.169x on Android and 1.086x on Windows, thirty paired
trials per case/target. Windows nested-input median is about 4% slower and
its compiler DLL grows by 20,992 bytes; Android library size stays 50,120.
These are frontend results, not compiler-pipeline or application victories.
[Full table, uncertainty and rejected candidate](07_OPTIMIZATION_PROOFS.md#p0-carry-triggered-capacity-flag).

The .NET SDK blocker is resolved: Windows x64 SDK 10.0.402 is installed and
the unchanged pinned Brainfly CLI builds. All twelve frozen corpus programs
pass exact output checks in JIT and generated NativeAOT modes. These are build
and correctness checks, not scored competitive timing. The
[follow-up](../evidence/brainfly_brainfry_followup.json) also records three
reproduced Brainfry optimizer defects; the
[analysis](09_BRAINFRY_ANALYSIS.md) explains their scope and optimization priorities.

The decoder and complete-importer case counts are separate runs of the same
393-case corpus. The eight Activity cases are separate from frontend checks.
The preceding filter/reset native cycles each use twelve exact fixtures, own source and
seven boundary checks: twenty checks per generation on each target, including
the group boundary and all-byte opcode fixtures. None of these correctness counts is
a timing measurement.

The preceding filter frontend is 4,355 source bytes and 2,110 executable instructions.
It accepts 65,533 raw source bytes, 3,840 instructions and 255 nested loops.
The source limit keeps a complete request within the native 65,536-byte input
view. It passed 42 independent-interpreter checks and 47 Windows native
checks plus 530 byte/property cases
plus three native rebuild generations. Android passed three filter-frontend
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

## Preceding filter frontend measurements

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
XAX graph or original competitor result changes. The separate
[fresh-process experiment](18_BACKEND_BUILD_CACHE.md) now carries the same
existing API through complete builds. It validates all sixteen v4 artifacts
on both targets and times three sources, with 1.009x Android-target / 1.001x
Windows-target point estimates. Neither comparison is significant; Windows'
exploratory interval includes a slowdown. Brainfry remains about 56–57x faster
on that subset, with lower compiler RAM and smaller files. The cold
configuration remains experimental. Windows native-helper execution is still unavailable through
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
| [frontend_capacity_gate.json](../evidence/frontend_capacity_gate.json) | Carry-triggered capacity flag; exhaustive states, independent seed, Windows/Android fixed points and importer parity, paired frontend trials and rejected gate candidate |
| [brainfly_brainfry_followup.json](../evidence/brainfly_brainfry_followup.json) | Installed SDK identity; twelve Brainfly JIT and generated NativeAOT correctness cases; pinned Brainfry release tests and reproduced optimizer defects; no new competitive timing score |
| [bfx_v2_optimization.json](../evidence/bfx_v2_optimization.json) | BF clear/full-wrap optimizer, canonical v1/v2 importer, independent/native correctness, optimized fixed points and separate three-arm complete build/process/resource measurements |
| [bfx_v3_arithmetic.json](../evidence/bfx_v3_arithmetic.json) | Standard BF arithmetic packing, canonical v1/v2/v3 consumer, 908 cross-target record cases, 22,120 full-buffer calls and three-component native fixed points; timing measured separately |
| [bfx_v3_measurements.json](../evidence/bfx_v3_measurements.json) | Matched three-run v2/v3/Brainfry timings, memory and full sizes; arithmetic native-call improvements remain distinct from later movement results |
| [bfx_v4_movement.json](../evidence/bfx_v4_movement.json) | Monotone movement packing, bounds proofs, 1,164 importer cases, 9,592 complete-buffer calls and four-component native fixed points |
| [bfx_v4_measurements.json](../evidence/bfx_v4_measurements.json) | Fresh matched v3/v4/Brainfry complete builds, process execution, native calls, resources and full file sizes; no overall sweep |
| [bfx_v4_native_boundaries.json](../evidence/bfx_v4_native_boundaries.json) | Current native frontend boundaries, oversized-view guards and three maximum-count v4 stores, exact on both targets |
| [bfx_v4_call_controls.json](../evidence/bfx_v4_call_controls.json) | Post-primary load/slot/thread-CPU diagnostics on four selected Android cases; identical-library controls, raw primary scores retained |
| [scalability_capacity_audit.json](../evidence/scalability_capacity_audit.json) | Current resource-cap rejection of pinned Brainfry Mandelbrot; no timing score |
| [streaming_frontend_prototype.json](../evidence/streaming_frontend_prototype.json) | Private BF chunk filtering/validation snapshot on both targets; does not itself compile larger programs |
| [streaming_frontend_bootstrap.json](../evidence/streaming_frontend_bootstrap.json) | Three identical bounded-pipeline rebuilds and native/independent own-source parity; private packet rejected by ordinary BFX import |
| [streaming_frontend_verification.json](../evidence/streaming_frontend_verification.json) | Source/fixture and unchanged-bootstrap audit, tool identities and immutable earlier reports |
| [wide_profile.json](../evidence/wide_profile.json) | Separate v5 native coordination/import, larger compiled programs, exact Mandelbrot, capacity stress and explicit fixed-budget limits |
| [stream_runs.json](../evidence/stream_runs.json) | Native streaming run properties, independent checks, complete-buffer regressions and private fixed-packet specialization |
| [wide_bootstrap.json](../evidence/wide_bootstrap.json) | Three identical native own-source cycles through v5, verified canonical edits, source/SDK audit and publication replay |
| [wide_final_audit.json](../evidence/wide_final_audit.json) | Final private coordinator reproduces all fourteen verified regression stores; local links and fixed-budget scope checked |
| [backend_build_cache.json](../evidence/backend_build_cache.json) | Existing compile-local proof cache through complete fresh builds; 64 byte-identical validation builds, both-target execution, seven cache tests and 216 timed three-source BBC/BBC-cache/Brainfry builds; negligible gains and open gates retained |
| [build_runtime_resources.json](../evidence/build_runtime_resources.json) | Fresh complete-build latency, compiler/runtime memory, Windows standalone comparisons, raw samples, calibrations, excluded launcher probe and explicit scope |
| [standalone_windows.json](../evidence/standalone_windows.json) | Canonical Windows host and public hello transaction; 23 native programs, 28 host checks, native binding replay/verify/stale rejection and exact empty/hello rebuilds; explicit unchanged generic inlining configuration |
| [standalone_android.json](../evidence/standalone_android.json) | Static Android process host and binding, correctness/artifact hashes, primary raw process timings against pinned Awib/brainfry, size summaries, retained excluded concurrent-validation probe |
| [standalone_native_replay.json](../evidence/standalone_native_replay.json) | Native-only replay of 23 Android programs; exact native authority; Windows driver binding replay, verification and stale-root rejection |
| [wide_tape_reset.json](../evidence/wide_tape_reset.json) | Current canonical importer transaction; 393 cases per version/target, 380 decision checks per version/target, three twenty-check frontend generations per target, native-call A/B and fresh Android process comparisons |
| [windows_native_driver.json](../evidence/windows_native_driver.json) | Bounded Windows native CLI: 212 verification cases with explicit declines/diagnostic gap, PE/resolve/edit fixtures, 31 adapter checks and 256 flag-regression inputs; no native corrected self-store verification |
| [windows_native_driver_followup.json](../evidence/windows_native_driver_followup.json) | Canonical diagnostic-order correction; 160 exact full-diagnostic semantic cases, 110 helper checks, native build/edit controls, packed-v5 verification and original-driver decoder/CFG/table diagnosis; self-store/native-pipeline gates remain open |
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
| [bfx_xax_import.json](../evidence/bfx_xax_import.json) | Initial canonical importer replacement and its source/validation scope; later target and reset reports retain separate identities |
| [repository_cleanup.json](../evidence/repository_cleanup.json) | Historical repository cleanup and external recovery archive; Git history was preserved |

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
  remaining costs before extending the frontend. P1 clear/full-wrap folding is
  implemented, and v3 arithmetic powers are EXECUTED. General odd-step clear, affine transfer,
  scan and movement-envelope optimization still need independent equivalence
  proofs, safe bounds/error ordering, versioned BFX design and native evidence.
- Linux execution is UNIMPLEMENTED in this integration; no Linux execution
  host is available. Cross-compilation alone will not establish support.
- Native XAX compiler-host execution on Android is UNIMPLEMENTED in this cycle.
- The general ARM64 large-composite return-copy defect remains open as
  [XAX OI-49](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/XAX_OPEN_ISSUES.md#oi-49--android-arm64-large-composite-return-copy).
  The importer uses checked scratch outputs and mixing results of at most
  16 bytes, so it avoids that operation and executes successfully.
- M4 is incomplete: frontend profiling, two P0 improvements and the first
  [competitor test-pipeline pilot](08_BENCHMARKS.md) are MEASURED. Further P1/P2,
  steady-state comparisons, broader compiler/deployment boundaries,
  broader compiler/runtime RAM coverage and full application coverage remain.
  The new twelve-source follow-up supplies scoped build/RAM measurements. XAX graph
  verification bucket includes cold helper setup. The follow-up identifies
  local proof-cache reuse, repeated checked-access type hashing and the
  missing Windows native-helper host path. The new
  [cold-build cache experiment](18_BACKEND_BUILD_CACHE.md) reuses the existing
  APIs with an empty cache and full first verification, but measures only
  negligible complete-build gains. It does not close the backend latency gap;
  any new helper integration must be canonical XAX graph work. The standalone
  hashing host covers hashing and stream transport. The separate native driver
  prototype executes the store/graph/CFG/type/verifier chain on tested stores;
  full diagnostic/large-store coverage, common-loader migration and BBC DLL
  packaging remain outstanding. The [native-driver follow-up](19_NATIVE_DRIVER_FOLLOWUP.md)
  fixes the known mismatch, checks all 508 original graph bodies natively and
  rules out the audited decoder/CFG/table budgets. A private canonical probe
  locates the self-store decline at resource-callee action 2; its underlying
  graph outcome remains under investigation.
  Frontend tuning does not
  address these backend costs. M8 is NOT YET ACHIEVED; follow
  [the measurement and coverage plan](06_PERFORMANCE_PLAN.md).
- No stable release or performance superiority is claimed. Android and Windows
  are required; Linux implementation and benchmarking are optional and non-gating.
