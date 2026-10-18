# BBC maintenance instructions

The current requirements are the user's BBC/XAX markdown prompt and their
explicit instruction that all retained bootstrap implementation be Brainfuck.

- Keep every implementation, bootstrap algorithm and executable test in
  standard `.bf` using only the original eight instructions. Do not add
  foreign-language harnesses, build scripts, CI scripts or disguised code in
  metadata. Markdown, licenses, binary fixtures and evidence JSON are allowed.
- The authoritative frontend is `compiler/compiler.bf`. Bootstrap framing is
  `bootstrap/frame_source.bf`. Read their contracts and tape notes before
  changing their instruction streams. Do not duplicate either algorithm.
- Keep annotations free of all eight instruction characters. Hash-prefixed
  lines are a visual convention, not a different lexer. Whitespace is free.
- Read `docs/BBX_CONTRACT.md`, `docs/BRAINFUCK_PROFILE.md`,
  `docs/BOOTSTRAP.md` and `docs/STATUS.md`. Preserve their semantics and
  framing unless a documented version change is intentional.
- Apply SRP and separation of concerns to framing, filtering, validation,
  emission and graph import within the existing small structure. Keep the
  BBX and decision interfaces narrow (ISP); depend on their contracts and
  verified XAX interfaces (DIP and least knowledge).
- Keep extensions explicitly versioned (OCP) and interchangeable execution
  backends faithful to identical semantics and failures (LSP). Use DRY,
  KISS and YAGNI; improve touched code without inventing classes, syntax,
  speculative frameworks or extra layers for these principles.
- Name the portable format BBX and save modules as `.bbx`. Keep the binary
  version in record metadata. The contract is its authoritative definition.
- XAX owns graph import, optimization, native code, ABIs, platform calls and
  packaging. Implement that work only in the separate XAX repository and
  follow its normative graph/workspace instructions. Do not recreate the
  retired BBC ELF, PE, JNI or APK backends.
- Keep independent seed interpreters and verification drivers outside this
  repository. They may execute BF, compare results and perform file/process
  I/O; they must not supply production frontend parsing or translation.
- Native execution is not cross-compilation. An interpreted compiler round
  trip is not native self-hosting. Never promote a target without execution.
- Verify source annotations, binary fixtures, size/error boundaries, bootstrap
  byte identity and independent interpreter agreement after relevant changes.
  Use EXECUTED, MEASURED, PROTOTYPE and UNIMPLEMENTED precisely; record source
  and external tool hashes. Do not claim timing superiority from one run.
- Android ARM64 comes first, Windows x86-64 second, Linux x86-64 third.
  The typed Android caller, app actions and native frontend self-hosting
  cycle have executed; preserve their evidence. Windows native decision and
  frontend component cycles also execute using XAX's shared backend. Linux
  x86-64 still needs an execution host; the user has confirmed none is available.
  Do not expose the internal borrowed-view core as an untrusted pointer ABI.
- Keep this repository small. Preserve recovery data outside the repository;
  do not restore obsolete files merely because they existed before.
