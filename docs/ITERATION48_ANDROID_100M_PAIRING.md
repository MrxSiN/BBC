# Iteration 48 — 32-bit bracket pairing over a 100M-command source

## Implemented

Two independently executable standard Brainfuck stages: an opt-in framed 32-bit source scanner retaining the Iteration 47 byte protocol with one additional terminal separator, and a 32-bit stack pairing stage that returns matched loop start/end offsets. A host adapter moves opaque byte streams between stages and spools output atomically; it does not parse Brainfuck or compute loop matches. The authoritative Linux and Android compilers were not changed.

## Source compliance

The framed scanner contains 14,886 executable standard BF instructions; the pairing stage contains 2,017. Both were compiled using the existing Linux BF compiler, with comment-stripping parity verified. The 255-depth stack is explicit. No special source instruction or privileged compiler comment was introduced.

## Self-hosting

Fresh Linux-native Stage 1 and Stage 2 self-compilation reproduced the unchanged 475,703-byte ELF byte-for-byte. The independent cold Stage 0 bootstrap and Android-native self-compilation were not re-executed. The proof is included in the machine-readable evidence.

## Correctness

The focused suite passed 146 valid programs, rejected 27 invalid inputs, and reproduced 173 original-scanner outputs after removing only the new separator byte. Six seed-interpreter comparisons passed. A 100,000,002-byte actual raw source produced the single expected pair at offsets 0 and 100,000,001. Both 255-deep and 256-deep tests were executed. Host atomic-output preservation on rejected input passed.

## Memory safety

The stack is limited to 255 entries of five cells beginning at cell 32. It is not a formal proof of all input-dependent BF pointer paths. The generic transport caps raw bytes and emitted byte sizes. Incomplete framing beyond the accepted stage protocol is not claimed as fully robust; reject failure must not replace an existing output.

## Performance

A uniform 100-million-command byte source compresses to a small generic run record. That test proves count and matching arithmetic, not typical real-source throughput or native runtime speed. See machine-readable evidence for test execution duration. Native Android image generation remains limited to 2,719 commands.

## External dependencies

Python test and byte transport helpers, independent reference interpreters written in C, and the installed self-hosted Linux BF compiler. None performs production source instruction classification or pairing.

## Platforms

Linux-native BF stages: EXECUTED. Android AArch64 generated executables above 2,719 instructions: UNIMPLEMENTED. New Android-device execution and expanded S2: NOT RUN. Windows unchanged.

## Documentation and next priority

README, status matrix, Android capacity specification, handoff and roadmap are synchronized. Next implement BF-owned compact streamed IR, source-to-code address mapping, long-range AArch64 relocation and dynamic executable/DSO construction. The real GmailHideAds, TwitterHideAds and ThreadsHideAds policies and a 100M native program remain mandatory unpassed tests.

## Additional regression gates

The original 100-million-source scanner regression passed 152 differential cases and the real 100 MB raw-file test again. The eleven-policy acceptance manifest and source-comment compliance tests passed; the Android V1 transport contract passed its reference and negative cases. Documentation and local-link checking passed across 99 maintained Markdown files. No Android loader or new APK test was executed.
