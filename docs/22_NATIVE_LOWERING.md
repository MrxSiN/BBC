# Native lowering and remaining Android coverage

## Implemented scope

The [execution report](../evidence/native_windows_lowering.json) records a
verified native XAX backend extension. BBC's twelve Brainfuck instruction
streams and its single BFX wire contract are unchanged. Production changes
live in the separate XAX repository as canonical graphs and three ordered,
expected-root transactions. No Python SDK or builder implementation was changed
by these transactions.

The [tested XAX source](https://github.com/MrxSiN/XAX/blob/e2681460a35ac6c4593faccd8e7d741c08e606f5/compiler/integration/windows_helpers/DRIVER.md)
adds Windows pointer frame lowering, signed displacement validation, modulo-256
byte arithmetic and page probes for large Windows stack frames. The final root
is `db44f3a8cdc955cf264aec7f4eabed549bca1bcc5bcb5d0685c6a1ee4b658e18`.
The 11,866,112-byte compiler PE has SHA-256
`23d0b374b3701f011e7ad3aa7f5169085b237c2078db603aab8376591c914f1c`.
Bounds, ABI and semantic verification requirements remain mandatory.

Bootstrap used unchanged generic SDK revision `1c211da`. Its same-process
ProofCache and exact SDK-produced function fragments are external bootstrap
setup, not a fresh-process compiler speedup. Three private helpers also rebuild
byte-identically under upstream `2e1af7c`; that is not a whole-driver rebuild.

## Executed evidence

- Twenty-four pointer/bounds programs and three stack programs pass. The former
  8,192-addition stack program now returns 16392 instead of an access violation.
- Counted byte grids check all 65,536 operand pairs for each of six operations
  on two call routes: 786,432 route executions. The second route forces actual
  non-inline calls. All results and exact iteration counts pass.
- Forty-eight earlier build controls pass; four byte-width cases now accept.
  The other 44 expectations retain exact bytes. Six additional unsupported
  operations retain exact diagnostics. All 160 semantic diagnostic cases agree.
- Private native helper checks pass 240 displacement, 20 stack-prologue and
  24 byte-store cases. Their DLL bootstrap does not implement driver DLL packaging.
- All six original prepared BBC snapshots build twice identically and execute
  correctly on Windows or the Pixel 8 Pro. A broader 42-target corpus passes
  38 cases, including successful large-source, transfer, scan and bounds cases.
  These source constructs execute through existing O1 instructions; this does
  not establish new affine-transfer or scan optimizations.

The four broader failures remain visible:

| Prepared case | Target | Native result |
|---|---|---|
| deep-512 | Android ARM64 | Verification succeeds; build declines with exit 2 |
| deep-512 | Windows x86-64 | Build rejects NATIVE-CALL-ARITY, actual [5,4] |
| right-edge | Windows x86-64 | Same call ABI rejection |
| right-trap | Windows x86-64 | Same call ABI rejection |

The public BBC command store also verifies but reaches that Windows ABI gate.
Android native build coverage is the next priority. Self-store/resource-callee
coverage, shared libraries, common helper loading and the complete Python-free
source-to-native workflow remain INCOMPLETE. These results do not establish
new three-generation native compiler self-builds.

## Measured boundary

Fresh-process native builds of six **prepared snapshots** have medians
24.25–31.83 ms, with one warmup and nine scored observations per case. Source
compilation, BFX import, binding and snapshot preparation are excluded. This
exploratory boundary has no competitor verdict and does not replace the
[full-build baseline](20_MODERNIZATION.md).

Separate OS-counter runs sample about 3.31 GiB peak private commit and
11.2–13.3 MiB peak resident memory. The large committed allocation is an
unresolved cost, despite the small resident sample. These are driver process
measurements, not complete process-tree RAM, and the fixed arenas do not grow
dynamically. Raw samples and limitations are preserved in the report.

The old full-source baseline remains approximately 1.46–1.58 seconds for BBC
versus 23–24 ms for pinned Brainfry. No new full-source build, sustained runtime
or compiler-RAM competitive score exists. M4 is incomplete and M8 is not achieved.

Next work is to locate the Android deep-nesting decline, extend verified native
Android build coverage, then reduce graph/build allocation costs. Windows ABI
and packaging work remain necessary but are secondary to Android platform work.
