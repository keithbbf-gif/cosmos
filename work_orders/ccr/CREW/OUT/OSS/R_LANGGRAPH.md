# R_LANGGRAPH — MOTIF stage-1 RESEARCH (source, not marketing)

**DEFINE:** `work_orders/ccr/DEFINE_OSS_BORROW.md`  
**Source pin:** `langchain-ai/langgraph` @ `81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1` (default branch at fetch, 2026-09-07)  
**Method:** GitHub contents + raw.githubusercontent.com of the files named below. Not docs.langchain.com.  
**Canon:** COSMOS Core is the OS. MOTIF stays MOTIF. Time-travel / fork-from-checkpoint / LangGraph-as-loop stay **REFUSE**. Do not import `langgraph`.

---

## 1. Mechanisms (path + symbol + quote)

### 1.1 `interrupt()` — first call raises; resume returns; checkpointer required

**File:** `libs/langgraph/langgraph/types.py`  
**Symbol:** `interrupt`

On the first invocation inside a node this raises `GraphInterrupt` with an `Interrupt` whose id is a hash of the checkpoint namespace. Later invocations in the same task consume resume values **by order** (`scratchpad.interrupt_counter()`). The graph **re-executes the node from the start**. The docstring states the durability bound:

```python
    # no resume value found
    raise GraphInterrupt(
        (
            Interrupt.from_ns(
                value=value,
                ns=conf[CONFIG_KEY_CHECKPOINT_NS],
            ),
        )
    )
```

Same function, earlier in the docstring (mechanism, not a slogan): *“To use an `interrupt`, you must enable a checkpointer, as the feature relies on persisting the graph state.”* And: *“The graph resumes from the start of the node, **re-executing** all logic.”*

**COSMOS match:** HITL pause is already an OS organ — `PAUSE.flag` (`docs/PAUSE_PROTOCOL.md`: `hold` never self-clears; `resume_gate` carries `auto_resume_at`), SEED watchers (`cosmos_context.Session.close` records `OPEN_CONTEXT` on forced close), CCr `--accept` as the human resume. COSMOS does **not** re-execute a node from scratch on resume: **DONE = Output exists**. Positional interrupt matching is worse than named `order_id`.

**Bucket:** **IN COSMOS** (pause + named resume). Re-execute-from-start and positional resume lists: **REFUSE**.

---

### 1.2 `Command(resume=...)` — resume is a pending write, not a new invoke

**File:** `libs/langgraph/langgraph/types.py`  
**Symbol:** `Command`

```python
@dataclass(**_DC_KWARGS)
class Command(Generic[N], ToolOutputMixin):
    graph: str | None = None
    update: Any | None = None
    resume: dict[str, Any] | Any | None = None
    goto: Send | Sequence[Send | N] | N = ()
```

**File:** `libs/langgraph/langgraph/pregel/_io.py`  
**Symbol:** `map_command`

```python
def map_command(cmd: Command) -> Iterator[tuple[str, str, Any]]:
    """Map input chunk to a sequence of pending writes in the form (channel, value)."""
    if cmd.graph == Command.PARENT:
        raise InvalidUpdateError("There is no parent graph")
    ...
    if cmd.resume is not None:
        yield (NULL_TASK_ID, RESUME, cmd.resume)
```

Resume is not “call invoke again with None”. It is a **named write** on the `RESUME` channel, keyed under `NULL_TASK_ID`, applied to the current thread’s checkpoint. Empty input without that write raises `EmptyInputError` (`_loop.py` `_first`).

**COSMOS match:** `accept_order` / `cosmos_work_order_run.py --accept <order_id>` is the explicit resume command. It **reads Output**; it does not re-spawn. `reject_order` stays DONE. Empty re-invoke analog is refused (`FAILED` cannot be accepted).

**Bucket:** **IN COSMOS**.

---

### 1.3 Interrupt is persisted as a `writes` row, not as “the graph paused”

**File:** `libs/langgraph/langgraph/pregel/_runner.py`  
**Symbol:** `PregelRunner.commit`

```python
    def commit(self, task: PregelExecutableTask, exception: BaseException | None) -> None:
        ...
        elif exception:
            if isinstance(exception, GraphInterrupt):
                # save interrupt to checkpointer
                if exception.args[0]:
                    writes = [(INTERRUPT, exception.args[0])]
                    if resumes := [w for w in task.writes if w[0] == RESUME]:
                        writes.extend(resumes)
                    self.put_writes()(task.id, writes)
            ...
            else:
                # save error to checkpointer
                task.writes.append((ERROR, exception))
                ...
                self.put_writes()(task.id, task.writes)
        else:
            ...
            self.put_writes()(task.id, task.writes)
```

Successful sibling tasks also `put_writes`. On the next tick, those writes are reapplied so completed nodes are **not** re-run:

**File:** `libs/langgraph/langgraph/pregel/_loop.py`  
**Symbol:** `_reapply_writes_to_succeeded_nodes`

```python
    def _reapply_writes_to_succeeded_nodes(
        self, tasks: Mapping[str, PregelExecutableTask]
    ) -> None:
        """Restore successful channel writes from checkpoint to in-memory tasks.

        Skips control signals (ERROR, ERROR_SOURCE_NODE, INTERRUPT, RESUME)
        so that failed/interrupted tasks remain with empty writes and will be
        re-executed (or routed to error handlers) by the runner.
        """
        for tid, k, v in self.checkpoint_pending_writes:
            if k in (ERROR, ERROR_SOURCE_NODE, INTERRUPT, RESUME):
                continue
            if task := tasks.get(tid):
                task.writes.append((k, v))
```

`put_writes` is a **no-op without a checkpointer** (or when `durability=="exit"`):

```python
        if self.durability != "exit" and self.checkpointer_put_writes is not None:
            ...
            fut = self.submit(self.checkpointer_put_writes, config, writes_to_save, task_id, ...)
```

```python
    def _put_pending_writes(self) -> None:
        if self.checkpointer_put_writes is None:
            return
```

**COSMOS match:** DONE = Output file exists (`cosmos_workspace.output_exists`: `is_file() and st_size > 0`). The runner does not re-run a DONE order. Sibling lanes (Lane A Output, Lane B PR) are independent files. **Hole:** pickup writes JSON under `picked/` and **does not append the ledger** (`cosmos_work_order.py` header: *“Does not modify kernel / ledger”*). Folder state is not authority.

**Bucket:** sibling-success skip by Output existence: **IN COSMOS**. First durable *authority* record at pickup: **ADAPT** (see §4).

---

### 1.4 Checkpointer snapshot — `SqliteSaver.put` vs `PostgresSaver.put`

**File:** `libs/checkpoint/langgraph/checkpoint/base/__init__.py`  
**Symbol:** `Checkpoint` / `BaseCheckpointSaver`

A checkpoint is `{v, id, ts, channel_values, channel_versions, versions_seen, updated_channels}`. The saver interface is `put`, `put_writes`, `get_tuple`, `list`, `delete_thread`. Metadata `source` includes `"input" | "loop" | "update" | "fork"` — **`fork` is time-travel. REFUSE.**

Docstring on the base class: *“The `thread_id` is the primary key used to store and retrieve checkpoints. Without it, the checkpointer cannot save state, resume from interrupts, or enable time-travel debugging.”*

**File:** `libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py`  
**Symbol:** `SqliteSaver.setup` / `SqliteSaver.put`

Two tables. Channel values live **inline in the checkpoint BLOB**. WAL. `INSERT OR REPLACE`. Latest checkpoint = `ORDER BY checkpoint_id DESC LIMIT 1` when `checkpoint_id` is omitted.

```python
            CREATE TABLE IF NOT EXISTS checkpoints (
                thread_id TEXT NOT NULL,
                checkpoint_ns TEXT NOT NULL DEFAULT '',
                checkpoint_id TEXT NOT NULL,
                parent_checkpoint_id TEXT,
                type TEXT,
                checkpoint BLOB,
                metadata BLOB,
                PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
            );
            CREATE TABLE IF NOT EXISTS writes (
                thread_id TEXT NOT NULL,
                checkpoint_ns TEXT NOT NULL DEFAULT '',
                checkpoint_id TEXT NOT NULL,
                task_id TEXT NOT NULL,
                idx INTEGER NOT NULL,
                channel TEXT NOT NULL,
                type TEXT,
                value BLOB,
                PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
            );
```

```python
            cur.execute(
                "INSERT OR REPLACE INTO checkpoints (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    str(config["configurable"]["thread_id"]),
                    checkpoint_ns,
                    checkpoint["id"],
                    config["configurable"].get("checkpoint_id"),
                    type_,
                    serialized_checkpoint,
                    serialized_metadata,
                ),
            )
```

Class note: *“meant for lightweight, synchronous use cases (demos and small projects) and does not scale to multiple threads.”*

**File:** `libs/checkpoint-postgres/langgraph/checkpoint/postgres/__init__.py`  
**Symbol:** `PostgresSaver.put`

Primitives stay in the `checkpoints` JSONB row. Non-primitives and `_DeltaSnapshot` blobs go to a **separate `checkpoint_blobs` table**. Writes go to `checkpoint_writes`. Pipeline/transaction around the upsert.

```python
        blob_values = {}
        for k, v in checkpoint["channel_values"].items():
            if isinstance(v, _DeltaSnapshot):
                blob_values[k] = copy["channel_values"].pop(k)
                copy["channel_values"][k] = True
            elif v is None or isinstance(v, (str, int, float, bool)):
                pass
            else:
                blob_values[k] = copy["channel_values"].pop(k)

        with self._cursor(pipeline=True) as cur:
            if blob_versions := {k: v for k, v in new_versions.items() if k in blob_values}:
                cur.executemany(self.UPSERT_CHECKPOINT_BLOBS_SQL, self._dump_blobs(...))
            cur.execute(
                self.UPSERT_CHECKPOINTS_SQL,
                (thread_id, checkpoint_ns, checkpoint["id"], checkpoint_id,
                 Jsonb(copy), Jsonb(get_serializable_checkpoint_metadata(config, metadata))),
            )
```

**COSMOS match:** Authority is the **append-only hash-chained service-signed JSONL ledger** (`cosmos_ledger.Ledger.append` re-primes from disk, HMAC, `fsync`). SQLite is a **rebuildable projection**, never authority (`docs/FINAL_ARCHITECTURE.md`, `CDECK_PERPLEXITY_STACK.md`). Large artifacts are content-addressed (filename = hash; ledger holds the pointer) — closer to Postgres `checkpoint_blobs` than to Sqlite inline BLOBs, but the pointer lives on the ledger, not in a second DB. `parent_checkpoint_id` / `list()` / `source: "fork"` are time-travel. **REFUSE.**

**Bucket:** ledger-as-authority + CAS blobs: **IN COSMOS**. SqliteSaver or PostgresSaver as run/state authority: **REFUSE**.

---

### 1.5 `thread_id`

**File:** `libs/langgraph/langgraph/graph/state.py`  
**Symbol:** `StateGraph.compile`

```python
            checkpointer: A checkpoint saver object or flag.
                ...
                **Important**: When a checkpointer is enabled, you should pass a `thread_id`
                in the config when invoking the graph:

                config = {"configurable": {"thread_id": "my-thread"}}
                graph.invoke(inputs, config)

                The `thread_id` is the key used to store and retrieve checkpoints.
```

**File:** `libs/langgraph/langgraph/pregel/_loop.py`  
**Symbol:** `PregelLoop.__init__` — coerces `thread_id` to `str` if present; does not invent one.

**File:** `libs/langgraph/langgraph/pregel/main.py`  
**Symbol:** `Pregel.get_state`

```python
        if not checkpointer:
            raise ValueError("No checkpointer set")
```

Without `thread_id` + a saver, there is no row to get. `InMemorySaver` still keys storage `thread_id → checkpoint_ns → checkpoint_id` but it is a `defaultdict` in process RAM (`libs/checkpoint/langgraph/checkpoint/memory/__init__.py`). Process death = gone.

**COSMOS match:** identity keys already exist and are stricter: `tree_id` (sentinel), session `sid`, work-order `order_id`. HMAC SEED binds `tree_id`. A second identity namespace (`thread_id` as LangGraph conversation memory) is a second occupancy. **REFUSE** as a new key. Reuse `order_id` / `sid`.

**Bucket:** **IN COSMOS** (named ids). Importing `thread_id` as a parallel conversation store: **REFUSE**.

---

### 1.6 `interrupt_before`

**File:** `libs/langgraph/langgraph/graph/state.py` — `compile(..., interrupt_before=..., interrupt_after=...)` stored as `interrupt_before_nodes`.

**File:** `libs/langgraph/langgraph/pregel/_algo.py`  
**Symbol:** `should_interrupt`

```python
def should_interrupt(
    checkpoint: Checkpoint,
    interrupt_nodes: All | Sequence[str],
    tasks: Iterable[PregelExecutableTask],
) -> list[PregelExecutableTask]:
    """Check if the graph should be interrupted based on current state."""
    version_type = type(next(iter(checkpoint["channel_versions"].values()), None))
    null_version = version_type()
    seen = checkpoint["versions_seen"].get(INTERRUPT, {})
    any_updates_since_prev_interrupt = any(
        version > seen.get(chan, null_version)
        for chan, version in checkpoint["channel_versions"].items()
    )
    return (
        [task for task in tasks if (... task.name in interrupt_nodes ...)]
        if any_updates_since_prev_interrupt
        else []
    )
```

**File:** `libs/langgraph/langgraph/pregel/_loop.py`  
**Symbol:** `PregelLoop.tick`

```python
        # before execution, check if we should interrupt
        if self.interrupt_before and should_interrupt(
            self.checkpoint, self.interrupt_before, self.tasks.values()
        ):
            self.status = "interrupt_before"
            raise GraphInterrupt()
        ...
        self._put_checkpoint({"source": "loop"})
        if self.interrupt_after and should_interrupt(
            self.checkpoint, self.interrupt_after, self.tasks.values()
        ):
            self.status = "interrupt_after"
            raise GraphInterrupt()
```

This is a **compile-time node name list**, not a human Command. It only fires if some channel version moved since the last interrupt. Empty `GraphInterrupt()` (no payload) vs `interrupt(value)` which carries a payload.

**COSMOS match:** MOTIF stage gates (DEFINE before BUILD; critics before consensus; CCr before live-tree write) are named gates **before** a stage runs. `PAUSE.flag` is the runtime interrupt_before for the 15s clock. HOLD never self-clears.

**Bucket:** **IN COSMOS**.

---

### 1.7 What is NOT durable without a checkpointer

From the same files, not from marketing:

| Thing | What the code does without a saver |
|---|---|
| `interrupt()` / HITL | Raises in-process; `put_writes` skipped (`checkpointer_put_writes is None`). Resume cannot find INTERRUPT/RESUME rows. |
| `interrupt_before` / `interrupt_after` | Same: `GraphInterrupt` is raised, then lost at process exit. |
| Channel snapshots | `_put_checkpoint`: `do_checkpoint = self._checkpointer_put_after_previous is not None and (exiting or durability != "exit")`. No saver → no put. |
| Sibling success writes | `commit` still calls `put_writes()`, which no-ops. Next process re-runs everyone. |
| `get_state` / `list` | `ValueError("No checkpointer set")`. |
| `InMemorySaver` | Is a checkpointer **but not process-durable**. Analog of a BUCm pointer with no HMAC SEED. |
| `durability="exit"` | Intermediate supersteps are not put until loop exit. Crash mid-run = no loop checkpoint. |
| `durability="async"` | Put races the next step; not fail-closed. |
| Crash before first `put` | Their own issue #8764: recovery raises `EmptyInputError`, `durable checkpoints: 0`. The run can be “accepted” by the caller and leave **no durable failure record**. |
| `UntrackedValue` channels | Explicitly stripped before persist (`put_writes` in `_loop.py`). |
| `source: "fork"` / `list(before=checkpoint_id)` / `update_state` at a past id | Time-travel. Requires a saver **and** is **REFUSE** for COSMOS. |

**COSMOS match:** Session close without HMAC SEED is `OPEN_CONTEXT` / `NO_SEED` — a **named incident**, not silence (`cosmos_session.close_session`, `cosmos_context.Session.close`). Ledger `append` fsyncs every event. HOLD pause never self-clears. Work-order **Output missing = FAILED**, cannot `--accept`.

**Bucket:** session/SEED/ledger durability: **IN COSMOS**. Work-order pickup not yet on the ledger: **ADAPT**. Async/exit durability modes and InMemorySaver: **LEARN**. Time-travel APIs: **REFUSE**.

---

## 2. COSMOS organs that already match

| LangGraph organ | COSMOS organ | Evidence |
|---|---|---|
| Checkpointer `put` + fsync-ish persist | `Ledger.append` (re-prime, HMAC, `os.fsync`) | `cosmos/cosmos_ledger.py` |
| Thread identity | `tree_id` / `sid` / `order_id` | sentinel, `cosmos_session`, `cosmos_work_order` |
| Session snapshot + next-boot inject | HMAC `state/SEED.json` + `SEED.decl.json` | `cosmos_session.close_session` / `start_session` |
| Close without snapshot is an incident | `OPEN_CONTEXT` | `cosmos_context.Session.close` |
| HITL pause | `PAUSE.flag` `hold` vs `resume_gate` | `docs/PAUSE_PROTOCOL.md` |
| `Command(resume=)` | CCr / COW `--accept` / `accept_order` | `cosmos_work_order.accept_order`; `docs/CCR.md` |
| DONE predicate | Output file exists and non-empty | `cosmos_workspace.output_exists`; `file_done` |
| Sibling success not re-run | assigned-tasks JSON + Output path | `file_done` → `assigned/`; accept requires DONE |
| Compile-time interrupt_before | MOTIF DEFINE → BUILD; CCr before live write | `docs/MOTIF.md`, P10 |
| Heartbeat as liveness (not LLM poll) | 15s WD2 / work-order runner heartbeat | `cosmos_work_order_run.py` |
| Blob off the row | content-addressed store; ledger holds pointer | `docs/FINAL_ARCHITECTURE.md` |
| SQLite | projection cache only | `CDECK_PERPLEXITY_STACK.md` |

Work-order module **explicitly does not touch the ledger**. That is the only hole this read found that is not already an OS organ.

---

## 3. Bucket table (one bucket each)

| Mechanism | Bucket | Why |
|---|---|---|
| `interrupt()` + `GraphInterrupt` persist | **IN COSMOS** | PAUSE / SEED watchers / CCr `--accept` |
| `Command(resume=)` as named RESUME write | **IN COSMOS** | `accept_order` requires DONE Output |
| Node re-executes from start on resume | **REFUSE** | DONE = Output exists is the better predicate |
| Positional `interrupt_counter` resume list | **REFUSE** | Named `order_id` already |
| `interrupt_before` / `interrupt_after` node lists | **IN COSMOS** | MOTIF stage gates + HOLD |
| `thread_id` as occupancy key | **IN COSMOS** | `sid` / `order_id` / `tree_id`; do not add a parallel key |
| `SqliteSaver` as authority | **REFUSE** | SQLite is projection; ledger is authority |
| `PostgresSaver` as authority | **REFUSE** | Second DB authority (`CDECK_PERPLEXITY_STACK.md`) |
| Inline BLOB vs blob table | **LEARN** | COSMOS already CAS+ledger pointer; no port |
| `InMemorySaver` | **LEARN** | Shows “checkpointer ≠ durable”; analog of BUCm without HMAC SEED |
| `durability=sync\|async\|exit` | **LEARN** | Core is already sync+fsync; async/exit are weaker |
| `UntrackedValue` (strip before persist) | **LEARN** | Encode: projections must not pretend to be carry-over |
| `put_writes` sibling successes | **IN COSMOS** (files) / **ADAPT** (ledger) | Output-exists skip is live; pickup is not ledgered |
| First durable record before the run is “accepted” | **ADAPT** | Their #8764; our work-order pickup is off-ledger |
| `list` / `get_state(checkpoint_id)` / `source: "fork"` / time-travel | **REFUSE** | `PROFILES.md`; Studio DEFINE |
| LangGraph as MOTIF / COW loop | **REFUSE** | P01; `CDECK_PERPLEXITY_STACK.md` |
| Import `langgraph` package | **REFUSE** | DEFINE: do not import their packages as the MOTIF loop |

---

## 4. One ADAPT candidate (no LangGraph import, no time-travel)

**Name:** First durable pickup on the ledger (crash-before-Output is a named incident).

**What LangGraph actually does:** `PregelRunner.commit` writes INTERRUPT / ERROR / success `writes` against `(thread_id, checkpoint_id)` *during* the superstep. `_put_checkpoint` is skipped if there is no saver. If the process dies **before the first `put`**, recovery has **zero rows** and `EmptyInputError` (issue #8764, 2026-08-30, still open at pin). The interrupt is only real once it is a write.

**What COSMOS already has:** HMAC SEED + `OPEN_CONTEXT` for **sessions**. DONE = Output exists for **orders**. CCr `--accept` is the only COMPLETED transition.

**The hole:** `pickup_order` atomically files `picked/<order_id>.json` with `state=PICKED_UP` and does **not** append the ledger. If the runner dies after pickup and before Output/heartbeat, the only record is a folder file. Folders are not authority. That is the same visibility boundary LangGraph hits with “accepted run, 0 checkpoints”.

**ADAPT (our code, our emit):**

1. On `pickup_order` (and only then), `ledger.append("WORK_ORDER_PICKED", {order_id, agent, output_path, picked_at, sid})`. That is the first durable record **before** the agent runs.
2. Keep **DONE = Output exists**. Do not re-execute from start.
3. Resume remains `--accept` / `--reject` on that `order_id`. No `checkpoint_id`, no `list()`, no `source: "fork"`, no `update_state` at a past snapshot.
4. If pickup never ledgered and no Output: surface a typed incident at the next runner tick (OPEN_CONTEXT-class for orders), **do not invent COMPLETED**.

**Live emit (P04):** a ledger event `WORK_ORDER_PICKED` with `seq` / `hmac` / `prev_sha` that only `live/ledger` can produce, quoted in the report. Exit code is not done.

**Not this candidate:** LangGraph MOTIF, Postgres snapshots, Studio time-travel, `interrupt()` vendored in, node replay from a past checkpoint.

---

## Off-limits (unchanged)

- Do not vendor-in LangGraph as MOTIF or COW.
- Do not stand Postgres as run/state authority.
- Do not add fork-from-here / re-run-from-step / per-step traces.
- cDeck remains `cdeck.exe`. Core remains `:8770`.
- Do not write `V:\Ai`. Do not file USPTO. Do not publish.

**Pin for BUILD (if CCr disposes the ADAPT):** `langchain-ai/langgraph@81bf17b23123e4ef8b9d5f49fa09a0122fc2edd1` — read only; do not add the package.
