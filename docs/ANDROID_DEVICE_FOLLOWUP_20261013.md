# Android USB device follow-up — 2026-10-13

The expanded BF-generated program path passed on a real Pixel 8 Pro. The performance target did not: the fastest C transfer baseline beat native BF in this session, and warmed Java beat the existing GM BF-to-C/JNI policies. Compiler source was unchanged.

## Device acceptance

ADB `37.0.1-15733141` from `D:\Android\platform-tools` connected over USB to serial `38021FDJG00610`. Device: Pixel 8 Pro, arm64-v8a, Android 17/API 37, fingerprint `google/husky/husky:17/CP3A.261005.005/16271449:user/release-keys`, 4,096-byte runtime pages.

All **13** existing Iteration 37 fixtures passed actual Android loader execution: empty program, binary NUL/0xff/0x7f I/O, EOF zero, nested loops, 255 nesting levels, the five ELF size transitions, the 2,000-command loop program, and both tape traps. Trap status was 2; successful programs returned 0 and exact reference stdout. Uploaded ELF/stdin files were pulled back and hash-verified before execution. Raw stdout, stderr, exit codes and [device verification](../evidence/android_device_20261013/device_verification.json) are preserved. The fixture manifest SHA-256 is `1365ffbac36b6ebcd40d3958e8ebdaf38aa4ec5b56d2047d06ee49bdb80b4bcf`.

This verifies generated programs on this device. Android-native compiler execution, native self-hosting, 300,000-command emission, other Android devices/ABIs, and a callable JNI backend remain open. The 16 KiB-aligned ELF files running on a 4 KiB-page device do not prove execution on a 16 KiB-page device.

## Rebuilt native benchmarks

[The new harness](../benchmarks/android_device_followup.py) preserves results separately from the earlier benchmarks. It uses the existing BF compiler stages through two independent Windows BF interpreter seeds; both produce identical optimized transfer executables. NDK Clang 19 and Rust build comparison programs and the independent timing harness only. Java is compiled into DEX with the installed JBR and D8.

All **2,072** byte/EOF output checks and **3** deliberate timing-harness rejection checks passed. The sampler validates exit status and exact output before accepting a timing. The timing run used **101 randomized rounds**, **1,010 samples**, CPU 8 (rated maximum 2,914,000 kHz), and a common on-device fork/exec/I/O timer, excluding ADB transport.

| Transfer implementation | Median fresh-process time |
|---|---:|
| BF optimized native PIE | 2.2204 ms |
| C dynamic, O3 | 14.2361 ms |
| C static, O3 | 3.8119 ms |
| C freestanding, O3/LTO | 2.1922 ms |
| C freestanding, Oz/LTO | 2.1930 ms |
| C direct echo, O3/LTO | **2.1646 ms** |
| Rust standard runtime, optimized | 14.4913 ms |
| Rust direct echo, optimized/LTO | 2.2061 ms |
| Java/DEX on ART, JIT enabled | 346.1894 ms |
| Java/DEX on ART, interpreted | 347.6556 ms |

The fastest-baseline/BF timing ratio was **0.9749**, paired bootstrap 95% interval **0.9603–0.9952**, with the fastest baseline reselected in each resample. BF took about **2.6% longer** than C direct echo. Status: **NOT_PROVEN_FASTEST**; general performance objective **NOT_ESTABLISHED**. The interval is exploratory and cannot remove uncontrolled thermal/frequency/background effects.

The Java rows include a fresh VM per sample. They establish startup-inclusive behavior, not warmed Java or method-level JIT superiority. DEX is ART input, not a separate runtime; no same-device HotSpot JVM was available. Strong C/Rust comparisons eliminate the apparent advantage over heavier runtime startup. Inference: loader/entry and runtime costs dominate this one-byte workload, so it cannot rank general computation throughput.

USB charging remained on; battery level was 23%, temperature approximately 41.0→40.8°C. Frequency was not locked. See [native report, exact flags and raw samples](../evidence/android_followup_20261013/native/report.json).

## Actual release APK

The existing GM app at `D:\Android\AndroidStudioProjects\GM` was rebuilt successfully with its benchmark release configuration and this repository's isolated application-ID init script. Gradle executed 9 tasks and reused 78 unchanged task outputs. The APK hashes match the previous build; this is a fresh device retest of the same implementation, not a code-change speedup.

Application ID: `io.github.mrxsin.gmailhideads.codexbench`; test ID: the same plus `.test`. The production module's package was not replaced. APK SHA-256: `49582963397ea949e0afa59a78dbcab303bee3f9e5e67f5d965703debf9d3e09`; test APK: `4e689f4f340a71f3d20223ac82d18959b292f1ba277bd90164e3faae54875047`.

The app/test APKs were installed over USB and executed through instrumentation. Three process runs followed profile reset plus forced `verify` compilation, then three followed forced `speed` compilation for both packages. Package diagnostics confirmed `status=speed`, `reason=cmdline`. Each case uses 20,000 warmup calls and 20,000 individually timed calls. **21 test executions passed**, including **634,229 parity comparisons** and the robustness/concurrency suite. The verify/warmup mode permits JIT but does not prove each method was JIT-compiled.

| Uncached policy | BF/JNI p50 after ART speed | Java p50 after ART speed | BF/Java time ratio |
|---|---:|---:|---:|
| Ordinary class | 2.93 µs | 0.57 µs | 5.14× |
| Derived ad row | 3.22 µs | 0.49 µs | 6.57× |
| Scope | 1.95 µs | 0.16 µs | 12.19× |

These are medians of three run-level p50 values, not pooled samples. The cached verdict median was 0.16 µs and executes no new BF policy. APK tests have fixed inputs/case order and no CPU-affinity/frequency lock. They include the timer and volatile sink. Current times are slower than the earlier archive despite identical APKs; uncontrolled device conditions prevent attributing that difference to a compiler regression.

This APK uses **GM's existing BF-to-C AOT output plus JNI**, not BrainfuckCC's BF-owned native backend. Both GM policy sources exceed the current 2,000-command Android emitter, and the emitter provides shell byte syscalls rather than the required callable policy ABI. Treat the APK as the available application baseline, not proof that BrainfuckCC builds APKs.

Code inspection shows that `GmailPolicy` encodes names and hierarchy facts into a request; `PolicyFrame` copies the encoded heap buffer into a reused direct buffer, invokes JNI and validates the response. JNI obtains direct buffer addresses/capacities, while `bf_run` clears the program tape and executes the generated policy with a budget. Inference: this extra request/runtime path explains why eliminating VM startup does not make the uncached policy faster. A component benchmark or profile is still needed to assign costs to each part. No implementation change was made on this inference alone. [APK report and logs](../evidence/android_followup_20261013/apk/report.json) contain every run, compilation response, artifact hash and package diagnostic.

## Reproduce

From this repository, with the phone connected and authorized:

```powershell
D:\Android\platform-tools\adb.exe devices -l
python tools/android_device_acceptance.py run-device build/android_device_acceptance_37 evidence/new_device_run --adb D:\Android\platform-tools\adb.exe --serial YOUR_SERIAL
python benchmarks/android_device_followup.py --serial YOUR_SERIAL --output evidence/new_native_run
$env:JAVA_HOME = 'C:\Program Files\Android\Android Studio\jbr'
Push-Location D:\Android\AndroidStudioProjects\GM
.\gradlew.bat -I D:\GitHub\BrainfuckCC\benchmarks\gm_benchmark.init.gradle -PbenchmarkRelease :app:assembleRelease :app:assembleReleaseAndroidTest --console=plain
Pop-Location
python benchmarks/android_apk_followup.py --serial YOUR_SERIAL --output evidence/new_apk_run
python tests/verify_android_followup_harness.py
python tools/sync_status.py
python -X utf8 tools/check_docs.py
```

On this host `python` was invoked using the bundled absolute executable `C:\Users\SiN\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`. The documentation checker needs `-X utf8` because its existing default text reads encounter Unicode in this Windows checkout. The new measurement harnesses require an empty output directory to preserve earlier evidence. The device acceptance runner can reuse the prepared bundle. APKs and `/data/local/tmp` witnesses remain available for inspection.

The canonical `compiler/core.bf` remains 15,559 bytes, SHA-256 `f73a9b7ddc9d6f1971435251edefd85e3bb81a0dda23e8b11630a2d7cf7407e9`. New harness checks cover malformed/incomplete APK logs and timing ratio direction/baseline selection. The stale status generator was corrected to derive Iteration 27–37 entries from their stored evidence, check source/artifact hashes, and include the new raw device results without promoting historical simulations. Status generation and checks of all **70 maintained Markdown files** passed. Linux cold bootstrap/full release gates were not rerun: WSL is unavailable and BF source was unchanged. Android-native S2 and Windows remain unimplemented.
