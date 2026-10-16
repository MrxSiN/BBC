# Android application roadmap after Iteration 56

**Executed progress:** A Brainfuck-native canonical-clear prepass reduces TwitterHideAds `action.bf` from 4,723 to 3,819 IR records and permits an actual **15,300-byte AArch64 callable image** to be compiled end-to-end. Its machine bytes match the independent encoder, and ten original-BF versus optimized-IR frame comparisons pass. The previous Gmail policy images remain byte-identical with the prepass enabled. [Technical contract](ITERATION56_TWITTER_ACTION_CLEAR.md).

**This is not universal dynamic compilation.** The resolver still has a 4,096-record tape layout, brackets still have a 255-level bound, and the callable path's raw input remains bounded. Twitter's other policies and all six Threads policies still need compilation; no Twitter APK/JNI run or new Android-device test occurred here. The 100-million-command native compilation goal is unachieved.

## Next gates

1. Android-native execution and ABI parity of the original Twitter `action.bf` image, including all exact, suffix and fail-open decision cases, time budget, output limits and JNI call framing.
2. Genuine scalable callable IR storage: file-backed records and pointer/loop metadata with BF-owned semantics; removal of arbitrary 4,096-record and 255-level limits. Do not hide larger fixed arrays behind a new capacity number.
3. Original `discovery.bf` and `post.bf`, then six ThreadsHideAds policies. Include per-application tape, persistence, capability callbacks and correct host contract.
4. `lib*.so` export/link integration, instrumented APK parity and measurable native performance comparisons on the same Android device.
5. Large mixed-source stress and resource-exhaustion testing, scaling to the 100-million-command target per compilation unit. Keep memory/file/time consumption and 64-bit relocation correctness in the evidence.

The verified Gmail APK parity (634,229 comparisons) is historical evidence for the archived Gmail build, not proof for the new Twitter image. Linux and Windows source/status must remain unchanged while this Android track advances.
