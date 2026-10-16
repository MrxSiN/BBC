# Windows x64 — bounded linear Brainfuck byte-I/O backend

**Iteration 40: Linux-executed BF generation, Windows loader not tested.** This is a separate experimental path from the Iteration 39 four-instruction compiler. It generates source-dependent **2,048-byte PE32+** images from up to 64 *linear* Brainfuck instructions. The PE bytes are emitted by [`windows_linear_io_pe_64.bf`](../experiments/windows_linear_io_pe_64.bf), a **10,352-instruction standard Brainfuck program** built and executed through the existing self-hosted Linux compiler.

## Scope and contract

| Item | Behavior |
|---|---|
| Source instructions | `+ - > < . ,` (exact six of eight Brainfuck operators) |
| Loops | Unsupported; `[` and `]` rejected before publishing output |
| Maximum source | 64 executable BF commands; adapter accepts up to 1 MiB of raw source |
| Cell semantics | Zeroed 65,536-byte tape, modulo-256 arithmetic |
| Pointer safety | Checked movement; x64 `UD2` for either boundary violation |
| Byte input | Imported `GetStdHandle(STD_INPUT_HANDLE)` and `ReadFile` for one byte; EOF stores zero |
| Byte output | Imported `GetStdHandle(STD_OUTPUT_HANDLE)` and `WriteFile` for one byte; incomplete writes trap |
| Native PE | `.text` RX, `.idata` RW, `.tape` zero-backed RW; fixed three-section PE32+ image |
| Compiler status | Linux-executed BF generator; *not* a compiler running on Windows |
| Windows loader/API execution | **NOT RUN** |
| Windows native self-hosting | **UNIMPLEMENTED** |

The x64 prologue uses RBX as the active cell pointer, R12 as the tape base, R13 as the tape end, R14/R15 as addresses of shared I/O helpers. The 12-byte `.` and `,` command slots call R14 and R15, respectively. Each helper sets up Microsoft x64 32-byte shadow space, keeps RSP 16-byte aligned at API calls, sets the fifth argument of ReadFile/WriteFile to NULL, and checks the returned BOOL. ReadFile zeroes the cell before invoking the OS; if zero bytes are read, the cell remains zero. A failed call triggers an invalid-instruction trap; the Windows process-level exception/exit-code mapping is not yet verified.

All PE headers, native instructions, imports and fixed helper code are emitted by the saved BF program. The Python [`authoring aid`](../tools/author_windows_linear_io.py) produces that authoritative BF source for development; the normal [`transport adapter`](../bootstrap/run_windows_linear_io.py) only runs BF stages, verifies framing and atomically saves the PE. It does not produce native code or patch the image.

## Compile, inspect, validate

```sh
printf ',.' > /tmp/echo.bf
python3 bootstrap/run_windows_linear_io.py /tmp/echo.bf /tmp/echo.exe
objdump -p /tmp/echo.exe
objdump -d -j .text -Mintel /tmp/echo.exe
python3 tests/verify_windows_linear_io.py
```

The Linux-hosted suite verifies 87 generated PE/slot images, 31 reference BF-program executions, six independent BF-writer interpreter comparisons, six rejected invalid inputs with atomic output preservation, import records and x64 helper encodings. It does **not** prove that Win32 APIs, loader relocation policy, binary pipes, console output or Windows exception handling work when executed.

## Prepared Windows acceptance suite

The directory [`../build/windows40_acceptance/`](../build/windows40_acceptance/) contains eight BF-generated PE files and [`verify_windows40.ps1`](../build/windows40_acceptance/verify_windows40.ps1). On actual Windows x64, from the extracted directory, execute:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\verify_windows40.ps1
```

The script verifies SHA-256 values and records the OS, output bytes, exit codes and per-case outcomes in `device_results_windows40.json`. Preserve this result as evidence. **This suite has not yet been run here.** The pointer trap intentionally expects a nonzero exit but does not assume a specific Windows exception code.

## Next gates

1. Run this exact bundle through a real Windows x64 loader, capture process outputs and loader/exception behavior, and investigate all failures.
2. Introduce Brainfuck-owned bracket pairing, x64 conditional jumps and safe relocation to support all eight BF commands.
3. Extend capacity beyond 64 commands without corrupting PE layout and keep source-size limits explicit.
4. Execute the compiler itself on Windows and repeat a complete native self-compilation sequence, including reproducibility and independent semantic tests.

The Android bounded native S2 evidence remains archived; the separate 300,000-command Android acceptance target remains outstanding.
