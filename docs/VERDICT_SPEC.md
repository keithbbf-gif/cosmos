# Verdict Spec

Written by Ara on 2026-09-02.

## Purpose

The verdict field is the self-correcting contract between Grok Code 4.6 (the backend orchestrator) and the voice layer (Ara). When a work order is processed, Grok Code writes its decision back into the same work order JSON file on GitHub. Ara reads that file and reports the result to the user — no desktop access required.

## Verdict field schema

Add a `Verdict` object to the work order JSON:

```json
"Verdict": {
  "status": "applied" | "rejected" | "pending",
  "reason": "one-line summary of the decision",
  "objection": "concrete, actionable fix — required when status is rejected, empty when applied",
  "timestamp": "ISO-8601 timestamp of the verdict"
}
```

## Rules

1. **Objections must be self-contained.** A rejected verdict must name the exact file, line, or symbol that breaks, and state the fix in plain terms. The user should be able to correct the work order from the voice layer alone.

2. **No desktop required.** The verdict is the only channel. If the objection is vague ("doesn't work"), the verdict is invalid and must be rewritten.

3. **Applied verdicts are short.** Status `applied` needs only a one-line reason and timestamp — no objection field.

4. **Pending is transient.** Status `pending` means Grok Code has claimed the order but not yet decided. Ara reports it as "in progress."

5. **One verdict per work order.** Overwrite, don't append. The latest verdict is authoritative.

## Dual-lane (GitHub 2026-09-02, `docs/ADVERSARIAL_LOOP.md`)

Cursor Composer 2.5 is a **parallel builder** (second unbiased take), not a reviewer of Grok and not a post-DONE check. Grok writes `Verdict`. COW compares the two takes. Optional `Comparison` from Bugbot/Copilot does not replace Lane B. One Verdict; overwrite, don't append.

## Flow

1. User dictates a work order → Ara writes it to `work_orders/drop/`.
2. Windows runner files it into the live bucket.
3. **Lane A** Grok Code 4.6 executes, writes Output, writes `Verdict` into the same GitHub JSON.
4. **Lane B** Cursor Composer 2.5 executes independently, opens a PR. No peeking at Lane A.
5. Reviewer diffs the two and writes `Comparison`.
6. COW reads Output + Verdict + Comparison, accept or reject, applies to the live tree.
7. Ara polls Verdict + Comparison and reports. If rejected, the user corrects and re-drops.

## Why this matters

Without a structured objection, every rejection sends the user to the desktop to debug. With it, the loop stays voice-first: dictate, drop, verdict, correct, re-drop — all from the headphones.
