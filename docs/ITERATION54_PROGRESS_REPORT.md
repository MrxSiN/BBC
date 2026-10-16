# Iteration 54 engineering report

**Scope:** audit the user-provided Android device results and reproduce the
original Gmail policy compilation independently on Linux.

**New source:** `bootstrap/linux_policy_native.py` enables Linux policy stage
execution, `bootstrap/policy_seed_runs.c` accelerates only interpretation of
standard BF for cold verification, and the optional Linux backend in
`bootstrap/run_policy_native.py` leaves the Android-native path unchanged.

**Executed:** Both original Gmail `row.bf` and `scope.bf` recompiled through BF
stages into byte-identical AArch64 image bytes. Three Linux-native BF stages
match archived Android stage outputs, and the run-accelerated seed passes 152
independent interpreter comparisons. The ordinary original policy IR suite,
Android-device archive audit and source-comment tests also passed.

**Earlier Android evidence:** nine ELF loader passes, bounded S2, 21 GM APK
instrumentation executions, 634,229 Java-reference parity comparisons and
8,192 randomized kernel frame comparisons. No new device test was run here.

**Performance:** none of the BF-native Gmail benchmark performance claims are
improved by this work. The BF native path remains slower than the published
C/Java reference results in the archived evidence. Android platform runtime
and full original Twitter/Threads compilation remain separate open gates.

**Limits:** The cold interpreter is not a general native BF compiler; it only
executes the BF-owned policy compilation passes. Stage binaries reproduced by
the canonical Linux BF compiler are independent of the archived Android-stage
compiler, while archived AArch64 images are used only as acceptance oracles.

Evidence: `evidence/iteration54_linux_gm_policy_replay.json`,
`evidence/iteration54_linux_native_stage_parity.json`, and
`evidence/android_execution_20261014.json`.
