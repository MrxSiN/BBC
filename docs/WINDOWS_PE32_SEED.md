# Follow-up: Iteration 39

The original fixed-image seed is preserved below. A [new Brainfuck-owned bounded linear PE compiler](WINDOWS_LINEAR_PE.md) now emits source-dependent arithmetic and pointer-movement code for a maximum of 64 commands. This is a separate prototype; neither image has been executed under the Windows loader in this environment.

---

# Windows PE32+ — first Brainfuck-owned binary writer

This is the first Windows engineering slice after the archived Android native S2 gate. It creates a **fixed Windows x86-64 console exit image**, not yet a Brainfuck compiler and not yet an executed Windows binary. Its purpose is to prove that a normal standard-Brainfuck program can own Windows PE32+ header bytes, import-table bytes and x64 entrypoint bytes without a C/LLVM linker in the production generation path.

## What exists

| Component | Current result |
|---|---|
| [`experiments/windows_pe_exit_seed.bf`](../experiments/windows_pe_exit_seed.bf) | 6,194 standard BF instructions, emits 1,536 PE bytes |
| Linux-native executable of that BF emitter | [`build/windows_pe_exit_seed_x86_64_linux.elf`](../build/windows_pe_exit_seed_x86_64_linux.elf), 198,423 bytes |
| Generated PE image | [`build/windows_pe_exit_seed_x86_64.exe`](../build/windows_pe_exit_seed_x86_64.exe) |
| Machine and subsystem | AMD64 PE32+ console, two sections |
| Import | `KERNEL32.dll!ExitProcess` through an import address table |
| Section permissions | `.text` RX, `.idata` RW; no writable executable section |
| Execution status | Parsed by `objdump`, **NOT EXECUTED on Windows** |

The code reserves the Windows x64 stack home area, clears the first argument, and performs a RIP-relative call through the import address table. The entrypoint would call `ExitProcess(0)` if accepted by the Windows loader. That behavior is a **design expectation**, not an observed execution result. No arbitrary BF source is accepted; there is no Windows tape, BF loop lowering, byte I/O, bounds checks, Windows-native compiler execution, or Windows self-hosting yet.

The authoritative executable output logic is the raw `.bf` program. [`tools/author_windows_seed.py`](../tools/author_windows_seed.py) is a development-only deterministic source-authoring aid; it must not become a production code generator, parser or linker. The resulting PE is emitted by executing the BF program as a Linux-native executable compiled by the existing Linux BF compiler.

## Verification

```sh
python3 tests/verify_windows_pe_exit_seed.py
objdump -p build/windows_pe_exit_seed_x86_64.exe
```

The test compares two executions of the compiled BF program against an independent standard BF interpreter, checks PE/COFF and import fields, validates section permissions and RIP-relative call displacement, and rejects selected corrupted fields. These checks are **structural only**; the Windows loader and Win32 API call need target-side execution evidence. The baseline output SHA-256 is `dad4128b16b931b0f140ec5aa0880f7198e390a74c79509973e4e262a4bc218e`.

## Next implementation gates

1. Execute the fixed PE through an actual Windows x64 loader and confirm exit status 0.
2. Implement a BF-owned source filter and command decoder, then real x64 instruction generation with a defined 65,536-byte tape and bounds checks.
3. Add byte input/output through documented Win32 standard handles and correct Microsoft x64 ABI rules.
4. Add BF-owned matching and relocation for nested loops, independently verify the executable corpus, and then make the Windows BF compiler build and recompile itself on Windows.

Do not count this fixed image as a working Windows compiler or a Windows S1/S2 milestone.
