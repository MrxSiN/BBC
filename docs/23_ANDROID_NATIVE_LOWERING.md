# Android native lowering

## Implemented change

The [execution report](../evidence/native_android_lowering.json) records an
Android ARM64 coverage fix in the native XAX compiler. The former depth-512
prepared snapshot passed verification but declined during native compilation.
A canonical diagnostic probe locates the decline at live-interval construction,
trace stage 31. That pass reserved space for every possible block/value pair,
even when most pairs needed no interval.

One expected-root graph transaction replaces this pessimistic reservation with
three-word linked records allocated as needed inside the existing fixed arena.
The allocator checks the remaining capacity with subtraction before advancing
the head. All three allocation sites carry borrowed views through both branches
and immediately propagate exhaustion. Interval order, weights, links and counts
retain their meaning. The separate edge-table address calculation is unchanged.

The [canonical XAX implementation](https://github.com/MrxSiN/XAX/blob/b765a4c3f8c9b1fb3d915752406b78074049bfa9/compiler/integration/windows_helpers/DRIVER.md)
includes the driver, allocation helper and transaction. Its verified root is
`68ecf527e4c18c163d1fc2bdddc76335ca2f205eff4f57766cec944a67915f4c`.
The 11,870,208-byte Windows compiler PE has SHA-256
`fa50e6005717a521e30123ad8e9cc637aa3fe15f28a1935cf394f0d4f2ee1125`.
Full verification, Workspace.save, stale-edit rejection and the allocation-site
audit pass. The generic SDK and its builders were not modified.

BBC's twelve implementation instruction streams and XAX's BFX production tree
are unchanged. The two new regression sources, requests and expected O1 records
live in [tests/compile](../tests/compile/README.md). O0/O1 use the same BFX format;
the active source has different instruction sequences at those levels.

## Executed checks

Twenty-two prepared Android snapshots pass 44 fresh native builds. Each pair
has identical artifact and provenance bytes. All 20 previously successful
Android artifacts remain byte-identical. Forty-seven actual Pixel 8 Pro
executions agree with independent interpreter output/status expectations,
including three oversized-input rejections.

The zero-entry depth-512 case emits `01`. The active depth-512 case enters every
nested loop, executes its inner body three times and emits `03 02 01 00`.
These are native Windows-hosted cross-builds followed by Android execution;
an Android-hosted compiler is not implemented by this work.

The native allocation helper passes 388 boundary/random cases and six repeated
allocation/exhaustion calls. Four framed native frontend calls check both new
sources at O0/O1. All 160 semantic diagnostic controls preserve complete bytes.
Three Windows smoke artifacts and their outputs remain exact. The Windows
checks establish regression coverage, without extending its implementation.

A separate [Android hello smoke](../evidence/android_hello_smoke.json) adds two
native builds and one Pixel execution. Its 5,880-byte ELF remains identical
to the preceding artifact and emits the exact greeting bytes. This check is
separate from the 22-snapshot corpus above.

Historical evidence retains its original bytes, including the previous report's
Android failure. Private rejected attempts remain in the external archive. The
verifier rejected an initial failure branch lacking explicit borrowed-view flow.
A subsequent address-pattern query included an edge-table calculation; an
isolated code-size mismatch caught that intent error before publication. The
corrected edit audits exactly three range sites and preserves all prior
successful Android artifacts. Only the corrected source is published.

## Measurement boundaries

These are prepared-store build and target execution checks. Source compilation,
BFX import, binding and snapshot creation are outside the native build command.
The unchanged generic Python SDK bootstraps the compiler using existing local
ProofCache and SDK-produced code fragments. Its pinned bootstrap revision is
`1c211da`; authoring/full verification also uses SDK `2e1af7c`.
No producer-supplied verification facts are trusted.

Raw build wall times are diagnostic and unscored. The two repetitions of each
deep case run concurrently in separate processes with distinct output paths.
They establish reproducibility, without constituting a controlled performance
comparison. Deep analysis remains expensive and needs further profiling.

The fixed driver views still declare 3,550,558,208 bytes. Allocating interval
records as needed avoids an oversized logical reservation; it does not grow the
underlying arena or establish a peak-memory reduction. The earlier prepared
driver measurements of about 3.31 GiB private commit and 11.2–13.3 MiB resident
memory retain their original source and measurement scope.

| Metric | Old BBC | New BBC in this phase | Pinned Brainfry | Result |
|---|---|---|---|---|
| Complete source build | 1.46–1.58 s baseline | Not remeasured | 23–24 ms baseline | No new score |
| Runtime latency | No new matched run | Not measured | Not rerun | Unscored |
| Complete compiler RAM | Earlier baseline retained | Not remeasured | Not rerun | Unscored |
| Android hello executable | 5,880 bytes | 5,880 bytes, identical | 1,760 bytes baseline | BBC remains larger |
| Large application execution | Earlier generic SDK evidence | No new matched application run | Not rerun | Unscored |

The [baseline](20_MODERNIZATION.md), [preceding lowering report](22_NATIVE_LOWERING.md)
and [measurement plan](06_PERFORMANCE_PLAN.md) remain separate authorities for
their configurations. This phase adds coverage and has no competitor victory.

## Remaining work

The complete public Python-free source-to-native command remains INCOMPLETE.
Native self-store/distinct resource-callee verification, common helper loading,
shared libraries and the Windows borrowed-return ABI gate remain open. No new
native three-generation compiler self-build is claimed. Affine/scan/offset
optimization, O2/O3, broader application coverage and competitive evaluation
remain unfinished. M2/M4 are incomplete and M8 is not achieved.

Android remains the priority: profile and reduce alias/range and graph-analysis
cost on deep programs, finish the native source workflow and library/verifier
gaps, reduce fixed workspace commitment, then rerun matched full-build, runtime,
memory and size comparisons. Preserve first verification and exact failure
semantics throughout.

