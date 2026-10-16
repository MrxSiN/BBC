# Iteration 53 engineering report — Android 64-bit PC-relative loop relocation

**Classification:** Linux-native standard Brainfuck compiler stages plus Linux-hosted AArch64 instruction simulations; no Android target execution.

## Functional change

Complete opt-in AArch64 freestanding PIE generation now uses 32-byte loop slots containing AArch64 `ADR`, `LDR (literal)`, shifted-register `ADD` and `BR`. The embedded signed 64-bit **word** displacement is computed by a Brainfuck program and relocated using a Brainfuck-derived native word position. This removes the previous `B imm26` encoding reach constraint and remains position-independent across tested load biases. The older direct-branch Iteration 52 route is untouched. Raw stream emission, dynamic file-backed pairing and ELF metadata stages remain BF-owned.

The four new compiled BF stages contain 7147, 10978, 10138, 15275 executable instructions. Each is below the current native compiler's 16,128-command source-input limit; each independently rebuilt byte-identically.

## Executed checks

| Check | Outcome |
|---|---|
| Small BF source cases | 57 passed |
| AArch64 simulator at two PIE biases | 114 passed |
| Matched loop relocation pairs | 1466 |
| Native arithmetic, including wide offsets | 36 passed |
| Bracket-free ELF byte parity | 6 passed |
| Atomic malformed-input/resource-limit rejections | 4 passed |
| Independent BF stage interpreter comparisons | 2 passed |
| New BF stage native regeneration | 4 byte-identical |
| Largest structurally verified synthetic BF source | 296,307 commands |
| Large synthetic ELF size | 3,686,824 bytes |
| LLVM AArch64 instruction disassembly | Verified PC-relative jump template |
| Prior Iteration 52 dynamic ELF regression | Passed |
| Android V1 transport regression | Passed |
| Eleven-policy metadata audit | Passed; policies **not** compiled |
| Linux canonical compiler S1/S2 replay | Byte-identical, 475,703 bytes |
| Android device loader | Not run |

## Current limitations

A >128 MiB branch distance passed the BF-native relocation arithmetic checks, but no actually loaded >128 MiB-branch ELF was executed. The structural large-source test used a repeated-command synthetic program, not the real upstream `scope.bf`, `row.bf` or any other required Android policy. The pipeline emits a freestanding PIE executable, **not** a JNI-loaded DSO; Android linker conventions, hooks, persistent tapes, callbacks, API frame protocols and APK packaging still need work. 100 million mixed BF commands have not completed native ELF compilation.

The canonical Linux compiler source SHA-256 remains `f73a9b7ddc9d6f1971435251edefd85e3bb81a0dda23e8b11630a2d7cf7407e9` and its native compiler executable SHA-256 `e95ec4e028a28f18d955f908cf40e2f9b9fbe650b6ebfd4df6d819c3f6f6cea8`. Cold Stage 0 was not rerun. The Android historical native S2 evidence is separate from the present backend.

## Evidence and next acceptance

- `evidence/iteration53_android_far_elf_tests.json`: exact new-source/native hashes, tested counts and execution class.
- `evidence/iteration53_large_synthetic.json`: ELF size and structural-only classification.
- `evidence/iteration53_linux_selfhost_replay.json`: fresh canonical Linux S1/S2 exact comparison.
- `build/android53_acceptance/manifest.json`: nine fixture hashes and expected output, on-device **not run**.
- `docs/ANDROID_DYNAMIC_ROADMAP_ITERATION53.md`: next real-app, JNI, long-span and 100M gates.

A genuine release path must first run these executables with the Android loader, then compile all eleven pinned original BF application policies with their JNI host contract intact, then profile million-to-100M mixed source workloads and demonstrate native self-hosting on Android.
