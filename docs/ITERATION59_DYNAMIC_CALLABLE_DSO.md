# Iteration 59 — BF-native callable ELF dynamic library metadata

## Implemented

The iteration-58 Brainfuck-controlled all-eight-command stream/loop compiler is unchanged. A new standard-Brainfuck header stage, `experiments/android_callable_dso_header59.bf` (**13,520 filtered commands**), now emits an AArch64 ELF64 ET_DYN shared-object header, segment and section tables, SysV export lookup, and a versioned `BFP1` marker. The generated policy machine code remains identical to the iteration-58 callable output for the same source. Production compile entry: `python3 -m bootstrap.android_dynamic_callable59 source.bf -o policy.so`.

The header has two program headers: an RX PT_LOAD aligned to 16 KiB, and a read-only PT_DYNAMIC. It contains `.hash`, `.dynsym`, `.dynstr`, `.dynamic`, `.text`, `.shstrtab` and an exported `bfc_call_v1` function at file/virtual offset `0x400`. The ELF length and function / `.text` section length are calculated by the **executed BF stage** with 64-bit checked arithmetic. The implementation detects segment-length overflow instead of silently wrapping. The function uses AAPCS64 integer registers and keeps the previous tape, byte I/O, trap and loop-gas convention. This is **not** a JNI symbol; JNI calls through a host adapter.

Only the fixed-format ELF prefix and linker metadata are new. `bootstrap/android_dynamic_callable58.py` retains the previous output as a regression option, with the new `shared_library=True` option selecting BF-emitted DSO framing. The Python adapter still only handles opaque frames, temporary files, relocation storage and atomic commit. The old paths are still verification fallbacks, and no numerical source command ceiling was reintroduced.

`tools/android_bfp1_bridge/` supplies a minimal JNI adapter and Java API. The adapter builds with Android NDK but **does not** contain Brainfuck parsing or machine-code generation. It uses `dlopen`/`dlsym`, passes the eight AArch64 arguments and commits mutable byte arrays. Linux host-JVM JNI integration against a **test-only x86_64 native stub** passed; this cannot establish an Android device result. ABI details and restrictions are in [host bridge guide](../tools/android_bfp1_bridge/README.md).

## Executed evidence

- Fresh byte-identical rebuild of the new standard-Brainfuck native header stage from the canonical Linux compiler.
- 15 64-bit segment size/overflow vectors and two BF-interpreter-versus-native-stage comparisons.
- 13 DSO source programs; 52 AArch64 instruction-simulator differential runs; 13 emitted native-code byte-identical comparisons with iteration 58; 13 `readelf` structural checks.
- Three malformed-input / caller-quota rejection checks with unchanged prior output.
- Three locally archived original policies, Gmail `row`, Gmail `scope`, and Twitter `action`, emitted as DSO files with global `bfc_call_v1` symbols. Hashes and sizes are in `evidence/iteration59_original_policy_dsos.json`.
- Independent AArch64 Clang/lld cross-link of a tiny consumer against a BF-produced DSO; imported symbol resolution confirmed, but the consumer was not executed.
- Real Linux JVM JNI transport via an x86_64 stub: validates `dlopen`, `dlsym`, byte buffers, tape mutation across calls, output-full, missing path and invalid budget. The stub is test-only and **not** the BF compiler.
- Iteration-58 simulator regression freshly reran and passed: 59 cases / 354 AArch64 simulator runs, 2,772 BF-controlled 64-bit loop relocations, and depth 1,030.
- Fresh canonical Linux S0/S1/S2 compiler replay, with two independent interpreter seeds: three stage binaries byte-identical, seven native runtime probes passed; this is **Linux-only** self-hosting, not new Android self-hosting.

Sources: `evidence/iteration59_dynamic_callable_dso.json`, `evidence/iteration59_original_policy_dsos.json`, `evidence/iteration59_dso_crosslink.json`, `evidence/iteration59_jni_host_smoke.json`.

## Limits and safety

No Android device, Android NDK, Bionic loader, installed APK, or dynamic callable compiler native AArch64 self-hosting was available to verify this iteration. The new image is ELF/linker validated and AArch64 instruction simulated, **not Android `dlopen` proven**. C host bridge compilation is outside the BF compiler logic; Android NDK/Java/Gradle remain host integration dependencies. The other eight original Twitter and Threads BF policies were not present locally and cannot be labeled compiled. Threads `CAP_CALL`, callback recursion, session persistence contract and host policy result parity remain open.

Memory safety is enforced by generated pointer checks and output quotas in the tested execution contract; this is execution evidence, **not** a formal safety proof. Tape and input/output buffer lifetimes remain host responsibility. Even though the ELF export uses a normal C-callable convention, an actual Android loader may reject the file for loader-contract reasons that static inspection misses. Resolve that with a supported physical device or Android emulator rather than assuming it will load.

## Next priority

1. Test the **actual BF-produced `.so`** with Android `dlopen` and `dlsym` on a supported arm64 device/emulator; run actual JNI calls, including nested loops, bounds traps, output-full, EOF and gas. Fix any loader/ABI defects in the **BF source**, not in an external linker.
2. Import and pin/hash the other eight original BF policies, generate all eleven DSOs, and execute original product parity and callback/persistence protocols. Keep app host services explicit.
3. Prove Android-target native BF compiler execution/self-hosting. Remove bounded older production fallbacks only after all replacement acceptance gates pass.

The 100-million-command target stays retired. Compilation scales with available resources and checked 64-bit representation; there is no replacement arbitrary command-count milestone.
