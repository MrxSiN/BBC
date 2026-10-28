# 🔗 XAX integration

> BBC writes Brainfuck. XAX turns it into machine code. This page is the handshake.

Everything here lives in the separate [XAX repository](https://github.com/MrxSiN/XAX/tree/40caaf7069bcee1a46165388dbe2548e329721c7/compiler/integration/bfx)
as canonical semantic graphs, changed only through verified expected-root
transactions. The [BFX spec](02_BFX_CONTRACT.md) is the contract between the two.

---

## 🧩 Who does what

| Piece | Lives in | Job |
|---|---|---|
| `stream_chunks.bf`, `stream_runs.bf`, `optimize.bf` | BBC | Filter, validate and optimize source, in Brainfuck |
| `compile.xax` / `compile_bfx` | XAX | The one public entry that drives those BF passes |
| `bfx.xax` | XAX | The single strict BFX decoder |
| `import_bfx.xax` | XAX | Turns a valid record into a verified decision store |
| `bbc.xax` | XAX | The whole `bbc.exe`: commands plus the native XAX driver |
| `bbc-android-arm64.xax`, `bbc-windows-x86_64.xax` | XAX | Host build requests the decision is bound into |

The decoder is shared by `bfx.xax` and `import_bfx.xax`, so there is exactly
one way to read BFX. No old-format fallback exists.

---

## 📐 Buffer contracts

Every component borrows typed views. They must be separate, initialized and
alive. Raw native pointers alone prove nothing.

| Component | Views (bytes, in argument order) |
|---|---|
| Public `compile_bfx` | source/work 1,114,112 · record 65,546 · output/work 1,114,112 · tape/work 1,114,112 |
| Decoder | record 65,546 (read-only) · scratch 524,288 · plus logical length |
| Importer | record 65,546 (read-only) · scratch 524,288 · arena 536,870,912 · hash scratch 2,048 |
| Source coordinator | same four views as `compile_bfx` |
| Packing coordinator | record 65,546 · input, output and tape work 1,114,112 each |

Return values pack length and status into one number:

| Component | Returns |
|---|---|
| Decoder | `(count << 32) \| status` |
| Importer | `(store_bytes << 32) \| status` |
| Source and packing coordinators | `(record_bytes << 32) \| status` |

Decisions borrow three 2,147,246,080-byte views (input, output, tape). Hosts reserve them
and commit pages as touched; see
[XAX dynamic tape](https://github.com/MrxSiN/XAX/blob/main/compiler/integration/bfx/DYNAMIC_TAPE.md).

On any failure, discard every provisional buffer.

The importer's record length goes in the first scratch u32. The private
source-coordinator layout (source at offset 65,536, length at record offset 0)
is internal; callers use `compile_bfx`. Source over 1 MiB is rejected before
the tape is touched.

---

## ⚙️ How a build runs today

`bbc.exe compile` does everything in one native process, with no Python. The
full pipeline is in [native compilation](25_NATIVE_COMPILE.md).

1. BBC's Brainfuck passes produce BFX.
2. The XAX importer turns it into a decision store.
3. A framing function wraps that store as an expected-root edit record.
4. The driver steps run in turn:
   - **edit** binds the decision into the host request;
   - **resolve** produces the build snapshot;
   - **build** verifies it, lowers it to machine code and packages it.

The generic Python XAX SDK is used once, to bootstrap `bbc.exe` itself.

---

## 📎 History

- The standalone Android and Windows hosts embed decisions, not BFX decoders.
- Their earlier packaging and app evidence keeps its original scope.
- The [ARM64 alias index](../evidence/xax_alias_index.json) and later driver changes
  touch only the XAX backend. BFX and BBC's Brainfuck are unchanged.
- The format migration changed no generic SDK files and was built with SDK
  `3dcb358`. All eight migration-snapshot component images rebuilt identically.
