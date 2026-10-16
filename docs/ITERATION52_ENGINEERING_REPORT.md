# Iteration 52 — Dynamic Android AArch64 ELF engineering report

## Completed implementation

The Linux-hosted development pipeline now creates full **freestanding AArch64 ELF64 ET_DYN** binaries from all eight standard Brainfuck instructions. This is the first integrated compact ELF path in the archived project beyond the older 2,719-instruction tier. It uses nine cooperating pure Brainfuck stages: three existing compact emission/ledger/stack stages and six new native branch arithmetic, patch index, and ELF layout stages. Development-only Python authors the BF stage sources; during compilation it transports opaque bytes and performs file storage, not instruction encoding or semantic BF compilation.

The generated executable uses 65,536 unsigned wrapping cells, EOF-zero input, bounds-trapped pointer movement and binary Linux/Android syscall I/O. The three loadable segments isolate ELF headers, a 65,536-byte zero tape and dynamically sized compact RX instructions. Native AArch64 branches and segment length fields are computed and emitted by standard Brainfuck, including carry and branch-reach rejection.

## Executed verification

| Test or measurement | Result |
| --- | --- |
| Small differential programs | **55 passed** |
| AArch64 simulations at two PIE load biases | **110 passed** |
| BF-controlled bracket pairs checked in these cases | **1,165** |
| Expected pointer-boundary traps | **29** |
| Atomic malformed/quota rejection tests | **4 passed** |
| Six new BF stage native images regenerated from both full and filtered BF sources | **Byte-identical** |
| Source arithmetic including positions crossing 32-bit boundary | Passed |
| Signed-26-bit branch-distance overflow | Rejected |
| `readelf` on small ELF images | Passed |
| Largest additional synthetic BF source | **296,307 commands** |
| Resulting synthetic ELF | **3,686,784 bytes** |
| Large synthetic ELF structural `readelf` check | Passed |
| Linux self-compilation stages 1 and 2 | Byte-identical to installed **475,703-byte** compiler |
| Android native device test of Iteration 52 ELFs | **Not performed** |
| Original eleven Gmail/Twitter/Threads BF policy programs compiled | **0 of 11** |

The large synthetic source is one opening bracket, 296,305 `+` instructions and one closing bracket, **not** the 296,307-command ThreadsHideAds `nested.bf` policy. Its native machine code was **structurally inspected**, not CPU-simulated at full length or executed on Android. The new compiler-stage BF command limit remains 16,128, but user-source output uses streaming records and resource-governed file growth.

## Six new self-hosted BF stages

| Stage | BF instructions |
| --- | ---: |
| `android_compact_span64_52.bf` | 7,538 |
| `android_compact_branch_words52.bf` | 7,467 |
| `android_compact_patch_indices52.bf` | 7,968 |
| `android_compact_elf_word_plus7_52.bf` | 15,526 |
| `android_compact_elf_words_to_bytes52.bf` | 4,406 |
| `android_compact_elf_header52.bf` | 3,545 |

All stages were compiled using `build/compiler_x86_64_linux.elf`, itself produced by the canonical unchanged `compiler/core.bf`. The original Android-native bounded Stage 0–3 S2 evidence remains archival and has not been reproduced for this new pipeline.

## Hard limits and open acceptance gates

AArch64 unconditional `B` has signed 26-bit word displacement, so code sections can grow without a fixed slot count but **loops beyond direct branch reach are rejected**, not transparently compiled. Branch islands or veneers are mandatory for unrestricted large sources; 100 million executable commands are **not** demonstrated end to end. Disk, memory, addressing and time also remain finite resources. The user-source command counter is separated from the 16,128-instruction limit on compiler-stage source files.

The freestanding `ET_DYN` image is structurally valid and simulator-tested, but it is **not verified on the Android kernel loader or linker**. It is also not a JNI-loadable `.so` implementing the original applications' custom host frame, capability, persistence and callback ABIs. Consequently it is not yet an APK compiler. No Windows, full Android universal self-hosting or claimed superiority to C/Rust is established.

## Reproduction

From the repository root:

```sh
python3 tests/verify_android_compact_dynamic_elf52.py
python3 bootstrap/android_compact_dynamic_elf52.py examples/android_loop_demo.bf -o /tmp/bfc52.elf
readelf -Wl /tmp/bfc52.elf
python3 tools/sync_status.py
python3 tools/check_docs.py
```

Nine device-side fixtures are provided in `build/android52_acceptance/` with a shell runner and SHA-256 expectations, but target-side execution and acceptance evidence are pending. See `docs/ITERATION52_DYNAMIC_AARCH64_ELF.md`, `docs/ANDROID52_DEVICE_ACCEPTANCE.md` and the machine-readable evidence files.
