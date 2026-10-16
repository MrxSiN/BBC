# Windows x64 — 128-command Brainfuck-owned PE32+ writer

**Iteration 43: Linux CPU execution passed. Real Windows loader execution is not yet verified.**

The new optional path accepts up to **128 filtered Brainfuck commands**, including nested `[` and `]`, and generates a **3,072-byte PE32+ console executable**. All eight instructions retain the V0 8-bit, modulo-256, 65,536-cell tape model and checked pointer moves. The previous [64-command backend](WINDOWS_FULL64_PE.md) remains in the repository and passes its regression tests.

## Reproduce

```sh
python3 bootstrap/run_windows_full128.py build/windows43_acceptance/loop_across_slot64.bf /tmp/transfer128.exe
python3 tests/verify_windows_full128.py
python3 tests/verify_windows_full64.py
python3 tools/check_docs.py
objdump -p /tmp/transfer128.exe
```

If the named example differs between branches, replace `build/windows43_acceptance/loop_across_slot64.bf` with your own small `.bf` file. The compiler accepts ignored non-instruction source bytes; no additional BF syntax is recognized.

## Production compilation stages

| Stage | Authoritative implementation | Contract |
|---|---|---|
| Scan | `experiments/android_source_scan.bf` | Filter input, report 24-bit count |
| Bracket metadata and matching | `experiments/android_wide_bracket_metadata.bf`, `experiments/android_wide_bracket_pairs.bf` | Produce one-based paired positions |
| x64 branch arithmetic | `experiments/windows_x64_loop_rel32.bf` | Two six-byte `rel32` records per bracket pair |
| PE and x64 code emission | `experiments/windows_loop_slots_pe_128.bf` | 128 twelve-byte x64 slots; 3,072 PE bytes followed by status |
| Relocation application | `experiments/windows_x64_loop_patch_pe_128.bf` | BF-owned patched PE bytes and a status byte |

`bootstrap/run_windows_full128.py` only passes bytes between the native BF stages, validates framing and length, and atomically places the emitted executable. Its Python code does **not** parse brackets, calculate x64 branch displacements, generate PE bytes or patch x64 code. Development-only `tools/author_windows_loop_slots_128.py` and `tools/author_windows_loop_patcher_128.py` generated the saved standard-BF sources; they are not part of production compilation.

The x64 slots are 12 bytes, with 31 bytes of startup code. The PE `.text` section grows from 0x400 to **0x800** raw bytes at file offset `0x200` and RVA `0x1000`. `.idata` remains at RVA `0x2000` but moves to file offset **`0xA00`**. `.tape` remains a 65,536-byte, zero-initialized, writable (not executable) section at RVA `0x3000`. The PE imports `ExitProcess`, `GetStdHandle`, `ReadFile` and `WriteFile` from `KERNEL32.dll`. The test-only Linux harness has been updated for this specific bounded layout.

The BF rel32 encoder still emits one-byte slot indices and 16-bit loop span arithmetic with sign extension into a 32-bit displacement. At 128 slots, these are within the proven bounded range. **This is not a general source-size solution:** the next extension beyond 255 positions requires a different record/index contract, and subsequent increases also require PE section sizing/layout work.

## Evidence, not guesses

- **100** differential x64 CPU executions passed under test-only Linux Win32 ABI shims, including 26 programs beyond 64 commands.
- **868** generated bracket displacement destinations were checked against the 12-byte-slot target rule.
- **2** independent Brainfuck interpreter comparisons reproduced native BF-stage output.
- **8** malformed or over-limit source inputs were rejected; atomic output preservation was checked.
- **12** target-side Windows acceptance executables are prepared with SHA-256 hashes and expected binary I/O in `build/windows43_acceptance/manifest.json`.
- Existing 64-command and earlier Windows regressions passed, and Linux self-compilation Stages 1–2 stayed byte-identical.

Evidence is recorded in [`../evidence/iteration43_windows_full128.json`](../evidence/iteration43_windows_full128.json) and the [Iteration 43 report](ITERATION43_REPORT.md).

## Open gates

The executable has **not** run through the Windows x64 loader or real KERNEL32. Run `build/windows43_acceptance/verify_windows43.ps1` on a supported native Windows x64 machine and retain the result log. A Linux CPU shim is not a substitute for target-native evidence. Windows-native BF compiler execution, repeated S2 self-hosting, source capacities far beyond 128, and the separate Android 300,000-command acceptance goal remain open.
