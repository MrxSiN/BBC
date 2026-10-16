# Iteration 58 — resource-scaled callable AArch64 with nested loops

## Implemented

This iteration connects the **existing standard-Brainfuck-controlled file-backed bracket stack** and signed-64-bit relocation stages to a new **callable** AArch64 emitter. The previous dynamic callable path handled only six loop-free instructions; the new path handles all eight ordinary Brainfuck commands, including nested loops, without a fixed command table or a 255-level bracket stack.

- `experiments/android_callable_slots58.bf` emits native callable instruction records after filtering raw source characters. Each open loop uses a 14-word veneer plus execution-budget check. Each close loop uses an eight-word veneer. Both contain opaque 64-bit PC-relative branch literal placeholders. The implementation uses `x15` and `x17` as volatile scratch; **Android-reserved `x18` is not touched**.
- `experiments/android_callable_ledger58.bf` records exact 64-bit native word positions. It counts the expanded 14-word open-loop prologue and eight-word close-loop slots. It detects 64-bit position overflow.
- The existing BF-controlled file-backed stack pairs nested bracket records, and the existing BF `span64`, `position53` and `delta53` stages calculate signed long-range jump literals. The host stores, retrieves, and patches *opaque data* at BF-generated indices; it does not decide which command or loop was present, or encode target branches.
- `bootstrap/android_dynamic_callable58.py` connects the stages, adds entry/return bytes emitted by the original BF linear callable stage, and adds the 64-bit ELF segment size emitted by the BF header stage. Output replacement is transactional and rejects malformed source, quota failures, and stage failures without publishing partial artifacts.
- The generic transport's record-length validation now accepts up to 252 bytes per code chunk, instead of the previous 48-byte assumption, to permit growing callable loop templates. This is a generic length validation, not an ISA or BF-specific code generator.

## Execution and safety contract

**Artifact:** AArch64 ELF64 `ET_DYN`, one read/execute load segment, callable code starting at file offset 128, `BFP1` header. It is **not** yet an Android-linkable shared library; it has no JNI exports or verified Android dynamic-linker integration.

The callable convention expects input address/length (`x0`,`x1`), output address/capacity (`x2`,`x3`), initialized tape/cell count (`x4`,`x5`), nonnegative loop-entry budget (`x6`), and output-used pointer (`x7`). Each nonzero opening `[` consumes one unit of execution budget; with none remaining it returns status 1, including output count and used budget. Zero-valued loops skip without consuming budget. Output exhaustion records status 2 without writing beyond the output buffer. Pointer underflow/overflow returns status 3 before dereference. Cells wrap modulo 256 and EOF stores zero. Initial tape contents and memory persistence are caller responsibilities.

The BF source is the entire eight-command language. The output instruction loop templates and relocation records are internal data, not new source operators.

Signed relative offsets are stored as 64-bit word deltas and applied through `ADR`, literal `LDR`, scaled `ADD`, and `BR`, so AArch64 direct conditional-branch reach is not an assumed global source-size limit. The compiler still requires output representability and available CPU, disk, memory, process runtime and host 64-bit address space. It does not provide an infinite tape or infinite file.

## Fresh evidence

Run:

```sh
python3 -m bootstrap.build_android_dynamic_callable58
python3 -m tests.verify_android_dynamic_callable58
python3 -m bootstrap.android_dynamic_callable58 examples/nested.bf -o build/iteration58_dynamic/nested58.elf
readelf -Wl build/iteration58_dynamic/nested58.elf
```

- Both new BF stages rebuild **byte-identically** using the canonical native Linux BF compiler; their BF instruction counts are **7,346** and **10,978**.
- **59** source programs, **354** independent AArch64 instruction-simulator executions, **2,772** BF-owned 64-bit patch operations, **4** independent-interpreter stage checks, and **6** byte-identical loop-free regressions against Iteration 57.
- Explicit tests cover modulo arithmetic, nested transfer loops, zero-skipped loops, loop-entry budget, output quotas, tape traps, EOF, ignored/NUL source bytes, 1,030 nested bracket levels, 6,000 straight-line commands, and a 1,048,599-byte raw input.
- Six invalid-bracket tests plus two explicit quotas reject without modifying the prior output image.
- Original pinned **Gmail `row`**, **Gmail `scope`**, and filtered **Twitter `action`** sources each produce AArch64 callable ELFs in this lane. Their exact new image sizes, hashes and BF-controlled pair counts are recorded in `evidence/iteration58_original_policy_compiles.json`. These were **not** executed through an Android dynamic loader, original JNI ABI, or real application policies. Only three of the eleven source files are present locally for this milestone; the remaining eight must be obtained and hash-verified against the pinned manifest before compilation.

Evidence: `evidence/iteration58_dynamic_callable_loops.json` and `evidence/iteration58_original_policy_compiles.json`. The 354 simulator executions are not Android device runs and do not constitute formal proof of memory safety. Filesystem-backed Python transport remains a production dependency for this experimental lane, and **the entire compiler is not yet Android-native/self-hosting**. The unchanged canonical Linux BF compiler remains self-hosted.

## Remaining acceptance gates

1. Acquire the other eight pinned original Twitter and Threads BF files and compile/verify all eleven in this path.
2. Provide BF-generated Android ELF shared-library metadata and a documented Android JNI/BFP1 bridge, with host-side tape and persistence semantics intact; validate loader acceptance on a real supported Android environment.
3. Run original application parity and device instrumentation (including recursive callbacks and persistence), check resource use, benchmark callable execution, and complete a target-native compiler self-hosting cycle.
4. Only after the new path passes these gates, delete the bounded callable/old freestanding production fallbacks; preserve archived evidence and any independent regression tools.

The 100-million-command artificial target remains retired. There is no new numeric command-count acceptance target.
