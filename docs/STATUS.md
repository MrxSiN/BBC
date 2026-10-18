# BBC status

2026-10-18. PROTOTYPE. The updated prompt's BBX format and `.bbx` artifacts
are implemented, including a separate binary version byte. Repository cleanup
and BF-owned bootstrap framing remain in place. The BBX-to-XAX graph importer
and Android app have executed on a Pixel 8 Pro. The native Brainfuck frontend
completed three exact rebuild generations through the external XAX backend.

| Milestone | Status | Evidence or remaining work |
|---|---|---|
| M0 contract and inspection | EXECUTED | BBX/profile fixed; real XAX construction interfaces inspected and smoke-tested |
| M1 frontend and BF bootstrap | EXECUTED | Independent interpreters agree; BF framer feeds the BF frontend; interpreted round trips pass |
| M2 Android vertical slice | EXECUTED | XAX-built Activity visibly permits, blocks and handles errors on Android 17/API 37 ARM64 |
| M3 native frontend self-hosting | EXECUTED | Three identical frontend generations on Android and Windows; native BF framing on Android; external XAX backend |
| M4 Windows x86-64 | EXECUTED | Native PE decision component and frontend cycle; no Windows GUI app claimed |
| M5 Linux x86-64 | UNIMPLEMENTED | WSL is absent; user confirmed no Linux host is available |
| M6 optimization | UNIMPLEMENTED | No speed advantage claimed |

## Implementation and execution

All seven executable source files are ordinary Brainfuck: the frontend,
bootstrap framer, decision example and four small profile tests. Together
they contain 2,808 instructions. Other retained files are documentation,
licenses, non-executable metadata, exact binary fixtures and evidence. No
foreign-language implementation, bootstrap, build script, test harness or
vendored project remains outside Git history. Generated output is ignored.

The frontend is unchanged: 4,531 source bytes, 2,455 instructions; maximum
65,535 raw source bytes, 3,840 instructions and nesting 255. The new bootstrap
framer is 1,207 bytes and 302 instructions, buffering at most 7,680 NUL-free
text bytes. Read [BOOTSTRAP.md](BOOTSTRAP.md) for the termination restriction
and the still-required external seed interpreter. The text restriction does
not alter the compiler's binary source semantics.

- **224 frontend checks EXECUTED** under the external C# interpreter on
  Windows/.NET, including 160 deterministic random byte sources, all byte
  values, malformed framing, count/nesting limits and compiler round trip.
- **18 bootstrap checks EXECUTED** under that interpreter: byte preservation,
  count carry, maximum size and rejection, fixtures, BF-produced compiler
  input, compiler round trip and compiled-framer parity.
- **24 checks EXECUTED** under the separate external Python interpreter,
  covering exact compiler/profile/bootstrap fixtures, bootstrap limits,
  both tape bounds, compiled-framer parity and own-source agreement.
- The sample decision emits `01` for input `00` and `00` for nonzero input.
  The native Android app now uses these bytes to show/hide its sample row.
- Maximum observed tape cells were 61,471 for the compiler and 61,455 for
  bootstrap framing, within their documented layouts. This is test evidence,
  not a formal proof or an XAX backend guarantee.
- The external source audit accepted all seven BF files and their annotations;
  longest code line is 64 columns. All nine Markdown documents and their local
  links passed consistency checks. Source/tool/artifact hashes, the recovery
  archive, retained-file count and `git diff --check` also passed.

Evidence and tool hashes: [frontend](../evidence/bbx_frontend.json),
[bootstrap](../evidence/bbx_bootstrap.json),
[Python reference](../evidence/bbx_reference.json),
[XAX inspection](../evidence/bbx_xax_inspection.json),
[XAX integration](../evidence/bbx_xax_integration.json),
[Android device](../evidence/bbx_android.json),
[native Android frontend cycle](../evidence/bbx_selfhost_android.json), and
[Windows execution](../evidence/bbx_windows.json).
The recorded elapsed times are development runs, not controlled benchmarks.

The format migration changes only emitted magic/version bytes and their
dependent artifacts; request framing, validation and execution semantics are
preserved. Old records require recompilation as described in
[BBX_CONTRACT.md](BBX_CONTRACT.md). The new maintenance instructions apply
SRP/SoC, narrow interfaces, versioned contracts, backend substitutability and
DRY/KISS/YAGNI within the existing structure; no extra layers were added.
The cleanup record is historical: its pre-migration source hashes remain the
hashes observed during cleanup. Current source hashes are in the BBX evidence.

## External dependencies

Independent interpreters and verification drivers are external development
tools. The former Python reference and annotation checker were preserved
outside the repository for independent testing. No production algorithm was
moved there to conceal a dependency. The running bootstrap path consists of
the two BF programs plus an external seed that only interprets Brainfuck.

XAX is a separate foreign toolchain dependency. Its importer is local commit
`2ce6797782532a08f7938d8db6a2e881c013d3e9`; its Android caller/app is local
commit `fa516f2bbab1036905e17df4039eb40f91917da9`. Windows fixes and tests are
local commit `51bb251aff4abfe340901960b150eb11dc2a9a50`. The pre-existing
modified README was left untouched. Older inspection/integration records are historical.
The remote-main push awaits explicit authorization after automatic approval
review rejected it. Current evidence pins the tested file hashes and commit.

Twenty-seven of 30 XAX test methods passed with the Android Studio JDK on PATH;
three existing platform-dependent methods skipped. The original importer tests
include 29 ARM64 emulations and 13 additional real-BBX integration checks.
Four new Android tests add 15 caller cases plus deterministic graph/APK checks.

The core borrows distinct initialized input, output and tape views, clears the
full tape per call and returns a packed length/status. It is not an untrusted
raw-pointer/JNI entry. The new XAX JNI caller establishes allocated initialized
views, checks the returned byte/count, releases buffers and returns the UI mode.

ADB now connects to the Pixel 8 Pro using the user's platform-tools path.
Eleven direct native cases and five Activity cases passed on Android 17/API 37
ARM64, including both tape bounds, wrapping, loops, EOF, capacity and length
failures, permit/block row visibility and app rejection. The test-signed APK is
35,440 bytes; XAX emitted its 17,432-byte library and 2,104-byte DEX. Device
properties, UI dumps, screenshots, logs and hashes are recorded in evidence.

Twenty-two native self-hosting checks passed: both BF sources were framed by
the native BF framer, three compiler generations produced identical BBX,
canonical graph and 66,504-byte ELF, initial/final compilers matched all eight
fixtures, and the bootstrap module was reproduced. This is BF frontend
self-hosting with an external XAX backend; the XAX compiler host used Python
bootstrap helpers on Windows. Exact host authority and test-transport hashes
are disclosed. No XAX-backend self-hosting is claimed.

Limits: the APK uses a public test certificate. OOM traps before memory access
and terminates the app process. Native self-hosting used 65,536-byte buffer
views, which fit the canonical sources but not the full 65,538-byte maximum
general source frame. Linux native execution and its native frontend cycle
remain unverified. Historical backend claims in the recovery
archive are not current pipeline evidence. The retired legacy suite was not rerun.

Windows now passes 22 native checks: 11 decision/profile cases from actual BF
frontend output, three exact BBX/graph/PE compiler generations, and eight
frontend fixtures. Its decision DLL is 8,704 bytes and compiler DLL is
701,952 bytes. XAX's existing backend now supports the needed narrow wrapping
arithmetic and proven pointer parameters, and probes large Windows stack
frames in both hosted lowering paths. Regression coverage includes 36 narrow
arithmetic cases and a 128 KiB frame in a fresh process. The focused pytest
run passed 45 tests and 158 subtests; 12 environment-dependent tests skipped.
The Android library, DEX and both stores remain byte-identical after adding
target selection. This is native Windows component proof, not a GUI app.
Linux execution remains unverified because no Linux host is available.
