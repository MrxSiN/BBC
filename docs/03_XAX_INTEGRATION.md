# BBC integration with XAX

The decoder and application baseline sources are pinned to revision
[`ac7821c9bf9c1bde0c18f00da6d1a60a3b320816`](https://github.com/MrxSiN/XAX/commit/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816).
The current importer is pinned to [revision `7761cf2`](https://github.com/MrxSiN/XAX/commit/7761cf24218472c459c3491dcf7570263bc3b373)
with its [reset proof and measurements](https://github.com/MrxSiN/XAX/blob/7761cf24218472c459c3491dcf7570263bc3b373/compiler/integration/bfx/WIDE_RESET.md).
The local checkout is `D:\GitHub\XAX`; the links below also work without that
checkout. BFX v1 is governed by [02_BFX_CONTRACT.md](02_BFX_CONTRACT.md), and generated
decisions follow [01_BRAINFUCK_PROFILE.md](01_BRAINFUCK_PROFILE.md).

## Source and responsibility

The standalone Windows host is pinned separately to
[revision `3dcb358`](https://github.com/MrxSiN/XAX/commit/3dcb358e48b0f9a45b8cb72767c1aa600e55cd78).
Its [canonical source and build guide](https://github.com/MrxSiN/XAX/blob/3dcb358e48b0f9a45b8cb72767c1aa600e55cd78/compiler/integration/bfx/WINDOWS_STANDALONE.md)
describe the kernel32-only process interface and required generic bootstrap
lowering configuration. [Windows execution evidence](../evidence/standalone_windows.json)
records 23 native programs, 28 host checks, native binding replay and exact
empty/hello rebuilds. This does not complete the native XAX build driver.

| Canonical XAX source | Responsibility |
|---|---|
| [bfx.xax](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/bfx.xax) | Validate records and compute matching loop indices |
| [import_bfx.xax](https://github.com/MrxSiN/XAX/blob/7761cf24218472c459c3491dcf7570263bc3b373/compiler/integration/bfx/import_bfx.xax) | Emit, hash, sort and serialize a complete native decision store |
| [android_bfx.xax](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/android_bfx.xax) | Native decision caller, JNI lifecycle, managed UI and Android package/build metadata |
| [backend_tests.xax](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/backend_tests.xax) | Arithmetic and large-stack regression checks |

These saved canonical graphs are authoritative source. Initial construction
uses XAX's supported graph facilities; later changes use exact-root verified
transactions and workspace saves. No textual XAX substitute or Python BFX
algorithm is maintained. BBC owns Brainfuck source filtering, validation and
future semantic optimization; XAX owns graph verification, native lowering,
ABIs and platform packaging.

The [numbered BFX guide](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/docs/18_BFX_IMPORT.md) indexes the XAX-side
contracts and static case data.

## Decoder and importer

The decoder checks magic, binary version, successful compiler status, exact
record length, supported instruction/nesting limits, all payload opcodes and
balanced brackets. Its scratch contains loop pairs and a bounded opening
stack. It does not execute Brainfuck or emit a graph.

The importer calls that decoder and emits decision operations/control edges,
semantic hashes and a complete canonical store. Its internal native export is:

`import_bfx(record_pointer, workspace_pointer, output_pointer, hash_pointer) -> u64`

| Buffer | Extent | Caller requirement |
|---|---|---|
| BFX record | 3,847 bytes | Live, initialized, read-only byte view |
| Decoder workspace | 16,380 bytes | Live, initialized, writable byte view |
| Output/serialization workspace | 67,108,864 bytes (64 MiB) | Live, initialized, writable byte view |
| Hash scratch | 2,048 bytes | Live, initialized, writable u32 view, alignment 4 |

All buffers are distinct. Typed arguments include view ownership and memory
frontiers, which return with the call and erase from the native pointer ABI.
Before every invocation, write the logical record length as u32 little endian
to workspace bytes 0..3. The decoder overwrites that request area.

Success returns `store_length << 32`; publish exactly that output prefix.
Failure returns a decoder validation error in the low 32 bits and no successful
store. Other workspace bytes are unspecified. Reinitialize the logical length
before calling again. [Decoder errors](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/README.md)
are separate from compiler response errors and native decision statuses.

Hash chaining words occupy scratch bytes 1760..1791; the digest occupies
1728..1759. Small mixing results and checked scratch outputs keep this program
within the Android target's supported frame/return paths. The general
[ARM64 large-composite return defect, OI-49](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/XAX_OPEN_ISSUES.md#oi-49--android-arm64-large-composite-return-copy)
remains open. The importer avoids that operation; no generic backend source
was changed. [The importer contract](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/IMPORT.md)
documents storage bounds and the recorded semantic transaction.

## Native decisions and rebuild cycle

Generated decisions borrow three initialized, non-aliasing 65,536-byte views
for input, output and tape. Valid calls reset the tape. Their native scalar is
`(output_length << 32) | status`: 0 success, 1 tape bounds, 2 output exhaustion,
3 invalid logical lengths. Callers discard output on failure and establish all
pointer/lifetime preconditions before crossing this internal boundary.

The decoder passed 393 native cases on each of Android and Windows. The
complete importer separately passed 393 cases on each target, plus three real
Android frontend outputs. Android stores matched the established Windows
output byte for byte, preserving input and all four buffer guards. Thirteen
emitted Windows modules passed 89 native decision calls.

Three frontend generations per platform reproduced identical BFX, stores and
target-native libraries. Android passed eight exact frontend fixtures in each
generation. [Current importer/cycle evidence](../evidence/bfx_android_importer.json)
records exact sources, artifacts and external-tool hashes.

The current BBC frontend uses counted source-byte groups and single-copy
opcode decoding, and retains the
65,533-byte source limit so a complete request fits the unchanged input view.
[Windows filter evidence](../evidence/frontend_filter_windows.json) and
[Android filter evidence](../evidence/frontend_filter_android.json) bind
three native generations per target to that source. Android passes twelve
fixtures per generation and seven boundary checks; its stores match Windows
stores byte for byte. The [P0 proof](07_OPTIMIZATION_PROOFS.md) separates this
frontend change from XAX lowering and decision-runtime optimization. No
canonical XAX graph, ABI, format or platform implementation changed.

## Eight-byte decision tape reset

The current importer replaces byte-at-a-time initialization with checked
eight-byte zero stores, retaining alignment one and the complete tape reset.
It changes no Brainfuck source, BFX bytes, public ABI, input/output operation
or movement check. [The exact-root transaction](https://github.com/MrxSiN/XAX/blob/7761cf24218472c459c3491dcf7570263bc3b373/compiler/integration/bfx/wide_reset.edit) derives
from root `108fe27f40ea8b1fffa14426c6ee85bcecb7caef91e2f8313292ec22770badb8`
and produces `6af38cf7dce17eaeb4929a5e3cde770f04996db84026d5c9acb6743a07f4e63e`.

[The new execution report](../evidence/wide_tape_reset.json) retains 393 importer
cases per version/target and 380 decision checks per version/target. All bytes
of the output and tape agree with an independent interpreter; input and guards
are preserved. Three frontend generations on each target have twenty checks
per generation and identical BFX/store/native bytes. The installed Android app
keeps its previously tested embedded module.

Bootstrap verification/lowering use unchanged generic Python utilities.
Separate native-only Windows replay and Android children run with
`XAX_REQUIRE_NATIVE=1`, recording their exact artifact authority. The standalone
Windows driver replays this edit byte for byte, rejects its stale root and
verifies the result. That does not complete the driver's unrelated DLL,
diagnostic-parity, large-edit or self-verification gates.

[Absolute native-call and fresh Android competitor times](08_BENCHMARKS.md#eight-byte-tape-reset)
are a separate experiment. No competitor is surpassed.

## Standalone Android process

The [canonical host](https://github.com/MrxSiN/XAX/blob/5d3a41c649c08974825b9e5b4c199cb6d59b3185/compiler/integration/bfx/standalone_arm64.xax) and
[hello-binding transaction](https://github.com/MrxSiN/XAX/blob/5d3a41c649c08974825b9e5b4c199cb6d59b3185/compiler/integration/bfx/standalone_hello.edit) now package an
imported decision as a complete static executable. The [XAX guide](https://github.com/MrxSiN/XAX/blob/5d3a41c649c08974825b9e5b4c199cb6d59b3185/compiler/integration/bfx/STANDALONE.md)
documents the typed contract and unchanged bootstrap reproduction commands.
The existing AArch64 syscall target executes on Android; no desktop Linux
execution or delivery is claimed. There is no shared-library host or dynamic
loader in this package, and the existing checked decision graph is called
directly without a Brainfuck interpreter.

The host buffers raw stdin to EOF, up to 65,536 bytes, in one of three distinct
owned initialized views. It rejects excess input before execution, preserves
the core's full tape reset and checks status/length before writing successful
output. It retries fragmented reads and partial writes, handles I/O errors and
releases all views. This buffered process transport has no command-line flags.
Language failures discard the core's entire output prefix; physical write
failures may still emit a prefix that callers must discard on nonzero exit.

[Primary evidence](../evidence/standalone_android.json) includes twenty
existing decisions, binary/fragmented and maximum/excess input, actual closed
descriptors, a failure after a written prefix, output overflow and a 65,025-byte
file/pipe output. [Native-only replay](../evidence/standalone_native_replay.json)
runs 23 Android programs and records exact roots and complete ELF digests in
`xax_native.AUTHORITY`, with `XAX_REQUIRE_NATIVE=1`. The Windows native driver
also replays the public binding, verifies the result and rejects a stale root.
Empty and hello executables rebuild byte for byte through unchanged Python
bootstrap utilities. BBC source and BFX bytes are unchanged.

[Fresh process timings](08_BENCHMARKS.md#standalone-android-process) favor BBC
over the pinned Awib configuration on the tested common subset, while brainfry
remains faster. This changes no Windows, compiler-latency, RAM, best-mode or
application claim. The installed Android UI app keeps its previous module.

## Windows native hashing host

A standalone Windows helper host is implemented as a
[canonical XAX graph](https://github.com/MrxSiN/XAX/blob/a31a3560e66d375b5f01fab42c01d52c1faa4962/compiler/integration/windows_helpers/hash_host.xax).
Its [contract and rebuild instructions](https://github.com/MrxSiN/XAX/blob/a31a3560e66d375b5f01fab42c01d52c1faa4962/compiler/integration/windows_helpers/README.md)
are pinned separately from the BFX integration above. It reads raw bytes
through Windows APIs, calls the existing generic XAX BLAKE3 graph and writes
the raw 32-byte digest. Input, scratch and I/O allocations have checked views
and explicit cleanup; no foreign hash algorithm is used by the executable.

[Execution evidence](../evidence/windows_hash_host.json) records 139 successful
native stream cases, five failure cases, an exact-root error-state transaction
and a byte-identical PE rebuild. The host accepts at most 16 MiB. Oversized
input fails without publishing a digest; invalid handles and failed output
are also tested. A separate installed BLAKE3 implementation is used only as
the external test oracle.

This is a standalone native hashing component. The common in-process helper
loader remains unchanged and does not invoke it. The separate driver prototype
below covers the native verifier call chain on tested stores; general coverage
and full-pipeline measurements remain outstanding. The larger general driver
store still exceeds this hashing host's inherited single-input limit.
No new Android execution or whole-toolchain native claim is made.

## Windows native driver prototype

A separate [canonical Windows driver](https://github.com/MrxSiN/XAX/blob/3ddafd26752511d7efbc6ff715e2f4899be93ff2/compiler/integration/windows_helpers/driver.xax)
and [rebuild guide](https://github.com/MrxSiN/XAX/blob/3ddafd26752511d7efbc6ff715e2f4899be93ff2/compiler/integration/windows_helpers/DRIVER.md)
now host the existing XAX compiler call chain as a native PE process. Hashing,
store/graph decoding, CFG, typing and verification run in XAX machine code;
kernel32 and msvcrt provide allocation, arguments, path conversion and files.
The common Python helper loader is unchanged.

[Execution evidence](../evidence/windows_native_driver.json) records 212 store
cases: all 78 reference-valid stores accept; 130 malformed stores reject; four
malformed stores explicitly decline without a validity claim. Accepted real
stores include BBC's compiler, the BFX decoder and both importer variants.
One malformed case receives a different rejection diagnostic from the
reference. Exact diagnostic parity is unmet.

A request resolves byte for byte to the reference snapshot. A small Windows
PE build produces reference-identical executable and provenance bytes, and
its executable runs correctly. Native host-record and small graph-edit replays
are byte-identical; the small edit also rejects its stale root. Windows DLL
packaging, native verification of the corrected driver store and replay of
the large flag edit all decline. Their coverage/limit diagnosis remains open.
Do not call this native self-verification, a compiler fixed point or a complete
native BBC build pipeline.

The port adapts 100 host call sites and adds six canonical Windows adapters.
A verified exact-root transaction captures 522 comparison results as 64-bit
flags in 95 functions to avoid a bootstrap branch-fusion defect. The equivalent
fixed regression graph passes 256 native inputs; the 31 adapter checks and five
driver I/O/path checks pass. The generic Python compiler sources are unchanged.
[XAX OI-50](https://github.com/MrxSiN/XAX/blob/3ddafd26752511d7efbc6ff715e2f4899be93ff2/XAX_OPEN_ISSUES.md#oi-50--x86-64-branch-fusion-loses-cross-block-comparison-values)
and [OI-51](https://github.com/MrxSiN/XAX/blob/3ddafd26752511d7efbc6ff715e2f4899be93ff2/XAX_OPEN_ISSUES.md#oi-51--windows-native-driver-coverage-and-diagnostic-parity)
record the general backend defect and remaining driver gates.

The driver declares 22 views totaling 3,550,558,208 bytes; that budget is not
measured resident RAM. Source and edit-record views are 32 MiB and 16 MiB,
with stricter component limits possible. Its PE is 11,857,408 bytes. Bootstrap
construction, full canonical verification, lowering and PE emission still use
disclosed unchanged Python tools. Native test processes use
`XAX_REQUIRE_NATIVE=1`; the report records native process authority separately
from bootstrap fallback authority. No new Android execution is claimed.

[Fresh-process verification timings](08_BENCHMARKS.md#windows-native-verification-cli)
use a separate same-host paired experiment. They do not change full-pipeline
or competitor measurements.

## Android application

Package: `org.bbc.bfxdecision`. Activity: `.DecisionActivity`.
Integer Intent extras: `flag` (default 0), `capacity` (default 1).
The native caller allocates distinct initialized input/output/tape views,
executes the compiled decision, validates the result and releases its buffers.
The managed XAX UI displays the result and shows or hides a sample row.

This fixed embedded decision is bounded. The current lifecycle/UI call is
synchronous; a worker path for potentially unbounded decision modules has
not been implemented or executed. Do not extend this path to unbounded
Brainfuck on the main thread. XAX's managed callback and pthread facilities
still need a verified graph integration covering worker ownership, JNI
lifetimes, safe UI delivery and cleanup before such a claim.

The eight executed Activity cases are:

| Flag | Capacity | Expected UI |
|---|---|---|
| 0 | 1 | PERMIT, row visible |
| 1 | 1 | BLOCK, row hidden |
| 255 | 16 | BLOCK, row hidden |
| 0 | 0 | ERROR, row hidden |
| 256 | 1 | ERROR, row hidden |
| 0 | 17 | ERROR, row hidden |
| -1 | 1 | ERROR, row hidden |
| 0 | -1 | ERROR, row hidden |

These run on Pixel 8 Pro, Android 17/API 37. The application embeds the compiled
decision; it contains no runtime importer or Brainfuck interpreter. Generic
native/managed-class lowering produces the library and platform DEX. A separate
XAX JVM-to-DEX lowering supplies UI DEX; generic APK packaging links both DEX
files. The single APK build request alone does not include that UI DEX.
Development APKs use the existing public test signing fixture.

[Application evidence](../evidence/bfx_retirement.json) records device/UI results
and source hashes. The [XAX Android guide](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/ANDROID.md)
describes exact linkage and build steps. `backend_tests.xax` passes 36 narrow
arithmetic checks and a fresh-process 128 KiB stack probe.

The capacity iteration also re-executed all eight Activity cases on the same
Pixel 8 Pro. The installed APK hash matched the earlier application evidence;
UI hierarchies again confirmed each label and row visibility. That follow-up
is recorded in [Android capacity evidence](../evidence/source_capacity_android.json).

## Host tools and evidence scope

Native importer/frontend execution occurs on Android and Windows. For the
recorded frontend and application cycles, canonical verification,
reference-transaction application, native lowering, DEX/APK
packaging and signing use unchanged generic Python bootstrap tools on Windows.
`XAX_REQUIRE_NATIVE` was unset; these results do not establish an Android-hosted
XAX compiler or whole-toolchain source purity. External ctypes and NDK C test
transports allocate buffers, move bytes and call exports; they provide no
production parsing or import algorithm. The separate independent .NET seed
interpreter executes BBC only for bootstrap and reference checks. The external
P0 timing transport uses NDK Clang 19 and monotonic clocks around complete
native calls, with output validation outside the timed interval; it is not
linked into a delivered application.

The tested Android transport is `C:\platform-tools\adb.exe`, with development
files under `/data/local/tmp/bbc_bfx_20261019`. Generated host artifacts stay
outside tracked source, normally in ignored `build/` or an external directory.
[05_STATUS.md](05_STATUS.md) is the current evidence index and remaining-work list.
