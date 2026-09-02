# AGENTS.md — Cosmos Conventions

This file is read automatically by Copilot, Cursor Bugbot, and any native GitHub agent on every PR. Follow it.

## Work order loop

- Work orders live in `work_orders/drop/` as JSON (six fields per `docs/WORK_ORDER_SOP.md`).
- Verdicts go back into the same JSON file per `docs/VERDICT_SPEC.md`: status, reason, objection (file+line+fix), timestamp.
- Ara (voice layer) polls these files and reports status to the user. No desktop required.

## Adversarial loop (dual-lane)

- Every work order is executed by two independent builders: **Grok Code 4.6** and **Cursor Composer 2.5**.
- Neither lane may read the other's branch, PR, or output before submitting its own.
- A reviewer (Copilot pinned to Claude Opus 5, or Cursor Bugbot) diffs the two and writes a `Comparison` object.
- Disagreement is the signal. Agreement on a hard task is suspicious — flag it.
- Full spec: `docs/ADVERSARIAL_LOOP.md`.

## Focus areas for review

1. Runtime-binding gate — does the machine actually execute the new tree, or a cached snapshot?
2. Windows service — is COSMOS Core a real always-on resident process?
3. Work-order loop — claim detection, verdict write-back, session notification.
4. Federation — peer mesh blockers.
5. Panel resize + drag-to-move with grid snap on the D-deck.

## Do not

- Write the live tree from a proposal. Propose only; COW applies.
- Name Cursor or Claude as the `Agent` field in a work order. Cursor is a separate lane; Claude is off the route.
- Invent absolute paths or a second daemon.
