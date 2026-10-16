# Iteration 50 — Android dynamic code size and disk-backed bracket pairing

## Scope and result

This iteration **does not complete the universal Android compiler**. It replaces two fixed resource assumptions in **separate, opt-in, Brainfuck-owned experimental stages** and verifies their native-Linux execution. Every executable source stage contains only the eight standard Brainfuck instructions. Development-time Python macros author those `.bf` sources, but no Python compiler/assembler runs when processing user Brainfuck source. The host provides lossless byte transport, output transactions, and a generic expandable byte stack.

### 1. Compact streaming AArch64 machine instructions

[`android_streaming_compact_slots.bf`](../experiments/android_streaming_compact_slots.bf) compiles to [`android_streaming_compact_slots_x86_64_linux.elf`](../build/android_streaming_compact_slots_x86_64_linux.elf). It accepts arbitrary raw source bytes through a simple presence frame, recognizes `+ - > < . ,`, ignores noninstruction bytes, and emits length-prefixed **AArch64 instruction bytes**. Its output is raw code, **not** an ELF or Android shared library. Brackets are explicitly rejected. The existing 48-byte padded instruction templates are unchanged in executable content; only unused trailing AArch64 NOP words are removed.

| BF operation | Old slot bytes | Compact bytes |
| --- | ---: | ---: |
| `+` or `-` | 48 | 12 |
| `>` or `<` | 48 | 28 |
| `.` | 48 | 40 |
| `,` | 48 | 48 |

A real 300,001-command `+` source generated **3,600,012 raw code bytes**, versus 14,400,048 with the old layout. A separate **1,000,000-command** source emitted 12,000,000 raw AArch64 code bytes in **17.887 seconds** on the available Linux host. That result is for a uniform arithmetic source, not diverse 1M programs. There is no command-count table or hard-coded output length in this new stage; source storage, output capacity, and throughput are resource-constrained. The transport atomically preserves a previous output when BF rejects brackets or when an optional output-byte quota is exceeded.

The suite passed **159 byte-by-byte instruction-stream comparisons**, **150 AArch64 test-oracle instruction executions**, and **54 expected pointer-trap observations** within those executions. These test-oracle executions use a synthesized test-only ELF overlay and **are not newly generated loadable ELFs**, nor actual Android execution. Source and machine-code hashes are in [`iteration50_android_compact_stream.json`](../evidence/iteration50_android_compact_stream.json).

### 2. Dynamic file-backed bracket stack

[`android_dynamic_stack_pairs.bf`](../experiments/android_dynamic_stack_pairs.bf) controls a generic stack service. It requests the next source event, pushes opening positions, pops at closing positions, tests for empty-stack completion, emits matching pairs, and rejects unmatched brackets. The host stores opaque 8-byte positions in a dynamically extended temporary file, with **no fixed 255-level table** and no application-specific matching logic. This is a host-provided memory device controlled by BF, **not standalone BF memory growth**.

The BF-owned [`android_pair_event_bridge.bf`](../experiments/android_pair_event_bridge.bf) adapts the earlier BF scanner's **32-bit** source positions into eight-byte stack records. The scanner still has the 32-bit source-position limit; independent generic stack-device tests verified full **64-bit stored values**, but have **not verified 64-bit source scanning**.

The integrated scanner→BF bridge→BF stack route passed **104 source cases** (100 accepted, 4 rejected), successfully nested **4,096 levels**, and matched a loop spanning a real **100,000,002-byte source** with closing position 100,000,001. Two independently implemented C Brainfuck interpreters matched the BF stack stage's request/response transcript. Invalid event tags, underflow, unclosed brackets, and caller pair quotas do not overwrite previous results. Details: [`iteration50_android_dynamic_stack.json`](../evidence/iteration50_android_dynamic_stack.json).

### 3. Unchanged trust and platform gates

- [`compiler/core.bf`](../compiler/core.bf) remains the authoritative Linux BF compiler; its previously established self-hosting fixed point must be preserved.
- The pre-existing **complete** Android ELF backend is still capped at **2,719 commands** for the tested all-eight-instruction path. It does not use the new compact/dynamic-stack stages.
- The previous bounded Android-native self-hosting proof is archived, not rerun on an Android device in this iteration.
- The eleven original GmailHideAds/TwitterHideAds/ThreadsHideAds policy sources have **not** been compiled through these new stages. No Android APK, JNI-loadable `.so`, target-native 100M executable, or new device run exists.

### 4. Required integration before claiming dynamic native compilation

1. Replace the current 32-bit source scanner with BF-owned 64-bit (or validated larger) source and output offsets, retaining generic compression as transport only.
2. Merge the BF compact instruction writer and dynamic pair stream into one all-eight-instruction pipeline. Source-relative positions are **not** native-code byte offsets once slot lengths vary.
3. Compute native-code addresses and long-distance branch relocation in standard BF, with range validation or veneers, rather than using host-side machine-code patch arithmetic.
4. Build fully dynamic ELF64/Android shared-library segment layouts in BF using checked 64-bit file sizes. Preserve tape memory, EOF-zero, pointer trap and ABI semantics.
5. Compile the eleven pinned real policies, run their original byte-protocol/JNI parity suites, then obtain actual Android loader/device execution and native self-hosting for the general compiler.

Practical scaling means no gratuitous count/depth tier; finite RAM, disk, address ranges, execution time, and target ABI limits still apply. Fail atomically on resource or encoding exhaustion. **No full dynamic Android compiler acceptance is claimed for this iteration.**

## Reproduce

From the repository root:

```text
python3 tests/verify_android_compact_stream.py
python3 tests/verify_android_dynamic_stack.py
python3 tools/sync_status.py
python3 tools/check_docs.py
```

The 100MB source test writes a temporary source file and verifies scanner/pairing. The 1M compact test is recorded separately in [`iteration50_million_linear.json`](../evidence/iteration50_million_linear.json).
