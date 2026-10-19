# BBC integration with XAX

The maintained XAX sources are pinned to revision
[`ac7821c9bf9c1bde0c18f00da6d1a60a3b320816`](https://github.com/MrxSiN/XAX/commit/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816).
The local checkout is `D:\GitHub\XAX`; the links below also work without that
checkout. BFX v1 is governed by [BFX_CONTRACT.md](BFX_CONTRACT.md), and generated
decisions follow [BRAINFUCK_PROFILE.md](BRAINFUCK_PROFILE.md).

## Source and responsibility

| Canonical XAX source | Responsibility |
|---|---|
| [bfx.xax](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/bfx.xax) | Validate records and compute matching loop indices |
| [import_bfx.xax](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/integration/bfx/import_bfx.xax) | Emit, hash, sort and serialize a complete native decision store |
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

## Android application

Package: `org.bbc.bfxdecision`. Activity: `.DecisionActivity`.
Integer Intent extras: `flag` (default 0), `capacity` (default 1).
The native caller allocates distinct initialized input/output/tape views,
executes the compiled decision, validates the result and releases its buffers.
The managed XAX UI displays the result and shows or hides a sample row.

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

## Host tools and evidence scope

Native importer/frontend execution occurs on Android and Windows. Canonical
verification, reference-transaction application, native lowering, DEX/APK
packaging and signing use unchanged generic Python bootstrap tools on Windows.
`XAX_REQUIRE_NATIVE` was unset; these results do not establish an Android-hosted
XAX compiler or whole-toolchain source purity. External ctypes and NDK C test
transports allocate buffers, move bytes and call exports; they provide no
production parsing, import algorithm or Brainfuck interpreter.

The tested Android transport is `C:\platform-tools\adb.exe`, with development
files under `/data/local/tmp/bbc_bfx_20261019`. Generated host artifacts stay
outside tracked source, normally in ignored `build/` or an external directory.
[STATUS.md](STATUS.md) is the current evidence index and remaining-work list.
