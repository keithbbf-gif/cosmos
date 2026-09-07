# Appendix — How BTS-MESH works (July 2026 predecessor)

**Kind:** written description / provenance for Legal to attach to US provisionals.
**Status:** not a USPTO filing. Excerpts from the local predecessor tree
`V:\Ai\BTS_MESH` (GrokBot pen). This TUI **read** those files; it does **not**
write that tree. Do not commit keys, OAuth, or live ledgers.
**Purpose:** prove the mesh **ran in early/mid July 2026**, and describe the
architecture COSMOS later replaced — so provisionals are not a history rewrite.

## Dates (measured)

| Fact | Date | Where |
|---|---|---|
| North-star architecture written | **2026-07-10** | `BTS_MESH_NORTH_STAR.md` (local) |
| Working foundation README | **2026-07-10** / README stamp 2026-07-11 | `README.md` — bus, registry, cards, watcher, orchestrator; 29 tests |
| SOP / wiring / state feed | **2026-07-14** | `BTS_SOP.md`, `WIRING.md`, `BTS_STATE_2026-07-14.md` |
| GitHub `bts-mesh` created | **2026-08-16T10:21:14Z** | public repo; About names CRUCIBLE; tracked files have 0 CRUCIBLE hits |
| COSMOS architecture ratified | **2026-08-23** | GitHub `cosmos`; `docs/RATIFIED.md` |

July operation = **local run records**. GitHub August 16 is **not** the start of
operation. Private-now does not un-publish GitHub.

## The goal (Keith, recorded 2026-07-10)

Grok could start a new session of another model (or ChatGPT) and load/point to
needed context, and vice-versa, as new sessions and topics spawn — multi-session,
multi-agent, multi-AI simultaneous coordination — and get Keith out of the middle
as the human message-wire.

The one insight: no consumer chat tab can autonomously boot **and seed** another
vendor’s session. That capability has to live in a **local orchestrator** on the
operator’s machine.

## Five components (as of 2026-07-10, working code)

1. **Shared bus** (`bts_bus.py`). Append-only, author-prefixed signal log.
   Payloads written atomically (temp + rename) so no reader sees a half-file.
   Per-reader cursor; self-filtering so a side never eats its own signals.
2. **Session seed.** Every spawned session starts by reading a
   `SESSION_SEED_<topic>.md` pointer. “Load the needed context” = read the seed.
   Orchestrator auto-creates seeds from a template. This is BootUP generalized.
3. **Session registry** (`SESSION_REGISTRY.json`). Single source of truth for
   `{agent, topic, url, status, tasks}`. Prevents two sessions doing the same work.
4. **Capability cards + routing.** Each AI advertises what it is best at; the
   daemon routes a new topic to a node. Cards are data (`cards/*.json`).
5. **Orchestrator daemon** (`bts_orchestrator.py`). Consumes the bus, updates
   the registry, handles `SPAWN_SESSION` (route → seed → register → queue launch).
   `launch_session()` was the remaining stub (Chrome bridge).

Wire format (contract v1.1): `{type, path, note, ts}` plus routing extras.
Types included `NEW_OUTPUT_READY`, `QUESTION_FOR_YOU`, `NEEDS_INPUT`,
`TASK_COMPLETE`, `ACK`, `SPAWN_SESSION`.

## Honest ceilings recorded in July (not smoothed)

- Not real-time. File-paced (seconds to minutes).
- Browser legs brittle. Prefer vendor APIs; fall back to DOM.
- More nodes = more drift (fake-DONE / contradictory state). Mitigations named
  then: append-only log, single-source registry, adversarial cross-check.
  Keep topology supervisor + fan-out, not all-to-all.

## What COSMOS kept, and what it replaced

BTS-MESH is the **predecessor mesh**. COSMOS is the **OS** that took the same
job — multi-AI coordination without Keith as the wire — and put **authority**
in one resident Core:

| BTS-MESH (July) | COSMOS (ratified 2026-08-23) |
|---|---|
| File bus + registry as coordination | One signed JSONL ledger as authority; projections rebuild |
| Orchestrator daemon as conductor | Core = API + scheduler + arbiter + sole ledger writer |
| Atomic temp+rename payloads | Fenced commit gateway + fencing tokens |
| Session seed files | Signed `SEED.json` at session close (OPEN_CONTEXT if missing) |
| Capability cards | Registry + rails matrix; DOM-first policy |
| Keith still in some loops | CCr one writer; orch does not hold the COSMOS pen |

Continuity of **operation** (July run → August GitHub → live Core) is provenance.
Continuity of **code** is successor architecture, not a claim that the July bus
is the 2026-08-23 ledger.

## What this is not

Not a dump of the BTS tree into a patent. Not keys, Drive folder IDs, or OAuth.
Not a claim that GitHub `bts-mesh` disclosed the method in tracked files (it
did not, for CRUCIBLE). Not permission to flip GitHub private from this TUI.

## Attach to

P07 (Core as successor authority), P05 (occupancy / multi-AI coordination),
P11 (seed / carry-over), and the provenance note Legal wants on the public
record. Duplicate into each FILE provisional that needs July operation as
support for 112(a) or for inventor-grace timing. Legal copies further excerpts
from `V:\Ai\BTS_MESH`; this TUI does not.
