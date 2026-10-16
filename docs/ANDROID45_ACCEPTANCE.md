# Iteration 45 Android class eight loader acceptance

The seven checked AArch64 executable images in [`../build/android45_acceptance`](../build/android45_acceptance/manifest.json) are built by Linux-native Brainfuck stages, not a C/C++ compiler or assembler. They cover the old/new ELF boundary, nested loops, binary input/output including NUL and FF, EOF, and a deterministic pointer trap. Their expected stdout bytes and exit codes are recorded in the manifest, together with SHA-256 hashes for every generated executable and input stream.

**No Android-device execution is claimed for these seven images.** They were prepared and checked offline. Execute only on a supported arm64 Android shell environment with `adb` and a working `/system/bin/linker64`:

```sh
python3 tools/android_device_acceptance.py run-device build/android45_acceptance evidence/android45_device_results --serial DEVICE_SERIAL
```

The existing transport verifier checks local ELF hashes, pushes files, pulls them back to compare SHA-256, executes the shell runner and pulls output/status files for exact comparison. Do not mark these fixtures EXECUTED until the actual device properties, raw results, and generated `device_verification.json` exist and pass audit. Some Android releases or installation contexts may reject native executable loading; this is a separate platform compatibility result rather than evidence that the compiler silently succeeded.

If execution is unavailable, `python3 tests/verify_android_class8_2719.py` checks Linux-native BF generation and AArch64 simulation only. Record these as distinct evidence classes. The 300,000-command acceptance goal remains unmet.
