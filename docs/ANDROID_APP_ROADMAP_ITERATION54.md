# Android-native compiler roadmap after the Gmail device checkpoint

## Verified now

The freestanding dynamic ELF loader passes real Android tests (nine fixtures).
Android bounded native compiler S2 remains verified by the recorded device
artifacts. GmailHideAds `row.bf` and `scope.bf` are both built by the
standard-Brainfuck native policy stages, embedded in a real test APK, and
validated against the original application's Java policy oracle. Iteration 54
adds **independent Linux byte-identical reproduction** for both images.

## Work needed in priority order

1. **Performance:** benchmark instruction-level hotspots in the BF-generated
   native Gmail kernels and implement an actual BF-owned code-generation
   improvement, with parity against all archived frames and fresh on-device
   measurements. The BF kernels remain much slower than optimized C.
2. **Real-application breadth:** compile TwitterHideAds `action.bf`, then its
   `post.bf` and `discovery.bf`, followed by all six ThreadsHideAds policies.
   These applications have distinct JNI/host APIs; a bare ELF is insufficient.
3. **Capacity and dynamism:** remove the callable route's 4,096-record and
   255-bracket constraints and integrate dynamically growing source, tape and
   ELF layout into the actual callable library path, with controlled resource
   failures.
4. **Integration:** build real ABI-stable AArch64 shared libraries, run each
   app's parity suite and instrumentation under a genuine device loader,
   then verify actual Xposed hook operation in separate authorized tests.
5. **Resource-scaled stress:** demonstrate correctness and practical memory,
   disk and compilation-time behavior for sources growing toward 100 million
   BF commands per compilation unit, including long loops, then verify
   target-side self-hosting for that backend.

No unfinished milestone is classified as achieved merely because a source
scanner handles a larger number or a synthetic ELF is structurally valid.
