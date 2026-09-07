# RESEARCH — OSS source (not layout). MOTIF stage 2.

**DEFINE:** `work_orders/ccr/DEFINE_OSS_BORROW.md`
**Date:** 2026-09-07. CCr. Code quoted from public GitHub raw.

Prior stack REJECT stands. This pass reads **mechanisms**.

## Sources opened

| Tree | File (quoted) |
|---|---|
| `langchain-ai/langgraph` | `libs/langgraph/langgraph/types.py` — `interrupt()`, `Command`, `Durability`, `TimeoutPolicy`, `RetryPolicy` |
| `langchain-ai/langgraph` | `libs/checkpoint` README — `BaseCheckpointSaver.put/get_tuple/list/delete_thread` |
| `n8n-io/n8n` | `packages/nodes-base/nodes/Wait/Wait.node.ts` — `execute`, `putToWait`, `putExecutionToWait` |
| Temporal (SDK/proto, not our runtime) | activity `heartbeat_timeout` vs `start_to_close_timeout`; miss → TIMED_OUT |
| Dify `HumanInputNode` path | **404** on `api/core/workflow/nodes/human_input/human_input_node.py` this fetch; discussion #29048 describes PauseRequestedEvent — treat as UNMEASURED until a live path is quoted |

LangFlow editor/runtime split: not quoted this pass (embed already REJECT).

## Mechanisms (with quotes)

### 1. LangGraph `interrupt()` — pause is an exception + checkpointer

From `types.py` `interrupt()`:

- First call in a node **raises** `GraphInterrupt` with an `Interrupt` payload (`value` for the human, `id` to resume).
- Resume is `Command(resume=...)`. The graph **restarts the node** and replays until the interrupt index has a resume value.
- Docstring: *"To use an interrupt, you must enable a checkpointer."*
- `Durability`: `'sync'` persist before next step; `'async'` while next step runs; `'exit'` only on graph exit.
- `TimeoutPolicy`: **run_timeout** (hard wall, never refreshed) vs **idle_timeout** (refreshed by progress or `runtime.heartbeat()`).
- `RetryPolicy`: exponential backoff, jitter, max_attempts, retry_on.

**Crash-before-first-checkpoint** (issue #8764): an accepted run can vanish if `put` never lands. That is our placation class.

### 2. n8n Wait — do not keep the process (or the LLM) spinning

From `Wait.node.ts` `execute()`:

- Resume modes: timeInterval, specificTime, **webhook**, **form**.
- Webhook resume URL is **generated at runtime** (`$execution.resumeUrl`), sent *before* the wait node.
- If wait < 65s: in-process `setTimeout` (process stays alive).
- If wait ≥ 65s: `putExecutionToWait(waitTill)` — **persist and leave**. LLM is not the waiter.
- `waitingNodeTooltip` tells the operator the resume URL. Authentication optional on the resume webhook.

### 3. Temporal heartbeat — two clocks, miss is failure

Activity proto: `start_to_close_timeout` (one attempt wall) vs `heartbeat_timeout` (max gap between pings). Missed heartbeat → TIMED_OUT, then retry policy. Last heartbeat can carry **details**. Heartbeat is also how cancel is delivered (no heartbeat timeout ⇒ cannot cancel).

LangGraph `TimeoutPolicy` is the same split (run vs idle).

## Bucket table

| Mechanism | Bucket | COSMOS already | Apply |
|---|---|---|---|
| Pause that **persists** and does not poll the LLM | **IN COSMOS** | P13 daemon + GitHub drop; HOLD vs resume-gate (P11) | Keep. Do not add Temporal. |
| Resume token / URL the human can hit | **ADAPT** | Drop `work_orders/drop/`; CCr `--accept` | Review pane: FINDINGS row must show it is **waiting for CCr**, not a dead run. Resume is `--accept`, not a vendor webhook. |
| Interrupt payload (`value` the human sees) | **ADAPT** | FINDINGS is the Core word | Paint FINDINGS body on Review (DEFINE pane-fns). Do not add annotation POST. |
| Checkpointer required for HITL | **LEARN / IN COSMOS** | Ledger + SEED. Crash before first put = OPEN_CONTEXT / placation | HITL without a ledger event is a lie. Gate: FINDINGS implies a ledger event (P04). |
| Re-execute node from start on resume | **LEARN** | Dual-lane rebuilds from DEFINE, not from a mid-node scratchpad | Do not blindly replay a half-run. Resume from DEFINE / drop, not LangGraph scratchpad. |
| Durability sync/async/exit | **LEARN** | Ledger append is sync-enough; projections async | Do not add a durability enum to MOTIF. |
| run_timeout vs idle/heartbeat timeout | **ADAPT** | jukebox `stale_flag` on RUNNING past window; ingest `last_run_epoch`; report-never-retry | Keep stale as **reported**, not silent RUNNING. Already in `cosmos_jukebox_panel.py`. Tighten only if live emit shows RUNNING with no stale. |
| RetryPolicy with jitter | **REFUSE** as auto-retry | report-never-retry is canon | Do not borrow n8n/LangGraph auto-retry onto Core jobs. |
| Checkpoint history / fork-from-id | **REFUSE** | `PROFILES.md` time-travel out | Do not list checkpoints as a time machine. |
| `Send()` map-reduce fan-out | **LEARN** | Dual-lane is two isolated builders, not N Send() into shared state | Porosity overlay is seating, not LangGraph Send. |
| n8n as scheduler / LangGraph as MOTIF / Temporal worker | **REFUSE** | H2/H8; Perplexity stack REJECT | Unchanged. |
| LangFlow canvas embed | **REFUSE** | Studio extra pane | Unchanged. |
| Wait <65s in-process timer | **LEARN** | 15s Activity Clock is the OS waiter | Do not add a second in-process wait loop in Core. |

## What should be in COSMOS (organs)

Already: ledger (P07), fence, SEED (P11), drop+daemon (P13), spend confirm (P09), DOM-first (P08), runtime-bind (P04), occupancy (P05), jukebox stale, FINDINGS outcome.

**Hole to fill (ADAPT, not a new engine):** make the HITL pause **look and bind** like `interrupt()`+`putExecutionToWait` *on our emits*:

1. FINDINGS (or Review wait) **must** quote a ledger/heartbeat artifact (P04).
2. cDeck Review must say **waiting for CCr** when FINDINGS is the pause, analogous to n8n `waitingNodeTooltip`.
3. Stale RUNNING must stay visible as stale (Temporal missed heartbeat), never as healthy in-flight (DEFINE pane-fns: BROKE/stale ≠ in-flight).

## What can be borrowed (code in our tree, not their runtime)

- The **two-timeout** names: wall vs idle. Map onto existing stale window; do not import `TimeoutPolicy`.
- The **resume URL generated at wait time** idea: the GitHub drop path *is* that URL. Document it on Review/Talk. Do not stand n8n webhooks.

## What can be adapted

- Studio graph nodes stay MOTIF stages, heat from `/jukebox` (already).
- Dual-lane isolation ≠ LangGraph shared state + Send.
- Phone/terminal adversarial (P13/P05) is our `Send` to N seats with peeking ban.

## What can be learned (docs only)

- Interrupt without checkpointer is a no-op in LangGraph — same as HITL without ledger.
- Re-executing a node on resume is a footgun; our iterate goes back to DEFINE.
- n8n keeps short waits in RAM and long waits on disk — we already chose disk (drop + clock).

## Off this pass

No LangGraph/Temporal/n8n/Dify pip/npm. No Postgres checkpointer. No time-travel UI. Dify HumanInputNode source UNMEASURED (404).
