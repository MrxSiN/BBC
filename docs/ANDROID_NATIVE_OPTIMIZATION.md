# Android native optimization and GM baseline

**Planning note (2026-10-13):** This document is archived **executed evidence for small Android programs**; it does not show a native compiler on Android, full self-hosting, arbitrary BF source size or all Android ABIs. The Android-first [implementation roadmap](IMPLEMENTATION_ROADMAP.md) plans 14 Android iterations followed by 6 Windows and 2 shared release gates. All recorded device measurements remain historical and unchanged.

Two additional standard Brainfuck stages now fold clear/adjacent transfer loops,
remove Bionic startup, prove bounded stack tape use, and skip unused slots.
The production Linux compiler is unchanged. All optimization and machine-code
patching happens in raw BF; Python transports and verifies bytes.

The nine-command transfer `,[>+<-]>.` drops from 11,287 to 31 executed native
instructions for input `FF`, a **364.10x instruction reduction**. Its same-run
median elapsed time improves **4.57x**.
These are different metrics: syscall/process startup dominates elapsed time.

## Measured result on Pixel 8 Pro

Android 17/API 37, 4-KiB pages, CPU 8; 101 randomized interleaved rounds per
variant. The device-local timer includes fork/exec, I/O and exit, excludes ADB.

| Variant | Median elapsed | Peak process RSS |
|---|---:|---:|
| brainfuck_original | 10.7497 ms | 1836 KiB |
| brainfuck_optimized | 2.3514 ms | 1212 KiB |
| c_dynamic | 14.3839 ms | 3808 KiB |
| c_static | 3.8713 ms | 1212 KiB |
| rust_std | 14.9520 ms | 4100 KiB |
| c_freestanding_o3 | 2.3698 ms | 1212 KiB |
| c_freestanding_oz | 2.3770 ms | 1212 KiB |
| c_direct_echo | 2.3532 ms | 1212 KiB |
| rust_freestanding | 2.3574 ms | 1212 KiB |
| rust_direct_echo | 2.3828 ms | 1212 KiB |

BF has the lowest observed median, only **0.076%** ahead of direct-echo C.
The BF speed ratio is **1.000762x**; paired bootstrap 95% interval
**0.972286–1.013517x**.
The interval includes a tie and a loss. **NOT_PROVEN_FASTEST** remains the
acceptance status. The earlier exploratory run gave 0.9953x against its fastest
baseline and also included a tie; it did not meet the goal either.

The C references include `-O3` and `-Oz`, LTO, no CRT/libc, one load segment,
and the direct observable echo algorithm. Rust includes no-std LTO and a
corresponding direct-echo variant. All preserve byte/EOF and error-status
contracts. Neither an interpreter nor managed-runtime startup is the fastest
baseline. No frequency lock or background-load control was available.

[Raw report](../benchmarks/results/android_optimized.json) includes all 1,010
samples, hashes, flags, versions, compilation times and battery observations.
The incomplete first run was exploratory and is not substituted for this
report. Every completed schedule block is also saved before later tests run.

## What was verified

- 444 reference/simulator comparisons across two load bases, including the
  entire final 65,536-byte tape, output and exit status.
- 37 byte-identical image comparisons between independent BF interpreters.
- 24 artificial boundary cases plus read/write error paths.
- 1,032 native Android runs of transfer, empty/nested and both bounds traps.
- 1,542 optimized BF/C/Rust native byte and EOF comparisons before timing.
- Both interpreters execute `core.bf` to build both optimizer stages to
  identical Linux ELF bytes. Linux ELF execution/self-hosting was not rerun.
- 514 Windows seed byte/EOF checks, comment-invariant adapter output and two
  failed inputs that cannot overwrite a previously accepted artifact.

[Optimizer evidence](../evidence/android_native_optimization.json),
[affine-stage notes](../experiments/android_native_optimize.bf.notes.md), and
[resource-stage notes](../experiments/android_resource_optimize.bf.notes.md)
record hashes, protocols and the exact bounds-check elimination condition.

## Reproduce on Windows

Visual Studio Build Tools with C support, the installed Android NDK, Rust's
Android target, Python and exactly one authorized wireless/USB device are
required. The existing six-stage BF source/binary provenance must match its
archived evidence. These commands also work with the authorized wireless ADB
endpoint; disconnects are retried using its advertised mDNS endpoint.

```powershell
cmd /c bootstrap\build_windows_seeds.cmd
python tests/verify_windows_seed_io.py
python tests/verify_android_native_optimization.py
python tests/verify_android_optimized_adapter.py
python bootstrap/run_android_optimized.py examples/android_loop_demo.bf build/android_optimization/program.elf
python benchmarks/compare_android_optimized.py --gm D:\Android\AndroidStudioProjects\GM
```

Windows uses local independent BF interpreters for compilation. Only native
execution and timing require the phone. The generated Linux optimizer ELFs
can be executed by the adapter on Linux, but that route is unexecuted here.
Android artifacts remain native shell programs, not APKs or Android-native
compiler self-hosting. The executable is still 4,192 bytes with ten source
command slots. EINTR is not retried by these Android I/O slots.

## GM policy baseline

The supplied GM project was used without changing its policy sources. Its
committed BF-derived C policies were compiled with NDK `-O3 -flto` and measured
through the existing bounded request ABI: 20,000 warmup calls, 20,000 timed
calls per sample, eleven samples. Responses and checksums were validated.

| GM case | Median time per warmed native call |
|---|---:|
| scope | 327.9 ns |
| ad_row | 451.5 ns |
| ordinary_row | 325.6 ns |

This measures the existing C AOT policy core, including its runtime request
contract and checksum loop. It is a separate baseline, not a comparison
against this compiler's BF-native policies or full JNI/app latency.
GM's row policy has 18,748 BF commands and scope has 18,192: both exceed the
production 16,128-command ceiling and this Android prototype's ten-command
ceiling. GM also needs its bounded request/tick ABI rather than byte syscalls.
Scalable BF source storage and code relocation, general loop analysis, and a
compatible callable policy ABI remain necessary before full GM parity.
Warmed Java/ART, JVM and full application superiority are not established.


## GM release APK and warmed ART

The existing GM release application and instrumented test APK were built with
Gradle/NDK, installed and run through wireless ADB. A Gradle init script gives
the benchmark a separate `io.github.mrxsin.gmailhideads.codexbench` package ID;
the user's installed module and GM policy sources were not changed. This
build uses GM's BF-to-C AOT compiler output, not this native BF backend.
The existing parity and robustness suite passed **16 tests**, including
**634,229 old-Java-versus-BF comparisons**.

Both benchmark packages then received `cmd package compile -m speed -f`.
The existing test warms each case for 20,000 calls and measures another 20,000.

| Uncached policy | BF/JNI p50 | Legacy Java p50 after ART speed compilation |
|---|---:|---:|
| Ordinary class | 1.75 us | 0.73 us |
| Derived ad row | 1.51 us | 0.24 us |
| Scope | 0.85 us | 0.08 us |

Cached verdict lookup measures 0.08 us, but performs no new BF policy call.
These fixed-input, sequential microbenchmarks include frame encoding, JNI,
response parsing, timer and volatile sink work. They are one run per ART mode,
with no APK CPU-affinity/frequency lock, and are not full Gmail/Xposed latency.
The initial mode does not prove each warmed method was JIT compiled.
[APK report and provenance](../benchmarks/results/gm_apk_baseline.json) retain
initial and forced-speed observations, test results and artifact/log hashes.
There is still no same-device HotSpot JVM result.

To rebuild the isolated baseline on this workstation:

```powershell
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
cd D:\Android\AndroidStudioProjects\GM
.\gradlew.bat -I D:\GitHub\BrainfuckCC\benchmarks\gm_benchmark.init.gradle -PbenchmarkRelease :app:assembleRelease :app:assembleReleaseAndroidTest
D:\Android\platform-tools\adb.exe install -r app\build\outputs\apk\release\GmailHideAds-v2.1.0.apk
D:\Android\platform-tools\adb.exe install -r app\build\outputs\apk\androidTest\release\app-release-androidTest.apk
D:\Android\platform-tools\adb.exe shell cmd package compile -m speed -f io.github.mrxsin.gmailhideads.codexbench
D:\Android\platform-tools\adb.exe shell cmd package compile -m speed -f io.github.mrxsin.gmailhideads.codexbench.test
D:\Android\platform-tools\adb.exe shell am instrument -w -r -e class my.MrxSiN.gmailhideads.policy.PolicyBenchmarkTest,my.MrxSiN.gmailhideads.policy.PolicyParityTest,my.MrxSiN.gmailhideads.policy.PolicyRobustnessTest io.github.mrxsin.gmailhideads.codexbench.test/androidx.test.runner.AndroidJUnitRunner
D:\Android\platform-tools\adb.exe logcat -d -s System.out:I
```

The benchmark APKs remain installed for inspection. No actual Gmail hook was
enabled or tested. The next optimization needs to retain BF-owned decisions
while reducing request construction, JNI and callable policy work. Faster
fresh-process startup cannot establish this application's performance target.
