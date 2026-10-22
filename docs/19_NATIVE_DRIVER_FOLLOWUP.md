# 🗂️ Snapshot: native driver fixes

> Historical. Correctness work on the Windows-native XAX driver before it could
> build BBC programs by itself. Timings here are unscored.

---

## 🩹 Diagnostic fix

In `semantic-43-function_byte`, a GRAPH_FRAGMENT read as a bits type was reported
as "trailing bytes" before the kind check ran. A canonical guard now reports the
reference `XAX.TYPE.EXPECTED / TYPE-BITS` first.

- One 16,756-byte expected-root transaction. Stale replay is rejected.
- 110 helper checks pass.
- The 160-case semantic corpus matches exactly: 63 accepts, 97 rejects, 0 declines.

📎 [windows_native_driver_followup.json](../evidence/windows_native_driver_followup.json)

---

## 🔎 Self-store decline

- A second independent bootstrap reproduced the 508-function driver PE byte for byte.
- All 508 graph bodies decode natively and fit their views.
- The driver still declined its *own* store. A probe pinned that to
  resource-callee action 2 in its 2,149-block entry graph, with a zero deferred-callee token.
- A tiny 1,919-byte store calling two different callees also declined: a
  separate coverage gap. A common cause was never established.

📎 [resource diagnosis](../evidence/windows_native_resource_diagnosis.json)

---

## ➕ One-bit AND/OR/XOR

The frame fallback learned `bits1` AND, OR and XOR.

- 48 build controls and 160 verifier cases keep their exact bytes.
- 3 of 6 prepared BBC snapshots then built and ran.

📎 [native_bits1.json](../evidence/native_bits1.json)

---

## ➡️ What came next

- [Native lowering](22_NATIVE_LOWERING.md): all six original snapshots build.
- [Android lowering](23_ANDROID_NATIVE_LOWERING.md): depth-512 builds.
- [Native compile](25_NATIVE_COMPILE.md): the complete Python-free pipeline.
