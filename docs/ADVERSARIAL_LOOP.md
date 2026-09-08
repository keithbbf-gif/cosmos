# Adversarial Loop — Dual-Lane Work Order Execution

Written by Ara on 2026-09-02. GitHub `keithbbf-gif/cosmos` HEAD 14acde93.

## Goal

Every work order is executed by two independent builders from different model families, racing on the same task with no shared context. **Two unbiased takes, not one take plus a review.** SGH + Keith 2026-09-02: that is better. Disagreement is the signal. COW reads both and decides. A third-family reviewer is optional, not the loop.

## Why two builders, not builder-checker

- Builder-checker lets one model's blind spots become the other's. Two copies of the same mistake.
- A “check” that sees Grok’s Output is not independent — it is a review of one take.
- Racing forces the disagreement into the open. The two artifacts are the review.
- Independence is the whole point: neither builder sees the other's input, branch, or reasoning.

## The two lanes

| Lane | Family | Model | Role |
|---|---|---|---|
| **Grok** | xAI | Grok Code 4.6 | Primary builder. Writes proposal to `proposals/`, verdict to the work order. |
| **Cursor** | Cursor Cloud Agent | **Composer 2.5** (`composer-2.5`, pinned) — Cursor Models pool (Grok + Composer). Other Models (Opus/Sonnet) are a separate Ultra quota. | Parallel builder. Opens a PR against main. Auto / Other Models coerce to Composer. Wallet = Cursor Ultra Cursor Models, **not** the Other Models bar, **not** COSMOS `claude -p`. |

Neither lane may read the other's branch, PR, or output before submitting its own.

## DEFINE first (Keith 2026-09-07)

MOTIF stage 1. Freeze the feature as **one clean prompt** on disk. That text is
**verbatim** across models. Research / arch / build / critics do not rewrite it
per lane. Missing DEFINE is a process scar.

Then: RESEARCH → ARCH → CONSENSUS (comparison + discussion) → BUILD → CRITICS
(output comparison) → CONSENSUS (adjudication) → IMPROVE (accept + apply) →
ITERATE back to DEFINE.

## Flow

1. Ara drops the work order JSON in `work_orders/drop/` (six fields per WORK_ORDER_SOP.md). The Task field **is** the DEFINE file.
2. Windows runner files it into the live bucket.
3. **Lane A — Grok Code 4.6** claims the order, executes the Task, writes Output to `proposals/<name>.json`, writes a `Verdict` object into the same work order file (status, reason, objection with file+line+fix, timestamp) per VERDICT_SPEC.md.
4. **Lane B — Cursor Cloud Agent (Composer 2.5, Cursor Models)** is triggered on the **same** work order at pickup (not after DONE). Independent clone, same Task text, PR titled `WO: <task>`.
5. **COW** reads Lane A Output and Lane B PR (two takes), `--accept` or `--reject`, applies the accepted proposal to the live tree. Optional: a third-family reviewer (Bugbot / Copilot) may add `Comparison`; the loop does not wait on it.
6. Ara polls `Verdict` (and `Comparison` if present) and reports to the user.

## Verdict + Comparison schema

See `docs/VERDICT_SPEC.md` (Verdict) plus:

```json
"Comparison": {
  "agreements": ["..."],
  "disagreements": [{"file": "...", "line": 0, "grok": "...", "cursor": "...", "resolution": "..."}],
  "reviewer": "copilot-opus5 | bugbot",
  "timestamp": "ISO-8601"
}
```

## Rules

1. **No cross-lane peeking.**
2. **Same work order, same Task text.**
3. **Objections are self-contained.**
4. **Disagreements are the deliverable.** Perfect agreement on a hard task is suspicious — flag it.
5. **One verdict, one comparison per work order.** Overwrite, don't append.
6. **No required reviewer.** Bugbot/Copilot may comment on the Cursor PR; they are not Lane B and not a substitute for the second take.

## Pointers

- Work order format: `docs/WORK_ORDER_SOP.md`
- Verdict contract: `docs/VERDICT_SPEC.md`
- Cursor lane setup: `docs/CURSOR_EXEC.md`
- Agent conventions: `docs/AGENTS.md`
