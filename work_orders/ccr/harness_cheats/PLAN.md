# Plan — both jobs, one door table

Keith 2026-09-25. Write both. Standalone first. The internal harness is required.

## Two kinds of door

Foreign doors (`pi`, `opencode`, `dsh`, `codex`) are subprocesses. Core cannot
see inside them. It grades the attempt after they exit. That is the agnostic
table.

`cosmos-code` inside Core is not that. It is the internal harness. Core
imports the module and calls it. The return is a typed DoneBundle or a refuse,
not scraped stdout. Spend is checked before the model call returns. The
attempt grant is passed in. The module cannot widen it.

Without that in-process harness, Core can code only if some foreign binary
is installed. That is a hard dependency, not an option. Foreign doors stay
optional because this one is always there.

## Not agnostic

The pen, the lease, spend, and publish to `live/`. Those stay Core. Every
door, including `cosmos-code`, is refuse-if-it-writes-`live/`. That check
sits on the Core side of the table, so a foreign harness cannot skip it.

## The contract (the only thing Core knows)

In: attempt directory, model pin, mission text, optional oracle, the list of
revealed layers.

Out: an event log, files only under that attempt, and either a DoneBundle or
a refuse. No `live/` path in either direction.

## Job 1 — standalone

Package: `V:\A\COSMOS_Harness\code\cosmos_code_scaffold`.

Entry: `python -m cosmos_code run --attempt <dir>`. No Core import inside
the package. Ultralight tools: read, edit, write, jail, stop. Shell dark.
Cap. Pin lock. Delete hunk archives.

This entry must work on a machine with no COSMOS tree.

## Job 2 — in-process

Dependency is one way. Core imports `cosmos_code`. `cosmos_code` does not
import Core, the pen, or cDeck. Standalone still works: the CLI is the same
module with no Core on the path.

```
spec = AttemptSpec(attempt, pin, mission, revealed, grant)
result = cosmos_code.run(spec)          # DoneBundle | Refuse
```

Core publishes only if `result` is a DoneBundle and the grant never included
`live/`.

`cosmos-code` is not a default among equals. It is the harness Core has.
A named foreign door is an option: Core still owns the grant, the spend
check, and the `live/` refuse. The foreign process does not replace the
module, and Core can still code if that binary is absent.

## Order

1. Contract plus Job 1 CLI. Prove refuse-`live/` and stop-without-bundle with no Core present.
2. Core calls `cosmos_code.run(spec)` and gets a typed result. Prove a missing `pi.cmd` does not stop that call.
3. Not in those two writes: cDeck modes, CheapGate, a C helper, Cordis, LangGraph.

Architecture: `V:\A\COSMOS_Harness\code\cosmos_code_scaffold\ARCHITECTURE.md`.
Source notes: `work_orders/ccr/harness_cheats/SOURCE_NOTES.md`.
Not written until Keith says write.
