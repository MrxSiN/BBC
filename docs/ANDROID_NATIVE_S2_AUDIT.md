# Android GM native checkpoint — 2026-10-14

GM now has an installed direct BF-native AArch64 APK: 21 passing instrumentation executions and 634,229 parity comparisons. Nine dynamic ELFs passed the Android loader, and native compiler Stages 0–3 were freshly byte-identical. The performance target remains unmet. See [the current report](ANDROID_GM_NATIVE_20261014.md) for the new BF optimization, actual timings, artifacts and limits. Earlier checkpoints below retain their historical scope.

---

# Android native Brainfuck compiler — archived device evidence audit

**Recorded device test:** Pixel 8 Pro, Android 17/API 37 (`arm64-v8a`), 2026-10-13. The supplied [v3 device report](../evidence/android_native_selfhost_20261013_v3/report.json) records execution of Stage 0 and three successive Android-native self-compilation stages, producing byte-identical AArch64 executables. [The offline audit](../tests/audit_android_native_selfhost_evidence.py) has independently checked the archive's source, ELF hashes, recorded program outputs and status codes. The device was **not reconnected** in this iteration; archived device execution is not a new device run.

## Verified archive properties

| Evidence | Result |
|---|---|
| Authoritative Android source | [`compiler/android_core.bf`](../compiler/android_core.bf), 14,727 source bytes, 14,575 standard BF instructions |
| Compiler artifact | 933,008-byte freestanding AArch64 PIE |
| Compiler artifact SHA-256 | `11782dea43d79697b248f164a1313ef5219e94105023c4456e4aa7ed28f1827c` |
| Stage 0 through Stage 3 | Byte-identical archived ELFs; Stages 1–3 have recorded device timings |
| Independent interpreter seeds | Reported identical by the recorded device runner |
| Program corpus | 14 recorded native Android executions cross-checked against BF reference output |
| Rejection corpus | 7 invalid compilation stream results audited |
| Compiler input limit | 16,128 BF commands and 255 bracket levels |
| Generated tape | 65,536 zeroed 8-bit cells; pointer bounds trap |
| Device range | One Pixel 8 Pro, API 37, 4 KiB runtime page size |

This is **S2 EXECUTED in archived evidence for the bounded Android native compiler**. The supplied run also records a further identical Stage 3. The source is raw standard Brainfuck; a development-only Python authoring aid was used to construct source text historically, but compilation and target machine-byte generation in the verified native execution path are performed by the saved Brainfuck compiler. The two independent seed executables and raw device data are part of the archive; we verified their reported outputs, not a fresh cold bootstrap with these seed programs on the current host.

## Important limits

The 300,000-command Android acceptance target remains unmet. The earlier Linux-hosted **2,000-command** Android ELF pipeline and the new **16,128-command** Android-native compiler are distinct implementations; neither should be presented as a 300,000-command integrated compiler. This does not prove Android APK/JNI generation, support for additional Android ABIs or versions, complete compiler-internal memory safety, or C/Rust performance dominance. Device attestation is limited to the recorded ADB evidence. The canonical 15,559-byte Linux `compiler/core.bf` and its S2 build remain unchanged.

## Recheck on this host

```sh
python3 tests/audit_android_native_selfhost_evidence.py
python3 tools/check_docs.py
```

To **repeat** device execution, use [`tools/verify_android_native_selfhost.py`](../tools/verify_android_native_selfhost.py) on a configured host with an authorized Android device, executable seed interpreters and `adb`. Do not treat an offline report audit as a new on-device pass.
