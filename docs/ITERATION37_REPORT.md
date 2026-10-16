# Iteration 37 — Android device acceptance gate prepared

**Result:** Verification infrastructure delivered; Android loader execution is **UNVERIFIED**. No compiler expansion beyond 2,000 commands is claimed.

## Implemented

- Added `tools/android_device_acceptance.py` to generate a reproducible, versioned bundle of 13 Android AArch64 PIE executables with byte-exact expected results and SHA-256 hashes. ELF machine code, relocation, file layout and startup remain entirely Brainfuck-authored by the existing Linux-native stages. This tool only packages, verifies and transports results.
- Added `tests/verify_android_device_acceptance.py` with ELF64/AArch64 PIE structure verification, expected byte I/O and tape traps, case coverage across six ELF size classes, synthetic-audit corruption checks and a no-adb failure test.
- Added a real-device `adb` path that first verifies local generated files, then verifies transferred bytes by pulling them back, executes under the Android shell, captures exact binary stdout/stderr and exit status, and records Android properties for review. It has **not run in this environment**.
- Preserved the canonical `compiler/core.bf`, all native Brainfuck stages and previous historical evidence; no C/Rust/Python machine-code generator was introduced.

## Tests run here

| Gate | Result |
|---|---|
| Thirteen BF-generated fixture binaries and six page classes | PASS, Linux-native BF compiler stages |
| Structural ELF and tape placement preflight | PASS, 13 files |
| AArch64 simulator with two load biases | PASS, 24 executions |
| Exact NUL/0xff stdin/stdout and EOF reference | PASS |
| Left and right tape-trap expectation | PASS as reference; right trap not executed in simulator preflight |
| Audit rejects wrong bytes, wrong status and missing status | PASS, synthetic results only |
| Missing `adb` does not manufacture device success | PASS |
| Source-comment and documentation checks | PASS |
| Linux native Stage 1 → Stage 2 self-compilation | PASS, 475,703-byte byte-identical ELF |
| Independent Linux Stage 0 cold bootstrap | NOT RERUN |
| Android loader execution of these thirteen ELF binaries | NOT RUN — no device/adb |
| Android-native compiler self-hosting | NOT IMPLEMENTED |
| 300,000-command Android executable | NOT IMPLEMENTED |
| Windows native PE32+ | NOT IMPLEMENTED |

The 13 ELF artifacts are in `build/android_device_acceptance_37`, with their versioned test manifest. Evidence is in `evidence/iteration37_android_acceptance_preflight.json` and `evidence/iteration37_linux_replay.json`. See [device instructions](ANDROID_DEVICE_ACCEPTANCE.md).

## Next engineering priority

1. Run the prepared suite through a genuine Android loader and preserve the output and device properties in a new evidence file. A simulator is not a replacement.
2. If that gate passes, move the Brainfuck compiler itself onto Android; prove it compiles ordinary BF natively and then recompiles its entire authoritative `.bf` source through repeated native cycles.
3. Expand BF-owned slot tables, branch relocation, ELF/RX length and tape-address arithmetic beyond 2,000 commands; the 300,000-command target is not remotely qualified yet.
4. Begin Windows only after Android-native self-hosting is verified, as requested.

The original 22-iteration roadmap was a forecast. Iteration 37 does not complete the Android platform gate.
