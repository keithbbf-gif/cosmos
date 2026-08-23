Reading the file _copg_prompt.txt to get the prompt content so it can be answered directly. Running a file view.

● Read _copg_prompt.txt
  └ 1 line read

Reading the large prompt file in three line ranges (1-400, 401-800, 801-1200) to capture its full content for answering. Running parallel view calls.

✗ Read _copg_prompt.txt
  └ view_range out of bounds

● Read _copg_prompt.txt
  └ L401:800 (69 lines read)

● Read _copg_prompt.txt
  └ L1:400 (271 lines read)

(A) JSON block for H1–H10
[
  {"id":"H1","how":"Converge state into append-only, signed event streams per artifact (ledgers) plus a registry index that records canonical identities and provenance. On write, a writer appends an event and then the system performs a read-back probe and integrity check; reconciliation uses the ledger history to compute durable state. This makes forgotten facts detectable and repairable by replay/merge.","risk":"Append-only storage must be atomic on a single-volume; cross-volume semantics need arbiter coordination to avoid split-brain."},
  {"id":"H2","how":"Enforce fail-loud via strict typed-return model: all APIs return typed absences (NOT_FOUND / OUT_OF_CLOCK / NOT_IN_CORPUS / UNPRICED) and all path/manifest/claim errors are fatal unless an explicit, auditable fallback is selected. Selftests include negative-controls and the runtime refuse-to-run on torn/unparseable state.","risk":"Operational friction: strict refusal increases visible failures during porting and demands clear operator workflows."},
  {"id":"H3","how":"Design for named failure modes with layered defenses: (1) lease+fencing tokens and arbiter-issued claims for cross-volume/cluster coordination; (2) append-only ledgers and read-back verification to detect lying/corrupting mounts; (3) per-worker identity, timeouts and OS-job-object integration on Windows to avoid orphaned descendants; (4) reservation checks for credit/rail failures before spend. Each mode has a probe+guardian path that refuses unsafe actions.","risk":"A resident arbiter service is a single moving part that must itself be highly available and trusted; failure modes there must be rehearsed."},
  {"id":"H4","how":"Make the seven OS primitives first-class modules: integrity-verified I/O layer (byte-counts and hashes), return-watchers (subscription/watch mechanism tied to dispatch), return-validation pipeline (pluggable validators), registry-reality reconciler (periodic probes + audit), session/context manager (per-stream OS-captured transcripts), platform adapter layer (encoding/path/line-ending normalization), typed absence embedded in all APIs. These are library-level primitives used by all subsystems, not adapters bolted on later.","risk":"Requires early audit and discipline in every module; retrofitting across 149 tools is work-heavy."},
  {"id":"H5","how":"Enforce concurrency via a scheduler that owns leases and priorities. Locks implemented as lease+fencing tokens recorded to append-only ledger; arbiter issues short leases with fencing tokens; local filesystem helpers use atomic rename where available; advisory locks are forbidden past N>1. Scheduler maintains per-lane single-threaded execution, global priority queues, and per-worker identity embedded in every artifact.","risk":"If the arbiter is unavailable, the system must decline cross-volume operations, impacting availability unless fallback policies are explicitly approved."},
  {"id":"H6","how":"Total connectivity is registry-driven: every rail (CLI/API/DOM/CHAT/other) is first-class in the Registry with discovery metadata, supported probe handlers, and per-rail ledgers. DOM-first routing is expressed as a policy layer inside the scheduler: DOM links are preferred and probed; API/CHAT fall back only when DOM is explicitly absent. Probes record age and measurement results in the registry.","risk":"DOM-first imposes integration needs for legacy tools that do not expose DOM; adaptation layers required."},
  {"id":"H7","how":"Installer writes one configured root (settable during install); a sentinel file with signed metadata binds root; resolver uses the sentinel to fail-fast if root mismatches. COSMOS runs as a service (Windows service or cloud daemon) with remote API authentication; the product surface is the KDash API. Distribution includes a service-mode installer and a WRK7 service profile.","risk":"Service-mode increases operational complexity on heterogeneous hosts; installers must be honest about platform limitations."},
  {"id":"H8","how":"Preserve incumbent behaviors by codifying them as required invariants: claim-by-rename semantics are supported when single-volume; otherwise arbiter-issued claim tokens are required. Three-worded outcomes (done/findings/failed) become explicit output directories; log-first policy is enforced by opening and writing logs before executing; helper convention (underscore-prefix) enforced in-runner; ledger append-only requirement is documented and enforced for mounts; priority+concurrency preserved by scheduler policies.","risk":"Complete preservation requires precise behavioral contracts for many small tools; some tools will need adapter layers."},
  {"id":"H9","how":"Real-OS hooks are native: one authoritative clock source (configurable NTP/host-RTC) is used by the arbiter and ledger timestamps; scheduler integrates with OS task scheduler and job objects (Windows) for interrupts and process control; file-change/timer/signal watchers drive interrupt-driven wakeups rather than pure polling. Heartbeats include local+epoch+UTC+lane to avoid misreads.","risk":"Dependence on host facilities means heterogeneous host behavior (clock skew, differing job-object semantics) must be tested and tolerated."},
  {"id":"H10","how":"MVP separability achieved by explicit seams: core registry + scheduler + filesystem queue + runner + KDash API form the MVP. Frontier features (voice, alternate frontend, federation) are exposed as API surfaces only. The architecture documents which components are required for the MVP and which are plug-ins, enabling a code-phase deliverable that does not require redesign to support later features.","risk":"Some incumbent features (e.g., full federation) are deferred — integration risk remains unless interfaces are stable and tested."}
]

(B) Design (prose — components, data flows, deployment, enforcement)
Overview
COSMOS is a distributed, registry-driven mesh with a scheduler-centered control plane, append-only artifact ledgers, and a small trusted arbiter for cross-volume coordination. The design favors immutable manifests, read-back probes, typed absences, and a single-configured root per install. The KDash live backend is the product API; frontends (including voice) are API clients.

Components
- Registry service (local JSON/append-index + optional replicated store): records nodes, rails, tool contracts, lane names, sentinel, and probe metadata. Single authoritative per-install.
- Arbiter service (lightweight resident daemon/service): issues fenced leases, mediates cross-volume claims, signs fencing tokens, and validates append-only ledger anchors for multi-volume operations. Stateless recovery via ledger replay.
- Scheduler (per-install): owns lanes, priority queues, task dispatch, identity embedding, and enforces single-threaded lane execution. Integrates with OS job objects (Windows) for process control and timeouts.
- Queue substrate: immutable manifest files per job (filesystem-first) + local SQLite side-cache for index/performance. Job lifecycle: create manifest → append ledger entry → arbiter claim (if cross-volume) → scheduler assigns → runner executes → runner appends outcome event → read-back verification.
- Runner (per-host worker): enforces helper conventions (_-prefix), opens log-first (RUNNING + cmd), spawns controlled subprocesses (job objects), writes append-only ledger entries, emits heartbeat with identity + offsets, enforces per-job timeout and writes RED - TIMED OUT on timeout.
- Ledgers and logs: append-only jsonl ledgers per lane/artifact, fsync guaranteed; ledger entries include identity, epoch+UTC offset, hash of content, and optional HMAC signed by arbiter if cross-volume.
- Return-validation pipeline: validators for DOI, quotes, path checks, encoding, and typed absence enforcement; validators run before any return is accepted.
- Probe/heartbeat subsystem: per-worker heartbeat files discovered by glob; heartbeats carry local+epoch+UTC+lane and are used by monitoring and takeover detection.
- KDash live backend & API: one service exposing product endpoints (health, registry, audit, run control). KDash and frontend may be separate processes but share the same API surface and auth model.
- Backup subsystem: scheduled backup jobs that perform hashed, rehearsed restores to off-machine targets; backup is implemented as scheduled jobs run by elevated ops worker, with restore rehearsals recorded and audited.
- Platform Adapter: encoding, path normalization, line endings, MAX_PATH handling, canonicalization (case normalization), and quoting, isolated from tools.

Data flows
1. Authoring/Install: installer writes sentinel in configured root, registry initialized, arbiter anchor registered.
2. Job submission: client writes job manifest to queue dir → appends ledger event → scheduler probes and assigns → if cross-volume or contested, arbiter issues fencing token; runner reads manifest, writes RUNNING log entry, executes guarded subprocess, writes outcome event.
3. Verification: Read-back probe validates outputs, validators run, typed absence is enforced. If outcome is discrepancy: exit code 2 (FINDINGS), and findings written to done\findings\.
4. Audit & backup: periodic audit reads ledgers and registry, re-probes rails, writes audit ledger events; backup jobs run and produce hash-verified archives; rehearsals recorded.

What runs where
- Registry + Arbiter + KDash: recommended as services on WRK7/SRV hosts (Windows service or cloud). Arbiter may be colocated with Registry for small installs.
- Scheduler: local to install root, runs as service.
- Runners: on worker hosts; per-host single runner per lane or multiple runners with identity enforced.
- Frontend: client-side apps (desktop/phone) interacting with KDash API.
- Backup targets: off-machine storage (LAN or cloud).

Enforcement
- Ledgers + arbiter signatures enforce lease/fencing; all modifications go through append-only pipeline.
- Negative controls in selftests and gate checks at install/service start.
- Typed returns and fail-loud behavior enforced by return-validation pipeline.
- No last-writer-wins: every writable shared artifact is mediated by scheduler/arbiter and recorded in ledgers.

(C) Explicit answers to the rubric's six REQUIRED QUESTIONS
1) Lock enforcement mechanism
Chosen: lease + fencing token + append-only event ledger, mediated by a lightweight resident arbiter service when cross-volume or multi-host coordination is required. Justification: this covers the named failure modes (lying mounts, split-brain, two writers across sandbox/native) by providing a central authority for fencing tokens and auditable append-only records. The arbiter earns its rent by enabling safe cross-volume claims and generating signed tokens that prevent takeover without a recorded lease; on single-volume local installs the filesystem atomic rename + ledger is used opportunistically to reduce arbiter dependency.

2) Queue substrate
Chosen: filesystem manifests (immutable job files) as canonical substrate, with a local SQLite index as a performance/cache layer only. Justification: filesystem manifests preserve immutability and fit existing expectations (append-over-rename when needed) and avoid shared mutable DB contention across mounts. SQLite is used for local query performance and index operations but is not the single source of truth for distributed coordination (that role is the manifests + arbiter ledger).

3) Resolver timing
Chosen: explicit-instantiation (object/class) with sentinel-verified root and fast fail on instantiation. Justification: import-time side-effects risk hidden failures; explicit instantiation surfaces root mismatches and sentinel problems at the point of constructing the resolver, enabling fail-loud behavior (H2) and safer unit testing. If code demands import-time checks for critical boot-time validation, those calls use the same explicit-instantiation path during service start.

4) Where DOM lanes live in the scheduler design (H6)
DOM lanes are first-class lanes within the scheduler. The scheduler exposes DOM watchers/dispatchers that prefer DOM routes; DOM dispatch is implemented as a plugin to the scheduler's dispatch matrix so DOM probes are part of the scheduler’s probe lifecycle. DOM links are discovered via the Registry and preferred for routing; fallback to API/CHAT is explicit and auditable.

5) KDash live backend + frontend API: one service or two, and why
Chosen: two components with a single API surface (seam): a KDash backend service (data + control plane) and optional lightweight frontend processes (UI/voice clients) that consume the same API. Justification: separation allows the backend to be served (WRK7/cloud) and scaled independently; the frontend is an API client that can be replaced without backend redesign. The API surface is the product contract and must remain stable for incremental work.

6) Backup subsystem placement
Chosen: backup implemented as scheduled jobs run by an elevated ops worker (service) with a kernel-integrated rehearsal mechanism. Backups are scheduled via the scheduler with a backed ledgered plan and rehearsals are performed to an off-machine target and hash-verified. Restore rehearsals are mandatory: a backup job includes a rehearsal run that restores to a scratch area and verifies hashes. Justification: kernel service level execution gives appropriate privileges; rehearsals provide the required auditable assurance.

(D) MVP cut-line: what ships in code phase, what is a seam
MVP (ship in code phase)
- Installer that sets sentinel-configured root and initializes Registry.
- Registry service (local) with a JSON+ledger index and probe API.
- Scheduler core (lane model, priority queues, single-threaded lane execution).
- Filesystem immutable-manifest queue substrate + local SQLite index.
- Runner that enforces helper convention, log-first behavior, job-object-based subprocess control (Windows), heartbeat, and append-only local ledgers.
- Append-only ledger implementation with fsync and read-back verification.
- Arbiter prototype: lightweight resident service supporting fencing tokens for cross-volume claims (minimal secure token issuance + verification).
- Return-validation pipeline with core validators (path checks, encoding, typed absence).
- KDash backend MVP exposing basic API: health, registry, run submit/status, audit read.
- Backup job runner + one off-machine target support + rehearsal flow.
- Selftest harness including negative controls for each shipped piece.

Seams (deferred or explicit interfaces)
- Federation and full peer sync (design interfaces provided; implementation deferred).
- Voice and alternate frontend (exposed as API clients; not implemented in MVP).
- Advanced per-tool adapters and full 149-tool behavioral cards (adapter scaffolds shipped; cards produced in follow-ups).
- Full arbiter HA and replication (prototype shipped; HA optional in later increments).

UNKNOWNs and honest trade-offs
- Unknown: exact arbiter HA design and its operational practices for large multi-node meshes — MVP uses single arbiter per install; cloud/high-availability patterns marked UNKNOWN until field tests.
- Unknown: optimal balance between filesystem-manifests and SQLite for extreme-scale workloads — telemetry required post-MVP.
- Risk tradeoff: enforcing strict fail-loud increases immediate visible failures; operator flows and migration tools are required and scoped as immediate follow-ups.

Acceptance alignment (how this meets H1–H10)
- H1: append-only ledgers + read-back probes satisfy carry-over stability.
- H2: typed absences + fail-loud resolver enforce no silent fallback.
- H3: lease+fencing + job-object integration and read-back verification defend named failure modes.
- H4: primitives implemented as core libraries used everywhere.
- H5: scheduler + arbiter + per-lane locks enforce concurrency.
- H6: registry-driven rails and DOM-first policy within scheduler.
- H7: sentinel-configured root and service deployment model supported.
- H8: incumbent behaviors codified and enforced in runner and ledger patterns.
- H9: authoritative clock, scheduler integration, interrupt-driven wakeups included.
- H10: MVP seams defined so the code phase delivers a coherent deployable product.

Operational notes (short)
- Negative controls in CI and selftests are required for each shipped component.
- Heartbeats and ledgers are discoverable by glob and audited regularly.
- Stale jobs reported, never auto-retried; operators requeue after deliberate reconciliation.

End of deliverable.

