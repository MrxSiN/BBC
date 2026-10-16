# Android Iteration 53 loader acceptance — prepared, NOT executed

Nine fresh AArch64 freestanding PIE executables are in [`build/android53_acceptance/`](../build/android53_acceptance/). Their SHA-256 hashes, expected binary stdout bytes and expected exit statuses are in [`manifest.json`](../build/android53_acceptance/manifest.json).

**Do not infer Android-native execution from the existing Linux AArch64 simulator results.** This environment has no attached Android device, `adb` or target system loader.

On an authorized Android arm64 test device, copy the contents of [the standalone acceptance ZIP](../build/android53_acceptance/manifest.json) to an executable path (for example, `/data/local/tmp/android53`), then run `sh run_android53.sh`. Review `device_model.txt`, `android_api.txt`, `selinux_mode.txt`, `results.txt`, every `.stderr` and every `.got`. A plain SD-card location is often `noexec`; a failure to start is a loader/permission observation, not a BF program result. Re-verify hashes after transfer.

The test runner covers empty programs, wrapping arithmetic, transfer loops, nested loops, `NUL`/`FF` I/O, EOF-to-zero, pointer underflow, 300-level nesting, and compilation past the old 2,719-command ceiling. It checks stdout bytes and exit statuses. Android linker/JNI `.so` compatibility is a separate gate.
