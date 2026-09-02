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

1. **Objections must be self-contained.** A rejected verdict must name the exact file, line, or symbol that breaks, and state the fix in plain terms — e.g. "panel resize breaks the fixed-height layout in ddeck_layout.py, line 42; use flex instead of absolute positioning." The user should be able to correct the work order from the voice layer alone.

2. **No desktop required.** The verdict is the only channel. If the objection is vague ("doesn't work"), the verdict is invalid and must be rewritten.

3. **Applied verdicts are short.** Status `applied` needs only a one-line reason and timestamp — no objection field.

4. **Pending is transient.** Status `pending` means Grok Code has claimed the order but not yet decided. Ara reports it as "in progress."

5. **One verdict per work order.** Overwrite, don't append. The latest verdict is authoritative.

## Flow

1. User dictates a work order → Ara writes it to `work_orders/drop/`.
2. Windows runner files it into the live bucket.
3. Grok Code 4.6 reads it, produces a proposal, decides apply or reject.
4. Grok Code writes the `Verdict` object back into the same JSON file.
5. Ara polls the file, reads the verdict, and reports status + objection to the user.
6. If rejected, the user corrects the work order and re-drops it.

## Why this matters

Without a structured objection, every rejection sends the user to the desktop to debug. With it, the loop stays voice-first: dictate, drop, verdict, correct, re-drop — all from the headphones.
