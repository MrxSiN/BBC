# Iteration 56 — BF-owned early clear canonicalization and Twitter action policy

## Engineering change

The existing callable Android policy compiler has a 4,096-record working-tape ceiling. An original 24,616-command TwitterHideAds policy, `brainfuck/src/action.bf`, contains 4,723 ordinary run-length records, so its unmodified input cannot enter the record resolver. This iteration adds an **optional, streaming standard-Brainfuck prepass**, `experiments/policy_clear56.bf`, between `policy_rle` and `policy_resolve`.

The prepass looks ahead at three opaque `(opcode, run count)` records and replaces exactly `[` (count 0), `-` (count 1), `]` (count 0) with one private `0` (count 0) record. The BF source operator set remains **exactly eight commands**. The private `0` denotes the existing single-word zero-store IR opcode, not new syntax. For wrapping 8-bit cells, this transformation has the same effect as `[-]` and does not move the pointer or change I/O behavior. All other records are emitted unchanged, including nested, nontrivial loops.

`tools/author_policy_clear56.py` constructs the standard-BF source at development time only. Its output contains **3,631 executable BF commands**. At compilation time, the BF stage itself recognizes the pattern, preserves unmatched RLE records, and emits the transformed stream. The Python adapter `PolicyCompiler.compile(..., canonical_clears=True)` only selects that stage and transports its bytes. The default path is unchanged.

This **does not remove the 4,096-record limit**. It enables sources whose RLE stream can safely shrink below it. The wider scalable, file-backed callable IR and nested-loop architecture remain outstanding.

## Verified original application workload

| Field | Result |
|---|---|
| Upstream | [MrxSiN/TwitterHideAds](https://github.com/MrxSiN/TwitterHideAds), `brainfuck/src/action.bf` |
| Original Git blob | `7bf2eb045cace0fad460ad879bbc72f04c823df0` |
| Saved fixture | `tests/fixtures/real_apps/twitter_action_filtered.bf` (only original eight executable BF characters; comments removed) |
| Effective BF commands | 24,616 |
| Original RLE records | 4,723 |
| Canonicalized RLE records | **3,819** |
| Collapsed clear loops | **452** |
| New source-to-image result | **15,300-byte AArch64 ET_DYN callable ELF** |
| ELF SHA-256 | `09e5e737f8bdb4531f081577f8d2b8450ce5e5b71a8f55b1e0298d0316a575fc` |
| Independent AArch64 machine-byte oracle | **Exact match** |
| `readelf` header/program-header acceptance | Passed |
| Original BF interpreter versus optimized IR frame responses | **10/10 equal** |
| Linux-native BF prepass differential tests | **136 passed** |
| Independent BF interpreter prepass checks | **4 matched** |

The Twitter policy was compiled as a **callable code image**, not linked into the TwitterHideAds APK. It was **not executed on Android**, and its generated AArch64 instructions were **not executed on a physical AArch64 CPU in this iteration**. IR execution and byte-for-byte machine-code encoding validation must not be misrepresented as native runtime tests.

Both original GmailHideAds policies were recompiled from their archived unfiltered source with the opt-in prepass and produced the exact same Android-accepted baseline images. Both also reproduced the Iteration 55 valuefold images byte-for-byte. This establishes opt-in compatibility with the earlier two-policy milestone.

## Remaining gates

1. Execute the Twitter `action` callable image on Android with its actual JNI runtime and reference parity suite, including binary request framing, output buffer limits, budgets and error status.
2. Extend source-to-image compilation to the original Twitter `discovery` and `post` policies. Their record counts remain above 4,096 even after simple clear canonicalization.
3. Replace the 15-cell-per-record fixed compiler tape layout with resource-managed storage so all original ThreadsHideAds policies, then large diverse sources, can compile without arbitrary record counts.
4. Preserve Brainfuck-owned parsing, semantic optimization, code emission and relocation; add real native-app tests, performance profiling, and eventually the 100-million-command full compilation target.

## Reproduce

```bash
python tools/author_policy_clear56.py
python tests/verify_policy_clear56.py
python tools/sync_status.py
python tools/check_docs.py
```

The source fixture was extracted from the original GitHub program without altering its Brainfuck commands; the upstream noninstruction comments were not copied. See [the evidence record](../evidence/iteration56_policy_clear.json) for hashes and classifications.
