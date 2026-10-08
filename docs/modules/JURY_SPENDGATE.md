# Jury — Token Center and Core SpendGate

Date: 2026-10-08. Five jurors. Model slug `grok-4.7`. No live charges, no secrets, no edit to either wallet during the debate.

Question: should this chair bind Token Center to Core SpendGate in the finish wave? They are two wallets. A grant and a meter emit are separate commits. Binding them can double-charge or double-deny.

## Juror 3 — read-only bridge

VERDICT: BIND_READ_ONLY

Token Center sells and meters credits. SpendGate fences live spend. A full bind now would let an unfinished desk grant, reserve, or deny Core work. A purchase with no Stripe or PayPal already returns 503, and that refusal should stay. Only a configured RunPod call meters and charges. Vertex is not attached. Bedrock, OpenRouter, and Azure must fail closed and must not fall through to RunPod. cDeck does not sell credits. `credits_face_usd` and `meter.db` stay separate. SpendGate may show Token Center totals. It must not debit them, reserve them, or treat a missing purchase as a Core deny.

## Juror 2 — keep two wallets

VERDICT: DO_NOT_BIND

`cosmos/` does not import `cosmos_pay`. SpendGate settles the Core ledger. Token Center settles `credits_face_usd` and `meter.db` as separate commits. Wiring both onto one call before a single transaction exists can reserve twice, deny twice, or charge twice. A bad bind is harder to undo than split headroom. This juror also said not to attach Vertex, Stripe, or PayPal. That sentence is recorded. The rails work already running is fail-closed dispatch, not a SpendGate bind, and it is not stopped by this one vote.

## Juror 4 — one transaction first

VERDICT: DO_NOT_BIND

`Store.reserve`, `settle`, and `grant` commit `credits_face_usd` on `keys.db`. `Meter.emit` commits later on `meter.db`. No single transaction spans both. `PayGateway.chat` can settle and then swallow a meter error. Core does not import `cosmos_pay`. The pay gateway does not import `cosmos_spend`. A read-only view of a split book can still look like spend when one row is missing. Cross-bind only after grant and meter emit commit or roll back together, proved by a test that kills the process between the two writes.

## Juror 1 — bind now

VERDICT: BIND_NOW

One SQLite transaction should write the credit delta and the meter row under one event id, then commit once. SpendGate stays the only run breaker. Do not also call `store.reserve` and `guarded_call` on the same run. No live rail, Stripe, or PayPal call. No server restart.

## Juror 5 — skeptic

VERDICT: DO_NOT_BIND

Not bound today. A mirror comment is not a call. Reject bind-now and transaction-first because they need a live charge or a restart of port 8770. Reject read-only as "bound" while SQLite still spends. Reject two wallets as a finished state. Finished today means the non-bind is explicit: stores unmerged, rails fail closed, deck string UNMEASURED, no live key, no live charge, service left as it was started.

## Tally and chair

BIND_NOW 1. BIND_READ_ONLY 1. DO_NOT_BIND 3.

Chair: DO_NOT_BIND. No SpendGate import of `cosmos_pay`. No merge of `credits_face_usd` and `meter.db`. No restart of port 8770. The fail-closed rail work is not a bind and continues. A later single-transaction fold is a separate change after a crash test on a temp database.
