# BBC measurement plan

Status: **MEASURED** initial Awib/brainfry process-execution, test-pipeline
compilation and size pilot on Android ARM64 and Windows x86-64. The
[results and eight-project coverage matrix](08_BENCHMARKS.md) are separate
from this plan. The [fresh-build/resource follow-up](08_BENCHMARKS.md#build-latency-ram-and-windows-standalone)
now measures both target builds, compiler/runtime memory and Windows standalone
processes on the twelve-source corpus. Steady-state runtime, broader RAM
coverage, real-application comparisons,
best-mode coverage and scored deployment timing remain incomplete.
The competitive objective is **NOT YET ACHIEVED**. Linux is optional and
never gates functional delivery or a required-target sweep.

The [v2 follow-up](11_V2_BENCHMARKS.md) retains that twelve-source corpus and
adds four preregistered clear-loop workloads. It reports three-arm complete
build/process/resource trials and a separately preregistered native-call BBC
A/B. Every timed result is checked; all builds reproduce validated artifact
hashes. Its caller allocation policy, current CPU and native/bootstrap
boundaries are explicit, so earlier snapshots retain their own scopes.

## Next gate and ownership

The current P0 frontend has been revalidated on both required targets.
The [Windows report](../evidence/frontend_filter_windows.json) records independent
seed and Windows execution; [Android follow-up](../evidence/frontend_filter_android.json)
records three native generations and boundary checks.
Earlier [app and self-hosting evidence](05_STATUS.md) remains
tied to its original source hashes. Do not rebuild an already demonstrated app
merely to repeat M2.

P0 profiling separates length bookkeeping, opcode comparisons, slot movement
and emission on ignored ASCII, raw NUL, raw FF, instruction-heavy input,
nested loops and own source. Both the grouped-byte counter and single-copy
opcode decoder are implemented and measured; [proofs](07_OPTIMIZATION_PROOFS.md)
record their invariants and costs. After decoding, slot transfer accounts for
53% of executed work on the fixed baseline compiler source; grouped length
bookkeeping accounts for 79% on maximum ignored NUL. Profile these remaining
costs before extending P0, retaining raw FF/NUL, instruction-heavy and
self-compilation coverage. The competitor pilot identifies graph verification as a
larger test-pipeline compilation cost than BBC filtering. Investigate that
stage through XAX-native facilities before expensive frontend work intended
to close the full compilation gap. The
[verification follow-up](08_BENCHMARKS.md#verification-cost-diagnosis) now
separates cold helper setup, type-CID hashing and repeated verification.
It measures existing proof-cache reuse in a warm backend-stage prototype;
full cold pipeline and competitor timing must be rerun before updating their
scores. New Windows helper integration must remain XAX graph work, with
legacy Python left unchanged. Do not multiply ratios from different benchmark
snapshots or claim a full-pipeline win from a frontend-only improvement.
The [standalone Windows hashing host](03_XAX_INTEGRATION.md#windows-native-hashing-host)
is now implemented and executed, reusing the existing XAX BLAKE3 graph.
It does not activate the common helper loader or the complete native
verification path. Its inherited 16 MiB input limit also excludes the larger
general compiler-driver store. A separate
[Windows native driver prototype](03_XAX_INTEGRATION.md#windows-native-driver-prototype)
now executes the verifier chain on tested stores and has
[fresh-process CLI measurements](08_BENCHMARKS.md#windows-native-verification-cli).
Four malformed cases decline, one rejection diagnostic differs, and the
corrected self-store, large flag edit and DLL packaging decline. Complete those
gates and common-loader integration, then measure the full pipeline before
changing competitive claims.
The external interpreter records exact executed instructions and highest
visited tape cell. Those counters are diagnostic work measures, not native
runtime or compiler timing. A counted instruction includes each dispatched
command; a closing bracket jumps to the loop body when nonzero.

The [eight-byte tape reset](07_OPTIMIZATION_PROOFS.md#xax-eight-byte-tape-reset)
is now verified in the canonical importer and measured on both required targets.
Its scope is full-tape initialization in generated native calls. The separate
Android process recheck still favors Awib and brainfry; complete native-driver
integration and full-pipeline measurements remain necessary to close the build
gap. This change does not implement Brainfuck source rewriting.
The [standalone Android host](03_XAX_INTEGRATION.md#standalone-android-process)
now removes the fixed shared-library process host. Its fresh twelve-program
comparison favors BBC over pinned Awib, while brainfry remains faster.
Preserve that narrow result. The later [build/resource follow-up](08_BENCHMARKS.md#build-latency-ram-and-windows-standalone)
measures fresh compiler latency, runtime/compiler memory and Windows standalone
execution. Broader workload, best compatible mode and real-application gates remain. Source
optimization and lower generated-code cost are still needed for hot compute
and file-size comparisons.

BBC owns source recognition, analysis and optimization in standard Brainfuck.
The optional `compiler/optimize.bf` pass now folds exact clear loops and full
arithmetic wraps under the [v2 contract](10_BFX_V2_CLEAR.md), with canonical
XAX lowering. Retain transparent BFX v1 for differential tests. Before any
further optimized opcode, specify encoding, safety, rejection rules,
resource/fallback budgets and XAX lowering support.
Use checked mathematical offsets capable of representing beyond signed 16 bits;
preserve intermediate movement traps and conditional loop entry.

The [Brainfry analysis](09_BRAINFRY_ANALYSIS.md) records the SDK follow-up,
reproduced even-step clear and movement-envelope defects, and prioritized
build/runtime/memory/size work. The first capacity-flag frontend change
has its own [proof and Android/Windows A/B scope](07_OPTIMIZATION_PROOFS.md#p0-carry-triggered-capacity-flag).
Android native execution also passes three generations. Retain the negative cases when implementing
source-loop rewriting; they are not timed workloads.

The actual XAX integration is pinned in [03_XAX_INTEGRATION.md](03_XAX_INTEGRATION.md).
It has canonical decoder/importer/application stores, verified workspace saves
and expected-root transactions. Generic verification, native lowering and
packaging still use disclosed unchanged legacy Python tools on Windows.
This is not a whole-toolchain XAX-only or Android-hosted compiler claim.

## Comparator coverage

Use the exact pins, executed modes and blockers in
[08_BENCHMARKS.md](08_BENCHMARKS.md). Awib C and brainfry native AOT have
executed on both required targets. Brainfry's freestanding ARM64 syscall
output is tested on Android; a Linux target name alone is not grounds for
excluding a working Android execution path. No desktop Linux result is used.

The matrix retains all eight projects. Missing LLVM/MLIR development
toolchains are local build blockers, not victories or proof
of unsupported platforms. Unverified translation routes remain visible.
The .NET SDK is now installed and the pinned Brainfly JIT and generated
NativeAOT modes pass the twelve-program Windows correctness corpus; their
scored timings and Android eligibility remain unverified.
Verify best compatible alternate modes before unrestricted claims; JIT and
interpreter/VM results must retain their distinct labels.

Publish GCC/Clang optimized C and optimized Rust translation references with
the translator pinned and translation time included. The pilot's Awib C
rows also supply the same translator's GCC-Windows/Clang-Android references;
do not count duplicate data as extra independent compiler wins. Clang-Windows
is now measured on the original twelve-source corpus; optimized Rust still
needs complete measurements. All such tools and drivers remain outside both
implementation repositories.

## Corpus and execution prerequisites

Freeze source bytes, supplied bytes/flags, inputs, hashes, expected outputs,
eligible common subsets, exclusions and holdouts before optimization tuning.
Pre-register sanity/short-run, hot-compute and real-decision runtime categories.
Extend the small existing sanity corpus with transfer/multiply, scans,
checksum/math, nested loops and source-limit stress only as needed. Programs
outside the 3,840-instruction or 65,533-source-byte limits are **UNSUPPORTED**.
Never change an algorithm or hide exclusions to improve a score.

Before a general claim, require at least 20 real eligible workloads per target,
including three distinct decision modules exercised once and repeatedly from
a real XAX app. Each unrestricted competitor result needs at least ten distinct
comparable workloads spanning two categories; otherwise **INSUFFICIENT COVERAGE**.
Correctness-only bounds, EOF, failure ordering and capped nontermination cases
are not normal runtime races. A timeout proves neither equivalence nor divergence.

Inspect each baseline's actual wrapping, tape, EOF, bounds and failure behavior.
Validate successful bytes and status before timing a semantics-equivalent subset.
Record profile incompatibility; do not weaken BBC's semantics. Any external
reference adapter must preserve semantics and include its costs.

The fixed Android app currently calls its bounded embedded decision synchronously
from lifecycle/UI flow. A general potentially unbounded decision worker path
remains **UNIMPLEMENTED**. XAX has managed callback carriers and pthread contracts;
their existence alone does not prove the required worker/JNI lifetime/UI delivery
integration. Implement that flow as verified graphs and execute it before
expanding the demo to unbounded programs. No foreign shim or main-thread
unbounded demonstration can satisfy this gate.

## Measurement and pass rules

Keep the runner external to both implementation repositories and pin its
revision/hash. Publish static raw samples, corpus and artifact hashes. Use a
pinned native BBC frontend for scored end-to-end compilation; report interpreter
seed bootstrap separately. Record the same build host/configuration, execution
device/ISA, OS, flags, toolchains, thermal/power conditions and target revisions.

Separate cold process startup, warm complete calls including tape reset, real
app calls, BBC frontend, XAX import/verify/lower and complete source-to-runnable
build/package cost. Compare matching process/function and artifact boundaries.
Report raw bytes/s, instructions/s, executed BF steps/raw byte and optimizer
cost. Measure compiler/runtime RAM independently; full-pipeline memory is peak
simultaneous live process-tree memory, with shared-page/sampling policy stated.
Separate module code/data from stripped executable/APK bytes and virtual
reservation from resident/committed memory. Energy is **NOT MEASURED** until
controlled device measurements exist.

Use counterbalanced paired order, warmups, at least ten timed trials across
three independent runs, batching complete short calls above timer resolution.
Consume or verify every result. Publish medians, IQR and paired log-speedup
confidence intervals; pre-register comparison families and use Holm adjustment
or a justified alternative. Report category means and worst regressions.

A per-competitor victory needs statistically supported runtime and full-build
geometric-mean speedups above 1.0, no supported category slowdown above 10%,
and separate baseline/BBC geometric-mean ratios at least 1.0 for compiler RAM,
runtime RAM and comparable artifact bytes. Sampled RAM near parity needs a
pre-registered uncertainty rule ruling out meaningful regression. Stretch
targets are 1.20 runtime and 1.10 compile/resources. Missing data never passes.

A target sweep requires every eligible named competitor to pass all gates,
coverage and correctness, with at least one eligible comparator. Both required
targets must independently pass before claiming **surpassed all eligible
Android/Windows comparators**. Translation references remain prominent and
separate. No universal or cross-machine victory is implied.

For each optimization, record its falsifiable hypothesis, proof and work/tape
budget, targeted adversarial tests, self-hosting, and same-machine A/B stage
costs. Keep it only with a demonstrated net benefit; report rejected attempts
and approximate repeated-call break-even cost. Semantic correctness and source
purity are absolute gates. Full pinned sweeps belong at M8, not every small edit.

The [v3 matched run](13_V3_BENCHMARKS.md) follows the fixed-corpus protocol
with twelve observations across three independent runs per arm/case/target.
Its exploratory intervals and exact three-run sign-flip limitations do not
meet the confirmatory competitor-victory gates above.

The [v4 matched run](15_V4_BENCHMARKS.md) retains that sixteen-source corpus
and trial count, comparing v3, v4 and pinned Brainfry. It remains an
exploratory optimization measurement; missing modes and confirmatory
competitor-victory gates remain open.
