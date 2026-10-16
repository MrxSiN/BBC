# Optional BF filtered compilation adapter

Iteration 14 adds `bootstrap/run_filtered_compiler.py`. This is an **opt-in two-executable path**, not a replacement for `compiler/core.bf` and not a single self-contained native compiler. Both lexical filtering and ELF code generation still execute in genuine Brainfuck programs.

## Run it

From the repository root after the release verification suite:

```sh
python3 bootstrap/run_filtered_compiler.py examples/hello.bf /tmp/hello-filtered.elf
/tmp/hello-filtered.elf
```

The adapter hashes the authoritative compiler source, native compiler, BF filter source, and filter ELF against the executed bootstrap/filter evidence. If anything changed, it refuses to compile until the verification tests rebuild evidence. It transports byte-stuffed file contents to the native BF filter, checks its terminal status, transports its output to the existing native BF compiler, checks that status, and atomically installs the resulting executable.

**What the adapter does not do:** locate Brainfuck commands, remove ignored characters, parse brackets, optimize, construct ELF bytes, or link machine code. The BF filter performs the first two operations; `core.bf` performs parsing and native code generation. There is no new instruction or privileged BF comment syntax.

## Boundaries

The optional Python transport caps raw source at **8 MiB** to bound adapter memory consumption. This is an adapter resource limit, not a new Brainfuck-language rule. It checks the byte count without parsing commands. The BF filter processes sources longer than 16,128 bytes within that limit, but its **filtered commands** still must fit the unchanged backend's 16,128-byte source limit. The backend retains its 255-level nesting limit. **Iteration 19 directly integrates command filtering into the authoritative BF compiler; the two-process adapter is now optional historical tooling, not required for comments.** The optional adapter's Python process, two subprocess invocations, buffering, and source file I/O are real external dependencies. Calling this the same as a single standalone native compiler would be inaccurate.

For direct execution of `build/compiler_x86_64_linux.elf` nothing has changed: ignored input bytes consume buffer slots and 32-byte output slots. This adapter is not an integrated production frontend and does not complete the compiler-source filtering milestone in `docs/PROJECT_REQUIREMENTS.md`.

## Executed checks

`python3 tests/verify_filtered_adapter.py` exercises 28 inputs through the optional path, verifies byte-identical results against the native compiler receiving command-only inputs, and runs each resulting ELF against the semantics reference. It tests NUL and FF transport, long comments, nested loops, 16,128 filtered commands, CLI file creation, compiler rejection, preserving an earlier output on failure, tampered filter binary rejection, and a comment-heavy version of the authoritative compiler self-compiling one more stage. See `evidence/filtered_adapter.json`.

## Iteration 15 integration contract

`python3 tests/verify_filter_integration_contract.py` adds 36 executed comparison cases with arbitrary ignored bytes interleaved **inside** live Brainfuck loops, deterministic random program fragments, deeply nested control flow, EOF, wrapping, and pointer traps. It compares filtered native ELF files byte-for-byte with direct command-only compilation, independently inspects every generated slot and loop displacement, and executes the binaries against the semantic reference. Five invalid capacity/bracket/resource cases reject. The Python harness acts only as an independent oracle. Raw sources above 8 MiB fail before invoking either native executable. Evidence: `evidence/filter_integration_contract.json`.

The integration contract is a regression gate for a future decoder change. It does **not** assert that `core.bf` already compacts source.

## Next engineering step

Integrate the BF-owned streaming decoder into `compiler/core.bf`, or design a smaller BF-only packed decoder that fits the compiler's own tape and source budget. Do not promote this adapter to integrated filtering by changing only a status label.
