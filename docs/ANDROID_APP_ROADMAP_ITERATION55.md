# Android application roadmap after Iteration 55

GmailHideAds original BF policy compilation works on Android in the archived Iteration 54 device test. A fresh Linux-executed BF optimization now produces shorter new Gmail policy images, but it is **not Android performance evidence**. Read the [Iteration 55 implementation contract](ITERATION55_GMAIL_VALUEFOLD.md).

## Next acceptance gates

1. **Run the optional new Gmail images on Android**, including the same 634,229-case Java parity suite and checked randomized frames. Measure kernel-only latency with unchanged CPU/thermal disclosures. Keep the archive accepted results as the baseline, not as results of the new image.
2. **Scale callable IR beyond 4,096 records**, without replacing BF-owned code-generation decisions with host Python or native C. The original TwitterHideAds `action.bf` already needs more records than this after ordinary RLE.
3. **Compile and integrate the other nine original BF policies**, first TwitterHideAds and then ThreadsHideAds, preserving their JNI/capability protocol and persistent state requirements. A standalone ELF does not complete an Android module.
4. **Remove bounded nesting and source transport limits**, moving callable compilation to file-backed resource-managed IR and ELF construction. Keep branch relocation and bounds checks BF-owned.
5. **Qualify 100-million-command compilation** using large, varied inputs. Scanning 100M and matching a 100M-span loop were achieved in isolated stages; a runnable 100M-command native app is not verified.

Linux S2, recorded Android native S2 and the Windows experimental PE artifacts must remain regression-stable. The original 11-policy workloads and APKs, not synthetic command counts alone, are required gates.
