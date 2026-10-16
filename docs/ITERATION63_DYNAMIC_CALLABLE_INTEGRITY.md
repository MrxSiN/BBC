# Iteration 63 — Fail-closed dynamic callable ELF export validation

## What changed

The resource-scaled AArch64 BF compiler already emitted the ELF shared-object prefix and callable machine code using ordinary eight-instruction Brainfuck. Its host transport previously checked only a few header positions. A broken export table, section entry or dynamic lookup record might therefore survive the transport and be written to the requested output path. Actual Android Bionic loader acceptance is still not available here; catching plainly malformed metadata first is useful.

The new `bootstrap/android_callable_elf_validate63.py` validates generated `.so` files **after** BF stage emission and **before** the atomic `replace` in `bootstrap/android_dynamic_callable58.py`. It verifies ELF class, endianness, AArch64 type, both program headers, segment file extent and 16 KiB alignment, SysV symbol hash layout, `bfc_call_v1` export binding and size, string table, dynamic lookup tags, section headers and the BFP1 version marker. It does not create headers, calculate branch relocations, parse Brainfuck programs, modify the generated output, invoke a linker or execute native code. Python remains file transport and independent integrity checking, never the compiler.

Only the first 1,024 bytes and the filesystem-reported length are needed: validator memory usage does not scale with program or code size. The ELF ABI contract remains versioned as BFP1. For now, a future deliberate new ELF layout requires updating the validator with a reviewed contract and tests. A legitimately different DSO cannot silently pass under the old version.

## Reproduce the executed checks

From repository root:

```sh
python3 -m tests.verify_android_dynamic_callable63
python3 -m tests.verify_android_dynamic_callable59
python3 -m tests.verify_android_apk62
python3 -m tests.verify_android_jni61_host
python3 tools/check_docs.py
```

The new test compiles 240 seeded BF programs into AArch64 shared objects and compares 960 emitted-code interpreter simulations against the independent Brainfuck semantics reference, with randomized input, budgets, tape lengths and output capacities. It then corrupts 40 distinct ELF header fields, tries four wrong file lengths, and injects malformed BF-stage output into the production adapter to verify that the previous artifact survives. Finally a BF-generated header for a sparse 4 GiB+ file validates 64-bit metadata accounting using fixed memory. **Sparse extent is not native code generated from a 4 GiB program and is not a throughput benchmark.**

Earlier iterations' native Linux bootstrap stages and canonical Brainfuck source are unchanged. The new validator is a transport check, not a second compiler. Linux-host JNI regressions execute C test stubs, not the BF-generated AArch64 code on Android.

## Acceptance and limitations

Executed locally: BF-native DSO generation, structural rejection and atomic output protection, AArch64 instruction simulation, and host Java/JNI stub tests. Not executed: Android Bionic `dlopen`, Android ART/JNI invocation of BF-generated code, installed test APK, full original application-policy parity, remaining eight original policies, or native Android self-hosting. Neither the sparse-file test nor `readelf` alone establishes Android compatibility.

The active goal is a fully dynamic callable Brainfuck native compiler. There is no fixed 100-million-command gate. The former bounded compiler implementations remain fallbacks only until actual target-side execution, policy parity, and native self-compilation pass. Evidence: [iteration 63 integrity result](../evidence/iteration63_dynamic_callable_integrity.json) and [iteration 62 device acceptance guide](ITERATION62_ANDROID_APK_ACCEPTANCE.md).
