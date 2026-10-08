## Claim grades

**Consistent with the tree (verified as stated):**
- Token Center PayGateway built with no vertex_rail; `_resolve_rail` falls through to RunPod for any non-injected rail — **grade: accurate**. Stock payment traffic silently rides a foreign rail.
- Bedrock/OpenRouter/Azure have no rail file — **grade: accurate**; those names would hit the NO_RAIL / RunPod fallback path.
- Credits purchase returns 503 without a Stripe or PayPal secret — **grade: accurate**; no secret, no ledger append.
- credits_face_usd and meter.db in separate commits; cosmos/ never imports cosmos_pay — **grade: accurate**. The face and the meter are not wired together in one tree state.
- cDeck day/week UNMEASURED; SpendGate.audit lacks a day/week field; meter_window exists but is uncalled; no Token Center client; 5 failed / 33 passed from stale probe JSON — **grade: accurate**. The 5 failures are not logic failures, but they are still failing runs.
- Resession grok-only; claude raises ANTHROPIC_OFF; other names raise NO_RAIL; auto-resession gated on execute; close line 190000/200000 — **grade: accurate**. That is 95% of the window consumed with one rail and a gate that is off by default.
- GET seats 501; GET chamber/temporal snapshot-only; POST chamber/temporal 501 pending ledger append — **grade: accurate**.
- propose() done false; DISPATCH_LOCKED; wipe_proof false — **grade: accurate**.
- Uncommitted Hermes/voice/federation/cluster safety diffs; no ruff package config; 13 core modules fail ruff 0.16 defaults — **grade: accurate**.

## Five highest-risk holes

1. **Money path is split at the commit level.** meter.db and credits_face_usd live in different commits, cosmos/ does not import cosmos_pay, and purchases 503 without secrets. There is no single tree state where a credits charge and its meter can be proven against each other.

2. **Spend measurement has no day/week resolution anywhere.** SpendGate.audit cannot express it, meter_window is never called, cDeck never displays it, and five tests are red. Budget enforcement is unmeasured at exactly the granularity operators need.

3. **Resession is a single point of failure near its ceiling.** One rail (grok), one provider file, close at 190000/200000, and auto-resession disabled unless execute is set. Every other rail name is a hard raise.

4. **All state-writing endpoints are 501.** POST chamber and POST temporal do not append the ledger; seats is 501. Snapshots read fine; nothing persists.

5. **Dispatch is locked with wipe_proof false.** propose() returns done false and DISPATCH_LOCKED stands, meaning proposal-to-execution is unproven, while thirteen modules fail ruff and four subsystems carry uncommitted safety diffs.

Nothing here is closed.