# Android dynamic compiler roadmap — after Iteration 52

**Current verified state:** Native Linux executions of standard-BF compiler stages generate complete, dynamically sized, freestanding AArch64 ELF programs with all eight instructions, BF-owned loop pairing, 64-bit span arithmetic, signed branch relocation and BF-owned ELF metadata. The 55-program simulator suite passed 110 runs; a 296,307-command synthetic source produced a structurally valid ELF. No new Android device runs, original application policy compilation or JNI/DSO linkage occurred.

## Mandatory next gates

1. **Android loader evidence:** Run the nine-fixture Iteration 52 shell bundle on actual arm64 Android. Record process stdout bytes, status, execution failures, model/API, SELinux context and loader behavior. Revise the PIE layout if necessary.
2. **Unrestricted nested-loop reach:** Implement standard-BF-owned AArch64 far-branch islands or long-distance veneers and test both directions across signed imm26 boundaries. Preserve source scalability, atomic errors, and instruction-cache correctness.
3. **Original GmailHideAds policies:** Compile the actual `scope.bf` (18,192 commands) and `row.bf` (18,748 commands) from pinned Git revisions; demonstrate byte-for-byte parity with their reference policy logic, respecting 32-cell ABI, frame boundaries and request budgeting.
4. **TwitterHideAds and ThreadsHideAds:** Extend to the remaining nine original BF sources, including `ThreadsHideAds/nested.bf` (296,307 commands), not just same-sized synthetic fixtures; verify their 11 distinct program tapes, persistent state and multi-program host calls.
5. **Android shared-library integration:** Deliver JNI-compatible AArch64 `.so` entries, memory/buffer frame contracts, capability callbacks, program dispatch, safe ABI lifetime and Android NDK/Gradle integration. Build the three project APKs and run their original parity/instrumentation tests.
6. **Universal scaling and self-hosting:** Establish scalable native compiler source ingestion and 64-bit relocations for 100 million commands, independently verified on actual mixed input. Execute Stage 0, S1 and S2 on Android with byte-identical compiler images and document resource bounds; arbitrary 100M compilation is not a present claim.

**Core principle:** Native code/ELF decisions must be owned by the eight standard Brainfuck instructions. Python/C/host processes may provide generic filesystem and communication transports, never a substituted production code generator. Each completed stage needs reproducible evidence with its exact workload and execution environment.
