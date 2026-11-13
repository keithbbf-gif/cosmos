# GHX public architecture mine (not a xerox)

- Writer: GbGH Snapshot (executor). Snapshot is not the pen.
- Date: 2026-08-17 (CT)
- Job: standing QA Engineer (Keith, via GbQA) — mine public architectures for a federated multi-agent mesh.
- Output path: `V:\Ai\tmp\GHX_PUBLIC_ARCH_MINE.md` (this file). Nowhere else.
- Method: WebSearch + WebFetch of live GitHub/docs pages on 2026-08-17. `gh` was not logged in; no clone of keithbbf-gif/bts-mesh; no other clones. No `.env`, tokens, push, or commit.
- Rule: extract the PATTERN (how single-writer / append-only / queue / seat-move works). Do not copy folder layouts into any mesh tree.
- Star counts below are what GitHub showed via WebFetch on 2026-08-17. They are observations, not marketing.

Four patterns in scope:

1. job/queue
2. single-writer
3. append-only ledger
4. portable seats (agent identity / session / location-transparent workers that can move)

---

## 1. Restate — virtual objects = single-writer per key

- Repo: https://github.com/restatedev/restate (observed ~4,304 stars)
- Docs: https://docs.restate.dev/foundations/services
- Also: https://www.restate.dev/what-is-durable-execution
- Example (virtual objects): https://github.com/restatedev/examples/blob/main/typescript/basics/src/2_virtual_objects.ts
- Teaches: **single-writer**, **job/queue**, **portable seats**

Stealable idea: Restate is a durable-execution runtime in front of your handlers. A Virtual Object is a key (user, session, agent, cart). Write handlers on that key are serialized — "at most one writer per key; mimics a queue per object key" — while shared/read-only handlers can run concurrently. Handlers themselves are stateless; Restate attaches the object's K/V and journals steps so a crash resumes the same key on whatever worker is registered. Workers are location-transparent: they run on Lambda, k8s, or a process and register an endpoint; Restate routes by key, not by host.

Do not xerox: do not import Restate's three service types (Service / Virtual Object / Workflow), SDK, or deployment-register CLI as the mesh's public surface. Steal the *key-as-single-writer-queue* rule, not their binary or handler annotations.

---

## 2. Temporal — Workflow ID is the lock; task queues are the job bus

- Repo: https://github.com/temporalio/temporal (observed ~22,369 stars)
- Docs: https://docs.temporal.io/workflow-execution/workflowid-runid
- Lock-as-Workflow-ID: https://docs.temporal.io/guides/lock-shared-resources
- Teaches: **job/queue**, **single-writer**

Stealable idea: A Workflow ID is a business key (order, customer, seat). Temporal guarantees at most one *open* execution per Workflow ID in a namespace. That uniqueness *is* the lock — starting a second run fails (or terminates/uses-existing, by conflict policy). Workers poll named task queues; any worker that can run the workflow type can pick the next task, so the process is portable. History is an event log the worker replays to recover deterministic workflow state. The lock-shared-resources guide shows encoding a permit as a child Workflow ID (`permit:{resource}:{slot}`): start succeeds = you hold the lock.

Do not xerox: do not copy Temporal's worker/task-queue/history-service split, protobuf surface, or "workflow must be deterministic" tax into the mesh. Steal Workflow-ID-as-single-writer and queue-polled portable workers. Cadence is the same family; no need for a second xerox.

---

## 3. NATS JetStream — append-only streams + leafnode federation

- Repo: https://github.com/nats-io/nats-server (observed ~20,532 stars)
- Docs: https://docs.nats.io/nats-concepts/jetstream
- Leafnodes: https://docs.nats.io/learn/topologies/leaf-nodes
- Teaches: **append-only ledger**, **job/queue**, (federation, not a seat model)

Stealable idea: A JetStream stream is a server-side append: publish to a subject, server assigns a sequence number, message is durable. A consumer is a *cursor* the server remembers; ack advances it, timeout redelivers (at-least-once job queue). Multiple consumers can read the same stream independently — one log, many readers. Leafnodes let a site open an outbound link to a hub; JetStream *domains* keep the leaf's streams and the hub's streams from colliding. Mirrors/sources copy data across the leaf after reconnect, so a factory floor can append locally and later source into the hub.

Do not xerox: do not adopt NATS subjects, accounts, or JetStream domain names as the mesh's identity scheme. Steal "append + named cursor + leaf-domain isolation." Sharing the system account across a leaf *extends* the hub's JetStream instead of isolating it — that is the foot-gun.

---

## 4. Microsoft Orleans — grain identity is the portable seat

- Repo: https://github.com/dotnet/orleans (observed ~10,834 stars)
- Docs: https://learn.microsoft.com/en-us/dotnet/orleans/overview
- Grain identity: https://learn.microsoft.com/en-us/dotnet/orleans/grains/grain-identity
- Teaches: **portable seats**, **single-writer**

Stealable idea: A grain is a virtual actor: type + key (e.g. `shoppingcart/bob65`). The identity is logical, not a process pointer, so a grain reference stays valid across process death, silo restart, and placement moves. The runtime activates the grain on some silo on first call, deactivates it when idle, and reactivates elsewhere after failure. Callers never choose a host. One activation per identity in the cluster gives turn-based single-writer on that seat. That is location-transparent worker identity.

Do not xerox: do not copy silos, .NET grain interfaces, or `IGrainWithGuidKey` into a non-.NET mesh. Steal "logical ID outlives the process; runtime places/activates; one live writer per ID." Dapr actors are the same virtual-actor family with a sidecar; skip a second xerox unless you specifically want HTTP placement.

---

## 5. EventStoreDB / KurrentDB — purpose-built append-only ledger

- Repo: https://github.com/EventStore/EventStore (same tree now branded KurrentDB; observed ~5,841 stars)
- Product: https://www.kurrent.io/event-sourcing
- Feature notes: https://www.kurrent.io/blog/exploring-the-main-features-of-eventstoredb-2/
- Teaches: **append-only ledger**, **single-writer** (optimistic, per stream)

Stealable idea: State is not overwritten. Each aggregate (order, seat, scar) is a stream of immutable events. Append is the only write. Each append bumps a stream version; the client sends an expected version, and a mismatch is a concurrency conflict — single-writer without a long-held lock. Readers (projections) subscribe and build whatever view they need. The log is the source of truth; current state is a fold.

Do not xerox: do not copy EventStore's gRPC clients, projection language, or "every noun is a stream" taxonomy. Steal "append + expected-version" as the ledger contract. Do not treat a CRUD SQLite row as an event log and call it the same thing.

---

## 6. LangGraph — checkpointed agent graph (thread = seat timeline)

- Repo: https://github.com/langchain-ai/langgraph (observed ~39,872 stars)
- Checkpointers: https://docs.langchain.com/oss/python/langgraph/checkpointers
- Persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- Checkpoint interface: https://github.com/langchain-ai/langgraph/blob/main/libs/checkpoint/README.md
- Teaches: **append-only ledger** (checkpoint history), **portable seats** (thread_id), **job/queue** (graph steps / pending writes)

Stealable idea: Compile a graph with a checkpointer and a `thread_id`. Every super-step writes a snapshot; node-level writes go to `checkpoint_writes` so a failed sibling does not force successful nodes to re-run. The thread is the portable seat: any worker with the same checkpointer backend can resume that thread (crash recovery, human-in-the-loop pause, time-travel branch). Durability modes (`sync` / `async` / `exit`) make the durability/latency trade explicit. A Store is separate: cross-thread long-term memory, not the run log.

Do not xerox: do not copy LangGraph's graph DSL, reducer model, or LangChain lock-in as the mesh runtime. Steal "thread_id + per-step snapshot + pending writes" so an agent seat can move machines without losing the run. `MemorySaver` does not survive process death; a real backend is the pattern.

---

## 7. SQLite WAL + Litestream — single-writer local ledger, portable file

- Repo: https://github.com/benbjohnson/litestream (observed ~14,262 stars)
- Site: https://litestream.io/guides/go-library/
- VFS / write mode: https://litestream.io/reference/vfs/ and https://github.com/benbjohnson/litestream/blob/main/docs/VFS.md
- Teaches: **single-writer**, **append-only ledger** (WAL / LTX), **portable seats** (the DB file is the seat)

Stealable idea: SQLite WAL is already a single-writer, multi-reader local log. Litestream tails that WAL and ships incremental LTX files to object storage (or another file). The replica is the disaster-recovery / move primitive: restore the file on another box and the seat continues. The VFS can read the replica without a full restore; experimental write mode still assumes one writer and detects remote conflicts (`ErrConflict`) rather than taking a distributed lock. Portable seat = pick up the file (or replica URL), not the process.

Do not xerox: do not run multiple writers at one replica URL and hope. Do not treat Litestream as a multi-master mesh bus. Steal "one writer, append WAL, ship the log, restore elsewhere." Mixing SQLite drivers on POSIX breaks the lock; WAL is required.

---

## 8. Elixir Horde (+ OTP supervision) — named process that can move

- Repo: https://github.com/derekkraan/horde (observed ~1,493 stars; README fetched from raw.githubusercontent.com)
- Docs: https://hexdocs.pm/horde
- Eventual consistency: https://hexdocs.pm/horde/eventual_consistency.html
- Teaches: **portable seats**, **single-writer** (best-effort; CAP-honest)

Stealable idea: `Horde.Registry` gives a cluster-wide name; `Horde.DynamicSupervisor` starts the process on some node (hash ring) and, on node loss or graceful `stop/3`, redistributes children to remaining members. The seat is the *name*, not the pid. Membership is dynamic. Horde is explicit about CAP: CRDT-backed (DeltaCrdt), available and partition-tolerant, *not* immediately consistent. Duplicates can exist across a split; the registry then kills the loser with `{:name_conflict, ...}`. That is the honest portable-seat story: move on failure, detect split-brain, pick one.

Do not xerox: do not copy Elixir/OTP, Horde's CRDT, or "BEAM everything" into a Python/Go mesh. Steal "name ≠ pid; supervisor rehomes; duplicates are a first-class event." Do not assume Horde gives you a linearizable single-writer lock — it does not. For a true singleton they point at Highlander / HighlanderPG.

---

## 9. Letta (f.k.a. MemGPT) — identity + memory as a movable seat

- Landing (historical V1 archived): https://github.com/letta-ai/letta (observed ~24,287 stars)
- Current source: https://github.com/letta-ai/letta-code (observed ~3,019 stars)
- MemFS: https://docs.letta.com/concepts/memfs/index.md
- Memory: https://docs.letta.com/letta-code/memory/
- Teaches: **portable seats**, **append-only ledger** (git-backed memory)

Stealable idea: The agent is not a chat session. Identity lives in a git-backed filesystem (MemFS) that *projects* onto whichever machine the agent is running: `system/persona.md` is always in context; the rest is on-demand. Edits are local until commit/push; then any other projection of that agent sees the same memory. That is a portable seat: same agent ID, different host, same durable self. Dreaming/doctor use git worktrees so background memory writers do not block the live seat. Conversation search is a separate store from MemFS.

Do not xerox: do not copy Letta Cloud, MemFS directory names, or their desktop/CLI harness. Steal "seat = identity repo that checks out anywhere." Git-as-memory is multi-writer-capable; without a single-writer rule you get merge conflicts, not a ledger.

---

## 10. A2A protocol — federation between opaque agents (not a mesh xerox)

- Repo: https://github.com/a2aproject/A2A (observed ~25,379 stars; Linux Foundation, originated at Google)
- Spec/site: https://a2a-protocol.org/latest/
- Teaches: **job/queue** (task delegation), **portable seats** (Agent Card = discoverable identity). Not a ledger. Not a single-writer runtime.

Stealable idea: A2A is a *wire contract* between agents that do not share memory or runtime. Discovery is an Agent Card (capabilities + connection). Interaction is JSON-RPC 2.0 over HTTP(S), plus SSE stream and async push. Agents stay opaque — no shared store, no shared tools. MCP is complementary (agent-to-tool); A2A is agent-to-agent. That is federation: two meshes (or a mesh and a stranger) talk without merging trees.

Do not xerox: A2A is not an orchestrator, not a queue, not a ledger, not a seat runtime. Do not replace the mesh's internal bus with A2A, and do not treat MCP tool-calling as inter-agent federation. Use A2A at the *edge* where a foreign agent must remain opaque.

---

## Looked up, not selected (why)

Verified they exist; they did not beat the ten above on a missing pattern.

| Family | URL (fetched or listed) | Why not in the ten |
| --- | --- | --- |
| Dapr actors + pubsub | https://github.com/dapr/dapr — https://docs.dapr.io/developing-applications/building-blocks/actors/actors-features-concepts/ | Same virtual-actor / turn-based lock as Orleans, plus a sidecar. Orleans states the seat pattern more cleanly. |
| Hatchet | https://github.com/hatchet-dev/hatchet (observed ~7,737 stars) | Durable task queue / workflows; overlaps Temporal + Restate. Useful later if you want worker-slot control without Temporal's determinism tax. |
| DBOS | https://github.com/dbos-inc/dbos-transact | Durable workflows/queues *in Postgres*, no extra broker. Overlaps Temporal; steal only if "the database *is* the queue" is a hard constraint. |
| etcd leases / Raft | https://github.com/etcd-io/etcd — https://github.com/etcd-io/raft | Lease + compare-and-create is a *lock primitive*, not an architecture. Election does not fence a stale leader by itself (see etcd#10125). Use as a building block under a single-writer, not as the mesh. |
| Automerge / Yjs | (CRDT docs family; not fetched as a pick) | Multi-writer merge. Opposite of single-writer ledger. Horde already shows the CRDT cost (duplicates). |
| MCP | https://modelcontextprotocol.io/ | Agent-to-tool, not agent-to-agent. Pair with A2A; do not call it a mesh. |
| Cadence | Temporal predecessor | Same pattern as Temporal. |
| Celery / Ray | classic queues / distributed compute | Do not teach a pattern the ten lack. Ray is a cluster scheduler, not a seat/ledger. |

---

## How this maps to a federated multi-agent mesh

Map *patterns*, not product folders. Internal names below (job bus, seat lock, SCARS/ledger, seats) are the four targets from the job — not a request to copy any of the repos' trees.

**Job / queue.** Temporal and Hatchet/DBOS: named queues, workers pull, retry is the server's problem. NATS: stream + consumer cursor + ack/redeliver. Restate: the per-key mailbox *is* the queue. Mesh implication: a job is an append to a work stream or a start on a workflow/object key; the worker is whoever is alive and subscribed, not a pinned host.

**Single-writer lock.** Restate virtual object and Orleans grain: one writer per key/identity, readers concurrent. Temporal: Workflow ID uniqueness. EventStore / SQLite: optimistic version or WAL lock, not a lease. etcd: lease election if you need an explicit lock service — add a fencing token or you will split-brain. Horde: name uniqueness is *eventual*; treat conflict-kill as the signal, not as linearizability. Mesh implication: a seat, a scar stream, or a ledger head has exactly one writer; everyone else appends *requests* to that writer's queue.

**Append-only SCARS / ledger.** EventStore: stream + expected version. NATS JetStream: sequence-numbered stream. LangGraph: checkpoint + pending writes per thread. Litestream: WAL/LTX shipped off-box. Letta MemFS: git commits as the memory log (only if you add a single-writer rule). Mesh implication: SCARS/ledger entries are facts that never update in place; conflict = version mismatch, not row overwrite. Federation copies *cursors* (NATS mirror/source, Litestream replica), not live writers.

**Portable seats.** Orleans grain ID and Restate object key: call the ID, runtime places the activation. Horde: register a name, supervisor rehomes the process. Letta: checkout the identity repo on a new machine. Litestream: restore the file. LangGraph: resume `thread_id` on any worker that can see the checkpointer. A2A: the Agent Card is how a *foreign* seat is addressed without moving it. Mesh implication: a seat is an ID + durable state (log and/or memory repo). The worker process is disposable. Moving a seat means (1) fence the old writer, (2) replay or restore the log, (3) announce the ID from the new location. Do not move by copying a live process tree.

**Federation (the "not a xerox" closer).** NATS leaf + domain = site-local append, hub-level source. A2A = talk to an opaque outsider without merging stores. MCP = give a seat tools, not peers. A federated mesh should keep a single-writer ledger *inside* a domain and use leaf/source or A2A *between* domains. Do not run one global writer across sites, and do not flatten foreign agents into local seats.

---

## Sources actually opened (2026-08-17)

- https://github.com/restatedev/restate
- https://docs.restate.dev/foundations/services
- https://www.restate.dev/what-is-durable-execution
- https://github.com/restatedev/examples/blob/main/typescript/basics/src/2_virtual_objects.ts
- https://github.com/temporalio/temporal
- https://docs.temporal.io/workflow-execution/workflowid-runid
- https://docs.temporal.io/guides/lock-shared-resources
- https://github.com/nats-io/nats-server
- https://docs.nats.io/nats-concepts/jetstream
- https://docs.nats.io/learn/topologies/leaf-nodes
- https://github.com/dotnet/orleans
- https://learn.microsoft.com/en-us/dotnet/orleans/overview
- https://learn.microsoft.com/en-us/dotnet/orleans/grains/grain-identity
- https://github.com/EventStore/EventStore
- https://www.kurrent.io/event-sourcing
- https://www.kurrent.io/blog/exploring-the-main-features-of-eventstoredb-2/
- https://github.com/langchain-ai/langgraph
- https://docs.langchain.com/oss/python/langgraph/checkpointers
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://github.com/benbjohnson/litestream
- https://litestream.io/guides/go-library/
- https://litestream.io/reference/vfs/
- https://github.com/derekkraan/horde
- https://raw.githubusercontent.com/derekkraan/horde/master/README.md
- https://github.com/letta-ai/letta
- https://github.com/letta-ai/letta-code
- https://docs.letta.com/concepts/memfs/index.md
- https://github.com/a2aproject/A2A
- https://a2a-protocol.org/latest/
- https://github.com/hatchet-dev/hatchet
- https://github.com/dapr/dapr
- https://docs.dapr.io/developing-applications/building-blocks/actors/actors-features-concepts/
- https://github.com/dbos-inc/dbos-transact (search/list; README via search hits)

Not opened: Legal/. Not cloned: keithbbf-gif/bts-mesh. No tokens in this file.
