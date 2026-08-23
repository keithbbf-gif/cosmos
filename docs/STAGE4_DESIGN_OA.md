```json
[
  {
    "id": "H1",
    "how": "COSMOS uses an append-only, hash-chained event ledger as the authority for operational state: dispatches, claims, leases, handoffs, context snapshots, returns, validations, probes, spend reservations, settlements, and tool decisions are events rather than mutable assertions. Materialized views are disposable projections rebuilt from the ledger. Every session has a required context manifest naming its inherited facts, unresolved return watchers, active leases, and handoff recipient; session closure without a valid manifest becomes an explicit OPEN_CONTEXT incident. A required fact that is absent from the manifest, has a broken pointer, or has not been revalidated by its policy is detectable state loss, not an operator-memory failure.",
    "risk": "This makes context capture and pointer validation mandatory work. If the required-fact schema is initially too narrow, COSMOS can faithfully preserve too little; the MVP must therefore preserve the scar-derived minimum and treat expansion as a governed schema change."
  },
  {
    "id": "H2",
    "how": "All boundaries use typed results such as FOUND, NOT_FOUND, UNREADABLE, UNPARSEABLE, IDENTITY_MISMATCH, STALE, OUT_OF_CLOCK, NOT_IN_CORPUS, NOT_IN_RECORD, and UNREACHABLE. The resolver accepts exactly one configured root and verifies a sentinel containing the installation identity before exposing any role. Framed records carry declared byte length, SHA-256, schema version, writer identity, and offset-aware timestamp; incomplete, malformed, or hash-mismatched records refuse processing. Route selection has no implicit fallback: an unavailable DOM rail does not silently become API, and an unpriced call is UNPRICED rather than zero.",
    "risk": "Fail-loud behavior can stop useful work during an outage. COSMOS therefore needs clear operator-visible refusal reports and explicit, audited override actions; convenience fallback must not be disguised as recovery."
  },
  {
    "id": "H3",
    "how": "The native COSMOS service is the authoritative arbiter and write gateway. It stores authoritative ledger and queue state on one verified native volume under the configured root; sandbox or mount-visible surfaces are untrusted ingress/egress replicas. It validates bytes read by the native host against declared bytes and hashes, and never treats a mount read as authority. Locks are leases issued by the service with monotonically increasing fencing tokens; every protected commit is rejected unless its current token is presented. Leases expire on the arbiter clock, abandoned sessions are reclaimed through recorded expiry events, credit reservations expire before the provider call and are settled once, and a dead rail produces a terminal or explicitly resumable return state rather than an inferred success.",
    "risk": "The service is a critical availability point. It earns that dependency by eliminating the native-versus-sandbox split-brain class; availability is mitigated with Windows service recovery, durable ledger replay, backup/restore rehearsal, and a deliberately fail-closed posture rather than a second unsynchronized writer."
  },
  {
    "id": "H4",
    "how": "The seven primitives are kernel-level COSMOS interfaces, not optional libraries: (1) VerifiedIO reads framed bytes and verifies declared length/hash; (2) Dispatch creates an immutable return watcher before a rail call begins; (3) ReturnValidator runs DOI/source/path/receipt validators before a return can affect a projection; (4) Reconciler compares registry assertions with dated behavioral probes; (5) ContextManager owns stream identity, transcript capture, inherited context, and closure manifests; (6) PlatformAdapter alone owns Windows paths, extended-length prefixes, shell quoting, encoding, process containment, and line endings; and (7) TypedAbsence is the common result algebra used by API, tools, probes, queue, and UI.",
    "risk": "A primitive can be bypassed if builders are allowed direct filesystem, subprocess, or provider-client access. The code phase must enforce imports and capability boundaries so adapters and gateways are the only permitted paths."
  },
  {
    "id": "H5",
    "how": "Concurrency belongs to the service scheduler, which admits work according to lane, priority, dependency, budget reservation, rail capacity, node capacity, and lock scope. The lock arbiter grants a lease and fencing token before a worker receives executable capability. Every job attempt, log, heartbeat, result, message, and workspace is named by immutable job ID, attempt ID, worker ID, lane, and token; workers write only attempt-private workspaces. Publication is a fenced service commit that validates expected inputs and records a new event, so no shared file has last-writer-wins semantics. Windows Job Objects contain native subprocess trees and record timeout/kill outcomes.",
    "risk": "Legacy tools that directly overwrite shared files cannot safely receive unrestricted parallel execution. They must initially run in a serialized compatibility lane or be adapted behind fenced publication."
  },
  {
    "id": "H6",
    "how": "The registry models Node, Surface, Rail, Link, Credential Scope, Route Policy, Probe, and Measurement as first-class entities. A Link declares source, destination, rail type (DOM, API, CLI, CHAT, or OTHER), adapter, capability, cost model, health policy, authorization scope, and last behavioral probe. Route policy is data: for example DOM-first, API-only, chat-not-for-files, or prohibit a rail for a data class. The scheduler dispatches every rail through the same job lifecycle, including cheap live preflight probes and return watchers, so DOM is a normal schedulable execution lane rather than an unmanaged side channel.",
    "risk": "Some vendor DOM surfaces may be unstable, inaccessible to automation, or governed by terms that prevent a desired implementation. Such a link remains REGISTERED but UNREACHABLE or BLOCKED until a dated probe proves it; registry presence is not a claim of working connectivity."
  },
  {
    "id": "H7",
    "how": "Installation writes one machine-local COSMOS installation record containing the configured root, installation ID, sentinel digest, service identity, and allowed bind addresses. Bootstrap resolves this record before composing the application; each role is derived from the verified root and no code derives paths by walking from __file__ or assumes a drive letter. COSMOS runs as a Windows service on WRK7 for the MVP, exposing versioned HTTPS API endpoints with authenticated, authorized remote access; a cloud-hosted deployment uses the same service image and API contract. The KDash and future frontend consume this API rather than local files.",
    "risk": "A machine-local installation record is itself critical configuration. It must be ACL-protected, included in backup scope, checked against the root sentinel at boot, and intentionally recreated during restore rather than guessed from environment variables."
  },
  {
    "id": "H8",
    "how": "A versioned Tool Contract Registry records each incumbent tool name, verbs, inputs, observable outputs, state surfaces, overlap semantics, negative controls, and disposition: PRESERVED, ADAPTED, REPLACED, or ABANDONED with an architecture-wins decision. The compatibility runner preserves claim semantics where applicable, three worded outcomes CLEAN/FINDINGS/BROKE, log-first execution, report-never-retry handling, helper exclusion, and append-over-rename for mount-exposed state. Contract tests execute behavior cards against the new implementation; no tool is called migrated merely because a similarly named script exists.",
    "risk": "Only four spike-module behavior cards are supplied here; the other approximately 135 tools are not evidenced in this packet. Their contracts and dispositions are UNKNOWN until the mandated behavioral-card fan-out is completed."
  },
  {
    "id": "H9",
    "how": "The service obtains authoritative UTC from a configured offset-aware time authority and records source, offset, uncertainty, and measurement time; worker clocks are evidence only. The scheduler uses Windows Task Scheduler as a registered durable trigger source and also consumes service timers, filesystem change notifications, process completion, webhook/signal events, and DOM/browser events. File and signal wakeups enqueue durable scheduler events immediately; periodic scans are reconciliation controls, not the primary mechanism. Every registered scheduled task is read back through the OS API and reconciled with the task registry.",
    "risk": "Filesystem notification streams can overflow or be unreliable on some mounts. COSMOS records watcher health and performs bounded reconciliation scans; an overflow is a loud degraded-state event, not permission to assume no change occurred."
  },
  {
    "id": "H10",
    "how": "The architecture separates stable contracts from optional implementations: the API, registry schemas, event ledger, scheduler job model, rail adapter interface, frontend contract, voice adapter contract, federation adapter contract, and backup target interface exist from the MVP. The code-phase MVP can ship root/bootstrap, service/API, authoritative ledger, queue, locks, native runner, registry/probes, KDash API, task integration, backup verification, and a compatibility lane without implementing the alternate frontend, voice, federation, or unknown wishlist items. Those later features attach as adapters and clients rather than requiring a queue, lock, or state-model replacement.",
    "risk": "The W1-W12 definitions are not present in the supplied material. Their exact implementation status and acceptance criteria are UNKNOWN; only their extension seams can honestly be committed now."
  }
]
```

## Architecture design

### 1. One resident COSMOS service on WRK7

The MVP has one resident Windows service: **COSMOS Core**. It earns its resident status because it is simultaneously:

- the lock arbiter and fencing-token issuer;
- the scheduler and queue owner;
- the authoritative event-ledger writer;
- the API host for KDash, remote clients, and future frontend/voice clients;
- the registry and probe executor;
- the spend reservation and settlement gate;
- the return-watcher owner;
- the backup-policy coordinator.

This is intentionally one service process with internal components, not a collection of independent daemons. Separating lock arbiter, scheduler, KDash backend, and write gateway into separately authoritative services would recreate coordination and split-brain risks.

The service runs on WRK7 in the MVP. A cloud deployment is a deployment target of the same service and API contract, not a second architecture. Remote users connect through authenticated HTTPS API access. Local direct file access is not the product interface.

### 2. Root, installation identity, and role resolver

At install time, the installer asks for one COSMOS root, for example:

```text
V:\A\Ai\COSMOS
```

or:

```text
D:\Ai\COSMOS
```

It creates:

```text
<COSMOS_ROOT>\
  .cosmos-install.json
  .cosmos-sentinel.json
  state\
  ledger\
  queue\
  work\
  logs\
  registry\
  backups\
  publish\
  tools\
  config\
```

The sentinel contains an installation UUID, root identity, schema version, and expected directory-role identities. It is not merely an existence check.

A machine-local installation record points to the chosen root and contains the expected sentinel digest. At service composition time, `RootResolver` verifies:

1. the configured root exists;
2. the root sentinel parses;
3. the sentinel hash matches the installation record;
4. the installation UUID matches;
5. every required role directory exists and has its own expected marker;
6. paths normalize under the configured root;
7. Windows filesystem paths use the platform adapter’s extended-length handling where required.

There is no root-search ladder, no parent walk from source code, no drive-letter literal in business code, and no fallback root. A resolver failure prevents the service from accepting work.

The resolver is **explicitly instantiated during boot composition**, rather than resolved as an import side effect. This preserves fail-fast behavior while avoiding import-order dependence and allowing installer, diagnostics, and tests to inspect configuration without pretending that the machine is ready.

### 3. Authority model: ledger first, projections second

COSMOS has one authoritative operational history: an append-only event ledger written by COSMOS Core.

Examples:

```text
INSTALL_VERIFIED
NODE_REGISTERED
LINK_REGISTERED
PROBE_STARTED
PROBE_RESULT
JOB_SUBMITTED
JOB_ADMITTED
BUDGET_RESERVED
LEASE_GRANTED
WORKER_STARTED
RETURN_WATCHER_REGISTERED
RETURN_RECEIVED
RETURN_VALIDATED
LEASE_RELEASED
JOB_COMPLETED_CLEAN
JOB_COMPLETED_FINDINGS
JOB_COMPLETED_BROKE
BACKUP_VERIFIED
RESTORE_REHEARSAL_PASSED
```

Each event is framed and includes:

- schema version;
- event ID;
- causal parent IDs;
- installation ID;
- job/attempt/worker/lane identity where applicable;
- offset-aware timestamp and arbiter time source;
- payload byte length;
- payload SHA-256;
- previous-event hash or segment-chain hash;
- writer identity;
- signature or service-authenticated origin.

The service serializes authoritative appends. Projections such as queue status, KDash panels, rail health, spend totals, tool registry status, and task registry status are rebuildable views. A corrupted projection is discarded and rebuilt from verified ledger segments; a corrupted ledger segment refuses and raises an integrity incident.

This design carries facts across sessions structurally. A fact only counts as operationally known if it has an event, a typed state, provenance, and a valid pointer chain.

### 4. Queue and worker model

The queue substrate is **immutable filesystem manifests plus authoritative append-only ledger events**, not a shared SQLite database and not rename-driven mutable queue folders.

A submission creates an immutable job manifest. A manifest contains:

- job ID and request ID;
- requested lane and priority;
- requested rail or route-policy class;
- dependency IDs;
- allowed data scope;
- budget reservation requirement;
- input pointers and hashes;
- required validators;
- timeout and retry policy;
- tool contract version, if a legacy tool is involved;
- submitter identity;
- idempotency key;
- schema version.

The manifest is immutable after acceptance. State changes are ledger events, not edits to the manifest.

The scheduler maintains an in-memory and rebuildable projection of runnable work. It decides concurrency, lane limits, priorities, dependencies, spend availability, node availability, and rail health. Workers never “notice a file and run it” without scheduler admission.

For sandbox-originated work, the sandbox writes a unique immutable ingress envelope to a designated exchange surface. The envelope is not authoritative until the native service reads it, checks declared bytes against consumed bytes, verifies its hash and schema, validates its sender identity, and records acceptance in the native ledger. The service does not rely on mount rename behavior.

### 5. Locks, leases, and fenced publication

COSMOS chooses **arbiter service + leases + fencing tokens**, not advisory file locks.

A protected operation works as follows:

1. Scheduler identifies the lock scope: tree, tool state, publication target, budget account, or other registered resource.
2. COSMOS Core grants a lease with:
   - lease ID;
   - holder worker and attempt ID;
   - resource ID;
   - expiry according to arbiter time;
   - monotonic fencing token.
3. The worker receives only a capability scoped to that lease.
4. The worker writes outputs to its private attempt workspace.
5. To publish an output or modify protected state, the worker calls the service commit API with its fencing token and expected input hashes.
6. The service rejects stale tokens, invalid lease holders, expired leases, mismatched inputs, or concurrent superseding publications.
7. The service records either the commit or refusal as an event.

A crashed session does not require cleanup discipline. Its lease expires under arbiter time and the expiry is recorded. Stale takeover is an explicit `LEASE_EXPIRED` then `LEASE_GRANTED` chain, never silent clearing.

This defeats the named native/sandbox split-brain failure because neither universe can make an authoritative protected commit by writing a plausible lock file. The service is the sole authority.

### 6. Worker execution

Workers are registered nodes. WRK7 native workers are the MVP execution target. A worker receives:

- immutable manifest;
- attempt ID;
- worker identity;
- lease capability;
- explicitly scoped input pointers;
- route adapter capability;
- budget reservation token where required.

Every artifact carries job, attempt, worker, lane, and timestamp identity. Workspaces are private:

```text
work\<job-id>\<attempt-id>\<worker-id>\
```

Native subprocesses run under Windows Job Objects so timeout cancellation includes descendants where Windows permits it. The recorded result includes whether graceful stop, forced termination, or containment failure occurred.

The compatibility runner keeps incumbent semantics where required:

- logs open before execution;
- output decoding is forced UTF-8 at parent and child boundaries;
- helpers are explicitly non-runnable;
- the command is built from the admitted/claimed artifact identity, not a pre-admission path;
- outcome text is `CLEAN`, `FINDINGS`, or `BROKE`;
- stale work is reported and investigated, never automatically rerun merely because time passed;
- legacy mutable tools run in a serialized compatibility lane until adapted.

### 7. Rails, DOM lanes, and return handling

The registry is the routing authority. It stores nodes, surfaces, rails, links, credentials, scopes, probes, measurements, and policies.

A DOM lane is not external to the scheduler. It is a rail adapter with a job kind such as:

```text
DOM_NAVIGATE
DOM_SUBMIT
DOM_OBSERVE
DOM_DOWNLOAD
DOM_SESSION_CHECK
```

The DOM adapter runs in a designated browser-capable worker context. It manages browser/profile/session identity through the platform adapter and exposes browser events to COSMOS Core. DOM dispatch:

1. is admitted by the same scheduler as CLI, API, and chat work;
2. reserves budget if the action can incur spend;
3. performs a cheap live session/rail probe where policy requires;
4. registers a return watcher before interaction;
5. records DOM evidence, action receipt, and resulting return;
6. validates the return before it can update operational state.

DOM watchers can consume browser protocol events, download completion events, page-state transitions, and explicit timer deadlines. A dead DOM rail becomes a typed `UNREACHABLE`, `SESSION_EXPIRED`, `AUTH_REQUIRED`, or other evidenced result. It does not silently route to API unless the route policy explicitly authorizes that fallback and records it.

Chat is a lane, not a source of truth. CLI, API, DOM, CHAT, and OTHER are all first-class rail types and can be measured, restricted, budgeted, and audited.

### 8. Spend, quotas, and credit expiry

Spend enforcement is in the caller path:

1. Scheduler estimates worst-case cost and records the provenance as estimate.
2. Spend gate attempts an atomic reservation against the ledger projection.
3. If reservation fails, the call is denied before dispatch.
4. The rail adapter calls the provider only after reservation.
5. The result is settled with measured and later billed values where available.
6. Reconciliation compares tracked, provider-reported, and billed values.
7. Discrepancies become loud incidents.

A reservation has an expiry. A worker cannot use an expired reservation; it must obtain a new one. An unpriced call is `UNPRICED`, never zero. A rail with expiring credits exposes expiry in registry health and scheduler admission.

### 9. Return validation and reconciliation

Every dispatch creates a return watcher before the action starts. Watchers have expected return type, deadline, evidence requirements, and validator chain.

Examples:

- DOI return: Crossref or configured source validation before citation use.
- Quote return: source location and text comparison before use.
- Path return: native host verifies the resolved object, identity marker, bytes, and hash.
- Vendor action: receipt, provider status, and measured cost must agree before completion.
- Backup: destination listing, per-file hash verification, and restore rehearsal evidence are required.

Registry state is never “verified” merely because configuration says so. A separate reconciliation schedule re-probes rails, nodes, backups, tasks, credentials, and declared capabilities. Panels display both current state and measurement age.

### 10. KDash backend and frontend API

KDash is an API projection within COSMOS Core, not a file-reading dashboard. It exposes:

- live queue and lane state;
- active leases and stale/expired lease incidents;
- rail matrix with last probes and age;
- spend, budgets, quotas, reservations, and billed discrepancies;
- backup status and restore-rehearsal status;
- task registry and OS read-back status;
- health controls, including negative-control results;
- tool contract/disposition status;
- audit snapshots and evidence pointers.

Every panel response includes `measured_at`, `observed_at`, provenance, and staleness policy.

The alternate orchestration frontend is a separate client application later. It uses the same versioned API as KDash. Voice is another API client/adapter: speech input becomes a properly authenticated command request; voice output subscribes to permitted events. Neither changes scheduler, queue, lock, or state semantics.

### 11. Mailbox and peer messaging

COSMOS replaces fixed pair-letter files with addressed immutable messages:

```text
exchange\messages\<recipient-worker-id>\<message-id>.json
```

Messages carry sender, recipient, creation time with offset, correlation ID, payload length/hash, data classification, and expiry/staleness policy. Each recipient has an inbox identity. Missing inbox, unreadable inbox, empty inbox, stale unanswered message, and malformed message are distinct typed states.

For mount-visible message exchange, a unique immutable envelope is ingested by the native service and acknowledged through a separately recorded receipt. “Sent” and “received” are distinct events.

Federation remains an adapter seam. A peer cannot be counted as a mesh node until registry probes establish reachability, measured throughput, mesh addressability, identity, and scope policy.

### 12. Backup and restore

Backup is a COSMOS Core subsystem with OS scheduler integration, not an unattended script.

Backup policy identifies:

- irreplaceable scopes;
- local, LAN, and cloud targets;
- retention;
- encryption/key scope;
- schedule;
- required off-machine copies;
- hash-verification requirements;
- restore rehearsal cadence.

The service schedules and records backup jobs. Windows Task Scheduler is registered and read back as a durable wakeup/operational integration point, while the service owns policy, state, verification, alerts, and audit. Backup completion is not success unless the destination copy is enumerated and hashes verify. A backup without an off-machine verified target is loud failure.

Restore rehearsal restores a selected, policy-defined sample or full test scope into an isolated restore workspace, verifies root/sentinel identity and file hashes, and records a `RESTORE_REHEARSAL_PASSED` or failure event. Restore rehearsal is an acceptance condition, not documentation.

---

## Explicit answers to the six required questions

### 1. Lock enforcement mechanism

**Chosen: resident arbiter service with leases and fencing tokens.**

OS file locks alone are insufficient because COSMOS must survive a lying or semantically different mount, native and sandbox writers, abandoned sessions, and operations whose real effect is outside a lock file. COSMOS Core grants leases using its authoritative clock and issues monotonic fencing tokens. Every protected publication or state change goes through the service and is rejected if its token is stale.

The arbiter earns its rent because the same service already must be resident for API serving, scheduling, queue admission, spend gating, return watchers, KDash live state, and registry reconciliation. It is not an additional single-purpose daemon.

### 2. Queue substrate

**Chosen: immutable filesystem manifests plus append-only authoritative ledger events.**

SQLite may be used only as a disposable, service-private projection cache; it is not the authority and is never shared through a mount. Queue state is reconstructed from immutable manifests and ledger events.

This avoids shared mutable database semantics across native and sandbox universes, preserves append-over-rename behavior for mount-exposed exchange, enables audit replay, and prevents last-writer-wins queue mutation. The scheduler, not directory placement, determines runnable state.

### 3. Resolver timing

**Chosen: explicit resolver instantiation during service/bootstrap composition, with fail-fast boot.**

Imports have no machine-dependent root side effect. Instead, the service cannot enter READY state, bind its work API, or accept jobs until `RootResolver` verifies the installation record, sentinel content, role markers, and platform path handling. Diagnostics may instantiate the resolver explicitly and report failure.

This preserves the incumbent’s valuable fail-fast property while avoiding hidden import-order behavior and allowing installer/test tooling to operate intentionally.

### 4. Where DOM lanes live

**DOM is a first-class scheduler rail adapter.**

DOM jobs are queue manifests admitted by the same scheduler as API, CLI, and chat work. They receive route policy, budget reservation, worker assignment, timeout, return watcher, validation chain, and health probe. Browser/DOM events feed scheduler wakeups and watcher completion. DOM probes are registry probes with measured result and date. DOM-first is expressible as routing policy, not hardcoded control flow.

### 5. KDash live backend and frontend API

**One COSMOS Core service, one versioned API; KDash is an API consumer/projection.**

The live backend belongs in the service because it needs authoritative scheduler, registry, ledger, spend, and health state. The KDash UI may be served by the service initially or deployed as a static authenticated client, but it does not become a second authority. The alternate frontend and later phone/desktop clients use the same API.

### 6. Backup placement and restore rehearsal

**Backup policy and verification live in COSMOS Core; Windows Task Scheduler is a registered trigger/integration point.**

A scheduled script alone is insufficient because it cannot be the source of policy, verification, alerting, evidence, and restore-rehearsal state. COSMOS Core schedules backup jobs, checks target hashes, records result evidence, and alerts loudly. Task Scheduler registrations are read back and reconciled as real-OS hooks. Restore rehearsal is an actual scheduled job restoring into an isolated workspace and validating hashes, sentinel identity, and readability before recording success.

---

## MVP cut-line

### Ships in the code phase

1. **Windows service bootstrap**
   - configured-root installer input;
   - machine installation record;
   - sentinel-content verification;
   - role-based resolver;
   - no hardcoded drive literals or parent-walk resolution.

2. **COSMOS Core service**
   - authenticated versioned API;
   - remote authorized access from a second machine;
   - Windows service recovery configuration;
   - authoritative offset-aware clock integration.

3. **Integrity and state primitives**
   - framed append-only ledger;
   - declared-bytes versus consumed-bytes verification;
   - hashes and schema validation;
   - typed absence/result model;
   - projection rebuild;
   - refusal on torn or malformed authoritative state.

4. **Scheduler, queue, and worker MVP**
   - immutable job manifests;
   - priority and lane scheduling;
   - lease/fencing arbiter;
   - per-worker attempt workspaces;
   - Windows Job Object containment;
   - log-first execution;
   - CLEAN/FINDINGS/BROKE outcomes;
   - stale-work report-never-retry behavior.

5. **Registry and rail MVP**
   - node, surface, rail, link, probe, measurement, and policy schemas;
   - CLI/API/DOM/CHAT/OTHER rail types;
   - at least one measured native rail;
   - DOM adapter seam and DOM health/probe representation;
   - rails matrix showing measurement age and UNREACHABLE states.

6. **Return watcher and validator MVP**
   - watcher registration at dispatch;
   - timeout/dead-return handling;
   - path/disk validation;
   - initial source/DOI validator seam;
   - registry-reality reconciliation schedule.

7. **Spend and audit MVP**
   - reserve-before-call gate;
   - expiry-aware reservations;
   - settlement ledger;
   - UNPRICED state;
   - on-demand and scheduled audit report with measurement dates.

8. **KDash backend/API MVP**
   - live queue, rail, spend, lease, health, and backup data;
   - visible panel age;
   - task registry status;
   - evidence pointers.

9. **Real-OS hooks**
   - Task Scheduler registration and read-back;
   - filesystem/timer/signal wakeup pipeline;
   - demonstrated interrupt-driven wakeup;
   - watcher-health reporting.

10. **Backup MVP**
    - policy-defined protected scope;
    - at least one verified off-machine target;
    - per-file hash verification;
    - loud failure;
    - one recorded restore rehearsal.

11. **Spike-tool compatibility work**
    - behavior-card-backed adaptation for `bts_paths`, `tree_lock`, `bts_phone`, and `bts_runner`;
    - contract registry and disposition records;
    - no `.bat` creation;
    - never-delete staging to `_delme` where retirement is needed.

### Explicit seams, not delivered functionality

- Alternate orchestration frontend beyond API/KDash capability.
- Voice input and voice output implementation.
- Federation/KMesh/JMesh/HMesh live operation.
- Peer data-scoping policy implementation beyond schema and enforcement seam.
- Cloud deployment automation beyond deployable service configuration.
- Mobile and desktop applications.
- R2/GDX/ODX implementation details not evidenced in the supplied packet.
- Full migration adapters for all incumbent tools beyond the four spike modules.
- Full behavioral cards for the remaining approximately 135 tools: **UNKNOWN** until the required evidence fan-out is completed.
- W1-W12 definitions, priority, acceptance criteria, and implementation status: **UNKNOWN**. The architecture provides adapter and API seams only.