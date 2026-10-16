# Iteration 62 APK acceptance

`python3 -m tools.android_bfp1_bridge.apk_acceptance62 --prepare` stages the nine BF-generated AArch64 libraries. `--build` assembles the separate test-only Gradle APK if SDK/NDK/Gradle are installed. `--device --serial SERIAL` installs and exercises the APK, verifies a fresh nonce-bound private JNI test transcript and saves device evidence only after success. Host-only tests: `python3 -m tests.verify_android_apk62`. **No Android success is claimed from preparing or mocked ADB.** See [guide](../../docs/ITERATION62_ANDROID_APK_ACCEPTANCE.md).

---

# BFP1 shared library and Android JNI host bridge

This directory is a **host adapter**, not a Brainfuck compiler. The shipped policy ELF is built by standard-BF stages. Android NDK/Gradle builds only the JNI bridge and the surrounding app.

## Generate a policy shared object

From the repository root:

```sh
python3 -m bootstrap.build_android_dynamic_callable58
python3 -m bootstrap.android_dynamic_callable59 examples/nested.bf -o policy.so
readelf -Wl -Ws -d policy.so
```

The policy ELF is AArch64 ET_DYN. It has a 16 KiB aligned RX PT_LOAD, a PT_DYNAMIC, SysV hash/dynstr/dynsym, and one exported symbol `bfc_call_v1` at offset `0x400`. The symbol is a normal AArch64 function, not a `Java_*` JNI function. There are no imported symbols and no relocations. The callable code and ELF metadata are emitted by executed Brainfuck compiler stages; Python only handles raw transport, opaque patch storage and atomic output.

## ABI contract

The `bfc_call_v1` function expects eight AAPCS64 arguments:

| Register | Value |
|---|---|
| x0 | Input buffer pointer |
| x1 | Input length in bytes |
| x2 | Output buffer pointer |
| x3 | Output capacity in bytes |
| x4 | Mutable tape pointer |
| x5 | Tape length in cells, at least one |
| x6 | Loop-entry gas budget, nonnegative |
| x7 | Pointer to writable 64-bit output-used value |

Return `x0` is status 0 (success), 1 (budget exhausted), 2 (output capacity exhausted), or 3 (pointer out of bounds). `x1` holds a budget-used value as an internal extended convention; the ordinary C bridge **does not expose or promise to capture it**. All eight source commands follow the byte-cell/EOF-zero semantics of the compiler, but **the caller** owns tape initialization, isolation/persistence, and buffer validity. The `x7` address must remain valid until return. Calls may mutate tape or output before a nonzero status.

## Android JNI host integration

Build `bfp1_jni_bridge.c` with an Android NDK CMake build (see `CMakeLists.txt`) as `libbrainfuckcc_bridge.so`, and bundle a BF-generated policy `.so` as a separate target-architecture shared library. Include `org/brainfuckcc/Bfp1Bridge.java` in the Java/Kotlin source set. Call `Bfp1Bridge.run(libraryPath, input, output, tape, budget, outputUsed)` with an absolute library path visible to the app linker namespace. `outputUsed` must have at least one element; its first element receives the number of bytes written. Pass a freshly zeroed tape for isolated requests or reuse the same byte array for persistent policies. Input, output, and tape must be separate Java arrays.

The bridge calls `dlopen`, `dlsym("bfc_call_v1")`, invokes the already-generated native code through AAPCS64, and commits the output/tape buffers. It never parses Brainfuck. It reports negative transport errors separately: `-1` invalid arguments, `-2` library load error, `-3` missing export, `-4` JNI allocation error, and `-5` invalid native result. Android library namespaces, loading restrictions, app packaging and permissions are host-specific; not every absolute path is loadable. A 16 KiB-aligned ELF header by itself is not Android loader proof.

The bridge currently calls `dlopen` and `dlclose` per request; this favors a small auditable contract, not peak performance. Threads callbacks and recursive `CAP_CALL` are **not** implemented by this simple eight-argument ABI bridge. Those require compatible host-protocol integration, not new Brainfuck instructions.

## Verification boundary

```sh
python3 -m tests.verify_android_dynamic_callable59
python3 -m tests.verify_android_dynamic_callable59_policies
python3 -m tests.verify_android_dynamic_callable59_link
python3 -m tests.verify_android_dso59_jni_host
```

The last command executes **Linux x86-64 JVM JNI transport** against a deliberately trivial C test-only shared object. It validates JNI array and `dlopen` plumbing, not BF correctness or the Android dynamic linker. The cross-link test verifies exported symbol resolution with Clang/lld as development/test tools only. Actual ARM64 Android `dlopen`, JNI execution, original app parity, full 11-source acceptance, and Android-native self-hosting remain open. No Android NDK/device is present in this iteration's test environment.

## Iteration 60 Android loader verification

The device acceptance bundle is a **host-side test only**, not an alternate BF compiler. Prepare and locally validate nine BF-generated libraries with:

```sh
python3 -m tests.verify_android_loader_probe60
```

On a supported arm64 device, with Android NDK and ADB:

```sh
export ANDROID_NDK_HOME=/path/to/android-ndk
python3 -m tools.android_bfp1_bridge.device_acceptance60 --device --serial DEVICE_SERIAL
```

This builds `device_loader_probe60.c` with NDK, copies the nine BF-generated shared objects to `/data/local/tmp/bfc60_callable/`, verifies their device-side hashes and invokes `dlopen`, `dlsym` and policy call assertions for EOF, nested loops, tape state, gas and traps. It records `build/iteration60_android_loader/device_result.json` only after actual device success. It is a shell loader gate, **not** Android app namespace/JNI/APK parity. No such device execution took place during Iteration 60 development. See [the detailed report](../../docs/ITERATION60_ANDROID_LOADER_ACCEPTANCE.md).

The JNI bridge has also been hardened to pass valid sentinel pointers for zero-length arrays. Zero capacity/input preserves the native policy's size contracts; host Linux JVM tests cover both cases. These changes affect transport only, not the BF-generated code.
