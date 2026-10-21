# BBC and BFX status

Current migration: **2026-10-20–21**. Production uses one
[BFX specification](02_BFX_CONTRACT.md), with new magic `42 46 58 00` and
identifier `01`. No other identifier, legacy decoder or fallback is accepted.
All optimization levels and supported source sizes use the same u32-count
record and shared canonical XAX decoder. Current XAX sources are pinned in
[integration](03_XAX_INTEGRATION.md).

## Current execution evidence

[canonical_bfx.json](../evidence/canonical_bfx.json) records exact source,
transaction, native-image, test-tool and result hashes. Android execution uses
a Pixel 8 Pro, Android API 37; Windows uses x86-64 native DLLs. These are
correctness/coverage results, not performance scores.

| Check | Current result |
|---|---|
| Strict decoder | 1,231 cases; 6,155 Windows calls across five alignments; all cases also execute on Android |
| Importer rejection | 1,168 invalid records per target; includes old signatures and all unsupported identifiers |
| Source coordination | 433 cases per target, including 1 MiB source, binary input and maximum count/depth |
| Streaming packing | 215 cases per target; CLEAR and existing encoded opcodes preserved; 260 additional Windows header rejection checks |
| Private BF run core | 1,800 cases per target, including independent zero/opaque opcode checks, guards and five Android alignments |
| Bounded frontend | 274 cases per target, including all twelve migrated fixtures and source/count/depth limits |
| Bounded transforms | All 57 migrated static cases pass natively on both targets and independently; 15 further per-target shared-opcode cases |
| Frontend bootstrap | Three identical native own-source BFX/store/artifact generations on each target |
| Six BF components | Each compiles through native source/packing/import; Android/Windows record and store bytes match |
| Complete programs | Fourteen streaming regressions and twenty bounded optimization-level variants; six full-buffer vectors each per target |
| Maximum native imports | Five 65,536-instruction stores match across targets; canonical storage integrity checked, not full SSA/lowering of all maximum graphs |
| Mandelbrot | Transparent and packed programs execute on both targets with exact 6,240-byte output |

Current source limits are **65,533 raw bytes / 3,840 instructions / depth 255**
for the bounded frontend, and **1 MiB / 65,536 pre-pack instructions / balanced
depth 32,768** for streaming compilation. They are implementation budgets,
not format variants. Runtime workspace growth remains UNIMPLEMENTED.

## Authority and historical boundaries

All BBC implementation remains standard BF; XAX owns canonical graph import,
ABIs, native code and packaging. Native component calls have no interpreter
fallback and record artifact/authority identities. Generic verification,
lowering and packaging still run on Windows using unchanged Python SDK files;
Windows common-helper loading still falls back to Python. This does not complete
the native XAX compiler driver or establish an Android-hosted compiler.

The standalone process hosts and Android demo embed decisions rather than BFX
decoders. Their previous process/packaging/eight bounded Activity checks remain
historical, not new application coverage. Linux execution remains unverified.
All 44 pre-migration BBC evidence files retain exact bytes. Old executable wire
fixtures were migrated; old implementation and fixture bytes remain in Git history.
Previous named formats appear below only to identify historical evidence.

## Modernization baseline

The new assignment's [Milestone 0 audit](20_MODERNIZATION.md) is EXECUTED and
MEASURED at BBC 2d9fbd6 / XAX 42de0fc. It records 180 fresh-process builds,
three workloads, both target outputs, kernel resident/commit counters and stage
timing. All six Android baseline programs execute correctly. BBC build medians
are 1.46 to 1.58 seconds versus 23 to 24 ms for pinned Brainfry on this subset.
This is a frozen diagnostic baseline, not a new implementation speedup or
competitive milestone. The native driver accepts the current hello bound store,
source coordinator and importer, but declines its self-store and the small
two-distinct-resource-callee fixture. The public entry point was open at that baseline and is implemented by the
following phase. Full native packaging and broader evaluation remain open.

## Historical evidence index

| Report | What it establishes |
|---|---|
| [frontend_capacity_gate.json](../evidence/frontend_capacity_gate.json) | Carry-triggered capacity flag; exhaustive states, independent seed, Windows/Android fixed points and importer parity, paired frontend trials and rejected gate candidate |
| [brainfly_brainfry_followup.json](../evidence/brainfly_brainfry_followup.json) | Installed SDK identity; twelve Brainfly JIT and generated NativeAOT correctness cases; pinned Brainfry release tests and reproduced optimizer defects; no new competitive timing score |
| [bfx_v2_optimization.json](../evidence/bfx_v2_optimization.json) | BF clear/full-wrap optimizer, canonical v1/v2 importer, independent/native correctness, optimized fixed points and separate three-arm complete build/process/resource measurements |
| [bfx_v3_arithmetic.json](../evidence/bfx_v3_arithmetic.json) | Standard BF arithmetic packing, canonical v1/v2/v3 consumer, 908 cross-target record cases, 22,120 full-buffer calls and three-component native fixed points; timing measured separately |
| [bfx_v3_measurements.json](../evidence/bfx_v3_measurements.json) | Matched three-run v2/v3/Brainfry timings, memory and full sizes; arithmetic native-call improvements remain distinct from later movement results |
| [bfx_v4_movement.json](../evidence/bfx_v4_movement.json) | Monotone movement packing, bounds proofs, 1,164 importer cases, 9,592 complete-buffer calls and four-component native fixed points |
| [bfx_v4_measurements.json](../evidence/bfx_v4_measurements.json) | Fresh matched v3/v4/Brainfry complete builds, process execution, native calls, resources and full file sizes; no overall sweep |
| [bfx_v4_native_boundaries.json](../evidence/bfx_v4_native_boundaries.json) | Recorded native frontend boundaries, oversized-view guards and three maximum-count v4 stores, exact on both targets |
| [bfx_v4_call_controls.json](../evidence/bfx_v4_call_controls.json) | Post-primary load/slot/thread-CPU diagnostics on four selected Android cases; identical-library controls, raw primary scores retained |
| [scalability_capacity_audit.json](../evidence/scalability_capacity_audit.json) | Recorded resource-cap rejection of pinned Brainfry Mandelbrot; no timing score |
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
| [wide_tape_reset.json](../evidence/wide_tape_reset.json) | Recorded canonical importer transaction; 393 cases per version/target, 380 decision checks per version/target, three twenty-check frontend generations per target, native-call A/B and fresh Android process comparisons |
| [windows_native_driver.json](../evidence/windows_native_driver.json) | Bounded Windows native CLI: 212 verification cases with explicit declines/diagnostic gap, PE/resolve/edit fixtures, 31 adapter checks and 256 flag-regression inputs; no native corrected self-store verification |
| [windows_native_driver_followup.json](../evidence/windows_native_driver_followup.json) | Canonical diagnostic-order correction; 160 exact full-diagnostic semantic cases, 110 helper checks, native build/edit controls, packed-v5 verification and original-driver decoder/CFG/table diagnosis; self-store/native-pipeline gates remain open |
| [windows_native_resource_diagnosis.json](../evidence/windows_native_resource_diagnosis.json) | Private canonical probe identifies the declined self-store entry graph and zero defer token; five tiny normal-driver resource-call controls and exact fixture rebinding isolate a separate multiple-callee coverage limit |
| [windows_native_verification_profile.json](../evidence/windows_native_verification_profile.json) | Three separate runs, ten randomized pairs per case/run for Python versus native verification CLI; raw samples on the current Windows host; no full-build or competitor result |
| [windows_hash_host.json](../evidence/windows_hash_host.json) | Standalone canonical Windows hashing host: 139 successful streams, five failure cases, explicit error-state transaction and byte-identical PE rebuild; no compiler-loader integration |
| [graph_verification_profile.json](../evidence/graph_verification_profile.json) | Cold reader/check decomposition, Python fallback authority, repeated type-hash trace, existing proof-cache tests and warm XAX-stage A/B; no new competitor verdict |
| [competition_pilot.json](../evidence/competition_pilot.json) | Pinned Awib/brainfry native process, test-pipeline compile and artifact-size pilot on both required targets; all eight projects remain visible; no sweep |
| [frontend_filter_windows.json](../evidence/frontend_filter_windows.json) | Recorded BBC source with the preceding importer: 42 seed checks, 393 importer cases, 47 native checks and three Windows generations |
| [frontend_filter_android.json](../evidence/frontend_filter_android.json) | Recorded BBC source with the preceding importer: three generations, twelve fixtures per generation and seven boundary checks |
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


## Remaining work

- General potentially unbounded Android decisions need an executed off-main
  worker path with verified lifetimes and UI result delivery. The current
  app embeds a bounded decision and calls it synchronously in lifecycle/UI flow.
  Existing XAX managed callbacks and pthread contracts are enabling facilities,
  not evidence that this integration has been implemented.
- After P0 decoding, slot transfer dominates accepted-instruction work and
  grouped length bookkeeping dominates ignored NUL input. Profile those
  remaining costs before extending the frontend. P1 clear/full-wrap folding is
  implemented, and arithmetic powers are EXECUTED. General odd-step clear, affine transfer,
  scan and movement-envelope optimization still need independent equivalence
  proofs, safe bounds/error ordering, validated shared-opcode design and native evidence.
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
  locates the self-store decline at resource-callee action 2 in its entry graph,
  with no deferred callee token. A separate 1,919-byte multiple-callee case
  reproduces a small coverage gap. The underlying entry-graph failure remains
  under investigation; the probes do not prove a common cause.
  Frontend tuning does not
  address these backend costs. M8 is NOT YET ACHIEVED; follow
  [the measurement and coverage plan](06_PERFORMANCE_PLAN.md).
- No stable release or performance superiority is claimed. Android and Windows
  are required; Linux implementation and benchmarking are optional and non-gating.

## Unified compilation phase

**IMPLEMENTED and EXECUTED:** one public compile_bfx entry for 1 MiB sources,
65,536 pre-pack commands and depth 32,768; O0/O1 share one BFX format.
The Windows emit-bfx/check/info command executes without Python. The bounded
compiler and manual pass interfaces are private seed/reference components.
[The guide](21_UNIFIED_COMPILATION.md) and [raw report](../evidence/unified_compilation.json)
record 1,074 per-target frontend cases, eleven unchanged-buffer Windows
rejections, 1,899 CLI checks, 468 generated-program full-buffer calls,
three identical final frontend generations on each target and Mandelbrot replay.
No existing evidence report is rewritten. The streaming coordinator fixes
capacity-before-bracket precedence across chunks.

Full native compilation remains INCOMPLETE. At the interface phase's pinned
driver source, an Android snapshot packages and runs hello, while the Windows
build rejects one-bit values; subsequent lowering results follow below.
Library packaging, self-store/multiple
resource-callee coverage and common helper loading remain open. No new complete
build speedup, advanced loop optimization or universal competitor win is claimed.

## Native frame backend follow-up

[Native bits1 evidence](../evidence/native_bits1.json) records the next
canonical XAX driver change: frame fallback supports one-bit AND/OR/XOR.
Forty-eight build controls and 160 exact diagnostic controls pass. 3 of six
prepared BBC target snapshots build, reproduce and execute correctly; inspect
the raw report for remaining failures. Earlier interface-phase observations
are preserved as snapshots. Full source-to-native driver, libraries, graph
reuse work and competitive targets remain INCOMPLETE.

## Native lowering follow-up

[The preceding native lowering phase](22_NATIVE_LOWERING.md) and its
[immutable report](../evidence/native_windows_lowering.json) extend that scope:
all six original prepared target snapshots now build twice identically and
execute correctly. A separate 42-target corpus passes 38. Android deep-512
verified but declined during build; three Windows cases rejected a call ABI
shape. The Android follow-up below resolves that target's decline.
The report includes 786,432 counted byte-operation route executions, pointer
and stack cases, and 160 preserved semantic diagnostic cases. Prepared native
build medians of 24.25–31.83 ms exclude frontend/import/binding. OS samples show
about 3.31 GiB private commit despite 11.2–13.3 MiB resident memory.
The public native build workflow, libraries, self-store/resource-callee coverage,
common loading, M4 and M8 remain incomplete. Historical reports retain their
original bytes and scope.

## Android native lowering

[The Android follow-up](23_ANDROID_NATIVE_LOWERING.md) fixes the depth-512
native build decline through checked allocation of live-interval records
inside the existing fixed arena. All 22 prepared Android snapshots pass
44 native builds and 47 actual Pixel 8 Pro executions. Each build pair has
identical artifact/provenance bytes, and all 20 previously successful Android
artifacts remain exact. Both zero-entry and active depth-512 programs pass.
There are 388 allocation boundary/random cases, six exhaustion calls, four
framed O0/O1 frontend checks, 160 exact diagnostic controls and three unchanged
Windows smoke artifacts. [Raw evidence](../evidence/native_android_lowering.json)
preserves source hashes, failed private attempts and unscored timing samples.
A separate [Android hello smoke](../evidence/android_hello_smoke.json) adds two
identical native builds and one device execution, retaining the 5,880-byte ELF.

The BFX contract and BBC implementation streams are unchanged. The fixed view
budgets do not grow dynamically, and no peak-RAM or competitor win is claimed.
Full source workflow, Android-hosted compiler execution, self-store/resource
verification gaps, common loading and shared libraries remain incomplete.
Android graph-analysis cost and the complete native workflow take priority.
M2/M4 remain incomplete; M8 is not achieved.
