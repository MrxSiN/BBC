# Iteration 56 engineering report — callable Twitter action policy

## Outcome

**A third original real-application Brainfuck policy now compiles into AArch64 callable code.** The existing two GmailHideAds policy source-to-image compilations are preserved. The first TwitterHideAds policy, `action.bf`, is 24,616 executable BF commands. Its 4,723 run-length records previously exceeded the bounded callable IR resolver's 4,096-record tape. A new **3,631-instruction standard-Brainfuck stream prepass** folds 452 exact `[-]` clear loops early, reducing the record stream to 3,819 records. The existing callable backend then emits a 15,300-byte ELF.

The new transformation is opt-in via `PolicyCompiler.compile(..., canonical_clears=True)`, and no source language operators or stage semantics are delegated to a non-Brainfuck compiler. The host remains byte transport. `tools/author_policy_clear56.py` is a source-authoring helper and does not participate in compilation runs.

## Source provenance and integrity

The fixture `tests/fixtures/real_apps/twitter_action_filtered.bf` is the original project's executable BF instruction stream, obtained from [MrxSiN/TwitterHideAds](https://github.com/MrxSiN/TwitterHideAds) at Git blob `7bf2eb045cace0fad460ad879bbc72f04c823df0`. Non-executable house-style comments are removed, leaving exactly 24,616 BF commands. SHA-256 of the effective stream: `a422986cc484115f489d1e8caec5adf439f06346e3c82a4f8e61a3c332e54d24`.

`experiments/policy_clear56.bf`: SHA-256 `069fd93964a2dc6081d6f3f92041b6d79808594a7cf7b5ae7d8d74eed15b8504`; 3,631 BF instructions. Its Linux-native BF ELF: 116,407 bytes, SHA-256 `3d886eb0c51252c13550292683888d02002127e0a79e28800512dc9a1dc44e0d`.

Twitter callable AArch64 ELF: 15,300 bytes, SHA-256 `09e5e737f8bdb4531f081577f8d2b8450ce5e5b71a8f55b1e0298d0316a575fc`.

## Executed verification

| Gate | Outcome |
|---|---|
| Native standard-BF prepass versus separate RLE oracle | 136 cases passed |
| Independent standard-BF interpreter versus prepass | 4 cases passed |
| Full original Twitter `action.bf` source-to-ELF | Passed: 15,300 bytes |
| Original Twitter BF source versus optimized IR execution | 10 framed requests matched |
| Independent AArch64 instruction-byte encoder | Image byte-identical |
| `readelf -h` and `readelf -l` | Passed |
| Original Gmail `row` and `scope` source-to-image | Byte-identical to archived device images, 2/2 |
| Original Gmail Iteration 55 valuefold variants | Byte-identical, 2/2 |
| Legacy policy IR regression | 120 cases passed |
| Legacy optional valuefold pass regression | 109 cases passed |
| Independent interpreter seed regression | 152 cases passed |
| Archived policy Linux-native stage parity | 3/3 passed |
| Android V1 compiler contract | Passed |
| Android archived native S2 offline audit | Passed, no new device run |
| Source-comment validation | Passed |
| Fresh Linux native compiler Stages 1 and 2 | Byte-identical; cold Stage 0 not rerun |
| Documentation consistency | 141 maintained Markdown files passed |
| New Twitter Android loader/JNI/APK execution | **Not performed** |

The combined legacy regression command timed out once after several completed checks. Its remaining checks were rerun separately and passed; that aggregate timeout itself is not a passed test.

## What this does not establish

The 15,300-byte ET_DYN file is a callable BF-kernel image, **not a loadable Android shared library with symbol exports**, and it was not integrated into the original Twitter APK. Ten source-versus-IR frame checks are not AArch64 device executions. The real JNI host protocol, output limits, budget behavior and performance remain target-side gates. The 4,096-record working-tape limit persists; Twitter's `discovery.bf` and `post.bf`, all ThreadsHideAds policies, and full 100M-codegen are outstanding. The saved Gmail Android parity and performance evidence was not rerun on-device.

## Next steps

Run the actual Twitter action kernel through JNI and the original app's parity tests. Then replace fixed callable IR tape storage with file-backed, BF-controlled dynamic records, preserving native-code decisions in Brainfuck. Proceed to the remaining Twitter/Threads original policy sources and realistic application-scale device tests.

## Reproducibility

Run `python tests/verify_policy_clear56.py`, `python tests/verify_policy_ir.py`, `python tests/verify_policy_transport.py`, `python tools/sync_status.py`, and `python tools/check_docs.py`. See [technical contract](ITERATION56_TWITTER_ACTION_CLEAR.md), [roadmap](ANDROID_APP_ROADMAP_ITERATION56.md), [evidence](../evidence/iteration56_policy_clear.json) and [Linux self-host proof](../evidence/iteration56_linux_selfhost.json).
