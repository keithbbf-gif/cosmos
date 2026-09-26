# Phase 2 unique KEEP — what this pen did (2026-09-24)

Did **not** farm 35 CCrew jobs. Did the unique bites that don’t write T and don’t bounce Core.

| Item | Disposition |
|---|---|
| `record_hit_vectors` default `error_mag=5` | **LANDED** — omit mag; existing compare test passes mag=5 explicitly |
| Session-tools verbs scan/load/convert/diff/check/anonymize/crash-recover/migrate | **PRESENT** — not rebuilt |
| Session-tools **rebind** | **LANDED** — missing ARCH verb; refuses `ses_cow_*`; hermetic tests |
| Factory TICK 60s | **PROPOSE** `FACTORY_TICK_PROPOSE.md` — loop exists; no second clock |
| Phase 1 P1–P4 | **HOLD** until Core bounce (`FORGED_EVENT`) |
| WO-031/037 porosity farm | **DROP** — superseded by landed tensor writer/WOMB |
| SpendGate UNPRICED settle $0 | **LANDED** — worst case held (`unpriced_held_usd`); headroom shrinks. test_spend_context 16/16 |
| Inter-orch mailbox | F-55 channel **PRESENT**. Unique leftover **LANDED**: gbot writer on COSMOS live → `SHARED_TREE`. Mail tests 25/25 |
| cDeck token+dollar meters | **LANDED** header `#tokStrip` (IN/OUT UNMEASURED, settled $ from `/spend`, day/week UNMEASURED). `meter.json` tokens/usd fields |
| New-AI scout | **LANDED** `cosmos_scout.py --once` — diffs NEW_AI_SCOUT vs MESH (no invented web). 16 candidates, 15 still new |
