Here is a design for COSMOS.

### (A) JSON Block: Rubric Compliance

```json
{
  "H1": {
    "id": "H1",
    "how": "State is persisted in a transactional, append-only event log (the Journal) and a set of versioned state files (e.g., registries) stored under a content-addressable scheme. The Kernel Service ensures that all state changes are journaled before being committed. 'Forgetting' a fact means the Journal entry is missing or the state file hash doesn't match the Journal's pointer, which is a detectable, auditable, and recoverable bug.",
    "risk": "The primary risk is performance degradation under extremely high write load, as every state change requires a transactional write to the Journal service. If the Journal service becomes a bottleneck, the entire mesh's state update throughput is affected."
  },
  "H2": {
    "id": "H2",
    "how": "The system employs strict, typed data contracts (Pydantic models) for all configuration, state, and API payloads. Parsing or validation failure at any boundary (file read, API call) raises an immediate exception, preventing the use of torn, incomplete, or malformed data. There are no silent fallbacks; 'typed absence' (e.g., NOT_FOUND vs. TIMED_OUT) is enforced at the API layer, and path resolution fails with an exception if a sentinel file is missing.",
    "risk": "This strictness can reduce resilience to minor, recoverable errors (e.g., an extra comma in a non-critical config file). It may require manual intervention for issues that a more lenient system might ignore, increasing operational overhead initially."
  },
  "H3": {
    "id": "H3",
    "how": "Failure modes are addressed by: (Lying mount) Integrity-verified I/O checks hashes against the Journal. (Session dying) The Kernel Service's Arbiter reclaims expired, time-based lease locks. (Two writers) All shared state writes are gated through the Kernel Service; direct file access is for immutable artifacts only, preventing last-writer-wins. (Expiring credit) Spend Gate service tracks budgets in real-time and denies dispatches that would exceed them. (Dead rail) The Rail Registry marks rails down after failed probes and reroutes traffic based on policy; jobs fail immediately if no valid rail exists.",
    "risk": "The system's resilience is now heavily dependent on the availability and correctness of the central Kernel Service. A failure or bug in the Kernel Service could halt all coordinated work across the entire mesh, creating a single point of failure."
  },
  "H4": {
    "id": "H4",
    "how": "Primitives are native to the core framework: (I/O) A `CosmosIO` module wraps all critical file access with hash verification against the Journal. (Watchers) The Scheduler, upon dispatch, registers an expected return with a unique job ID; the Kernel receives all returns and matches them to watchers. (Validation) A `Validation` service is a pluggable component used before state commitment, with rules for paths, DOIs, etc. (Reconciliation) The `Registry` service has a built-in-loop to periodically re-probe entities and update their status with a new timestamp. (Session/Context) The `Scheduler` creates and passes a `Context` object for every job. (Adapter) The `Platform` module centralizes all OS-specific logic (paths, shell quoting). (Typed Absence) API responses use a specific enum to distinguish failure reasons, enforced by the shared data models.",
    "risk": "Integrating all primitives so deeply means they are not easily replaceable. If a fundamental flaw is found in the design of one primitive (e.g., the watcher mechanism), it may require a significant, cross-cutting refactor of the core services rather than a simple module swap."
  },
  "H5": {
    "id": "H5",
    "how": "Concurrency is owned by the Kernel Service. A lease-based lock arbiter service, using time-fenced tokens, provides exclusive write access to logical resources. The Scheduler assigns jobs from a transactional SQLite queue, respecting priorities and resource locks. Every artifact generated (logs, outputs) is written to a unique, immutable path containing the worker's identity and job ID, eliminating shared mutable files and last-writer-wins conflicts.",
    "risk": "The reliance on a central arbiter for locking can introduce latency. A high frequency of short-lived tasks all contending for the same lock could be slower than a filesystem-based approach, as every lock request/release is a network roundtrip to the Kernel Service."
  },
  "H6": {
    "id": "H6",
    "how": "A dedicated Rail Registry, managed by the Kernel Service, defines all communication links (API, CLI, DOM, CHAT) as typed objects with specific probe methods. The Scheduler queries this registry to find a valid, 'live' rail for a given job's requirements, enforcing a DOM-first policy by default. Rails are continuously probed in the background; a failed probe immediately marks a rail as 'down' with a timestamp, removing it from eligibility for new jobs.",
    "risk": "The continuous background probing of all rails, especially against metered third-party APIs, could incur non-trivial cost and network traffic. A bug in the probing logic could also lead to false negatives (marking a healthy rail 'down') or, worse, denial-of-service against a sensitive endpoint."
  },
  "H7": {
    "id": "H7",
    "how": "COSMOS is configured via a single `COSMOS_ROOT` environment variable at install time. The Kernel Service verifies this root on startup by checking for a sentinel file (`.cosmos_root`). The Kernel itself runs as a Windows service (or systemd unit on Linux) exposing a gRPC/REST API. This API is the product surface, used by all clients (KDash, Alternate Frontend, remote CLI), enabling served mode from WRK7 or a cloud VM.",
    "risk": "Using a single environment variable as the root source, while simple, can be fragile. An incorrectly set or missing variable can prevent the entire system from starting. A more robust discovery mechanism (e.g., searching standard locations) was deliberately avoided for fail-fast behavior, but this places a higher burden on correct initial configuration."
  },
  "H8": {
    "id": "H8",
    "how": "Incumbent behaviors are preserved through specific components. A 'Legacy Job Adapter' translates file-drop tasks into modern Scheduler jobs, preserving claim-by-rename semantics virtually. It maps exit codes (0, 2, other) to the three worded outcomes (CLEAN, FINDINGS, BROKE). The Journal enforces log-first. The Scheduler's policy is 'report-never-retry' for stale jobs. Append-over-rename is the default for all state updates via the Journal. Helper conventions (`_`-prefix) are enforced by the job discovery process.",
    "risk": "Maintaining adapters for legacy behavior adds complexity and a potential performance penalty. The `claim-by-rename` emulation, in particular, might not perfectly replicate the atomicity guarantees of the original filesystem operation under all edge cases, potentially introducing subtle race conditions."
  },
  "H9": {
    "id": "H9",
    "how": "The Kernel Service provides real-OS hooks. It maintains the single authoritative, timezone-aware clock. It integrates with the OS scheduler (e.g., Windows Task Scheduler) only to ensure the Kernel Service itself is running; all COSMOS-internal scheduling is handled by the Kernel's own priority scheduler. It uses OS-native file system watchers (e.g., `watchdog` library) and timer events to trigger jobs, enabling interrupt-driven workflows instead of polling loops.",
    "risk": "Filesystem watching at scale can be complex and resource-intensive. Watching a large and active tree of files might overwhelm the service with events, and there are known edge cases (e.g., with network-mapped drives) where notifications can be unreliable or lost, which would break the interrupt-driven promise."
  },
  "H10": {
    "id": "H10",
    "how": "The architecture is holistic, but components are decoupled via the central API. The MVP ships the Kernel Service (with Scheduler, Arbiter, Journal, Registries) and the core toolset. The Alternate Frontend, Voice Control, and Federation modules (KMesh, etc.) are seams; they are simply clients of the Kernel's public API. They can be developed and shipped later without any redesign of the core COSMOS architecture, as their interfaces are already provisioned.",
    "risk": "The risk is that the API, designed 'up-front' for these future components, may be incomplete or based on incorrect assumptions about their needs. This could lead to API versioning challenges or require awkward server-side workarounds when those components are eventually built, partially undermining the 'no redesign' goal."
  }
}
```

### (B) Prose Design

#### 1. Core Components & Philosophy

The COSMOS architecture is centered around a single, stateful master process: the **Kernel Service**. This service is the heart of the system, acting as the single source of truth and the sole gateway for all state-mutating operations. It runs as a persistent Windows service on a primary node (like WRK7) or as a daemon in the cloud, enforcing the rules of the mesh. All other components, whether they are local tools, remote agents, or user frontends, are clients of the Kernel Service's API. This design moves from a decentralized, file-based coordination system (BTS_MESH) to a centralized, service-oriented architecture, directly addressing the requirements for enforcement, auditability, and remote access.

#### 2. Component Breakdown

*   **The Kernel Service (Windows Service on WRK7/Cloud VM):**
    *   **API Server:** Exposes a secure gRPC API (with a REST/JSON gateway for web clients). This is the single product surface for KDash, the Alternate Frontend, and any other authorized client.
    *   **Scheduler:** The brain for job dispatch. It reads from the SQLite-based Job Queue, respects priorities, checks resource availability via the Arbiter, and selects a live rail from the Rail Registry to execute the job. It creates a `Context` object for each job, containing identity, tracing info, and secrets.
    *   **Arbiter (Lock Manager):** An internal module that implements lease-based locking. Clients request a lock on a logical resource (e.g., `dissertation_corpus`). The Arbiter grants a time-fenced token. Only the holder of a valid token can perform write operations on that resource, which are still proxied through the Kernel. It reclaims expired leases, solving the "session dying without release" problem.
    *   **Journal:** A transactional, append-only log (using SQLite with `WAL` mode for concurrent read/write). **Every single state change in the system** (a job dispatch, a lock acquired, a registry update, a file written) is first recorded as an event in the Journal. State files on disk are content-addressed (their filename is their hash), and the Journal stores the pointer (the hash) to the current "live" version. This provides a complete, auditable history and a mechanism for recovery and integrity verification.
    *   **Registries (In-memory, backed by Journal/State files):**
        *   **Rail Registry:** Tracks all communication links (APIs, CLIs, DOMs). A background task continuously probes each rail, updating its status (`UP`, `DOWN`, `DEGRADED`) and last-probed timestamp.
        *   **Tool Registry:** The authoritative source for all 149+ tools, their contracts, and implementations (or recorded decisions for adaptations).
        *   **Peer Registry:** Manages identity and capabilities of all nodes in the mesh.
    *   **Event Watcher:** Listens for OS-level events (file changes via `watchdog`, timers) and translates them into jobs for the Scheduler, enabling interrupt-driven execution.

*   **The Cosmos SDK (Python Library):**
    *   A client library used by all Python-based tools and agents. It handles communication with the Kernel Service API.
    *   **Path Resolver:** An object instantiated with the `COSMOS_ROOT` path. It provides role-based path resolution (`resolver.get_path('archive')`). On instantiation, it verifies the root by checking for the `.cosmos_root` sentinel file, providing fail-fast behavior.
    *   **Platform Adapter:** A module within the SDK that abstracts OS-specifics like `\\?\` path prefixing, line endings, and secure subprocess invocation using Job Objects on Windows to prevent orphaned processes.
    *   **Integrity-Verified I/O:** Provides functions like `sdk.io.read_verified('path/to/file')` which automatically fetches the expected hash from the Kernel Service and validates the file on read.

*   **The Job Queue (SQLite Database):**
    *   A single SQLite file (`queue.db`) managed exclusively by the Kernel Service. It replaces the filesystem-manifest queue. Using a database provides transactional integrity (ACID), priority support via a column, and efficient querying, solving the "two ticks taking one job" problem definitively. Jobs are records in a table, not files in a directory.

*   **Backup Subsystem (Scheduled Tool):**
    *   Runs as a high-priority, scheduled job within COSMOS itself, not as a separate kernel service. It reads its configuration from the Tool Registry.
    *   **Process:** It queries the Kernel for the list of critical state files (by querying the Journal). It then hashes each file, streams it to one or more configured targets (local, LAN, R2), and verifies the remote hash against the source hash. The results (success/failure, hashes, timings) are written back to the Journal.
    *   **Restore Rehearsal:** Is a specific job type. A `rehearse-restore` job pulls a specified backup from a remote target to a temporary location, hash-verifies it against the original manifest, and reports success/failure without touching the live system. This is scheduled to run periodically, proving restorability.

#### 3. Data and Control Flow

1.  **Job Submission:** A user on the Alternate Frontend wants to run a tool. The frontend makes an API call to the Kernel Service: `POST /api/v1/jobs`.
2.  **Queueing:** The Kernel's API server validates the request, creates a job record in the `queue.db` with `PENDING` status and a priority, and logs the creation event in the Journal.
3.  **Dispatch:** The Scheduler, in its next cycle, sees the pending job. It requests a lock from the Arbiter for any required resources. It queries the Rail Registry for a live rail.
4.  **Execution:** The Scheduler dispatches the job via the chosen rail, passing a secure `Context` object containing the job ID and any necessary credentials. For a local Python script, this involves invoking the Python interpreter with the script path and the context as an environment variable or argument.
5.  **Execution Logging:** The running script uses the Cosmos SDK to log its progress. Each log entry is an API call to the Kernel, which appends it to the job's specific, immutable log file and records the write in the Journal.
6.  **Return:** Upon completion, the script exits with a specific code (0, 2, etc.). The rail captures the exit code and any output.
7.  **Settlement:** The return value is sent back to the Kernel Service. The Kernel updates the job's status in the queue (to `CLEAN`, `FINDINGS`, or `BROKE`), releases its locks in the Arbiter, and records the final outcome in the Journal. The "return watcher" is fulfilled.

### (C) Answers to Required Questions

1.  **Lock enforcement mechanism:** **Arbiter service.** The Kernel Service includes a mandatory, non-optional arbiter module. It provides time-based leases (fencing tokens) for logical resources. This is chosen over OS locks (which don't work across machines/mounts and can be fragile) and a simple lease ledger (which requires clients to be honest). The arbiter earns its rent (S1) because it is not a *new* daemon; it's an integral component of the required-anyway **Kernel Service**. It provides absolute enforcement, solves the "dead session" problem by expiring leases, and provides a central point for auditing lock contention, which is a key stability requirement (H3, H5).

2.  **Queue substrate:** **SQLite.** A single SQLite database file (`queue.db`), managed exclusively by the Kernel Service, is used for the job queue. This is chosen over filesystem manifests because it provides transactional ACID guarantees out of the box, preventing race conditions like two workers claiming the same job (H5). It natively supports priority, complex queries, and is more performant for a central scheduler than scanning a directory of files. It is a "shared mutable file," but its access is mediated by a single process (the Kernel Service), which is a safe and standard database architecture, thus not violating the "last-writer-wins" prohibition.

3.  **Resolver timing:** **Explicit instantiation.** The Path Resolver is a class that is instantiated explicitly at the start of a process (e.g., `resolver = PathResolver(root=os.environ['COSMOS_ROOT'])`). This combines the best of both worlds: it fails fast (instantiation fails if the root is invalid, satisfying the incumbent's proven `import-time` benefit) but avoids the pitfalls of import-time side effects, which make code harder to test and reason about. This explicit dependency injection is a more robust software pattern and directly addresses H2 (no plausible-path resolution).

4.  **Where DOM lanes live in the scheduler design:** DOM lanes are treated as a specialized, high-priority **Rail Type** in the Rail Registry (H6). Jobs that require DOM interaction will specify `rail_type: 'DOM'` in their definition. The Scheduler will then query the Rail Registry for a live, available DOM rail. A "DOM Worker" process (likely a separate, dedicated agent that can control a browser instance) registers itself as a DOM rail with the Kernel. The Scheduler dispatches the job to that worker, which then executes the DOM manipulation. Probes for DOM rails involve launching the browser and performing a simple, cheap action (e.g., loading a blank page) to ensure the control channel is alive. Watchers work the same way: the Scheduler logs the dispatch and waits for a return from the DOM worker.

5.  **The KDash live backend + frontend API:** **One service.** The KDash live backend and the new Alternate Frontend API are powered by the **same single Kernel Service**. KDash is simply another client of this API. The Kernel's API will expose endpoints like `/api/v1/system-health`, `/api/v1/jobs/status`, and `/api/v1/rails/list` which both frontends will call. This minimizes moving parts (S1), ensures data consistency, and makes the API the true product surface from day one (H7). The visible "age" on KDash panels is derived directly from the `last_probed` or `last_updated` timestamps served by the API for each piece of data.

6.  **Backup subsystem placement:** **Scheduled tool.** The backup system is a tool that runs as a scheduled job within COSMOS, not a standalone kernel service. This is justified because: 1) It leverages the existing COSMOS infrastructure (scheduling, logging, identity, error handling) without adding a new daemon (S1). 2) A backup is a periodic task, not a persistent service. 3) **Restore rehearsal is designed in** as a separate, non-destructive job type (`rehearse-restore`) that is also scheduled. This job pulls data from a backup target, verifies it, and reports back, proving the backup's integrity and the system's ability to restore *without* the risk of a developer manually running a script. This makes rehearsal an automated, first-class, and auditable operation.

### (D) MVP Cut-line

#### What Ships in the Code Phase (MVP):

*   **The Kernel Service:** The core Windows service with the API server, Scheduler, Arbiter, Journal (SQLite-based), and Registries (Tool, Rail, Peer). It will be capable of running jobs.
*   **The Cosmos SDK:** The essential client library with the Path Resolver, Platform Adapter, and basic API client for submitting jobs and logging.
*   **The SQLite Queue:** The `queue.db` schema and the Kernel's logic to manage it.
*   **Ported Spike Modules:** `tree_lock`, `bts_phone`, `bts_runner`, and `bts_paths` logic will be ported to use the new SDK and run as jobs within the new system. The `bts_runner` logic is split: the file-watcher part moves into the Kernel's Event Watcher, and the job execution logic becomes a "legacy job adapter."
*   **Basic KDash Backend:** The Kernel API will provide the core endpoints needed to make KDash's existing panels "live" (system status, queue depth, rail status).
*   **The Backup Tool:** The core backup and restore-rehearsal jobs, schedulable by the Kernel.
*   **Installer:** A script to set up the `COSMOS_ROOT`, install the Kernel as a Windows Service, and configure a basic set of tools and rails.

#### Seams for Future Work (Post-MVP):

*   **Alternate Frontend:** UNKNOWN. It is a pure client of the Kernel API. A mock client or Postman collection will be used to validate the API surface during MVP development.
*   **Voice Control:** UNKNOWN. This is a layer on top of the Alternate Frontend/API. The API is designed to be agnostic to the input modality; no core work is needed. This is a seam.
*   **Federation (KMesh/JMesh/HMesh):** This is a seam. The Peer Registry and the Kernel API are designed to support peer-to-peer communication, but the initial implementation will be for a single-Kernel mesh. Federating will involve teaching one Kernel to be a client of another Kernel's API.
*   **Full Tool Porting:** The MVP will only port the spike modules and a handful of critical tools. The other ~140 tools will be ported incrementally as jobs that use the new SDK.
*   **Advanced KDash Features:** Richer interfaces and new panels are frontend work that can consume the stable backend API post-MVP.
*   **DOM Worker/Rail:** A prototype DOM worker will be built to prove the concept, but a fully robust, multi-browser implementation is a post-MVP task.