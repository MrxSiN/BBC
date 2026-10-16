# Windows x64 — bounded 192-command Brainfuck PE generator

Iteration 44 adds an opt-in 192-command writer and rel32 patcher. The production logic of both stages is standard Brainfuck. It supports all eight instructions, nested loops, wrapping bytes, EOF-to-zero, a zero-initialized 65,536-cell tape, and checked pointer movement. Generated Windows executables have **not run under the Windows loader**. The independent test environment runs their actual x64 instructions on Linux and substitutes four KERNEL32 imports.

## Reproduce the Linux-hosted checks

```sh
python3 tools/author_windows_loop_slots_192.py
python3 tools/author_windows_loop_patcher_192.py
python3 tests/verify_windows_full192.py
python3 tests/verify_windows_full128.py
python3 tools/check_docs.py
python3 bootstrap/run_windows_full192.py build/windows44_acceptance/transfer_192.bf /tmp/windows192.exe
objdump -p /tmp/windows192.exe
```

The authoring scripts generate the `.bf` files deterministically. During actual compilation, Brainfuck-native ELF stages generate all instruction slots, relocation bytes and final PE content. The Python adapter forwards byte streams, checks record framing and writes files atomically. It is not a hidden compiler.

| Setting | Value |
|---|---|
| Supported source | Exactly the eight standard BF instructions, at most 192 executable instructions |
| Backend | PE32+ x86-64 console, Microsoft x64 ABI |
| Image size | 3,584 bytes (`0xe00`) |
| `.text` raw size and RVA | `0xa00` bytes, `0x1000` |
| `.idata` raw offset and RVA | `0xc00`, `0x2000` |
| `.tape` RVA and virtual size | `0x3000`, `0x10000` |
| Source slots | 192 × 12 bytes |
| Loop displacement | BF-owned signed rel32 records and BF-owned PE patching |
| Win32 imports | ExitProcess, GetStdHandle, ReadFile, WriteFile |
| Failure behavior | Compilation rejects unmatched brackets and over-limit sources; existing destination is preserved |

The 192-slot implementation uses one-byte slot indices. This cannot be extended past 255 by raising a constant. The next source-size expansion must adopt multi-byte source/record indices and revalidate the PE layout. The previous [128-slot contract](WINDOWS_FULL128_PE.md) and [64-slot contract](WINDOWS_FULL64_PE.md) remain available.

## Evidence versus remaining work

The [Iteration 44 evidence](../evidence/iteration44_windows_full192.json) records 77 Linux-CPU differential executions, 990 branch relocation checks, 60 used-slot parity cases against the 128-slot backend, eight invalid-input rejections, and two independent BF-interpreter comparisons of emitter stages. The [Windows smoke bundle](../build/windows44_acceptance/manifest.json) contains 14 target-side test executables and a PowerShell runner. Their **Linux** shim checks passed, but their **Windows** execution status is NOT RUN.

A Windows loader run must validate imports, redirected binary I/O, EOF, loop behavior, tape traps, and nonzero failures. That evidence cannot be inferred from `objdump` or the Linux shim. The generated program is not a Windows-native BF compiler and cannot self-compile yet; Windows S1/S2 remain unimplemented. The Android 300,000-command objective is still separate and unmet.
