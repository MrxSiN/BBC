# Native driver diagnostic and coverage follow-up

> Format migration note: measurements and source identities below describe their
> pinned pre-migration snapshots. Historical version names identify that evidence,
> not current decoder modes. Current production uses only [BFX](02_BFX_CONTRACT.md).
> No migration performance or broader completion claim follows from these reports.


The canonical Windows XAX driver now resolves its known type-diagnostic
mismatch. This is backend correctness work toward the native compiler path;
it establishes no new build-time, RAM or competitor score. M4 remains incomplete
and M8 is **NOT YET ACHIEVED**.

[Execution evidence](../evidence/windows_native_driver_followup.json) preserves
the exact sources, transaction, artifacts, native authority and checks. Earlier
reports remain immutable. The current
[XAX source](https://github.com/MrxSiN/XAX/blob/6c9ed73474307d4b3f6130dd09a16431b0f8046d/compiler/integration/windows_helpers/driver.xax)
and [rebuild guide](https://github.com/MrxSiN/XAX/blob/6c9ed73474307d4b3f6130dd09a16431b0f8046d/compiler/integration/windows_helpers/DRIVER.md)
contain the implementation and its limits.

## Corrected diagnostic

In `semantic-43-function_byte`, an object of kind GRAPH_FRAGMENT is read as a
bits type. The previous native renderer reported trailing body bytes before
the required kind check. The canonical guard now reports the reference
`XAX.TYPE.EXPECTED / TYPE-BITS`, with expected TYPE and actual GRAPH_FRAGMENT.

The 16,756-byte expected-root transaction supplies two new semantic objects,
binds the renderer and preserves its existing fallback. Full verification and
`Workspace.save` establish the resulting store; a stale replay rejects. The
driver has 509 functions. No generic Python compiler source changes.

The native helper passes 110 checks across all eleven object kinds, five first
bytes and two copied lengths. The native driver separately passes the existing
160-case seeded semantic corpus: 63 accepts, 97 rejects, zero declines and
exact complete diagnostic equality, including dependencies and repair
neighborhood. These are correctness checks, not timed trials. The full original
212-case corpus was not rerun; its four malformed declines remain open.

Native controls retain correct BBC frontend/v4-importer verification, binary
container rejection, exact small-edit replay, stale-root rejection and PE
smoke build/execution. The v5 packed Mandelbrot store verifies successfully;
the transparent store still declines.

## Rebuild and self-store diagnosis

A second independent bootstrap rebuild of the original 508-function driver
reproduces its 11,857,408-byte PE exactly, SHA-256
`e2b730647e5005321166513c68c51223b7e8b4ee78222197f99dcf2725016d43`.
This is an independent bootstrap rebuild, not native self-compilation.

The corrected PE is 11,864,576 bytes, SHA-256
`ff0355c5bf148bc79cf463748a285c3f982b6c8e47faf8d2d25bd3571b2ad638`.
Its unchanged SDK bootstrap uses the existing same-process function-fragment
API, retaining 507 exact immutable functions and freshly compiling the changed
entry and guard after full verification. These diagnostic build durations are
unscored; fragment reuse is not a cold-build performance result.

All 508 original graph bodies decode successfully through the native decoder.
Their audited CFG inputs and outputs fit the existing views; the object-table
word count also fits. The largest body is 1,884,002 bytes, below 2 MiB. A private
canonical probe locates the original self-store decline at resource-callee
action 2. That identifies a stage; the underlying graph outcome remains under
investigation. Increasing capacities without identifying the cause is not a
validated fix.

The separate [resource diagnosis](../evidence/windows_native_resource_diagnosis.json)
now identifies the corrected self-store's entry graph as that declined graph:
2,149 blocks, 37,533 nodes, 112 direct calls to 37 targets and a zero deferred
callee token. Its graph is
`85a20ba4e71d38112f4a59ec76ede95cab3810090495a8580b11acc98205aaa6`.
The precise node/facts reason remains undiagnosed. Private canonical diagnostic
records preserve the state capture; their exits are not production CLI statuses.

Five small normal-driver controls isolate a separate resource-call coverage
limit. One callee and two calls to the same callee accept; a valid 1,919-byte
store calling two distinct identity callees declines. A malformed second callee
rejects with the exact full reference diagnostic. A verified 138-byte fixture
transaction rebinds the second call to the first callee, making verification
succeed while retaining both functions in the module. This is a diagnostic
control, not a production optimization. The small fixture shares the resource
decision stage with the self-store; a common underlying cause is not established.

The corrected driver still declines its own store. Native self-verification,
the large flag transaction, Windows DLL packaging, common helper-loader
migration and a complete native BBC build remain outstanding. The declared
3,550,558,208 bytes of driver views are allocation budgets, not measured RAM.
No new Android compiler-host execution or competitive timing is claimed.

The [measurement plan](06_PERFORMANCE_PLAN.md) still governs promotion. The
[cold-build cache experiment](18_BACKEND_BUILD_CACHE.md) remains a separate
configuration with negligible measured full-build gains.
