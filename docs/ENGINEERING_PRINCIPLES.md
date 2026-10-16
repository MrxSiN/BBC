# Engineering principles, minus the costume

SOLID is useful guidance. Brainfuck has no classes, methods or inheritance. Inventing them just to say we applied Liskov would be a strange use of the eight commands.

| Idea | What we actually do |
|---|---|
| **SRP / SoC** | Keep source parsing, native byte emission, transport, testing and annotation work in distinct regions or tools. Compiler logic stays in BF. |
| **OCP** | Extend test cases and verification without rewriting a working compiler. Real new targets still require BF changes and a fresh S2 bootstrap. |
| **LSP** | Require independently implemented BF seed executors to obey the same execution contract. There are no language-level subtypes. |
| **ISP** | Expose only bytes and a documented compiler status to tools that need them. Don't make transport care about native opcode internals. |
| **DIP** | Compare behavior against the execution spec and output protocol, not one interpreter's accidental behavior. |
| **DRY** | `core.bf` is the one compiler; generated annotated views and status records are derived. Independent references are deliberate test redundancy. |
| **KISS** | Keep fixed-size slots until a verified improvement makes them unnecessary. Fewer clever invariants to break. |
| **YAGNI** | No invented OO framework, universal IR, JIT, or unused backends. |
| **Law of Demeter** | Test tools use public streams and artifacts, not secret tape-cell addresses. |
| **Boy Scout Rule** | When touching something, fix stale claims, add a regression test, and rerun the evidence gates. |

## Rules for changing `core.bf`

1. Read the latest project requirements, normative V0 spec, and current annotation map.
2. Make one small change tied to an actual correctness, size or performance issue.
3. Keep the authoritative source executable by any standard Brainfuck interpreter. Its six safe ignored annotation lines are checked with a linter, but user-source comment compaction remains unfinished. Preserve the filtered command stream when editing explanations, and do not silently exceed the self-compilation byte limit.
4. Update annotation offsets and source hash; regenerate the view.
5. Run differential semantics, two-seed Stage 0, native Stages 1–2, ELF decoding and syscall fault checks.
6. Update status and open issues with observed results. Failed tests don't become successful by editing their descriptions.

The result should be easier to understand or objectively better, without quietly becoming another language. If code doesn't need changing, leave it alone. BF is already hard enough to debug.
