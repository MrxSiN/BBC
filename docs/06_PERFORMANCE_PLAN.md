# 🎯 Measurement plan

> How BBC is allowed to claim it beat someone. Short version: with receipts.

Results live in [benchmarks](08_BENCHMARKS.md). This page is the rulebook.
**Status: no competitor beaten yet.** The [latest run](08_BENCHMARKS.md) shows
where BBC stands.

---

## 🧪 What gets measured

Each of these is measured separately, and never mixed:

- ⏱️ **Build time**: source in, runnable executable out, fresh process.
- 🏃 **Run time**: the whole program process, including startup.
- 🔁 **Warm calls**: repeated decision calls, including the tape reset.
- 🧠 **Memory**: compiler RAM and program RAM. Resident is not the same as committed.
- 📦 **Size**: complete executable bytes. Module and host bytes are kept separate.
- 🔋 **Energy**: not measured until controlled device measurements exist.

---

## 📋 Fair-play rules

- 🧊 Freeze sources, inputs, expected outputs, holdouts and exclusions **before** tuning.
- ✅ Check every output and status before trusting a timing.
- 🧮 Use paired, counterbalanced order, warmups and several independent runs.
  Report medians and spread.
- 🧾 Keep raw samples, hashes, tool versions and hosts. Keep the runner outside
  both repositories and pin it.
- 🚫 Never change an algorithm, drop a workload or hide an exclusion to improve a score.
- 🧷 Don't multiply ratios from different runs. Don't call a frontend-only gain a
  full-pipeline win.
- 🏷️ Label JIT, interpreter and VM results as what they are.

Each competitor's semantics (wrapping, tape size, EOF, bounds) are checked
first. Only programs every arm runs identically are timed.

---

## 🏆 What "beating" a competitor means

A **per-competitor win** needs all of:

- Run time and full build time both faster on geometric mean, with statistical support.
- No category slower by more than 10%.
- Compiler RAM, program RAM and executable size each at least as good on geometric mean.
- At least ten comparable workloads across two categories. Otherwise: **insufficient coverage**.

A **target sweep** needs every eligible competitor beaten on both Android and
Windows, separately. Stretch goals are 1.20× run time and 1.10× build/resources.
Missing data never passes.

A general claim also needs 20 real workloads per target, including three real
decision modules called from a real XAX app.

---

## 🔬 For each optimization

Record a falsifiable hypothesis, the proof, tape and work budgets, adversarial
tests, self-hosting, and a same-machine A/B. Keep it only with a net benefit.
Report the rejected ones too.

---

## 🧭 Next priorities

1. **Lowering.** It is now the biggest build cost (about 40% of driver time on
   small programs, most of it on big ones).
2. **Generated code quality.** The [latest run](08_BENCHMARKS.md) shows BBC's
   executables are far slower on compute-heavy programs.
3. **Semantic loop optimizations.** Affine transfer, scans and general odd-step
   clears, each with a full equivalence proof.
4. **Device runs.** New artifacts need execution on a real Pixel and Windows.
5. **Android off-main-thread worker** for programs that may not terminate.
   XAX has callback and pthread contracts; that alone does not prove the integration.
