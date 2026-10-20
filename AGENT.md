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
- [compiler/compiler.bf](compiler/compiler.bf) is the authoritative frontend;
  [bootstrap/frame_source.bf](bootstrap/frame_source.bf) is the text framer.
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
- Version extensions explicitly. Every target must preserve identical
  Brainfuck semantics and failures. BBC owns semantic optimization and its
  equivalence proof; XAX owns general graph and machine-code optimization.
- Keep the internal borrowed-view decision core private. The typed caller
  establishes initialization, lifetimes and non-aliasing; raw native pointers
  alone do not establish those proofs.
- Keep the repository small. Store generated artifacts in ignored `build/`
  and recovery data outside the repository.

## Verification and current scope

- Android ARM64 comes first, Windows x86-64 second; Linux is optional and
  never gates required delivery or benchmarking.
  The decoder and importer execute natively on Android and Windows. Three
  current frontend generations pass on each platform, with twelve fixtures per
  Android generation and twelve current boundary checks. Eight fixed bounded Activity
  cases are separately verified. Use current evidence rather than earlier hashes.
- The recorded BBC cycles use Windows-hosted XAX bootstrap verification,
  lowering and packaging. A separate canonical Windows native driver prototype
  verifies tested stores and builds a PE fixture. Its diagnostic parity,
  corrected self-store, large-edit and DLL gates remain unmet; do not promote
  it to a complete native build path. Native component execution is not XAX compiler-host execution;
  cross-compilation is not target execution. Linux still needs an execution
  host; do not promote its support without one.
- The current frontend limits raw source to 65,533 bytes, keeping the complete
  request within the 65,536-byte native input view. Current Android and Windows
  native rebuild cycles have separate reports; do not promote earlier hashes
  to current evidence.
- Keep competitive completion separate from functional delivery. The
  [competitor pilot](docs/08_BENCHMARKS.md) measures Awib and brainfry process
  execution, test-pipeline compilation and size on both targets. It does not
  establish steady-state, RAM, application or best-mode victories. Preserve
  every pinned comparator and exclusion; follow
  [the measurement plan](docs/06_PERFORMANCE_PLAN.md) before claiming wins.
- The verification diagnosis separates cold helper setup from graph checks.
  Existing ProofCache reuse is a measured external warm-stage prototype;
  it must not skip the first verification or trust producer-supplied proofs.
  Windows native-helper loading still falls back to Python. Implement new
  host integration only as canonical XAX graphs, and rerun full pipeline
  timing before changing competitor scores.
- The standalone Android host and hello-binding transaction are canonical XAX
  sources. `evidence/standalone_android.json` records a process advantage over
  pinned Awib on twelve common-subset workloads; brainfry remains faster.
  `evidence/standalone_native_replay.json` records native authority. Do not
  generalize this to best modes, Windows, compiler latency, RAM, real apps or
  an unrestricted sweep. Older shared-library pilot measurements stay immutable.
- The standalone Windows PE host and hello binding are canonical XAX sources.
  `evidence/standalone_windows.json` records 23 native programs, 28 host checks,
  native binding replay and exact rebuilds. Its required generic bootstrap
  inlining view avoids a Win64 call-path decline; preserve canonical verification
  and disclose that build configuration. This does not complete the native
  compiler driver. Keep fresh build/resource results separate from older pilots.
  `evidence/build_runtime_resources.json` adds scoped fresh builds, compiler/runtime
  memory and Windows process comparisons on the twelve-source corpus. Compiler
  resident sums are sampled lower bounds; job peak commit is a distinct kernel
  counter. Preserve the excluded launcher calibration and raw counterbalanced
  trials. These measurements do not complete best-mode/app/coverage gates.
- The current XAX importer clears the full decision tape with checked eight-byte
  stores at alignment one. Its 393 record cases and 380 decision checks per
  arm/target, native authority and three twenty-check frontend generations
  are in `evidence/wide_tape_reset.json`. Preserve full-reset semantics and
  the rejected-length guard before reset. Native-call gains do not establish
  a compiler, process-startup, application or competitor victory.
- P0 grouped-byte bookkeeping and single-copy opcode decoding have exhaustive
  state checks and native
  frontend A/B measurements. The optional `compiler/optimize.bf` pass now folds
  exact unit-step clear loops and removes full 256-command arithmetic groups;
  see [v2](docs/10_BFX_V2_CLEAR.md) and [proofs](docs/07_OPTIMIZATION_PROOFS.md).
  Its precondition is a complete validated successful v1 record followed by
  byte one. It is not an untrusted-record validator. Keep BFX v1
  transparent and do not describe frontend work reductions as application wins.
- The capacity-flag frontend is 4,537 bytes / 2,192 instructions. It adds 82
  instructions and no cells, preserving exact BFX v1 output. Its separate
  `evidence/frontend_capacity_gate.json` covers 42 seed checks, 7,682 complete
  tape states, 785 Windows byte/property cases, 393 importer cases and three
  Windows generations. The later Android run passes 393 importer cases,
  three native generations, twelve fixtures each and twelve boundary checks;
  stores match Windows. Keep preceding Android hashes distinct. No device
  was connected initially; it became available during the follow-up.
- The user-local .NET SDK 10.0.402 resolves the Brainfly Windows build blocker.
  Twelve pinned corpus programs pass JIT and generated NativeAOT correctness
  checks in `evidence/brainfly_brainfry_followup.json`; no Brainfly timing
  score is established. Preserve the reproduced Brainfry even-step clear and
  intermediate-movement defects as negative rewrite cases. They do not
  invalidate separately checked pilot workloads or exclude the whole compiler.
- Preserve the importer's hash scratch/output and small-result contracts.
  The general ARM64 composite-return defect is tracked in XAX OI-49; the
  maintained importer avoids it. The pinned revision and ABI details belong
  in [XAX integration](docs/03_XAX_INTEGRATION.md).
- After executable changes, verify annotations, exact fixtures, size/nesting
  boundaries, bootstrap byte identity, independent-interpreter agreement and
  affected target execution. Optimization changes require positive, negative,
  nested-loop, wraparound and bounds-equivalence tests.
- Use EXECUTED, MEASURED, PROTOTYPE, UNIMPLEMENTED and BLOCKED precisely.
  Record source/artifact hashes, device/target, tool identities and unchanged
  bootstrap dependencies. Do not infer timing superiority from one run.

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
