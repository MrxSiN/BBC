# policy_oneshot55 — Iteration 55 standard Brainfuck stage

This is an opt-in policy compiler stage. All compilation decisions are made inside the eight-instruction Brainfuck program, not by the Python authoring helper or transport. See [the implementation contract](../docs/ITERATION55_GMAIL_VALUEFOLD.md).

- Source SHA-256: `987622eb8b8124810ae1bf0960e91c10b77de47b72ba82d3ab845a7b82054ea8`
- Filtered instruction SHA-256: `eb53d17b2616f8cac27db3bab4179eb6efad172a32cc14c476618e4861eeb064`
- Standard BF instructions: **11638** (native input cap: 16,128)
- Linux-native stage ELF: `build/iteration55_linux/stages/policy_oneshot55.elf`
- Linux-native ELF SHA-256: `4f47bc8d950550c6d03e932d60fc6be5ffc2720c2d713ac38a85db9ede98a2ab`
- Verification: `python tests/verify_policy_valuefold.py`

Not Android-loader-tested or benchmarked on a device. The original unsuffixed policy stage is unchanged and retained for archived Android evidence.
