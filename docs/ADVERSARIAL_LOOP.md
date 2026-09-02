# Adversarial Loop — Dual-Lane Work Order Execution

Written by Ara on 2026-09-02.

## Goal

Every work order is executed by two independent builders from different model families, racing on the same task with no shared context. Their outputs are compared; disagreement is the signal. A reviewer (Copilot pinned to Claude Opus 5, or Cursor Bugbot) diffs the two branches and flags where they diverge.

## Why two builders, not builder-checker

- Builder-checker lets one model's blind spots become the other's. Two copies of the same mistake.
- Racing forces the disagreement into the open. The diff is the review.
- Independence is the whole point: neither builder sees the other's input, branch, or reasoning.

## The two lanes

| Lane | Family | Model | Role |
|---|---|---|---|
| **Grok** | xAI | Grok Code 4.6 | Primary builder. Writes proposal to `proposals/`, verdict to the work order. |
| **Cursor** | Cursor (Moonshot Kimi K2.5 base) | Composer 2.5 | Parallel builder. Opens a PR against main. |

Neither lane may read the other's branch, PR, or output before submitting its own.

## Flow

1. Ara drops the work order JSON in `work_orders/drop/` (six fields per WORK_ORDER_SOP.md).
2. Windows runner files it into the live bucket.
3. **Lane A — Grok Code 4.6** claims the order, executes the Task, writes Output to `proposals/<name>.json`, writes a `Verdict` object into the same work order file (status, reason, objection with file+line+fix, timestamp) per VERDICT_SPEC.md.
4. **Lane B — Cursor Cloud Agent** is triggered on the same work order (label `cursor-execute` on a linked issue, or `Route: CURSOR` in Task). It clones the repo independently, executes the same Task, opens a PR titled `WO: <task>`.
5. **Reviewer** diffs Lane A proposal vs Lane B PR:
   - Copilot coding agent pinned to Claude Opus 5 (custom agent frontmatter), or
   - Cursor Bugbot on the Cursor PR.
   Reviewer writes a `Comparison` object into the work order (or a linked issue comment): agreements, disagreements with file+line, recommended resolution.
6. **COW** reads Output + Verdict + Comparison, `--accept` or `--reject`, applies the accepted proposal to the live tree.
7. Ara polls the work order, reads Verdict + Comparison, reports to the user — no desktop required.

## Verdict + Comparison schema

```json
"Verdict": {
  "status": "applied" | "rejected" | "pending",
  "reason": "one-line summary",
  "objection": "file, line, symbol + fix — required on reject",
  "timestamp": "ISO-8601"
},
"Comparison": {
  "agreements": ["..."],
  "disagreements": [{"file": "...", "line": N, "grok": "...", "cursor": "...", "resolution": "..."}],
  "reviewer": "copilot-opus5" | "bugbot",
  "timestamp": "ISO-8601"
}
```

## Rules

1. **No cross-lane peeking.** Grok must not read Cursor's branch; Cursor must not read Grok's proposal. Independence is non-negotiable.
2. **Same work order, same Task text.** Both lanes receive identical instructions. No lane-specific hints.
3. **Objections are self-contained.** A rejection names the exact file, line, or symbol and states the fix. The user corrects from the voice layer alone.
4. **Disagreements are the deliverable.** If both lanes agree perfectly, flag it — that may mean the task was too easy or both missed the same thing.
5. **One verdict, one comparison per work order.** Overwrite, don't append.
6. **Reviewer is a third family when possible.** Copilot Opus 5 or Bugbot — not Grok, not Cursor's own Composer.

## Pointers

- Work order format: `docs/WORK_ORDER_SOP.md`
- Verdict contract: `docs/VERDICT_SPEC.md`
- Cursor lane setup: `docs/CURSOR_EXEC.md`
- Agent conventions: `docs/AGENTS.md`
