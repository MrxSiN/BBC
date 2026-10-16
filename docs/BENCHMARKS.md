# Benchmarks

**Current benchmark boundary (2026-10-13):** The 2026-10-12 [optimized Android native BF evidence](ANDROID_NATIVE_OPTIMIZATION.md) additionally measured 2.3514 ms for one small BF transfer/echo program against 2.3532 ms for the fastest direct-echo C variant, with a paired 95% interval spanning a tie/loss. **NOT_PROVEN_FASTEST**; neither universal C/Rust parity nor production application speed is established. The historical Linux measurements below remain valid for their recorded workloads. Planned performance gates are in [the roadmap](IMPLEMENTATION_ROADMAP.md).

**Reliable superiority to optimized C/Rust is not established.** BF's new
Android optimization improves elapsed time 4.57x. Its median narrowly leads
freestanding C, but the uncertainty interval includes a tie/loss.
[Updated native and GM evidence](ANDROID_NATIVE_OPTIMIZATION.md).
[Initial C/Rust/Java DEX/ART run](ANDROID_DEVICE_BENCHMARK.md) is historical.

## Historical results for Iterations 8–9

| Metric | Iteration 8 | Iteration 9 |
|---|---:|---:|
| Canonical BF commands | 15,518 | 15,907 |
| Self-hosted compiler ELF | 1,021,071 bytes | 509,239 bytes |
| Fixed zero padding | 524,280 bytes | 0 bytes |
| Native instruction slot | 32 bytes | 32 bytes |
| Self-hosted Stages 0–2 | Identical | Identical |

The self-compiler ELF is **511,832 bytes smaller**. The difference is file backing, not a measured runtime speedup. Compile-time counting adds BF execution work while saving disk output. The Stage 0–2 durations and BF instruction counts appear in `evidence/selfhost.json`; they are single runs, not stable comparative benchmarks.

## Needed for a real comparison

Use equivalent algorithms, inputs and output contracts in optimized C and Rust. Collect raw timed samples, repeated interleaved measurements, CPU/kernel/toolchain details, peak memory, binary sizes and compilation time. Don't compare a new BF runtime against an interpreter and call it faster than native C.

## Iteration 16: BF filter comparison (not a C/Rust baseline)

`tests/verify_stream_filter_equivalence.py` builds the historical 1,031-command and current 816-command Brainfuck stream filters using the existing native Brainfuck compiler and runs two input shapes on the same Linux execution host. Nine interleaved samples per binary/workload are recorded in [`../evidence/stream_filter_equivalence.json`](../evidence/stream_filter_equivalence.json), with raw milliseconds and medians. These short runs include process startup and are sensitive to host scheduling; don't claim statistical performance leadership from them. The Iteration 16 filter ELF was 27,959 bytes, compared with 34,839 bytes previously. Under Iteration 19 in-core filtering the same 816-instruction stream filter compiles to 26,327 bytes, due to removal of ignored source slots. The new filter is an experimental second executable, and a genuine like-for-like C/Rust comparison remains unmeasured.

## Iteration 19 compiled-size results

The native self-hosted compiler shrank from **512,727 to 475,703 bytes** as it gained in-core filtering: its own ignored source annotations no longer emit NOP slots, and the canonical source dropped to 14,859 BF commands after 39 arithmetic construction substitutions. The latter were independently checked on 9,984 isolated modulo-byte inputs. Stages 0–2 agree. These are code-size measurements, not proof of optimized execution performance relative to C or Rust.

## Iteration 22 — native Category B C comparison

A reproducible comparison has now been run on **two** identical-output nested
affine-loop workloads, each reading one byte and writing one byte. The native
BF binary is produced by the self-hosted Brainfuck compiler. The C reference
uses `cc -O3 -std=c11`, with equivalent unsigned 8-bit wrapping behavior and
identical loop structure. `rustc` was not installed on this host, so Rust
remains **UNMEASURED**. No external compiler participates in the shipping BF
compiler; C is used only as a benchmark baseline.

| Program | Native BF median | Optimized C median | BF / C |
|---|---:|---:|---:|
| `nested_affine` | 0.4945 ms | 0.6114 ms | ~0.81x |
| `nested_affine_stress` | 9.0794 ms | 0.7023 ms | **~12.93x** |

Each median uses 13 alternating-order fresh process executions with the same
input (`ad` hexadecimal); these measurements include startup and are not CPU
cycle microbenchmarks. The smaller-workload speed advantage is particularly
sensitive to startup variance and is **not** evidence of generally faster
compiled BF. The larger workload demonstrates a serious optimizer gap.
Sources, precise raw samples, environment, compiler versions and hashes are
in [`../benchmarks/results/nested_affine.json`](../benchmarks/results/nested_affine.json)
and [`../benchmarks/results/nested_affine_stress.json`](../benchmarks/results/nested_affine_stress.json).
The exact samples can vary between runs; the source and command counts are
fixed. The Python benchmark driver is measurement infrastructure only.

```sh
python3 tests/verify_native_benchmark_contract.py
python3 benchmarks/compare_native.py --case nested_affine
python3 benchmarks/compare_native.py --case nested_affine_stress
```

These are not actual Gmail/Twitter/Threads/G29 policy workloads and do not
compare against their existing compiler backends. In particular, neither the
0.9999x cross-workload performance target nor superiority to C/Rust has been
established. This benchmark identifies a performance regression priority:
fold loops and arithmetic before allocating 32-byte native instruction slots.
