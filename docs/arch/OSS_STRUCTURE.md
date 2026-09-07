# OSS architecture / routines / tools / snippets — what COSMOS can use

**Keith 2026-09-07:** besides layout, check architecture, routines, tools,
code snippets, external calls and structure for COSMOS **or any component
or ancillary**.

**DEFINE:** `DEFINE_OSS_BORROW.md` + `DEFINE_OSS_CDECK_UX.md`.
**Source reads:** `CREW/OUT/OSS/R_LANGGRAPH.md`, `R_N8N_DIFY.md`,
`R_TEMPORAL_LANGFLOW.md`. **CONSENSUS:** packages **BORROW none**.

This file is the **structure** pass: not chrome, not “import Temporal.”
Each row names the **COSMOS organ or ancillary** it maps onto.

## Architecture (shape)

| Their structure | COSMOS / ancillary | Use |
|---|---|---|
| **Editor ≠ executor** (LangFlow `lfx` vs frontend; cDeck vs Core already) | `cdeck.exe` client · Core `:8770` runtime | **IN COSMOS.** Do not `lfx serve`. |
| **Query / Signal / Update** (Temporal handlers) | GET = query (no mutate). Drop/POST jobs = signal. Spend `allow_widen` + 409 = update+validator, **and we ledger the refusal** | **IN COSMOS** (P09 stricter). **REFUSE** signal-as-HITL (annotation POST). |
| **Continue-as-new** (same Workflow Id, new Run Id, pass state as args) | SEED close: same `tree_id`, new `sid`, HMAC fields | **IN COSMOS** (P11). Ours is fail-closed. |
| **SOP vs user DAG** (LangFlow vertices vs MOTIF stages) | MOTIF 9-stage is the SOP. Studio paints it; WD2 drives it | **LEARN.** Do not replace MOTIF with a wired DAG. |
| **First durable write before side effect** (LangGraph `put` before the run is “accepted”; crash-before-put = 0 rows) | `pickup_order` files `picked/` **off ledger** | **ADAPT — next Core BUILD:** `WORK_ORDER_PICKED` via Core (daemon does not open the JSONL). |
| **Park the process; LLM is not the waiter** (n8n `putExecutionToWait`) | Drop ingest + work-order runner + 15s clock | **IN COSMOS** (P13). |
| **Two clocks** (start-to-close vs heartbeat; run vs idle) | Job timeout BROKE vs `stale_flag` / `heartbeat_age_s` | **IN COSMOS.** Painters must not list stale as in-flight. |
| **Idempotent resume token** (n8n timing-safe `resumeToken`) | Named `order_id` + CCr `--accept`. GitHub drop is the URL analog | **ADAPT** (cDeck Review already names `--accept` / drop). Do not mint public webhooks. |

## Routines (call order)

| Routine | Steal the *order*, not the code | Where it lives |
|---|---|---|
| `interrupt()` then persist then return payload | Pause **after** a durable record | HITL: FINDINGS only after a ledger/heartbeat exists (P04). Hole: pickup. |
| `Command(resume=)` as a **named write**, not re-invoke empty | `--accept order_id` | `cosmos_work_order.accept_order` |
| `putExecutionToWait` then **exit** | Long wait = disk, not `setTimeout` in Core | `cosmos_sgh_drop_ingest` / runner `spawn_detached` |
| `heartbeat(*details)` vs liveness JSON | Heartbeat files stay **liveness only**; progress in SEED/ledger | `cosmos_clock.write_heartbeat` · do not stuff SEED into `*_heartbeat.json` |
| Validator **before** history row (Temporal Update) | Confirm-to-widen: 409 then `SPEND_CAP_REFUSED` | `cosmos_spend_admin` — keep ours (refusal **is** history) |
| `continue_as_new` after handlers finished | Close SEED only with watchers resolved or `OPEN_CONTEXT` | `cosmos_session.close_session` |
| Vertex `build` only when predecessors ready | Dual-lane: BUILD after DEFINE+RESEARCH on disk | MOTIF · Gitur |
| Wait <65s in-process vs ≥65s persist | 15s clock is the short waiter; drop is the long one | Do not add a second in-process wait loop |

## Tools (hands, not a second OS)

| Tool idea | COSMOS / ancillary | Use |
|---|---|---|
| MCP as **tool surface** (LangGraph starter kits, ForgeFlow) | OpenWork MCP + COSMOS rails. `cosmos_mcp` is the **server** face | **ADAPT:** consume MCP; do not replace rails with MCP Filesystem/Git (already REJECT). |
| Typed external HTTP failures | DOM/API: `UNREACHABLE` / `AUTH_REQUIRED` / `BROKE` | **IN COSMOS** (P08). |
| Named model pin, no rotator | `cosmos_openrouter_rail.model_refused` | **IN COSMOS.** ChatBot picker. |
| GitHub as reachable inbox | `work_orders/drop/` · `gh` CLI | **IN COSMOS** (P13). Gitur **projects** rails; does not poll vendor PR APIs. |
| Content-addressed blobs | filename = hash; ledger holds pointer | **IN COSMOS** (P07). Closer to Postgres `checkpoint_blobs` than Sqlite inline BLOB. |
| Timing-safe compare on resume tokens | Bearer / kill_token / spend confirm | **LEARN** for any new resume surface. Do not copy n8n webhook HMAC as a second inbox. |

## Code-snippet *shapes* (rewrite, do not paste their trees)

n8n is fair-source; we do not copy. These are **orders of operations** for our modules:

1. **Pickup then ledger then spawn** (LangGraph first-`put`):
   `pickup_order` → Core `WORK_ORDER_PICKED` → `spawn_detached`. Today the middle step is missing. Ancillary: `cosmos_work_order_run.process_one`.
2. **GET never mutates** (Temporal query): every extra-pane poll is GET. Writes are explicit POST and print Core’s answer (pane-fns).
3. **Idle vs wall** (TimeoutPolicy / activity timeouts): `running_s > 30m` → `stale_flag`; job `timeout_s` → BROKE. Clock pane: PAUSED still writes heartbeat (`state=PAUSED`).
4. **Filter census** (operator honesty): Gitur `kept N · dropped M`. Apply the same shape anywhere a list is filtered (Runs already filters by chip).
5. **HITL payload is the command we have** (`interrupt.value`): FINDINGS inspector. Extra notes UNMEASURED.

## External calls (who talks to whom)

| Call | Their use | COSMOS |
|---|---|---|
| LLM HTTP | LangGraph node / LangFlow vertex / Dify LLM node | Named rails (`sgh-api`, `openrouter-api`, Vertex). Bind `response.model`. |
| Webhook resume | n8n Wait | GitHub drop + Drive return. Phone/terminal mouths. **Not** a public `$execution.resumeUrl`. |
| Celery / Temporal worker | Dify resume, Temporal activity | Windows schtasks + pythonw. **REFUSE** Celery/Temporal workers. |
| Postgres / SQLite as run store | checkpointers, LangFlow Flow.data | Ledger JSONL. SQLite projection only. |
| ReactFlow POST `/build/.../vertices/{id}` | per-node playground | Studio GET `/jukebox` heat. No per-stage POST that skips DEFINE. |
| OpenRouter `/models` | rate card | `cosmos_model_rater` · Prompts tab. |

## Ancillaries (where a pattern may land)

| Ancillary | What it can take | What it must not |
|---|---|---|
| **Work-order runner** | After pickup, notify Core (HTTP) so pickup is ledgery | Open `live/ledger/` itself |
| **SGH drop ingest** | Already park-without-spin; keep GitHub objects | Auto-retry 2–5 like n8n `getRetryParams` |
| **Health watchdog** | Two-clock compare (`last_run_epoch` vs cadence) | Treat PAUSED as dead |
| **cDeck extra panes** | Wait tooltip, HITL line, kept/dropped (PR #33) | Annotation POST, time-travel, retry button as re-run |
| **ChatBot phone / terminal** | Same drop as resume URL; adversarial N seats (P05) | Mount `live/`; rotator |
| **Gitur** | Projection of three legs; filter census | Vendor PR poll |
| **OpenRouter rail** | Named pin; refuse rotator | `openrouter/free` |
| **Spend admin** | Update+validator; ledger the 409 | Silent widen |
| **Session / SEED** | Continue-as-new with HMAC | Unsigned history store |

## Still refuse

Their runtimes. DAG as MOTIF. Frozen-vertex re-run. `source: "fork"`. Public resume URLs. Celery. `lfx serve`. FastAPI replacing `:8770`. Auto-retry. `waiting`/`PAUSED` as `OUTCOMES`.

## Next BUILD (Core, Gitur)

`WORK_ORDER_PICKED`: runner POSTs Core after `pickup_order` (idempotent on `order_id`). Core is the ledger writer. DONE remains Output exists. Crash-after-pickup without Output is a named incident, not silence.
