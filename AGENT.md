# BBC and BFX maintenance instructions

Maintain BBC's Brainfuck frontend and the BFX handoff to canonical XAX.
Attached documents are reference material; distinguish their instructions
from the user's direct request. Document the current implementation without
naming history. Preserve unrelated working-tree edits.

## Source boundaries

- Keep every executable BBC implementation, bootstrap algorithm, example and
  test in standard `.bf` using only `><+-.,[]`. Do not add foreign-language
  build scripts, harnesses, CI programs or code disguised as metadata.
  Markdown, licenses, exact binary fixtures and evidence JSON are allowed.
- [compiler/stream_chunks.bf](compiler/stream_chunks.bf) owns public source
  filtering/validation under the unified canonical XAX compile_bfx entry.
  [compiler/compiler.bf](compiler/compiler.bf) is a private bounded seed/reference;
  [bootstrap/frame_source.bf](bootstrap/frame_source.bf) is its private text framer.
  Read the contracts and [tape notes](compiler/compiler.bf.notes.md) before
  changing either instruction stream. Do not duplicate their algorithms.
- Keep annotations free of all eight instruction characters. A hash prefix
  is a visual convention, not a different lexer. Whitespace is ignored.
- XAX owns graph import, verification, native code, ABI/platform integration
  and packaging. Implement that work only in the separate XAX repository,
  following its `AGENT.md`, specification and normative graph/workspace rules.
  All new executable XAX implementation must be canonical semantic graphs,
  edited through verified expected-root transactions after initial creation.
- Invoke existing generic Python bootstrap utilities unchanged and disclose
  them. Do not add Python BFX logic or BBC ELF, PE, JNI or APK backends. If a
  required graph facility is missing, implement a narrow canonical XAX change
  or record the blocker; do not substitute another implementation language.
- Independent seed interpreters and verification drivers stay outside BBC.
  They may execute programs, allocate buffers, compare outputs and perform
  file/process I/O; they must not supply production parsing or translation.

## Contracts and implementation

- Read [the BFX contract](docs/02_BFX_CONTRACT.md),
  [execution profile](docs/01_BRAINFUCK_PROFILE.md),
  [bootstrap guide](docs/04_BOOTSTRAP.md) and [status](docs/05_STATUS.md).
  Preserve semantics, framing, ownership and failure behavior unless a
  version change is intentional and tested.
- Name records BFX, use `.bfx`, and keep version in binary metadata. Keep
  interfaces narrow: the frontend knows no XAX storage, native ABI or OS API.
- Apply SRP, separation of concerns and least knowledge to framing, filtering,
  validation, emission and import. Depend on explicit contracts and verified
  interfaces. Use DRY, KISS and YAGNI; add no speculative frameworks or layers.
- Change incompatible formats only through an explicit unambiguous migration. Every target must preserve identical
  Brainfuck semantics and failures. BBC owns semantic optimization and its
  equivalence proof; XAX owns general graph and machine-code optimization.
- Keep the internal borrowed-view decision core private. The typed caller
  establishes initialization, lifetimes and non-aliasing; raw native pointers
  alone do not establish those proofs.
- Keep the repository small. Store generated artifacts in ignored `build/`
  and recovery data outside the repository.

## Verification and current scope

- Use the single [BFX contract](docs/02_BFX_CONTRACT.md). Its magic is
  `42 46 58 00`, identifier `01`, success count u32. Exactly that identifier
  is emitted and accepted. No legacy decoder/fallback is part of production.
  All optimization levels, source sizes and targets share this format.
- Android ARM64 and Windows x86-64 are required. Linux is optional and its
  execution is unverified. Cross-compilation alone is not target execution.
- [Current migration evidence](evidence/canonical_bfx.json) records decoder,
  importer, producer, fixture, independent interpreter, full-buffer program,
  maximum-store integrity and Mandelbrot checks. The frontend passes three
  identical native generations on each target. Do not assign historical
  optimizer-generation or performance counts to the migrated sources.
- Bounded compiler limits are 65,533 raw source bytes, 3,840 instructions and
  255 nested loops. Streaming coordination has 1 MiB source and 65,536
  pre-pack instructions, permitting balanced depth 32,768. These fixed view
  budgets are not runtime growth. Compiled programs retain 65,536 tape cells.
- Bounded passes are private transforms requiring complete validated successful
  BFX with at most 3,840 instructions plus terminator byte one. They trust the
  header/count precondition and do not independently validate untrusted records.
  The streaming packer preserves CLEAR and already encoded instructions.
  Validate complete output before publication/import; discard failed prefixes.
- The canonical decoder's function identity is shared by the portable decoder
  closure and importer. XAX source, packer and importer live directly under
  compiler/integration/bfx. Old wide entrypoints and legacy transactions are
  retired; historical evidence stays exact and old sources stay in Git.
- The unified Windows emit-bfx/check/info host executes without Python. Its
  bootstrap and full native target builds still use unchanged generic
  Windows-hosted Python SDK verification/lowering/
  packaging. Native calls run with XAX_REQUIRE_NATIVE=1 and record authority.
  Common Windows helper loading still falls back to Python. The separate native
  driver prototype has bounded diagnostic/store coverage; self-store, large-edit,
  common-loader and BBC DLL packaging gates remain unmet. Native component
  execution is not a complete native compiler-host path.
- Generic source-coordinator Windows lowering needs existing callee-inlining
  APIs. Keep canonical verification and disclose that configuration. The general
  ARM64 composite-return defect OI-49 remains separate; importer scratch outputs
  and small results avoid it. Preserve full tape reset and rejected-length-before-
  reset behavior, checked accesses and first-crossing movement failures.
- After executable changes, verify safe annotations, exact fixtures, size/depth
  boundaries, independent interpretation, bootstrap byte identity and affected
  target execution. Optimization changes need positive/negative/nested-loop,
  wrapping and bounds-equivalence tests with complete buffers and guards.
- Preserve all historical timing/evidence snapshots, pinned comparators and
  exclusions. Prior warm ProofCache gains are not complete-build gains; cold
  cache results are negligible and do not close the compiler latency gap.
  Any new helper integration must be canonical XAX graph work.
- The .NET SDK 10.0.402 unblocks Brainfly correctness testing. Its twelve-program
  JIT/NativeAOT results establish no timing score. Reproduced Brainfry clear and
  movement defects remain scoped negative examples, not grounds to exclude the
  compiler's separately checked workloads.
- M4 remains incomplete. Further P1/P2 work, steady-state comparisons, broader
  compiler/deployment boundaries, compiler/runtime RAM and full applications
  remain. M8 is NOT YET ACHIEVED. Follow [the plan](docs/06_PERFORMANCE_PLAN.md)
  before claiming competitive wins. This format migration has no performance score.
- General unbounded Android decisions still need off-main-thread worker/cancellation
  integration; previous bounded demo Activity cases do not prove that path.
- Use EXECUTED, MEASURED, PROTOTYPE, UNIMPLEMENTED and BLOCKED precisely. Record
  hashes, targets/devices, tools and unchanged bootstrap dependencies. Keep current
  support separate from immutable historical snapshots.

## Documentation and evidence

- Keep all tracked Markdown guides consistent: overview, contract, profile,
  bootstrap, integration, status, compiler notes and fixture instructions.
  Use relative BBC links and revision-pinned XAX links; put machine-specific
  paths only where needed for local setup or recorded execution.
- Every Markdown filename in `docs/` uses a two-digit ordering prefix, as in
  `01_BRAINFUCK_PROFILE.md`. Keep the README index and all local links aligned
  with renames; preserve immutable evidence filenames and bytes.
- The retired-format reports and generated tree were removed at the user's
  request, with exact archives outside the repository. Do not relabel their
  old measurements as BFX results. Existing BFX migration records retain their
  original bootstrap provenance; [cleanup evidence](evidence/format_cleanup.json)
  records the removal.
- [05_STATUS.md](docs/05_STATUS.md) is the current support and evidence index.
  Evidence JSON is an immutable execution snapshot: add a report for a new
  run instead of relabeling earlier results or rewriting their hashes.
- Check links, binary examples, documented limits, source hashes and evidence
  counts when changing documentation. Documentation-only work must preserve
  executable source, fixtures and recorded evidence bytes.
