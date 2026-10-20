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
