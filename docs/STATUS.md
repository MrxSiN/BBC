# BBC and BFX status

Evidence date: **2026-10-19**. Format: **BFX v1**, magic `42 46 58`, binary
version `01`. The [contract](BFX_CONTRACT.md) and
[execution profile](BRAINFUCK_PROFILE.md) define the shared behavior.

## Executed support

| Component | Android ARM64 | Windows x86-64 | Evidence |
|---|---|---|---|
| BBC frontend | EXECUTED | EXECUTED | Three native rebuild generations per platform reproduce the seed BFX |
| Canonical XAX decoder | EXECUTED: 393 cases | EXECUTED: 393 cases | Length, magic, version, opcode, bracket and resource limits |
| Canonical XAX importer | EXECUTED: 393 cases plus compiler, framer and decision outputs | EXECUTED: 393 cases | Android stores match the established Windows output byte for byte; input and four buffer guards preserved |
| Generated decision components | EXECUTED | EXECUTED: 89 calls across 13 modules | Native behavior agrees with the Brainfuck profile |
| Frontend rebuild cycle | EXECUTED: identical BFX/store/ELF across three generations; eight fixtures per generation | EXECUTED: identical BFX/store/DLL across three generations | Import and frontend execution occur on the target; native lowering occurs on Windows |
| Decision application | EXECUTED: eight Activity cases | UNIMPLEMENTED: no GUI application | Pixel 8 Pro, Android 17/API 37 |

The decoder and complete-importer case counts are separate runs of the same
393-case corpus. The eight Activity cases are separate from the 24 Android
frontend fixture checks. Neither count is a performance measurement.

The frontend is 4,531 source bytes and 2,455 executable instructions. It accepts
65,535 raw source bytes, 3,840 instructions and 255 nested loops. The
interpreter seed passed 21 fixture, boundary and bootstrap checks.

## Evidence index

| Report | What it establishes |
|---|---|
| [bfx_android_importer.json](../evidence/bfx_android_importer.json) | Current importer source and transaction; Android/Windows execution, native decisions, both rebuild cycles and reproducible artifacts |
| [bfx_migration.json](../evidence/bfx_migration.json) | Frontend/decoder hashes, 21 seed checks and 393 decoder calls on each target |
| [bfx_retirement.json](../evidence/bfx_retirement.json) | Canonical application hashes, eight Activity cases, 36 arithmetic checks and a 128 KiB stack probe |

Reports are immutable execution snapshots. Use the report for the component
and source hash being assessed; a report is not a continuously updated support
matrix. [XAX integration](XAX_INTEGRATION.md) pins the maintained source revision.

## Build host and boundaries

The importer and compiled Brainfuck frontend execute natively on Android and
Windows. Canonical verification, native lowering and Android packaging run on
Windows through unchanged generic XAX Python bootstrap utilities.
`XAX_REQUIRE_NATIVE` was unset; no Android-hosted XAX compiler claim is made.
The Android app embeds a compiled decision, without an importer or Brainfuck
interpreter. All BBC executable source remains `.bf`; XAX integration source
is canonical semantic graphs in the separate repository.

## Remaining work

- BBC-specific optimization is UNIMPLEMENTED. Any rule needs Brainfuck source
  changes and positive, negative, wraparound, loop and bounds-equivalence tests.
- Linux execution is UNIMPLEMENTED in this integration; no Linux execution
  host is available. Cross-compilation alone will not establish support.
- Native XAX compiler-host execution on Android is UNIMPLEMENTED in this cycle.
- The general ARM64 large-composite return-copy defect remains open as
  [XAX OI-49](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/XAX_OPEN_ISSUES.md#oi-49--android-arm64-large-composite-return-copy).
  The importer uses checked scratch outputs and mixing results of at most
  16 bytes, so it avoids that operation and executes successfully.
- No performance superiority or stable three-platform release is claimed.
