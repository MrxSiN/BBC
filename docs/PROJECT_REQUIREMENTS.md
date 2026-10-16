# Mission: Build a Fully Self-Hosted, Native, Memory-Safe Brainfuck Compiler

## 1. Role and mission

You are the principal architect, compiler engineer, optimizer engineer, systems programmer, security engineer, test engineer, and technical maintainer of this project.

Your mission is to build a serious, production-oriented Brainfuck compiler that is:

- Written entirely in standard Brainfuck.
- Self-hosted from its first accepted working milestone.
- Capable of producing native machine code.
- Designed for C-like and assembly-like performance.
- Memory-safe within its explicitly defined execution model.
- Capable of running natively on Linux, Windows, and Android, with bare-metal support as a separate goal.
- Aggressively optimized without changing program meaning.
- Capable of building, testing, and maintaining itself.
- Fully inspectable by humans despite being written in Brainfuck.
- Maintained autonomously by AI without requiring human-written implementation code.

The project must use the original eight Brainfuck instructions and nothing else.

The central principle is:

**Keep Brainfuck unchanged. Make the compiler powerful.**

Do not invent a replacement language.

Do not introduce a second programming language.

Do not make Brainfuck look like C or Rust.

Do not solve difficult compiler problems by quietly moving the implementation into another language.

The compiler itself must be a real Brainfuck program.

The ultimate objective is to make Brainfuck a practical systems-programming language wherever its existing semantics can genuinely support the required work.

This objective must be pursued through compiler engineering, optimization, target-specific code generation, reproducible builds, and verified evidence.

Do not confuse an architectural ambition with an implemented capability.

---

## 2. Read the repository before changing anything

You have access to the complete project repository.

Before writing or modifying code:

1. Inspect the repository structure.
2. Read every existing architectural and normative document.
3. Find the current authoritative compiler source.
4. Identify the current bootstrap procedure.
5. Identify all external tools and dependencies.
6. Examine existing native-code generation.
7. Run existing correctness and conformance tests.
8. Run existing benchmarks where practical.
9. Identify the last proven self-hosting cycle.
10. Determine which features actually work.

Do not assume a README describes the current implementation accurately.

Do not assume generated artifacts are correct merely because they exist.

If the repository is empty, create the project from these requirements.

If a previous prototype uses Python, C, Rust, LLVM, or another implementation language, treat it as reference material only. It must not become the authoritative compiler.

Preserve any useful verified behavior, but do not preserve an architectural dependency that violates the Brainfuck-only implementation requirement.

Do not rewrite functioning components without a clear technical reason.

Record the repository's actual starting state before upgrading it.

---

## 3. Absolute language rule: exactly eight instructions

The Brainfuck instruction set is fixed permanently.

| Instruction | Meaning |
|---|---|
| `>` | Move the data pointer one cell right |
| `<` | Move the data pointer one cell left |
| `+` | Increment the current cell |
| `-` | Decrement the current cell |
| `.` | Output the current cell as a byte |
| `,` | Read one input byte into the current cell |
| `[` | Begin a loop conditional on the current cell |
| `]` | Return to the matching loop test when the current cell is nonzero |

These are the only executable language instructions.

Never introduce:

- New operators.
- Additional keywords.
- Functions as new syntax.
- Variables as new syntax.
- Types as new syntax.
- Classes, structures, or traits as new syntax.
- Inline assembly syntax.
- Preprocessor directives.
- Macros that become an authoritative source language.
- Special compiler-recognized comment commands.
- Built-in system-call instructions.
- Hidden library-call instructions.
- Additional control-flow instructions.
- Custom Brainfuck dialects.
- Special instruction sequences with privileged semantics.

The compiler may recognize patterns of existing Brainfuck instructions and replace them with more efficient equivalent machine code.

However, the replacement must preserve the exact observable behavior of the original instruction sequence.

For example:

```brainfuck
[-]
```

may compile into a direct cell-clear operation when valid under the chosen cell semantics.

Similarly:

```brainfuck
[->+<]
```

may compile into a cell-transfer operation when all necessary safety and semantic conditions hold.

These are compiler optimizations, not language extensions.

No optimization pattern may act as a hidden new instruction with behavior unavailable to ordinary Brainfuck execution.

**Eight instructions enter the compiler. Optimized machine instructions leave it. The language never changes.**

---

## 4. Raw Brainfuck source, inline comments, and documentation

All authoritative compiler implementation files must use `.bf`.

Keep the actual code as raw, standard Brainfuck. Only `><+-.,[]` execute. Whitespace and other characters are ignored by the Brainfuck execution model; do not add comment parsing, directives, or new source-language syntax.

### Comments inside `.bf` files

**Human-readable comments must live alongside the real Brainfuck instructions in `.bf` files.** Do not make separate notes the only way to understand the code.

Use a simple repository convention: a line starting with `#` contains an explanation, not executable Brainfuck. An inline `#` after instructions is also allowed. The `#` is just an ordinary ignored character, **not** a Brainfuck comment operator. Standard interpreters still scan every byte.

Therefore, **the comment text must contain none of the eight instruction characters** (`><+-.,[]`). In particular, punctuation such as a period, comma, hyphen, or angle bracket is unsafe inside a `.bf` comment. A mandatory source linter must check comment regions and reject violations. Do not rely on `#` to hide executable Brainfuck.

Example of valid raw `.bf` source:

```brainfuck
# Clear the current cell
[-]
# The cell now holds zero
```

The executable instruction stream from this file is exactly `[-]`. All comments are ignored by any conforming interpreter that ignores non-instruction characters. A generated, instruction-only `.bf` file may be useful for verification or distribution, but it is derived output, never the authoritative source.

Keep comments close to non-obvious blocks. Explain the purpose, pointer position, cell ownership, required initial state, and safety assumptions only where they matter. Do not narrate each `+` or `>`.

For explanations that need command characters, diagrams, long proofs, or complex memory maps, use an optional companion file such as `compiler/core.bf.notes.md`. Link notes to stable offsets in the **filtered instruction stream** and the corresponding source revision. Generate an annotated view only when useful; it must not replace the `.bf` source.

Mandatory checks:

1. Extract the executable stream by retaining only the eight instruction bytes.
2. Reject any Brainfuck instruction byte inside a declared comment region.
3. Verify balanced brackets and the expected filtered-source hash.
4. Verify optional note offsets against that filtered stream and source revision.
5. Verify that changing or removing comments without changing instruction bytes produces the same generated artifact.
6. Verify that the commented source and its stripped instruction stream behave identically under independent, compatible Brainfuck interpreters.

The compiler must accept ordinary Brainfuck source containing ignored non-instruction characters. Comments are never recognized as directives and must not affect compilation, optimization, or execution.

### Comment and documentation writing style

Use the actual tone of this profile README as the reference:

https://github.com/MrxSiN/MrxSiN

Apply it to **everything**: `.bf` comments, README, architecture documents, target guides, tests, changelogs, agent instructions, troubleshooting, and release notes. Not just annotations.

Write like a technically competent developer explaining what they built to another developer. Direct, conversational, concise, accurate, and occasionally dry or sarcastic. The reference uses Brainfuck-specific humor and admits how awkward the language is; keep that character without copying its prose or forcing jokes into every paragraph.

- Explain what works, how it works, why a choice matters, and what is still broken.
- Use small headings, short useful examples, exact commands, clear limitations, and measured results.
- Document assumptions, ABI contracts, pointer positions, tape layouts, bootstrap steps, and reproducible verification where necessary.
- Avoid corporate marketing, fake certainty, ceremonial language, overlong boilerplate, and comments that restate instructions.
- Keep README short and practical; put real detail where readers need it.
- For `.bf` comments, obey the safe-character rule above. Use normal punctuation freely in Markdown documents.

Good Markdown note:

> This block copies the value into the next cell. The original cell ends at zero.

Good Markdown warning:

> Keep this bounds check. The pointer can reach the end of the tape here.

Bad documentation:

> This revolutionary highly optimized computational construct leverages advanced techniques to ensure exceptional performance.

Accuracy wins over humor. Do not make debugging harder to make the README funnier.

---

## 5. Self-hosting is mandatory from the beginning

This is the highest architectural requirement after semantic correctness.

**The first accepted compiler must already be implemented in Brainfuck and capable of compiling its own Brainfuck source.**

A compiler written in Python, C, C++, Rust, JavaScript, or another language with a future promise to rewrite it in Brainfuck does not meet the requirement.

Do not begin with a non-Brainfuck compiler as the main implementation.

Do not implement the optimizer in Rust and call a Brainfuck wrapper self-hosted.

Do not hide code-generation logic inside the bootstrap tool.

### Definition of genuine self-hosting

A compiler is self-hosted when:

1. Its authoritative compiler logic is written in Brainfuck.
2. It accepts ordinary Brainfuck source.
3. It generates an executable or supported target artifact.
4. It can compile its own complete authoritative Brainfuck implementation.
5. The resulting compiler performs equivalent compilation independently.
6. Repeated self-compilation produces semantically equivalent compilers.
7. No external compiler contains hidden Brainfuck-specific compilation logic.

Self-hosting must be demonstrated through executable evidence.

A README statement is not sufficient.

### Permitted bootstrap mechanism

A temporary, independent, standard Brainfuck interpreter is permitted solely to execute the Brainfuck compiler source during the initial bootstrap.

The bootstrap interpreter may implement Brainfuck execution semantics.

It may not implement the project's parser, optimization passes, machine-code generator, binary linker, or other compilation logic.

The initial process is:

```text
Authoritative compiler source in Brainfuck
                  |
                  v
       Independent BF interpreter
                  |
                  v
       First native compiler binary
                  |
                  v
      Compile the same BF source
                  |
                  v
      Second native compiler binary
                  |
                  v
         Repeat self-compilation
                  |
                  v
       Verify stable equivalence
```

The interpreter is the seed execution environment.

It is not the compiler.

### Required bootstrap stages

**Stage 0 — Interpreted compiler**

Execute the compiler's Brainfuck source with an independent, standard-conforming interpreter.

Use the compiler's own Brainfuck logic to generate the initial native compiler executable.

**Stage 1 — Native compiler**

Execute the native compiler generated by Stage 0.

Use it to compile the same authoritative Brainfuck compiler source.

**Stage 2 — Self-compiled compiler**

Execute the compiler generated by Stage 1.

Use it to compile the authoritative source again.

**Stage 3 — Reproducibility verification**

Compare the results of the successive self-compilation stages.

Prefer byte-identical artifacts.

If a documented target introduces unavoidable artifact differences, normalize only explicitly justified nonsemantic fields and separately prove functional equivalence.

Do not excuse unexplained binary differences as normal.

Also compare compilation behavior across a meaningful independent program corpus.

### Bootstrap acceptance criteria

The bootstrap is accepted only when:

- All required native compiler binaries execute.
- The compiler successfully compiles itself.
- Independently obtained executables agree on tested compilation results.
- Generated programs preserve Brainfuck semantics.
- No foreign compiler participates in the self-compilation cycle.
- All bootstrap inputs and outputs have recorded hashes.
- The bootstrap procedure can be repeated from a clean checkout.
- Every external bootstrap dependency is disclosed.
- The source of the bootstrap interpreter is inspectable or independently obtainable.
- The release contains instructions for independently verifying the bootstrap.

Record the distinction between reproducible compilation and proof that a bootstrap seed is trustworthy.

Where practical, use multiple independently implemented Brainfuck interpreters to bootstrap the same source and compare results.

Do not claim that reproducible builds alone eliminate compiler-trusting-trust attacks.

### Non-negotiable delivery rule

Do not declare the project's first milestone successful until this self-hosting cycle works.

If self-hosting is not achieved, report the project as incomplete.

Do not relabel an interpreter, BF-to-C translator, or external compiler wrapper as a self-hosted native compiler.

---

## 6. Fix the Brainfuck execution semantics

Brainfuck does not have one universally agreed formal specification for tape size, cell size, overflow, EOF, and pointer boundaries.

Do not pretend these differences do not exist.

Create an explicit normative execution profile before implementing optimizations.

For the initial implementation, use:

| Property | Initial semantic policy |
|---|---|
| Cell width | Unsigned 8-bit |
| Arithmetic | Modulo 256 |
| Initial cell values | Zero |
| Initial pointer | Cell zero |
| Tape | Fixed-size, explicitly configured |
| Default tape size | 65,536 cells |
| Pointer outside tape | Deterministic trap |
| Input | Raw bytes |
| Output | Raw bytes |
| EOF | Store zero |
| Loops | Test current cell for zero |
| Unmatched brackets | Compile-time error |
| Cell address arithmetic | Never permits host-memory escape |

Document this as the project's initial Brainfuck profile.

Tape size and target memory layout are build parameters, not new source-language instructions.

Every change to an execution profile must be explicit and versioned.

Never silently switch from wrapping bytes to unbounded integers.

Never treat undefined host memory access as legal Brainfuck behavior.

Never exploit accidental behavior of a particular interpreter.

### Semantic invariants

All optimizers and backends must agree on:

- Cell wrapping.
- Pointer positioning.
- Loop entry and exit conditions.
- Input consumption order.
- Output byte order.
- EOF behavior.
- Tape initialization.
- Tape boundaries.
- Trap conditions.
- Termination behavior.

Optimization may reduce execution time.

It must not change program meaning.

This includes programs that run very slowly, never terminate, reach tape boundaries, or depend on wrapping arithmetic.

---

## 7. Absolute engineering priorities

Use this priority order:

1. Exact Brainfuck semantic correctness.
2. Genuine Brainfuck self-hosting.
3. Memory safety and optimizer correctness.
4. Runtime performance.
5. Required Linux, Windows, and Android portability.
6. AI generation and maintenance reliability.
7. Memory footprint.
8. Executable size.
9. Compilation speed.
10. Reproducible builds.
11. Dependency elimination.
12. Human inspectability.
13. Convenience features.

Self-hosting must never be postponed to gain development speed.

Correctness and memory safety must never be sacrificed for benchmark results.

Human readability should be available without adding new instructions or mandatory runtime overhead.

Do not add abstraction layers unless they solve a demonstrated problem.

### Engineering principles: apply SOLID without inventing object-oriented Brainfuck

SOLID applies to **responsibilities, contracts, compiler passes, tape regions, and target backends**. It does not require classes, interfaces, dynamic dispatch, or new Brainfuck instructions. A useful convention on an ordinary tape is enough.

- **SRP — Single Responsibility:** Give each logical pass or tape region one clear job and one reason to change. Parsing must not quietly become ELF encoding; target-specific I/O must not live in the optimizer.
- **OCP — Open/Closed:** Keep proven parsing and semantic rules stable when adding a target or optimization. Extend through small, documented pass/backend contracts; change shared code only when those contracts actually need to evolve.
- **LSP — Liskov Substitution:** Every backend conforming to the same contract must preserve observable Brainfuck semantics, diagnostics, and safety. Swapping targets cannot silently change wrapping, EOF, or tape boundaries. Platform-dependent I/O and executable formats must be specified separately.
- **ISP — Interface Segregation:** Use minimal contracts. A parser should not need relocation fields; a byte emitter should not need optimization internals. Do not add universal interfaces merely to satisfy this principle.
- **DIP — Dependency Inversion:** Keep shared compiler logic dependent on documented input, IR, emission, and error contracts rather than a particular operating system's binary format. Express these contracts through simple tape conventions and byte protocols where needed.

Apply these general rules as well:

- **DRY:** One normative definition for execution semantics, one source of truth for target capabilities, and no needless duplicated target-independent logic. Reuse verified Brainfuck routines or derived data where reuse actually reduces complexity.
- **KISS:** Prefer direct lowering, fixed layouts, explicit offsets, and a few understandable passes. Fewer moving parts beat a clever framework unless measurements prove otherwise.
- **YAGNI:** Build only what is needed for the next verified milestone. No speculative plugin system, universal IR, generic linker, dynamic library framework, or target matrix full of empty promises.
- **Law of Demeter:** Each pass should touch its own tape region and the defined contracts of its immediate neighbors. Avoid reaching into another pass's undocumented scratch cells.
- **Boy Scout Rule:** Leave each touched region slightly clearer, safer, or easier to test without unrelated rewrites. Keep code changes local and preserve self-hosting.
- **Separation of Concerns:** Keep source filtering, bracket matching, optimization, machine encoding, executable format, platform I/O, and validation conceptually separate; combine only where a simpler proven implementation benefits.

For every proposed abstraction, ask: **What real duplication, bug, or target requirement does this eliminate?** If there is no concrete answer, leave it out. Never trade correctness or measured runtime for cosmetic adherence to a principle.

---

## 8. Compiler architecture

The compiler must be implemented entirely through standard Brainfuck operations.

Its conceptual architecture should be:

```text
Brainfuck source bytes
          |
          v
Input validation and filtering
          |
          v
Bracket matching and parsing
          |
          v
Compact internal representation
          |
          v
Brainfuck-specific optimization
          |
          v
Target instruction selection
          |
          v
Machine-code generation
          |
          v
Relocation and binary construction
          |
          v
Native executable artifact
```

Every compilation stage containing actual compiler logic must be implemented in Brainfuck.

Share the source parser and semantic optimizer across targets. Isolate machine instruction encoding, executable layout, startup, traps, and byte I/O behind the smallest useful target contracts. A simple target selector and a few per-target paths are enough; do not construct a general-purpose backend framework. Any necessary target selection belongs to the documented compiler input protocol, not to Brainfuck source syntax.

The intermediate representation exists as data stored in Brainfuck's tape.

It is not a new source language.

Do not make users author an IR.

Do not add an external optimizer written in another language.

Do not delegate normal native code generation to GCC, Clang, rustc, or LLVM.

Those tools may be used as comparison baselines, validation tools, disassemblers, or isolated development aids.

They must not be required to produce the final native executable in the verified self-hosting path.

### Internal compiler memory layout

Design a documented tape layout for the compiler itself.

Possible regions include:

- Input buffering.
- Source instruction storage.
- Bracket stack.
- Loop metadata.
- Intermediate representation.
- Optimization workspaces.
- Generated machine-code bytes.
- Relocation records.
- Target configuration.
- Output state.
- Error state.

These are implementation conventions, not Brainfuck language features.

Every region must have a defined ownership and lifetime convention.

Verify that compiler-internal memory regions cannot accidentally overlap.

If a compilation exceeds the compiler's memory capacity, fail deterministically rather than corrupting memory.

### Bounded initial scope

The initial compiler may impose explicit source-size, code-size, and nesting-depth limits.

Limits must be documented and tested.

Self-hosting must work within those limits.

Do not silently truncate programs.

Do not claim support for arbitrary source sizes when the implementation is bounded.

---

## 9. Native code generation without another compiler

Native code generation is a core requirement.

The first required target is:

**Linux x86-64, static ELF executable, System V-compatible environment, without a mandatory libc dependency.**

This is the **bootstrap target**, not the only required platform. Windows x86-64 and Android AArch64 are mandatory subsequent native targets, as defined in Section 14. Keep the first bootstrap small and working before adding their backends.

Implement the relevant output generation in Brainfuck.

The compiler must construct executable bytes rather than emit C source for GCC to finish.

### Initial native backend

Implement:

- ELF header generation.
- Program header generation.
- Executable code sections or segments.
- Tape storage.
- Entry-point setup.
- Machine instruction encoding.
- Branch displacement calculation.
- Loop target resolution.
- Address patching.
- Input/output operations.
- Program termination.
- Tape-boundary traps.

Use a minimal, well-defined ABI and startup sequence.

Do not require dynamic linking.

Do not require an external assembler.

Do not require a JIT.

Do not require LLVM.

Do not require a garbage collector.

Do not require a managed runtime.

### Code-generation strategy

Begin with a correctness-first machine-code backend.

Implement direct lowering of all eight Brainfuck instructions.

Then introduce a compact internal representation and optimizations while preserving the original implementation as a reference.

Machine-code generation should eventually support:

- Register allocation or effective fixed-register conventions.
- Pointer movement folding.
- Immediate arithmetic.
- Relative and indirect addressing where needed.
- Direct branches.
- Branch displacement patching.
- Instruction selection.
- Peephole optimization.
- Code layout.
- SIMD instructions when useful.
- CPU-feature-specific code generation.

Do not overengineer a universal backend before the first self-hosting cycle succeeds.

Build a working native compiler first.

Improve it incrementally.

### Compiler I/O contract

The self-hosted compiler must receive its Brainfuck source through a documented input protocol and emit its compilation result through a documented output protocol.

A stdin/stdout-based interface is acceptable.

Because ordinary Brainfuck exposes only byte input and output, a diagnostic or artifact protocol may use framed byte records.

Any minimal host adapter may handle transport, file placement, or process exit-status mapping, but it must not parse Brainfuck, optimize instructions, or generate machine code.

Compiler semantics must remain entirely inside the Brainfuck program.

Document exactly which functionality is compiler logic and which is transport.

The native compiler must operate without a Python, C, or Rust compilation engine behind it.

---

## 10. Optimization engine

Runtime performance is the primary ongoing engineering focus once correctness and self-hosting are proven.

Develop an aggressive Brainfuck-specific optimizer.

The objective is:

**Generate the lowest practical execution cost for exact Brainfuck semantics on the selected target.**

Implement optimizations incrementally.

Every transformation requires an explicit correctness argument and tests.

### Level 1 — Basic instruction optimization

Implement:

- Consecutive increment merging.
- Consecutive decrement merging.
- Arithmetic normalization modulo 256.
- Consecutive pointer movement analysis.
- Constant folding.
- Dead instruction elimination where proven safe.
- Redundant operation elimination.
- Basic control-flow cleanup.

Examples:

```brainfuck
+++++
```

can lower to one addition of five.

```brainfuck
-----
```

can lower to one subtraction of five.

Do not erase pointer movement that would cause a boundary trap.

For example, opposite movements are not always removable if the first movement crosses a prohibited boundary.

### Level 2 — Loop recognition

Recognize and optimize common Brainfuck loop patterns.

Examples include:

```brainfuck
[-]
```

```brainfuck
[+]
```

```brainfuck
[->+<]
```

```brainfuck
[->+++<]
```

```brainfuck
[>]
```

Potential transformations:

- Clear-cell operations.
- Cell transfers.
- Multiplication and addition.
- Affine cell updates.
- Pointer scanning.
- Constant-value loop elimination.

Do not assume every loop is a transfer loop.

Do not assume every loop terminates.

Analyze the induction cell, loop displacement, cell arithmetic, intermediate pointer accesses, and any I/O operations.

### Level 3 — Affine loop analysis

Represent eligible loops as mathematical transformations over the 8-bit cell domain.

Use modulo-256 arithmetic correctly.

Support:

- Multiple destination cells.
- Constant coefficients.
- Source-cell elimination.
- Static loop-trip reasoning when valid.
- Composition of compatible transformations.
- Detection of nonterminating arithmetic cycles.

For loops whose induction step is not invertible modulo 256, do not apply transformations that assume a unique iteration count.

Preserve intermediate bounds-trap behavior.

### Level 4 — Whole-program analysis

Implement where useful:

- Constant propagation.
- Known-zero propagation.
- Value-range analysis.
- Symbolic pointer tracking.
- Memory-state analysis.
- Dead-store elimination.
- Loop-invariant reasoning.
- Partial evaluation.
- Equivalent instruction-sequence elimination.
- Whole-program simplification.
- Elimination of unnecessary tape initialization work.

All analyses must use Brainfuck semantics.

Do not introduce C-style undefined behavior assumptions.

### Level 5 — Machine-code optimization

Improve generated native instructions through:

- Instruction combining.
- Register reuse.
- Load/store forwarding.
- Efficient addressing modes.
- Branch optimization.
- Code layout.
- Strength reduction.
- Loop unrolling.
- Reduced memory traffic.
- Instruction scheduling where justified.
- Target-specific instruction selection.

Do not insert an optimization that makes typical workloads slower merely because it improves one benchmark.

Maintain a representative workload corpus.

### Level 6 — SIMD optimization

Investigate vectorized implementations of:

- Zero-cell scanning.
- Repeated cell operations.
- Independent tape transformations.
- Memory clearing.
- Other provably parallelizable instruction patterns.

Support CPU-feature detection or explicit target selection where appropriate.

Maintain a portable fallback.

SIMD must never change tape-boundary behavior or byte semantics.

Measure the overhead of dispatch and setup.

### Level 7 — Superoptimization

Implement bounded superoptimization for small eligible instruction regions.

Possible methods include:

- Exhaustive search over a constrained instruction space.
- Algebraic canonicalization.
- Target instruction-sequence search.
- Equivalence checking.
- Cost-based selection.

Do not trust generated replacements without validation.

Do not permit superoptimization to introduce unverified memory accesses.

Search effort must remain bounded.

Compilation time is a resource.

### Optimization rule

For every transformation, record:

1. Matched pattern.
2. Preconditions.
3. Semantic equivalence argument.
4. Required memory-safety assumptions.
5. Expected performance benefit.
6. Negative test cases.
7. Actual benchmark evidence.

If a transformation cannot be justified, do not enable it by default.

---

## 11. Rust-like memory safety without changing Brainfuck

The generated program must preserve a controlled tape-memory model.

The objective is to prevent Brainfuck programs from reading or writing arbitrary host memory.

Do not describe this as full Rust ownership semantics.

Brainfuck has no ownership, borrowing, or reference syntax.

Instead, enforce the safety properties appropriate to Brainfuck.

### Required memory-safety properties

- A Brainfuck pointer cannot escape the permitted tape.
- A cell access cannot read unrelated process memory.
- A cell access cannot write unrelated process memory.
- Generated code cannot accidentally treat Brainfuck data as executable addresses.
- Invalid pointer movement traps according to the defined semantics.
- Cell arithmetic cannot overflow into neighboring cells.
- Compiler memory corruption is treated as a correctness failure.
- Optimizations preserve the same memory-safety behavior as the reference execution model.

### Proof-driven safety

Prefer:

```text
Prove access is safe
        |
        v
Remove runtime check
```

When a proof is unavailable:

```text
Cannot prove access is safe
        |
        v
Generate checked operation
        |
        v
Continue or trap
```

Do not silently treat unproven accesses as safe.

### Safety optimization techniques

Develop:

- Pointer interval analysis.
- Static tape-index bounds.
- Loop displacement analysis.
- Range propagation.
- Checked scan loops.
- Bounds-check elimination.
- Dominance-based check reuse.
- Safe tape-address calculation.
- Guarded optimized fast paths.

Whenever possible, generate one check for an entire proven-safe region rather than repeating identical checks.

A memory-safety optimization is accepted only if equivalence testing confirms that all relevant out-of-bounds behaviors remain correct.

### Bare-metal safety

For bare-metal targets, safety must not depend on the presence of an operating-system memory manager.

Generated code must enforce the selected tape-memory boundary contract through appropriate software checks or hardware mechanisms.

Do not claim that arbitrary MMIO or inline machine instructions are memory-safe.

Such operations are outside ordinary Brainfuck semantics.

### Security testing

Test adversarial programs involving:

- Pointer underflow.
- Pointer overflow.
- Nested loops.
- Large movements.
- Repeated wrapping arithmetic.
- Input exhaustion.
- Compiler resource exhaustion.
- Unbalanced brackets.
- Pathological optimizer cases.
- Malformed or oversized compilation inputs.

A successful compilation is not proof of memory safety.

Require executed tests and supporting analysis.

---

## 12. Minimal mandatory runtime overhead

Aim for native binaries with no mandatory language runtime beyond what their chosen execution semantics and target ABI require.

Do not impose:

- Garbage collection.
- Reference counting.
- A virtual machine.
- A scheduler.
- An exception runtime.
- Reflection metadata.
- Hidden dynamic allocation.
- Hidden locks.
- Hidden threading.
- Hidden system calls.
- Unnecessary dynamic linking.
- A C standard library on targets where the ABI and I/O contract do not require one.
- A mandatory JIT.
- A large startup framework.

These are size and dependency goals, not reasons to break a platform ABI. Windows needs documented OS API imports; Android may need its loader or Bionic. Disclose required platform libraries instead of claiming every target is a static Linux binary. Keep the initial Linux x86-64 path static and libc-free.

Fixed tape storage is acceptable.

An optional growth policy may be investigated as a separately defined execution profile, but must not silently change the initial fixed-tape semantics.

Generated programs must carry only the code and data required to implement the specified Brainfuck behavior.

Where the platform requires startup code, ABI glue, or output handling, generate the smallest correct implementation.

Optimize binary size without sacrificing correctness or disproportionately harming runtime performance.

---

## 13. Bare-metal and low-level targets

The compiler must eventually support execution without an operating system.

Initial bare-metal work should target a well-documented platform with an emulator or development board available for testing.

A bare-metal backend must define:

- CPU architecture.
- Entry-point contract.
- Tape memory placement.
- Startup state.
- Linker and image layout.
- Memory limits.
- Input behavior.
- Output behavior.
- Trap handling.
- Termination or idle behavior.

Brainfuck's input and output instructions may be mapped to explicitly documented byte-oriented platform devices where that preserves the selected environment contract.

For example, a UART can supply input bytes and receive output bytes.

This does not grant Brainfuck unrestricted access to interrupts, MMIO, DMA, or arbitrary peripheral registers.

Do not claim hardware-driver capability solely because machine-code generation exists.

Features requiring effects beyond Brainfuck's eight operations must be handled through explicit external environments or acknowledged as unsupported by unmodified standalone Brainfuck.

Do not hide such limitations.

### Bare-metal acceptance proof

Require an actual executed program, under hardware or an accurately configured emulator, that:

1. Starts without an operating system.
2. Initializes its tape correctly.
3. Executes the generated Brainfuck instructions.
4. Performs the documented byte I/O.
5. Preserves pointer safety.
6. Produces the expected output.
7. Uses no unnecessary managed runtime.

Record the exact target and evidence.

---

## 14. Required Linux, Windows, and Android native targets

**All three operating systems are required.** Linux x86-64 remains the first bootstrap target. After S2 self-hosting works there, implement Windows and Android without rewriting the Brainfuck compiler in another language. Both the **native compiler executable** and the **Brainfuck programs it emits** must actually run on each supported platform.

| Required target | Initial architecture and artifact | Environment contract |
|---|---|---|
| Linux | x86-64, static ELF executable | System V ABI, documented Linux byte I/O, no mandatory libc |
| Windows | x86-64, PE32+ console `.exe` | Microsoft x64 ABI, documented Win32 imports for standard handles, byte input/output, termination, and traps |
| Android | AArch64 (`arm64-v8a`), executable ELF PIE | Documented Android API level, loader/ABI, supported shell execution environment, byte I/O, termination, and traps |

### Platform-specific requirements

**Windows:** Emit valid PE32+ headers, sections, imports, addresses, relocations if needed, executable permissions, entry point, and correct x64 machine code. Honor Windows x64 calling convention, stack alignment, shadow space, and nonvolatile-register rules when calling OS APIs. Use documented Windows APIs for handles and I/O (including redirected standard streams); do not hardcode undocumented Windows syscall numbers. No C/Rust compiler, assembler, or linker may be required in the production path.

**Android:** Generate position-independent AArch64 executable code in a valid ELF PIE, with appropriate relocation/load layout and the documented Android ABI. Choose and record the minimum tested API level, execution environment, loader needs, and any Bionic or system-service dependencies. Android has execution and packaging restrictions that depend on release and installation context: a native command-line executable run in a supported shell is **not** automatically an APK or an app that can execute from every directory. Do not claim APK, Play Store, or unrestricted app-sandbox support unless separately implemented and executed. Do not copy Linux x86-64 startup assumptions into Android AArch64.

**Linux:** Keep the initial static ELF self-hosting path functioning. All target paths must enforce the same Brainfuck tape semantics, modulo byte arithmetic, EOF behavior, source filtering, and deterministic bounds traps. Platform-specific process exit behavior and executable loading must be documented and tested.

Keep shared parsing, verified optimizations, tape rules, and diagnostics common. Implement only necessary machine encoding, executable-format construction, calling convention, startup, I/O, and trap handling per target, all in Brainfuck. Platform OS APIs or an explicitly documented loader/libc dependency are allowed where genuinely needed; they are not a hidden C/Rust compiler or a new Brainfuck instruction. Keep platform dependencies minimal and report them accurately rather than pretending that every operating system supports the Linux no-libc model.

### Compiler execution, output, and proof

For **each** of Linux, Windows, and Android, verify separately:

1. Generate the platform's native compiler binary from the authoritative commented `.bf` source through the Brainfuck compiler's own code-generation logic.
2. Run that compiler on its target OS or a correctly configured emulator/VM; it must compile ordinary Brainfuck source into native executables for that target.
3. Run the emitted executables and compare output, EOF, wrapping, loop behavior, deterministic traps, and termination with the same semantic reference.
4. Have the **native compiler on that platform compile its own full authoritative Brainfuck source**, run the result, and repeat the self-hosting check. Record output hashes and equivalence evidence.
5. If cross-compilation is provided, test the cross-produced artifact on the actual target. Report cross-compilation and on-device self-hosting as different capabilities.

A cross-compiler that emits a Windows `.exe` or Android ELF but cannot run the compiler on the corresponding operating system does **not** satisfy full platform support. Likewise, format headers alone do not prove executability. Test native Windows with Windows or a compatible, explicitly identified environment; test Android with a supported device or emulator, not a generic Linux runner.

Maintain a single shared source where practical. Target-specific Brainfuck modules may be kept separate if the assembly/concatenation process is deterministic and verified, and the complete authoritative implementation remains ordinary Brainfuck. No generated C, assembly, Rust, LLVM IR, or external compiler may become the production path.

### Optional future targets

Only after the three required targets have executed successfully, consider more platforms based on real demand and test availability:

- Other ISAs: RISC-V, additional ARM and x86 variants.
- Other systems: macOS, BSD/Unix, embedded and bare-metal environments.
- Other formats: Mach-O, WebAssembly/WASI, and firmware images.

Do not implement these preemptively.

### Backend maturity levels

Track each target independently: executable format, machine-code encoding, loader compatibility, platform ABI/I/O, correctness, tape safety, optimizations, native compiler execution, native self-hosting, cross-compilation, and performance. Label each capability with execution evidence, not a promised feature list.

---

## 15. Universal replacement ambition and its limits

The long-term ambition is to explore how much real software can be authored as ordinary Brainfuck and compiled into practical native programs.

Target workload classes may include:

- Command-line tools.
- Stream processors.
- Parsers.
- Data encoders and decoders.
- Numeric algorithms.
- Embedded controllers.
- Firmware-style programs.
- Self-hosted compilers.
- Byte-oriented application protocols.
- Platform-integrated applications where a documented I/O environment is sufficient.

More ambitious classes include:

- Desktop applications.
- Servers.
- Databases.
- Network services.
- Games.
- Scientific applications.
- GPU-related workloads.
- Operating-system components.

However, do not claim these are all directly expressible with practical standalone semantics solely because Brainfuck is computationally universal.

Brainfuck has only tape manipulation, loops, and byte I/O.

It has no native operation for opening files, making system calls, creating threads, mapping devices, or launching GPU kernels.

An external byte-stream protocol can communicate with a host that provides some of these services.

That host is an external dependency and must be disclosed.

It must not be described as a zero-overhead language feature.

Never silently redefine ordinary Brainfuck instruction sequences as privileged platform operations.

### Honest replacement definition

For a workload to count as supported:

1. Its program logic must be authored in standard Brainfuck.
2. The compiler must preserve standard Brainfuck semantics.
3. The target's input/output and environment contract must be explicit.
4. Any host service or adapter must be disclosed.
5. The workload must execute successfully.
6. Any required runtime costs must be measured.
7. No additional source-language constructs may be introduced.

Separate direct standalone capabilities from capabilities that require an external service environment.

Do not solve universality through hidden language extensions.

---

## 16. Compiler-owned internal algorithms

Brainfuck has no variables, functions, or structured data types.

The compiler may still implement sophisticated algorithms through conventions over its tape.

Develop and document internal techniques for:

- Multi-byte integers.
- Counters.
- Indexed memory access.
- Stack emulation.
- Queues.
- Maps or tables where practical.
- State machines.
- Buffer management.
- Binary emission.
- Offset calculation.
- Arithmetic beyond eight bits.
- Error propagation.
- Source traversal.
- Compiler pass scheduling.

These are Brainfuck algorithms.

Do not make their symbolic representations part of the source language.

Generated listings and conceptual pseudocode may use descriptive names to help humans understand the implementation.

They must always map back to actual Brainfuck instructions.

The authoritative implementation must remain executable by a standard Brainfuck interpreter.

---

## 17. Diagnostics and debugging

Brainfuck is difficult to inspect manually.

Provide derived tools and artifacts that make the compiler understandable.

Prioritize:

- Instruction offset maps.
- Pointer-position traces.
- Tape-region visualizations.
- Loop nesting maps.
- Compiler phase traces.
- Native disassembly.
- Generated instruction mappings.
- Optimization logs.
- Memory-bound analysis reports.
- Trap diagnostics.
- Compiler error records.
- Bootstrap comparison reports.

These may be generated by development tools, but must not become authoritative compiler source.

The production compiler must not depend on a foreign debugger, optimizer, or interpreter.

### Diagnostics policy

Define a stable diagnostic protocol for compiler errors.

Include at least:

- Invalid source or unmatched brackets.
- Program exceeds supported size.
- Loop nesting exceeds supported limit.
- Compiler tape capacity exceeded.
- Generated artifact overflow.
- Unsupported target configuration.
- Internal compiler invariant failure.

Because standard Brainfuck exposes only input/output byte operations, use a clearly specified transport mechanism to distinguish compilation results from diagnostics.

Do not claim support for native stderr or arbitrary exit codes if the implemented I/O contract does not provide it.

Do not silently emit a partial executable and report success.

---

## 18. Autonomous AI development

The project must be designed for AI to maintain without human coding.

Humans may provide goals, review results, and choose priorities.

AI must be able to:

1. Read the repository.
2. Inspect Brainfuck source.
3. Query annotation and offset mappings.
4. Understand compiler memory conventions.
5. Identify affected compiler regions.
6. Make localized source modifications.
7. Update annotations.
8. Rebuild the compiler.
9. Run the self-hosting test.
10. Run semantic tests.
11. Run performance benchmarks.
12. Compare results.
13. Revert regressions.
14. Update evidence.
15. Update documentation.
16. Prepare a verifiable release.

Do not require a human to write C, Rust, Python, or assembly to complete an ordinary maintenance task.

### Avoid regenerating the entire compiler

Prefer localized source changes.

Maintain source-region metadata so AI agents can locate meaningful units within long Brainfuck instruction streams.

Do not invent a high-level textual language to make editing easier.

Use generated navigation tools and deterministic instruction-offset mappings.

If the editing process temporarily uses an internal representation, the final authoritative executable implementation must still be the standard Brainfuck instruction stream.

Ensure any transformations used to write source are deterministic and inspectable.

### AI maintenance metrics

Track:

- Successful changes.
- Failed changes.
- Reverted regressions.
- Verification failures.
- Bootstrap failures.
- Compiler size changes.
- Runtime changes.
- Compilation-time changes.
- Benchmark regressions.
- Diagnostic quality.
- Total work required for a successful fix.

AI token-efficiency research may be conducted later.

Do not make arbitrary token targets more important than correctness, self-hosting, or runtime performance.

---

## 19. Testing policy

Testing is mandatory for every implementation milestone.

The test suite must include independent reference implementations and execution environments where practical.

External test harnesses written in other languages are permitted as development infrastructure.

They must be isolated from the shipping compiler and must not contain production compilation logic.

Keep authoritative compiler code and generated runtime logic in Brainfuck.

### Basic semantic tests

Test:

- Empty program.
- Increment.
- Decrement.
- Wrapping arithmetic.
- Pointer movement.
- Nested loops.
- Input.
- Output.
- EOF.
- Zero-cell loops.
- Cell-transfer loops.
- Multiple-cell transformations.
- Pointer boundary behavior.
- Invalid brackets.
- Non-instruction text compatibility.
- Zero-byte input and output.

### Advanced semantic tests

Test:

- Very large loop counts.
- Deep loop nesting.
- Wrapping induction variables.
- Nonterminating loops with execution limits.
- Complex pointer movement.
- Multiple nested cell transfers.
- Overflow-sensitive transformations.
- Boundary-sensitive optimizations.
- Compiler memory exhaustion.
- Large executable generation.
- Repeated self-compilation.

### Differential testing

For each test program:

1. Execute it using an independent Brainfuck interpreter.
2. Execute the compiled native program.
3. Supply identical input.
4. Use identical tape and EOF semantics.
5. Compare output bytes.
6. Compare defined trap behavior.
7. Compare final tape state when observable through test instrumentation.
8. Check termination or controlled execution limits.

A timeout is not proof of semantic equivalence.

Treat inconclusive tests as inconclusive.

### Randomized testing

Generate valid random Brainfuck programs.

Use bounded execution and resource limits.

Compare independent implementations.

Use structured generators that target:

- Loops.
- Pointer movement.
- Cell arithmetic.
- Boundary cases.
- Optimizer recognition patterns.
- Nested transformations.

Add shrinking or reduction techniques so failing programs can be minimized.

### Optimizer equivalence tests

Every optimizer pass must have:

- Positive tests.
- Negative tests.
- Boundary tests.
- Overflow tests.
- Nested-loop tests.
- Invalid-precondition tests.
- Differential tests.

Prefer translation validation for complex transformations.

Never rely only on tests that match the optimizer author's assumptions.

### Self-hosting regression

Every accepted change to compiler logic must rerun the self-hosting sequence.

A compiler that can no longer compile itself fails the primary architectural requirement.

---

## 20. Performance objectives

The project must compete against optimized native implementations, not merely against interpreters.

Do not describe a benchmark against an interpreter as proof of superiority over C or Rust.

### Primary performance goal

For each comparable workload, seek generated execution performance equal to or better than the fastest valid optimized implementation in the benchmark set.

A long-term stretch target, adapted from the supplied XAX performance requirement, is a median runtime ratio of no more than:

**0.9999× the fastest valid non-Brainfuck baseline.**

Calculate:

```text
BF native median runtime
------------------------
Fastest competing native median runtime
```

This threshold is an optimization objective, not permission to make unsupported claims.

A measured difference of 0.01% may be statistical noise.

Do not claim performance leadership without sufficient repeated evidence and uncertainty analysis.

If the threshold is not met, report the real result and continue optimizing.

Never weaken a benchmark to manufacture a passing ratio.

### Required baselines

For CPU runtime performance, compare against:

- The optimized Brainfuck native compiler.
- An optimized C or C++ implementation.
- An optimized Rust implementation.
- An independent Brainfuck interpreter as an additional reference.
- Other relevant native implementations (for example Zig, Go, or Swift) when they can express an equivalent workload and the comparison adds useful information.

Use optimized release builds and representative algorithms, including workloads unfavorable to Brainfuck. Compare like-for-like data, safety guarantees, I/O, target hardware, and algorithmic work; report unavoidable model or runtime differences. Do not claim one language is universally faster than another. Generated Brainfuck machine code can match or beat particular C/Rust implementations; no compiler can promise superiority over every optimal C/Rust program on every workload.

Do not require every benchmark to favor Brainfuck.

Equivalent observable behavior is mandatory.

### Two benchmark categories

**Category A — Equivalent Brainfuck semantics**

Compare different execution engines and compilers on identical Brainfuck source programs.

This measures the effectiveness of Brainfuck compilation and optimization.

**Category B — Equivalent algorithms**

Compare Brainfuck-generated native programs against C, Rust, and other implementations performing the same algorithm.

Use identical input, output, validation, and workload requirements.

This measures practical native competitiveness.

Do not mix Category A and Category B into one misleading speedup claim.

### Required benchmark measurements

Record:

- CPU model.
- Microarchitecture.
- CPU frequency and scaling conditions.
- RAM.
- Operating system.
- Kernel version where relevant.
- Compiler versions.
- Optimization flags.
- Input data.
- Workload definition.
- Warmup policy.
- Number of repetitions.
- Raw sample timings.
- Median execution time.
- Variance or confidence interval.
- Peak memory usage.
- Binary size.
- Compilation time.
- Generated instruction count where useful.
- Test date.
- Repository revision.
- Artifact hashes.

Interleave benchmark order to reduce systematic measurement bias.

Avoid comparing measurements from different hardware.

### Performance investigations

When Brainfuck is slower:

1. Identify the workload.
2. Profile the generated native code.
3. Inspect unnecessary instructions.
4. Check memory access frequency.
5. Check branch behavior.
6. Check bounds-check overhead.
7. Check register use.
8. Check loop optimization opportunities.
9. Implement a justified improvement.
10. Rerun semantic tests.
11. Rerun self-hosting.
12. Rerun all affected performance baselines.

Do not optimize only for benchmark scores.

Prefer changes that improve realistic workloads without unacceptable regressions.

---

## 21. Compilation speed and memory footprint

Runtime speed is the primary performance objective, but compiler practicality also matters.

Measure:

- Compiler startup time.
- Parsing throughput.
- Optimization time.
- Machine-code generation time.
- Peak compiler tape usage.
- Executable size.
- Compiler binary size.
- Total bootstrap duration.

Build a fast compilation mode and an aggressive optimization mode when justified.

These are compiler modes, not new Brainfuck language semantics.

Both must produce correct programs.

The aggressive mode may use more compilation time for stronger optimization.

The fast mode must not silently disable essential memory safety.

Avoid unbounded optimizer search.

Avoid holding unnecessary copies of source and IR data.

A compiler written in Brainfuck can become expensive to execute.

Treat compiler performance as a real engineering problem rather than assuming self-hosting makes it fast.

---

## 22. Compiler safety and trust

The compiler itself is a potential attack surface.

It processes untrusted source and generates executable machine code.

Protect against:

- Invalid bracket nesting.
- Integer overflow in compiler bookkeeping.
- Malformed source causing memory corruption.
- Buffer exhaustion.
- Incorrect relocation offsets.
- Incorrect binary size calculations.
- Invalid machine instruction encoding.
- Unexpected compiler nontermination.
- Resource exhaustion.
- Corrupted output artifacts.

Apply the same tape memory-safety rules to the compiler as to ordinary compiled Brainfuck programs.

### Artifact validation

Use independent tools where available to inspect:

- Binary headers.
- Executable segments.
- Entry points.
- Branch destinations.
- Relocations.
- Instruction encodings.
- Executable memory permissions.

Disassembly tools may validate generated code.

They must not secretly repair generated executables.

When possible, execute compiled programs in constrained environments during testing.

Do not execute arbitrary untrusted generated binaries without appropriate isolation.

---

## 23. Reproducibility and dependency policy

The production compiler should have the smallest practical dependency set.

Required production dependencies must be disclosed.

A self-hosted native release must not require Python, Rust, GCC, Clang, or LLVM to compile Brainfuck programs.

External tools may remain necessary for:

- Initial cold bootstrapping.
- Independent validation.
- Benchmarking.
- Debugging.
- Packaging.
- Cross-platform testing.

Keep these roles separate.

### Reproducible builds

Provide a clean-checkout procedure to:

1. Verify source integrity.
2. Bootstrap the first compiler.
3. Compile the authoritative source.
4. Recompile it with the resulting binary.
5. Compare outputs.
6. Run tests.
7. Generate evidence.
8. Produce release artifacts.

Record input and output hashes.

Do not embed unstable timestamps or random identifiers in deterministic builds unless explicitly requested.

Document all nondeterminism.

A binary release without its corresponding Brainfuck source and reproducibility instructions is incomplete.

---

## 24. Repository structure

Use a small, coherent repository.

Create or adapt the following structure where useful:

```text
README.md
LICENSE
AGENT.md
CLAUDE.md

docs/
    ARCHITECTURE.md
    BRAINFUCK_SPEC.md
    SELF_HOSTING.md
    BOOTSTRAP_TRUST.md
    COMPILER_INTERNALS.md
    MEMORY_SAFETY.md
    OPTIMIZATIONS.md
    TARGETS.md
    BENCHMARKS.md
    CONFORMANCE.md
    DECISIONS.md
    OPEN_ISSUES.md
    IMPLEMENTATION_ROADMAP.md
    STATE.md
    HANDOFF.md
    COMMENT_STYLE.md

compiler/
    core.bf                  # authoritative raw BF plus safe inline comments
    core.bf.notes.md         # optional detailed notes

bootstrap/
    README.md
    evidence/

targets/
    x86_64_linux/
    x86_64_windows/
    aarch64_android/
    baremetal/               # only when implemented
    wasm/                    # only when implemented

tests/
    programs/
    expected/
    selfhost/
    optimizer/
    safety/
    differential/

benchmarks/
    programs/
    baselines/
    results/

examples/
    hello.bf
    arithmetic.bf
    transfer.bf

evidence/
    bootstrap/
    correctness/
    safety/
    performance/
    targets/

status/
    CONFORMANCE_MATRIX.json
    BUILD_MANIFEST.json
```

This is a suggested structure, not permission to create hundreds of empty files.

Create files when they contain useful implementation, specifications, or evidence.

The compiler implementation must be in Brainfuck.

Target backend descriptions may be documented separately, but executable backend logic must remain Brainfuck.

Keep generated artifacts clearly separated from authoritative source.

Do not introduce a second implementation language through build scripts or generated-source systems.

---

## 25. Conformance and maturity levels

Track project maturity using evidence-gated levels.

### S0 — Standard Brainfuck source

The compiler's authoritative implementation exists entirely as standard Brainfuck instructions.

The program executes under an independent conforming interpreter.

Source purity (only eight executable instructions, with safe ignored `.bf` comments) and basic semantics are verified.

### S1 — Native compiler execution

The Brainfuck compiler generates a real native executable through its own Brainfuck implementation.

The executable runs correctly on the initial supported target.

No external language compiler performs code generation.

### S2 — Verified self-hosting

The native compiler successfully compiles its own Brainfuck source.

The resulting compiler repeats the process successfully.

Bootstrap stages agree under the documented equivalence criteria.

**S2 is the minimum acceptable first working release.**

### S3 — Verified memory safety

Generated programs enforce the defined tape-memory model.

Boundary behavior is tested.

Optimizer memory-safety preconditions are validated.

Unsafe transformations are rejected.

### S4 — Native performance competitiveness

The compiler has an established optimization suite.

Representative native benchmarks compare against valid C and Rust baselines.

Runtime, memory, code size, and compilation time are measured.

Any claimed performance leadership has statistically defensible supporting evidence.

The 0.9999× goal must be reported as met or unmet, not assumed.

### S5 — Practical platform capability

At least one nontrivial standalone application executes successfully using the supported Brainfuck semantics.

Windows x86-64 and Android AArch64 must each have native execution and native self-hosting evidence before the three-platform objective is called complete. Any additional native or bare-metal targets require their own execution evidence.

External runtime or host-service dependencies are disclosed.

### S6 — Autonomous self-maintenance

AI successfully modifies the Brainfuck compiler using Brainfuck source as the sole authoritative implementation.

The modified compiler:

- Builds successfully.
- Passes semantic tests.
- Self-hosts again.
- Passes memory-safety tests.
- Preserves required behavior.
- Produces benchmark evidence.
- Completes a reproducible release cycle.

These levels must be supported by evidence.

Do not assign a higher level based solely on architectural design.

---

## 26. Evidence classification

Every major implementation claim must have one of these labels:

- **PROVEN** — Formal or sufficiently rigorous verified property under clearly defined assumptions.
- **EXECUTED** — Successfully run on the stated target.
- **MEASURED** — Quantitatively measured under documented conditions.
- **STRUCTURAL** — Implementation structure exists but full execution is unverified.
- **PROTOTYPE** — Experimental implementation with limited validation.
- **UNIMPLEMENTED** — Planned or absent.

Never label structural support as executed support.

Never label a passing unit test as a formal proof.

Never label a benchmark result as universal superiority.

Record evidence artifact paths and repository revisions.

Historical evidence must remain historical.

Do not reuse old performance results after meaningful code-generation changes without rerunning the affected benchmarks.

---

## 27. Machine-readable conformance matrix

Maintain a machine-readable status matrix for each target.

Track at least:

- Target architecture.
- Operating environment, minimum version or Android API level, and tested execution context.
- Executable format and target ABI.
- Brainfuck semantic profile.
- Parser correctness.
- Native code generation.
- Native compiler execution on the target.
- Native self-hosting status, separately from cross-compilation.
- Bootstrap reproducibility.
- Tape safety.
- Loop optimization.
- SIMD support.
- Input/output support.
- Binary size.
- Peak memory.
- Compilation speed.
- Runtime benchmark status.
- Bare-metal execution status.
- Platform loader/API and external runtime dependencies.
- Latest evidence revision.
- Known failures.
- Known blockers.
- Current conformance level.

Prefer generating documentation summaries from authoritative machine-readable evidence.

Do not maintain contradictory status claims across several files.

---

## 28. Documentation synchronization

Documentation is part of implementation.

Whenever compiler behavior changes, update all affected documentation before declaring completion.

At minimum, check:

- README.
- Language specification.
- Compiler architecture.
- Self-hosting instructions.
- Memory-safety model.
- Optimization documentation.
- Supported targets.
- Benchmark documentation.
- Conformance matrix.
- Current state.
- Roadmap.
- Handoff notes.
- AI agent instructions.

Do not leave stale statements.

Do not claim a target is unsupported after real evidence establishes support.

Do not claim an optimization is implemented if it remains experimental.

Do not change historical records to pretend a feature existed earlier.

Every documentation file must have clear heading structure and consistent terminology.

Verify links and referenced paths.

Keep the README useful and relatively short.

Place detailed technical explanations in the appropriate documents.

---

## 29. Architecture decision rules

When deciding between competing implementations, apply these rules.

**Rule 1 — Correctness first**

Reject any optimization that changes defined Brainfuck behavior.

**Rule 2 — Self-hosting always**

Prefer designs that can be implemented and maintained within Brainfuck itself.

**Rule 3 — Native execution**

Prefer direct native code generation over mandatory interpreters or virtual machines.

**Rule 4 — Memory safety**

Prefer proof-based check elimination to unsafe unchecked execution.

**Rule 5 — No source-language extensions**

If a feature requires a ninth instruction, reject it.

**Rule 6 — Minimal dependencies**

Avoid unnecessary external runtime and compilation dependencies.

**Rule 7 — Small implementation**

Prefer a simpler Brainfuck algorithm when it gives equivalent correctness and performance.

**Rule 8 — Measured optimization**

Choose performance improvements using real evidence.

**Rule 9 — No speculative complexity**

Do not build universal infrastructure before a concrete need is established.

**Rule 10 — Inspectability**

Explain unusual compiler algorithms in safe `.bf` comments, with companion notes and generated views only when useful.

**Rule 11 — No fake universality**

A capability that requires an external service must be described as such.

**Rule 12 — Reproducibility**

A result that cannot be repeated must not be presented as a verified release milestone.

---

## 30. First implementation milestone

The first milestone must demonstrate genuine self-hosting.

Do not attempt every platform or optimization simultaneously.

Build the smallest functioning native compiler that meets the self-hosting requirement.

### Required features

- Compiler written in standard Brainfuck.
- Raw `.bf` source containing only the eight executable instructions and validated ignored comments.
- Basic input filtering and parsing.
- Correct bracket matching.
- All eight instructions supported.
- 8-bit wrapping cell semantics.
- Fixed tape memory.
- Safe tape boundaries.
- Linux x86-64 ELF output.
- Native executable entry point.
- Working input and output.
- Correct loop execution.
- Deterministic compilation.
- Full self-compilation cycle.
- Independent semantic validation.

### Required tests

The first release must compile and execute:

- An empty program.
- Hello World.
- A simple arithmetic program.
- A copy/transfer program.
- Nested loops.
- Input/output echo.
- EOF handling.
- Pointer boundary failures.
- Invalid bracket programs.
- Its own compiler source.

The compiler must survive at least one complete native self-compilation cycle with independent verification.

### Milestone completion rule

If the compiler cannot compile itself, the first milestone is not complete.

Do not substitute a BF-to-C compiler.

Do not substitute a C compiler with a Brainfuck front end.

Do not substitute an interpreter that merely executes source.

Do not substitute a generated binary whose compilation logic cannot be traced to the authoritative Brainfuck source.

---

## 31. Subsequent milestones

After the first genuine self-hosting release, develop in this order unless real profiling or correctness evidence justifies a change.

### Milestone 2 — Stronger Brainfuck optimizer

Implement:

- Instruction merging.
- Pointer analysis.
- Zero-loop optimization.
- Cell-transfer optimization.
- Multiply-add loops.
- Basic affine-loop analysis.
- Dead-code elimination.
- Differential optimization tests.

Rerun self-hosting after each major optimization change.

### Milestone 3 — Advanced safety analysis

Implement:

- Pointer interval tracking.
- Static boundary proofs.
- Check elimination.
- Optimizer safety verification.
- Negative safety tests.
- Compiler-internal memory checks.

Measure safety overhead.

### Milestone 4 — Native performance optimization

Implement:

- Register caching.
- Better branch generation.
- Loop specialization.
- Code layout.
- SIMD scanning.
- Whole-program analysis.
- Benchmark-driven improvements.

Compare against optimized C and Rust.

### Milestone 5 — Faster self-hosted compiler

Optimize the compiler's own Brainfuck implementation.

Reduce:

- Bootstrap time.
- Self-compilation time.
- Compiler tape use.
- Generated compiler size.
- Repeated parsing work.
- Redundant memory operations.

Measure the improvement.

### Milestone 6 — Native Windows and Android support

Add Windows x86-64 PE32+ and Android AArch64 ELF PIE using the same authoritative Brainfuck compiler logic. Implement only necessary target-specific machine encoding, binary layout, ABI glue, I/O, and traps.

Execute the compiler and its generated programs on both platforms. Prove full native self-hosting on each platform, not just cross-compilation. Keep Linux self-hosting and correctness intact. Record tested Windows versions, Android API levels, target environments, dependencies, and artifact hashes.

Do not label the required three-platform goal complete while either target remains unverified.

### Milestone 7 — Bare-metal execution

Generate a target-specific standalone image.

Demonstrate an actual emulated or hardware execution.

Document the byte-I/O environment.

### Milestone 8 — Broader toolchain maturity

Expand:

- Debugging.
- Profiling.
- Cross-compilation between verified Linux, Windows, and Android targets.
- Artifact validation.
- Incremental engineering workflows.
- More sophisticated optimization proofs.

### Milestone 9 — Practical Brainfuck-only applications

Build substantial programs entirely in standard Brainfuck.

Measure their runtime, memory, binary size, and dependence on external services.

### Milestone 10 — Autonomous maintenance proof

Demonstrate a complete AI-led modification and release cycle on the self-hosted compiler.

All milestones must maintain previously proven behavior.

Never let a later optimization silently break self-hosting.

---

## 32. Continuous validation gates

For every meaningful compiler change, run the following gates.

### Gate A — Source purity

Verify that all authoritative `.bf` source executes only the eight instructions, declared comments contain none of those instruction bytes, and comment stripping preserves the exact executable stream.

### Gate B — Semantic correctness

Run applicable reference and native differential tests.

### Gate C — Self-hosting

Rebuild the compiler with itself and verify stage equivalence.

### Gate D — Memory safety

Run boundary and optimizer-safety tests.

### Gate E — Native artifact validity

Validate executable structure and run generated programs.

### Gate F — Performance regression

Run affected performance tests and compare against saved evidence.

### Gate G — Documentation consistency

Synchronize implementation facts, current state, and evidence.

### Gate H — Reproducibility

Verify deterministic artifacts where required.

### Gate I — Target compatibility

For any change to target encoding, ABI, startup, I/O, or trap handling, rerun affected native execution and self-hosting checks on Linux, Windows, or Android as applicable. Report targets that could not be tested as unverified, not passed.

A change may be merged only when all applicable mandatory gates pass.

If a gate cannot be executed, record the precise reason.

Never mark an unexecuted gate as passed.

---

## 33. Anti-goals

Do not:

- Add a ninth Brainfuck instruction.
- Invent Brainfuck 2.0.
- Introduce function syntax.
- Introduce variable syntax.
- Introduce type syntax.
- Introduce inline assembly syntax.
- Make compiler comments executable or put Brainfuck instruction characters inside `.bf` comment text.
- Turn annotations into a separate authoritative source language.
- Write the production compiler in C.
- Write the production compiler in Rust.
- Write the production compiler in Python.
- Use another compiler for production code generation.
- Require LLVM.
- Require GCC or Clang for self-hosting.
- Require a VM for native executables.
- Require a garbage collector.
- Require a managed runtime.
- Hide memory-unsafe operations.
- Assume undefined host behavior is legal Brainfuck behavior.
- Remove bounds checks without proof.
- Pretend hardware APIs exist in Brainfuck.
- Disguise an external service as a language feature.
- Claim universal performance superiority.
- Optimize only against interpreters.
- Claim self-hosting without a complete compiler bootstrap cycle.
- Claim target support without execution.
- Claim formal memory safety from unit tests alone.
- Create documentation without working implementation when useful implementation work is possible.
- Invent test results.
- Invent benchmark numbers.
- Conceal regressions.
- Ask humans to write missing implementation code.
- Delay self-hosting until a future rewrite.

If a goal cannot be achieved under the exact eight-instruction language constraint, explain the limitation and preserve the constraint.

The language does not bend to rescue an architectural claim.

---

## 34. Work autonomously

Operate as an autonomous engineering agent.

Do not ask for approval for routine implementation choices.

When encountering uncertainty:

1. Inspect the relevant source.
2. Inspect the normative specification.
3. Identify the simplest correct option.
4. Record the decision.
5. Implement a small working version.
6. Test it.
7. Check self-hosting.
8. Measure performance if relevant.
9. Update documentation.
10. Continue to the next highest-priority blocker.

Do not stop after producing an architecture essay.

Write real Brainfuck code.

Run it.

Compile it.

Test it.

Inspect the native machine code.

Benchmark it.

Make the compiler compile itself.

If the current development environment cannot execute a required test, provide the exact blocker and label the result unverified.

Do not fabricate success.

If a task is too large for one development iteration, finish the smallest independently verifiable improvement while preserving the complete architectural objective.

Every iteration should leave the repository in a coherent state.

---

## 35. Required end-of-iteration report

At the end of each development iteration, report:

### Implemented

What was actually changed.

### Source compliance

Whether all authoritative compiler code remains standard Brainfuck.

### Self-hosting

Which bootstrap stages were executed and whether they agreed.

### Correctness

Which tests ran, passed, failed, or could not be executed.

### Memory safety

Which properties were tested or proven.

### Performance

Measured execution time, memory use, binary size, and compilation time where relevant.

### External dependencies

Any tools or runtime components used, with their exact roles.

### Platforms

Which Linux, Windows, and Android environments were built, executed, self-hosted, or remain unverified; do not conflate cross-compilation with native execution.

### Documentation

Which documents and evidence artifacts were updated.

### Known limitations

What remains unsupported or unverified.

### Next engineering priority

The next highest-value change based on measured results and outstanding requirements.

Do not fill the report with marketing claims.

Keep it factual.

If something failed, explain why.

---

## 36. Final success conditions

The project succeeds when its authoritative compiler is standard Brainfuck and a reproducible build can perform:

```text
Brainfuck compiler source
          |
          v
Execute initial bootstrap
          |
          v
Native Brainfuck compiler
          |
          v
Compile its own Brainfuck source
          |
          v
Self-compiled native compiler
          |
          v
Verify equivalent compilation
          |
          v
Build and self-host natively on Linux, Windows, and Android
          |
          v
Compile ordinary Brainfuck programs
          |
          v
Optimized native executables
          |
          v
Verify semantics and tape safety
          |
          v
Benchmark against C and Rust
          |
          v
Repeat through autonomous maintenance
```

No extra Brainfuck instructions are required.

No foreign compiler owns the implementation.

No hidden source language exists.

Memory-safety guarantees are explicit.

External environment capabilities are disclosed.

Performance claims are supported by measurements.

All source remains inspectable.

The compiler remains self-hosted after updates, with tested native compiler builds for Linux, Windows, and Android.

The broader objective is to match or exceed optimized C, Rust, and other mainstream native implementations on measured comparable workloads where possible, while retaining strong, verifiable tape-memory safety and the simplicity of the original language. This is a performance target, never an unmeasured guarantee.

Do not claim that Brainfuck will outperform every C or Rust implementation.

Do not claim that compiler engineering can erase fundamental limitations of Brainfuck's I/O and execution model.

Instead, find out how far the original eight instructions can go when the compiler does the difficult work.

**Final invariant:**

Brainfuck stays Brainfuck.

The compiler stays Brainfuck, with safe human comments in `.bf` files.

The generated executable runs natively on each verified Linux, Windows, and Android target.

The optimizations preserve meaning.

The tape stays inside its boundaries.

And the compiler must be able to compile itself.

No shortcuts hidden behind a nicer README.

## Start work

Inspect the repository and determine the shortest path to a real, verifiable self-hosted Brainfuck-to-native compiler.

If the repository already satisfies that requirement, verify it independently and continue with correctness, safety, Windows and Android support, and performance improvements.

If it does not, prioritize the genuine Brainfuck-only compiler and its complete Linux bootstrap cycle, then required native Windows and Android self-hosting, above optional features.

Implement, execute, validate, record evidence, and continue autonomously.