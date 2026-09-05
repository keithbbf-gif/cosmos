# COSMOS Work Order — schema + lifecycle

**Operator SOP (SGH voice/mobile — how to format and drop):** `docs/WORK_ORDER_SOP.md`.
SGH inbox on GitHub: `work_orders/drop/`. This file is the contract. Do not duplicate a second desk.

_Keith 2026-08-27. The formal work-order contract. It enforces WRITE-PRIVATE + P10 by the
MECHANISM, not by asking the agent nicely: an agent only ever writes its own output file — never
the live tree — and nothing enters the tree until COW reads and accepts it._

## The bucket
Work orders are dropped in a **bucket** (a queue folder). A **Windows-native Python runner** polls
the bucket, picks up each work order, **creates the named agent**, and passes it the assignment.
The Windows clock carries the overhead — not Claude.

## Work-order record — the typed schema
One record per assignment. Fields:

| Field | Meaning |
|---|---|
| **Agent** | `Family \| Clade \| Version` — the exact model to instantiate (see `docs/MODEL_ACCESS.md`). e.g. `Anthropic \| Sonnet \| sonnet-5`, `xAI \| Grok \| grok-4.6`, `OpenAI \| Codex \| gpt-5.3-codex`. |
| **Context source** `[read*]` | The inputs the agent READS. `*` = read-only. The agent reads these for context; it does not write them. |
| **Task** | The assignment. |
| **Target & scope** | What it targets + the boundary of what it may produce/touch. |
| **Timestamp** | When the work order was dropped. |
| **Output** | `folder \| filename` — where the agent writes its deliverable (its only write surface). |

## Lifecycle — two deciders (runner vs COW)

1. **DROPPED** — the work order sits in the bucket.
2. **PICKED UP** — the native Python runner takes it, **creates the agent** (per `Agent`), passes it
   the `Task` + `Context source` + `Target & scope`. The agent works **WRITE-PRIVATE**: it reads the
   context sources and writes **only** its `Output` folder/filename — never the live tree.
3. **DONE** — when the agent finishes and the output file exists, the runner files the work order as
   **DONE** in the **ASSIGNED-tasks folder** (`live/state/work_orders/assigned/`). DONE = executed +
   output produced. **Not yet checked. Not yet accepted.** This is the “done folder.”
4. **Lane B (pickup, parallel)** — Cursor Composer 2.5 on the **same** drop, independent clone,
   no shared context with Lane A. PR `WO: <task>`. Not the `Agent` field. Spec:
   `docs/ADVERSARIAL_LOOP.md`.
5. **CHECKED** — **same runner, after DONE, before COW looks.** CI only: GitHub Actions (UNMEASURED
   until a workflow exists) and GitLab `.gitlab-ci.yml`. Stamp `checks.github` / `checks.gitlab`.
   A missing rail is **UNMEASURED**, never a fake green. Does not COMPLETE. Cursor is **not** this
   step — Cursor already ran as Lane B.
6. **COMPLETED** — this TUI reads both takes (Grok Output + Cursor PR) + `Verdict` + CI stamps, then
   **reviews/refines**. If accepted and the output touches the tree, **CCr writes** it (Keith
   2026-09-04: work orders + GitHub/Cursor/GitLab + review, not in-session authoring). Agents never
   write the live tree.

COW does not run the lanes or the CI in the orch TUI. Cursor-as-critic (post-DONE Cloud Agent on
Grok's Output) is **wrong** for this desk — Cursor is the parallel coder.

## Why (canon)
- **P10 enforced by mechanism, not goodwill.** The agent physically writes only its output file, so
  it *cannot* write the live tree. This closes the `--cwd = live tree` + `--always-approve` hole in
  the old grok lane (the Codex rail already ran attempt-private; this makes it universal).
- **DONE ≠ COMPLETED = the fenced commit gateway.** The runner marks DONE (work executed); COW alone
  decides COMPLETED (output read + accepted). Nothing enters the tree unreviewed.
- **Model is a first-class field.** `Family|Clade|Version` lets a work order name any of the tappable
  versions (`docs/MODEL_ACCESS.md`) — coding→Grok/Cursor, research/SSA→Sonnet, etc.
- **The OS runs the machine.** Native Python runner + Windows clock; Claude makes the sparse
  decision (drop the order, accept the output).
