# Iteration 42 — Windows x64 CPU execution with test-only Win32 shims

**Classification:** EXECUTED native x86-64 machine instructions on Linux; Windows loader **NOT RUN**. **Date:** 2026-10-13.

## Implemented

Added an independent test-only C harness and differential Python runner. The C harness maps a specifically validated, bounded PE image at its preferred load base, installs four Win32-import test doubles with the Microsoft x64 calling convention, and invokes the BF-generated entry point. It catches `UD2` pointer traps and checks byte output and exit status. There is no shipping/compiler C implementation; production Brainfuck code, source parser, native emitter and patcher are **unchanged**.

This is the first execution of the *actual Windows-target x64 instruction bytes* in this local development environment, but it is **not an actual Windows device or loader run**. The native execution environment is still Linux with simulated API services. Do not relabel this as Windows target acceptance.

## Executed correctness and safety

- 164 BF source cases executed: **162** successful completions and **2** expected pointer traps, checked against the independent reference interpreter.
- 97 cases supplied binary input; 436 output bytes were verified. Source length reaches the full **64-command** backend limit.
- **11** unchanged Iteration 41 Windows smoke executables executed through the test harness and matched their archived expectations.
- Four bad-image lengths/header cases were rejected by the harness; the host-side compiler continues to preserve the destination file on failed source compilation.
- The earlier Windows PE seed, four-instruction, six-instruction and eight-instruction regression suites, plus source comment linting, passed.
- Fresh native Linux Stage 1 and Stage 2 self-compilation both reproduced the installed **475,703-byte** compiler ELF byte-for-byte. Independent cold Stage 0 **NOT RERUN**.

See [execution protocol](WINDOWS_LINUX_CPU_EXECUTION.md), [machine-readable shim evidence](../evidence/iteration42_windows_x64_cpu_shim.json) and [Linux self-hosting replay](../evidence/iteration42_linux_selfhost.json).

## Memory safety and dependency scope

The test harness enforces distinct RX and RW memory protections and translates generated `UD2` instructions into a controlled test status. This checks selected executed boundaries only; it is **not** a formal proof of target safety. GCC is a **test-only tool** to build the C shim harness. Linux, GCC and the shim are not involved in emitting PE code in the production BF-owned compilation path. The harness is not a general Windows loader or sandbox and must not be used with untrusted PE images.

## Platforms and remaining work

- Linux: existing S2 preserved and re-executed at native Stage 1→2; cold bootstrap not repeated.
- Android: bounded native S2 remains documented in archived Pixel 8 Pro evidence, while the 300,000-command target is incomplete.
- Windows: all eight BF instructions compiled within 64 commands and x64 machine-code execution checked on **Linux with Win32 shims**, but **Windows loader execution, native compiler execution and Windows S2 remain unverified/unimplemented**.

## Next priority

Execute the original Windows smoke suite under the real Windows x64 loader. Then extend Brainfuck-owned PE layout and bracket relocation beyond 64 commands; pursue Windows-native compiler and S2 with separate on-target evidence. Do not claim Windows runtime acceptance from the shim run.
