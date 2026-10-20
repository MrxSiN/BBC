# Compile-local verification cache

This experiment carries XAX's existing successful-object proof cache through
a fresh source-to-runnable build. It uses the native v4 BBC frontend and
optimization passes, native import, and unchanged generic Windows-hosted XAX
verification, binding, lowering and packaging. It adds no BBC executable
source, XAX graph or native helper implementation.

**MEASURED:** complete-build speedups are only 1.009x for Android-target and
1.001x for Windows-target builds. Windows' exploratory interval includes a
slowdown. The earlier warm-stage cache gain does not establish a comparable
cold-process gain. Keep this configuration experimental; no material build
gap is closed. [Raw evidence](../evidence/backend_build_cache.json) preserves
the frozen plan, 216 timed builds, correctness checks and source authority.

## Configuration and trust boundary

Create one empty `ProofCache` per compiler process. Give it to the first
`StoreReader` for native-imported bytes and run `verify_store`. The cache must
have zero entries and zero hits at this first verification. No proof sidecar
or producer assertion supplies a trusted fact.

Apply the existing expected-root binding transaction to the canonical
standalone host. The existing `apply_reference` result does not retain a
reader cache. Construct the bound `StoreReader` from those exact result bytes
with the same local cache, then run `verify_store` before lowering. The
unchanged verifier checks store integrity, reference resolution, rootedness
and cycles and reuses successful object facts under its existing verifier
identity, content identity and dependency tuple contract. Changed objects
still require verification. Android's packaging path also retains that reader
for its existing verification calls. Discard the cache when the build exits.

Windows uses the existing inlined lowering view and default function closure.
This experiment does not combine cache reuse with the separate v5 Windows
closure-pruning configuration. Both arms close the importer output mapping
before verification/lowering and retain the full 65,536-cell execution tape.

The cache is build configuration through existing generic APIs. External
orchestration lives outside both implementation repositories and supplies no
Brainfuck parsing, optimization, BFX translation or native backend.

## Validation and measurement boundary

All sixteen v4 corpus programs must reproduce the prior executable hashes on
both targets. Cached and uncached builds must also agree on BFX, imported
store, binding transaction and bound-store hashes. Execute the Windows
programs and the identical cached Android artifacts against exact inputs and
expected outputs. Run the unchanged generic cache tests, including stale
invalid semantics, verifier identity, dependency tuples and corruption.

The timing subset is fixed before timing: `hello` for sanity, `nested_math`
for the largest existing hot-compute instruction count, and `checksum_four`
for a decision with four fixed input bytes. These three sources do not meet
general competitor coverage requirements.

Compare baseline BBC, cache-enabled BBC and pinned Brainfry in twelve paired
observations per case/target/arm across three runs. Use each of the six arm
orders twice, with one excluded fresh-build warmup per arm/case/target/run.
The timer surrounds process launch through output collection and exit. It
includes interpreter/SDK startup, frontend passes, import, first verification,
binding, lowering, packaging and file I/O. OS file caches are warm; hardware
cold boot is not controlled. Compiler RAM is the single process's kernel
lifetime peak working set; peak pagefile usage is a separate counter.

Report raw samples, medians, IQRs, paired speedups and run-cluster intervals.
With only three independent runs, exact two-sided sign-flip tests have a
minimum p-value of 0.25. Holm correction cannot turn this experiment into a
confirmatory competitor victory. No runtime, deployment, application,
energy or general compiler-process-tree memory result follows from these
build measurements.

## Results

All 64 validation builds reproduce the prior v4 executable hashes across
sixteen sources, two targets and two BBC configurations. Each cached first
verification has 23 misses, zero hits and zero prior entries. Bound stores
reuse 20 object facts and still verify 17 misses for Android or 29 for
Windows. BFX, imported-store,
transaction and bound-store hashes agree between arms. All 32 Windows
executions pass, as do the sixteen Android programs whose artifacts are
identical between arms. The seven unchanged generic cache tests pass.
Thirty-four executed generic SDK modules match the pinned bootstrap sources
after disclosed CRLF normalization; all 41 prior evidence reports retain
their bytes. The native BF components retain their recorded identities.

The three-run experiment has twelve observations per source/target/arm,
plus excluded warmups. Complete-build medians in milliseconds are:

| Target | Source | BBC baseline | BBC local cache | Brainfry |
|---|---|---:|---:|---:|
| Android ARM64 | hello | 1674.907 | 1664.362 | 28.050 |
| Android ARM64 | nested_math | 1594.869 | 1595.616 | 28.179 |
| Android ARM64 | checksum_four | 1559.630 | 1536.236 | 28.093 |
| Windows x86-64 | hello | 1684.263 | 1686.620 | 29.024 |
| Windows x86-64 | nested_math | 1621.041 | 1608.709 | 28.019 |
| Windows x86-64 | checksum_four | 1565.260 | 1566.445 | 27.764 |

These builds run on Windows with Ryzen 7 5800H and Python 3.13.5. The Android
artifacts execute on Pixel 8 Pro, API 37. Source, native components, hosts,
generic SDK and Brainfry pins and hashes are in the report. SDK import and
helper setup remain inside the fresh-process boundary; no overhead is
subtracted. Do not combine these times with another host's measurements.

| Build comparison, numerator/cache | Paired geometric-mean ratio | Exploratory 95% run-cluster interval | Holm-adjusted p |
|---|---:|---:|---:|
| Android BBC baseline | 1.009 | 1.005–1.012 | 1.0 |
| Windows BBC baseline | 1.001 | 0.979–1.016 | 1.0 |
| Android Brainfry | 0.0180 | 0.0172–0.0188 | 1.0 |
| Windows Brainfry | 0.0174 | 0.0171–0.0179 | 1.0 |

Ratios above one favor cached BBC. Per-case regressions remain in the table;
the worst median baseline/cache ratio is 0.999 for Windows hello. None of
the four hypotheses passes the registered significance rule. The three-run
intervals are exploratory even where they exclude one. Brainfry's complete
builds remain about 56–57 times faster on this subset.

Cache-enabled compiler peak working-set medians are 57.38–57.45 MiB;
Brainfry's are 5.15–5.17 MiB. The baseline/cache geometric-mean working-set
ratios are 0.9995 on Android-target builds and 1.0004 on Windows-target builds;
no RAM improvement is established. The excluded touched-16-MiB control
increases the kernel working-set counter by exactly 16 MiB. Peak pagefile
usage, a separate counter, retains raw values in the report. These are
compiler process measurements, not Android runtime RAM.

BBC file bytes are unchanged. Brainfry/BBC full-file geometric-mean ratios
are 0.327 on Android and 0.163 on Windows. Code-size and resource gates still
favor Brainfry. No runtime speed, best-mode or real-application result is
added. The external runner is archived locally at Git commit
`5049b07`; independently published reproduction remains pending.

## Native driver diagnosis

The separate 30,566,077-byte Windows driver source has 508 functions. Its
largest graph body is 1,884,002 bytes, below the existing 2,097,152-byte graph
body budget. This rules out that particular simple size explanation for the
recorded self-store decline; it does not identify or repair the decline.
Diagnostic parity, self-store and large-edit verification, BBC DLL packaging
and common-loader migration remain open. Cache reuse does not implement the
missing native Windows helper host path or remove repeated checked-access
type hashing.

Follow the [measurement plan](06_PERFORMANCE_PLAN.md). M4 remains incomplete
and M8 remains **NOT YET ACHIEVED**.
