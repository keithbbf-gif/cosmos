# R_N8N_DIFY — MOTIF stage-1 RESEARCH (wait / pause / resume / execution list)

**Stream:** Cm OSS-borrow (`DEFINE_OSS_BORROW.md`). Not BUILD. Not a vendor-in.
**Date of this return:** 2026-09-07.
**Sources (HEAD at fetch):**
- `n8n-io/n8n` SHA `b5072af998f1a6162ffba863553304fa989d6580`
- `langgenius/dify` SHA `0df092d3c7c6954b515c28f388449a9644d1390f`

**Hard rulings already on disk (this file does not reopen them):**
- n8n **as scheduler** = **REJECT** (H2/H8). `docs/arch/meshadditions_ARCH.md` row 20; `work_orders/ccr/CDECK_PERPLEXITY_STACK.md`.
- Do **not** embed n8n or Dify. Do **not** stand Postgres / Celery / graphon as authority.
- Human gate in COSMOS is **CCr one pen**, not a Temporal/n8n/Dify signal. Review = FINDINGS + stale RUNNING from `GET /api/v1/jukebox`. Dispose is CCr. No annotation POST.

This return extracts **wait-node / pause / resume / execution-list mechanisms** that can be **ADAPTED onto `/jukebox`** without running n8n or Dify.

Bucket vocabulary (`DEFINE_OSS_BORROW.md`): **IN COSMOS · BORROW · ADAPT · LEARN · REFUSE**. One bucket per row.

Live Core paint this maps onto (measured 2026-09-07, `CDECK_PANE_FNS.md`):
`GET /api/v1/jukebox` → `QUEUED · RUNNING · BROKE · CLEAN · FINDINGS` (+ `stale_flagged`). Scheduler words in `cosmos/cosmos_sched.py`: `OUTCOMES = {CLEAN, FINDINGS, BROKE}`; report-never-retry.

---

## 0. How a human wait works in each tree (one paragraph each)

**n8n.** A Wait / sendAndWait / Form node calls `IExecuteFunctions.putExecutionToWait(waitTill)`. That writes `runExecutionData.waitTill` and `setExecutionStatus('waiting')`. The process **exits**. The execution row stays `waiting` in the DB (not `running`, not terminal). Resume is **not** an LLM poll: either `WaitTracker` (leader, 60s DB query + `setTimeout`) fires at `waitTill`, or `WaitingWebhooks.executeWebhook` receives a signed URL (`resumeToken` timing-safe compare, or HMAC for send-and-wait `approved=`). Resume **disables** the wait node so it cannot wait again, clears `waitTill`, re-runs the persisted `nodeExecutionStack`. Short waits `< 65000 ms` cheat: in-process `setTimeout` because the tracker only polls every 60s.

**Dify.** A Human Input node does not loop the LLM. `DifyHITLCallback.__call__` creates a persisted form (`HumanInputFormStatus.WAITING`) and returns `PauseRequested`. Graphon emits `NodeRunPauseRequestedEvent` then `GraphRunPausedEvent`. Persistence sets `WorkflowExecutionStatus.PAUSED` and dumps `WorkflowResumptionContext` (serialized graph runtime state + generate entity). The engine thread **ends**. A human submits via token (`HumanInputService.submit_form_by_token` → `mark_submitted` → `enqueue_resume` → Celery `resume_app_execution`). Resume loads the pause entity (`resumed_at is None`), rebuilds `GraphRuntimeState.from_snapshot`, continues with `WorkflowStartReason.RESUMPTION`. Node-level timeout resumes on handle `__timeout`; global timeout is **not** a resume (AssertionError / form EXPIRED).

**COSMOS already.** The LLM is not the clock (P13: "The LLM does not poll itself"). Work parks as a ledger-projected job: SUBMITTED→QUEUED, CLAIMED→RUNNING, DONE→`CLEAN|FINDINGS|BROKE`. A human gate is FINDINGS (checker found something; not BROKE) or stale RUNNING (flag, never auto-rerun). Resume is a **new** drop / CCr `--accept`, not a snapshot replay. `SEED.json` is session carry-over, not a graph snapshot.

---

## 1. n8n — file paths + symbols (execution layer, not the visual editor)

### 1.1 Wait node

| Path | Symbols |
|---|---|
| `packages/nodes-base/nodes/Wait/Wait.node.ts` | `class Wait extends Webhook`; `execute`; `configureAndPutToWait`; `putToWait`; resume modes `'timeInterval' \| 'specificTime' \| 'webhook' \| 'form'` |
| `packages/workflow/src/constants.ts` | `WAIT_INDEFINITELY = new Date('3000-01-01T00:00:00.000Z')` |
| `packages/core/src/execution-engine/node-execution-context/base-execute-context.ts` | `BaseExecuteContext.putExecutionToWait(waitTill)` — sets `runExecutionData.waitTill` + `setExecutionStatus('waiting')` |
| `packages/workflow/src/interfaces.ts` | `putExecutionToWait(waitTill: Date): Promise<void>` |

Human wait (webhook/form): `configureAndPutToWait` defaults `waitTill = WAIT_INDEFINITELY` unless `limitWaitTime`. Resume URL is generated at runtime (`$execution.resumeUrl` / `$execution.resumeFormUrl`) and stuffed into `setMetadata`. **No LLM is in this path.**

Time wait: if remaining `< 65000` ms, in-process `setTimeout` + `onExecutionCancellation`; else `putToWait`. Comment in source: *"we just check the database every 60 seconds."*

### 1.2 Execution status machine

| Path | Symbols |
|---|---|
| `packages/workflow/src/execution-status.ts` | `ExecutionStatusList`; `ExecutionStatus`; `CompletedExecutionStatus`; `TerminalExecutionStatus`; `CRASHABLE_EXECUTION_STATUSES`; `isCompletedExecutionStatus`; `isTerminalExecutionStatus` |
| `packages/core/src/execution-engine/workflow-execute.ts` | `class WorkflowExecute`; `status: ExecutionStatus = 'new'`; `run` sets `'running'`; `handleWaitingState`; `getRetryParams`; `continuesOnError`; `rethrowLastNodeError`; `handleDisabledNode` |
| `packages/cli/src/execution-lifecycle/execution-lifecycle-hooks.ts` | `hookFunctionsWorkflowEvents` (skips post-execute emit when `runData.status === 'waiting'`; emits `execution-waiting` if `latestTask.metadata.resumeUrl`); `hookFunctionsPush` sends `executionWaiting` vs `executionFinished`; `hookFunctionsSave` **never discards** a run that has `waitTill` |

Status words (closed set): `'canceled' | 'crashed' | 'error' | 'new' | 'running' | 'success' | 'unknown' | 'waiting'`.

**`waiting` is deliberately not crashable** (`CRASHABLE_EXECUTION_STATUSES = ['new','running','unknown']`) so recovery cannot mark a paused run as crashed. **`waiting` is not terminal.** A `waiting` execution has `stoppedAt` set (current run stopped) — OpenAPI note in `packages/@n8n/api-types/src/dto/executions/execution-public.openapi.ts`.

Resume of a waiting execution: `WorkflowExecute.handleWaitingState` unsets `waitTill`, **disables** the wait node on the stack (so it does not wait again), **pops** the last run of that node. Disabled-node pass-through in `handleDisabledNode(..., forwardAllOutputs)` is how webhook output branches survive resume (issue 12823 comment).

### 1.3 Human resume without LLM polling

| Path | Symbols |
|---|---|
| `packages/cli/src/webhooks/waiting-webhooks.ts` | `class WaitingWebhooks`; `executeWebhook`; `validateToken` (timing-safe); `validateSignature` (HMAC for send-and-wait); `disableNode`; `getWebhookExecutionData`; `emitExecutionResumedEvent` (`resumeSource: 'webhook'`) |
| `packages/cli/src/wait-tracker.ts` | `class WaitTracker`; `startTracking` (`setInterval(..., 60000)`); `getWaitingExecutions`; `startExecution`; `resumeParentExecution`; `withRetry`; `expectedStatus: 'waiting'`; `ExecutionAlreadyResumingError` |
| `packages/cli/src/webhooks/waiting-forms.ts` | form-waiting endpoint (`WAITING_FORMS_EXECUTION_STATUS`) |
| sendAndWait ops | e.g. `packages/nodes-base/nodes/EmailSend/v2/sendAndWait.operation.ts` — `configureWaitTillDate` + `putExecutionToWait` |

Resume claim: `workflowRunner.run(..., { executionId, expectedStatus: 'waiting' })`. Duplicate resume → `ExecutionAlreadyResumingError` (lost-claim analog). Parent-of-waiting-child is itself put to `WAIT_INDEFINITELY` so `WaitTracker` does **not** wake the parent at the child's `waitTill` (`BaseExecuteContext.executeWorkflow`).

### 1.4 Retry / error at execution layer (not the editor)

| Path | Symbols |
|---|---|
| `packages/core/src/execution-engine/workflow-execute.ts` | `getRetryParams` → `[maxTries, waitBetweenTries]`; clamp `maxTries` to `[2,5]` default 3; `waitBetweenTries` to `[0,5000]` default 1000; **skipped** if `metadata.resumeError` (sub-workflow already failed); `continuesOnError` (`continueOnFail` or `onError ∈ {continueRegularOutput, continueErrorOutput}`); `handleNodeErrorOutput` |
| `packages/cli/src/execution-lifecycle/execution-lifecycle-hooks.ts` | `executeErrorWorkflow` on non-success **except** `waiting`; `requireNotCanceled: true` so a completed worker cannot overwrite user-cancel |
| `packages/cli/src/wait-tracker.ts` | parent-resume retry: `MAX_PARENT_RESUME_ATTEMPTS = 3`; exponential backoff `100 * 2**(attempt-1)`; do not retry `UserError` / `UnexpectedError` |

This is **node-local auto-retry**, not a second scheduler. It is still auto-rerun. COSMOS `cosmos_sched` is report-never-retry.

### 1.5 Execution list (queue fold analog)

CLI filter (`packages/@n8n/cli/src/commands/execution/list.ts`): `--status canceled|error|running|success|waiting`. Public API documents `waiting` as a first-class list word. Editor utils (`packages/frontend/editor-ui/src/features/execution/executions/executions.utils.ts`) refuse retry of a `waiting` execution with an info toast — **waiting is not retry**.

---

## 2. Dify — file paths + symbols

### 2.1 HumanInput node (runtime, not `web/.../node.tsx`)

The React `HumanInputNode` under `web/app/components/workflow/...` is the **canvas**. Runtime is Python + graphon HITL callback.

| Path | Symbols |
|---|---|
| `api/core/workflow/nodes/human_input/entities.py` | `HumanInputNodeData` (`type = BuiltinNodeTypes.HUMAN_INPUT`); `FormInputConfig`; `UserActionConfig`; `expiration_time`; `validate_human_input_submission` |
| `api/core/workflow/nodes/human_input/enums.py` | `HumanInputFormStatus`: `WAITING`, `EXPIRED`, `SUBMITTED`, `TIMEOUT`; `HumanInputFormKind.RUNTIME` |
| `api/core/workflow/nodes/human_input/pause_reason.py` | `DifyHITLEventType.HUMAN_INPUT_REQUIRED`; `HumanInputRequired` (form_id, inputs, actions, node_id, `resolved_default_values`); `PauseReason = HumanInputRequired \| SchedulingPause` |
| `api/core/workflow/nodes/human_input/callback.py` | `class DifyHITLCallback`; `__call__(ctx: HITLContext) -> HITLDecision`; returns `PauseRequested` / `Completed` / `Expired`; `_TIMEOUT_HANDLE = "__timeout"` |
| `api/core/workflow/node_runtime.py` | `class DifyHumanInputNodeRuntime`; `create_form`; `build_form_repository` → `HumanInputFormRepositoryImpl` |
| `api/core/workflow/nodes/human_input/__init__.py` | re-exports |

`DifyHITLCallback` contract (quoted from source): *only explicit node timeout resumes along the timeout handle, while global expiration is treated as an invalid resume state.*

If no form: `_create_form` then `PauseRequested(session_id=...)`. If form exists but not `submitted`: return `PauseRequested` again (idempotent pause). If `TIMEOUT` or past node deadline: `Expired(selected_handle="__timeout")`. If `EXPIRED` or past global deadline while still WAITING: **AssertionError** (do not resume). If submitted: `Completed(selected_handle=selected_action_id, outputs=...)`.

### 2.2 Pause event + persisted paused state

| Path | Symbols |
|---|---|
| `api/core/app/workflow/layers/persistence.py` | `WorkflowPersistenceLayer.on_event`; `GraphRunPausedEvent` → `_handle_graph_run_paused` sets `execution.status = WorkflowExecutionStatus.PAUSED` (`update_finished=False`); `NodeRunPauseRequestedEvent` → node status `WorkflowNodeExecutionStatus.PAUSED`; `NodeRunRetryEvent` → `WorkflowNodeExecutionStatus.RETRY` + retry history |
| `api/core/app/layers/pause_state_persist_layer.py` | `WorkflowResumptionContext` (`version="1"`, `generate_entity`, `serialized_graph_runtime_state`, `serialized_response_stream_filter_state`); `PauseStatePersistenceLayer.on_event` on `GraphRunPausedEvent` → `repo.create_workflow_pause(...)`; `enrich_graph_pause_reasons` |
| `api/repositories/entities/workflow_pause.py` | `WorkflowPauseEntity` protocol: `get_state()`, `resumed_at`, `paused_at`, `get_pause_reasons()`; **never reused** — a second pause creates a new record |

Graph-level status (persisted, not a UI paint): `SUCCEEDED | PARTIAL_SUCCEEDED | FAILED | STOPPED | PAUSED`. Node-level: `RUNNING | RETRY | SUCCEEDED | FAILED | EXCEPTION | PAUSED`.

### 2.3 Resume (human submit → engine, not LLM)

| Path | Symbols |
|---|---|
| `api/services/human_input_service.py` | `HumanInputService.submit_form_by_token`; `ensure_form_active`; `mark_submitted`; `enqueue_resume`; `enqueue_agent_app_resume`; `_load_variable_pool_for_form` (loads pause entity **only if** `resumed_at is None`) |
| `api/tasks/app_generate/workflow_execute_task.py` | `@shared_task ... resume_app_execution`; `_resume_app_execution`; `WorkflowStartReason.RESUMPTION` |
| `api/services/workflow_run_service.py` | pause details API: `if pause_record.status != WorkflowExecutionStatus.PAUSED` → empty `paused_nodes` |
| `api/core/workflow/nodes/agent_v2/ask_human_hitl.py` | `ask_human_args_to_node_data` — agent-tool synthesizes a Human Input form |

Submit is a **write to the form row** then a **background enqueue**. The LLM is not waiting on a socket. Duplicate submit: `FormSubmittedError` HTTP 412. Expired: `FormExpiredError` 412.

**Do not confuse with LLM polling.** `DifyPreparedPollingLLM.start_llm_polling` / `check_llm_polling` in the same `node_runtime.py` is a **model** poll (provider async generation). That is the opposite organ from HITL pause.

---

## 3. Bucket table (one row = one mechanism)

### 3.1 n8n

| # | Mechanism (symbol) | Bucket | Why vs COSMOS Core |
|---|---|---|---|
| N1 | n8n process as scheduler / workflow OS | **REFUSE** | H2/H8. Core already is Pulse + WD2 + schtasks + work-order runner. Standing n8n is a second Core. |
| N2 | Wait node visual editor / canvas | **REFUSE** | Editor. Extra-pane steal maps onto live Core + `cdeck.exe`, not an iframe. |
| N3 | `putExecutionToWait` + persist `waitTill` + status `waiting`; process exits; LLM not in the loop | **IN COSMOS** (as organ) / **ADAPT** (as word) | Organ already exists: job parks in the ledger; runner is OS clock; LLM does not poll (P13). The **word** `waiting` is not a jukebox emit. Map: human-needed = `FINDINGS`; clock-parked = `QUEUED`; in-flight = `RUNNING`. Do not add a sixth jukebox chip unless the ledger grows a real `JOB_PAUSED` event. |
| N4 | Resume via signed webhook (`WaitingWebhooks.validateToken` / HMAC `validateSignature`) | **ADAPT** | Idea: resume is an **ingress event**, not a chat poll. COSMOS ingress is P13 drop box (`work_orders/drop/`) + CCr `--accept`. Do **not** open a public resume URL on `:8770`. Token analog already: drop SHA seen-set + `CCR.lease`. |
| N5 | `WaitTracker` 60s DB poll + in-memory `setTimeout` | **LEARN** | Same shape as schtasks + WD2 15s. Do not port their tracker. Their 65s in-process cheat is a process-bound clock; COSMOS forbids that (Windows clock carries overhead). |
| N6 | Short-wait in-process `setTimeout` (`Wait.execute` `< 65000`) | **REFUSE** | Ties wait to a live process. A Core bounce would lose it. OS clock or ledger `waitTill`-equivalent only. |
| N7 | `WAIT_INDEFINITELY = Date('3000-01-01')` sentinel | **REFUSE** | Sentinel-date as "forever" is a scar waiting to fire. COSMOS: omit the deadline, or a typed HOLD (does not self-clear). Resume-gate `auto_resume_at` is the only self-clear pause (`docs/PAUSE_PROTOCOL.md`). |
| N8 | Execution status set `{new,running,waiting,success,error,crashed,canceled,unknown}` | **ADAPT** | Fold onto existing jukebox words. Suggested map (do not invent chips): `new`→QUEUED; `running`→RUNNING; `waiting`→FINDINGS if human, else QUEUED (parked); `success`→CLEAN; `error`/`crashed`→BROKE; `canceled`→BROKE or a future HOLD (not today); `unknown`→UNMEASURED paint, never a job state. |
| N9 | `waiting` excluded from crash-recovery (`CRASHABLE_EXECUTION_STATUSES`) | **LEARN** | Same instinct as COSMOS: a parked/human job is not a crash. Encode in docs: do not let a Core restart rewrite FINDINGS/QUEUED into BROKE. |
| N10 | Disable wait-node on resume + pop last run (`handleWaitingState`) | **ADAPT** | "Resume must not re-enter the wait." COSMOS analog: claim is one-shot (`JOB_CLAIMED` only from QUEUED; `LOST_CLAIM`). A FINDINGS job is not re-CLAIMED by the same worker; CCr dispose / a **new** job_id (`CDECK_PANE_FNS.md`: "file NEW job… not a retry of the same id"). |
| N11 | `expectedStatus: 'waiting'` + `ExecutionAlreadyResumingError` | **ADAPT** | Lost-claim for resume. If two mouths hit the same paused job, one wins. Already true of `Scheduler.claim`. Do not add a second claim path. |
| N12 | Execution **list** with `waiting` as a first-class filter | **ADAPT** | Review pane already = FINDINGS + stale RUNNING (`CDECK_PANE_FNS.md` item 5). That **is** the waiting list. Do not add a `waiting` filter that Core does not emit. Heat overlay already maps RUNNING→BUILD, FINDINGS→CRITICS, BROKE→IMPROVE. |
| N13 | Refuse retry of a `waiting` execution (editor toast + engine) | **IN COSMOS** | `cosmos_jukebox_panel.py`: no cancel/hold/retry button because `cosmos_sched` has no such verb. A jukebox retry of FINDINGS would be a lie with a border. |
| N14 | Node `retryOnFail` / `maxTries` auto-rerun | **REFUSE** | Conflicts with report-never-retry (`JOB_STALE` is a flag). A BROKE job is not re-run by Core. Human/CCr files a **new** job. |
| N15 | `continueOnFail` / `onError: continueErrorOutput` (error as data on a side branch) | **LEARN** | Closest COSMOS word is FINDINGS (checker found something; job is not BROKE). Do not port error-output sockets. |
| N16 | `executeErrorWorkflow` on failure | **LEARN** | A BROKE job can enqueue a **new** work order (Gitur / drop). Do not nest a second workflow engine. |
| N17 | sendAndWait (Slack/email/Teams approval URL) | **LEARN** | Mouths already: P13 drop, ChatBot phone, CCr. Do not add Slack-as-authority. HMAC-on-query (`approved=true`) is the right instinct if a URL mouth is ever named — still not this tick. |
| N18 | Parent execution waits indefinitely for child; tracker must not double-wake | **LEARN** | COSMOS has no nested execution engine. Occupancy (P05) is N isolated proposers + one disposer, not parent/child runs. |
| N19 | `resumeToken` stored on execution data; old rows without token skip validation (back-compat hole) | **LEARN** | Fail-closed: a resume without a token should refuse, not skip. COSMOS drop ingest already fail-closed on parse. |
| N20 | Persist `pushRef` on waiting manual runs so the UI reconnects | **REFUSE** | Editor session. cDeck polls `GET /jukebox`; no WS execution channel. |

### 3.2 Dify

| # | Mechanism (symbol) | Bucket | Why vs COSMOS Core |
|---|---|---|---|
| D1 | Embed Dify / graphon / SQL pause tables / Celery `resume_app_execution` | **REFUSE** | Second OS. Postgres as run/state authority already DO NOT (`CDECK_PERPLEXITY_STACK.md`). Celery is a second clock. |
| D2 | Visual `HumanInputNode` canvas (`web/app/components/workflow/...`) | **REFUSE** | Editor. Studio extra-pane is the steal, painted from Core. |
| D3 | Human Input pauses the **engine** and returns; LLM is not polled (`DifyHITLCallback` → `PauseRequested`) | **IN COSMOS** | P13 + CCr. The organ is: typed work parks; OS daemon lists; human/CCr resumes. Dify proves the same split in another tree. No port required. |
| D4 | `HumanInputRequired` pause reason (form_id, node_id, actions, resolved defaults) as a **typed event** | **ADAPT** | If `/jukebox` Review needs "why is this FINDINGS", carry the reason on the **ledger event** (already payload), not a form table. Do not invent a HumanInput node type in Core. |
| D5 | Persist full `WorkflowResumptionContext` / `GraphRuntimeState.dumps()` snapshot | **REFUSE** | Time-travel / invented traces stay out (`PROFILES.md`). Carry-over is HMAC `SEED.json` (P11), not a graph snapshot. A paused MOTIF stage is the **wishlist/backlog + SEED**, not a pickled engine. |
| D6 | `WorkflowPauseEntity` append-only (never reused; new row per pause) | **LEARN** | Matches ledger instinct (append events; do not mutate a pause row as authority). Their SQL row is still a second store. Ours: append `JOB_*` to `sched_ledger.jsonl`. |
| D7 | `WorkflowExecutionStatus.PAUSED` as a first-class run status | **ADAPT** | Do **not** add PAUSED to `OUTCOMES`. FINDINGS is the human-needed outcome; HOLD is the TidyUP pause (`PAUSE_PROTOCOL.md` — never self-clears). If a job must park mid-run for CCr, that is FINDINGS or a **new** QUEUED follow-on, not a snapshot. |
| D8 | Form status `WAITING/SUBMITTED/TIMEOUT/EXPIRED` | **ADAPT** | Map onto work-order + jukebox: WAITING→QUEUED or FINDINGS (if human must act); SUBMITTED→RUNNING then CLEAN/FINDINGS/BROKE; TIMEOUT→stale_flagged RUNNING (flag, not auto-resume); EXPIRED→BROKE or HOLD. Node-timeout-as-success-along-`__timeout` is **not** COSMOS (that would auto-continue past the human). |
| D9 | Node timeout vs global expiration split (`DifyHITLCallback`) | **LEARN** | Resume-gate (`auto_resume_at`) vs HOLD (never self-clears) is the COSMOS split. Do not port two SQL deadlines. |
| D10 | `submit_form_by_token` → `mark_submitted` → `enqueue_resume` (Celery) | **ADAPT** | Replace Celery with **schtasks + work-order runner**. Submit analog: drop JSON / CCr `--accept`. Duplicate submit = 412 analog of `LOST_CLAIM` / `FormSubmittedError`. |
| D11 | `HumanInputFormRepository` as form authority | **REFUSE** | Ledger is authority. A form row is a projection at best. P13 drop files stay; seen-set is not authority. |
| D12 | Idempotent re-pause (`PauseRequested` if form exists and not submitted) | **IN COSMOS** | Re-reading a FINDINGS job does not re-run it. Projection fold is the truth. |
| D13 | Agent v2 `ask_human` synthesizing a Human Input form | **LEARN** | Occupancy (P05) already has the human as disposer, not as an agent tool. Do not add ask_human to Core. |
| D14 | `DifyPreparedPollingLLM` start/check polling | **REFUSE** | LLM polling. Opposite of this research. Vendor async generation is a rail concern, not a wait-node. |
| D15 | Pause-details API (`paused_nodes`, `pause_type: human_input`) | **ADAPT** | Review pane detail: show FINDINGS payload + stale RUNNING age. Do not add `paused_nodes[]` unless Core emits it. UNMEASURED if missing. |
| D16 | Email / webapp delivery of the form (`delivery_methods`, `display_in_ui`) | **LEARN** | Mouths: phone ChatBot, drop, CCr. Delivery is P13, not Dify channels. |
| D17 | `NodeRunRetryEvent` + retry history in `process_data` | **REFUSE** | Same as N14. Report-never-retry. History of retries is a trace we do not invent. |

---

## 4. What to actually do on `/jukebox` (ADAPT list, no n8n process)

These are the only MOTIF-stage-2 candidates. Each must paint a value only live Core or live cDeck can emit (P04). Exit code is not done.

1. **Review = waiting list.** Keep Review as FINDINGS + `stale_flagged` RUNNING. Label the pane in copy as the human-wait list (n8n `waiting`, Dify `PAUSED`) **without** adding those words to `OUTCOMES`. Live emit: `GET /api/v1/jukebox` counts already measured (FINDINGS 4, stale_flagged 1 on 2026-09-07).
2. **No retry button on FINDINGS / stale RUNNING.** n8n already refuses retry of `waiting`. COSMOS already has no retry verb. Pin it if the pane grows a button.
3. **Resume is a new job or CCr dispose, never a snapshot.** Dify's `WorkflowResumptionContext` is the anti-pattern. P13 drop / CCr `--accept` / `POST /api/v1/jobs` with a **new** `job_id`.
4. **Do not auto-continue on timeout.** Dify `__timeout` handle would skip the human. COSMOS stale is a FLAG. HOLD does not self-clear. Only resume-gate has `auto_resume_at`.
5. **Optional later (HOLD, not this tick): `JOB_PAUSED` ledger event** if Keith names a mid-run park that is neither FINDINGS nor HOLD-the-session. Until then, do not grow the vocabulary. H8.

**BORROW rows: none.** Nothing here is copy-their-code. Mechanisms map onto organs we already have or onto `/jukebox` paint.

---

## 5. Explicit REFUSE (so a later lane cannot "just vendor")

- Do not run n8n CE, n8n queue mode, or n8n WaitTracker beside Core.
- Do not run Dify API / graphon / Celery / `workflow_pause` SQL.
- Do not add `waiting` or `PAUSED` to `cosmos_sched.OUTCOMES`.
- Do not persist graph snapshots for resume (SEED is the carry-over).
- Do not open `:8770/webhook-waiting/{executionId}` or a form-token URL as a second API.
- Do not auto-retry BROKE/STALE.
- Do not iframe their editors.

---

## 6. Proof this return read code (not marketing)

- n8n Wait human path ends in `putToWait` → `putExecutionToWait` → status `'waiting'` + `waitTill` (possibly year 3000). Resume is `WaitingWebhooks` or `WaitTracker.startExecution`, both rehydrate `IRunExecutionData` and disable the wait node.
- n8n `waiting` is excluded from crash recovery on purpose (`CRASHABLE_EXECUTION_STATUSES` comment).
- n8n node retry is `getRetryParams` in `WorkflowExecute`, clamp 2–5 tries, skipped on `resumeError`.
- Dify Human Input runtime is `DifyHITLCallback` + `DifyHumanInputNodeRuntime`, not the TSX node.
- Dify pause persistence is two layers: status `PAUSED` (`WorkflowPersistenceLayer`) and blob `WorkflowResumptionContext` (`PauseStatePersistenceLayer`).
- Dify resume is `HumanInputService.enqueue_resume` → Celery `resume_app_execution`, gated on `pause_entity.resumed_at is None`.

**Do not embed n8n. Do not embed Dify.** Stage 1 complete. BUILD only if CCr names an ADAPT row that already has a live Core emit.
