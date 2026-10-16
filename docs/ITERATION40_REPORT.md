# Iteration 40 — Windows BF-owned standard-stream I/O backend

## Implemented

Added the **10,352-command standard Brainfuck** source `experiments/windows_linear_io_pe_64.bf`. The native Linux BF compiler builds it into a **331,479-byte ELF**, and the stage emits **2,048-byte source-dependent Windows PE32+ executables**. Added 64-slot support for `.` and `,` using native x64 calls into BF-emitted Win32 helper routines. Supported subset is now six operators: `+ - > < . ,`, including zero-at-EOF behavior in emitted code and checked pointer moves. Brackets are rejected.

The accepted source limit is 64 executable commands. Machine-code selection, PE layout and import emission are owned by Brainfuck. The development-only Python authoring script produced the BF source but does not run in the production compile path. The Python transport is limited to scanning-stage framing and atomic file placement.

## Verification (executed on Linux)

- **87** source-dependent PE/slot-structure inspections; **31** independent Brainfuck reference-program executions (not native PE executions).
- **6** independent BF-interpreter runs emitted byte-identical images.
- **6** unsupported or over-limit programs rejected by the BF stage, including **6** atomic-output preservation checks.
- `objdump -p` recognized `ExitProcess`, `GetStdHandle`, `ReadFile`, and `WriteFile` imports.
- Static x64 checks cover helper call encodings, the intended 32-byte shadow-space frame, EOF-zeroing instructions, transfer counts and error traps. Call-time stack alignment and Win32 behavior require target execution.
- Iteration 39 four-instruction regression, Iteration 38 fixed PE seed regression, and source-comment checks passed.
- Native Linux Stage 1 and 2 self-compilation each reproduced the installed 475,703-byte compiler exactly. **Cold independent Stage 0 not rerun.**

## Target execution and constraints

**No Windows loader or Wine is installed here.** No new Windows-native execution, Windows API call, binary I/O or native compiler S2 was demonstrated. The Win32 ABI assumptions are structurally checked but target-runtime behavior is still unverified. Only 6 of 8 instructions are emitted, no loops, fixed 64-command ceiling. The PE lacks a relocation directory. Direct Windows console encoding behavior is unverified; the acceptance bundle uses redirected streams. A failed I/O call triggers `UD2`; exact Windows exit status must be measured.

## Next

Run `build/windows40_acceptance/verify_windows40.ps1` on Windows x64, preserve `device_results_windows40.json`, then implement Brainfuck-owned `[` and `]` branch lowering with correct x64 displacement patching. Retain Linux S2, archived Android native S2 and the open 300,000-command Android target.

See [contract](WINDOWS_LINEAR_IO_PE.md), [evidence](../evidence/iteration40_windows_linear_io.json), and [BF source notes](../experiments/windows_linear_io_pe_64.bf.notes.md).
