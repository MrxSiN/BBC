# 🗂️ Snapshot: Android native lowering

> Historical. How depth-512 nesting stopped breaking the Android build.

## 🐛 The bug

The depth-512 snapshot verified fine, but its native build declined. A probe
found it at live-interval construction: the pass reserved space for *every*
block/value pair, even though most needed none.

## 🛠️ The fix (XAX)

One expected-root transaction replaced that reservation with three-word linked
records, allocated as needed inside the existing arena.

- Capacity is checked by subtraction before the head moves.
- Exhaustion propagates immediately, and order, weights and links keep their meaning.
- Root `68ecf527…`. Compiler PE: 11,870,208 bytes.

## ✅ Checks

- 22 prepared Android snapshots → 44 native builds with byte-identical pairs.
- 47 real Pixel 8 Pro executions, matching the independent interpreter.
- All 20 previously working Android artifacts are unchanged.
- Zero-entry depth-512 prints `01`. Active depth-512 enters every loop and prints `03 02 01 00`.
- 388 allocator boundary and random cases, and 160 diagnostics, all exact.

The test sources are in [tests/compile](../tests/compile/README.md).

## 📝 Notes

- Build times here were diagnostic only; deep builds ran concurrently.
- The driver still declared 3,550,558,208 bytes of views. That was fixed later by
  [lazy views](25_NATIVE_COMPILE.md#-lazy-views).
- Next came the [alias index](24_XAX_BUILD_LATENCY.md), which made deep builds fast.

📎 [native_android_lowering.json](../evidence/native_android_lowering.json) · [Android hello smoke](../evidence/android_hello_smoke.json)
