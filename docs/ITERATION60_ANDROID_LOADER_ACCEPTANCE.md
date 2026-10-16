# Iteration 60 — Android callable loader acceptance bundle

## What changed

The compiler and its BF-generated AArch64 code are unchanged from Iteration 59. This iteration supplies **nine BF-compiled shared-library fixtures** and a small native host loader test, `tools/android_bfp1_bridge/device_loader_probe60.c`. It calls the actual `bfc_call_v1` export using `dlopen` and `dlsym`, checks the output length, exact output bytes, tape mutation, and result status. It intentionally does not parse Brainfuck or generate policy machine instructions. The Python adapter only compiles fixtures through the existing BF pipeline, verifies simulator/reference parity, transfers files, compares their hashes and collects the resulting device transcript.

The separate JNI host adapter now gives zero-length input/output arrays valid sentinel addresses without asking JNI to pin a zero-byte array. Real Linux JVM tests exercise both zero-length buffers, capacity failure, array-alias rejection, invalid tape and missing libraries. The BF code generation path and canonical Linux compiler source were not changed.

## Local verification

Run from the repository root:

```sh
python3 -m tests.verify_android_loader_probe60
python3 -m tests.verify_android_dso59_jni_host
python3 -m tests.verify_android_dynamic_callable59
```

`verify_android_loader_probe60` compiles nine BF sources into exported AArch64 `.so` files under `build/iteration60_android_loader/`, compares **nine** runs with the independent BF reference and the AArch64 instruction simulator, inspects all nine generated ELFs, and builds/executes the native probe on **Linux x86-64 using a test-only C shared library**. The local stub test exercises the host's `dlopen`/`dlsym`/error path but says nothing about whether Android loads the BF-produced code. Source files are empty program, EOF/zero input, transfer, nested loops, pointer trap, output overflow, loop gas, zero-loop skip and repeated tape mutation.

## Actual Android run — requires a device

A 64-bit Android device, Android NDK, ADB, and permission to execute a native test in `/data/local/tmp` are required. There is no device execution evidence from this iteration's development environment.

```sh
export ANDROID_NDK_HOME=/path/to/android-ndk
python3 -m tools.android_bfp1_bridge.device_acceptance60 --device --adb adb --serial DEVICE_SERIAL
```

Use `--api 28` (default) or an API level supported by the device and NDK. The script uses the NDK's `aarch64-linux-android<api>-clang` **only to build the test harness**, not the compiled BF policies. It checks `arm64-v8a`, the SDK, and SHA-256 hashes of the policy files copied to the device, then executes the nine cases under the Android loader. Exit failures or unexpected output fail the gate. On success it writes `build/iteration60_android_loader/device_result.json` with device facts, fixture SHA-256 hashes, and the loader transcripts. A separately recorded on-device Android run is mandatory before upgrading any Android execution status.

The program runs as an Android **shell** executable. That is not an APK, app linker namespace, JNI execution of the BF `.so`, or Android-native compiler self-hosting. A `dlopen` result in one namespace does not prove that Android's app namespaces permit the same file path; the JNI/APK acceptance gate remains separate.

## Checks and remaining gaps

- Local: nine BF-generated dynamic DSOs, nine independent-vs-simulator comparisons, nine `readelf` inspections, real host loader with test-only x86 native stub, Linux JVM/JNI buffer tests.
- Unverified: device loader acceptance, actual AArch64 execution, Android JNI call into the BF DSO, original APK parity, eight absent original policy sources, and Android-native self-hosting of the dynamic compiler.
- No fallback has been removed. Retired numerical throughput goals have not been restored. Resource-scoped compilation remains the only active direction.

Fresh native Linux S1/S2 replay produced **two byte-identical self-compiled compilers** matching the installed binary. The longer end-to-end cold-bootstrap test timed out after matching the independent seed, Stage 0 and Stage 1. It is not counted as a completed new cold-bootstrap gate; see [the native replay record](../evidence/iteration60_native_selfcompile.json).

Evidence: [local acceptance](../evidence/iteration60_loader_readiness.json), [prior DSO regression](../evidence/iteration59_dynamic_callable_dso.json), [active roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md).
