# RESEARCH — Temporal SDK + Langflow graph (OSS-borrow MOTIF 1)

**Job:** `DEFINE_OSS_BORROW.md` lane Temporal + LangFlow.  
**Date:** 2026-09-07. **We did not run Temporal. We did not embed Langflow.**  
**Canon already frozen:** Temporal as clock **REJECT** (same class as n8n, H2/H8). LangFlow embed **REJECT**. Extra-pane Studio already exists on `cdeck.exe`. Do not recommend FastAPI+React replacing `cdeck.exe`. Core remains `:8770`.

This is a **code read**, not a product trial. Each row is one bucket. No "maybe Temporal later."

## Sources (file paths + symbols, not slogans)

| Tree | Pin | What was read |
|---|---|---|
| `temporalio/sdk-python` | SHA `22a9e41fd857261ee0a9bb5ce57f439d93e7f88d` | `temporalio/activity.py` (`heartbeat`, `Info.heartbeat_timeout`, `Info.start_to_close_timeout`, `Info.heartbeat_details`); `temporalio/workflow/_handlers.py` (`@signal`, `@query`, `@update` + validator); `temporalio/workflow/_workflow_ops.py` (`continue_as_new`, `ContinueAsNewError`, `all_handlers_finished`) |
| `temporalio/samples-python` | `main` | `hello/hello_continue_as_new.py` (`LoopingWorkflow` → `workflow.continue_as_new`); `hello/hello_cancellation.py` (heartbeat + `heartbeat_timeout`) |
| Temporal docs (quote the SDK) | live 2026-09-07 | [Detecting Activity failures](https://docs.temporal.io/encyclopedia/detecting-activity-failures) (start-to-close vs heartbeat timeout); [Continue-As-New Python](https://docs.temporal.io/develop/python/workflows/continue-as-new); [Workflow message passing](https://docs.temporal.io/encyclopedia/workflow-message-passing) |
| `langflow-ai/langflow` | SHA `e3abffc1b8da1e38cc2f21a9cf1b23b4a21c15d5` | `src/lfx/src/lfx/graph/graph/schema.py` (`GraphData`); `src/lfx/src/lfx/graph/vertex/schema.py` (`NodeData`); `src/lfx/src/lfx/graph/graph/runnable_vertices_manager.py`; `src/lfx/src/lfx/load/load.py` (`Graph.from_payload`); `src/backend/base/langflow/services/database/models/flow/model.py` (`Flow.data`); `src/backend/base/langflow/api/v1/chat.py` (vertex order + whole-flow build); `src/lfx/README.md` (LFX executor vs editor) |

COSMOS organs cited: `cosmos/cosmos_clock.py` `write_heartbeat` / `heartbeat_age_s`; `cosmos/cosmos_session.py` `close_session` / `start_session`; `cosmos/cosmos_spend_admin.py` `WIDEN_REQUIRES_CONFIRM`; `builds/cdeck/ui/deck_studio.js` (MOTIF stages, not a vertex DAG); docket `docs/research/docket/P09_SPEND_GATE.md`, `P11_SEED.md`, `P13_THINKFAST_DROP.md`.

---

## 1. Temporal — ideas, not the product

### 1.1 Activity heartbeat (`temporalio.activity.heartbeat`)

**Source.** `temporalio/activity.py`:

```python
def heartbeat(*details: Any) -> None:
    """Send a heartbeat for the current activity."""
    heartbeat_fn = _Context.current().heartbeat
    ...
    heartbeat_fn(*details)
```

`Info` carries `heartbeat_details`, `heartbeat_timeout`, `start_to_close_timeout`, `schedule_to_close_timeout`. Docs: a heartbeat is a ping that the Worker has not crashed and that the Activity is making progress. Custom `*details` are stored and returned to the next attempt if the attempt times out on a missed heartbeat. Cancellation is delivered **on the next heartbeat** — an Activity that never heartbeats cannot be cancelled.

**COSMOS analog (P13).** Daemon liveness is `write_heartbeat` (`cosmos_clock.py:60-85`): every tick, pass **or idle**, writes `last_run_epoch`. Age is `heartbeat_age_s` (compare using epoch, not mtime). P13 [0017]: "Audit: daemon heartbeats (`last_run_epoch`)". Paused clocks still heartbeat `state=PAUSED` (principle P2) so a paused clock is never mistaken for a dead one.

**Not the same object.** Temporal's `*details` are a **progress resume payload** for the next attempt. COSMOS heartbeat JSON is **liveness only**. Progress / carry-over lives in SEED (P11) and the ledger (P07). Do not stuff SEED facts into `*_heartbeat.json` — that would be a competing second handoff.

### 1.2 Start-to-close vs heartbeat timeout

**Source.** Docs + SDK: at least one of `start_to_close_timeout` or `schedule_to_close_timeout` **must** be set on `workflow.execute_activity` (`temporalio/workflow/_activities.py` contract; README of sdk-python).

| Timeout | Meaning in Temporal | COSMOS analog already on disk |
|---|---|---|
| **Start-to-close** | Max time for **one attempt** after a Worker picks the task. Retryable. Detects a Worker that crashed **after start**. | A daemon's `interval_s` + lock: the attempt is one poll. A hung poll is a pid that holds the lock and never returns. |
| **Heartbeat timeout** | Max gap **between successful pings**. Retryable. Detects a Worker that is "running" but silent. | `heartbeat_age_s` vs `stale_s = cadence + slack` (`builds/health/cosmos_health_watchdog.py`). COMPARE USING `last_run_epoch`. |
| **Schedule-to-close** | Overall wall from first schedule through retries. | Work-order runner + collector: the job's age on `/jukebox`, not a Temporal retry policy. |
| **Schedule-to-start** | Time sitting in the task queue before a Worker picks it. Non-retryable. | Queue age of `QUEUED` on GET `/jukebox`. |

The useful **idea**: two clocks, not one. "Did this attempt take too long?" is not "did the ping go silent?" COSMOS already splits them (`interval_s` vs `last_run_epoch` age). Health already treats a fresh heartbeat with `ok=false` / `state=PAUSED` / `core_kind=UNREACHABLE` as **alive-and-honest**, not dead.

**Do not** import Temporal timeout objects, RetryPolicy, or task queues. Pulse, WD2, schtasks, and the work-order runner are the clocks.

### 1.3 Continue-as-new (`workflow.continue_as_new`)

**Source.** `temporalio/workflow/_workflow_ops.py` `continue_as_new(...) -> NoReturn` always raises `ContinueAsNewError` (must not be caught). Sample `hello_continue_as_new.py`:

```python
@workflow.run
async def run(self, iteration: int) -> None:
    if iteration == 10:
        return
    await asyncio.sleep(1)
    workflow.continue_as_new(iteration + 1)
```

Docs: the current run **closes successfully**; a new run starts with the **same Workflow Id**, a **new Run Id**, and a **fresh Event History**. Caller must pass "current state" as the next run's arguments. Trigger: `workflow.info().is_continue_as_new_suggested()` when history approaches limits. Handlers must finish first: `await workflow.wait_condition(workflow.all_handlers_finished)`.

**COSMOS analog (P11).** `SessionKernel.close_session` (`cosmos_session.py:205-271`) writes signed `state/SEED.json` + `SEED.decl.json` (`len`/`sha`/`mac` via install key). `start_session` refuses `NO_SEED` / `BAD_SEED` / `IDENTITY_MISMATCH`. Closing with unresolved watchers is `OPEN_CONTEXT` unless `force=True`. P11 [0003]: absence is an **incident**, not a warning.

| Temporal continue-as-new | COSMOS SEED close |
|---|---|
| Same Workflow Id, new Run Id | Same tree_id, new session sid |
| State is whatever you pass as args | Declared fields: facts, leases/watchers, handoff, incidents |
| History size suggested | Context watermark ~70% / hard close ~90% (P11 [0019]) |
| Missing state = you forgot to pass it | Missing/bad MAC = **OPEN_CONTEXT** / `NO_SEED` — fail-closed |
| `all_handlers_finished` before CAN | Unresolved watchers REFUSE unless force (then ledger `OPEN_CONTEXT`) |
| Not HMAC; Temporal service is the store | Install-key MAC; ledger `SESSION_SEED_WRITTEN` |

The **idea** (checkpoint-and-restart so the OS survives context death) is already P11. Temporal's CAN is a weaker, unsigned cousin. Do not stand a Temporal history store beside the JSONL ledger.

### 1.4 Signal vs query (and update)

**Source.** `temporalio/workflow/_handlers.py` + encyclopedia:

| Primitive | Decorator | Mutates? | Return? | History? | Worker must be up? |
|---|---|---|---|---|---|
| **Query** | `@workflow.query` | **Must not**. Sync `def` (async deprecated). | Yes | **Never** written | Yes (to run the handler) |
| **Signal** | `@workflow.signal` | Yes. Fire-and-forget. Return ignored. | No | `WorkflowExecutionSignaled` | No (server accepts; delivered later) |
| **Update** | `@workflow.update` + optional `.validator` | Yes | Yes | Accepted/completed events. **Rejected validator = no history row.** | Yes (sync until accepted) |

Docs: "Queries can read the current state of the Workflow but cannot block." "Signals are asynchronous write requests." "Updates are synchronous, tracked write requests" with a validator that can reject **before** the write is accepted.

**COSMOS analog (P09 + GET surfaces).**

- **Query ≡ GET.** `/api/v1/spend`, `/jukebox`, `/surfaces`, `/jobs` — projections, no mutation. Studio already paints these. A GET that mutated would be a scar.
- **Signal ≡ fire-and-forget write.** Human-in-the-loop in Temporal is often "signal `approve`." Canon: **CCr `--accept` is the human gate, not a Temporal signal** (`CDECK_PERPLEXITY_STACK.md`). Review pane = FINDINGS + stale RUNNING; no annotation POST. **REFUSE** signal-as-HITL.
- **Update + validator ≡ confirm-to-widen (P09).** Closest match: `POST /api/v1/spend` without `"allow_widen": true` (literal JSON bool) → `409 WIDEN_REQUIRES_CONFIRM`; stored cap **does not move**; then `SPEND_CAP_REFUSED` is **ledgered** (`cosmos_spend_admin.py:303-342`). Temporal's validator rejects **without** writing history. COSMOS is stricter: **the refusal itself is evidence** (P09 [0011]). Keep ours. Do not port Temporal Update.

---

## 2. Langflow — graph JSON, vertex run, editor vs runtime

### 2.1 How a graph is stored

**Source.** `FlowBase.validate_json` (`…/flow/model.py`): `data` must be a dict with **`nodes` and `edges`**. SQLModel `Flow.data: dict | None` as JSON column.

Runtime schema `lfx.graph.graph.schema.GraphData`:

```python
class GraphData(TypedDict):
    nodes: list[NodeData]
    edges: list[EdgeData]
    viewport: NotRequired[ViewPort]
```

`NodeData` (`lfx.graph.vertex.schema`): ReactFlow node — `id`, `data`, `position`, `type` (`genericNode` | `noteNode`). Saved files ship as `{"data": {"nodes": [...], "edges": [...]}}`. `Graph.from_payload(payload)` (`lfx.graph.graph.base.Graph`) accepts either the inner object or the wrapper (`lfx.extension.migration.rewrite` comment). `lfx.load.load.aload_flow_from_json` does `graph_data = flow_graph["data"]` then `Graph.from_payload(graph_data)`.

This is **ReactFlow canvas JSON**, not MOTIF. Authority in Langflow is the DB row (or, in LFX, the file). Authority in COSMOS is the ledger.

### 2.2 How a vertex run is invoked

**Source.**

1. `Graph.build_vertex(vertex_id, …)` / `Graph.astep` in `lfx/graph/graph/base.py` — build one vertex after predecessors fulfill (`RunnableVerticesManager.is_vertex_runnable`).
2. Deprecated editor route `POST /build/{flow_id}/vertices/{vertex_id}` (`langflow/api/v1/chat.py`) — per-node playground.
3. Supported route `POST /build/{flow_id}/flow` — whole-flow job; events polled. Caller-supplied `data` override is **write**, gated; execute-only callers run the **stored** graph.
4. Celery `build_vertex` in `langflow/worker.py` (soft_time_limit=30).
5. Frozen vertices skip rebuild (`vertex.frozen`) unless the vertex is a loop — this is **re-run-from-here / cache**, i.e. time-travel adjacent.

`RunnableVerticesManager` tracks `vertices_to_run`, `vertices_being_run`, `run_predecessors`, `cycle_vertices`. Execution is a DAG (with optional cycles), not an 8-stage SOP.

**COSMOS analog.** MOTIF is a **fixed SOP**, not a user-wired DAG. Studio (`builds/cdeck/ui/deck_studio.js`) hard-codes `STAGES` DEFINE→…→ITERATE and paints heat from GET `/jukebox` queue words. WD2 drives the next stage. There is no `Graph.build_vertex("critics")` that skips DEFINE. Per-step re-run / frozen vertex / fork-from-here stay **out** (`PROFILES.md`, `CDECK_STUDIO.md` "Do not invent").

### 2.3 Is the editor separable from the runtime?

**Yes, in their tree.** `src/lfx` is a **separate package** ("Langflow Executor"):

- `lfx run flow.json "input"` — no UI, stdout.
- `lfx serve flow.json` — FastAPI at `POST /flows/{flow_id}/run`, **NoopSession**, no `langflow.db`.
- Python `Graph(chat_input, chat_output)` without React Flow.
- Frontend (`src/frontend/…/PageComponent`) is `@xyflow/react` canvas; it is not required to execute.

**COSMOS already has this split.** Editor = `cdeck.exe` (Tauri client). Runtime = Core `:8770`. Studio is an extra pane that **GETs Core**, not a graph engine. LFX's "serve the JSON as FastAPI" is a **second API** — REFUSE. The *idea* "the canvas is not the executor" is already the occupancy host vs Core.

Langflow HITL on `lfx run`: checkpoints **in memory**, no durable resume, non-interactive runs skip the pause. Durable pause in COSMOS is `PAUSE.flag` (HOLD never self-clears) + SEED, not a frozen vertex.

---

## 3. Bucket table (one row, one bucket)

Per `DEFINE_OSS_BORROW.md`. **IN COSMOS** = already an organ. **BORROW** = copy a mechanism as our code (not their runtime). **ADAPT** = map onto an existing Core emit / cDeck pane. **LEARN** = encode in docs; do not port. **REFUSE** = second scheduler / API / DB / iframe / time-travel / rotator.

### Temporal

| # | Mechanism (path + symbol) | Bucket | Why |
|---|---|---|---|
| T1 | Temporal **as clock / worker / task queue** (self-host service + `Worker`) | **REFUSE** | Same class as n8n (H2/H8). Pulse, WD2, schtasks, work-order runner already schedule. License-free is not a second Core. |
| T2 | `activity.heartbeat` as **liveness ping** | **IN COSMOS** | `write_heartbeat` → `last_run_epoch` on every tick (P13 [0017]). Paused still pings (P2). |
| T3 | Heartbeat `*details` as **progress resume** for the next attempt | **LEARN** | Progress is SEED + ledger, not heartbeat JSON. Do not merge the two files. |
| T4 | **Start-to-close** vs **heartbeat timeout** (two clocks) | **IN COSMOS** | `interval_s` (attempt) vs `heartbeat_age_s` / `stale_s` (ping). Health already compares epoch. |
| T5 | Cancellation delivered **on heartbeat** | **LEARN** | COSMOS PAUSE is a file the daemon **pulls**. Do not add a server-push cancel channel. |
| T6 | `workflow.continue_as_new` + `ContinueAsNewError` | **IN COSMOS** (organ) + **REFUSE** (runtime) | Organ = P11 SEED close. Runtime = Temporal history store. Missing SEED is an incident; Temporal CAN is unsigned args. |
| T7 | `is_continue_as_new_suggested` / history-size trigger | **IN COSMOS** | P11 [0019] watermark ~70% / hard close ~90%. |
| T8 | `all_handlers_finished` before CAN | **IN COSMOS** | `close_session` REFUSES unresolved watchers unless force → `OPEN_CONTEXT`. |
| T9 | `@workflow.query` (read, no history, no mutate) | **IN COSMOS** | GET `/spend` `/jukebox` `/surfaces`. Studio paints GETs. |
| T10 | `@workflow.signal` as HITL / resume | **REFUSE** | Human gate is CCr `--accept`, not a signal. No annotation POST. |
| T11 | `@workflow.update` + `.validator` reject-before-history | **IN COSMOS** (stricter) | P09 `409 WIDEN_REQUIRES_CONFIRM` + ledgered `SPEND_CAP_REFUSED`. Temporal drops rejected updates from history; we keep the refusal. Do not port Update. |
| T12 | Event-sourced **workflow history as authority** | **REFUSE** | P07: service-signed JSONL is authority. SQLite is a projection. Temporal history is a second event store. |
| T13 | LangGraph + Temporal durable plugin | **REFUSE** | Already out (`PROFILES.md`, `CDECK_PERPLEXITY_STACK.md`). |
| T14 | FastAPI+React Temporal UI replacing `cdeck.exe` | **REFUSE** | Occupancy host is Tauri. One versioned API is Core. |

**BORROW from Temporal: none.** Nothing to copy as our code that is not already an organ.

### Langflow

| # | Mechanism (path + symbol) | Bucket | Why |
|---|---|---|---|
| L1 | LangFlow **embed / React Flow canvas** as the editor | **REFUSE** | Second UI. Extra-pane Studio already exists (`deck_studio.js` STAGES + inspector + heat). Do not iframe a workflow product. |
| L2 | `Flow.data = {nodes, edges, viewport}` as **authority store** | **REFUSE** | DB JSON as source of truth. COSMOS ledger is authority. MOTIF is not a user DAG. |
| L3 | Graph JSON **shape** (`GraphData` / `NodeData`) | **LEARN** | ReactFlow serialization. Studio does not need vertices/edges JSON to paint eight SOP stages. A stored DAG would be a second canvas product. |
| L4 | `Graph.from_payload` + `lfx run` (runtime without editor) | **LEARN** | We already split client (`cdeck.exe`) from runtime (`:8770`). Do not vendor `lfx`. |
| L5 | `lfx serve` FastAPI `/flows/{id}/run` | **REFUSE** | Second API. Core remains `:8770`. |
| L6 | `Graph.build_vertex` / `POST …/vertices/{vertex_id}` | **REFUSE** as re-run-from-step | Time-travel / fork-from-here stay out. MOTIF does not skip DEFINE. |
| L7 | One-stage-at-a-time **driven by a clock** (their DAG layer ≈ our SOP stage) | **IN COSMOS** | WD2 + MOTIF stages. Heat overlay from `/jukebox` already maps "which stage is hot." |
| L8 | `RunnableVerticesManager` predecessor / cycle logic | **LEARN** | MOTIF is linear SOP, not a cycle DAG. Do not port. |
| L9 | `vertex.frozen` / cache skip | **REFUSE** | Time-travel adjacent. |
| L10 | Editor separable from runtime (LFX vs frontend) | **IN COSMOS** | Already the rule: cDeck paints; Core executes. |
| L11 | CLI HITL in-memory checkpoint (`lfx run` Human Input) | **LEARN** | Durable pause is `PAUSE.flag` + SEED, not RAM. |
| L12 | FastAPI+React replacing `cdeck.exe` | **REFUSE** | Explicit. |

**BORROW from Langflow: none.** Graph-JSON / vertex-run do **not** map onto Studio/MOTIF without a second canvas. ADAPT already done for extra panes (LangSmith heat, n8n runs list) — that steal is not this ticket.

---

## 4. Map onto P09 / P11 / P13 (the three named organs)

| Docket | COSMOS organ | Temporal lookalike | Verdict |
|---|---|---|---|
| **P13** last_run_epoch heartbeat | `write_heartbeat` every tick; age vs cadence; paused still pings | `activity.heartbeat` + heartbeat_timeout | **IN COSMOS.** Keep epoch, not Temporal details-payload. |
| **P11** SEED close | HMAC `SEED.json` + `SEED.decl.json`; `NO_SEED`/`BAD_SEED`/`IDENTITY_MISMATCH`; OPEN_CONTEXT | `continue_as_new` (same id, fresh history, pass state) | **IN COSMOS**, stricter. Temporal CAN is not fail-closed. |
| **P09** spend 409 confirm | `allow_widen: true` literal; 409 leaves cap; `SPEND_CAP_REFUSED` ledgered | `@update` validator reject-before-history; query vs signal | **IN COSMOS**, stricter (refusal is evidence). Signal-HITL **REFUSE**. Query=GET **IN COSMOS**. |

No hole that requires standing Temporal or Langflow. The "heartbeat that is authority / wait-node that does not poll the LLM / human-input that persists" organs named in `DEFINE_OSS_BORROW.md` are **already Core**.

---

## 5. What this ticket will not BUILD

- No Temporal cluster, SDK worker, or schedule.
- No Langflow / LFX / React Flow canvas / iframe.
- No FastAPI second API, no React+Vite replacing `cdeck.exe`.
- No MOTIF-as-DAG, no vertex-run-from-here, no frozen-vertex cache.
- No BORROW PR. No ADAPT that is not already in extra-pane Studio.

If a later MOTIF iteration wants a **doc-only** note in `docs/` (T3 heartbeat-details vs SEED; T11 refusal-is-evidence vs Temporal silent reject), that is LEARN — CCr encodes canon, it is not a runtime change.

## 6. Proof this is RESEARCH, not a run

- Temporal was **not** started. No `localhost:7233`. Ideas extracted from SDK + docs that quote the SDK.
- Langflow was **not** installed or served. Graph/vertex/editor split extracted from pinned SHA.
- Core `:8770` and `cdeck.exe` were not modified.
- Return path: `work_orders/ccr/CREW/OUT/OSS/R_TEMPORAL_LANGFLOW.md`.
