# Windows PE x64 execution on Linux with test-only Win32 shims

**Iteration 42 — EXECUTED on a Linux x86-64 CPU. This is not Windows loader execution.**

The 64-command Windows PE writer already emitted all eight standard Brainfuck instructions in Iteration 41. Iteration 42 adds a *development-only validation harness* that maps those exact PE `.text` bytes into a Linux process and runs them on the native x86-64 CPU. Four Windows API imports are supplied by test-only C functions using Microsoft's x64 calling convention. No Brainfuck parser, optimizer, assembler or native compiler logic is in the harness.

## Run it

```sh
python3 tests/verify_windows_linux_x64_execution.py
python3 tests/verify_windows_full64.py
python3 tools/check_docs.py
```

The first test compiles the test harness with GCC, generates PE files through the existing BF-owned compiler stages, executes their **actual x64 instructions** and compares outputs or expected traps against an independent BF interpreter. It also replays all 11 existing Windows acceptance binaries without changing them. The program under test still contains x64 calls via its imported API pointers, not substituted source logic.

Implementation: [`../tests/windows_pe_linux_x64_shim.c`](../tests/windows_pe_linux_x64_shim.c) and [the differential runner](../tests/verify_windows_linux_x64_execution.py). The harness uses `mmap` at the bounded PE image's preferred base, copies `.text` and `.idata`, keeps a zero-initialized 65,536-byte tape, and fills the import table with Microsoft-ABI (`ms_abi`) shims for `ExitProcess`, `GetStdHandle`, `ReadFile` and `WriteFile`. It uses page permissions for RX code and RW tape. Native x64 `UD2` is translated by the test harness into exit status 99, so the independent reference's tape-boundary failures can be compared. It checks basic PE structural fields and rejects wrong file lengths, but **is not a sandbox for untrusted PE files**.

## Measured evidence

From [`../evidence/iteration42_windows_x64_cpu_shim.json`](../evidence/iteration42_windows_x64_cpu_shim.json):

- 164 newly compiled source programs completed an executed comparison: 162 successful exits and two expected pointer traps.
- 97 of those programs supplied binary input; byte output, wrapping, EOF, nested/transfer/zero loops and safe pointer motion were exercised.
- All 11 archived Iteration 41 smoke-test PE images passed the shim with their recorded expected output/status.
- Four malformed PE-image cases rejected before native execution.
- The maximum generated source remains 64 executable BF commands. **No larger Windows compiler has been implemented.**

These observations are **EXECUTED on a Linux CPU with test doubles**. The independently compiled Brainfuck program has not run with the genuine Windows PE loader, KERNEL32 implementation, Windows shell or ASLR behavior. This is not Windows native S1/S2, not full Win32 ABI conformance, and not a performance measurement.

## Remaining gates

Run [`../build/windows41_acceptance/verify_windows41.ps1`](../build/windows41_acceptance/verify_windows41.ps1) on Windows x64 and retain unmodified result logs and hashes. Separately extend BF-owned PE sizes and branch records beyond 64 commands, produce a Windows-native BF compiler binary, and demonstrate repeated target-side self-compilation. The Android 300,000-command objective remains open; historical bounded Android S2 is independent.
