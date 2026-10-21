# XAX ARM64 alias indexing and build latency

**IMPLEMENTED, EXECUTED and MEASURED, 2026-10-21.**
[Raw evidence](../evidence/xax_alias_index.json) records a canonical XAX backend
optimization. BBC's twelve Brainfuck implementation streams, canonical BFX,
optimization levels and compilation fixtures are unchanged.

XAX changes are confined to compiler/integration/windows_helpers/driver.xax,
android_alias_index.xax, android_alias_index.edit, the private regression/android_alias
fixtures, DRIVER.md and the new evidence/attribute entries. BBC changes are
documentation, AGENT.md and evidence/xax_alias_index.json. No SDK or builder
implementation is changed. The compiled driver is installed in ignored build/.
The [canonical XAX implementation](https://github.com/MrxSiN/XAX/blob/c97a11d0d1762c863ae9fc17ca311954d195aaba/compiler/integration/windows_helpers/DRIVER.md)
is pinned to the tested source commit.

## Change and correctness

A fresh development profile spent about 112.4 of 112.7 seconds in ARM64
alias/range analysis on a depth-512 prepared snapshot. The parameter-alias
fixed point scanned every CFG edge argument for each parameter. XAX now builds
one incoming-edge index per function and visits only the relevant block's
incoming edges, reading the parameter's argument directly.

The transaction preserves range analysis, node/view aliases, first-appearance
parameter order, source-block/edge order, canonical representatives, self
exclusion, stamped distinctness, immediate alias updates and fixed-point rounds.
Eighty-one original blocks remain exact; one entry edge redirects through two
new dispatch blocks. Scratch needs 2 times (blocks plus edges) words. Capacity is
checked with subtraction before the arena head advances, and the head is restored
on success. If scratch cannot fit, the unchanged canonical scan runs from the
original state. Mandatory first verification and all trust rules remain intact.

The source root is `ec66899fddc117eb0496bbd504e06742daf9931d0b8e64e9efde0725dae45ebd`.
The compiler PE is 11,876,864 bytes, SHA-256
`aa72234d6dd8a111efde62b47ced8449a482c4c5506d876714ff7fbe0968ab79`. An expected-root transaction, full verification,
Workspace.save and stale replay rejection pass. Implementation lives in XAX;
the unchanged generic SDK bootstraps it using existing process-local proof and
immutable function-fragment APIs. Bootstrap time is excluded from the score.
The compiler PE grows by 6,656 bytes; generated program artifacts remain exact.

## Executed checks

- 1,091 native index-helper checks and 1,091 native production-dispatch checks
  agree with an independent whole-CFG reference. They include cycles, duplicate
  arguments, self edges, zero-width values, initial aliases, capacity failures,
  repeated state reuse and a 200-block reverse dependency chain.
- 22 Android snapshots pass 44 sequential native builds and 47 Pixel 8 Pro
  executions. Every prior artifact remains byte-identical; each repeated build
  also preserves provenance. A separate hello case adds two builds and one
  actual device execution, retaining the 5,880-byte ELF.
- 160 semantic controls retain full diagnostic bytes; three Windows smoke
  artifacts and outputs remain exact. Generic SDK and builder source are unchanged.

## Fresh-process prepared-build measurement

| Android snapshot | Previous median ms | Indexed median ms | Reduction | Scored samples per arm |
|---|---:|---:|---:|---:|
| hello-android | 32.15 | 26.76 | 16.8% | 9 |
| nested_math-android | 28.90 | 23.35 | 19.2% | 9 |
| checksum_four-android | 29.06 | 23.13 | 20.4% | 9 |
| deep-512-O1-android | 111340.40 | 327.08 | 99.7% | 3 |
| deep-active-512-O1-android | 146465.45 | 687.91 | 99.5% | 3 |

There are 76 builds: 66 scored and 10 excluded warmups. Three run clusters use
counterbalanced sequential old/new pairs on Ryzen 7 5800H, Windows 11, Balanced
power plan. Timing includes process launch, store decoding, mandatory verification,
native lowering, ELF packaging, artifact/provenance writes and exit. Every output
hash matches the frozen artifact. Raw observations and ranges remain in the report.
Deep cases have only three scored samples per arm; this is exploratory evidence.
The separate 50-ms stage sampler adds observation overhead and is unscored.

Source frontend, BFX import, binding and snapshot construction are excluded in
both arms. This does not replace the frozen 1.46–1.58-second full-source BBC versus
23–24-ms Brainfry baseline. No full-source, competitor, runtime, peak-RAM or
output-size win follows. Fixed driver views still declare 3,550,558,208 bytes.

| Broader metric | Previous BBC | Indexed BBC | Brainfry | Result |
|---|---|---|---|---|
| Full-source build | Frozen 1.46–1.58 s | Not remeasured | Frozen 23–24 ms | No new verdict |
| Runtime latency | Not remeasured | Not remeasured | Not remeasured | No new verdict |
| Compiler RAM | Prior prepared-stage 3.31 GiB private commit | Not remeasured | No matched sample here | No new verdict |
| Generated executable size | Frozen artifacts | Exact same bytes | Previous corpus differs | BBC A/B tie |
| Large-workload execution | Earlier scoped coverage | No new sustained-runtime sample | Not measured here | No new verdict |

Those older figures retain their original [baseline](20_MODERNIZATION.md) and
[prepared-stage RAM](22_NATIVE_LOWERING.md) boundaries. Depth-512 build latency
above is a compiler measurement, not large-workload runtime.

The next priorities are the complete native source workflow and its startup,
binding and verification boundary, followed by fixed workspace commitment and
remaining graph costs. Shared-library packaging, self-store/resource-callee
coverage and common loading remain incomplete. Android-hosted compiler execution
and the separate Windows ABI gap remain open. M4/M8 are not complete.
