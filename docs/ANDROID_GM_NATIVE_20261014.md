# GM now runs direct BF native code on Android

The original GM policy sources compile into callable AArch64 code, the isolated
APK loads that code, and the original parity and robustness suites pass on a
Pixel 8 Pro. Android-native compiler self-hosting was repeated successfully.
**The faster-than-C/Rust/Java target is not achieved.**

## What ran

ADB from `D:\Android\platform-tools` connected to Pixel 8 Pro, Android 17/API 37,
arm64-v8a, with 4 KiB runtime pages. This session used the device's wireless ADB
transport. Every uploaded native benchmark image was SHA-256 checked on device.

| Gate | Executed result |
|---|---|
| Iteration 53 dynamic ELF loader bundle | 9/9 exact stdout/status matches, including 300-level nesting and the old capacity boundary |
| Android native self-compilation | Two independent Windows BF seeds agree; native Stages 0–3 are byte-identical |
| Self-hosted compiler corpus | 14 native programs and 7 compilation rejections pass |
| GM original sources | `row.bf`: 18,748 commands / 3,894 RLE records; `scope.bf`: 18,192 / 3,917 |
| Compiler implementation | Eight raw BF policy stages compiled by the Android-native BF compiler and executed on Android |
| GM release APK | Built offline, installed as `io.github.mrxsin.gmailhideads.nativebf` |
| GM instrumentation | 21 passing executions across ART verify/warmup and forced speed modes |
| GM policy parity | 634,229 comparisons against the frozen Java reference |
| Kernel differential checks | 8,192 randomized frames match original C stdout and status, plus three checked timed frames |

Both original BF files match the pinned Git blob IDs in
[the application source catalog](../status/ANDROID_APPLICATION_GATES.json).
The original `D:\Android\AndroidStudioProjects\GM` checkout was not edited.
The installed production module was not replaced. Actual Gmail/Xposed hooks
were not enabled or tested.

## Compilation and platform boundary

```text
ordinary GM BF source
  -> BF scanner -> BF run folding -> BF bracket validation
  -> BF static tape proof / clear folding -> BF affine loop folding
  -> BF single-iteration loop proof -> BF operand encoding
  -> BF AArch64 code emission -> BF callable ELF writer
  -> generic linker embeds unchanged machine bytes in libgmailbf.so
  -> new JNI buffer adapter -> existing GM Java framing and policy callers
```

The source scanner handles comments and escaped NUL/FF bytes. Python transports
opaque stage streams; it does not parse policies, choose instructions, encode
branches, or repair machine bytes. Development-only authoring helpers arrange
the saved `.bf` implementation. Independent Python instruction/IR oracles are
tests, not production compilation.

GM's old `bf_engine.c`, old JNI implementation and generated C policy functions
are **not linked into this APK**. A new small C JNI adapter validates program
IDs, direct buffers, input/output limits and then calls the BF-produced code.
NDK C/assembly compilation and linking provide Android's platform library and
copy the BF images with `.incbin`; they perform no BF-to-native translation.
The final APK library contains both complete BF-produced ELF byte sequences
unchanged. Java only encodes inputs and validates framed results.

The callable ABI uses wrapping byte cells, EOF zero, a fresh 32-cell GM tape,
bounded output and a per-request loop budget. The BF static proof establishes
a minimum of 31 reachable cells; the adapter supplies and zeros all 32.
The BF code uses caller-saved AArch64 registers and returns status/tick counts
plus response length. Runtime budget accounting follows remaining loops after
optimization, rather than counting eliminated BF loops. Remaining potentially
repeating loops retain budget checks. The three timed frames also match C's
tick counts: 58, 40 and 44. Random differential checks validate output/status,
not universal equality of tick counters.

This callable path is bounded to 4,096 RLE records, 255 bracket levels and
1 MiB of raw transported source. It compiles these two full GM policies despite
the separate core compiler's 16,128-command ceiling. It does not establish
100M native compilation, other products' protocols, or a general BF-owned
Android dynamic linker. The bounded core compiler remains self-hosted; each
extension module is compiled natively by that core. No combined unbounded
compiler self-compilation claim is made.

## Fixes and optimization

The previous callable operand emitter assumed a literal output accumulator
retained its initial value on every record-loop iteration. It actually retained
the previous record's final value, corrupting subsequent branch opcode bytes.
Resetting the accumulator's known-state assumption at record entry fixes the
root cause. The independent native-word oracle now checks 120 source cases and
both original policies, including emitted affine/conditional variants.

The first GM APK without affine folding passed scope tests but failed six row
and concurrency tests: ordinary row inputs exhausted the budget while executing
transfer loops that GM's C compiler already folds. The affine build passed the
full suite. Those failed inputs, logs and APK remain in the earlier evidence
directories; their timings are not accepted performance results.

The new `policy_oneshot.bf` pass scans each statically bounded loop for a
guaranteed direct clear of its source cell. Nested control flow invalidates the
fact until a later direct clear; any subsequent source write invalidates it.
When the fact holds at the matching closing bracket, the loop becomes one
conditional branch. The existing BF matcher recalculates every native span
after transformation. Pointer-drifting loops and loops without this proof keep
their original backedge and checks. `I`/`E` are private IR record kinds, never
new source-language operators.

| Policy image | Affine build | Conditional build | Reduction |
|---|---:|---:|---:|
| row | 15,864 bytes | 13,064 bytes | 17.6% |
| scope | 16,112 bytes | 13,168 bytes | 18.3% |

The size reduction did not materially improve GM elapsed time in these runs.
No performance gain is inferred merely from fewer emitted instructions.

## Measurements

GM app values are medians of three run-level p50 values after forced ART speed
compilation. Each case has 20,000 warmup and 20,000 timed calls. They include
request encoding, JNI, native code, response validation, timer and volatile sink.

| GM case | BF native app | Frozen Java policy |
|---|---:|---:|
| Ordinary row | 21.73 µs | 0.65 µs |
| Derived ad row | 47.08 µs | 0.24 µs |
| Scope | 6.71 µs | 0.08 µs |

Kernel-only measurements use 31 randomized rounds, CPU 8, 20,000 warmup and
20,000 timed calls per sample. They include tape initialization and output
checksum but exclude Java/JNI and process startup.

| Checked kernel frame | BF native | Original GM C, O3/LTO |
|---|---:|---:|
| Positive row | 15.496 µs | 0.489 µs |
| Negative row | 10.448 µs | 0.297 µs |
| Positive scope | 5.878 µs | 0.339 µs |

The remaining gap is already present inside the generated kernels. The C source
folds policy state tests into `if`/`switch`; the BF pipeline retains many scratch
cell operations and individual state tests. Constant propagation and predicate/
state dispatch folding are the next candidates. No instruction-level profile
has yet assigned the gap to a particular sequence, and these separate sessions
must not be subtracted to invent an exact JNI cost.

An initial hand-built kernel frame encoder incorrectly treated alphabet order
as ABI code order for `r`, `n` and `d`. The final kernel runner uses their actual
codes (11, 9, 10), asserts expected yes/no responses, and checks random frames
before timing. Earlier kernel reports are retained as diagnostic attempts and
excluded from the accepted summary. The APK suite always used GM's own correct
encoder. Likewise, the first self-hosting runner had a historical hardcoded date;
the final `_v2` self-hosting report records this run's actual October 14 date.

Separate small-program tests compare optimized freestanding C/Rust and ART:

| Test | BF | Strong comparison |
|---|---:|---:|
| Fresh one-byte process | 1.553 ms | Rust: 1.561 ms; C O3: 1.570 ms |
| Warm stream byte | 3.858 µs | Rust: 3.293 µs; C Oz: 3.386 µs |
| Warm ART stream byte | BF: 3.858 µs | Java JIT enabled: 13.738 µs; interpreted: 14.098 µs |

The fresh-process fastest-baseline/BF ratio is 1.0048, with paired bootstrap
95% interval 0.9752–1.0237: **NOT_PROVEN_FASTEST**. The warmed stream ratio is
0.8535, interval 0.5453–0.9896: BF is slower than the strongest native comparison
in this session. CPU frequency, temperature and background work were not locked.
ART warmup plus JIT enabled does not prove compilation of particular methods.
DEX is ART input, not another runtime. No same-device HotSpot JVM was available.
These stream inputs are separate from GM policy workloads.

## Artifacts and reproduction

- [Installed native APK](../evidence/gm_native_20261014_v4/app.apk)
- [Instrumentation APK](../evidence/gm_native_20261014_v4/test.apk)
- [Build provenance](../evidence/gm_native_20261014_v4/build.json)
- [App measurements and raw logs](../evidence/gm_native_device_20261014_v4/report.json)
- [Kernel measurements](../evidence/gm_native_kernel_20261014_v3/report.json)
- [C/Rust/ART stream measurements](../evidence/android_compact_benchmark_20261014/report.json)
- [Fresh native self-hosting](../evidence/android_native_selfhost_20261014_v2/report.json)
- [Dynamic ELF loader results](../evidence/android53_device_20261014/results.txt)
- [Audited combined results](../evidence/android_execution_20261014.json)

APK SHA-256: `83ee05db717b07eb7a6f35237823e7d52a92862ac2ab274ae5bb00f5450b97e8`.
The native core compiler remains 933,008 bytes, SHA-256
`11782dea43d79697b248f164a1313ef5219e94105023c4456e4aa7ed28f1827c`.

```powershell
python -X utf8 tools/verify_android_native_selfhost.py --serial YOUR_SERIAL --output evidence/new_selfhost
python -X utf8 tools/build_gm_native.py --serial YOUR_SERIAL --proof evidence/new_selfhost --output evidence/new_gm
python -X utf8 benchmarks/android_apk_followup.py --serial YOUR_SERIAL --native-build evidence/new_gm --output evidence/new_gm_device
python -X utf8 benchmarks/gm_native_kernel_compare.py --serial YOUR_SERIAL --native-build evidence/new_gm --output evidence/new_gm_kernels
python -X utf8 benchmarks/android_compact_compare.py --serial YOUR_SERIAL --output evidence/new_stream_comparison
python -X utf8 tests/verify_policy_ir.py
python -X utf8 tests/verify_policy_transport.py
python -X utf8 tools/audit_android_20261014.py
python -X utf8 tools/sync_status.py
python -X utf8 tools/check_docs.py
```

Builds use the installed JBR, NDK 28.2 and Gradle offline cache. NDK/Rust/JBR/D8
commands are recorded in the comparison/build reports. C is a disclosed kernel
comparison oracle only. The canonical Linux compiler remains **15,559 bytes**
with **zero** fixed emitted padding. Linux release gates requiring `cc` and Linux
ELF execution could not run on this Windows host. Windows, actual Gmail hooks,
other devices/ABIs, 16 KiB-page hardware and universal compiler tape safety remain
unverified. Twitter/Threads and 100M executable acceptance remain open.
