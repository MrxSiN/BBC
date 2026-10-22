# 📊 Status

> What works today, what doesn't yet, and where the proof lives.

Updated **2026-10-22**.

---

## ✅ Working

| Area | State |
|---|---|
| **Compile** | `bbc.exe compile` turns Brainfuck into Windows x86-64 and Android ARM64 programs in one native process, no Python ([native compile](25_NATIVE_COMPILE.md)) |
| **Format** | One [BFX format](02_BFX_CONTRACT.md): magic `42 46 58 00`, id `01`. No fallback, no legacy decoder |
| **Levels** | O0 keeps primitives; O1 packs runs and folds safe clear loops. O2/O3 don't exist yet |
| **Correctness** | 83 programs × O0/O1 × 2 targets: 332 builds and 588 runs match an independent interpreter |
| **Competitors** | All 18 [benchmark](08_BENCHMARKS.md) programs give correct output |
| **Devices** | Earlier artifacts ran on a Pixel 8 Pro and Windows 11; new builds reproduce them byte for byte |
| **Self-hosting** | Three identical native own-source frontend generations on each target |

**Limits** (fixed budgets, not growth):

- Public entry: 1 MiB source, 65,536 instructions before packing, depth 32,768.
- Bounded seed: 65,533 bytes, 3,840 instructions, depth 255.
- Program tape: 65,536 wrapping byte cells, checked movement, EOF reads 0.

---

## 🚧 Not yet

- 🐢 **Generated code is slow on heavy compute.** Mandelbrot takes about 22 s
  vs 0.5–1.7 s for the competitors. Loop optimizations (affine, scan, offset) are missing.
- ⏱️ **Build time** is about 0.1 s for small programs under Wine; native competitors
  take 4–80 ms. Lowering is the biggest cost.
- 📱 **Android:** no off-main-thread worker for unbounded programs; no
  Android-hosted compiler.
- 📦 **Windows DLL packaging** and common helper loading are open.
- 🐧 **Linux** is optional and not a target. Cross-compiling doesn't count.
- 🧩 **XAX OI-49** (large ARM64 composite returns) is open; the importer avoids it.
- 🏁 **Milestones:** M4 incomplete, M8 not achieved. No performance lead is claimed.

---

## 📚 Evidence index

Each report is an immutable snapshot for the sources it names.

### 🏁 Benchmarks

| Report | What it shows |
|---|---|
| [competitor_benchmark_2026-10-22.json](../evidence/competitor_benchmark_2026-10-22.json) | **Current.** BBC vs 8 compilers: 18 programs, build, run, size, RAM |
| [competition_pilot.json](../evidence/competition_pilot.json) | First Awib/brainfry pilot; competitor pins |
| [brainfly_brainfry_followup.json](../evidence/brainfly_brainfry_followup.json) | Brainfly correctness, brainfry optimizer defects |
| [build_runtime_resources.json](../evidence/build_runtime_resources.json) | Earlier build latency and memory |
| [modernization_baseline.json](../evidence/modernization_baseline.json) | Frozen baseline: 180 builds |
| [scalability_capacity_audit.json](../evidence/scalability_capacity_audit.json) | brainfry Mandelbrot resource-cap rejection |

### ⚙️ Native compile

| Report | What it shows |
|---|---|
| [native_proof_cache.json](../evidence/native_proof_cache.json) | Each graph checked once per compile |
| [native_lazy_views.json](../evidence/native_lazy_views.json) | Peak commit 3,398 → under 140 MiB |
| [native_single_process.json](../evidence/native_single_process.json) | Driver inside `bbc.exe` |
| [native_compile.json](../evidence/native_compile.json) | Python-free source-to-executable path |
| [xax_alias_index.json](../evidence/xax_alias_index.json) | ARM64 alias scan via incoming-edge index |
| [native_android_lowering.json](../evidence/native_android_lowering.json) | All 22 Android snapshots, 47 Pixel runs |
| [android_hello_smoke.json](../evidence/android_hello_smoke.json) | 5,880-byte Android hello |
| [native_windows_lowering.json](../evidence/native_windows_lowering.json) | Windows pointer frames, byte arithmetic |
| [native_bits1.json](../evidence/native_bits1.json) | One-bit AND/OR/XOR lowering |
| [unified_compilation.json](../evidence/unified_compilation.json) | One public compile entry |

### 🧾 Format and frontend

| Report | What it shows |
|---|---|
| [canonical_bfx.json](../evidence/canonical_bfx.json) | Current BFX: decoder, importer, frontend, Mandelbrot |
| [frontend_capacity_gate.json](../evidence/frontend_capacity_gate.json) | Carry-triggered capacity flag |
| [stream_runs.json](../evidence/stream_runs.json) | Streaming run packer |
| [wide_profile.json](../evidence/wide_profile.json) · [wide_bootstrap.json](../evidence/wide_bootstrap.json) · [wide_final_audit.json](../evidence/wide_final_audit.json) · [wide_tape_reset.json](../evidence/wide_tape_reset.json) | Large programs and full tape reset |
| [streaming_frontend_prototype.json](../evidence/streaming_frontend_prototype.json) · [streaming_frontend_bootstrap.json](../evidence/streaming_frontend_bootstrap.json) · [streaming_frontend_verification.json](../evidence/streaming_frontend_verification.json) | Chunked source filter |
| [frontend_filter_windows.json](../evidence/frontend_filter_windows.json) · [frontend_filter_android.json](../evidence/frontend_filter_android.json) · [frontend_filter_profile.json](../evidence/frontend_filter_profile.json) | Source filter |
| [frontend_counter_windows.json](../evidence/frontend_counter_windows.json) · [frontend_counter_android.json](../evidence/frontend_counter_android.json) · [frontend_counter_profile.json](../evidence/frontend_counter_profile.json) | Instruction counter |
| [source_capacity.json](../evidence/source_capacity.json) · [source_capacity_android.json](../evidence/source_capacity_android.json) | Capacity checks |

### 🔁 Optimizations

| Report | What it shows |
|---|---|
| [bfx_v2_optimization.json](../evidence/bfx_v2_optimization.json) | Clear and full-wrap loops |
| [bfx_v3_arithmetic.json](../evidence/bfx_v3_arithmetic.json) · [bfx_v3_measurements.json](../evidence/bfx_v3_measurements.json) | Arithmetic packing |
| [bfx_v4_movement.json](../evidence/bfx_v4_movement.json) · [bfx_v4_measurements.json](../evidence/bfx_v4_measurements.json) · [bfx_v4_native_boundaries.json](../evidence/bfx_v4_native_boundaries.json) · [bfx_v4_call_controls.json](../evidence/bfx_v4_call_controls.json) | Movement packing |

### 🧱 Hosts and driver history

| Report | What it shows |
|---|---|
| [standalone_windows.json](../evidence/standalone_windows.json) · [standalone_android.json](../evidence/standalone_android.json) · [standalone_native_replay.json](../evidence/standalone_native_replay.json) | Standalone process hosts |
| [windows_native_driver.json](../evidence/windows_native_driver.json) · [windows_native_driver_followup.json](../evidence/windows_native_driver_followup.json) · [windows_native_resource_diagnosis.json](../evidence/windows_native_resource_diagnosis.json) · [windows_native_verification_profile.json](../evidence/windows_native_verification_profile.json) | Early native driver |
| [windows_hash_host.json](../evidence/windows_hash_host.json) | Native hashing host |
| [graph_verification_profile.json](../evidence/graph_verification_profile.json) · [backend_build_cache.json](../evidence/backend_build_cache.json) | Verification cost, cold cache |

### 🗃️ Migration and cleanup

| Report | What it shows |
|---|---|
| [bfx_migration.json](../evidence/bfx_migration.json) · [bfx_android_importer.json](../evidence/bfx_android_importer.json) · [bfx_xax_import.json](../evidence/bfx_xax_import.json) · [bfx_retirement.json](../evidence/bfx_retirement.json) | Move to BFX and the XAX importer |
| [format_cleanup.json](../evidence/format_cleanup.json) · [repository_cleanup.json](../evidence/repository_cleanup.json) | Retired formats and files, archived outside the repo |
