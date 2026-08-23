Reading V:\Ai\BTS_MESH\_copg_prompt.txt to retrieve the prompt so it can be answered in full.

● Read _copg_prompt.txt
  └ 1 line read

Reading the file in chunks to capture the entire prompt for answering. Now retrieving lines 1–2000, 2001–4000, 4001–6000, and 6001–8000.

● Read _copg_prompt.txt
  └ L1:2000 (189 lines read)

● Read _copg_prompt.txt
  └ L190:800 (169 lines read)

● Read _copg_prompt.txt
  └ L359:900 (393 lines read)

● Read _copg_prompt.txt
  └ L752:1400 (110 lines read)

(A) JSON block: H1–H10
[
  {"id":"H1","how":"Authority = append-only ledger (signed/framed JSONL segments) + immutable manifests; ledgers anchor content-addressed state files. On-write: append event → service records anchor → optional signed anchor for cross-volume claims; projections rebuilt from ledger. Discovery of missing facts is via read-back probes and ledger replay.","risk":"Performance under extreme write load; cross-volume atomicity requires arbiter coordination; mitigations: batching, WAL-backed local index, and spoke-level telemetry."},
  {"id":"H2","how":"Typed-results + fail-loud: every API and resolver returns typed absences (FOUND/NOT_FOUND/UNREADABLE/UNPRICED/etc.). Resolver instantiated explicitly during boot-composition and validated against sentinel; validators run before any state commit.","risk":"Operational friction during migration; requires curated operator flows and migration tools."},
  {"id":"H3","how":"Named failure defenses: resident arbiter issues time-fenced leases + monotonic fencing tokens; ledgers + read-back probes detect lying mounts; per-worker identity + OS containment (Job Objects/containers) avoid orphaned descendants; spend/reservation gate enforced pre-dispatch.","risk":"Service availability becomes critical; mitigate with durable replay, fail-closed posture, and operational recovery runbooks."},
  {"id":"H4","how":"Seven primitives as core modules: VerifiedIO (byte-count/hash verification), ReturnWatcher (pre-dispatch subscribers), ReturnValidator (pluggable validators), Reconciler (registry reality probes), ContextManager (session manifests & closure), PlatformAdapter (paths/JobObjects/encoding), TypedAbsence (result algebra). Each primitive exposes a stable internal API to allow later extraction into separate processes without client-facing API change.","risk":"Early project-wide discipline required; retrofitting is laborious."},
  {"id":"H5","how":"Scheduler owns concurrency: leases+fencing tokens via Arbiter; per-lane single-threading with global priority queues; workers write to attempt-private workspaces; publication is a fenced commit validated by ledger pointers and fencing token.","risk":"Latency for short high-frequency tasks; mitigations: optimistic fast-path on single-volume where safe."},
  {"id":"H6","how":"Registry-driven rails: every rail is typed and probed. DOM is a first-class rail policy (DOM-first by routing policy). Scheduler includes probe lifecycle and route policies so DOM fallbacks are explicit and auditable.","risk":"Legacy tool adaptation needed for DOM-first workflows."},
  {"id":"H7","how":"Installer writes single configured COSMOS_ROOT and sentinel with install identity; RootResolver explicitly instantiated at boot and validated against sentinel; service runs as resident (Windows service) exposing one versioned API surface used by all clients.","risk":"Single-root fragility; mitigations: strict ACLs, installer checks, and documented restore flows."},
  {"id":"H8","how":"Incumbent behaviors preserved via compatibility lane and adapters: claim-by-rename supported when single-volume; otherwise arbiter-issued claims required. Log-first and three-worded outcomes preserved; Tool Contract Registry records dispositions.","risk":"Adapter effort for many tools; scope and pacing required."},
  {"id":"H9","how":"Authoritative clock integrated (configurable NTP/host with recorded offset/uncertainty). Scheduler integrates OS hooks (Task Scheduler, watchers). Heartbeats and probe measurements recorded with provenance.","risk":"Host heterogeneity; require telemetry and reconciliation."},
  {"id":"H10","how":"Clear seams: core Kernel Service API and registry schemas are stable; frontends, voice, federation are API clients. Internal components expose stable composition boundaries to allow later split (service → multiple processes) without API break.","risk":"Seams must be enforced from day one; design-time discipline required."}
]

(B) Prose design — revised COPG in (A)-(D) shape, adopting the merge synthesis and answering OPEN items

1. Purpose and high-level stance
Adopt the merge verdict: one resident authority (Kernel/COSMOS Core) that earns its rent; canonical state is immutable manifests + append-only ledger events; any database (SQLite) is a service-private projection/cache only. This revision concedes to the synthesis where it improved safety and auditability, and defends CoPG strengths (signed anchors, opportunistic single-volume fast-path).

2. Internal module layout (service internals / split-ready composition) — answered (open #1)
Goal: define module boundaries so the monolithic resident service can later be split into separate processes without changing the public API.

- Composition model (single process for MVP; clear internal APIs for split):
  - API Layer (gRPC/REST gateway): product surface; minimal logic, forwards to Kernel controllers.
  - Kernel Controller surface (in-process RPC interface): orchestrates the primitives below. This controller API is the stable composition seam that later becomes an RPC surface if split.
  - Arbiter module (lock manager): lease issuance, fencing tokens, cross-volume anchor signing; implements a small, well-documented interface: RequestLease, RenewLease, ReleaseLease, VerifyFencingToken, SignAnchor. In MVP it’s a library/module inside Kernel; its interface intentionally designed to be network-call-safe so it can be extracted to a resident daemon later.
  - Ledger / Journal module: framed, signed JSONL segment writer, segment manager, and read-back probe utilities. Exposes AppendEvent, ReadSegment, VerifySegment, SnapshotPointer.
  - Manifest Ingestor: accepts immutable job manifests (ingress envelopes), validates framing and hashes, writes acceptance event.
  - Scheduler module: lane model, priority queues, admission control, lease coordination. Exposes AdmitJob, AssignWorker, PreflightProbe.
  - Runner adapter (native worker host): per-host runner that accepts attempted work units, applies JobObjects/containment, writes attempt-local artifacts, and calls Commit APIs.
  - Registries (Rail/Tool/Peer): in-memory rebuildable projections backed by ledger events. Exposes stable query APIs (ListRails, ProbeStatus).
  - SDK (Cosmos SDK): PathResolver, PlatformAdapter, client helpers that use the Kernel API.
  - Return Validation / Reconciler: pluggable validator pipeline used by commit path and reconciliation runs.
  - Backup/Restore coordinator: scheduled job manager that records rehearsals into the ledger.

Rationale and split-readiness: each module has a small, strongly-typed interface; the Kernel Controller routes internal calls through these interfaces. Splitting means replacing in-process calls with RPC calls with the same signatures — no API surface change to clients. The Arbiter interface is intentionally minimal and stable so extraction to a separate resident arbiter process or a clustered arbiter is feasible later.

3. Ledger implementation with mount rules (answered, open #2)
Decision (revised, synthesizing merge authors):
- Canonical ledger = framed, signed JSONL segments stored under ledger/; events are append-only, offset-aware frames containing schema_version, event_id, parent_ids, installation_id, job/attempt identity when applicable, payload_length, payload_sha256, previous_segment_hash, writer_identity, and signature/HMAC for cross-volume anchors.
- Content-addressed state files (filename = hex(hash)) sit under state/. The ledger stores pointers (hashes) to the live state for artifacts.
- Service-private SQLite-WAL is an indexed projection for performance (querying recent jobs, indexes by job_id, lane, priority). This SQLite DB is never shared via mounts and its contents are rebuildable from the ledger; it is explicitly declared non-authoritative.
- Signed anchors: when cross-volume claims or multi-volume coordination are involved, the arbiter signs ledger segment anchors (HMAC or asymmetric signature) so a remote verifier can assert the ledger segment's authenticity. For purely single-volume, same-host fast-paths the Kernel may accept an atomic-rename-backed optimization for ephemeral performance; such fast-paths are gated by a local availability check and logged as an opportunistic optimization.
Mount rules (enforced):
  - Any mount-visible file is an ingress envelope only until the Kernel reads, validates bytes/hash/schema/writer identity, and records an ACCEPTED event in the ledger.
  - No mount-visible file is treated as authoritative without ledger acceptance; clients must present the accepted pointer/hash when asking for publication.
  - Publication (fenced commit) requires presenting the lease/fencing token and expected input hashes; the Kernel rejects mismatches.
  - Corrupted ledger segments refuse to be read; a refusal raises an incident and blocks dependent commits until operator reconciliation.
Rationale: This combines OA’s framed JSONL auditability, GEM’s SQLite performance cache, and CoPG’s signed anchors and opportunistic single-volume fast-path. It preserves the merge rule: canonical state = immutable manifests + ledger events.

4. DOM worker containment (answered, open #3)
Design:
- DOM workers are dedicated rail-capable worker processes that register as DOM rails with the Registry. A DOM worker provides:
  - Worker identity (node_id + worker_id) and a profile identity (profile_id) for browser profile isolation.
  - Capability declarations: browser engine(s) supported, headless vs headed, maximum concurrent sessions.
  - Lifecycle hooks: Register, Heartbeat, Probe, AcquireSession, ReleaseSession.
- Session/profile management:
  - Each DOM job is assigned a session token and an ephemeral profile (either ephemeral browser profile directory or containerized profile) tied to attempt-id. The runner provisions a profile directory under work\<job>\<attempt>\<profile_id>\ and launches the browser bound to that directory.
  - Secrets and credentials required by the DOM job are passed via the secure Context object; the worker uses OS-level secrets APIs (protected files, or secure stores) and ensures minimal footprint in profiles.
- Containment:
  - Browser processes run under OS containment: Windows Job Objects (for Windows hosts) or container sandboxes (e.g., ephemeral container) when available. Timeouts, kill signals, and descendant tree kills are orchestrated by the Runner.
  - Network egress and provider credentials are mediated by the rail adapter; any provider calls are recorded with provenance and potential spend reservations.
- Failure semantics (browser dies mid-job):
  - The Runner observes process death via Job Object/monitor. Immediate actions:
    1. Capture evidence: process exit code, stdout/stderr logs, browser crash dumps, HAR and DOM snapshots if available; write these to attempt-private workspace and record a RETURN event type = SESSION_DIED/SESSION_EXPIRED/UNREACHABLE as appropriate.
    2. The ReturnWatcher is fulfilled with a typed result: SESSION_EXPIRED or UNREACHABLE or BROKE depending on evidence; validators run but the commit path refuses unless validators accept partial outputs and operator policy allows.
    3. Lease handling: if the job held leases, they remain valid until arbiter expiry; the scheduler may attempt immediate reassign under explicit idempotency policy or mark the job as needing operator intervention depending on the job’s idempotency markers and tool contract.
    4. Automatic retries: only allowed for idempotent jobs and under explicit retry policy; otherwise the attempt is marked as BROKE and findings recorded.
  - Recovery and resume:
    - If the job is resumable (contract declares checkpointable state and the worker captured sufficient evidence/checkpoints), scheduler can requeue a new attempt that presents the previous attempt’s checkpoint pointers; commit still requires fencing token and hash match of expected inputs.
    - For non-resumable jobs, operator remediation is required.
Rationale: DOM workers are first-class rails with strict containment and typed failure modes. This design enforces the merge's rule: DOM is a scheduling rail and failures are typed and audited, not silently routed.

5. Defend/concede where merge overruled original COPG
- Concede: canonical state model revised to immutable manifests + ledger events with service-private DB projections (merged synthesis). The original CoPG preference for signed ledgers is preserved but integrated into the merged canonical model.
- Adopted: resident arbiter inside the resident service; DOM-first scheduling as policy; one API surface for product (KDash/API).
- Defend retained elements: keep CoPG HMAC/signed anchors for cross-volume claims and opportunistic single-volume fast-path for performance where safe.
- Concession rationale: safety and auditability gains outweigh the narrower on-disk-only models; the service-private projection approach balances operational performance with authoritative ledger.

(C) Explicit answers to the required six questions (A–D shape preserved)

1. Lock enforcement mechanism
Chosen: resident Arbiter (inside Kernel Controller for MVP) issuing time-fenced leases and monotonic fencing tokens; interface designed to be extractable to a separate process later. Filesystem atomic-rename is permitted as an opportunistic single-volume fast-path but never as cross-volume authority. All protected commits require presenting fencing token and expected input hashes; stale tokens rejected and recorded. This aligns with merge unanimous verdict and preserves CoPG signed-anchor protections for cross-volume claims.

2. Queue substrate
Chosen: canonical substrate = immutable job manifests (filesystem ingress) + append-only ledger events for authoritative state. A service-private SQLite-WAL projection provides fast querying and scheduler indices but is rebuildable from ledger events (non-authoritative). Rule: manifests accepted only after ledger acceptance; mounts used only for ingress envelopes; no shared writable DB on mounts.

3. Resolver timing
Chosen: explicit instantiation at boot composition (RootResolver), validated against sentinel. No import-time side effects. The service cannot enter READY until resolver validates sentinel, installation record, and role directories.

4. Where DOM lanes live in the scheduler design
DOM is a first-class rail type in the Rail Registry and Scheduler. DOM jobs are admitted like other jobs, receive a Context, have ReturnWatchers registered before interaction, and run in contained DOM workers with ephemeral profiles. DOM probes are part of the scheduler’s probe lifecycle and DOM-first routing is expressed as a routing policy that is auditable. Fallbacks to API/CHAT are explicit and recorded.

5. KDash live backend + frontend API: one service or two, and why
Chosen: one product API surface served by the Kernel Service (single authoritative API). Operationally implemented as two components for deployment concerns: Kernel Service (data + control plane) and optional frontend processes (UI/voice clients). The backend is authoritative and provides the API; frontends are clients. This preserves a single source of truth while allowing independent scaling of UI.

6. Backup subsystem placement
Chosen: backup as scheduled jobs orchestrated by the Kernel Service (elevated ops job runner). Restore rehearsal is mandatory: every backup policy includes a scheduled rehearse-restore job that restores to isolated workspace, verifies sentinel and per-file hashes, and records RESTORE_REHEARSAL_PASSED or failure in the ledger. Task Scheduler (Windows) is used as a durable trigger integration but policy, verification, alerts, and evidence live in the service.

(D) MVP cut-line — what ships, seams, and UNKNOWNs

Ships in code phase (minimal, coherent deployable):
- Installer & RootResolver: sentinel-configured root, installation record, fail-fast checks.
- Kernel Service (single-process MVP) with clear internal module boundaries: API Layer, Kernel Controller, Scheduler, Arbiter module (in-process), Ledger module (framed signed JSONL), Manifest Ingestor, Registries, ReturnValidation/Reconciler, Backup coordinator.
- Immutable-manifest queue substrate + manifest ingestion and append event path.
- Service-private SQLite-WAL projection for scheduler index/performance (rebuildable).
- Runner prototype: per-host runner enforcing log-first behavior, attempt-private workspaces, Windows Job Object containment, heartbeat, and append-only attempt ledgers.
- DOM worker prototype: rail adapter, ephemeral profile provisioning, containment, evidence capture (HAR/snapshots).
- Cosmos SDK: PathResolver, PlatformAdapter, client helpers for job submission and verified IO.
- KDash API MVP: health, queue, rails, audit pointers, run submit/status endpoints.
- Backup job runner + off-machine target + rehearsal flow (rehearse-restore).
- Selftests and negative-control harnesses for core components (resolver, ledger, arbiter, scheduler, DOM adapter, backup rehearse).

Seams (deferred/exposed interfaces):
- Arbiter HA/replication (prototype shipped; HA mode UNKNOWN).
- Full federation/federated ledger sync (design seam present; implementation deferred).
- Full porting of all incumbent tools (adapter scaffolds shipped; behavior cards for all tools remain follow-up work).
- Advanced DOM multi-browser high-scale harness (prototype only).
- Optional extraction of arbiter and ledger services into separate processes (interface-ready, extraction deferred).

UNKNOWNs (honest admissions):
- Arbiter HA/large-mesh operational patterns and best-practices: UNKNOWN until field runs.
- Optimal batching and sizing of ledger segments vs WAL for extreme high-throughput write workloads: telemetry required.
- Full migration timeline/cost for ~140+ tools: UNKNOWN until behavior-card fan-out completes.

Acceptance notes and verification
- Acceptance criteria: ledgers append-only and verified by read-back; manifests accepted only after ledger event; fenced commits require valid lease and matching hashes; DOM jobs produce typed returns under all failure modes (UNREACHABLE/SESSION_EXPIRED/AUTH_REQUIRED).
- Validation: provide end-to-end smoke: install → submit manifest → scheduler admit → runner execute (DOM and native) → commit → ledger verified → KDash reflects eventual state. Backup rehearsal must pass on at least one off-machine target before acceptance.

Final statement (how this design changes COPG):
- The revised CoPG design concedes the merged synthesis that canonical state is manifests + ledger events and that the resident arbiter belongs integral to the service, while preserving CoPG’s signed-anchor protections and opportunistic single-volume fast-path. The service internals are restructured into split-ready modules with documented interfaces to allow later extraction of arbiter, ledger, or scheduler into independent processes without client API change. Ledger technology chosen is framed, signed JSONL segments as the canonical authority with a rebuildable SQLite-WAL projection for performance. DOM workers are first-class rails with strict containment, ephemeral profiles, explicit typed failure modes, and documented recovery semantics (SESSION_EXPIRED/UNREACHABLE/BROKE). UNKNOWN is used where synthesis requested it rather than guessing (arbiter HA patterns; extreme-scale tuning; full tool-card completion). End of revision.

