# Modernization audit and fresh baseline

**Milestone 0: EXECUTED and MEASURED, 2026-10-21.** This is the baseline for the
new modernization assignment, not completion of the earlier performance milestone
M4 or the competitive milestone M8. [Raw evidence](../evidence/modernization_baseline.json)
freezes revisions, tools, samples, hashes and limitations before implementation.

## Architecture at the baseline

BBC revision `2d9fbd6c44b223905c6d486bcefe35d7433dd0cd` has one
[BFX format](02_BFX_CONTRACT.md). XAX revision
`42de0fc3ce31d4447f697e35a565cb4fdc489eda` shares one strict decoder between
its portable decoder closure and importer. No second format migration is needed.
The old requested guide name docs/17_BFX_V5_WIDE.md was retired; its maintained
replacement is [streaming compilation](17_STREAMING_COMPILATION.md).

| Stage | Authoritative implementation | Current host |
|---|---|---|
| Bounded bootstrap/source filtering | compiler/compiler.bf | Native BF decision or independent seed interpreter |
| Wide filtering/validation | compiler/stream_chunks.bf, XAX source.xax coordinator | Native BF and canonical XAX |
| Clear, arithmetic, movement optimization | compiler/optimize.bf, pack_arithmetic.bf, pack_moves.bf, stream_runs.bf | Native BF; separate private components |
| Record validation/import | XAX integration/bfx/bfx.xax and import_bfx.xax | Native on Windows and Android |
| Graph integrity, types, proofs, binding | Generic XAX SDK and native-driver prototype | Current complete builds still use Python |
| Native lowering/packaging | XAX generic SDK; standalone_windows.xax / standalone_arm64.xax hosts | Windows-hosted bootstrap tools |

The remaining public-interface duplication is source framing and manual pass
orchestration: small and streaming workflows are exposed separately. One native
entry point must hide those details. This does not require another BFX identifier.
Existing operations are fixed one-byte primitives, CLEAR and arithmetic/movement
powers. Affine transfers, scans and offset operations remain unimplemented.
Any extension must preserve one authoritative format and strict validation.

## Frozen measurements

The corpus is the existing pinned hello, nested_math and checksum_four subset.
Brainfry is pinned to `e55d45735a6feb450a7e47852f4340f5b532fef8` with its
native AOT default optimization and explicit target. The Windows reference host
is Ryzen 7 5800H, Windows 11, Python 3.13.5. Each arm/source/target has twelve
fresh-process samples across three run clusters; 36 warmups are excluded.
**180 builds** were executed. Windows artifacts are checked on every sample;
all six distinct Android artifacts execute on Pixel 8 Pro/API 37 with exact output.

| Source | Target | BBC median ms | Brainfry median ms | Peak resident MiB BBC / Brainfry | Artifact bytes BBC / Brainfry |
|---|---|---:|---:|---:|---:|
| hello | windows | 1578.88 | 24.02 | 63.07 / 5.21 | 25600 / 3584 |
| hello | android | 1558.06 | 23.62 | 63.07 / 5.20 | 5880 / 1760 |
| nested_math | windows | 1507.37 | 23.43 | 63.18 / 5.21 | 17408 / 3072 |
| nested_math | android | 1468.73 | 23.62 | 63.03 / 5.21 | 3540 / 1200 |
| checksum_four | windows | 1500.27 | 23.84 | 62.84 / 5.21 | 17408 / 3072 |
| checksum_four | android | 1462.52 | 23.51 | 62.96 / 5.20 | 3496 / 1216 |

Complete timing surrounds process launch, output collection and exit. The BBC
arm uses native streaming BF source/packing/import, followed by generic SDK
verification, binding, lowering and packaging. It includes snapshot/hash/report
instrumentation and warm OS file caches; no overhead is subtracted. The resident
and peak commit values are distinct Windows kernel counters for a single process,
not a process-tree estimate. Raw peak commit and all samples are in the report.
These diagnostic subset results do not establish general superiority, statistical
victory, a new implementation speedup, or an under-25-ms native compiler.

## Bottlenecks and next dependencies

For Windows hello, median startup/SDK import is about 815 ms, first verification
133 ms, binding with its internal checks 233 ms, repeated verification 72 ms and
lowering 180 ms. Native BF filtering, packing and import together take about
1.6 ms. Stage medians are separate summaries and need not sum to total median.
Android lowering/packaging is reported together because the existing API combines
those operations. Cold helper setup is included in startup/store-read buckets;
no separate helper-only measurement is claimed.

Prioritize native host startup and the verified build path over frontend tuning.
Then remove redundant graph work through existing proof identities, preserving
mandatory first checks. Semantic optimizations follow those dependencies, with
explicit bounds/error proofs. The native driver freshly accepts current BBC
hello's bound store, source coordinator and importer. It still declines its
self-store and the two-distinct-resource-callee fixture; shared-library packaging
and the full native BBC workflow remain open. Decline is not a validity result.

Awib, sustained runtime, process-runtime, broader RAM/application coverage and
best compatible mode comparisons remain to be measured in later phases. The
[performance plan](06_PERFORMANCE_PLAN.md) retains the full competitive gates.
All 45 earlier BBC evidence reports retain exact bytes; this report is additional.
