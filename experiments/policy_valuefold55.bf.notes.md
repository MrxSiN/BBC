# policy_valuefold55 — Iteration 55 standard Brainfuck stage

This is an opt-in policy compiler stage. All compilation decisions are made inside the eight-instruction Brainfuck program, not by the Python authoring helper or transport. See [the implementation contract](../docs/ITERATION55_GMAIL_VALUEFOLD.md).

- Source SHA-256: `50e820aaab4079a272dcf6c6f09b5b4a7a0fa3da0bf8969e65cb032d79e2d51e`
- Filtered instruction SHA-256: `a73adf3bb369a83a5631be1e97ed3bf6de421f7f4d15089bbbe276bdd7144ede`
- Standard BF instructions: **4733** (native input cap: 16,128)
- Linux-native stage ELF: `build/iteration55_linux/stages/policy_valuefold55.elf`
- Linux-native ELF SHA-256: `8e571436e310fe6c9156923732a5ab67278bcd4ff53977014811e821e923ce12`
- Verification: `python tests/verify_policy_valuefold.py`

Not Android-loader-tested or benchmarked on a device. The original unsuffixed policy stage is unchanged and retained for archived Android evidence.
