# P04 — Runtime-binding gate vs green-log

**Kind:** method / selection gate. **Status:** FILE. **Fee:** US provisional micro $65.

## What it is (in-tree)

DONE is a **value only the live tree can emit**. Exit codes, critic prose, dashboard color, and this PDF are not evidence. Fail-closed: a missing or contradicting artifact is a refusal, not a silent pass. Encoded MOTIF gate; `docs/SCAR_PLACATION.md` (fabricated compliance).

## Problem / scar

A pipeline reports success because tests exited zero or a critic said “looks good.” That is fabricated compliance — a plausible lie that closes the ticket while the running system does not do the thing.

## Written description

1. For a change to be accepted, require an artifact that **only the running system** can produce (a live API value, a ledger event field, a hash only the true run emits).
2. Treat CI green, critic “LGTM,” and UI checks as **projections**, never authority.
3. If the live emit is missing or contradicts the claim, record a **refusal** (fail-closed). Do not repair a green log in place.
4. The report of the change must carry the live artifact or the refusal.

## Already public

Runtime-binding language in public MOTIF / architecture (cosmos 2026-08-23).

## Prior art to name (R1)

**Related:** Proof-or-Stop arXiv:2607.14890; Microsoft Azure 2026-08-29 “validate at runtime”; The New Stack runtime verification; CI as quality gate (Jenkins, GitHub Actions) — the *opposite* occupancy if CI is treated as DONE. No US patent found that claims “only a live-system-emitted value is DONE.” Patent occupancy **thin**. Paper/engineering occupancy **high 2026**.

## What this is not

Not “don’t trust CI.” Not a test framework. Not a bake-off.

## Suggested independent idea

Binding “finished” to a value only the live tree can emit, with fail-closed refusal when that value is absent.
