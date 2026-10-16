# Iteration 54 — Linux reproducibility for the Android-native Gmail policies

## Classification

**Executed Linux BF-stage replay; archived Android outputs verified.** This
iteration introduces no new Android device execution, no new app build, and no
performance win. It expands independent reproducibility of the successful
2026-10-14 Android device checkpoint.

The uploaded archive records nine Android AArch64 dynamic ELF loader passes,
Android-native bounded S2, and a test installation of a native-policy Gmail
APK with 21 instrumentation test executions and 634,229 Java-policy parity
comparisons. `tools/audit_android_20261014.py` rechecks preserved original
artifacts, source hashes, log extracts, executable images and signed APK
checksums. These are archived device results, not device execution on Linux.

## New independent compiler reproduction

`bootstrap/run_policy_native.py` now supports `backend='linux-seed'` (the Linux
`auto` choice) and `backend='linux-native'`. It previously hardcoded a Windows
seed executable for non-Android execution.

The Linux seed mode builds `bootstrap/policy_seed_runs.c` with a normal C host
compiler. That utility **interprets** the original BF-stage instruction streams.
It groups repeated BF commands and recognizes linear loops as runtime
shortcuts; it does **not** generate AArch64 output, parse policy IR, or select
native operations. Those decisions are still made by the unchanged
`experiments/policy_*.bf` programs. The canonical Linux BF compiler and
Android BF compiler are unchanged.

The optimized seed was compared with the original independent
`bootstrap/seed_interpreter.c` on **152 BF programs** with byte-for-byte
stdout and identical exit statuses, including nested and transfer loops,
EOF, wrapping bytes, pointer traps and malformed brackets. It is a
bootstrap/test tool only, not an acceptable substitute for an Android-native
BF stage or a general 100M compiler.

On Linux, `tests/verify_linux_gm_replay.py` reprocesses the **original**
`evidence/gm_native_20261014_v4/GM/brainfuck/src/row.bf` and `scope.bf`
without replacing or transforming their instruction streams in the host:

| Source | BF instructions | AArch64 image | Expected SHA-256 |
| --- | ---: | ---: | --- |
| `row.bf` | 18,748 | 13,064 bytes | `c66bb638c2da02ec21936f5168efdad11d2c60ac72e01ff9c6d7e665aa2b6ffb` |
| `scope.bf` | 18,192 | 13,168 bytes | `e6f468abf3b79a07abdb51081509935fc5dda053f69265bd9f71d2efa30c302c` |

Both images are **byte-identical** to those recorded by the Android-native
pipeline and embedded unchanged in the archived test APK.

Separately, `tests/verify_linux_policy_stages.py` executes three BF stages
compiled by the authoritative self-hosted Linux BF compiler—source scanner,
RLE and bracket resolver—and compares their outputs byte-for-byte with the
archived Android stage traces. The base-optimizer Linux-native output was
also checked manually, but the automated acceptance gate intentionally does
not depend on replaying that comparatively expensive stage.

## Verification commands

```sh
python tests/verify_policy_seed_runs.py
python tests/verify_linux_gm_replay.py --evidence-output evidence/iteration54_linux_gm_policy_replay.json
python tests/verify_linux_policy_stages.py
python tests/verify_policy_ir.py
python tests/verify_policy_transport.py
python tools/audit_android_20261014.py
python tools/sync_status.py
python tools/check_docs.py
```

The native Linux stage images are hash-pinned under `build/iteration54_linux/`.
Run `LinuxPolicyNative.compile_stage` to regenerate them from the BF source
using `build/compiler_x86_64_linux.elf` (the larger optimizer stage takes
considerably longer than the three fast acceptance stages). The replay tests
assert the compiled artifact hashes before using them.

## Still open

The final test APK did not exercise real Gmail/Xposed hooks, and native kernels
were slower than the existing optimized C baseline. The archived speed-mode
app medians were about **21.73 µs** (ordinary row), **47.08 µs** (derived ad)
and **6.71 µs** (scope), compared with **0.65, 0.24 and 0.08 µs** respectively
for the frozen Java decision path. These are device measurements from the
archive, not new measurements. No speed superiority claim is justified.

The direct-callable policy path remains bounded to 4,096 RLE records, 255
nesting levels and a 1 MiB transported raw source. TwitterHideAds and
ThreadsHideAds original policies, general shared-library ABI generation,
100-million-command native compilation, cross-device testing and
application-level production release remain open.
