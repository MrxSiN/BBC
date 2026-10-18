# BBC — Brainfuck Ballsdeep Compiler That Works With XAX

#### A Brainfuck compiler, written in Brainfuck, that compiles itself ☾

- 🧠 Eight commands, `><+-.,[]`. No ninth instruction, no hidden C or Python code generator doing the real work
- 🔁 Compiles its own source into a native Linux x86-64 ELF, then that ELF compiles the source again, byte for byte
- 🧾 Every claim has a test or an evidence file. If it says **unverified**, nobody ran it on the real thing

---

#### Status

| Target | What works | Limit |
|---|---|---|
| Linux x86-64 | **Self-hosted (S2)**. Source compiles itself through byte-identical stages 0–2 | 16,128 commands, 255 nesting levels |
| Android AArch64 programs | **Executed** on Pixel 8 Pro, Android 17/API 37 | 2,000 commands on device, 2,719 in simulation |
| Android callable `.so` | BF-generated DSOs with `bfc_call_v1`, Linux simulated and fail-closed validated | No Bionic, ART/JNI or APK run yet |
| Android native compiler | Bounded self-compile recorded on device | Dynamic native self-hosting still open |
| Windows x86-64 PE32+ | All eight commands, 192 commands, tested under Linux CPU shims | No Windows loader run, no Windows S2 |

The authoritative source is [`compiler/core.bf`](compiler/core.bf): **15,559 bytes**, 14,859 executable instructions. It emits a 475,703-byte Linux ELF, exactly `215 + 32 × commands`, with zero fixed trailing padding. Tape is 65,536 unsigned 8-bit wrapping cells, zero initialized, EOF reads zero, out-of-range pointer traps.

---

#### Try it

Linux, Python 3:

```sh
python3 bootstrap/run_compiler.py examples/hello.bf /tmp/hello.elf
chmod +x /tmp/hello.elf
/tmp/hello.elf
```

Full release check:

```sh
sh tools/verify_release.sh
python3 tools/check_docs.py
```

Python here only moves bytes around and checks results. It does not parse BF or write machine code. That part is Brainfuck's problem.

---

#### Where things are

| Path | What |
|---|---|
| [`compiler/`](compiler/) | The compiler. Brainfuck only |
| [`experiments/`](experiments/) | Android and Windows backend stages, also Brainfuck, each with a `.notes.md` |
| [`bootstrap/`](bootstrap/) | Transport adapters that chain BF stages together |
| [`tests/`](tests/), [`tools/`](tools/) | Verification and doc checks |
| [`evidence/`](evidence/), [`status/`](status/) | Raw test records and the conformance matrix |
| [`docs/`](docs/) | [State](docs/STATE.md), [targets](docs/TARGETS.md), [architecture](docs/ARCHITECTURE.md), [spec](docs/BRAINFUCK_SPEC.md), [open issues](docs/OPEN_ISSUES.md), [handoff](docs/HANDOFF.md) |

Every iteration, from wide bracket pairing to callable Android shared objects, is in the [changelog](CHANGELOG.md).

---

#### License

[MIT](LICENSE). Use it, fork it, explain it to your coworkers. Good luck with that last one.
