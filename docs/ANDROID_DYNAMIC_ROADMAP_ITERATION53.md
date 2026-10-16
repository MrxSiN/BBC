# Dynamic Android compiler roadmap — after Iteration 53

**Current gate:** BF-owned, PC-relative, signed 64-bit indirect branches eliminate the *direct branch encoding* constraint in the opt-in full-ELF pipeline. Small ELFs are AArch64-simulated; the 296,307-command synthetic ELF is `readelf`-validated only. The original Android app policies, real Android loader execution, JNI/DSO and 100M executable compilation remain unverified.

1. **Real Android loader:** Execute `build/android53_acceptance/run_android53.sh` on Android arm64 and capture hashes, stdout, status codes, kernel/API, loader and security context. Fix any loader defect before calling these images device-ready.
2. **Real upstream BF policies:** Pin exact Git commits, fetch and checksum the original `brainfuck/src` files for GmailHideAds (`scope.bf`, `row.bf`), TwitterHideAds (three files), and ThreadsHideAds (six files). Compile all eleven through the new path and check frame-level parity, pointer bounds and output resource policies. A same-sized synthetic file is not acceptance.
3. **JNI library ABI:** Freestanding command-line PIE output is not a JNI-loaded `.so`. Design BF-owned ET_DYN shared-library exports and a host bridge for callbacks, tape persistence, frame limits, capability I/O and reentrant execution; keep Android/Xposed mechanisms in Java/native host components.
4. **Real long reach:** Exercise one large ELF with an actual loop jump beyond ±128 MiB, and verify that no literal is executed as instructions. Test independent loads, far reverse jumps and failure limits.
5. **Mixed-size scaling:** Performance- and memory-profile 1M, 10M, and 100M mixed BF instructions, pathological nesting, and large bracket counts. Establish resource-relative failures and dynamic output growth rather than a hard source maximum.
6. **Native self-hosting:** After large real-policy parity and library acceptance, perform cold Android native compiler Stage 0 through Stage 2 under the larger protocol, with byte-identical outputs and on-device evidence.

Source generator logic remains strictly standard `><+-.,[]` Brainfuck; helper Python scripts may only author source or provide generic opaque byte/file transport, never replace BF native-code decisions.
