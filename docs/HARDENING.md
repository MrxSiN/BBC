# Native backend hardening — Iteration 9

## ELF file length

Brainfuck now calculates the executable file length before writing the ELF header. For `n` *filtered commands*, the output is exactly `215 + 32n` bytes: 206 bytes of headers/startup, one 32-byte slot per byte, then 9 bytes of native termination.

The RX segment has `p_filesz = 215 + 32n`, `p_memsz = 524288`, flags `R|X`, and a 4096-byte alignment. Linux loads the written bytes and zero-fills the remainder of the mapping. The separate RW tape segment reserves 65,536 cells and has no executable permission.

Old ELF files contained **524,280** unconditional zero bytes. New files contain **zero fixed trailing padding bytes**. Empty BF input produces a 215-byte ELF; the self-hosted compiler produces **475,703** bytes. The change lives in `compiler/core.bf` and survives two independent seeds plus three native compiler stages. No Python/C patcher touches the header.

### How the sizing code works

Source input is buffered on a four-cell stride. A Brainfuck-only scan advances a three-byte little-endian length accumulator by 32 per retained command, starting from 215. Carry detection handles the 8-bit wrap boundaries. The accumulator is moved back to the header writer and cleared after its bytes are output. The original input error flag is saved elsewhere and restored; skipping that step would mark oversized source as successful.

Ignored characters are discarded inside the BF compiler before sizing; they do not produce native slots.

`tests/verify_emission.py` checks exact file size, `p_filesz`, mapping flags, startup instructions, every 32-byte slot, branch displacements and deliberately corrupted files. It does not claim a formal proof.

## Byte I/O

The native `.` and `,` slots still retry Linux `-EINTR`, report non-successful `write` via exit(3), and report failed `read` via exit(4). EOF stores zero. `EAGAIN` fails fast. The kernel's default `SIGPIPE` behavior remains. The preexisting 32-byte slots were not widened by the ELF work.

## Evidence

- `tests/verify_selfhost.py`: two C Brainfuck execution seeds and three agreeing native stages, plus runtime and invalid-source probes.
- `tests/verify.py`: 178 reference/native semantic cases.
- `tests/verify_adversarial.py`: 345 additional deterministic execution and malformed-input cases, plus documented integrated comment filtering and command-capacity behavior.
- `tests/verify_emission.py`: exact native templates, W^X layout, branch targets, NOP slots and negative file mutations.
- `tests/verify_io_faults.py`: injected read/write `EINTR`, `EAGAIN`, bad FDs and SIGPIPE.
- `tests/verify_elf_size_primitive.py`: 62 checks of an independent 251-command BF arithmetic reference.

`tests/verify_tape_safety.py` checks the emitted x86-64 pointer-guard state invariant across 131,072 abstract transitions, executes nine native witnesses, and rejects ten altered unsafe templates. This is conditional generated-code evidence, not a compiler-internal scratch-tape proof. `tests/verify_command_filter.py` separately validates an experimental native-compiled BF-only comment filter; the integrated compiler now filters source independently of that experiment.

`S2 EXECUTED` is the current proven milestone. Testing the ELF header is not a general proof of memory safety or native speed superiority.
