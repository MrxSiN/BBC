# BFX v4 movement measurements

> Format migration note: measurements and source identities below describe their
> pinned pre-migration snapshots. Historical version names identify that evidence,
> not current decoder modes. Current production uses only [BFX](02_BFX_CONTRACT.md).
> No migration performance or broader completion claim follows from these reports.


The optional Brainfuck pass packs consecutive movement into powers of two.
This report compares v3 baseline and v4 movement packing
and its canonical XAX consumer; the competitive objective remains **NOT YET
ACHIEVED**. [Proofs](07_OPTIMIZATION_PROOFS.md#p1-movement-powers)
and the [v4 contract](14_MOVEMENT_PACKING.md) specify the implementation.

[Complete immutable evidence](../evidence/bfx_v4_measurements.json) contains
the frozen plan, exact source/input/output bytes, artifact and tool hashes,
all raw samples, correctness runs, calibration and exploratory intervals.
All twelve original workloads and holdouts remain; four clear-loop workloads
were added before primary timing. Brainfry is pinned at
`e55d45735a6feb450a7e47852f4340f5b532fef8`, default native AOT. Other competitors
and modes retain their [existing coverage status](08_BENCHMARKS.md).

## Boundaries and controls

The current Windows host is an AMD Ryzen 7 5800H, eight cores/sixteen threads,
Windows 11, with Python 3.13.5. Android execution uses Pixel 8 Pro, API 37.
These are separate fresh measurements; older reports retain their own host
metadata and must not be multiplied into these ratios.

Build-time and compiler-memory rows for both targets are Windows-hosted;
Android labels the output target, not an Android compiler host.
Each complete build starts a fresh required compiler process and ends after
the standalone executable is written and the process exits. BBC's native BF
frontend, canonical validators, native BF clear/arithmetic/movement passes and importer
feed unchanged generic Python XAX verification, binding and lowering. Brainfry
runs directly as its native compiler. Compiler construction, SDK installation
and deployment are excluded. Every timed build must reproduce the previously
validated executable hash. All 96 artifacts and all 48 executions per target
pass exact output/status checks.

Both BBC arms use the same OS-backed zero-initialized 64 MiB importer view,
released before verification/lowering. This is an external caller buffer
configuration. Its extent is not resident RAM; its effect cannot be attributed
to the semantic pass or compared directly with the older retention snapshot.
No new Python/C production BF translation or optimizer is supplied.

Runtime means the complete standalone process with binary input and output.
Windows includes CreateProcess, output consumption and waiting. Android uses
a native monotonic timer around fork/exec/output/wait; ADB and pipe/input
preparation stay outside. There is no overhead subtraction. Unchanged program binaries provide noise controls; exact per-workload hashes
and sizes remain in the evidence.

There are three independent run clusters and four observations per arm/case
in each, plus warmups. All six three-arm orders occur twice. Jobs are
serial; frequency, affinity, thermals and ordinary background maintenance/work
are uncontrolled. The three-cluster paired bootstrap intervals are exploratory.
Exact two-sided run-level sign flips have minimum p = 0.25; Holm-adjusted
per-case tests support no confirmatory superiority claim. The evidence gives
quartiles and keeps paired-log interval estimates separate from median ratios.

## Complete build and process time

Values below are geometric means of sixteen workload medians, in milliseconds.
Lower time is better; a reference/optimized ratio above one favors optimized BBC.

| Target | Boundary | BBC v3 | BBC optimized | Brainfry | BBC v3 / optimized | Brainfry / optimized |
|---|---|---:|---:|---:|---:|---:|
| android | runtime | 6.493 | 6.464 | 5.560 | 1.005 | 0.860 |
| android | build | 1132.662 | 1110.700 | 26.518 | 1.020 | 0.024 |
| windows | runtime | 25.589 | 25.993 | 26.663 | 0.984 | 1.026 |
| windows | build | 1159.749 | 1137.062 | 26.675 | 1.020 | 0.023 |

The extra pass has workload-dependent build costs. Brainfry retains a large
complete-build advantage. Process startup dominates the small Windows cases;
identical binaries show why their fluctuations cannot establish an optimizer
effect. Broader workloads, best modes, real application calls and energy are
unmeasured here. The `real-decision` category labels source workloads; these
runs execute standalone programs.

## Runtime medians by workload

All entries are milliseconds. The evidence retains category/holdout flags,
quartiles, individual observations and order.

### Android

| Workload | BBC v3 | Optimized | Brainfry | BBC v3 / optimized |
|---|---:|---:|---:|---:|
| hello | 5.3895 | 5.0574 | 4.7935 | 1.066 |
| binary_echo | 5.1385 | 5.1031 | 5.0211 | 1.007 |
| wrap | 5.0174 | 5.1064 | 4.8451 | 0.983 |
| nested_count | 5.0675 | 5.2740 | 5.2037 | 0.961 |
| transfer_repeat | 7.4503 | 7.2532 | 5.3115 | 1.027 |
| multi_transfer | 8.8767 | 7.5584 | 5.0569 | 1.174 |
| scan | 5.0701 | 5.2966 | 4.8988 | 0.957 |
| nested_math | 71.9748 | 85.3167 | 32.4748 | 0.844 |
| clear_set | 5.1626 | 4.6207 | 4.6940 | 1.117 |
| permit_flag | 5.6402 | 5.1817 | 4.7318 | 1.088 |
| countdown_actions | 5.0684 | 5.0423 | 4.9292 | 1.005 |
| checksum_four | 5.1217 | 5.6628 | 4.8644 | 0.904 |
| clear_input | 5.0299 | 4.9872 | 4.9184 | 1.009 |
| increment_clear | 5.0254 | 5.1608 | 4.7390 | 0.974 |
| clear_repeat | 5.7576 | 5.4756 | 5.2180 | 1.052 |
| nested_clear | 5.3421 | 5.5941 | 4.9729 | 0.955 |

### Windows

| Workload | BBC v3 | Optimized | Brainfry | BBC v3 / optimized |
|---|---:|---:|---:|---:|
| hello | 26.1808 | 25.9524 | 27.0747 | 1.009 |
| binary_echo | 24.3629 | 25.2046 | 24.5650 | 0.967 |
| wrap | 25.7308 | 26.5230 | 26.3877 | 0.970 |
| nested_count | 24.9848 | 25.3509 | 25.1241 | 0.986 |
| transfer_repeat | 24.5402 | 25.7176 | 25.4408 | 0.954 |
| multi_transfer | 25.9597 | 27.5339 | 25.6179 | 0.943 |
| scan | 25.3287 | 25.4385 | 25.8223 | 0.996 |
| nested_math | 32.5361 | 32.8799 | 53.4938 | 0.990 |
| clear_set | 24.8061 | 24.5607 | 25.1964 | 1.010 |
| permit_flag | 25.1485 | 25.5434 | 24.7625 | 0.985 |
| countdown_actions | 24.8316 | 25.1005 | 25.2662 | 0.989 |
| checksum_four | 26.2897 | 25.8930 | 26.1199 | 1.015 |
| clear_input | 25.4081 | 25.3180 | 24.5242 | 1.004 |
| increment_clear | 24.8485 | 25.7749 | 25.2398 | 0.964 |
| clear_repeat | 24.4383 | 24.5367 | 25.6568 | 0.996 |
| nested_clear | 24.9832 | 25.5360 | 25.1341 | 0.978 |

## Memory and complete file size

Memory is the geometric mean of workload median lifetime resident high-water
counters, in MiB. Windows uses retained-handle kernel peak working set after
exit. Each measured build worker has one required process. Peak pagefile data
remain separate raw counters, not job peak commit. Android uses child wait4
ru_maxrss in KiB; shared pages and a fork/loader floor limit small-program
attribution. Excluded touched-16-MiB controls validate the units. These data
establish no statistical memory victory.

| Target | Boundary | BBC v3 MiB | Optimized MiB | Brainfry MiB |
|---|---|---:|---:|---:|
| android | runtime | 1.177 | 1.176 | 1.178 |
| android | build | 51.018 | 50.999 | 5.303 |
| windows | runtime | 4.587 | 4.588 | 4.545 |
| windows | build | 50.979 | 50.966 | 5.308 |

Complete PE/ELF bytes, geometric mean across the same sixteen programs:

| Target | BBC v3 bytes | Optimized bytes | Brainfry bytes |
|---|---:|---:|---:|
| android | 2742.9 | 2729.1 | 1139.8 |
| windows | 14183.1 | 14035.9 | 2890.2 |

android: 7 files shrink, 9 retain size and 0 grow versus v3.

windows: 4 files shrink, 12 retain size and 0 grow versus v3.

Android hello falls from 5,976 to 5,888 bytes against v3, but remains larger
than the earlier v2 file of 5,120 bytes. This remaining regression is retained.
The exact per-workload artifacts and hashes are in the evidence. Brainfry
remains smaller in aggregate. Component library sizes are not substituted
for complete executable sizes.

## Complete native decision calls

This separate diagnostic compares BBC v3 and optimized BBC only. It was
preregistered after the standalone runtime observations to isolate execution
from startup. All sixteen frozen sources are retained, with three fresh run
clusters, four counterbalanced pairs per case/run, eight full calls per
observation and two warmups per arm. Every call includes the full tape reset;
output/status validation follows each call outside its timer. Windows includes
ctypes overhead; Android invokes native function pointers. This is not a
Brainfry process comparison or a real-application result.

| Workload | Android v3 / optimized | Windows v3 / optimized |
|---|---:|---:|
| hello | 1.003 | 1.004 |
| binary_echo | 0.564 | 1.004 |
| wrap | 0.990 | 1.001 |
| nested_count | 0.980 | 1.005 |
| transfer_repeat | 0.937 | 1.001 |
| multi_transfer | 0.985 | 1.071 |
| scan | 0.981 | 1.017 |
| nested_math | 1.017 | 1.003 |
| clear_set | 1.000 | 1.000 |
| permit_flag | 0.997 | 1.000 |
| countdown_actions | 1.000 | 0.971 |
| checksum_four | 1.000 | 0.999 |
| clear_input | 0.631 | 0.995 |
| increment_clear | 1.007 | 1.002 |
| clear_repeat | 0.999 | 0.999 |
| nested_clear | 0.983 | 1.005 |

Geometric mean median ratios are 0.930x on Android and 1.005x on Windows. Individual changes and uncertainty remain workload-dependent.

## Post-primary native-call controls

The primary Android native-call aggregate remains **0.930x**, including
binary_echo at 0.564x and clear_input at 0.631x, although both corresponding
baseline/optimized library pairs are byte-identical. These observations
cannot be assigned to a semantic code change. No native-call runtime gain
is established by this v4 run.

A separate [post-primary diagnostic](../evidence/bfx_v4_call_controls.json)
froze four selected cases, three fresh run clusters and four call-order pairs
per cell. It tests original/reversed library loading and loading the same file
twice, recording function addresses and an additional thread-CPU diagnostic.
Every call retains full reset and output/status checking. This instrumented
collector is a diagnostic, not a replacement score or isolated causal test.
The original observations, aggregate, intervals and comparison families stay.

| Identical-library case | Original loading, baseline/optimized | Reversed loading, baseline/optimized | Same baseline file, slot 0/1 | Same optimized file, slot 0/1 |
|---|---:|---:|---:|---:|
| binary_echo | 0.995 | 1.002 | 1.000 | 1.000 |
| clear_input | 1.002 | 1.002 | 1.000 | 0.999 |

The diagnostic medians are near parity. Same-function-address trials also
vary: binary_echo's same-baseline-file pair ratios range from 0.631 to 1.892;
scan's range from 0.812 to 3.250. A systematic load-order mechanism is not
isolated; scheduling/frequency/thermal/address conditions remain uncontrolled.
The new samples neither erase the primary slowdown nor establish a pass effect.

The movement pass provides workload-dependent size/execution trade-offs.
Affine transfers, scans, generic code/package overhead and native
compiler-host integration remain the next optimization targets. No unrestricted
comparator or category sweep is declared complete.
