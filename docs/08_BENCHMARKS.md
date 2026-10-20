# BBC compared with other Brainfuck compilers

A fresh current-format [modernization baseline](20_MODERNIZATION.md) records
180 builds and separate stage/resident/commit results. The older measurements
below retain their pinned source/format identities. The three-source fresh
subset establishes no general competitor victory or post-change speedup.


> Format migration note: measurements and source identities below describe their
> pinned pre-migration snapshots. Historical version names identify that evidence,
> not current decoder modes. Current production uses only [BFX](02_BFX_CONTRACT.md).
> No migration performance or broader completion claim follows from these reports.


The latest [v4 movement report](15_V4_BENCHMARKS.md) measures complete
builds, memory, file size and standalone processes on both targets, retaining
the twelve original programs and four preregistered clear-loop workloads. Separate
native-call A/B results isolate BBC execution costs. The preceding complete
build/resource and Android process comparisons below remain unchanged.
The overall competitive goal is
**NOT YET ACHIEVED**.

Tables use elapsed time, memory and file bytes: **lower is better**.
One millisecond (ms) is one thousandth of a second. One MiB is 1,048,576 bytes.
These are small-program comparisons of pinned configurations, with retained
holdouts. They do not establish best-mode, sustained-computation or real-app
superiority.

The [SDK and Brainfry analysis follow-up](09_BRAINFRY_ANALYSIS.md) clears
Brainfly's .NET SDK blocker and verifies all twelve Windows corpus programs
in JIT and generated NativeAOT modes. It also reproduces Brainfry optimizer
correctness defects outside the scored corpus. These are setup/correctness
results, not new competitor scores. BBC's capacity-flag frontend has
separate [Android/Windows A/B evidence](07_OPTIMIZATION_PROOFS.md#p0-carry-triggered-capacity-flag);
the complete-build and process tables below are unchanged.

## Build latency, RAM and Windows standalone

Measured on **2026-10-20**. Both targets are built on the Windows Ryzen 9 5900HS
host; Android programs run on the Pixel 8 Pro. The [complete report](../evidence/build_runtime_resources.json)
contains the frozen plan, exact sources/inputs, artifact hashes, raw samples,
per-program quartiles, exploratory intervals and calibration data.

BBC's current Windows build pipeline takes longer and records higher sampled
resident-memory peaks than these competitors. Windows process-time differences
are small and inconclusive; these runs do not establish a runtime lead.

### Time to build a complete standalone program

This starts a fresh required build process and ends after the executable is
written and the build process exits. BBC runs its native frontend and native
XAX importer, then uses unchanged generic Python verification, binding and
native lowering. Awib translates to C and invokes the optimizing C compiler
and linker. Brainfry runs its native AOT compiler directly. Compiler bootstrap,
SDK installation, device deployment and APK packaging are excluded equally.

| Build for | BBC (ms) | Awib (ms) | brainfry (ms) |
|---|---:|---:|---:|
| Windows x86-64 | 986.982 | 137.309 | 14.799 |
| Android ARM64 | 886.699 | 750.419 | 15.195 |

Each compiler has thirty timing builds per source/target: ten in each of
three separate runs, plus one excluded warmup per run. The table averages
the twelve per-program medians, giving every program equal weight. All 2,160
timed builds check successful completion and reproduce the validated executable
hash. OS/file caches are warm; “fresh” describes process startup.

### Windows standalone execution, including startup

| Program runs on | BBC (ms) | Awib (ms) | brainfry (ms) |
|---|---:|---:|---:|
| Windows x86-64 | 14.396 | 13.784 | 14.938 |

BBC averages 0.611 ms more than Awib and 0.542 ms less than brainfry. Both
exploratory comparison intervals include faster and slower outcomes, so the
small differences above do not establish an advantage over either compiler.

These are complete executables with binary stdin/stdout. BBC needs no separate
decision DLL or fixed test host. The native timer covers detached process
creation, output consumption and completion. Input/pipe preparation and oracle
comparison are outside the timer for every arm; no overhead is subtracted.
All 1,080 timed invocations check exact output and exit status. Each cell again
averages twelve medians of thirty trials, across three runs.

### Peak resident memory while running

| Program runs on | BBC (MiB) | Awib (MiB) | brainfry (MiB) |
|---|---:|---:|---:|
| Windows x86-64 | 8.639 | 8.806 | 8.637 |
| Android ARM64 | 1.199 | 3.205 | 1.192 |

Each trial measures a whole process lifetime. Windows uses the kernel's
[peak working-set counter](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters)
on the retained process handle after exit. Android uses the waited child's
[maximum resident set](https://man7.org/linux/man-pages/man2/getrusage.2.html)
in KiB, converted to bytes. Each table cell averages twelve per-program
medians of thirty peaks. The two OS counters include shared resident mappings
and startup; they are not PSS, program-only allocation sizes or directly
comparable cross-OS accounting. Android collector self-memory is retained as
a diagnostic; small values near a launch floor cannot isolate program-only RAM.

### Resident memory during a complete build

| Build for | BBC (MiB) | Awib (MiB) | brainfry (MiB) |
|---|---:|---:|---:|
| Windows x86-64 | 104.938 | 45.932 | 8.528 |
| Android ARM64 | 111.714 | 71.489 | 8.580 |

These are **sampled peaks of the simultaneous resident sum across the entire
live build process tree**, including required coordinators and child tools.
Memory trials are separate from timing trials: four per source/compiler/target
in each of three runs, or 864 profiled builds. Each cell averages twelve
per-program medians of twelve measured peaks; individual maxima and quartiles
are retained in the report. Shared DLL pages can be counted
in more than one process. Sampling targets approximately 1 ms; the largest
observed gap was 7.131 ms. Brief peaks or short-lived descendants can be
missed, so these are lower bounds to the true
peak resident sum. They cannot prove memory parity or a general RAM victory.
BBC’s prototype coordinator retains initialized ABI buffers, including the
64 MiB importer workspace, through its build function; these are actual
pipeline measurements, rather than a minimum memory requirement.

### Peak committed memory during a complete build

| Build for | BBC (MiB) | Awib (MiB) | brainfry (MiB) |
|---|---:|---:|---:|
| Windows x86-64 | 91.759 | 27.398 | 1.552 |
| Android ARM64 | 98.793 | 13.035 | 1.548 |

Windows also records the job's kernel-maintained
[peak committed memory](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)
across the complete build tree. It measures committed backing, rather than
resident physical memory, and is separate from the sampled table above.
These builds all run on Windows, including the Android-target rows. Each
cell averages the twelve per-program medians of twelve independent memory
trials. Declared tape/workspace capacities and executable size are not used
as RAM measurements.

### Complete Windows executable size

| Compiler | Smallest–largest file (bytes) | Average file (bytes) |
|---|---:|---:|
| BBC | 9,216–101,376 | 38,827 |
| Awib | 111,104–115,200 | 114,517 |
| brainfry | 2,560–5,120 | 3,072 |

Each compiler contributes twelve complete executables. Shared OS libraries
are excluded equally. Awib's new Windows configuration links its static C
runtime; this differs from the older GCC pilot and does not select the best
compatible Awib mode.

### Configuration and limits

- The frozen sources, inputs, holdouts and expected outputs match the original
  pilot. Awib and brainfry retain their exact source revisions; their compiler
  binaries were rebuilt with the recorded tool versions.
- Windows Awib uses Clang 19 with `-O3 -funsigned-char`, MSVC 14.44 linking and
  a generic binary-stdio object. Android uses the same NDK Clang 19 setup as
  before. Brainfry uses its locked release build and native target modes.
- BBC's [Windows host proof](../evidence/standalone_windows.json) covers 23
  native programs and 28 host checks. Its [pinned build guide](https://github.com/MrxSiN/XAX/blob/3dcb358e48b0f9a45b8cb72767c1aa600e55cd78/compiler/integration/bfx/WINDOWS_STANDALONE.md)
  discloses the existing generic inlining configuration needed to avoid a
  Win64 call-path decline. That work is included in build time and memory;
  the complete native XAX build driver is still unfinished.
- All primary benchmark jobs ran serially with counterbalanced compiler order.
  Clocks, affinity, thermals and ordinary desktop/background activity were
  uncontrolled. Three run clusters and the exploratory family-adjusted
  intervals in the report limit statistical generalization.
- The first console-launch calibration imposed an extra Python coordinator
  on competitors and created extra console processes. Its completed partial
  samples are retained and excluded with the reason. The scored runs use
  native detached command sequencing and direct brainfry invocation. No
  workloads or samples were removed for poor performance.
- A concurrent parent/child allocation control validates Windows tree memory;
  a touched 16 MiB control validates Android peak-RSS units. Calibration samples
  are excluded from scores. Public distribution of the external hash-pinned
  collectors remains incomplete.

Build latency, runtime RAM and Windows standalone execution are now measured
on this corpus. Wider workload coverage, sustained calls, real apps, energy
and best compatible modes remain open. No unrestricted compiler is marked
SURPASSED; M8 remains unmet.

<details>
<summary>Per-program build times (median milliseconds)</summary>

#### Windows x86-64

| Program | BBC (ms) | Awib (ms) | brainfry (ms) |
|---|---:|---:|---:|
| hello | 901.711 | 136.244 | 14.425 |
| binary echo | 664.030 | 135.728 | 14.881 |
| wrap | 649.685 | 134.212 | 14.851 |
| nested count | 665.600 | 141.546 | 14.746 |
| transfer repeat | 1,284.093 | 137.772 | 14.777 |
| multi transfer | 1,349.233 | 135.699 | 14.672 |
| scan | 989.085 | 144.455 | 15.024 |
| nested math | 1,849.426 | 138.303 | 14.807 |
| clear set | 1,480.630 | 136.334 | 14.859 |
| permit flag | 657.928 | 134.565 | 15.102 |
| countdown actions | 647.673 | 137.176 | 14.587 |
| checksum four | 704.692 | 135.670 | 14.861 |

#### Android ARM64 target, built on Windows

| Program | BBC (ms) | Awib (ms) | brainfry (ms) |
|---|---:|---:|---:|
| hello | 817.222 | 747.300 | 15.082 |
| binary echo | 647.645 | 772.404 | 15.816 |
| wrap | 626.071 | 756.973 | 16.069 |
| nested count | 650.086 | 754.476 | 14.966 |
| transfer repeat | 1,086.292 | 744.907 | 15.071 |
| multi transfer | 1,155.318 | 742.192 | 15.062 |
| scan | 904.902 | 752.031 | 15.260 |
| nested math | 1,568.243 | 748.745 | 14.884 |
| clear set | 1,218.565 | 743.169 | 14.727 |
| permit flag | 636.531 | 748.578 | 15.365 |
| countdown actions | 630.615 | 744.589 | 14.975 |
| checksum four | 698.900 | 749.671 | 15.062 |

</details>

## Quick comparison

The tables in this section retain the earlier pilot and standalone Android
follow-up. Their build/package boundaries differ from the new measurements
above; their original samples and verdicts remain unchanged.

### Latest Android standalone process, including startup

| Compared with | BBC (ms) | Other compiler's program (ms) | BBC difference |
|---|---:|---:|---|
| Awib | 13.441 | 31.076 | 17.635 ms less |
| brainfry | 12.501 | 7.473 | 5.028 ms more |

These are new 2026-10-20 measurements with a complete BBC executable, using
the same twelve sources, inputs and pinned competitor executables. Each row
averages per-program medians; BBC has a separate paired population for each
competitor. [Scope, raw evidence and individual times](#standalone-android-process)
are below. This process result does not establish compiler, RAM, application
or best-mode superiority.

### Original shared-library pilot: process time including startup

| Run on | Compared with | BBC time (ms) | Other compiler's program (ms) | Extra time BBC takes (ms) |
|---|---|---:|---:|---:|
| Android ARM64 | Awib | 38.438 | 29.995 | 8.443 |
| Android ARM64 | brainfry | 38.076 | 8.017 | 30.059 |
| Windows x86-64 | Awib | 15.056 | 10.617 | 4.439 |
| Windows x86-64 | brainfry | 15.056 | 10.822 | 4.234 |

### Original pilot: time to compile into a runnable test artifact

| Build for | BBC (ms) | Awib (ms) | brainfry (ms) |
|---|---:|---:|---:|
| Android ARM64 | 800.375 | 355.749 | 164.945 |
| Windows x86-64 | 754.884 | 371.631 | 159.757 |

For example, building an Android test artifact takes about **0.80 seconds
with BBC**, **0.36 seconds with Awib** and **0.16 seconds with brainfry**.
Both targets are compiled on Windows. These times include the common test
runner's startup; they do not measure APK packaging or just the compiler itself.

Each time above is the arithmetic average of the twelve per-program medians,
giving each program equal weight. Each median uses thirty recorded trials.
Extra time is the difference of those averages, calculated before rounding.
These descriptive averages are not a new significance test or a measured
batch run. BBC's Android run times differ between its separately paired
Awib and brainfry trials; both populations are preserved.

### Latest Android standalone file size

| Compiler | Smallest file (bytes) | Largest file (bytes) | Average file (bytes) |
|---|---:|---:|---:|
| BBC | 1,876 | 13,552 | 5,423 |
| Awib | 4,480 | 4,904 | 4,644 |
| brainfry | 896 | 3,184 | 1,307 |

These count complete executables over the same twelve programs, excluding
shared OS libraries equally. Average file sizes are rounded to whole bytes.
BBC no longer needs its fixed test-host file for this Android package; it
still has the largest average file. This is not a RAM measurement.

### Original pilot: size of a runnable test program

| Built for | BBC, including its test host (bytes) | Awib executable (bytes) | brainfry executable (bytes) |
|---|---:|---:|---:|
| Android ARM64 | 22,960 | 4,480–4,904 | 896–3,184 |
| Windows x86-64 | 22,528–107,008 | 17,408–17,920 | 2,560–5,120 |

Ranges show the smallest and largest files across the twelve programs.
BBC includes its native module plus one copy of the generic host needed to
run it. Shared OS libraries are excluded for all compilers. File size does
not tell us RAM use, and these are not Android application package sizes.

See [individual program times](#results), [which compilers were tested](#coverage),
[how the measurements work](#measurement-boundary) and the separate
[BBC build-cost diagnosis](#verification-cost-diagnosis).

## Recorded versions and evidence

Competitor pilot date: 2026-10-19. BFX v1 and source-request v1. BBC base revision
`4bff2a3e8d07baf1cee93c46036b034966ed7592`, with the measured frontend
SHA-256 `6829614ef2d7778e8e1513ecdb94726ce00ad2989f12618987a569386a7dce88`.
XAX revision `ac7821c9bf9c1bde0c18f00da6d1a60a3b320816`.
The [complete evidence](../evidence/competition_pilot.json) supplies raw trials,
source/input/output bytes and hashes, tool identities, artifacts and intervals.

## Coverage

Pins identify inspected source, not a claim that every project built here.
This matrix records the original pilot's tool availability; the standalone
follow-up reuses its pinned executables and does not reassess those blockers.

The subsequent [2026-10-20 SDK follow-up](09_BRAINFRY_ANALYSIS.md) resolves
the original Brainfly Windows build blocker. Its JIT and generated NativeAOT
routes now pass twelve correctness cases each. Android remains unverified;
no Brainfly timing row is scored by this follow-up.

| Project (link to exact commit) | Android ARM64 | Windows x86-64 |
|---|---|---|
| [Awib @ f9f43a0](https://github.com/matslina/awib/tree/f9f43a0092b6c4ba77c6d2d9e21db3b3b37cd706) | EXECUTED: generated C with NDK Clang O3 | EXECUTED: generated C with GCC O3 |
| [brainfry @ e55d457](https://github.com/DirazCoder/brainfry/tree/e55d45735a6feb450a7e47852f4340f5b532fef8) | EXECUTED: freestanding linux-aarch64 syscall output on Android | EXECUTED: windows-x86_64 native AOT |
| [bf-x86 @ 3a2feb2](https://github.com/skeeto/bf-x86/tree/3a2feb241f484036a95c7b5f5123b33f4dc8fd0c) | NOT COMPARABLE: x86-64 code | NOT COMPARABLE: Linux ELF/syscall output |
| [bflang @ 612c8eb](https://github.com/Kuree/bflang/tree/612c8ebffbb2017cbbe36efef0224fdc556dbe5c) | BLOCKED on build host | BLOCKED on build host |
| [Brainfly @ 2e1d1b5](https://github.com/hez2010/Brainfly/tree/2e1d1b56725dd69b2278ee4566ee2dacfca5d348) | UNVERIFIED; build host lacks required SDK | BLOCKED: net10.0 project; no .NET SDK installed |
| [pablojorge/brainfuck @ 1539247](https://github.com/pablojorge/brainfuck/tree/153924714ae5e569ec39dcf0c0a5b5ae33600cc6) | UNVERIFIED translated routes; inspected JIT is x86-64 | UNVERIFIED translated routes; inspected JIT uses POSIX mapping and macOS syscalls |
| [abfc @ ea8d26d](https://github.com/fcostin/abfc/tree/ea8d26d6c92cac89019f0f2d5d29dc4798f9e66c) | NOT COMPARABLE: ia32/x86-64 assembly | NOT COMPARABLE: Linux syscall assembly |
| [Wilfred/bfc @ 2cd6a75](https://github.com/Wilfred/bfc/tree/2cd6a755578191d84e536ae2de1dcd75a635a7dc) | BLOCKED on build host | BLOCKED on build host |

The bflang CMake configure failed because LLVM development configuration was
absent; MLIR development packages are also absent. Its README requires LLVM
18 or later. Wilfred/bfc's locked release build failed in llvm-sys 140.1.2
because LLVM 14 was unavailable. Those are local toolchain blockers, not
evidence of unsupported target platforms or BBC victories. Brainfly's
NativeAOT and JIT remain unmeasured. No project was replaced by its interpreter
and counted as a compiler comparison.

Awib and brainfry leave the cell unchanged on EOF and do not share BBC's
fixed checked-tape contract. The scored subset performs no EOF read, accesses
only safe low tape indices and completes below output capacity. Full-profile
failure comparisons are NOT COMPARABLE. Native results and exit status must
match before any timing is accepted. No source algorithm changes per compiler.

## Measurement boundary

Windows build/execution host: AMD Ryzen 7 5800H, eight cores/sixteen logical
processors, Windows 11. Android execution: Pixel 8 Pro, Tensor G3, Android
17/API 37, arm64-v8a. Android compilation is cross-compilation on the same
Windows host. No desktop Linux execution or benchmark was used.

The corpus contains twelve distinct sources: three sanity, six hot-compute
and three small decision programs. Three holdouts are recorded. This is
below the general twenty-program coverage goal; the decisions have not been
integrated as three real XAX applications. One canonical input per source is
timed. Native correctness checks for other BBC profile cases remain in the
[existing reports](05_STATUS.md).

Each target has three independent measurement processes and ten paired trials
per source/run. Each process-execution arm has two warmups; arm order is
randomized with fixed seeds. Windows uses perf_counter_ns around subprocess execution;
Android uses CLOCK_MONOTONIC around fork/exec, pipe consumption and wait.
ADB is outside the timed interval. Whole process creation, loading, logical
tape reset, input, compute, output and termination are included. No overhead
is subtracted. Filesystem/OS caches are warm; cold here means fresh processes.
These are not steady-state native computation measurements.

BBC compilation runs the pinned native frontend, validates its complete BFX
success record, invokes the native canonical importer, verifies its graph
and uses unchanged XAX target lowerers and PE/shared-object writers. Awib
runs its native compiler, then the target C compiler/linker. Brainfry uses
its optimized native AOT compiler. Toolchain installation and seed bootstrap
are excluded equally. Intermediate BBC stages are recorded independently.

Every compilation arm includes a common fresh Python measurement CLI launch.
This orchestration overhead is retained, disclosed and also separated by
the recorded inner build interval. Runner startup can account for much of
a very fast compiler's reported time. These are complete **test-pipeline** times,
not clean compiler-only timing or Android application packaging. A direct
baseline-CLI and scored deployment-package timing remains to be established.

BBC's result is a native component executed through a fixed generic C
function-call transport outside both repositories. That host contains no BF
parser, interpreter, optimizer or backend. Size comparisons count the BBC
module plus one copy of the native host per standalone workload, and the
competitor's complete executable. Module and host bytes are also recorded
separately. Shared OS libraries are excluded equally; resident/shared runtime
RAM was unmeasured in that pilot; the separate follow-up above measures it. XAX emits no debug/static-symbol table in these modules;
C outputs use stripped symbols. No APK size comparison is implied.

Awib C uses unsigned-byte cells and a disclosed Windows binary-stdio adapter
that sets stdin/stdout to binary mode. Translation, adaptation and C linking
are included in compilation. The @lang_c directive contains no Brainfuck
commands; supplied and canonical command streams are checked identical.
Awib's native frontend is bootstrapped through its unchanged preprocessing
and C polyglot route. These external dependencies are not BBC implementation.

The raw evidence retains medians, quartiles, per-workload regressions,
category means and paired hierarchical bootstrap intervals. A conservative
32-contrast Bonferroni family covers four target/competitor pairs, two timing
metrics and overall/three-category summaries. Only three independent run
clusters exist; intervals are exploratory. Clocks, affinity and thermals were
not controlled. Android thermal snapshots are retained. Do not promote a
startup-dominated or noisy point estimate to a runtime victory.

## Results

Each per-program entry is the median of thirty recorded trials, in milliseconds.
**Lower is better.** Run times include process startup, tape initialization,
input/output and shutdown. Build times include test-runner startup and the
full source-to-runnable test pipeline.

The programs fall into three groups:

- Basic checks: `hello`, `binary_echo` and `wrap`.
- Compute: `nested_count`, `transfer_repeat`, `multi_transfer`, `scan`,
  `nested_math` and `clear_set`.
- Small decisions: `permit_flag`, `countdown_actions` and `checksum_four`.

The three holdout programs were reserved from optimization tuning. The small
decisions are standalone tests; they have not been integrated as three real
applications.

### Android: time to run

BBC was timed separately alongside each competitor. Compare the first BBC
column with Awib and the second with brainfry; the columns retain those
distinct trial populations.

| Program | BBC in Awib trials (ms) | Awib (ms) | BBC in brainfry trials (ms) | brainfry (ms) |
|---|---:|---:|---:|---:|
| `hello` | 32.653 | 31.495 | 31.332 | 4.433 |
| `binary_echo` | 32.650 | 31.353 | 31.643 | 4.929 |
| `wrap` (holdout) | 29.443 | 24.384 | 31.353 | 4.678 |
| `nested_count` | 33.038 | 30.800 | 32.399 | 4.905 |
| `transfer_repeat` | 35.210 | 29.271 | 34.137 | 5.857 |
| `multi_transfer` | 37.256 | 30.105 | 36.813 | 5.038 |
| `scan` (holdout) | 32.214 | 30.875 | 31.247 | 4.837 |
| `nested_math` | 97.990 | 26.667 | 99.652 | 41.696 |
| `clear_set` | 34.200 | 31.132 | 34.711 | 5.648 |
| `permit_flag` | 32.416 | 31.108 | 31.125 | 4.569 |
| `countdown_actions` | 32.777 | 31.628 | 31.994 | 5.070 |
| `checksum_four` (holdout) | 31.410 | 31.120 | 30.500 | 4.541 |

### Windows: time to run

The recorded BBC medians are identical in both comparator populations, so
they are shown once.

| Program | BBC (ms) | Awib (ms) | brainfry (ms) |
|---|---:|---:|---:|
| `hello` | 10.681 | 10.726 | 10.208 |
| `binary_echo` | 10.908 | 10.461 | 10.245 |
| `wrap` (holdout) | 11.370 | 11.476 | 11.098 |
| `nested_count` | 10.734 | 10.495 | 10.278 |
| `transfer_repeat` | 11.971 | 10.369 | 10.122 |
| `multi_transfer` | 13.456 | 10.687 | 10.495 |
| `scan` (holdout) | 10.882 | 10.463 | 10.207 |
| `nested_math` | 57.357 | 11.027 | 16.298 |
| `clear_set` | 11.393 | 10.520 | 10.274 |
| `permit_flag` | 10.430 | 10.267 | 10.082 |
| `countdown_actions` | 10.627 | 10.394 | 10.285 |
| `checksum_four` (holdout) | 10.864 | 10.523 | 10.270 |

### Android: time to compile

| Program | BBC (ms) | Awib (ms) | brainfry (ms) |
|---|---:|---:|---:|
| `hello` | 747.290 | 342.613 | 156.524 |
| `binary_echo` | 587.929 | 351.306 | 166.077 |
| `wrap` (holdout) | 605.621 | 356.532 | 167.332 |
| `nested_count` | 599.454 | 364.924 | 163.965 |
| `transfer_repeat` | 958.186 | 347.498 | 163.130 |
| `multi_transfer` | 1022.399 | 356.473 | 168.617 |
| `scan` (holdout) | 806.547 | 348.863 | 160.903 |
| `nested_math` | 1349.263 | 364.037 | 167.871 |
| `clear_set` | 1100.929 | 357.642 | 170.560 |
| `permit_flag` | 600.747 | 356.335 | 167.913 |
| `countdown_actions` | 579.200 | 351.737 | 158.671 |
| `checksum_four` (holdout) | 646.940 | 371.033 | 167.781 |

### Windows: time to compile

| Program | BBC (ms) | Awib (ms) | brainfry (ms) |
|---|---:|---:|---:|
| `hello` | 719.618 | 391.501 | 172.989 |
| `binary_echo` | 552.681 | 359.207 | 153.471 |
| `wrap` (holdout) | 572.957 | 389.793 | 165.367 |
| `nested_count` | 569.963 | 372.009 | 160.426 |
| `transfer_repeat` | 901.264 | 363.194 | 153.790 |
| `multi_transfer` | 947.672 | 363.983 | 154.416 |
| `scan` (holdout) | 741.579 | 372.660 | 155.871 |
| `nested_math` | 1273.032 | 364.684 | 155.421 |
| `clear_set` | 1060.855 | 369.572 | 162.549 |
| `permit_flag` | 566.119 | 367.888 | 161.360 |
| `countdown_actions` | 568.276 | 375.960 | 165.686 |
| `checksum_four` (holdout) | 584.594 | 369.117 | 155.743 |

### What the results show

BBC takes longer on average at both measured timing boundaries and produces
larger runnable files for every tested program. The recorded overall
statistical comparisons also favor each competitor on each target.
The competitive verdict for this pilot is **REGRESSION**.

The largest visible compute delay is `nested_math`: on Windows, BBC takes
**57.357 ms**, Awib **11.027 ms** and brainfry **16.298 ms**. Other differences
are small: Windows `hello` takes BBC **10.681 ms** and Awib **10.726 ms**.
Do not interpret such a small difference as an established BBC win.

The evidence retains the original overall/category statistical summaries,
adjusted uncertainty intervals, raw samples, quartiles and artifact hashes.
Those exploratory overall intervals favor the competitors; several basic
check and decision category intervals include no difference. Each comparison
has only three independent measurement runs. Sustained computation and
full resource verdicts remain **NOT MEASURED**.

### Build time inside the test runner

The following averages use the separately recorded interval inside the
runner, covering the build itself. They exclude the outer measurement CLI
startup. They are observed intervals, not estimates made by subtracting a
fixed overhead from the full build times above.

| Build for | BBC (ms) | Awib (ms) | brainfry (ms) |
|---|---:|---:|---:|
| Android ARM64 | 587.097 | 208.963 | 17.596 |
| Windows x86-64 | 546.574 | 227.277 | 16.446 |

As in the quick comparison, these are arithmetic averages of the twelve
per-program medians. For brainfry, the full test pipeline takes about
160–165 ms per program on average, while its inner build interval takes
about 16–18 ms. Runner overhead is substantial; use the correct timing
boundary when discussing compiler cost. Direct baseline-CLI and deployment
package timings remain unmeasured.

### What is counted in BBC's file size

| Built for | Native module (bytes) | Fixed test host (bytes) | Combined runnable test (bytes) |
|---|---:|---:|---:|
| Android ARM64 | 17,352 | 5,608 | 22,960 |
| Windows x86-64 | 4,608–89,088 | 17,920 | 22,528–107,008 |

The [original pilot's size table](#original-pilot-size-of-a-runnable-test-program) includes that host
so BBC's module is not compared alone with a complete competitor executable.
Native code/data section sizes and full file bytes are retained separately
in the evidence. The sectionless brainfry ARM64 ELF code/data breakdown is
**NOT MEASURED**. No resident-memory estimate is inferred from section sizes,
tape size or importer staging capacity.

### Where BBC spends compilation time

| Build for | Read source, frame and run BBC frontend (ms) | Import BFX (ms) | XAX read/verify (ms) | XAX lower/write native code (ms) |
|---|---:|---:|---:|---:|
| Android ARM64 | 2.420 | 0.975 | 328.076 | 120.472 |
| Windows x86-64 | 2.301 | 0.893 | 335.277 | 70.243 |

These are stage medians across the fixed corpus; they need not add up to
the median total. All stages execute on Windows. The read/verify stage
accounts for a median 75.5% of the instrumented Android-target pipeline
and 81.6% of the Windows-target pipeline; the BBC frontend accounts for
about 0.5–0.6%. The diagnosis below separates store/helper setup from graph
verification within that stage.

Importer output staging reserves a declared 64 MiB view; peak resident
compiler RAM was unmeasured in that diagnosis; see the new full-build memory tables above.

## Verification cost diagnosis

A separate [verification profile](../evidence/graph_verification_profile.json)
refines the earlier timer label. The pilot's verification bucket included
StoreReader construction, helper initialization, container digest/index
checks, object decoding/CID checks, semantic graph verification and function
lookup. It was not a timer for graph checks alone. The recorded competitor
timings and raw evidence are unchanged.

All measurements below use the same Windows build host and pinned XAX
revision. Android rows describe Android-target cross-compilation on Windows,
not an Android-hosted verifier.

The canonical programs already exist: xax_blake3_hash.xax,
xax_store_decoder.xax, xax_graph_decoder.xax, xax_cfg_analysis.xax,
xax_op_typing.xax and xax_store_verifier.xax in XAX's compiler/bootstrap.
The general compiler-driver graph contains the XAX-native semantic
marshalling/call chain. Exact helper hashes are in the new evidence.
The current common helper loader and general-driver process wrapper use
Linux host facilities. XAX already emits executable Windows decision DLLs;
activation of the verifier/hash helpers through this host path is the
missing integration operation, not a missing Brainfuck compiler or hash
algorithm.

| Observed source of cost | Exact location in pinned XAX | Finding |
|---|---|---|
| Cold helper initialization and store loading | [StoreReader](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/src/xax_compiler.py#L658) | Even the empty decision store takes about 188 ms to construct in a fresh process, before about 30 ms of explicit verification |
| Windows native-helper availability | [native_host](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/src/xax_native.py#L42) | Current common helper loader admits Linux x86-64 only; recorded Windows authority falls back to Python for hash, decoders, CFG, typing and store verification |
| Failed compression-helper setup | [native compression attempt](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/src/blake3.py#L117) | Loads/verifies/lowers a canonical compression helper before executable mapping rejects the Windows host; profiler also records first-use platform-probe/import costs |
| Repeated type construction and hashing | [checked byte-view validation](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/src/xax_compiler.py#L5427) | nested_math reconstructs bits<8> 1,492 times; the compiler graph reconstructs it 2,134 times, according to a separate untimed call trace |
| Repeated store verification | [Windows lowering](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/src/xax_x86_64.py#L2343), [ARM64 bundle lowering](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/src/xax_aarch64.py#L2453) | Driver verifies first; each backend verifies the same reader again |
| Existing proof reuse | [ProofCache](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/src/xax_compiler.py#L315), [verify_store](https://github.com/MrxSiN/XAX/blob/ac7821c9bf9c1bde0c18f00da6d1a60a3b320816/compiler/src/xax_compiler.py#L8202) | Attaching a fresh local cache to the reader before the first successful verification lets the unchanged backend reuse its object proofs |

The parsed-graph CID cache already exists at _PARSED_GRAPHS. It replays
dependency resolution when reusing a graph. The remaining repeated pass
without ProofCache still recomputes object CIDs; another generic parse
cache would duplicate existing machinery.
BYTE_ELEMENT_CID is also already available for bits<8>. The observed
one-byte access checks still reconstruct that same identity repeatedly
in the Python fallback. Reuse the existing canonical type facts in the
XAX-native path; do not patch the legacy Python checker under this work.

Three fresh processes per source separate cold phases. Thirty same-process
observations per source come from three processes with ten samples each.
These repeated observations have warmed graph/helper state and are not
cold compilation estimates. All fourteen stores contain 23 semantic objects;
graph/store byte size, not object count alone, explains the scaling.

| Store | Bytes | Fresh process: reader ms | Fresh process: explicit verify ms | Repeated verify without proof cache ms | Repeated verify with proof cache ms |
|---|---:|---:|---:|---:|---:|
| empty | 10,515 | 187.558 | 30.136 | 12.416 | 0.076 |
| permit_flag | 12,132 | 192.242 | 41.738 | 14.078 | 0.075 |
| hello | 22,080 | 197.300 | 116.938 | 23.008 | 0.076 |
| nested_math | 50,868 | 220.414 | 340.652 | 48.681 | 0.079 |
| compiler | 262,358 | 394.479 | 1,685.924 | 247.610 | 0.076 |

Profiler timings include profiler overhead and are diagnostic only. Native
authority is captured rather than assumed: setting XAX_REQUIRE_NATIVE=1
explicitly rejects this Windows helper path at the unavailable executable
mapping. No foreign hash library, Python patch or suppressed validation is
used to obtain a native claim.

**Smallest measured reduction.** An external prototype passes the existing
ProofCache API to StoreReader, keeps the explicit first verify_store call,
then invokes the same target backend. Every first verification has zero
cache hits. The backend still calls verify_store, which reuses exact local
object proofs and retains store/dependency checks. No serialized cache or
safety claim is accepted from BFX producers.

The randomized A/B measures the complete warm in-process XAX
read/verify/lower/emit interval, excluding BBC, BFX import, process startup
and disk I/O. Each primary row has three independent processes and ten pairs
per process. Both arms are warmed equally. All 400 measured native emissions,
including the separate compiler diagnostic, are byte-identical per
source/target; primary outputs also equal the previously executed pilot
binaries. The seven unchanged XAX proof-cache tests pass, including corrupt
cache, changed verifier/dependency and stale-invalid-semantics rejection.

| Target output | Source | Original XAX stage (ms) | With existing proof cache (ms) | Less time (ms) |
|---|---|---:|---:|---:|
| Android ARM64 | permit_flag | 84.709 | 69.234 | 15.475 |
| Android ARM64 | hello | 200.823 | 172.170 | 28.653 |
| Android ARM64 | nested_math | 553.876 | 498.468 | 55.408 |
| Windows x86-64 | permit_flag | 60.022 | 45.711 | 14.312 |
| Windows x86-64 | hello | 155.464 | 132.381 | 23.083 |
| Windows x86-64 | nested_math | 561.437 | 517.517 | 43.920 |

The last column is the difference between the two medians, calculated
before rounding. The recorded exploratory aggregate intervals favor cache
reuse for both targets. They are adjusted over eight case/aggregate
comparisons, with only three independent process clusters. Android
hello's adjusted interval includes no improvement; its point estimate
alone is not a supported individual win. Full statistical summaries remain
in the verification evidence. This limited stage experiment does not
establish a competitor win or a cold full-build improvement.

The larger compiler graph has a separate ten-pair, one-process diagnostic:

| Target output | Original XAX stage (ms) | With existing proof cache (ms) | Less time (ms) |
|---|---:|---:|---:|
| Android ARM64 | 4,562.346 | 4,513.582 | 48.763 |
| Windows x86-64 | 7,182.447 | 6,946.600 | 235.848 |

These point estimates are not replicated wins and are excluded from the
primary three-source summaries. All samples remain published. Lowering
dominates that warm workload, so
the tiny repeated-verification time must not be described as an equivalent
whole-build improvement.

The immediate option is to reuse the existing local proof cache in the
build call chain. The larger cold-cost task is a verified graph-native
Windows helper execution path, starting with hashing/loading and preserving
the Win64 ABI, lifetimes, integrity and verifier decisions. Existing PE
emission alone does not prove this helper integration. Do not implement it
by extending the legacy Python loader or adding a foreign hash replacement.
Keep cold helper setup, per-node type checks and remaining lowering costs
separate when measuring the next change.

The recorded diagnosis changes no BBC instruction stream or XAX graph.
Its external prototype invokes unchanged legacy APIs; it is not a production
XAX graph integration or a whole-toolchain native migration.
The twelve-source competitor results and M8 status remain unchanged.

## Windows native hashing host

The next implementation step is now **EXECUTED**: a
[standalone Windows hashing host](03_XAX_INTEGRATION.md#windows-native-hashing-host)
written as a canonical XAX graph. It owns its buffers and Windows stream I/O,
reuses the existing full BLAKE3 graph, and needs only kernel32 at runtime.
Unchanged Python bootstrap tools still verify and lower that graph.

The [separate execution report](../evidence/windows_hash_host.json) records
139 successful inputs and five failure cases against an independent hash
oracle, including fragmented pipes, redirected files and size boundaries.
The runnable PE is **45,568 bytes** and rebuilds identically. Its input limit
is **16 MiB**; the larger general compiler-driver store is correctly rejected.

The compiler's common helper loader does not yet use this hashing process.
The separate driver prototype below now executes the decoder, CFG, typing and
verifier chain on tested stores; general coverage and common-loader integration
remain incomplete. These are functional execution checks, with **no new full-build
timing or competitor comparison**. The pilot tables above remain unchanged.
This Windows-only host adds no Android implementation or execution result.

## Windows native verification CLI

A [canonical Windows driver prototype](03_XAX_INTEGRATION.md#windows-native-driver-prototype)
now executes the existing XAX verification chain directly as a PE process.
The common Python helper loader still falls back on Windows; this is an
explicit alternative CLI, with bounded coverage. Its correctness report
retains four malformed-input declines, one different rejection diagnostic,
and declines for the corrected self-store, large flag edit and DLL packaging.

The [2026-10-20 timing report](../evidence/windows_native_verification_profile.json)
compares **fresh verification processes**, including startup and store reads.
The native command additionally creates an empty success diagnostic file.
Each row has three separate runs and ten randomized pairs per run: 30 samples
per arm, 180 timed process invocations overall. All timed commands accept and
produce the expected empty success output. An unmeasured invocation warms OS
file caches equally before each case/arm/run; this is not a cold-disk test.

| Store checked | Reference Python CLI (ms) | Native Windows CLI (ms) | Less time (ms) |
|---|---:|---:|---:|
| BBC compiler store | 7,302.5 | 201.9 | 7,100.7 |
| Windows hashing-host store | 1,590.1 | 74.4 | 1,515.7 |
| Small semantic fixture | 1,150.1 | 53.6 | 1,096.6 |

Values are medians; the last column subtracts the medians before rounding.
For the BBC compiler store, observed times range from 4,690.2 to 8,433.6 ms for
Python and 136.9 to 614.8 ms for the native CLI. Raw samples, pair order and
per-run medians are retained. Clocks, affinity and thermals were uncontrolled;
these are exploratory descriptive measurements, without a significance claim.

This run uses a Ryzen 9 5900HS Windows host; the earlier pilot used a different
host. The boundary also differs from the earlier warm-stage and full-build
experiments. **Do not subtract these savings from the pilot's build times.**
There is no BBC filtering, BFX import, lowering, DLL/APK packaging, target
execution or competitor timing in this experiment. The compiler/deployment
comparison tables and M8 status remain unchanged. No new Android execution or
resident-RAM measurement is established.

## Standalone Android process

**2026-10-20:** a [canonical XAX host](03_XAX_INTEGRATION.md#standalone-android-process)
now calls the existing verified decision directly in a static executable.
It removes the shared-library test host and dynamic loader. BBC source,
BFX bytes, the full tape reset and source-program bounds/I/O checks stay
unchanged. It buffers at most 65,536 input bytes to EOF, checks success before
publishing output and handles fragmented input and partial writes.

[Primary evidence](../evidence/standalone_android.json) and
[native-only replay](../evidence/standalone_native_replay.json) retain canonical
roots, transactions, artifact/tool hashes and actual native authority.
Twenty existing decisions pass, with additional binary/fragmented and
maximum/excess input, closed-descriptor, failure-prefix, overflow and large
output checks. Twenty-three programs execute natively. A second bootstrap
build reproduces the empty and hello executable bytes; unchanged generic
Python utilities still verify, lower and package them.

The frozen twelve-program corpus, inputs, holdouts and comparator modes match
the original pilot. Awib and brainfry executable hashes are checked against
that evidence. Three separate runs have ten randomized pairs per source and
comparator, with two unmeasured warmups per arm/source/run: 1,440 timed process
invocations, all checked for complete output and exit status. The timer runs
on Android around fork, exec, pipe consumption and wait. Input-file opening,
pipe creation and ADB precede timing equally; no overhead is subtracted.
An initial probe overlapped validation. Its complete data and exclusion reason
are retained; the primary run started after validation, regardless of that
probe's timings.

| Compared with | Standalone BBC (ms) | Other program (ms) | BBC difference |
|---|---:|---:|---|
| Awib | 13.441 | 31.076 | 17.635 ms less |
| brainfry | 12.501 | 7.473 | 5.028 ms more |

Each value averages twelve per-program medians of thirty trials. Exploratory
family-adjusted paired bootstrap intervals put BBC's advantage over Awib at
16.661 to 20.206 ms and its disadvantage to brainfry at 4.738 to 6.341 ms.
Only three process clusters exist; clocks, affinity and thermals were
uncontrolled. These compare complete processes on the same Pixel 8 Pro;
they establish no steady-state or real-application comparator result.

### Individual standalone process times

| Program | BBC paired with Awib (ms) | Awib (ms) | BBC paired with brainfry (ms) | brainfry (ms) |
|---|---:|---:|---:|---:|
| hello | 6.185 | 30.379 | 3.555 | 3.703 |
| binary_echo | 5.720 | 31.092 | 4.709 | 4.337 |
| wrap | 5.324 | 30.469 | 4.169 | 4.157 |
| nested_count | 5.329 | 30.749 | 4.649 | 4.362 |
| transfer_repeat | 8.302 | 31.308 | 8.265 | 5.322 |
| multi_transfer | 10.924 | 31.682 | 10.656 | 4.780 |
| scan | 5.741 | 31.073 | 4.678 | 4.306 |
| nested_math | 88.491 | 31.814 | 88.623 | 40.706 |
| clear_set | 8.210 | 31.600 | 7.210 | 5.201 |
| permit_flag | 5.318 | 30.725 | 4.601 | 4.194 |
| countdown_actions | 5.704 | 30.660 | 4.225 | 4.153 |
| checksum_four | 6.046 | 31.357 | 4.668 | 4.458 |

BBC is faster than **the pinned Awib configuration on this common safe no-EOF
subset and Android process boundary**. Brainfry remains faster overall.
Complete native files range from 1,876 to 13,552 bytes, averaging 5,423 bytes;
BBC is still larger on average than both competitors. File size is not RAM.

This updates the Android standalone process comparison only. Original pilot
reports and Windows/build timings remain unchanged. Full-profile and best-mode
coverage, twenty real workloads, three application integrations, compiler
latency, RAM and Windows standalone comparisons were open in that snapshot; the separate follow-up above now measures them on this corpus. The installed
Android UI app keeps its previous module. No unrestricted comparator is
SURPASSED, and M8 remains **NOT YET ACHIEVED**.

## Eight-byte tape reset

**2026-10-20:** the canonical XAX importer now clears the full 65,536-byte
decision tape with checked eight-byte stores. It preserves alignment one,
Brainfuck semantics and BFX v1. [Proof and correctness checks](07_OPTIMIZATION_PROOFS.md#xax-eight-byte-tape-reset)
cover all tape bytes, dirty and unaligned buffers, loops and failures.

The [new evidence](../evidence/wide_tape_reset.json) measures repeated native
calls on the same frozen twelve-program corpus. Each observation averages
sixteen timed calls, each including the mandatory full reset. There are three
independent runs and ten randomized pairs per program/run, with three warmup
calls per version/program/run. Every timed output and status is checked outside
the timer. Each target has 11,520 timed calls. Startup, BFX import, verification
and native compilation are outside this boundary.

| Native-call boundary | Before (ms) | After (ms) | Less time per call (ms) |
|---|---:|---:|---:|
| Windows x86-64 | 6.168 | 5.624 | 0.544 |
| Android ARM64 | 1.360 | 1.302 | 0.058 |

These are arithmetic averages of the twelve workload medians of batch means.
For example, the Windows permit decision takes 0.311 ms before and 0.041 ms
after; the Android permit decision takes 0.099 ms before and 0.017 ms after.
The hot nested-math program still dominates average call time. Exploratory
intervals favor the change on both targets, with only three process clusters;
the evidence retains every workload and raw paired observation.

Windows uses the Ryzen 9 5900HS host and includes ctypes call overhead.
Android uses Pixel 8 Pro and clocks the direct native call. Clocks, affinity
and thermals were uncontrolled. These results do not measure application
integration or establish a steady-state comparison against other compilers.

### Fresh Android process comparison

The follow-up reuses the pinned Awib/brainfry executables, exact 5,608-byte
pilot host and identical inputs/expected outputs from the original pilot.
Artifact hashes are checked before measurement. Three runs have ten randomized
pairs per program/comparator/run: 1,440 timed process invocations, all checked
for output and exit status. The timer runs on Android around fork, execution,
pipe consumption and wait; ADB is outside it. Startup and dynamic loading count.

| Compared with | Optimized BBC program (ms) | Other compiler's program (ms) | Extra time BBC takes (ms) |
|---|---:|---:|---:|
| Awib | 39.347 | 32.055 | 7.292 |
| brainfry | 38.435 | 8.483 | 29.952 |

Each row averages the twelve per-program medians of thirty trials. BBC's two
paired populations stay separate. **Both process aggregates still favor the
competitors. No comparator is surpassed.** These are new measurements; they
do not replace or subtract savings from the original pilot or its build times.

The twelve measured native file sizes are unchanged. The separate empty-program
Windows regression DLL grows from 2,560 to 3,072 bytes at a PE padding boundary;
the Windows importer grows by 512 bytes. No smaller-file or resident-RAM claim
is made. No new end-to-end build timing, Windows competitor score, application
result or best-mode coverage is established. The installed Android app retains
its previously tested module; M8 remains **NOT YET ACHIEVED**.

## Remaining gates and next measured work

The standalone Android process result favors BBC over pinned Awib on its
recorded subset, while brainfry remains faster. No unrestricted comparator is
SURPASSED. Unavailable projects remain visible. Broader RAM coverage,
steady-state execution, application integration, best compatible alternate
modes and release coverage prevent a sweep on either required target.

GCC-generated C on Windows and Clang-generated C on Android are measured with
Awib as the pinned translator; those rows share the named Awib data and do
not count as extra independent compiler wins. The new follow-up above measures
Clang on Windows over the twelve-source corpus. Optimized Rust translations
still need separate full-corpus trials. Brainfry JIT and Awib's
alternate compatible modes also need checking before selecting best modes
for an unrestricted comparison.

The follow-up identifies local proof-cache reuse, cold helper setup and
repeated type hashing as separate costs. Complete the verified Windows
helper integration through XAX graph-native facilities, preserving
verification and canonical authority. Do not extend legacy Python to
implement a shortcut. BBC-owned
P1/P2 source optimization still needs its own measured native benefit, proofs
and versioned representation where necessary. No optimization was selected
using this pilot's holdout results.

The recorded pilot and diagnosis made **no BBC executable or XAX graph
changes**. Generic legacy Python XAX verifier/lowerers remain unchanged.
Their external test/benchmark code is separate from both implementation
repositories. The comparison tables present the original measurements in
elapsed time and bytes. The separate Windows hashing-host and driver
implementations, execution reports, verification CLI timings and tape-reset
experiment do not alter those earlier measurements or their verdicts. The
standalone Android comparison above is a separately measured package boundary.

External runner source is pinned by local Git tree
`9bb57e6de8edba20436095b7fb1525c0158d02f2` and file hashes in the evidence.
It remains local-only; independently published reproduction is pending.
The source/input/output corpus is reproduced exactly in the static evidence.

## Complete-build proof-cache follow-up

The [compile-local cache experiment](18_BACKEND_BUILD_CACHE.md) now measures
fresh source-to-runnable builds through the existing cache API. All sixteen
v4 programs retain exact executable bytes on both targets. A frozen three-source
subset has twelve observations per arm/target across three runs: 216 complete
builds comparing BBC baseline, cached BBC and pinned Brainfry. First verification
uses an empty cache and remains inside the timer. Unchanged generic Python
SDK verification/lowering still runs on Windows; this adds no native helper.

Paired baseline/cache geometric means are 1.009x for Android-target and
1.001x for Windows-target builds. The latter exploratory interval crosses
one; all Holm-adjusted p-values are 1.0 with only three run clusters.
No material cold-build gain or RAM improvement is established. Brainfry's
complete builds are about 56–57x faster on this subset and retain lower
compiler working set and smaller artifacts. Keep earlier warm-stage ratios
and all prior competitor scores separate. Raw samples, source authority,
kernel memory counters and calibration are in
[new immutable evidence](../evidence/backend_build_cache.json).

The three-source result supplies a measured cold-build boundary for the
cache experiment, with insufficient broad competitive coverage. Native driver
self-store/diagnostic/large-edit/DLL gates, common-helper migration, repeated
type hashing, steady-state, deployment, larger-profile measurements and
real applications remain open. M8 is **NOT YET ACHIEVED**.
