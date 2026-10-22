# 🤖 Maintaining BBC

> Rules for anyone (human or agent) changing this repository. Short, but every line matters.

Keep BBC's Brainfuck frontend and the BFX handoff to XAX correct. Attached documents
are reference material; the user's direct request wins. Document what exists now.
Leave unrelated working-tree edits alone.

---

## 🧱 What may live here

- **All executable BBC code is plain Brainfuck** (`><+-.,[]`): the compiler,
  bootstrap, examples and tests. No build scripts, harnesses or CI in other
  languages, and no code disguised as metadata. Markdown, licenses, exact binary
  fixtures and evidence JSON are fine.
- [`stream_chunks.bf`](compiler/stream_chunks.bf) owns public source filtering.
  [`compiler.bf`](compiler/compiler.bf) is the private bounded seed, and
  [`frame_source.bf`](bootstrap/frame_source.bf) its text framer. Read the
  contracts and [tape notes](compiler/compiler.bf.notes.md) before editing any of
  them, and don't duplicate their algorithms.
- Comments must not contain the eight instruction characters. `#` is only a
  visual habit; whitespace is ignored.
- **XAX owns** graph import, verification, native code, ABIs, platform glue and
  packaging. Do that work in the XAX repository, following its `AGENT.md`, as
  canonical semantic graphs changed through verified expected-root transactions.
- Use the existing generic Python bootstrap utilities unchanged, and say so. No
  Python BFX logic and no BBC ELF/PE/JNI/APK backends. If XAX lacks something,
  make a narrow canonical XAX change or record the blocker.
- Seed interpreters and test drivers live outside BBC. They may run programs and
  compare output, but never supply production parsing or translation.

---

## 📐 Contracts

- Read the [BFX spec](docs/02_BFX_CONTRACT.md), [profile](docs/01_BRAINFUCK_PROFILE.md),
  [bootstrap](docs/04_BOOTSTRAP.md) and [status](docs/05_STATUS.md) first.
  Keep semantics, framing, ownership and failures unless a tested change is intended.
- One format: magic `42 46 58 00`, id `01`, u32 count, `.bfx`. Exactly that id is
  emitted and accepted. No legacy decoder or fallback. All levels, sizes and
  targets share it.
- Keep interfaces narrow: the frontend knows nothing about XAX storage, native
  ABIs or OS APIs. Apply SRP, DRY, KISS and YAGNI. No speculative layers.
- Change formats only through an explicit, unambiguous migration. Every target must
  keep identical Brainfuck semantics and failures.
- BBC owns semantic optimization and its proofs. XAX owns graph and machine-code
  optimization.
- The borrowed-view decision core is private. Its typed caller proves initialization,
  lifetimes and non-aliasing; raw pointers prove nothing.
- Keep the repo small: generated files go in ignored `build/`, recovery data outside the repo.

---

## 🎯 Current scope

- **Required targets:** Android ARM64 and Windows x86-64. Linux is optional;
  cross-compiling alone is not target execution.
- **Limits:** the bounded seed takes 65,533 bytes, 3,840 instructions and depth 255.
  The public entry takes 1 MiB, 65,536 instructions before packing and depth 32,768.
  The program tape is 65,536 cells. These are fixed budgets, not growth.
- **Bounded passes** trust a complete validated success of up to 3,840 instructions
  plus `01`. They don't validate untrusted input. Validate their output, and
  discard failed prefixes.
- **Native compile.** `bbc.exe compile` is fully native and runs in one process: bind
  in-process, then the driver's edit, resolve and build. It commits its large
  views only when they're touched and checks each graph once per compile.
  [`bbc.exe`](docs/25_NATIVE_COMPILE.md) is bootstrapped once with the unchanged
  generic SDK. Runs under Wine or qemu are not device runs; new artifacts need real
  Pixel and Windows execution.
- **Biggest open costs:** generated-code speed on compute-heavy programs and build
  lowering ([benchmarks](docs/08_BENCHMARKS.md)).
- **Still open:** Android off-main-thread worker for unbounded programs, Windows DLL
  packaging, Android-hosted compiler, and affine/scan/offset optimizations. M8 is
  not achieved.
- **ARM64 note:** XAX OI-49 (large composite returns) is still open. The importer
  avoids it with scratch outputs and small results.
- **Preserve** full tape reset, rejected-length-before-reset, checked accesses and
  first-crossing movement failures.

---

## ✅ After changing code

- Check annotations, exact fixtures, size and depth limits, independent
  interpretation, bootstrap byte identity and execution on affected targets.
- For optimizations, add positive, negative, nested-loop, wrapping and bounds tests
  with complete buffers and guards.
- Use EXECUTED, MEASURED, PROTOTYPE, UNIMPLEMENTED and BLOCKED precisely. Record
  hashes, devices, tools and bootstrap dependencies.
- Follow the [measurement plan](docs/06_PERFORMANCE_PLAN.md) before claiming any
  win. Keep historical snapshots and pinned competitors as they are.

---

## 📝 Docs and evidence

- Keep README, docs, compiler notes and fixture READMEs consistent. Use relative
  links inside BBC and revision-pinned links into XAX.
- `docs/` files use a two-digit prefix (`01_…`). Keep the README index and links in
  sync with any rename.
- **Evidence JSON is immutable.** Add a new report for a new run; never relabel or
  rehash old ones. [Status](docs/05_STATUS.md) is the index.
- Retired-format reports were removed at the user's request and archived outside
  the repo ([cleanup record](evidence/format_cleanup.json)). Don't relabel old
  measurements as BFX results.
- When editing docs, check links, binary examples, limits, hashes and evidence counts.
  Doc-only work must not touch executable source, fixtures or evidence bytes.
