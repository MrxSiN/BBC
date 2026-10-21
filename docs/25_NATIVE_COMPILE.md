# Native source-to-executable compilation

**IMPLEMENTED and EXECUTED in emulated hosts, MEASURED under Wine, 2026-10-21.**
`bbc compile` turns Brainfuck source into an Android ARM64 or Windows x86-64
executable with native XAX code only: no Python, interpreter or foreign compiler
logic runs at any stage. [Raw evidence](../evidence/native_compile.json) records
stores, transactions, hashes, the differential campaign and timing samples.
BBC's twelve Brainfuck instruction streams, the BFX format, optimization levels
and fixtures are unchanged; all new executable work is canonical XAX.

The [XAX implementation](https://github.com/MrxSiN/XAX/blob/19d899db0db6503b37b1dfc8a1967d7b2798862f/compiler/integration/bfx/COMPILE.md#native-source-to-executable-compilation--2026-10-21)
is pinned to its tested commit.

## Use

Put `bbc.exe`, the native XAX driver as `xaxc.exe` and the host requests
`bbc-android-arm64.xax` and `bbc-windows-x86_64.xax` in one directory, such as
ignored `build/`. Then:

```text
build\bbc.exe compile android-arm64 -O1 program < program.bf
build\bbc.exe compile windows-x86_64 program.exe < program.bf
```

O1 is the default. Source is raw binary stdin; output paths are relative to the
working directory. Besides the executable, `<output>.xax` (the verified build
snapshot) and `<output>.provenance` remain. On any failure the executable,
snapshot and provenance are deleted. Exits: 0 success, 1 invalid source,
2 resource limit, 3 I/O or driver start failure, 4 usage or internal failure,
5 the native backend rejects or declines the program for that target.
`bbc bind` exposes the intermediate binding record for inspection.

## Pipeline

1. In one `bbc.exe` process: `stream_chunks.bf`, `stream_runs.bf` and
   `optimize.bf` through the unchanged `compile_bfx`; the unchanged strict
   decoder and importer; then a new canonical framing function turns the
   imported decision store into one expected-root edit record.
2. `xaxc edit` binds the decision into the target's host build request,
   recomputing every supplied CID and verifying the result.
3. `xaxc resolve` produces the build snapshot.
4. `xaxc build` performs mandatory first verification, lowering and packaging.

`bbc.exe` starts steps 2 to 4 with `CreateProcessW` and checks each exit. First
verification of everything the record supplies remains in the driver; the record
itself is never trusted.

## Native backend change

Windows builds of decisions the lowering view does not inline (over 256 nodes,
for example O0 hello or the depth-512 programs) previously rejected with
`NATIVE-CALL-ARITY` `[5,4]`. A canonical XAX driver transaction ports the AArch64
frame path's elision of borrowed views a callee gives back to the x86-64 frame
path. All 141 existing driver regression and declared-rejection stores keep
identical verification results, diagnostics, artifacts and provenance.

## Executed checks

- The native records for both depth-512 programs equal the Python-made Android
  binding fixtures byte for byte; the native edit plus the reference snapshot
  recipe reproduces the Android regression snapshot exactly.
- The single command reproduces the earlier native-driver artifacts executed on
  Windows 11 and Pixel 8 Pro for hello, nested_math and checksum_four on both
  targets, and the depth-512 Android artifact.
- 83 programs (pinned pilot programs, BBC tests, both depth-512 programs, the
  required negative loops under five initial values, 60 seeded random programs
  and capacity cases), O0 and O1, both targets: 332 builds and 588 executions,
  all matching an independent interpreter in output bytes and exit status.
  Inputs for which that interpreter did not terminate within its fuel are not run.

Android artifacts ran under `qemu-aarch64` user emulation and Windows artifacts
under Wine 9.0 on Linux x86-64. That is not device or Windows execution; the
byte identity with previously device- and Windows-executed artifacts is what
links these runs to real targets. New artifacts beyond those identities still
need execution on a Pixel and on Windows.

## Measurement

Fresh processes, one Linux x86-64 host, one warmup and ten alternating scored
trials per case. The previous arm runs the generic Python SDK binding,
verification, lowering and packaging from the native record, so it excludes the
frontend and import that it originally also ran.

| Complete Android build, median seconds | Native `bbc compile` under Wine | Previous Python SDK path |
|---|---:|---:|
| hello | 0.245 | 1.271 |
| nested_math | 0.247 | 1.238 |
| checksum_four | 0.237 | 1.236 |
| deep_nesting_512 O1 | 0.853 | 11.218 |

Both arms produce identical artifacts. A Wine process launch costs about
0.044 s on this host and `bbc compile` launches four. Stage medians are bind
0.050, edit 0.065, resolve 0.069 and build 0.075 s, each including one launch.

| Metric | Previous BBC | Native BBC | Brainfry | Result |
|---|---|---|---|---|
| Complete build latency | Frozen 1.46–1.58 s Windows; 1.24–1.27 s on this host | 0.24–0.25 s under Wine | Frozen 23–24 ms Windows | BBC faster than before; no new Brainfry verdict |
| Runtime latency | Not remeasured | Not remeasured | Not measured | No verdict |
| Compiler RAM | Not remeasured | Not measured | Not measured | No verdict |
| Executable size | Unchanged artifacts | Identical bytes | Earlier corpus differs | Tie with previous BBC |
| Large workload | Not remeasured | Not measured | Not measured | No verdict |

These timings are not Windows-native and carry no competitor verdict. The
remaining costs are four process launches, re-verification of the host request
in each driver step and the driver's fixed views. Merging bind, edit, resolve
and build into one verified driver process is the next build-latency step; the
fixed 3,550,558,208-byte driver view declarations remain. M4 and M8 remain open.

## Bootstrap finding

The generic bootstrap's Windows PE lowering of the new `bbc.exe` entry lost
scalar values carried from early blocks across later loops and calls, although
each had one definition in the verified graph. The entry keeps process scalars
in its own view and fetches standard handles where it uses them. The defect is
in the disclosed bootstrap backend, which `bbc.exe` still needs; the native
driver used for program builds is not affected.
