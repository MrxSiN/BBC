# Android real-application priority — Iteration 46

**Iteration 46 escalation (planning, not implementation):** All eleven Android policies remain mandatory, but 300,000 filtered commands is now only a *minimum compatibility checkpoint*. The product-level gate requires native compilation of every original BF program, per-app tape/host-protocol parity, JNI-loadable shared libraries and installable tested GmailHideAds, TwitterHideAds and ThreadsHideAds APKs. The larger-app stretch goal is >=10M commands per source and >=100M aggregate. See [Android acceptance contract](ANDROID_APPLICATION_ACCEPTANCE.md) and [machine gates](../status/ANDROID_APPLICATION_GATES.json).

---

# Mandatory external application workload audit

**Scope note (2026-10-13):** The [Android-first roadmap](IMPLEMENTATION_ROADMAP.md) proposes a **300,000-command** input acceptance test to remove the measured source-size barrier for the eleven audited Android BF policy files. This is a **future target**, not supported today; passing it would not automatically satisfy host ABI, semantic-profile or whole-APK requirements. See [PLATFORM_ACCEPTANCE.md](PLATFORM_ACCEPTANCE.md).

The four specified GitHub repositories are mandatory acceptance targets. This
report is a **source compatibility audit**, not a claim that the applications
build, that the Brainfuck policies execute, or that native code is faster.

The input evidence was retrieved through GitHub on 2026-10-12. The revision
and per-file Git blob identities, file sizes, and observed Brainfuck instruction
counts are recorded in [`../status/TARGET_WORKLOADS.json`](../status/TARGET_WORKLOADS.json).
The checkout need not use the latest branches: reproducible acceptance will
use pinned commits. No upstream code is bundled in this repository.

## Command capacity is the first blocker

| Project | BF program | Commands (filtered) | Current 16,128-command compiler |
|---|---|---:|---|
| GmailHideAds | `row.bf` | 18,748 | exceeds |
| GmailHideAds | `scope.bf` | 18,192 | exceeds |
| TwitterHideAds | `post.bf` | 108,565 | exceeds |
| TwitterHideAds | `action.bf` | 24,616 | exceeds |
| TwitterHideAds | `discovery.bf` | 55,770 | exceeds |
| ThreadsHideAds | `core.bf` | 151,449 | exceeds |
| ThreadsHideAds | `text.bf` | 225,546 | exceeds |
| ThreadsHideAds | `detect.bf` | 231,216 | exceeds |
| ThreadsHideAds | `sanitize.bf` | 69,343 | exceeds |
| ThreadsHideAds | `nested.bf` | 296,307 | exceeds |
| ThreadsHideAds | `pando.bf` | 113,160 | exceeds |
| logitech-g29-standalone-driver | `g29-main.bf` | unknown; 19,479,574 raw bytes | not evaluated directly |

All eleven fetched Android-policy programs have balanced brackets. This
proves only bracket structure in the fetched content; semantic execution,
compilation, memory capacity, platform loader support, and parity remain
unverified. The G29 source was too large to retrieve through the available
GitHub connector and only its source size was checked from repository metadata.

A filtered command count is not necessarily a generated machine-code size:
the current 32-byte-slot emitter is bounded to 16,128 commands, and any
larger program must be rejected, not silently truncated.

## Execution profiles and entire-application builds

- GmailHideAds, TwitterHideAds and ThreadsHideAds are Android Xposed modules.
  Their **Brainfuck decision-policy programs** are eligible compilation
  targets once large-source support, target execution, tape semantics, I/O
  frame compatibility, and native-to-host ABI have been validated. The Java,
  JNI, Gradle and Android/Xposed host parts are not Brainfuck source. A
  Brainfuck-to-native compiler alone cannot turn them into complete APKs.
- The G29 source is an actual Brainfuck program, but its documented execution
  contract uses **signed 32-bit cells with checked overflow**, a **131,072-cell
  tape**, bounded loop iterations, and a framed host protocol. The current V0
  compiler has unsigned wrapping 8-bit cells, a 65,536-cell tape and a
  different EOF policy. Running its output under V0 is not equivalent. A
  separately versioned compiler execution profile is required; this must not
  silently change V0 or the eight-instruction language. Its C/native Windows
  bridge, HID/DirectInput support, driver service, and packaging are separate
  external targets.
- GmailHideAds additionally ships a **different BF-implemented BF-to-C
  compiler**, `bfcc.bf`, approximately 5.84 MB, with its own BFL-generated
  authoring source and host device protocol. It is an important comparison
  implementation, not proof our native compiler can replace that pipeline.

Full product builds using no Java/C/C#/build system are not expressible by
unmodified Brainfuck with byte I/O alone. The acceptance definition separates
native compilation of every policy BF program from native application bridge
and packaging integration. None has passed yet.

## Reproduce the audit

```sh
python3 tests/verify_target_workloads.py
python3 tools/audit_target_workloads.py --output /tmp/bf-workload-audit.json
python3 tools/audit_target_workloads.py --root /path/to/four-clones
```

For the `--root` variant, directory names must match the four GitHub repository
names. Git object hashes and source command counts are checked against the
captured audit, so branch drift triggers a failure. Local G29 source can then
be scanned for a command count and balanced brackets without being compiled.

## Acceptance steps — not completed

1. Accept large sources without an externally imposed 16,128-command ceiling;
   use independently verified bounded memory and deterministic overflow errors.
2. Test each source under a **matching semantic and host-protocol profile**.
   Record expected input/output fixtures from each original project's tests.
3. Generate native Android AArch64 and Windows x86-64 artifacts entirely from
   Brainfuck compiler logic, with platform ABIs and loader requirements.
4. Exercise the emitted policy artifacts against the original projects'
   parity suites and actual native target devices or VMs.
5. Build and test the original application bridges with their required
   platform toolchains. Report this separately from Brainfuck-only compilation.
6. Compare like-for-like policy kernels against each project's existing AOT
   compiler and optimized C/Rust equivalents, with raw timing and environment
   evidence; do not claim the 0.9999x ratio before it is measured.

The next engineering blocker is large-source **native compiler capacity**;
this is more urgent for these specific workloads than the Android `+-.><,`
prototype's current feature count.
