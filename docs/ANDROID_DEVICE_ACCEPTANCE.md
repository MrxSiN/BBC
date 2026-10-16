# Android shell loader acceptance for Iteration 37

This is the device gate that the expanded Brainfuck-only AArch64 compiler has not yet passed. The scripts here make that gate reproducible. They do **not** add compiler semantics and are not a substitute for running on Android.

## What is ready

Run the offline preflight from the repository root:

```sh
python3 tests/verify_android_device_acceptance.py
python3 tools/android_device_acceptance.py prepare build/android_device_acceptance_37
```

The bundle contains thirteen BF-generated AArch64 PIE ELF files, exact stdin bytes, a shell runner, and a manifest of expected SHA-256 hashes, stdout bytes, exit statuses, and ELF layout. These exercise nested loops, 255 levels of nesting, NUL/0xff I/O, zero on EOF, left and right tape traps, the five page-class transitions, and a 2,000-command transfer program. All native code and ELF layout come from the existing Brainfuck stages; the Python code is development/test transport.

The offline tests check segment flags, file and memory sizes, 16 KiB alignment, program header types, the startup tape address, zero padding, input/output preservation, rejection of corrupted layouts, and two simulated load biases (except for the expensive 65,536-cell scanning trap). The reference Brainfuck interpreter, simulator and ELF checker are **independent test tools**, not the production compiler.

## How to run on a real Android device

Use a spare device or emulator under your control; these are raw native executables, not sandboxed APKs. The command requires a shell-accessible Android AArch64 device, `adb`, a writable and executable `/data/local/tmp` context, and a working `/system/bin/linker64`. Android version/API and device model must be recorded rather than assumed.

```sh
adb devices -l
python3 tools/android_device_acceptance.py run-device \
  build/android_device_acceptance_37 \
  evidence/iteration37_android_device_results --serial YOUR_ADB_SERIAL
```

The tool first checks the original local ELF files against the manifest, pushes the fixture bundle into `/data/local/tmp/bfc_iteration37`, then pulls back the executable and stdin files to verify their hashes before invoking the device shell script. Each program writes separate binary stdout and stderr files and a decimal exit-status file. Those results are pulled back, compared byte-for-byte against the independent reference, and recorded with `ro.product.cpu.abi`, `ro.build.version.sdk`, and `ro.build.fingerprint` in `device_verification.json`.

`--serial` is optional if exactly one device is connected. The tool never installs an APK, does not claim Play Store compliance, and does not auto-delete files on the device. If Android blocks shell execution, that is a target failure to investigate, not a passing test. Android-specific execution evidence counts only after the real-device command successfully runs and all fixture comparisons pass.

The `audit` subcommand can compare a folder of returned files, but cannot attest that the files came from Android. It labels them **UNATTESTED_RESULT_FILES**. Synthetic data must never be treated as actual device proof.

## Current outcome — USB follow-up on 2026-10-13

**PASSED: 13/13 on Pixel 8 Pro, Android 17/API 37**, over USB ADB. Uploaded ELF/stdin files were pulled back and hash-verified; actual binary stdout, stderr and exit statuses match the manifest. The device has 4 KiB runtime pages. See [raw results](../evidence/android_device_20261013/device_verification.json) and [device/performance follow-up](ANDROID_DEVICE_FOLLOWUP_20261013.md). Android-native compiler/S2 and 16 KiB-page devices remain unverified. The following paragraph records the original offline environment.

## Original Iteration 37 outcome

**NOT RUN ON ANDROID in Iteration 37.** This build environment lacks `adb`, an Android device, and an AArch64 system emulator. The 13 fixture binaries were generated, checked structurally, and 24 selected AArch64 simulator runs passed. The main compiler remains Linux S2 only. Android-native compiler execution, native self-hosting and 300,000-command artifact generation are still outstanding. A passing device shell suite would prove only the generated program path; it would not prove the compiler is running or self-hosting on Android.

Continue with a real device acceptance run, then native compiler execution, then a complete Android-native Stage 1–2 self-compilation. Do not begin the Windows backend on the strength of this offline bundle alone.
