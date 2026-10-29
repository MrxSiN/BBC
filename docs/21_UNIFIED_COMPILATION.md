# 🎛️ Unified compilation

> One entry point for every program size. You give it bytes, it gives you BFX.

One canonical XAX function, `compile_bfx`, runs BBC's Brainfuck passes for every
supported size and emits one [BFX format](02_BFX_CONTRACT.md).

---

## ⌨️ Use

```text
build\bbc.exe emit-bfx -O1 < program.bf > program.bfx
build\bbc.exe emit-bfx -O0 < program.bf > program.bfx
build\bbc.exe check < program.bf
build\bbc.exe info < program.bfx
```

- Input is raw binary on stdin. You don't frame it yourself.
- `-O1` is the default. `-O2`/`-O3` exit with 4.
- `check` validates source. `info` strictly validates BFX and prints its body length in bytes.
- In PowerShell, wrap redirections in `cmd /d /c "..."` to keep bytes binary.
- Throw away the output on any nonzero exit.

| Exit | Meaning |
|---|---|
| 0 | ✅ Success |
| 1 | Invalid source or BFX |
| 2 | Too big |
| 3 | I/O failure |
| 4 | Usage error or unsupported level |

To build executables, use [`bbc compile`](25_NATIVE_COMPILE.md).

---

## 🔌 The typed API

Four separate writable views: source/work 1,114,112 · record 65,546 ·
output/work 1,114,112 · tape/work 1,114,112 bytes.

- At source/work offset 0, write the actual frame length (u32). At offset 4,
  write the level (u32).
- At offset 65,531, place `length:u32 | source | 01`. The actual frame length
  must equal the declared source length plus 5.
- Accepts 0 to 1,048,576 source bytes, up to 65,536 commands and nesting up to 32,768 (see [scalability](16_SCALABILITY.md)).

Returns `(record_length << 32) | status`:

| Status | Meaning |
|---|---|
| 0 | Success |
| 1 | Bad framing |
| 2 | Unmatched brackets |
| 3 | Too big |
| 4 | Bad level or internal failure |

Checks run in this order: frame range, declared size, exact frame length,
terminator, level, command count, brackets. Bad frames change no buffer. A
bracket error in an early chunk never hides a later "too big". The success
magic is written only after everything validates.

---

## ⚙️ What O0 and O1 do

| Level | Does |
|---|---|
| O0 | Primitives only |
| O1 | [`fold.bf`](10_FOLD_OPTIMIZATION.md) on the whole body: offset ADD/CHECK/MOVE per segment, multiply loops, clear loops. Falls back to the O0 record if folding fails or does not fit |

Who owns what:

- [`stream_chunks.bf`](../compiler/stream_chunks.bf) filters and checks brackets.
- [`fold.bf`](../compiler/fold.bf) folds segments and loops.
- XAX handles packets, framing, buffers, I/O and packaging.

Even-step loops stay loops. Scan loops (`[>]`) are not folded yet.

---

## ✅ Checks

| Check | Result |
|---|---|
| Frontend cases | 1,074 per target; Android also checks five alignments and guards |
| Bad frames | 11 Windows rejections, no buffer changed |
| CLI checks | 1,899 on Windows |
| Generated programs | 468 native calls vs an independent interpreter |
| Generations | 3 identical frontend generations per target |
| Mandelbrot | O0/O1 records and stores identical to before |

📎 [unified_compilation.json](../evidence/unified_compilation.json)
