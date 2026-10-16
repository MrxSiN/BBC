# Iteration 55 — BF-owned constant stores in callable Gmail policies

## What changed

The optional `PolicyCompiler.compile(source, affine=True, valuefold=True)` path adds `experiments/policy_valuefold55.bf` after affine folding. This standard-Brainfuck stage tracks one proven constant cell while streaming seven-byte optimized IR records. After a direct zero store, a statically known addition or subtraction is turned into private IR kind `K` (write known nonzero byte) or `0` (write zero). Its tracking survives irrelevant pointer moves/reads and invalidates at branches, source-cell writes and unknown input. It only activates when the static tape-bound proof is present. `K` is not a ninth source instruction.

The separate `policy_oneshot55.bf` handles the new store kind during loop analysis; `policy_codegen55.bf` emits two AArch64 words for `K`: `MOVZ W9,#imm` then `STRB W9,[tape,#offset]`. The older arithmetic sequence used three words: load, add/subtract, store. A zero constant uses the existing single store-zero instruction. Bracket instruction spans are recalculated after IR word-cost changes.

This remains **Brainfuck-owned**: Python only arranges BF source at development time and transports opaque stage bytes. The old `policy_oneshot.bf`, `policy_codegen.bf`, Android-stored native policy images and their evidence hashes are unchanged. The flag is opt-in so original Android builds reproduce identically.

## Source-to-image results

| Original Gmail policy | Archived image | Optional valuefold image | New constant stores | Native bytes removed |
|---|---:|---:|---:|---:|
| `row.bf` | 13,064 | 12,772 | 73 | 292 |
| `scope.bf` | 13,168 | 12,964 | 51 | 204 |

The images are complete callable AArch64 ET_DYN files built from the original Git-pinned BF policies. They were generated on Linux by BF-executed compilation passes and checked against an independent AArch64 word encoder; there was **no Android native runtime or APK run for the new images**. A smaller ELF is not evidence of a faster kernel.

## Executed verification

- 109 compiler-IR differential programs, checking the Brainfuck-native pass against a separate Python IR oracle, plus the actual native ELF bytes against an independent instruction encoder.
- 480 completed original-Gmail policy IR executions compared byte-for-byte, including mutated framed inputs; no IR test timed out.
- Two independent BF interpreter runs agreeing with the Linux-native `policy_valuefold55` stage.
- Both original sources recompiled end-to-end with the opt-in stage, producing the recorded optimized image hashes.
- Both sources also recompiled without the flag, yielding the unchanged Android-accepted image hashes.
- Three new native Linux stage ELFs independently rebuilt byte-for-byte from their Brainfuck sources by the existing self-hosted compiler.
- A fresh Linux Stage 1→2 compiler replay was byte-identical; cold Stage 0 was not rerun.

See [source-to-image evidence](../evidence/iteration55_policy_valuefold.json), [execution oracle evidence](../evidence/iteration55_policy_semantics.json), and [Linux self-hosting replay](../evidence/iteration55_linux_selfhost.json).

## Limits and next steps

The callable policy compiler still has **4,096 RLE records**, 255 bracket nesting and 1 MiB raw-source limits. `policy_codegen55.bf` is 16,078 instructions and fits inside the present 16,128-instruction native compiler input ceiling by only 50 instructions; this is not a scalable final design.

The old Gmail app instrumentation (634,229 Java parity comparisons) is an archived pass for the **unmodified** kernels. These new images have *not* gone through new JNI/APK parity, target-side instrumentation or performance measurement. The previous Android measurement still shows substantial BF-kernel latency versus optimized C and Java.

Next: run the newly generated images in the Android GM test APK, repeat parity and randomized kernel checks, then benchmark against the same on-device C baseline. Improve value propagation and state dispatch only when that evidence identifies a real hotspot. In parallel, expand the callable record store for TwitterHideAds and ThreadsHideAds; the target remains resource-scaled compilation and eventually 100M commands per source unit, not a fixed small cap.

### Reproduce

```sh
python tools/author_policy_valuefold.py
python tools/author_policy_variant55.py
python tests/verify_policy_valuefold.py
python tests/verify_policy_valuefold_semantics.py --quick   # fast smoke; full 480 case replay omits --quick
python tests/verify_policy_ir.py
python tests/verify_policy_transport.py
python tools/audit_android_20261014.py
python tools/sync_status.py
python tools/check_docs.py
```
