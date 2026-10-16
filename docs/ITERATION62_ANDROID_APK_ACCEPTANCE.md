# Iteration 62 — Installed Android APK callable acceptance

The BF compiler still emits standard AArch64 ELF DSOs through Brainfuck-owned generation stages. This iteration adds an **installable Android debug APK** that packages nine byte-identical, BF-generated policies alongside the host-only NDK JNI bridge. This tests an installed application's native library namespace, not the `/data/local/tmp` shell or `app_process` namespace tested by prior harnesses.

## Code and output

The new test project is `tools/android_bfp1_bridge/apk62/`. The Android activity executes the existing nine-policy assertion suite against `getApplicationInfo().nativeLibraryDir`, with policy names `libbfc_<case>.so`. It calls `Bfp1Bridge.run` for every policy, which uses `dlopen`/`dlsym` to find the **Brainfuck-generated** `bfc_call_v1` export. The bridge handles JNI and byte transport only. It is not a compiler, interpreter or replacement optimizer.

The test project compiles only the host bridge with CMake/NDK. The nine policy DSOs come directly from the existing standard-BF generator and are copied unchanged into `app/src/main/jniLibs/arm64-v8a`. The APK uses legacy extraction so `nativeLibraryDir` contains real policy file paths. The activity is test-only, exported only to support explicit ADB triggering, and the debug package is debuggable for `run-as` result collection. It must **not** be shipped as a production application.

The source suite checks nested loops, byte input and EOF, output bytes and count, gas exhaustion, tape-boundary errors, output-full errors, zero-loop skip, persistent tape updates, missing DSO and invalid JNI arguments. A random invocation nonce binds the private result file to the current run. The host command removes the prior result file first and rejects incomplete, wrong-order, duplicate, failed or stale transcripts.

## Local verification

From the repository root:

```sh
python3 -m tools.android_bfp1_bridge.apk_acceptance62 --prepare
python3 -m tests.verify_android_apk62
python3 -m tests.verify_android_jni61_host
python3 -m tests.verify_android_dynamic_callable59
python3 -m tests.verify_android_loader_probe60
```

`--prepare` compiles and validates the BF DSOs with the independent reference versus AArch64 simulator before copying their unchanged bytes. It does **not** produce an APK or simulate Android's real loader. The APK62 unit test executes the shared Java assertions on Linux JVM using explicitly **C test-only policies**, and checks archive integrity plus mocked ADB error rejection. Fake-ADB successes are never saved as Android device evidence.

## Build and run on an ARM64 Android device

Requires an Android SDK with API 35 platform and build tools, compatible Gradle/JDK, Android NDK/CMake and authorized ADB access. Set `ANDROID_SDK_ROOT` and `ANDROID_NDK_HOME` and run:

```sh
python3 -m tools.android_bfp1_bridge.apk_acceptance62 --build
python3 -m tools.android_bfp1_bridge.apk_acceptance62 --device --serial YOUR_SERIAL
```

An already built APK can be provided using `--apk /absolute/path/to/app-debug.apk --device --serial YOUR_SERIAL`. An external unsigned, release or otherwise incompatible APK will fail install or acceptance. The tool does not bypass Android package signature requirements.

The adapter checks the APK ZIP contains all nine original BF-generated policy DSOs, byte-for-byte, rejects ambiguous duplicate entries and verifies the AArch64 bridge. It then installs the APK, reads the installed base APK back through ADB, requires a matching SHA-256, removes the prior report using `run-as`, launches the named activity with a fresh nonce, and verifies the exact private report. Only a successful **real device run** writes `build/iteration62_android_apk/device_result62.json` with the device, artifact hashes, and accepted transcript.

The device must permit `run-as` for a debuggable app and `adb pull` of its installed base APK. Any OEM restrictions cause a failed or blocked test, not a silent pass. The fixture app uses a debug certificate and target API 28 to test the initial declared runtime contract; it does not establish support for modern target-SDK policy constraints.

## Results and limitations

**Executed locally:** nine BF-generated policy preparations with simulator parity; Linux JVM/JNI against nine C test stubs using APK library naming; mutation rejection; APK byte-integrity and duplicate-ZIP guards; mocked ADB failures for stale, missing, incomplete and failed device reports; previously established DSO structural and simulator regressions.

**Not executed here:** Gradle Android APK build, Android APK installation, Bionic loading from an installed app namespace, ART/JNI call of BF-generated machine code on device, real app integration, three-policy end-to-end parity, the other eight absent original policies, or Android-native compiler self-hosting. Android SDK, NDK, Gradle, ADB and an authorized device are not available in this runtime.

The canonical compiler and AArch64 BF emission sources are unchanged. Fallback compilation paths remain until hardware integration, original-policy parity and native compiler self-hosting all pass. The old 100-million-command objective is retired. The active objective remains resource-scaled fully dynamic callable compilation.

Evidence: [iteration 62 release gates](../evidence/iteration62_release_gates.json), [iteration 61 shell ART guide](ITERATION61_ANDROID_JNI_ART_ACCEPTANCE.md), [active roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).
