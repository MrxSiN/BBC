# Windows x64 — all eight Brainfuck instructions, bounded PE writer

## Iteration 42 CPU-level execution addendum

The [Linux-native x64 test harness](WINDOWS_LINUX_CPU_EXECUTION.md) has executed these exact BF-generated x64 machine-code bytes with Microsoft-ABI Win32 API shims. **164 differential programs** and all **11** archived smoke binaries matched expected results, including EOF, wrapping, nested loops and traps. This is **not** the Windows PE loader or real Win32 APIs; Windows-native execution and S2 remain open. Production BF emitter sources and the 64-command limit are unchanged. [Evidence](../evidence/iteration42_windows_x64_cpu_shim.json).

---


**Iteration 41: Linux-hosted BF compilation verified; Windows execution NOT RUN.**

The new opt-in path accepts up to **64 filtered Brainfuck commands**, including matched nested or sequential `[` and `]`, and writes a **2,048-byte PE32+ console executable**. The entire parser-to-image compilation logic remains in standard Brainfuck. This extends, but does not replace, the previous [six-instruction Windows writer](WINDOWS_LINEAR_IO_PE.md).

## Run it

```sh
printf '+++[->+<]>.' > /tmp/transfer.bf
python3 bootstrap/run_windows_full64.py /tmp/transfer.bf /tmp/transfer.exe
objdump -p /tmp/transfer.exe
objdump -d -j .text -Mintel /tmp/transfer.exe
python3 tests/verify_windows_full64.py
```

Generated binaries are **not verified to load or execute on Windows**. For target-side checks, copy the contents of [`../build/windows41_acceptance/`](../build/windows41_acceptance/) to a real Windows x64 machine and run `verify_windows41.ps1`. Keep the resulting `device_results_windows41.json` as evidence. No Windows execution is claimed from `objdump` output.

## Brainfuck-owned stages and protocol

| Stage | Source | Function |
|---|---|---|
| Filter | [`android_source_scan.bf`](../experiments/android_source_scan.bf) | Ignore non-BF bytes; report filtered count |
| Parse | [`android_wide_bracket_metadata.bf`](../experiments/android_wide_bracket_metadata.bf) | Check bracket balance; emit command positions |
| Pair | [`android_wide_bracket_pairs.bf`](../experiments/android_wide_bracket_pairs.bf) | Produce matched one-based 24-bit position pairs |
| Encode | [`windows_x64_loop_rel32.bf`](../experiments/windows_x64_loop_rel32.bf) | Compute signed `rel32` displacement bytes in BF |
| Emit | [`windows_loop_slots_pe_64.bf`](../experiments/windows_loop_slots_pe_64.bf) | Select all eight native instruction slots; emit PE headers and Win32 helper code |
| Patch | [`windows_x64_loop_patch_pe.bf`](../experiments/windows_x64_loop_patch_pe.bf) | Insert BF-generated relocation bytes into the 64 code slots |

The x64 instruction slot is 12 bytes. `[` uses `cmp byte ptr [rbx], 0; je rel32; nop nop nop` and `]` uses the same comparison followed by `jne rel32`.

For a matching pair at one-based command positions `a` and `b`, where `b` is the closing bracket:

- Opening jump displacement: `12 * (b - a) + 3`, landing after the closing bracket slot.
- Closing jump displacement: `-12 * (b - a) - 9`, landing on the opening bracket slot to recheck the current cell.

These values are computed at **compiler execution time inside Brainfuck**. The bracket encoder consumes the BF pair stage's seven-byte records. It emits two six-byte records per pair: `0x5B, a, rel32le` and `0x5D, b, rel32le`, followed by a status byte. The BF patcher accepts those records followed by a zero terminator and an unpatched 2,048-byte BF-produced PE image. It streams a patched PE and status. The [Python adapter](../bootstrap/run_windows_full64.py) handles only transport, framing and atomic output placement; it does not match brackets, calculate branches, select machine code or modify PE bytes.

The encoder trusts correctly matched, bounded pairs from upstream BF stages. The patcher trusts validated records with slot positions 1–64. These are internal byte protocols, not general-purpose adversarial record parsers.

## Tape and platform boundaries

The PE uses a zero-initialized 65,536-byte tape, 8-bit wrapping cells, checked pointer movement using x64 `UD2` on out-of-bounds moves, and existing `KERNEL32.dll` imports for `ExitProcess`, `GetStdHandle`, `ReadFile`, and `WriteFile`. EOF-zero and binary I/O are emitted as native code but remain unexecuted on Windows. No loader or API compatibility conclusion is possible from offline instruction inspection alone.

The executable contains one fixed 64-slot code region, three PE sections and helper code. Oversized or unbalanced source rejects before output publication. Rejection preserves the old destination file.

**Limitations:** only x86-64 Windows console executables; maximum 64 Brainfuck commands; no Windows-native compiler or Windows-native self-hosting; no on-Windows runtime verification; no optimizer. A 2,048-byte image is a bounded experimental artifact, not a general Windows compiler release. Android bounded S2 remains archived separately; the 300,000-command Android acceptance target remains open.

See [Iteration 41 report](ITERATION41_REPORT.md) and [machine-readable evidence](../evidence/iteration41_windows_full64.json).
