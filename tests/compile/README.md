# Public compilation regressions

Each `.request` is exact `source_length:u32le || binary source || 01` data for
the [unified interface](../../docs/21_UNIFIED_COMPILATION.md), at source/work
offset 65,531. Supply actual frame length at offset 0 and level at offset 4.
`cases.json` records expected scalar status at O0 and O1. Failed calls return
zero record length; never publish their provisional record buffers.

The two overflow cases require capacity status 3 even when a bracket error
occurs before instruction overflow. The two exact-capacity cases require
bracket status 2. These are permanent regressions for the coordinator's
cross-chunk error precedence. The empty/binary cases require exact valid BFX.
Existing tests/bfx requests remain private bounded bootstrap/reference fixtures.
External test transports remain outside BBC.

The two `deep_nesting_512` cases also provide exact `.bf` source and expected
O1 `.bfx` records. The zero-entry source emits hex `01`. The active source enters
all 512 nested loops, repeats its inner body three times and emits `03 02 01 00`.
Both framed requests pass the unchanged native frontend at O0/O1. Their Android
snapshots build twice identically and execute on Pixel 8 Pro; see
[the Android evidence guide](../../docs/23_ANDROID_NATIVE_LOWERING.md).
O0 preserves primitives and can differ from the supplied O1 record while using
the same BFX format. The six earlier framing regressions remain unchanged.
