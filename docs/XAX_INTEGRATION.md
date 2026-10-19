# BFX and XAX integration

The XAX implementation is maintained in `D:\GitHub\XAX`. Its canonical
BFX stores provide record decoding, decision-store emission and an Android
application.

## Canonical XAX implementation

`compiler/integration/bfx/bfx.xax` is the authoritative BFX decoder.
It was authored through the existing `xax-construct-v1` construction interface,
verified and saved through `Workspace.save`. There is no new Python builder
or textual XAX substitute in either repository. Subsequent semantic changes
must use expected-root workspace transactions.

The graph checks magic, binary version, successful status, exact record
length, 3,840-instruction and 255-nesting limits, all eight payload opcodes
and balanced brackets. It writes matching loop indices into caller-supplied
scratch memory. Records with unsupported magic are rejected. It does not execute Brainfuck
or generate a decision graph. See the XAX-side `compiler/integration/bfx/README.md`
for its exact typed ABI, statuses, native exports and static test data.

The same decoder function executed 393 cases as a Windows x86-64 DLL and
393 cases as an Android ARM64 shared library on the connected Pixel 8 Pro,
Android 17/API 37. Tests compare error results and loop pairs, preserve input
bytes and check a scratch-buffer canary. External C on Android only supplies
buffers, calls the exported function and transports bytes; it implements no
BFX validation, graph import or Brainfuck execution.

ADB is `C:\platform-tools\adb.exe`. This iteration's files on the phone are
under `/data/local/tmp/bbc_bfx_20261019`. Generated host artifacts stay in
ignored `build/bfx/` or the external verification directory. Evidence and
tool hashes are in [bfx_migration.json](../evidence/bfx_migration.json).

## Native BFX graph/store emitter

`compiler/integration/bfx/import_bfx.xax` now implements the complete record-
dependent import algorithm: decoder call, native operation/control-edge
emission, semantic hashes, canonical record sorting and store serialization.
Its source is the saved canonical graph, authored with the existing
GraphBuilder/Proc construction interface, verified and tested before publication.
The maintained import algorithm is canonical XAX.

The native importer passed 393 record cases on Android and Windows, plus
89 emitted native Windows decision calls. Android compiler, framer and
decision outputs imported to the same canonical bytes as the Windows
reference. Input bytes and canaries on all four buffers were preserved.
Three frontend generations on each platform reproduced identical BFX, stores
and native libraries. Android also passed eight exact fixtures per generation.

The hash implementation uses a 16-byte mixing result and explicit chaining
words at scratch bytes 1760..1791, within the existing 2048-byte scratch view.
This stays within the target frame limit and avoids the general ARM64
large-composite return-copy defect, tracked in XAX OI-49. No generic backend
source changed. The maintained store was changed by an exact-root reference
transaction, verified and saved through the XAX workspace interface.

The generated decision views remain fixed at 65536 bytes; the importer borrows
64 MiB of serialization/output workspace. Exact ABI and bounds are documented
in XAX's `compiler/integration/bfx/IMPORT.md`. Current results and hashes are in
[Android and Windows import evidence](../evidence/bfx_android_importer.json).
Native lowering and canonical verification use unchanged Windows-hosted Python
bootstrap tools; the XAX compiler host does not execute on Android.

The decision ABI remains the documented profile: distinct initialized input,
output and 65,536-byte tape views; fresh zero tape per call; wrapping bytes;
EOF zero; immediate tape and output-capacity failures. The internal native
result is `(output_length << 32) | status`, with statuses 0 success, 1 tape
bounds, 2 output capacity and 3 invalid logical lengths. This is distinct
from decoder errors. Callers must establish ownership, lifetimes and
non-aliasing, and discard any output prefix on failure.

## Android application

The maintained app store `compiler/integration/bfx/android_bfx.xax` contains
native evaluation, a JNI lifecycle bridge, managed XAX UI, the standard
managed-class carrier, manifest and package/build metadata. It uses the new
BFX importer output and no Python BFX builder. Generic native/JVM-to-DEX
lowering and APK packaging produce the application; the separate UI DEX is
linked through those existing tools. Eight permit/block/error Activity cases
passed on Pixel 8 Pro. Generic arithmetic and large-stack regression checks
execute from `backend_tests.xax`. The build host uses unchanged Python
verification, native/JVM-to-DEX lowering, APK and signing utilities.
See [application evidence](../evidence/bfx_retirement.json) and XAX's
`compiler/integration/bfx/ANDROID.md` for exact linkage, dependencies and limits.
