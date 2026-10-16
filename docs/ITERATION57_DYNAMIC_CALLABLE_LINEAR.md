# Iteration 57 — dynamic callable AArch64 path, linear instruction milestone

## Purpose

The 100-million-command native compilation target has been **retired**. There is no replacement number. The active target is a **resource-scaled, fully callable Android AArch64 compiler**, with compiler-controlled semantics and native emission implemented using only the eight standard Brainfuck instructions. Source size, IR length, nesting, relocation indices and output size must be limited by available resources and representable machine formats, **not arbitrary arrays or milestone counters**.

This iteration implements the first independent, growing **callable** ELF lane. Unlike the earlier growing **freestanding** ELF emitter, this code uses the existing `BFP1` policy calling convention rather than Linux-style process startup and syscalls. It is deliberately incomplete: brackets are rejected transactionally. Do not use it for Twitter, Threads, Gmail, or another program with loops yet.

## New standard-Brainfuck implementation

- [`../experiments/android_callable_linear57.bf`](../experiments/android_callable_linear57.bf) reads generic length-prefixed raw-byte transport records `(present, byte)` and generates callable AArch64 machine-code bytes directly. Unknown source characters, including embedded NULs, are ignored; the source language remains the original eight instructions. The emitter supports `+`, `-`, `>`, `<`, `,` and `.` and explicitly rejects `[` or `]` through an end status byte.
- [`../experiments/android_callable_header57.bf`](../experiments/android_callable_header57.bf) reads the BF-generated native code byte length, performs a checked unsigned 64-bit addition of the 128-byte ELF header, and emits both segment lengths and the `BFP1` metadata. 64-bit overflow produces a nonzero status.
- [`../bootstrap/android_dynamic_callable57.py`](../bootstrap/android_dynamic_callable57.py) provides **generic** framed input, file-backed output, length transport and atomic file replacement. It does not recognize a BF command, parse brackets, optimize, choose instructions, or calculate ELF fields. It preserves the existing target on every rejection. Python and file-backed staging are currently an explicit transport dependency, not a self-contained Android-native compiler binary.

The new loop-free code path has no fixed source-size or record-count array. It emits a normal AArch64 `ET_DYN` single RX segment and starts callable code at file offset `0x80`. Its convention expects caller-provided input, input length, output buffer, output length, tape pointer, tape cells, execution budget and output-length pointer in `x0` through `x7`. Tape must contain at least one writable byte and is zero initialized by the host according to the selected policy. The loop-free code uses per-movement bounds checks; the `BFP1` static pointer shortcut is intentionally disabled. Overflowing the output buffer preserves the existing status-2 contract; tape escape returns status 3 after reporting used output length.

An ELF containing callable code is **not automatically a JNI-exporting `.so`**. The emitted image lacks Android shared-library export metadata and has not been run by the Android dynamic loader. The existing native-stage compiler is Linux x86-64 and has a separate 16,128-instruction source bound; the two new BF sources fit within it. This is not Android-native self-hosting evidence.

## Executed evidence

Reproduce:

```sh
python3 tools/author_dynamic_callable57.py
python3 -m tests.verify_android_dynamic_callable57
python3 bootstrap/android_dynamic_callable57.py path/to/loop_free.bf -o path/to/callable.elf
readelf -Wl path/to/callable.elf
```

The source-author tool is development-only and regenerates the authoritative raw `.bf` stages. Test evidence is in [`../evidence/iteration57_dynamic_callable_linear.json`](../evidence/iteration57_dynamic_callable_linear.json).

- Both BF native stages rebuilt **byte-identically** using the installed, verified Linux self-hosted BF compiler. A fresh native Linux compiler Stage 1→2 replay also produced byte-identical artifacts: [regression evidence](../evidence/iteration57_linux_s2_regression.json).
- **60** small linear-source cases, **240** simulated callable AArch64 runs, including byte input/output, tape underflow/overflow, modulo arithmetic and output limits.
- The emitted AArch64 bytes for `+`, `-`, `,`, and `.` paths match the existing independent callable backend oracle for eligible test programs.
- **5,000** increments, **5,000** outputs, **20,000** mixed commands, **100,010** bytes including a NUL, and **1,048,579** raw ignored/comment bytes plus source commands were compiled into ELFs accepted by `readelf`.
- **14** checked ELF-header length arithmetic tests, including 64-bit carry and rejection on overflow.
- Unsupported loop source and caller output-quota exhaustion leave the existing output file untouched.

The 240 AArch64 runs were performed in a constrained *instruction simulator*, not an Android device. These checks are neither formal memory-safety proofs nor evidence of a real JNI call.

## Remaining work before the user-requested compiler is complete

1. Add Brainfuck-owned, **file-backed dynamic IR and bracket pairing** that carries actual source/code offsets without the old 4,096-record or 255-depth tables. Indexing, pair output, and relocation computation belong to BF; host storage stays opaque.
2. Connect BF-owned signed-64-bit loop relocation to **callable** AArch64 emission, with entry/exit and budget/trap contracts preserved. Accept arbitrarily nested, valid source until real resource or representation exhaustion. Reject malformed brackets and failed partial emissions deterministically.
3. Use the original eleven pinned Gmail, Twitter and Threads policy sources as functional acceptance; compile each in the new lane and validate its real host framing, tape and persistence requirements. Do not conflate original BF source with Java or APK code.
4. Emit/load appropriate JNI-shared-library artifacts, run Android-device ABI and original application parity tests, then rerun Linux/Android self-hosting and safety/benchmark gates. Windows remains a separately verified future backend, not a substitute for Android callable completion.
5. **Only after** the dynamic lane passes its full source, ABI and regression gates, remove the fixed-array callable path and the former synthetic-capacity fallbacks. Until then, preserve archived reproducible compiler evidence and mark fallback paths as deprecated, not complete.

No fixed command-count target, including 100 million, is an active acceptance requirement. If platform file sizes, available storage, address representation or deadlines prevent a compilation, report the actual resource failure.
