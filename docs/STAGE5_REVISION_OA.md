## (A) JSON Block: Rubric Compliance

```json
[
  {
    "id": "H1",
    "how": "COSMOS authority is an append-only, hash-chained, service-authenticated event ledger plus immutable manifests and content-addressed state objects. Queue, registry, lease, spend, watcher, backup, and context state are rebuildable projections. Every closing session must record a Context Manifest identifying inherited facts, active leases, unresolved watchers, evidence pointers, and handoff recipient; closure without a valid manifest records OPEN_CONTEXT.",
    "risk": "A ledger can preserve only facts represented by its schemas and accepted inputs. The scar-derived minimum fact schema ships in the MVP; missing tool-specific behavioral cards remain UNKNOWN until evidenced and governed into the schema."
  },
  {
    "id": "H2",
    "how": "All boundaries use typed outcomes, including FOUND, NOT_FOUND, UNREADABLE, UNPARSEABLE, IDENTITY_MISMATCH, STALE, OUT_OF_CLOCK, NOT_IN_CORPUS, NOT_IN_RECORD, UNREACHABLE, SESSION_EXPIRED, AUTH_REQUIRED, UNPRICED, and REFUSED. Root resolution, ingress envelopes, manifests, ledger records, route selection, validators, and provider calls fail closed. Fallback is permitted only when an explicit route policy authorizes it and the fallback decision is ledgered.",
    "risk": "Fail-closed behavior creates visible operational refusals. Operator remediation and explicit audited override workflows are required; convenience fallback must not be represented as recovery."
  },
  {
    "id": "H3",
    "how": "One resident COSMOS Core service is the authoritative ledger writer, scheduler, spend gate, lease arbiter, registry/probe owner, return-watcher owner, and protected-write gateway. It issues expiring leases with monotonic fencing tokens and rejects stale protected commits. Native authoritative storage is on one verified volume; mount-visible surfaces are ingress/egress only and are never authority until native verification and ledger acceptance.",
    "risk": "COSMOS Core is a single availability point. The system mitigates this through durable replay, Windows service recovery, verified backup and restore rehearsal, and fail-closed refusal rather than a second unsynchronized writer."
  },
  {
    "id": "H4",
    "how": "VerifiedIO, Dispatch/ReturnWatcher, ReturnValidator, Reconciler, ContextManager, PlatformAdapter, and TypedAbsence are mandatory kernel interfaces. Workers and adapters receive scoped capabilities and cannot directly mutate protected state, invoke unrestricted provider clients, or bypass verified ingress, fenced publication, platform containment, and validator paths.",
    "risk": "Capability and import boundaries must be enforced in code review, tests, and packaging. A nominal interface is insufficient if a worker can import an internal filesystem or provider client directly."
  },
  {
    "id": "H5",
    "how": "The scheduler owns admission by priority, dependencies, lane capacity, rail health, budget reservation, node capacity, and lock scope. The arbiter grants leases and fencing tokens before execution. Workers write attempt-private workspaces only; publication is a service-side fenced commit with expected input hashes. Legacy mutable tools run serialized in a compatibility lane until behavior-card-backed adaptation earns parallelism.",
    "risk": "Serialized compatibility work can limit throughput. It is an intentional safety constraint, removed only for tools whose state surfaces and publication behavior have been demonstrated safe."
  },
  {
    "id": "H6",
    "how": "Node, Surface, Rail, Link, Credential Scope, Route Policy, Probe, Measurement, and Rail Adapter are first-class registry entities. DOM is a normal scheduler rail, subject to the same dispatch, reserve-before-call, preflight, watcher, evidence, validation, and typed-return rules as CLI, API, CHAT, and OTHER. DOM-first is route-policy data; fallback to API is explicit, authorized, and audited.",
    "risk": "A browser-capable rail may be unavailable, vendor-blocked, session-expired, or prohibited by applicable terms. Registration is not a claim of capability; dated behavioral probes determine eligibility."
  },
  {
    "id": "H7",
    "how": "Boot explicitly instantiates RootResolver from an ACL-protected machine-local installation record. Resolver verification checks the configured root, installation identity, sentinel digest/content, required role markers, and normalized-under-root paths before COSMOS Core can become READY. The service exposes authenticated versioned HTTPS API endpoints; KDash and future clients consume that API rather than local state files.",
    "risk": "The installation record is critical configuration and must be protected, backed up, validated against the root sentinel, and deliberately recreated during restore. It is never inferred by path search or guessed from an environment variable."
  },
  {
    "id": "H8",
    "how": "The Tool Contract Registry records each incumbent tool's inputs, outputs, state surfaces, overlap semantics, negative controls, and disposition: PRESERVED, ADAPTED, REPLACED, or ABANDONED with an architecture-wins decision. The compatibility lane preserves log-first, helper exclusion, UTF-8 boundaries, CLEAN/FINDINGS/BROKE, report-never-retry, and append-over-rename for mount-exposed state.",
    "risk": "Behavioral evidence exists here only for the named spike tools. Disposition and exact compatibility requirements for the remaining approximately 135 tools are UNKNOWN pending behavioral-card fan-out."
  },
  {
    "id": "H9",
    "how": "COSMOS Core records time-source identity, offset, uncertainty, and measurement time. Windows Task Scheduler registrations are durable triggers read back through the OS API; service timers, filesystem notifications, process completion, webhooks, and browser events feed durable wakeups. Windows Job Objects contain worker-owned native subprocess trees, including browser processes launched by the DOM worker.",
    "risk": "Filesystem notifications, browser automation events, and host clock conditions can fail or overflow. COSMOS records watcher health and performs bounded reconciliation; degraded observation is a loud state, never evidence of no change."
  },
  {
    "id": "H10",
    "how": "The stable product contract is the versioned COSMOS API, job model, event schemas, registry schemas, rail-adapter contract, worker protocol, and backup-target interface. Internally, Core has separable modules with explicit command/event contracts, enabling later process separation without changing the external API or creating another authority. Alternate frontend, voice, federation, mobile, and cloud automation remain clients or adapters.",
    "risk": "Internal separability does not establish a need to split services. A later split requires measured operational justification and must preserve one authoritative ledger/write path or use a formally designed replicated-authority protocol, which is UNKNOWN."
  }
]
```

## (B) Revised Architecture Design

### 1. Decision revision after merge

I adopt the merge synthesis on all load-bearing points:

- **one resident COSMOS Core authority;**
- **leases plus fencing tokens;**
- **explicit root resolver instantiation during boot composition;**
- **immutable manifests plus append-only ledger as canonical state;**
- **SQLite only as a service-private disposable projection/cache, never canonical state and never mount-shared;**
- **one versioned API surface for KDash and future clients;**
- **DOM as a first-class scheduler rail;**
- **backup policy, verification, alerts, and rehearsal evidence in Core; execution as scheduled jobs.**

I concede my earlier wording that emphasized “one process” too strongly. The authority remains one resident service and one authoritative write path, but secure execution workers—especially DOM workers—must be separate contained processes. This is not a second authority or a public API break.

I defend the rejection of separate authoritative registry, arbiter, and scheduler services for the MVP. They may be separable implementation modules, but independently authoritative processes would recreate coordination and split-brain risks without demonstrated need.

### 2. COSMOS Core internal layout

COSMOS Core is one Windows service process in the MVP, composed from modules with explicit internal interfaces. No module may mutate authoritative state except through the LedgerWriter/CommandGate path.

```text
COSMOS Core service
├── Bootstrap / Composition Root
│   ├── InstallationRecordReader
│   ├── RootResolver
│   ├── service readiness gate
│   └── dependency composition
├── API Gateway
│   ├── authentication and authorization
│   ├── versioned HTTPS API
│   └── KDash query/API projection endpoints
├── Command Gate
│   ├── typed command validation
│   ├── idempotency handling
│   ├── authorization and capability checks
│   └── authoritative state-transition admission
├── Ledger Authority
│   ├── LedgerWriter
│   ├── LedgerVerifier
│   ├── segment/anchor manager
│   ├── content-addressed object pointer manager
│   └── projection rebuild source
├── Projection Store
│   ├── queue projection
│   ├── registry projection
│   ├── lease projection
│   ├── spend projection
│   └── optional service-private SQLite cache
├── Scheduler
│   ├── admission and priority logic
│   ├── dependency and lane-capacity logic
│   ├── worker assignment
│   └── durable wakeup consumption
├── Arbiter
│   ├── lease issuance/renewal/expiry
│   ├── monotonic fencing-token issuance
│   └── protected-commit checks
├── Registry and Reconciler
│   ├── nodes, rails, links, credential scopes
│   ├── route policies
│   ├── probes and measurements
│   └── reconciliation schedules
├── Return and Context Manager
│   ├── watcher creation before dispatch
│   ├── validator chain
│   ├── Context Manifest validation
│   └── terminal/open-context incidents
├── Spend Gate
│   ├── reservation
│   ├── expiry
│   ├── settlement
│   └── provider/billed reconciliation
├── Worker Supervisor
│   ├── native worker protocol
│   ├── DOM worker supervision
│   ├── process/heartbeat observation
│   └── result ingestion
└── Backup Policy Coordinator
    ├── backup/rehearsal scheduling
    ├── target verification
    ├── alerting
    └── evidence retention
```

Internal modules communicate by typed commands and ledgered domain events, not by shared writable folders or direct database access. For example:

- Scheduler submits `ADMIT_JOB`, `DISPATCH_ATTEMPT`, and `EXPIRE_ATTEMPT` commands.
- Arbiter submits `GRANT_LEASE`, `RENEW_LEASE`, `EXPIRE_LEASE`, and `REFUSE_STALE_COMMIT`.
- Registry submits measured `PROBE_RESULT` commands.
- Worker Supervisor submits `WORKER_STARTED`, `HEARTBEAT`, `RETURN_RECEIVED`, and `WORKER_LOST`.
- Projection Store consumes verified events only.

A future split may move Scheduler, Registry/Reconciler, or Worker Supervisor into separately deployable processes, but only behind these same internal contracts. The external API, event schema, fencing semantics, and single authoritative ledger writer remain stable. A multi-writer or replicated-authority design is **UNKNOWN** and is not implied by this module layout.

### 3. Ledger decision and mount rules

**Chosen implementation: signed/service-authenticated, hash-chained framed JSONL ledger segments on the verified native authoritative volume.**

This adopts CoPG’s signed-anchor contribution and retains the OA requirement for framing and corruption refusal. SQLite-WAL is not the ledger. SQLite may support local projection queries only and can be discarded and rebuilt from verified ledger segments.

Each ledger event is canonical JSON encoded as one framed JSONL record containing at minimum:

- event ID and schema version;
- installation ID;
- event type;
- writer/service identity;
- causal parent IDs;
- arbiter timestamp, time source, offset, and uncertainty;
- payload byte length;
- payload SHA-256;
- previous-record hash;
- segment ID and record sequence;
- service HMAC or equivalent service-authenticated signature;
- optional anchor signature for exported/cross-volume verification.

A record is accepted only when its declared byte count, JSON parsing, schema, payload hash, chain predecessor, and authentication material verify. A partial final record, malformed record, invalid chain, invalid signature/HMAC, or missing anchored segment is an integrity incident. COSMOS refuses affected authoritative operations; it does not silently skip, truncate, or “repair” history.

#### Storage rules

1. **Authoritative ledger writes occur only on the native verified volume.**
   - One LedgerWriter serializes appends.
   - Workers, dashboards, sandbox processes, and mount clients have no direct write capability.
   - Ledger segments are rotated into immutable closed segments and anchored.

2. **Mount-visible state is append-only ingress/egress, never authority.**
   - A sandbox may write a unique ingress envelope or append an immutable request record.
   - The native service reads the bytes, verifies declared length, hash, schema, sender identity, and permitted scope.
   - Only `INGRESS_ACCEPTED` in the native ledger makes that content operationally accepted.
   - Rename, lock-file, timestamp, and directory-observation behavior on a mount are not trusted for authority.

3. **No mount-visible mutable database.**
   - SQLite, WAL files, projections, queues, and lock tables are never shared through a mount.
   - A corrupt service-private SQLite projection is discarded and rebuilt.

4. **Exports are immutable.**
   - Closed ledger segments and evidence objects may be exported read-only to backup, audit, or another volume.
   - Their segment anchor and hashes allow verification after transfer.
   - Exporting a segment does not make the target a writer or a competing ledger authority.

5. **Atomic rename is only an optimization.**
   - On one verified native volume, Core may use write-temp/fsync/atomic-rename to install an immutable content-addressed object.
   - This is not a lock protocol, not a cross-volume claim mechanism, and not an authority mechanism.
   - Fenced service commit remains required for protected publication.

This choice is more explicit than the prior design: framed JSONL is selected because it remains inspectable, append-oriented, segment-exportable, and independently verifiable while avoiding a mount-shared mutable database. The service serialization provides the transactional boundary required for authoritative state transitions.

### 4. Queue, locks, workers, and publication

A job submission creates an immutable manifest containing job ID, request ID, submitter identity, idempotency key, tool-contract version, required route policy, dependencies, input content hashes, expected validators, timeout policy, budget needs, lock scope, and permitted data scope.

The canonical lifecycle is ledgered:

```text
JOB_SUBMITTED
JOB_ADMITTED | JOB_REFUSED
BUDGET_RESERVED
LEASE_GRANTED
RETURN_WATCHER_REGISTERED
WORKER_ASSIGNED
WORKER_STARTED
RETURN_RECEIVED | WORKER_LOST | RETURN_TIMED_OUT
RETURN_VALIDATED | RETURN_REFUSED
LEASE_RELEASED | LEASE_EXPIRED
JOB_COMPLETED_CLEAN | JOB_COMPLETED_FINDINGS | JOB_COMPLETED_BROKE
```

Workers receive only scoped execution capabilities. They write only to:

```text
work\<job-id>\<attempt-id>\<worker-id>\
```

Protected publication requires a Core commit request carrying the active fencing token and expected input hashes. Core rejects expired tokens, superseded tokens, mismatched inputs, invalid worker identity, or failed validation. Workers cannot directly alter a protected tree, canonical registry, queue state, budget state, or ledger.

Legacy mutable-file tools remain in a serialized compatibility lane. This is retained from the earlier OA design and reinforced by the merge: unrestricted parallelism is earned per tool, not granted by default.

### 5. DOM worker containment

A DOM worker is a **separate, browser-capable worker process supervised by COSMOS Core**, not an in-process browser library and not an unmanaged user browser.

#### Identity and authorization

- Each DOM worker has a distinct worker identity and runs under a dedicated least-privilege OS service account.
- The worker authenticates to Core using a short-lived worker credential/certificate or equivalent scoped mechanism. Exact credential technology is **UNKNOWN**; it must support rotation, revocation, and worker-specific identity.
- Core dispatches a DOM attempt with an attempt ID, route capability, allowed credential scope, data-classification scope, deadline, and—where relevant—budget reservation token.
- The DOM worker has no authority to commit protected state. It submits evidence and a typed return to Core; Core validates and commits it.

#### Browser and profile management

- Browser profiles are dedicated by credential scope and rail identity. A DOM job does not use a shared interactive operator profile.
- Profile directories are ACL-restricted to the DOM worker identity and are not mount-visible writable state.
- Persistent profile reuse is permitted only where route policy explicitly requires a maintained session. Session identity, cookie/session freshness, and last successful session probe are registry measurements, not assumptions.
- Ephemeral profiles are used for jobs not requiring persisted session state.
- Secrets are not passed in manifests, command lines, logs, screenshots, or ledger payloads. The exact secret-store implementation is **UNKNOWN**; the worker contract requires scoped retrieval and redaction.

#### Process containment and browser death

- The worker launches browser processes under a Windows Job Object where platform behavior permits, so timeout/cancellation includes descendants.
- Worker Supervisor observes worker-process exit, browser-process exit, automation-protocol disconnect, and missed heartbeat.
- A browser death mid-job causes a ledgered `DOM_BROWSER_LOST`/`WORKER_LOST` event and a typed terminal or explicitly resumable result:
  - `UNREACHABLE` when browser/control transport is unavailable;
  - `SESSION_EXPIRED` when an authenticated session is no longer valid;
  - `AUTH_REQUIRED` when interaction requires reauthentication;
  - `BROKE` when the attempt cannot safely establish outcome;
  - a policy-defined resumable state only when evidence proves the remote action was not committed or can be queried safely.
- Core fences the attempt’s lease, prevents later publication by that attempt, records unresolved watcher state, and performs bounded cleanup/quarantine of the attempt workspace and browser profile as policy permits.
- COSMOS does **not** automatically rerun a dead DOM attempt merely because the browser died. It follows report-never-retry unless an explicit tool/route policy authorizes a safe idempotent retry.

DOM evidence may include redacted action receipts, browser protocol events, downloaded-object hashes, page-state evidence, and screenshots only where policy permits. It must never treat a screenshot or local browser state alone as proof of a paid or externally consequential action; required provider/DOM receipt validation remains route-specific.

### 6. KDash, backup, and API

KDash is an API projection of COSMOS Core. It is not a filesystem reader and not a second backend. Every response includes provenance, `observed_at`, `measured_at`, staleness policy, and evidence pointers where authorized.

Backup execution runs as scheduled jobs, potentially with an elevated operations worker. Policy, destination verification, alerting, evidence, retention status, and restore-rehearsal state remain in Core and are ledgered. Restore rehearsal is a scheduled `rehearse-restore` job into an isolated workspace, with root/sentinel identity, enumeration, readability, and hash verification before it can record success.

## (C) Explicit Required Answers

### 1. Lock enforcement mechanism

**Chosen: COSMOS Core arbiter issuing expiring leases and monotonic fencing tokens.**

Every protected commit passes through Core and presents its token. Stale, expired, superseded, or mismatched-token commits are rejected and ledgered. This is retained without concession because OS locks, mount lock files, and claim-by-rename do not safely cover native/sandbox disagreement, abandoned sessions, or cross-volume coordination.

Atomic rename on a verified single native volume may optimize immutable object installation, but it is not lock enforcement.

### 2. Queue substrate

**Chosen: immutable job manifests plus canonical ledger lifecycle events.**

The scheduler uses rebuildable projections, optionally cached in service-private SQLite. SQLite is not authority, is never mount-shared, and can be deleted and rebuilt. I concede GEM’s ACID concern only at the implementation level: Core’s serialized command-plus-ledger append is the authoritative transaction boundary; SQLite may make projections and queries efficient without becoming canonical mutable state.

### 3. Resolver timing

**Chosen: explicit instantiation during bootstrap composition.**

Core cannot enter READY, bind its work API, or accept jobs until the resolver verifies the machine installation record, configured root, sentinel digest/content, role markers, and platform-normalized paths. Import-time root resolution is rejected because it creates hidden machine-dependent side effects while adding no safety unavailable at explicit fail-fast boot.

### 4. DOM lane placement and containment

**Chosen: DOM is a first-class scheduler rail implemented by separately contained DOM workers.**

DOM work has manifests, route policy, lane capacity, budget reservation, live preflight, return watcher, evidence requirements, validator chain, typed failure, and explicit fallback rules. The browser-capable worker has its own OS identity, dedicated scoped profiles, Job Object containment, and no direct protected-write authority. Browser death produces a ledgered typed failure or explicitly evidenced resumable state; it never implies success and never silently falls back to API.

### 5. KDash backend and frontend API

**Chosen: one COSMOS Core authority and one versioned API surface.**

KDash is a client/projection of that API. The alternate frontend, voice interface, desktop/phone clients, and future cloud-hosted UI are also clients. I concede CoPG’s useful distinction between backend and frontend components, but not a separate KDash data/control authority: separating UI deployment is acceptable; duplicating authoritative backend state is not.

### 6. Backup placement and restore rehearsal

**Chosen: Core owns backup policy, verification state, alerting, and evidence; scheduled workers execute backup and rehearsal jobs.**

Windows Task Scheduler is a registered, read-back trigger/integration point. A backup is successful only after destination enumeration and hash verification. A restore rehearsal is a first-class scheduled job restoring to isolation and verifying the selected scope before recording `RESTORE_REHEARSAL_PASSED`.

## (D) MVP Cut-line

### Ships in the code phase

1. **Bootstrap and service**
   - Windows service installation and recovery configuration;
   - ACL-protected machine installation record;
   - explicit RootResolver;
   - sentinel, installation-ID, role-marker, and path verification;
   - authenticated versioned API and READY refusal on failed boot verification.

2. **Authoritative state**
   - native-volume framed, hash-chained, service-authenticated JSONL ledger segments;
   - segment verification and corruption refusal;
   - immutable content-addressed state objects;
   - projection rebuild;
   - optional service-private SQLite projection cache;
   - no mount-shared SQLite, queue, ledger, or lock database.

3. **Service module boundaries**
   - API Gateway, Command Gate, Ledger Authority, Projection Store, Scheduler, Arbiter, Registry/Reconciler, Return/Context Manager, Worker Supervisor, Spend Gate, and Backup Policy Coordinator;
   - typed internal command/event contracts;
   - one authoritative LedgerWriter.

4. **Queue, scheduling, and locks**
   - immutable job manifests;
   - priority, dependency, lane, and capacity admission;
   - leases, expiry events, fencing tokens, and fenced commit;
   - attempt-private workspaces;
   - serialized compatibility lane;
   - CLEAN/FINDINGS/BROKE and report-never-retry.

5. **Workers**
   - native worker protocol;
   - Windows Job Object containment for worker-owned subprocesses;
   - heartbeat, timeout, process-loss, and return ingestion;
   - log-first and UTF-8 boundary enforcement.

6. **Registry, probes, and rails**
   - Node, Surface, Rail, Link, Credential Scope, Route Policy, Probe, and Measurement schemas;
   - CLI/API/DOM/CHAT/OTHER rail types;
   - dated behavioral probes and health-age reporting;
   - explicit audited route fallback.

7. **DOM MVP**
   - one contained DOM worker implementation;
   - dedicated worker identity;
   - scoped profile management;
   - browser/session preflight;
   - browser/process/automation-disconnect detection;
   - typed `UNREACHABLE`, `SESSION_EXPIRED`, `AUTH_REQUIRED`, and browser-loss handling;
   - no silent retry or fallback.

8. **Return, context, and spend**
   - watcher-before-dispatch;
   - path/object validators and validator seam for DOI/source validation;
   - Context Manifest and OPEN_CONTEXT incident;
   - reserve-before-call, reservation expiry, settlement, and UNPRICED.

9. **KDash API**
   - queue, lease, rail, probe age, spend, watcher, backup, task, and incident projections;
   - provenance and measurement timestamps;
   - evidence pointers subject to authorization.

10. **Backup**
    - policy-defined protected scope;
    - at least one verified off-machine target;
    - scheduled backup execution;
    - destination enumeration and hash verification;
    - one recorded isolated restore rehearsal;
    - loud failure and visible KDash/API status.

11. **Spike-tool compatibility**
    - behavior-card-backed adaptation for `bts_paths`, `tree_lock`, `bts_phone`, and `bts_runner`;
    - Tool Contract Registry and dispositions;
    - no `.bat` creation;
    - never-delete staging to `_delme` where retirement is required.

### Explicit seams or UNKNOWN items

- Alternate orchestration frontend implementation.
- Voice input/output implementation.
- Federation/KMesh/JMesh/HMesh live operation and replicated authority design.
- Mobile and desktop clients.
- Cloud deployment automation beyond deployable service configuration.
- Complete secret-store technology for DOM worker credentials: **UNKNOWN**.
- Exact browser isolation hardening beyond dedicated identity, profile ACLs, Job Objects, and scoped capabilities: **UNKNOWN**.
- Full behavioral cards and dispositions for approximately 135 remaining tools: **UNKNOWN**.
- W1-W12 definitions, acceptance criteria, and implementation status: **UNKNOWN**.
- High-availability or multi-writer ledger design: **UNKNOWN** and explicitly outside the MVP.