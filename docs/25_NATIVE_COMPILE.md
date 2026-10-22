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

Put `bbc.exe` and the host requests `bbc-android-arm64.xax` and
`bbc-windows-x86_64.xax` in one directory, such as ignored `build/` (the
[single-process](#single-process) `bbc.exe` contains the driver; the earlier
four-process build also needs the driver as `xaxc.exe`). Then:

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

## Single process

**IMPLEMENTED, EXECUTED and MEASURED under Wine, 2026-10-21.** `bbc.exe` now holds
BBC's commands and the whole native XAX driver in one canonical program
([XAX source](https://github.com/MrxSiN/XAX/blob/1af64bff46723b54a132a9586a82f9a0fa527534/compiler/integration/bfx/COMPILE.md#single-process-compilation--2026-10-21)),
so `bbc compile` starts no helper process. After the in-process front writes
`<output>.edit`, it calls the driver's entry three times. Each call uses a
variant whose argument helpers produce that step's command line and whose final
`ExitProcess` is `SetLastError`, so the status returns to `bbc.exe`. Every step
still verifies its inputs. Install only `bbc.exe` and the two host requests.
`bbc.exe` also answers the driver's own commands (`verify`, `build`, ...).
[Raw evidence](../evidence/native_single_process.json) records the stores,
hashes and samples.

- 332 builds and 588 executions match the independent interpreter; all 332
  artifacts equal those of the four-process pipeline.
- Driver commands through `bbc.exe` match the driver PE byte for byte on 141
  regression and declared-rejection stores.
- Error paths exit 1, 4, 4, 3 and 3 for invalid source, target, level, a
  missing host request and a missing output directory, and leave no files.

| Complete Android build, median of 10 (s) | Single process | Four processes | Python SDK path |
|---|---:|---:|---:|
| hello | 0.110 | 0.271 | 1.409 |
| nested_math | 0.113 | 0.272 | 1.347 |
| checksum_four | 0.111 | 0.275 | 1.444 |
| deep_nesting_512 O1 | 0.883 | 0.993 | 13.094 |

This run's host was somewhat slower than the earlier one, so compare arms
within the table. One Wine launch (about 0.044 s) remains. These are not
Windows-native times and give no Brainfry verdict. The remaining small-build cost
is three driver entry runs, each committing the driver's fixed views and
re-reading and re-verifying its inputs; handing verified stores between steps
in memory is next. [Lazy views](#lazy-views) revises this plan.

## Lazy views

**IMPLEMENTED, EXECUTED and MEASURED under Wine, 2026-10-22.** `bbc.exe` no longer
commits the driver's 3,550,558,208 bytes of views up front
([XAX source](https://github.com/MrxSiN/XAX/blob/5091cb44a86f3fa70ff29340bf7badf9bc891bb1/compiler/integration/bfx/COMPILE.md#lazily-committed-driver-views--2026-10-22)).
The driver's 17 views of at least 1 MiB that never reach the C runtime are
reserved instead, and so are the front's 512 MiB importer arena and 16 MiB
record view. One vectored exception handler commits the touched 1 MiB slice of
such a reservation, zero-filled, and resumes. It acts only on reservations
marked `PAGE_NOACCESS`; any other fault still ends the process. The views that
file and argument calls write into stay committed. View types, extents, proofs
and verification are unchanged. [Raw evidence](../evidence/native_lazy_views.json)
records stores, hashes and samples.

- 332 builds and 588 executions match the independent interpreter; all 996
  output files equal those of the previous `bbc.exe`.
- Driver commands match the previous `bbc.exe` byte for byte on 141 stores.
- Error paths still exit 1, 4, 4, 3 and 3 and leave no files.

| Complete Android build | Peak commit before (MiB) | Now (MiB) | Median before (s) | Now (s) |
|---|---:|---:|---:|---:|
| hello | 3,398 | 67–98 | 0.100 | 0.100 |
| nested_math | 3,398 | 67–74 | 0.096 | 0.097 |
| checksum_four | 3,398 | 66–88 | 0.093 | 0.096 |
| deep_nesting_512 O1 | 3,398 | 117–131 | 0.676 | 0.652 |

Commit is the peak of the Wine process's private writable mappings over three
runs, not a Windows counter. Latency is unchanged.

### Step handoff

For hello, a Wine relay timeline gives front 3 ms, edit 10 ms, resolve 10 ms
and build 23 ms. File reads and writes take under 1 ms per step. About 8 ms of
each step is the first full verification of a different store, since edit does
not verify its output and resolve does not verify its snapshot. Build adds about
14 ms of lowering and packaging. Passing the files in memory would save under
1 ms, so it was not done, and verification may not be skipped. The remaining
latency step is a per-process proof cache, keyed by CID, inside the XAX
driver's verifier.
[Graph proof cache](#graph-proof-cache) takes that step.

## Graph proof cache

**IMPLEMENTED, EXECUTED and MEASURED under Wine, 2026-10-22.** The three driver
steps of one `bbc compile` now check each graph once
([XAX source](https://github.com/MrxSiN/XAX/blob/841e6d8f85dca72b78ce35b92582642f6491c9c4/compiler/integration/bfx/COMPILE.md#graph-proof-cache--2026-10-22)).

Profiling hello's steps showed:
- verification was about half of the driver's machine time and lowering 40%;
- the typing program was about 60% of verification;
- the host request, request and snapshot share their graphs, types and
  constants.

Before checking a graph, a step looks up its CID among graphs an earlier step
of the same process accepted ordinarily.

- **Hit:** the step replays that graph's recorded pointer extents and trap
  heads, which the build step's lowering reads, and its acceptance state.
- **Miss:** the step checks the graph as before and records an ordinary
  acceptance.

Object CIDs, type and constant checks and store-level checks still run in every
step. [Raw evidence](../evidence/native_proof_cache.json) records stores, hashes,
profiles and samples.

- 332 builds and 588 executions match the independent interpreter; all 996
  output files equal those of the previous `bbc.exe`.
- Driver commands match the previous `bbc.exe` byte for byte on 141 stores.
- Error paths still exit 1, 4, 4, 3 and 3 and leave no files.
- Typing-program time falls 41% for hello and 38% for deep_nesting_512.

| Complete Android build | Median before (s) | With cache (s) | Change |
|---|---:|---:|---:|
| hello | 0.113 | 0.109 | −3% |
| nested_math | 0.100 | 0.097 | −3.5% |
| checksum_four | 0.103 | 0.096 | −6.6% |
| deep_nesting_512 O1 | 0.690 | 0.639 | −7.5% |

These are 20 alternating trials per case under Wine. Host stalls that hit both
arms in about half of nested_math's trials are excluded and counted in the
evidence. They are not Windows-native times and give no Brainfry verdict.
Build's lowering is now the largest remaining cost.

## Bootstrap finding

The generic bootstrap's Windows PE lowering of the new `bbc.exe` entry lost
scalar values carried from early blocks across later loops and calls, although
each had one definition in the verified graph. The entry keeps process scalars
in its own view and fetches standard handles where it uses them. The defect is
in the disclosed bootstrap backend, which `bbc.exe` still needs. A first
single-process front with its loops inline hit the same class: a loop-carried
view pointer shared a spill slot, so the record copy read a wrong pointer. The
front is now loop-free, with its two loops in small helpers. Driver code is
unaffected and keeps byte-identical behavior.
