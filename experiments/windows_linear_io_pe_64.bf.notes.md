# Windows six-command linear I/O PE writer — Iteration 40

Source SHA-256: `b3bb09ce8708159eccfc58522fe6f5c0025d80a9f6a01e9c5731b4f3115b419e`  
Filtered instruction SHA-256: `500457d6ec7bc61f57931b915f681825a56f0262036f337d07d7f9a3839d6eb4`

The authoritative source is [`windows_linear_io_pe_64.bf`](windows_linear_io_pe_64.bf), containing **10,352 standard Brainfuck instructions**. The authoring aid is [`../tools/author_windows_linear_io.py`](../tools/author_windows_linear_io.py). It produces the Brainfuck source once; the saved BF program owns all source-dependent machine-code selection and final PE emission. It does not run during normal compilation.

## Tape conventions

- Cell 0: incoming filtered opcode, NUL indicates end of input.
- Cells 1–3: scratch for exact opcode equality.
- Cell 4: next command processing flag; cell 5: remaining source slots.
- Cell 6: reject status; cell 7: opcode matched.
- Cell 8: temporary loop multiplier for constant byte emission, zero between bytes.
- Cell 9: emitted byte accumulator, restored to zero after each static emission segment.
- Cells 10–13: slot count and opcode scratch.

## Output contract

- 64 source-dependent 12-byte x64 slots, padded with NOPs.
- `.text` at RVA 0x1000, `.idata` at 0x2000, zero-backed tape at 0x3000.
- Tape base and end live in R12/R13; tape pointer in RBX.
- R14/R15 point to fixed WriteFile/ReadFile helpers. Both helpers have an aligned 48-byte Win64 call frame containing 32-byte shadow space, stack argument and transfer count.
- Each helper imports GetStdHandle and the relevant Win32 I/O API. WriteFile must report one byte written; ReadFile zeros the cell before reading, so EOF leaves zero. A Win32 failure or short write executes UD2.
- The final byte is 0 for a successful BF compilation or 1 for rejected input; reject artifacts are discarded by the transport adapter.

## Limitations

`[` and `]` remain unsupported; 64 executable-command ceiling; 1 MiB raw-source transport limit. Win32 helper behavior and Windows exception semantics require actual target execution. No PE relocation table is provided; ASLR/loader behavior remains a target gate. Output through redirected handles is the primary binary I/O acceptance environment; direct console encoding semantics have not been verified. Do not treat source-byte scan capacity as PE compiler capacity.
