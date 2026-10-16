# Iteration 61 — Android ART/JNI callable acceptance gate

## Scope

Iteration 60 could probe Brainfuck-generated AArch64 shared libraries using a native Android `dlopen` client, but did not have a Java-to-JNI-to-policy device acceptance test. Iteration 61 adds that missing **test path**. It does not change the Brainfuck compiler, native machine-code emitter, the `bfc_call_v1` ABI, or the nine BF-generated DSO fixtures.

The device-side Java `Bfp1AndroidDeviceTest` uses `Bfp1Bridge.run`, which invokes the NDK-compiled host JNI transport `bfp1_jni_bridge.c`; the bridge uses `dlopen` and `dlsym` to call the BF-produced `bfc_call_v1`. C and Java are *host test/transport code*, not a new Brainfuck compiler or interpreter. The Java library loader accepts a **test-only absolute bridge path** through the property `brainfuckcc.bridge.absolutePath`; ordinary app usage retains `System.loadLibrary("brainfuckcc_bridge")`.

## Tested locally

From the repository root:

```sh
python3 -m tests.verify_android_jni61_host
python3 -m tests.verify_android_jni61_transport
python3 -m tests.verify_android_loader_probe60
python3 -m tests.verify_android_dynamic_callable59
python3 -m tests.verify_android_dynamic_callable58
python3 -m tests.verify_iteration60_native_stage_parity
python3 tools/check_docs.py
```

The first test compiles the actual JNI bridge for Linux and runs the **same Java assertions** through a real Linux JVM using nine **C test-only x86 policies**. All nine fixture calls and invalid-parameter checks pass; replacing the nested policy with an incorrect stub causes the Java harness to reject it. This proves test-driver and JNI host transport logic, not BF-native AArch64 or Android execution. The second test uses **mock ADB**, not a device; it checks exact stdout acceptance, on-device hash guard logic, and failure on mismatched hashes and incomplete transcripts.

Iteration-60 fixture tests compare nine actual BF-produced AArch64 DSOs with an independent Brainfuck reference and an instruction simulator; iteration-59 and -58 simulations are regression checks. None of those pass/fail results are a substitute for the next device run.

## Android acceptance command

Provide a 64-bit Android device with authorized ADB, an Android NDK, Android SDK build-tools with `d8`, and a JDK `javac` executable:

```sh
export ANDROID_NDK_HOME=/path/to/android-ndk
export ANDROID_SDK_ROOT=/path/to/android-sdk
python3 -m tools.android_bfp1_bridge.device_acceptance61 --device --serial YOUR_ADB_SERIAL
```

`--api 28` selects the initial NDK/DEX API level. Set `--api` to another API level supported by the NDK and device if required. `--ndk`, `--sdk`, `--d8`, `--adb`, and `--serial` allow explicit tool paths. The adapter:

1. Rebuilds the nine **Brainfuck-generated** AArch64 `.so` files and checks simulator/reference behavior.
2. Runs the existing native C shell loader test on the actual device. It also verifies SHA-256 of each copied BF policy DSO.
3. Builds a separate ARM64 JNI bridge using NDK Clang; this is transport, not BF code generation.
4. Compiles the Java device assertions with `javac` and converts them to `classes.dex` using Android `d8`.
5. Transfers the bridge, ART test JAR, and BF-generated DSOs to `/data/local/tmp`, verifying their device SHA-256 values.
6. Runs Android `app_process` and checks all nine exact policy pass lines, host-negative checks and suite completion. An incorrect status, output byte, output-used count, or persistent tape state aborts the gate.
7. Writes `build/iteration61_android_jni/device_result61.json` **only if both native shell loader and ART/JNI tests pass**.

Run without `--device` to rebuild the BF fixtures and clearly report that Android has not been executed. That mode never creates an Android success record.

## Acceptance limits

**Not executed on Android during this iteration**: this environment has no Android device, NDK, ADB or Android SDK build-tools. The new device command remains unverified on its intended runtime. Android permission or linker-namespace restrictions may require adjustments. In particular, a working shell ART process under `app_process` is **not** evidence that the same library loads in an installed APK's class-loader namespace.

Nine synthetic fixtures are not the eleven pinned original Gmail/Twitter/Threads policies. Testing those real applications and achieving self-hosting of the **fully dynamic** compiler on Android remain separate requirements. Historical Android device/compiler evidence does not automatically validate the new callable shared-object path. Older bounded compiler routes remain fallbacks until actual new-path acceptance passes.

The numerical 100-million-command objective remains retired; the only active compiler objective is resource-scaled fully dynamic callable compilation. See [active roadmap](ANDROID_DYNAMIC_CALLABLE_ROADMAP.md), [new JNI host evidence](../evidence/iteration61_jni_host_acceptance.json), and [release gate manifest](../evidence/iteration61_release_gates.json).
