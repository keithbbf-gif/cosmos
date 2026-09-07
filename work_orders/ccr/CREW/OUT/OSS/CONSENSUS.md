# CONSENSUS — OSS code borrow (MOTIF)

**DEFINE:** `DEFINE_OSS_BORROW.md`  
**RESEARCH:** `R1_CODE.md`, `R_LANGGRAPH.md`, `R_N8N_DIFY.md`, `R_TEMPORAL_LANGFLOW.md`

Three independent code reads agreed. Perplexity stack REJECT stands.

## Agreed

| Bucket | What |
|---|---|
| **IN COSMOS** | Pause-without-LLM-poll (P13), SEED close (P11), CCr `--accept` as resume, ledger authority (P07), spend 409 (P09), jukebox stale, FINDINGS as HITL, dual-lane isolation (P02). |
| **ADAPT** | (1) Ledger `WORK_ORDER_PICKED` at pickup before the agent runs — folder `picked/` is not authority (LangGraph crash-before-first-`put`). (2) Review = FINDINGS + stale RUNNING as their waiting list — already painted; do not add `waiting`/`PAUSED` to OUTCOMES. (3) Two clocks: wall vs idle = timeout BROKE vs stale RUNNING. |
| **BORROW** | **None.** No pip/npm of LangGraph, Temporal, n8n, Dify, LangFlow. |
| **LEARN** | Interrupt without checkpointer is a no-op; re-execute-node-on-resume is a footgun; short in-RAM wait vs long disk wait; heartbeat details ≠ SEED. |
| **REFUSE** | Their runtimes, Postgres/Sqlite as run authority, time-travel/fork, auto-retry, public resume URLs, Celery, LangFlow canvas, `lfx serve`, FastAPI replacing `:8770`. |

## Next BUILD (Gitur, Core)

`WORK_ORDER_PICKED` ledger event at `pickup_order` when Core is composed. Runner still does not hold the pen. DONE stays Output exists. Resume stays `--accept`/`--reject` on `order_id`.
