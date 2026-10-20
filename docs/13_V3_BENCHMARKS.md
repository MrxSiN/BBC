# BFX v3 arithmetic measurements

The optional Brainfuck pass packs consecutive arithmetic into powers of two.
This report compares v2 baseline and v3 arithmetic packing
and its canonical XAX consumer; the competitive objective remains **NOT YET
ACHIEVED**. [Proofs](07_OPTIMIZATION_PROOFS.md#p1-arithmetic-powers)
and the [v3 contract](12_BFX_V3_ARITHMETIC.md) specify the implementation.

[Complete immutable evidence](../evidence/bfx_v3_measurements.json) contains
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

Each complete build starts a fresh required compiler process and ends after
the standalone executable is written and the process exits. BBC's native BF
frontend, canonical validators, native BF clear/arithmetic passes and importer
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
preparation stay outside. There is no overhead subtraction. Nine unchanged
program binaries are byte-identical across BBC arms and provide a noise control.

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

| Target | Boundary | BBC v2 | BBC optimized | Brainfry | BBC v2 / optimized | Brainfry / optimized |
|---|---|---:|---:|---:|---:|---:|
| android | runtime | 6.275 | 5.825 | 5.432 | 1.077 | 0.933 |
| android | build | 1249.782 | 1143.032 | 26.927 | 1.093 | 0.024 |
| windows | runtime | 26.000 | 25.758 | 26.720 | 1.009 | 1.037 |
| windows | build | 1331.624 | 1171.857 | 26.938 | 1.136 | 0.023 |

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

| Workload | BBC v2 | Optimized | Brainfry | BBC v2 / optimized |
|---|---:|---:|---:|---:|
| hello | 5.0049 | 4.9366 | 5.0963 | 1.014 |
| binary_echo | 4.8517 | 4.7482 | 4.5395 | 1.022 |
| wrap | 4.8861 | 4.5443 | 4.6280 | 1.075 |
| nested_count | 5.1325 | 4.8392 | 4.7882 | 1.061 |
| transfer_repeat | 7.2487 | 6.5974 | 5.1739 | 1.099 |
| multi_transfer | 8.3892 | 6.9494 | 4.6567 | 1.207 |
| scan | 5.5132 | 4.6013 | 4.8859 | 1.198 |
| nested_math | 70.7051 | 48.6159 | 28.8196 | 1.454 |
| clear_set | 6.0555 | 4.7108 | 5.1774 | 1.285 |
| permit_flag | 4.7906 | 5.3849 | 4.6547 | 0.890 |
| countdown_actions | 4.8782 | 4.5341 | 4.8785 | 1.076 |
| checksum_four | 5.0013 | 5.1041 | 4.5421 | 0.980 |
| clear_input | 4.5827 | 4.7569 | 4.5198 | 0.963 |
| increment_clear | 4.9733 | 5.1496 | 4.7654 | 0.966 |
| clear_repeat | 4.9123 | 4.7075 | 5.7869 | 1.043 |
| nested_clear | 5.0469 | 4.9040 | 4.9630 | 1.029 |

### Windows

| Workload | BBC v2 | Optimized | Brainfry | BBC v2 / optimized |
|---|---:|---:|---:|---:|
| hello | 25.6114 | 26.1285 | 25.7390 | 0.980 |
| binary_echo | 24.4179 | 25.7437 | 24.8578 | 0.949 |
| wrap | 26.1908 | 25.6163 | 26.8000 | 1.022 |
| nested_count | 24.9032 | 25.9888 | 24.9756 | 0.958 |
| transfer_repeat | 25.5271 | 25.5495 | 26.2709 | 0.999 |
| multi_transfer | 27.2623 | 25.6461 | 25.6168 | 1.063 |
| scan | 25.6466 | 25.3145 | 25.8293 | 1.013 |
| nested_math | 37.2903 | 32.1870 | 52.0263 | 1.159 |
| clear_set | 24.5218 | 24.5832 | 25.1480 | 0.998 |
| permit_flag | 25.5333 | 25.0128 | 24.9513 | 1.021 |
| countdown_actions | 25.1918 | 24.7548 | 25.9505 | 1.018 |
| checksum_four | 25.2458 | 25.5542 | 25.6255 | 0.988 |
| clear_input | 24.7010 | 24.6138 | 24.7230 | 1.004 |
| increment_clear | 24.9772 | 25.9864 | 26.0134 | 0.961 |
| clear_repeat | 25.6131 | 25.2660 | 25.7721 | 1.014 |
| nested_clear | 25.5280 | 24.9862 | 25.2062 | 1.022 |

## Memory and complete file size

Memory is the geometric mean of workload median lifetime resident high-water
counters, in MiB. Windows uses retained-handle kernel peak working set after
exit. Each measured build worker has one required process. Peak pagefile data
remain separate raw counters, not job peak commit. Android uses child wait4
ru_maxrss in KiB; shared pages and a fork/loader floor limit small-program
attribution. Excluded touched-16-MiB controls validate the units. These data
establish no statistical memory victory.

| Target | Boundary | BBC v2 MiB | Optimized MiB | Brainfry MiB |
|---|---|---:|---:|---:|
| android | runtime | 1.176 | 1.177 | 1.177 |
| android | build | 51.223 | 50.974 | 5.300 |
| windows | runtime | 4.589 | 4.588 | 4.545 |
| windows | build | 51.146 | 50.992 | 5.305 |

Complete PE/ELF bytes, geometric mean across the same sixteen programs:

| Target | BBC v2 bytes | Optimized bytes | Brainfry bytes |
|---|---:|---:|---:|
| android | 3643.7 | 2742.9 | 1139.8 |
| windows | 21500.5 | 14183.1 | 2890.2 |

Seven Windows workloads shrink and nine retain their sizes. Android has six
shrinking workloads, nine unchanged and a 16.7% hello growth. Brainfry
remains smaller. The complete artifacts and hashes are in the evidence;
component library sizes are not substituted for executable sizes.

## Complete native decision calls

This separate diagnostic compares BBC v2 and optimized BBC only. It was
preregistered after the standalone runtime observations to isolate execution
from startup. All sixteen frozen sources are retained, with three fresh run
clusters, four counterbalanced pairs per case/run, eight full calls per
observation and two warmups per arm. Every call includes the full tape reset;
output/status validation follows each call outside its timer. Windows includes
ctypes overhead; Android invokes native function pointers. This is not a
Brainfry process comparison or a real-application result.

| Workload | Android v2 / optimized | Windows v2 / optimized |
|---|---:|---:|
| hello | 1.049 | 1.011 |
| binary_echo | 0.998 | 1.001 |
| wrap | 0.993 | 1.006 |
| nested_count | 1.001 | 1.002 |
| transfer_repeat | 1.511 | 1.245 |
| multi_transfer | 2.529 | 1.558 |
| scan | 0.995 | 1.005 |
| nested_math | 1.942 | 1.467 |
| clear_set | 20.446 | 7.996 |
| permit_flag | 1.000 | 0.995 |
| countdown_actions | 1.000 | 0.999 |
| checksum_four | 1.004 | 0.970 |
| clear_input | 1.000 | 1.003 |
| increment_clear | 0.990 | 1.018 |
| clear_repeat | 1.106 | 1.080 |
| nested_clear | 1.814 | 1.202 |

Geometric mean median ratios are 1.432x on Android and 1.236x on Windows. Individual changes and uncertainty remain workload-dependent.

The arithmetic pass provides workload-dependent size/execution trade-offs;
its extra build stage and Android hello growth remain exposed. Movement
packing, affine transfers, scans, generic code/package overhead and native
compiler-host integration remain the next optimization targets. No unrestricted
comparator or category sweep is declared complete.
