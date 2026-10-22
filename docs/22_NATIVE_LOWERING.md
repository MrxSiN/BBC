# 🗂️ Snapshot: native lowering

> Historical. The native XAX driver learned enough to build every original BBC
> snapshot, from prepared stores rather than from source yet.

## 🛠️ What was added (XAX)

Windows pointer frame lowering, signed displacement checks, byte arithmetic
mod 256, and page probes for big stack frames. Three expected-root transactions;
final root `db44f3a8…`. Compiler PE: 11,866,112 bytes.

## ✅ Checks

- 24 pointer/bounds programs and 3 stack programs pass. The 8,192-addition
  stack program now returns 16392 instead of crashing.
- 786,432 counted byte operations, over all 65,536 operand pairs × 6 ops × 2 call routes.
- 48 earlier build controls and 160 semantic diagnostics stay exact.
- All 6 original prepared snapshots build twice identically and run correctly.
  The broader corpus passed 38 of 42.

| Still failing back then | Target | Result |
|---|---|---|
| deep-512 | Android | Verifies, but the build declines |
| deep-512 | Windows | `NATIVE-CALL-ARITY` [5,4] |
| right-edge, right-trap | Windows | Same call ABI rejection |

All four were fixed later: [Android lowering](23_ANDROID_NATIVE_LOWERING.md)
and the [x86-64 call elision](25_NATIVE_COMPILE.md#-native-backend-change).

## ⏱️ Measured

Prepared-store builds took 24.3–31.8 ms, excluding frontend, import and binding.
The driver committed about 3.31 GiB of memory, with 11.2–13.3 MiB resident.
That was later fixed by [lazy views](25_NATIVE_COMPILE.md#-lazy-views).

📎 [native_windows_lowering.json](../evidence/native_windows_lowering.json)
