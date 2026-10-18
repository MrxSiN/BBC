# XAX integration

Status: EXECUTED on Android ARM64, 2026-10-18. A real XAX-built Activity invokes
the native Brainfuck decision and visibly acts on its byte result. The BF
frontend also completed its native self-hosting cycle with an external XAX
backend. Windows native components also execute; Linux has no available host.

The separate repository is `D:\GitHub\XAX`. Its importer is local commit
`2ce6797782532a08f7938d8db6a2e881c013d3e9`; the Android caller/app is local
commit `fa516f2bbab1036905e17df4039eb40f91917da9`. The pre-existing modified XAX
README was left untouched. Remote publication still awaits authorization
after automatic approval review rejected the earlier push.
Windows support is local commit `51bb251aff4abfe340901960b150eb11dc2a9a50`.

## Portable module and typed core

`compiler/src/xax_bbx.py` validates BBX magic/version/status/exact length,
instruction bytes, brackets and supported limits, then uses XAX's existing
`GraphBuilder` and `program_store` to construct and verify a canonical graph.
It consumes compiler output; source filtering/validation remain Brainfuck.
Subsequent graph edits must use XAX workspace transactions. No textual XAX
syntax or runtime opcode-fetch loop is introduced.

The graph zeroes all 65,536 tape cells per valid call, lowers instructions to
native checked byte operations and control-flow branches, wraps bytes, reads
zero after EOF, and checks both tape bounds and output capacity.

The internal call borrows distinct initialized input/output/tape view triples
(pointer, extent-bearing ownership proof, memory frontier), followed by u32
input length and output capacity. Extents are fixed at construction, at most
65,536 bytes. All triples return with updated memory frontiers; XAX erases
proof and borrowed pointer returns from the native ABI. The scalar result is
`(output_length << 32) | status`: 0 success, 1 tape bounds, 2 output capacity,
3 invalid logical lengths. Callers discard any output prefix on failure.

This is a typed XAX call, not an untrusted raw-pointer/JNI interface. Its caller
must establish the allocations, initialized views, non-aliasing and lifetimes.
The scratch tape may be reused because every valid call resets it.

## Android application

`compiler/src/xax_bbx_android.py` constructs the native JNI caller and managed
UI graphs. The native caller obtains three distinct zeroed allocations from
Bionic calloc, writes the input flag, directly calls the decision, checks its
status/count/byte, then releases all buffers. The managed graph reads Intent
extras, calls JNI and shows/hides a sample row. XAX emits the native ELF,
JVM-to-DEX code, binary manifest and APK. The small platform class shell only
loads the library and forwards onCreate; application behavior is in XAX.

| Input | Capacity | Native outcome | Visible application action |
|---|---|---|---|
| 0 | 1 | Success, byte 01 | PERMIT label and visible sample row |
| 1 or 255 | 1 | Success, byte 00 | BLOCK label and hidden row |
| 0 | 0 | Output exhausted | ERROR label and hidden row |
| 256 | 1 | Invalid application input | ERROR label and hidden row |

The sample accepts flags 0..255 and capacity 0..16. Unexpected output/count
also fails closed. Allocation failure uses XAX's existing null-heap trap before
memory access; OOM terminates the process rather than returning a status.
The APK uses XAX's public **test certificate**, never a production signing key.

With XAX `compiler/src` on PYTHONPATH, run from its `compiler/` directory:
`python -m benchmarks.android_bbx_app module.bbx output-directory`.
It saves the verified native/managed stores, library, DEX and test-signed APK.
The BBC artifact is `build/bbx/android/bbx-decision.apk` (35,440 bytes).

Install with `D:\Android\platform-tools\adb.exe install -r` and the APK path.
Launch using ADB `shell am start -S -W -n
org.bbc.bbxdecision/.DecisionActivity --ei flag 0 --ei capacity 1`.
Use flag 1 for block or capacity 0 for error. Generated artifacts, screenshots,
UI hierarchies and logs remain ignored under `build/bbx/`.

## Executed evidence

- [Android device evidence](../evidence/bbx_android.json): Pixel 8 Pro, Android
  17/API 37, native arm64-v8a; 11 direct native checks and five Activity cases.
  Exact UI text, row visibility, screenshots, logs, device properties, sources,
  external transports, compiler-host authority and artifact hashes are recorded.
- [Native frontend cycle](../evidence/bbx_selfhost_android.json): 22 checks,
  including native BF framing and three exact BBX/graph/ELF rebuild generations.
  See [BOOTSTRAP.md](BOOTSTRAP.md) for scope and component buffer limits.
- XAX checks: 27 of 30 unittest methods passed; three existing platform-dependent
  methods skipped. The new four caller tests include 15 ARM64 cases covering
  input/error paths, allocation release and precise null-allocation traps.
- [Earlier integration evidence](../evidence/bbx_xax_integration.json): 29 core
  ARM64 emulations and 13 additional real-BBX integration checks. This remains
  a historical simulation result, superseded by device execution for Android.

The Windows compiler host used Python bootstrap helpers. Evidence discloses
`xax_native.AUTHORITY`; `XAX_REQUIRE_NATIVE` was not enabled. Actual generated
machine code executes on Android, while the XAX backend itself is external.
The combined two-project toolchain is not Brainfuck-only. No foreign
implementation or executable testing tool was added to the BBC repository.

## Windows component

Pass `target_object=x86_64_windows_pe_target()` to `construct_bbx` in XAX,
then use its existing native lowering and `xax_pe.emit_pe_dll`. The graph and
BBX contract are shared with Android. XAX now masks narrow wrapping arithmetic,
accepts proven pointer parameters and probes large Windows stack frames.
No BBC backend was introduced.

[Windows evidence](../evidence/bbx_windows.json) records 22 native checks:
11 real-BBX decision/profile cases, three identical BBX/graph/PE frontend
generations and eight exact frontend fixtures. The decision DLL is 8,704 bytes;
the compiler DLL is 701,952 bytes. External ctypes supplies valid buffers to
the internal Win64 component; it contains no source compiler or BF VM. This
proves native component execution, not a Windows GUI application.

The focused pytest run passed 45 tests and 158 subtests; 12 environment-dependent
tests skipped. Windows regression cases include narrow arithmetic, invalid
lengths and a 128 KiB frame in a fresh process. Android library/DEX/stores are
unchanged after target selection was added. Native Windows execution of the
BF bootstrap framer itself was not tested.

Linux x86-64 still needs an execution environment: WSL is absent, and the user
confirmed no Linux host is available. Historical legacy claims are not current
pipeline evidence. No native Linux execution or speed advantage is claimed.
