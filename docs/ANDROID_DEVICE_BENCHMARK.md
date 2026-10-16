# Android device execution and benchmark

**Historical evidence note (2026-10-13):** This describes an earlier device-startup comparison. Later BF-owned optimization [changes the small-demo numbers](ANDROID_NATIVE_OPTIMIZATION.md), but **does not** establish Android-native compiler self-hosting or fastest C/Rust superiority. For current implementation state see [STATE](STATE.md), and for the Android-first, Windows-next plan see [IMPLEMENTATION_ROADMAP](IMPLEMENTATION_ROADMAP.md).

The initial run below is historical. The [new BF-owned optimizer and stronger
C/Rust comparison](ANDROID_NATIVE_OPTIMIZATION.md) improve BF elapsed time
4.57x, with no statistically established win over the fastest baseline.

## Initial device run

The ten-command Brainfuck backend now has a real Android execution witness.
On 2026-10-12, its generated AArch64 ELF ran on a Pixel 8 Pro with Android 17,
API 37, a 4-KiB page size and the Bionic loader. This is a native shell program,
not an APK or a complete application build. Android-native compiler
self-hosting remains unimplemented.

## Reproduce on this Windows workstation

Connect exactly one authorized AArch64 Android device, then run:

```powershell
python benchmarks/compare_android.py --adb D:\Android\platform-tools\adb.exe
```

The driver finds the installed SDK/NDK under `%LOCALAPPDATA%\Android\Sdk`,
Android Studio's Java runtime, and `%USERPROFILE%\.cargo\bin\rustc.exe`.
`--sdk`, `--java-home` and `--rustc` override those locations. Rust needs its
`aarch64-linux-android` standard library installed. This machine had it already.

Build artifacts are in `build/android_benchmark/`, including `brainfuck`,
the C/Rust baselines, `classes.dex`, the timing helper and C disassembly.
Device files are in `/data/local/tmp/brainfuck-bench/`.
Raw samples, hashes, tool versions and battery observations are in
[the JSON report](../benchmarks/results/android_transfer.json).

## What actually ran

Clang compiled the two existing independent Brainfuck interpreters for Android.
Each interpreter executed the same six unmodified Brainfuck compiler stages
on the phone. The emitted loop image was byte-identical between both seeds
and the archived Linux-produced image. Python only transported bytes and
checked statuses/hashes; it did not encode AArch64 instructions.

The nine-command workload is `,[>+<-]>.`: read a byte, transfer its value by
decrement/increment loops, and write it. C, Rust and Java implement the same
algorithm and byte contract, including EOF-zero and wrapping cells.
External compilers build only the independent seeds, timer and baselines.
The authoritative `compiler/core.bf` and all experimental BF sources are
unchanged.

Passed checks:

- 48 device byte-result checks: eight inputs across six execution variants.
- Empty program and nested loop execute successfully.
- Left and right tape escapes both exit with status 2 on the phone.
- Unmatched brackets and eleven-command sources are rejected.
- The timing helper rejects invalid input, incorrect output and failed children.
- Structural ELF validation and independent reference/simulator agreement.

Linux release gates and native self-compilation were not rerun: this Windows
host has no installed WSL/Linux environment. Existing Linux S2 evidence is
retained, not claimed as newly executed.

## Measured result

All variants ran on CPU 8, the highest rated frequency core (2,914,000 kHz),
with 31 randomized-order samples each. A C helper measures elapsed time on
the device around fork/exec, byte I/O and shutdown, excluding ADB transport.
Eight untimed correctness runs precede measurements, but each timed sample
starts a fresh process/VM.

| Variant | Median elapsed | Peak process RSS |
|---|---:|---:|
| Brainfuck native ELF | 7.2820 ms | 1,836 KiB |
| C `-O3`, dynamic | 10.7166 ms | 3,772 KiB |
| C `-O3`, static | **2.2077 ms** | 1,212 KiB |
| Rust `-O` | 11.0479 ms | 4,076 KiB |
| Java DEX, ART JIT enabled | 184.6364 ms | 94,984 KiB |
| Java DEX, ART interpreted | 186.6475 ms | 94,328 KiB |

BF speed divided by the fastest baseline speed is **0.3032x**, or about
**3.30x slower than static C**. An exploratory bootstrap interval for that
median ratio is 0.2764–0.3358. The user's updated goal is to surpass the
fastest baseline; this measured workload does not meet it. Beating dynamically
linked or managed startup time does not establish faster computation.

The BF artifact is 4,192 bytes. Its first-seed compilation took about
2,735 ms including ADB transfers. Build times and sizes for every baseline
are recorded in JSON; compilation routes differ, so these are not compiler
throughput rankings.

## Diagnosis and remaining scope

The C disassembly contains no transfer loop: `-O3` reduces the result to the
input byte. BF still executes its loop, checked pointer movements and fixed
48-byte slots. Affine-loop folding and removal of unnecessary slot work are
the concrete optimizer gap. Preserve bounds and I/O error handling when
implementing them.

DEX is the bytecode format executed by ART. ART combines interpretation,
JIT and AOT; those are execution/compilation modes, not independent source
languages. This test enables JIT but does not establish that its short Java
method was compiled. See the [official ART guide](https://source.android.com/docs/core/runtime/jit-compiler).
No same-device HotSpot JVM is installed, so JVM performance is unmeasured.
Desktop JVM timing would use different hardware and is not a substitute.

The phone was charging at a reported battery temperature of 38.7 C.
Frequency, background load and thermal behavior were uncontrolled. These
are fresh-process measurements, not steady-state kernel throughput or
general application performance. Installed-app AOT, warmed JIT, APK launch,
host API integration and the full Gmail/Twitter/Threads/G29 applications
were not tested. The Android backend still accepts only ten BF commands.
