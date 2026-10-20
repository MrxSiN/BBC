# BFX v2 optimization measurements

> Format migration note: measurements and source identities below describe their
> pinned pre-migration snapshots. Historical version names identify that evidence,
> not current decoder modes. Current production uses only [BFX](02_BFX_CONTRACT.md).
> No migration performance or broader completion claim follows from these reports.


The optional Brainfuck pass folds exact clear loops and removes complete
256-command same-direction arithmetic groups. This report measures that pass
and its canonical XAX consumer; the competitive objective remains **NOT YET
ACHIEVED**. [Proofs](07_OPTIMIZATION_PROOFS.md#p1-clear-loops-and-full-arithmetic-wraps)
and the [v2 contract](10_CLEAR_OPTIMIZATION.md) specify the implementation.

[Complete immutable evidence](../evidence/bfx_v2_optimization.json) contains
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
frontend, canonical validator, optional native BF pass and native importer
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
preparation stay outside. There is no overhead subtraction. Eight unchanged
program binaries are byte-identical across BBC arms and provide a noise control.

There are three independent run clusters and ten observations per arm/case
in each, plus warmups. All six three-arm orders occur five times. Jobs are
serial; frequency, affinity, thermals and ordinary background maintenance/work
are uncontrolled. The three-cluster paired bootstrap intervals are exploratory.
Exact two-sided run-level sign flips have minimum p = 0.25; Holm-adjusted
per-case tests support no confirmatory superiority claim. The evidence gives
quartiles and keeps paired-log interval estimates separate from median ratios.

## Complete build and process time

Values below are geometric means of sixteen workload medians, in milliseconds.
Lower time is better; a reference/optimized ratio above one favors optimized BBC.

| Target | Boundary | BBC v1 | BBC optimized | Brainfry | BBC v1 / optimized | Brainfry / optimized |
|---|---|---:|---:|---:|---:|---:|
| android | runtime | 7.335 | 7.019 | 6.172 | 1.045 | 0.879 |
| android | build | 1345.546 | 1347.989 | 30.182 | 0.998 | 0.022 |
| windows | runtime | 27.318 | 27.223 | 28.117 | 1.003 | 1.033 |
| windows | build | 1430.176 | 1432.855 | 30.171 | 0.998 | 0.021 |

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

| Workload | BBC v1 | Optimized | Brainfry | BBC v1 / optimized |
|---|---:|---:|---:|---:|
| hello | 5.4858 | 5.2485 | 5.2122 | 1.045 |
| binary_echo | 6.1034 | 5.5299 | 5.4065 | 1.104 |
| wrap | 5.4510 | 5.6653 | 5.1375 | 0.962 |
| nested_count | 5.2873 | 5.8548 | 5.0855 | 0.903 |
| transfer_repeat | 8.4631 | 8.4965 | 6.3256 | 0.996 |
| multi_transfer | 13.2259 | 9.2563 | 5.3934 | 1.429 |
| scan | 5.6482 | 5.3091 | 5.1771 | 1.064 |
| nested_math | 75.0908 | 79.6627 | 45.4893 | 0.943 |
| clear_set | 7.7921 | 6.4975 | 6.0119 | 1.199 |
| permit_flag | 5.6426 | 5.4420 | 4.9630 | 1.037 |
| countdown_actions | 5.3271 | 5.7454 | 5.2734 | 0.927 |
| checksum_four | 5.2851 | 5.5988 | 5.5861 | 0.944 |
| clear_input | 4.9430 | 5.2204 | 4.7392 | 0.947 |
| increment_clear | 5.7573 | 5.4966 | 5.4503 | 1.047 |
| clear_repeat | 6.9700 | 5.4676 | 6.3798 | 1.275 |
| nested_clear | 6.2362 | 6.0700 | 5.1787 | 1.027 |

### Windows

| Workload | BBC v1 | Optimized | Brainfry | BBC v1 / optimized |
|---|---:|---:|---:|---:|
| hello | 27.1609 | 27.5883 | 27.0158 | 0.985 |
| binary_echo | 26.2168 | 26.2810 | 26.8299 | 0.998 |
| wrap | 26.2833 | 27.3698 | 26.6940 | 0.960 |
| nested_count | 26.8288 | 25.9398 | 26.4569 | 1.034 |
| transfer_repeat | 26.6705 | 26.3957 | 26.5671 | 1.010 |
| multi_transfer | 27.5528 | 27.5193 | 26.9091 | 1.001 |
| scan | 25.4177 | 25.3627 | 25.9657 | 1.002 |
| nested_math | 38.2504 | 38.8196 | 52.7737 | 0.985 |
| clear_set | 25.4354 | 25.3184 | 26.0692 | 1.005 |
| permit_flag | 25.9520 | 26.8634 | 27.1723 | 0.966 |
| countdown_actions | 27.6549 | 26.9755 | 27.4915 | 1.025 |
| checksum_four | 27.5117 | 26.5562 | 27.7162 | 1.036 |
| clear_input | 26.3229 | 25.8601 | 26.0184 | 1.018 |
| increment_clear | 26.7714 | 26.2171 | 29.2936 | 1.021 |
| clear_repeat | 27.3766 | 27.5406 | 27.0110 | 0.994 |
| nested_clear | 27.6791 | 27.1722 | 27.3875 | 1.019 |

## Memory and complete file size

Memory is the geometric mean of workload median lifetime resident high-water
counters, in MiB. Windows uses retained-handle kernel peak working set after
exit. Each measured build worker has one required process. Peak pagefile data
remain separate raw counters, not job peak commit. Android uses child wait4
ru_maxrss in KiB; shared pages and a fork/loader floor limit small-program
attribution. Excluded touched-16-MiB controls validate the units. These data
establish no statistical memory victory.

| Target | Boundary | BBC v1 MiB | Optimized MiB | Brainfry MiB |
|---|---|---:|---:|---:|
| android | runtime | 1.189 | 1.190 | 1.189 |
| android | build | 51.042 | 51.001 | 5.299 |
| windows | runtime | 4.589 | 4.588 | 4.544 |
| windows | build | 51.008 | 51.030 | 5.306 |

Complete PE/ELF bytes, geometric mean across the same sixteen programs:

| Target | BBC v1 bytes | Optimized bytes | Brainfry bytes |
|---|---:|---:|---:|
| android | 3677.8 | 3643.7 | 1139.8 |
| windows | 21951.0 | 21500.5 | 2890.2 |

Eight workloads per target shrink; the others retain their sizes. Brainfry
remains smaller. The complete artifacts and hashes are in the evidence;
component library sizes are not substituted for executable sizes.

## Complete native decision calls

This separate diagnostic compares BBC v1 and optimized BBC only. It was
preregistered after the standalone runtime observations to isolate execution
from startup. All sixteen frozen sources are retained, with three fresh run
clusters, ten counterbalanced pairs per case/run, eight full calls per
observation and two warmups per arm. Every call includes the full tape reset;
output/status validation follows each call outside its timer. Windows includes
ctypes overhead; Android invokes native function pointers. This is not a
Brainfry process comparison or a real-application result.

| Workload | Android v1 / optimized | Windows v1 / optimized |
|---|---:|---:|
| hello | 1.055 | 0.997 |
| binary_echo | 0.999 | 1.001 |
| wrap | 1.000 | 0.992 |
| nested_count | 0.998 | 0.993 |
| transfer_repeat | 0.999 | 0.982 |
| multi_transfer | 1.318 | 1.142 |
| scan | 1.186 | 1.083 |
| nested_math | 1.000 | 0.999 |
| clear_set | 2.099 | 1.762 |
| permit_flag | 1.032 | 0.993 |
| countdown_actions | 1.000 | 1.003 |
| checksum_four | 1.032 | 0.912 |
| clear_input | 1.155 | 1.033 |
| increment_clear | 1.157 | 1.040 |
| clear_repeat | 28.805 | 7.418 |
| nested_clear | 1.844 | 1.625 |

Geometric mean median ratios are 1.416x on Android and 1.222x on Windows. Individual changes and uncertainty remain workload-dependent.

The semantic pass is retained for smaller transformed programs and reduced
clear-loop execution work, with its extra build stage exposed. Immediate
arithmetic, affine transfers, scans, generic code/package overhead and native
compiler-host integration remain the next optimization targets. No unrestricted
comparator or category sweep is declared complete.
