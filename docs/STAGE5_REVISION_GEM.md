Here is the revised design for COSMOS Stage 5.

### (A) JSON Block: Rubric Compliance

```json
{
  "H1": {
    "id": "H1",
    "how": "State authority is an append-only, hash-chained Journal of framed events, as adopted by the merge. Materialized views (registries, queue state) are rebuildable projections. My design's 'content-addressed state files' are used for large artifacts, with the Journal holding the authoritative pointer (hash). Session closure context manifests, adopted from OA, are recorded in the Journal. A forgotten fact is a missing Journal event or a broken pointer, a detectable integrity failure.",
    "risk": "The primary risk is performance degradation under extremely high write load, as all state changes are serialized through the Journal. This is a known trade-off for consistency and auditability."
  },
  "H2": {
    "id": "H2",
    "how": "The system uses strict, typed data contracts (e.g., Pydantic models) for all configuration, state, and API payloads. Parsing or validation failure at any boundary raises an immediate exception. 'Typed absence' is enforced at the API layer. The Resolver's explicit instantiation at boot and verification of a root sentinel is a fail-fast gate, as agreed in the merge.",
    "risk": "Strictness can reduce resilience to minor, recoverable errors, increasing operational overhead. An audited, explicit override mechanism may be needed for exceptional circumstances."
  },
  "H3": {
    "id": "H3",
    "how": "Failure modes are addressed by the merged consensus: (Lying mount) Ingress envelopes from sandboxes are verified before the Kernel Service records acceptance in the Journal. (Session dying) The Kernel's Arbiter reclaims expired, time-based lease locks. (Two writers) All protected state writes are gated through the Kernel Service using fencing tokens; stale tokens are rejected. (Expiring credit) Spend Gate tracks budgets and denies dispatches. (Dead rail) Rails are probed and marked down, with jobs failing immediately if no valid rail exists.",
    "risk": "The system's resilience depends entirely on the availability and correctness of the central Kernel Service. A bug or failure in this service could halt all coordinated work, representing a single point of failure mitigated by service recovery and durable replay."
  },
  "H4": {
    "id": "H4",
    "how": "Primitives are native to the core framework as per consensus. The Kernel Service centralizes these functions: (I/O) A `CosmosIO` module wraps critical file access with hash verification against the Journal. (Watchers) The Scheduler registers watchers before dispatch. (Validation) A pluggable service validates returns. (Reconciliation) A built-in loop re-probes entities. (Session/Context) The Scheduler creates and passes a `Context` object, including the OA-inspired context manifest. (Adapter) The `Platform` module centralizes OS logic. (Typed Absence) API responses use a specific enum for failure reasons.",
    "risk": "Deep integration of primitives means they are not easily replaceable. A flaw in a core primitive may require a significant, cross-cutting refactor."
  },
  "H5": {
    "id": "H5",
    "how": "Concurrency is owned by the Kernel Service, as per consensus. A lease-based Arbiter provides exclusive access via time-fenced tokens. The Scheduler dispatches jobs from its internal queue projection, respecting priorities and resource locks. The 'compatibility lane' (from OA) is adopted for legacy tools, which run serialized until adapted. All artifacts are written to unique, immutable paths.",
    "risk": "The central Arbiter can introduce latency. High-frequency contention for the same lock could be slower than less safe approaches, a trade-off for correctness."
  },
  "H6": {
    "id": "H6",
    "how": "A dedicated Rail Registry, managed by the Kernel Service, defines all communication links as typed objects with probe methods. The Scheduler finds a valid rail for a job's requirements. As per consensus, DOM is a first-class rail, not a side channel. Routing policy is data, not code, allowing configurations like 'DOM-first with audited API fallback'.",
    "risk": "Continuous background probing of rails could incur cost and network traffic. A bug in probing logic could cause false negatives (marking a healthy rail as 'down')."
  },
  "H7": {
    "id": "H7",
    "how": "COSMOS is configured via a `COSMOS_ROOT`. The Kernel Service verifies this root on startup via a sentinel file, as agreed. The Kernel runs as a persistent service (Windows Service) exposing a single, versioned API. This API is the sole product surface for all clients (KDash, Alternate Frontend, etc.), enabling served mode from WRK7 or a cloud VM.",
    "risk": "Using a single root source, while simple and fail-fast, places a high burden on correct initial configuration. An incorrectly set path can prevent the system from starting."
  },
  "H8": {
    "id": "H8",
    "how": "Incumbent behaviors are preserved through explicit components, as per my original design. A 'Legacy Job Adapter' translates file-drop tasks into modern Scheduler jobs and maps exit codes to worded outcomes. The Journal enforces log-first behavior. Append-over-rename is the default for all state updates via the Journal. These adapters exist within the 'compatibility lane' concept.",
    "risk": "Maintaining adapters for legacy behavior adds complexity. Emulation of filesystem atomicity might not be perfect under all edge cases, a risk that must be accepted during the transition."
  },
  "H9": {
    "id": "H9",
    "how": "The Kernel Service provides real-OS hooks. It maintains the single authoritative, timezone-aware clock. It integrates with the OS scheduler (e.g., Windows Task Scheduler) to ensure the Kernel Service itself is running. It uses OS-native file system watchers and timer events to trigger jobs, enabling interrupt-driven workflows.",
    "risk": "Filesystem watching at scale can be complex and resource-intensive. Unreliable notifications from network-mapped drives could break the interrupt-driven promise, requiring reconciliation loops as a fallback."
  },
  "H10": {
    "id": "H10",
    "how": "The architecture is holistic, with components decoupled via the central API, as per consensus. The MVP ships the Kernel Service and core toolset. Future additions (Alternate Frontend, Voice, Federation) are clients of this stable, versioned API. Their interfaces are provisioned as seams, allowing them to be developed later without a core redesign.",
    "risk": "The API, designed up-front for future components, may be incomplete. This could lead to versioning challenges or require server-side workarounds when those components are eventually built."
  }
}
```

### (B) Prose Design

#### 1. Core Components & Philosophy

The COSMOS architecture is centered around a single, stateful master process: the **Kernel Service**. This service is the heart of the system, acting as the single source of truth and the sole gateway for all state-mutating operations. It runs as a persistent Windows service, enforcing the rules of the mesh. This is the unanimous design adopted by all families.

The core philosophy is **authority through a durable, auditable log**, with all other state being a rebuildable projection. This moves COSMOS from a decentralized, file-based coordination system to a centralized, service-oriented architecture that provides enforcement, auditability, and remote access by design.

#### 2. Component Breakdown

*   **The Kernel Service:** A single process running as a Windows Service. It exposes a secure, versioned gRPC/REST API that is the one and only product surface. It is composed of several internal modules.
    *   **API Server:** The public-facing interface for all clients.
    *   **Journal:** The authoritative, append-only event log. It is implemented as a set of hash-chained, framed JSONL files. Every state change is an event recorded here first.
    *   **Scheduler:** The brain for job dispatch. It maintains an in-memory view of the job queue (rebuilt from the Journal), respects priorities, checks for resource leases, and selects a live rail. It creates a `Context` object for each job, which includes the session-closure context manifest.
    *   **Arbiter:** A lock manager that implements lease-based locking with time-fenced tokens. It is an internal module of the Kernel Service, not a separate process.
    *   **Registries:** In-memory caches (rebuilt from the Journal) for Rails, Tools, and Peers. A background task continuously probes rails, and the results are recorded as new Journal events.
    *   **Commit Gateway:** An internal module that receives publication requests from workers. It verifies the worker's fencing token, validates the incoming data (using the OA-inspired ingress envelope model), and, if valid, writes the new state to the Journal. Workers have no direct write access to protected paths.

*   **The Cosmos SDK (Python Library):**
    *   A client library used by all Python-based tools and agents. It handles communication with the Kernel Service API.
    *   **Path Resolver:** An object explicitly instantiated at process start, which verifies the `COSMOS_ROOT` sentinel before returning any paths, providing fail-fast behavior.
    *   **Platform Adapter:** Abstracts OS-specifics like `\\?\` path prefixing and secure subprocess invocation.
    *   **Legacy Job Adapter:** My design's contribution, integrated here. It translates file-drop conventions into API calls to the Scheduler and maps exit codes to worded outcomes, easing migration.

*   **Data Stores (Managed by the Kernel Service):**
    *   **Journal Store:** A directory of append-only, framed, and hash-chained JSONL files on the local filesystem of the Kernel Service host. This is the canonical state.
    *   **Content-Addressed Store (CAS):** A directory for large, immutable state files and artifacts, where the filename is the content hash. The Journal holds the authoritative pointer to the "live" version of any file. This was a key contribution of my original design.
    *   **SQLite Caches:** The Kernel Service is free to use SQLite as a private, performance-enhancing cache for its internal projections (e.g., of the job queue). This database is never the authority and is never shared via a mount. This synthesizes the queue substrate debate.

#### 3. Data and Control Flow

1.  **Job Submission:** A client makes an API call to the Kernel Service: `POST /api/v1/jobs`.
2.  **Journaling:** The Kernel's API server validates the request and writes a `JOB_SUBMITTED` event to the Journal.
3.  **Dispatch:** The Scheduler sees the new event, updates its internal queue, and selects the job. It requests a lock from the Arbiter, which grants a lease and fencing token, recorded as a `LEASE_GRANTED` Journal event.
4.  **Execution:** The Scheduler dispatches the job via a live rail, passing a `Context` object containing the job ID and fencing token.
5.  **Output & Publication:** The worker writes its outputs to a private workspace. To publish, it calls the `commit` endpoint on the Kernel API, presenting its fencing token and the data. The Commit Gateway validates the token and data, and on success, writes the new state (e.g., a pointer to a new CAS file) to the Journal.
6.  **Settlement:** On completion, the worker's exit is reported back to the Kernel. The Kernel writes a final `JOB_COMPLETED` event to the Journal and releases the lease.

### (C) Answers to OPEN Items and Required Questions

1.  **Service internals layout:** The Kernel Service shall be a single process with distinct internal modules: `api`, `scheduler`, `arbiter`, `journal`, and `registry`. These modules will communicate via well-defined internal interfaces (e.g., Python classes and methods), not via network calls. This modular monolith design allows for a potential future split into microservices if needed (e.g., separating the `scheduler` onto a different machine) by replacing the internal class call with an RPC call, without breaking the external client-facing API. For the MVP, it remains one process.

2.  **Ledger implementation with mount rules:** The ledger will be **framed, hash-chained JSONL files**, a synthesis of the OA and CoPG proposals. This provides human-readability and simple, verifiable append-only semantics. A segment file is written until it reaches a size/time limit, at which point it is closed, its final hash is calculated, and a new segment is created, chaining to the previous hash. Appends to the live segment must be atomic.
    *   **Mount Rules:** The Journal directory itself is private to the Kernel Service host and never shared on a mount. Any data exchange happening over a mount is treated as untrusted ingress. A worker on a sandbox/mount writes an "ingress envelope" to a drop location. The Kernel Service reads this envelope, verifies it, and only then records it as an authoritative event in its private Journal. This defeats the "lying mount" failure class.

3.  **DOM worker containment:** A DOM Worker is a specialized, trusted process running on a machine with a graphical environment.
    *   **Identity:** It registers with the Kernel Service as a "DOM Rail" and has a unique cryptographic identity, just like any other worker.
    *   **Session/Profile Management:** The DOM worker is responsible for managing browser instances and profiles. It should use separate, ephemeral profiles for each job by default to ensure isolation, unless a job explicitly requires a persistent session (which would be a leased resource managed by the Arbiter).
    *   **Failure Containment:** If the browser (or the worker process itself) dies mid-job, the OS-level process supervisor for the worker will report the failure to the Kernel Service. The Kernel Service will then mark the job as `BROKE` (with reason `WORKER_DIED`) and, critically, the time-based lease on any resources will expire via the Arbiter's clock, allowing for safe cleanup and preventing a permanently locked state. The return watcher for that job will time out, triggering an audited failure event.

4.  **Lock enforcement mechanism (DEFENSE):** I concede to the merge's stronger model. My original Arbiter is correct, but the addition of OA's fenced gateway for all commits provides a superior enforcement guarantee. A worker not only needs a token to start work but must present it again to finalize the work. This closes a potential race condition and is adopted.

5.  **Queue substrate (CONCESSION/SYNTHESIS):** I concede that using SQLite *as the authority* is incorrect in this distributed model. The merge's synthesis is correct and adopted: **canonical state is the immutable Journal and manifests; any database is a service-private, disposable projection/cache**. This satisfies my original desire for ACID-like transactional updates (now handled by the Kernel's serialized writes to the Journal) while resolving the shared-mutable-state problem.

### (D) MVP Cut-line

#### What Ships in the Code Phase (MVP):

*   **The Kernel Service:** The core Windows service as a single process with the internal `api`, `scheduler`, `arbiter`, `journal`, and `registry` modules.
*   **The Journal/Ledger:** Implementation of framed, hash-chained JSONL files, managed exclusively by the Kernel Service.
*   **The SDK & Adapters:** The core Cosmos SDK, including the explicit `PathResolver`, and the `Legacy Job Adapter`.
*   **Core Primitives:** Implementation of lease/fencing token management, the commit gateway, and the "compatibility lane" for serialized legacy jobs.
*   **Ported Spike Modules:** `tree_lock`, `bts_phone`, `bts_runner`, `bts_paths` logic ported to run as jobs within the new system, using the SDK and adapters.
*   **Basic KDash Backend:** The Kernel API will provide endpoints for system status, job queue, and rail status to make the existing KDash panels live.
*   **Backup & Rehearsal Tool:** The core backup and restore-rehearsal jobs, schedulable by the Kernel, with results written to the Journal. This was a strong point of my original design and is retained.
*   **Installer & Sentinel:** A script to set up the `COSMOS_ROOT`, create the sentinel file, and install the Kernel as a Windows Service.

#### Seams for Future Work (Post-MVP):

*   **Alternate Frontend & Voice Control:** UNKNOWN. These are pure clients of the Kernel API. The API is the seam.
*   **Federation (KMesh/JMesh/HMesh):** This is a seam. Federating will involve teaching one Kernel to be a client of another Kernel's API.
*   **Robust DOM Worker:** A prototype DOM worker will be built to prove the rail concept, but a fully hardened, multi-browser, security-sandboxed implementation is post-MVP.
*   **Full Tool Porting:** The ~140 remaining tools will be ported incrementally post-MVP.
*   **Cloud Deployment:** The service is designed to be cloud-deployable, but automated infrastructure for this is post-MVP.
*   **Grok Addendum:** UNKNOWN. Awaiting input. The modular design should allow integration as a new rail type, client, or validation service.