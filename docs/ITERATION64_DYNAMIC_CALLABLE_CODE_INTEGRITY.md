# Iteration 64 — Native callable instruction and relocation checks

## What changed

The standard-Brainfuck dynamic callable compiler and its generated AArch64 instructions are **unchanged**. The host publishing adapter now runs an independent streaming **native-code postflight** after the iteration-63 ELF header check, but before the existing atomic replace. The new `bootstrap/android_callable_code_validate64.py` checks the versioned BFP1 instruction templates, callable entry and exit code, and each BF-generated forward and backward loop branch. It rejects unknown instructions, broken instruction groups, malformed loop nesting, or a relocated branch that does not target its exact matched bracket boundary.

This Python code is an independent validator, **not an alternate Brainfuck compiler, optimizer, assembler, or ELF producer**. All authoritative Brainfuck parsing, emission and wide relocation remain in their original standard-BF stages. The validator does not modify the `.so` or calculate replacement instructions. A deliberate future change to the emitted BFP1 instruction format needs a reviewed validator update; the validator must fail closed on unknown new encoding.

The validation reads up to 56 bytes at a time, keeps a single bracket record per active loop in a temporary file and does not impose a fixed instruction count or nesting-depth limit. It does impose a specific *BFP1 binary-format contract*. Device memory, storage, supported 64-bit offsets and available execution time remain real resource constraints. The bytes in the loop literal are treated as signed 64-bit **data**, not executable AArch64 instructions. Each literal must point precisely to the correct counterpart boundary; therefore executable control flow cannot be redirected to the middle of a template by modifying only a relocation literal.

The previous ELF header validation remains necessary. This new check verifies the exact current compiler-generated code template language, not full machine-code security for arbitrary AArch64 binaries, a formal memory-safety proof, or Android loader acceptance. The host JNI adapter and installed-APK acceptance harness remain unchanged.

## Reproduce

```sh
python3 -m tests.verify_android_dynamic_callable64
python3 -m tests.verify_android_dynamic_callable63
python3 -m tests.verify_android_dynamic_callable59
python3 -m tests.verify_android_loader_probe60
python3 -m tests.verify_android_jni61_host
python3 tools/check_docs.py
```

The iteration-64 test generates **52 BF-native DSOs**, including 1,030 nested levels, and performs **104 differential AArch64 simulator/reference comparisons**. It corrupts seven code or branch-literal locations and verifies fail-closed rejection. Two additional test-only injections simulate a damaged BF-generated prologue and a damaged BF-generated relocation in the production build, each preserving the previous destination bytes. The scanner also accepts 13 archived compiled libraries, including Gmail `row`, Gmail `scope`, and Twitter `action`. These checks exercise real compiled BF output bytes, not just handcrafted AArch64 samples.

The iteration-63 240-program/960-simulator regression and iteration-59 DSO, iteration-60 loader-fixture, and iteration-61 Linux host-JNI suites passed in this environment. See `evidence/iteration64_dynamic_callable_native_integrity.json` and `evidence/iteration64_release_gates.json`.

## Open gates

There is **no new actual Android Bionic, ART/JNI, installed-APK or native Android dynamic-compiler self-hosting evidence**. The 13 local DSOs being structurally accepted does not prove the Android loader will accept them. Real device testing is the next blocking step. Original application parity and the eight remaining absent policy sources are likewise not complete. Older compiler lanes stay as temporary fallbacks until the dynamic lane passes those gates. The 100-million-command objective stays retired; no replacement fixed numerical threshold has been introduced.

The longer iteration-58 end-to-end regression was attempted in this session but exceeded the 120-second execution window. It is **incomplete this iteration**, not silently counted as passed. The narrower iteration-59, 60, 61, 62 and 63 suites and Linux native self-compilation were rerun successfully.
