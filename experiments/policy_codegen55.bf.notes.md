# policy_codegen55 — Iteration 55 standard Brainfuck stage

This is an opt-in policy compiler stage. All compilation decisions are made inside the eight-instruction Brainfuck program, not by the Python authoring helper or transport. See [the implementation contract](../docs/ITERATION55_GMAIL_VALUEFOLD.md).

- Source SHA-256: `e232a8650310839d9f51a60c24e4644ff0e54c7735c184772f28ed87920d6d7f`
- Filtered instruction SHA-256: `c65b084c681171401a48528eef3f5d14546638274859d4f2ca7cf09c7d4bdd3b`
- Standard BF instructions: **16078** (native input cap: 16,128)
- Linux-native stage ELF: `build/iteration55_linux/stages/policy_codegen55.elf`
- Linux-native ELF SHA-256: `d6b208dc9aed645f685b9ac1551a371e0ea089da6053cea0e105d0935c55c4cf`
- Verification: `python tests/verify_policy_valuefold.py`

Not Android-loader-tested or benchmarked on a device. The original unsuffixed policy stage is unchanged and retained for archived Android evidence.
