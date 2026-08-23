# COSMOS STAGE 4 — ARCHITECTURE DESIGN
**Family:** Grok 4.6 (Cursor lane) · **Date:** 2026-08-23 · **Independent return**
**Inputs used:** signed Stage 1 goal v5 · Stage 4 rubric (fixed before designs) · Stage 2 merge of scar/incumbent findings · Stage 2(a) observed behavior of the four spike modules · port survey measurements · pipeline standing rules.
**Inputs not used:** any other family's Stage 4 design. This return does not assume one exists.

A docstring is a claim. Scar-derived primitives are requirements. Where the packet does not name a fact, this document writes **UNKNOWN**.

---

## (A) HARD CRITERIA — JSON

```json
[
  {
    "id": "H1",
    "how": "Carry-over is a kernel-owned object, not a habit: BootUP loads the corrections store (count-weighted, printed at boot), the scar index (queryable), fixed-name handoffs, unreleased-lease set, unanswered mail, and backup-rehearsal window from the append-only ledger and refuses to declare GREEN if any expected item is absent (typed NOT_IN_RECORD, never an empty success). Session/context manager captures transcripts as OS-owned files keyed by stream id; a session that dies without release is detected by lease expiry on the arbiter clock and by BootUP's unreleased-session scan, both of which write a dated event rather than depending on the dying process to tidy. TidyUP is a shutdown job that can only announce; it cannot be the only path that makes state durable. Forgotten-fact detection is mechanical: every durable obligation is registered with an identity, a writer, and a next-check date, and the health board treats a missed check as a bug.",
    "risk": "The forgotten-fact detector can only alarm on obligations that were registered. A fact never written into the carry-over set is still invisible; the mechanism detects loss of known state, not the first failure to record. The 135 uncarded modules may hold such unregistered obligations — UNKNOWN until those cards exist."
  },
  {
    "id": "H2",
    "how": "Every resolver, lock, queue, mail, registry, and spend path has exactly one legal outcome for torn or unparseable state: REFUSE, with a typed absence (TORN_STATE / UNREADABLE / WRONG_IDENTITY / NOT_FOUND / OUT_OF_CLOCK / NOT_IN_CORPUS / NOT_IN_RECORD / UNREACHABLE / CREDIT_EXPIRED / UNPRICED / VOLUME_SPLIT). There is no fallback ladder, no plausible-path search, no env override that can shadow a healthy sentinel-verified tree, and no conversion of missing into zero or green. Unknown CLI flags exit 2. Host reads beat sandbox reads in code. An unpriced call is UNPRICED, never 0. A rail not probed is UNREACHABLE, never assumed up. Numbers carry provenance (estimate / measured / billed) and a measurement date; tracked-vs-billed mismatch fails loud.",
    "risk": "Refuse-everywhere will halt work that today's operators currently push through by hand. If a control file is frequently torn by the FUSE mount, the system will go RED more often than BTS did; that is correct, but it will be felt as fragility until ingress and append-over-rename cover every mount-exposed write."
  },
  {
    "id": "H3",
    "how": "Lying/corrupting mount: integrity-verified I/O checks bytes-declared vs bytes-consumed; claim-time hash manifests distinguish 'changed under me' from 'the mount lied'; torn files refuse; host reads are authoritative; mount-exposed state is append-only (renames are kernel-local, same-volume). Session dying without release: leases expire on the arbiter clock; takeover is a recorded LEASE_EXPIRED→LEASE_GRANTED chain; dying-holder recovery requires no cleanup discipline. Two writers in different universes: one install identity, one kernel, sandbox cannot commit (ingress envelope only), fencing token required on every publish, platform adapter owns path/shell semantics, Windows names are canonicalized and collisions refuse, no parent-walk, no drive literals. Expiring credit: probe-before-spend with reserve-worst-case-deny-call-settle in the caller; CREDIT_EXPIRED is a typed state; DOM-first policy can re-admit work onto an unmetered rail; UNPRICED stays UNPRICED. Dead rail mid-run: every dispatch has a return watcher; timeout marks the rail UNREACHABLE with a date; the job lands FINDINGS or BROKE per contract and is reported, never retried; remaining work is re-admitted under policy or refused.",
    "risk": "DOM-first re-admission after credit expiry or a dead API rail can change cost and latency in ways the job author did not write down. The architecture refuses silent re-route: re-admission is a new job event with a reason. Jobs that are not safely movable (side effects already started) still stop and report — they do not hop rails."
  },
  {
    "id": "H4",
    "how": "The seven primitives are kernel modules on the only I/O and dispatch paths, not optional libraries. cosmos.io is the only critical-read/write API (integrity-verified). cosmos.watch is invoked inside the dispatch function: a dispatch with no registered watcher is a contract violation and does not leave the kernel. cosmos.validate runs before a return is released to any caller (paths against disk in MVP; DOI/quote validators attach at the same hook). cosmos.reconcile is the only writer of VERIFIED: no registry row may hold VERIFIED without a dated behavioral probe, and the periodic audit re-probes. cosmos.session owns per-stream context and transcript files. cosmos.plat is the only layer that may touch encoding, quoting, MAX_PATH (\\\\?\\), line endings, or subprocess construction; tools import the adapter, never raw shell semantics. cosmos.abs is the return type of every public API. Build gates (number provenance, delivery tracking, pointer integrity, mirror age) are the same kind of native check, not a later dashboard.",
    "risk": "Making all seven native means the first bulk-port of 135 modules will break any file that talks to disk or subprocess directly. That is intended, but the port survey shows 73 files with drive literals and 8 with parent-walk — the primitive layer will be the critical path of the code phase, and a leaky bypass will recreate two-universes."
  },
  {
    "id": "H5",
    "how": "The scheduler owns concurrency and priority: a job manifest carries priority as a field (not a filename encoding), and the kernel admits N workers across lanes while each claimed job has exactly one worker. Locks are enforcing: a write to a guarded tree is accepted only with a current fencing token issued by the kernel; advisory/cooperative claim files are banned at N>1. Every artifact (heartbeat, log, ledger line, mail, claim, panel payload) carries worker identity plus an offset-aware timestamp and epoch. There is no shared mutable file whose last writer wins: mail is per-worker directories with unique immutable message files; the queue of record is immutable manifests plus an append-only transition ledger; heartbeats are per-worker files discovered by glob. Overlapping ticks: one winner, the loser receives a clean LOST_CLAIM and takes the next job. Windows job objects contain descendants so a timeout does not orphan children. Lane names pass the incumbent path-injection regex before they become directories.",
    "risk": "Enforcement is only as strong as the fenced-commit gateway. A tool that writes around cosmos.io (direct Path.write_text on a guarded file) is a hole. The platform adapter and a boot-time import-graph check are the intended seals; they are not a Windows ACL rewrite of the whole tree, which this design does not claim."
  },
  {
    "id": "H6",
    "how": "The rail registry is the only source of connectivity. Every link is a row with class CLI | API | DOM | CHAT | OTHER, endpoints, last_probe_at, probe_result, measured_throughput, mesh_addressable, and age. DOM is not a peer and not a sidecar: it is the default class in a registered routing policy the scheduler evaluates at admit time (reasoning-heavy and bulk → DOM; short structured scriptable → API only when the job says so and the API probe is live). Links are created by registration plus a cheap live probe; a listed-but-unprobed link is UNREACHABLE and does not count. Node hardware (WRK7, SRV1, cloud, new boxes, peers) answers the same three questions before it counts: reachability, measured throughput, mesh addressability. Cursor, GitHub, and GitLab are rails/surfaces in this registry, not special cases outside it.",
    "risk": "DOM lane workers can only be verified on Keith's machine (a cloud container cannot touch a Chrome session on the keith.bbf profile). Any cloud-originated claim that a DOM rail works is a claim about code, not behavior. The registry will stay honest only if UNREACHABLE is the default for unverified DOM links — operators may dislike a red matrix during the port."
  },
  {
    "id": "H7",
    "how": "Install writes one root into an installation record (not into source). A sentinel file at that root carries identity-constant + install-id + a hash of the role map; resolution asserts sentinel CONTENT, not directory existence. Roles (mesh, queue, board, secrets, publish, archive, working, mail, ledger, …) resolve from that one root; no drive letter and no parent-walk appear in code. The same COSMOS.svc binary is the product surface: a Windows Service on WRK7, or the same process in a cloud host, exposing the HTTP API from day one. Remote access is by authorized principals Keith names. There is exactly one live kernel per install identity — cloud-or-WRK7 is a placement choice at install, not two arbiters. Settability is proven by a second instantiate-against-scratch-root test, not by a comment.",
    "risk": "Authn/authz mechanism for remote principals is UNKNOWN in the packet (Windows integrated vs token vs other). The architecture reserves a principal registry; the first remote-client acceptance test cannot be declared until that choice is made. Dual-active WRK7+cloud kernels are forbidden and therefore not an HA story — HA is UNKNOWN and out of MVP."
  },
  {
    "id": "H8",
    "how": "Incumbent observable contracts are preserved as scheduler/lock/mail/runner laws: under overlap exactly one claimant runs the job and the loser loses cleanly; outcomes are worded CLEAN / FINDINGS / BROKE and land in done / done/findings / failed; the log line 'RUNNING' plus command is written before the child starts; stale running jobs are reported and never retried; files prefixed '_' are helpers and are not claimed, enforced in the runner; anything a sandbox can touch is append-only (kernel may rename only on a same-volume path it has asserted). Each of the 149 registered tools keeps name, verbs, and observable behavior unless the architecture conflicts — then the architecture wins, and the tool is adapted, replaced, or abandoned in a dated decision record, never by silent drift. LSSsr-class 'last folder previously read' state is session-owned, not a hidden global.",
    "risk": "Behavioral cards exist only for four modules. The other 135 contracts are UNKNOWN in this packet. A 'preserved' claim for those tools is a promise to measure, not a measurement. The architecture-wins valve will be used; how often is UNKNOWN."
  },
  {
    "id": "H9",
    "how": "One authoritative clock lives in the kernel (arbiter clock): every kernel timestamp is offset-aware local + epoch + UTC. Worker clocks are evidence, never the expiry authority (the naive-local / five-hour-stale class is closed here). Windows Task Scheduler is the OS hook for periodic and elevated work: elevated ops are repointed first (one UAC), every task is written with Set-ScheduledTask and verified by read-back, and every reader moves with its writer. Wakeups are interrupt-driven: ReadDirectoryChangesW (or equivalent) on ingress/queue/mail, waitable timers, and process/service signals feed the kernel event port. A 60-second scheduled tick may remain as a watchdog secondary; it is not the only way a job starts. One interrupt wakeup is an acceptance demonstration, not a future wish.",
    "risk": "ReadDirectoryChangesW and FUSE-mounted paths have historically missed or coalesced events. If the sandbox ingress volume does not deliver directory change events, the kernel must refuse to treat that volume as interrupt-capable (typed UNREACHABLE for interrupts) rather than silently falling back to poll-only while claiming H9. Poll-as-watchdog is allowed; poll-as-the-only-path is a failed gate."
  },
  {
    "id": "H10",
    "how": "The architecture is complete: kernel, registry, primitives, scheduler, rails (including DOM lanes), API, backup contracts, federation interfaces, voice/frontend URL trees, and peer-data-scope seam exist as types and paths now. The code-phase MVP implements the kernel + API + resolver + lock + queue/scheduler + mail + probes + spend gate + clock/interrupts + KDash API (age on every panel) + backup/verify/rehearse + health/task-registry + elevated ops + tool-decision log, and stops at the API for the alternate frontend and voice. W1–W12, federation go-live, phone/desktop apps, and dual-home HA attach at named seams (adapter, job type, rail class, panel, principal) without replacing the queue, lock, or state model.",
    "risk": "W1–W12 are named in the rubric and are not defined in any supplied packet document. Their acceptance criteria are UNKNOWN. Seams are reserved (new rail class, new job type, new panel, new adapter, new principal scope); if a wishlist item later requires a second source of truth, that item is a surgery and must be refused or must reopen architecture — this design will not pretend the contents are known."
  }
]
```

---

## (B) THE DESIGN

### B.1 One-sentence thesis

COSMOS is one install identity, one settable root, one resident kernel service that is the product API, the lock arbiter, the clock, and the event port; everything else is a scheduled worker, an interrupt, a client, or a seam.

### B.2 What runs where

| Place | What runs | What it is allowed to do |
|---|---|---|
| **WRK7 (home of a typical install)** | `COSMOS.svc` as a Windows Service | Authoritative kernel: HTTP API, lease/fence issuance, fenced commit, clock, return watchers, ingress ingest, spend gate, session manager, health snapshots |
| **WRK7** | Windows Task Scheduler | Starts lane workers, backup/verify/rehearse, periodic probes, scheduled audit, elevated ops; not a COSMOS daemon |
| **WRK7** | Lane workers / elevated ops process | Execute claimed jobs; write append-only artifacts with their worker id; cannot grant locks or settle spend |
| **WRK7** | DOM lane workers (local only) | Drive registered browser surfaces; the cloud container cannot do this and must not claim it |
| **Cloud** | Same `COSMOS.svc` binary *only if this install's home is cloud* | Same kernel roles; WRK7 then registers as a worker/node, not a second kernel |
| **Cloud Cursor container** | Editors and critics | Read/edit code; cannot bind runtime; cannot verify DOM; cannot see `V:` |
| **Sandbox (Cowork / FUSE session)** | Ingress writer only | Drop uniquely named envelopes; never hold a lease; never rename queue state; never be believed over a host read |
| **Remote machine / phone (later)** | API clients | Orchestrate through `/v1`; no direct tree writes |
| **Peer cold machine** | Fresh kernel after install | Own identity, own root, own kernel; federation via interfaces, not by sharing a lock file |

**Exactly one live kernel per install identity.** "Served from the cloud or from WRK7" is an install-time placement, not two arbiters. Two live kernels is the two-universes incident rebuilt as topology.

Remote authorized access is the WRK7 (or cloud-home) API reached from a second device. Desktop and phone apps are later clients of that same API.

### B.3 Resident moving parts (and why they earn rent)

BTS today has no COSMOS-owned daemon; Task Scheduler ticks scripts. H7 requires a served API. That forces **one** new resident process. This design puts every continuously-required enforcer inside it:

- API (the product surface)
- Lock arbiter + fenced write gateway
- Authoritative clock
- Event port (interrupts, watchers, ingress)
- Spend gate
- Session/context manager

**Not resident:** a second lock service, a KDash process, a backup daemon, a SQLite server, a federation daemon, a voice daemon. Backup, audit, probes, and lane execution are jobs. Voice and the alternate frontend are clients.

If a future proposal adds a daemon, it must name a duty the kernel cannot perform on the event port. "It would be cleaner" is not rent.

### B.4 Settable root and resolver

**One configured root** (examples from the goal: `V:\A\Ai\COSMOS` here, `D:\Ai\Cosmos` elsewhere). Set at install. Never a drive letter in code. Never `__file__` parent-walk. `ROLD` is a role, not `MESH.parent / "ROLD"`.

**Installation record** (live state, not git): root path, identity constant, install-id, home placement (WRK7|cloud), role map, clock policy.

**Sentinel** at the root: content is identity + install-id + hash of the role map. Existence of a directory is not identity. An existing-but-empty `mesh` role fails the content assertion (the 2026-08-21 empty-tools incident).

**Roles** (resolved from the one root; which directory is which is data in the role map, not history-split across two roots): `mesh`, `queue`, `board`, `mail`, `ledger`, `locks`, `sessions`, `registry`, `health`, `archive`, `working`, `publish`, `secrets`, `ingress`, `handoffs`, `corrections`, `scars`.

**`secrets` is safe by location:** it is a sibling of `publish`, never a child. R2 publish cannot ship it. An exclude list is a rotting blocklist; do not replace location with a list.

**Resolver timing — boot-gate object, not import-time, not lazy call-time:**

- `import cosmos.paths` does **no** filesystem I/O and resolves **nothing**. Import is not an assertion about the machine.
- Process entry (service `OnStart`, CLI `main`, scheduled-task wrapper) **must** construct `Resolver(installation_record)` and assert sentinel content. Failure is one line, process exits non-zero. This is the incumbent's fail-fast *user-visible* property, moved to a defined gate so a second non-default root can be instantiated in-process for the settability test.
- No module receives a path except through a `Resolver` instance it was given.
- Runtime env vars cannot shadow a healthy verified tree. Overrides are an install-time rewrite of the installation record, then re-asserted.
- Sandbox side may glob to *find* the mount because session names change; the glob must yield **one** identity-matching sentinel or REFUSE. `sorted()[0]` of multiple mounts is banned (OA API-03 class).
- Every walk uses the platform adapter's long-path prefix. A 275-character path that returns "not found" without `\\?\` is a resolver bug.

**D:\ is read-only** as a standing boundary. The resolver will refuse a role that resolves onto a read-only bound except for roles explicitly declared read-only.

### B.5 Platform adapter and integrity I/O (native primitives)

`cosmos.plat` owns: encoding (UTF-8 both ends of every pipe; the cp1252-under-redirect scar), quoting, line endings, path canonicalization (Windows case-insensitive identity: canonicalize, reject collisions), `\\?\` prefixing, subprocess construction, and Windows job-object assignment.

Tools do not call `subprocess` or build shell strings. Tools do not invent path arithmetic.

`cosmos.io` owns critical reads/writes: bytes-declared vs bytes-consumed; host read authoritative over sandbox read; torn/unreadable/absent are distinct; append is the only publish path on mount-exposed files.

Path-rewriting / migration tools skip prose (the docstring-corruption scar).

### B.6 Lock — lease + fencing, issued by the kernel

The incumbent `tree_lock` is two mechanisms: a cooperative claim file, and a hash manifest of watched control files. The claim file's "visibility, not enforcement" trade is **closed**. The hash manifest is **kept**: a lock says who held the pen, never what the page said. `--verify` still distinguishes "changed under me" from "the mount lied."

**Mechanism (not discipline):**

1. Writer asks the kernel for a lease on a named resource (tree, file set, or job).
2. Kernel, on its clock, issues `{lease_id, fence, expires_at, writer_id, resource, manifest}`.
3. `fence` is monotonic per resource. A commit with a stale fence is rejected and ledgered (`COMMIT_REJECTED`).
4. Every grant, expire, takeover, release, and reject is an append-only lock event (`LEASE_GRANTED`, `LEASE_EXPIRED`, `TAKEOVER`, `RELEASE`, `COMMIT_REJECTED`). Console output is not evidence (OA API-07).
5. Torn or unparseable lease/event state REFUSES (does not read as free).
6. Stale takeover is announced and ledgered, never silently cleared. Sessions that die without release are the expected case (08-22: 581 min stale after a correct `--release` rc=1); expiry is mandatory.
7. Writer set is closed; unknown writers exit 2.
8. Sandbox never holds a lease. A sandbox write is an ingress envelope; only the kernel commits, and only with a fence it issued.
9. `_sha()`-class helpers do not collapse unreadable vs absent into "changed."

**Why not OS file locks alone:** the mesh spans native NTFS and FUSE. FUSE lock semantics are a known lie. The two-universes incident (2026-08-16) was two holders in two path universes; `LockFileEx` on the path each side can see does not create one lock.

**Why not lease-without-arbiter (HMAC-only, no issuer):** a fencing counter needs a single monotonic issuer. Two universes with the same key mint two "next" tokens. HMAC proves possession of a secret, not uniqueness of a grant.

**Why the arbiter is not a second daemon:** it is a module of `COSMOS.svc`, which H7 already requires. See Question 1.

### B.7 Queue and scheduler

**Substrate of record: filesystem job manifests + append-only transition ledger. Not SQLite.**

A job is an immutable manifest file with a unique name (`<utc-epoch>__<priority>__<origin-worker>__<nonce>.job.json`) containing: origin identity, priority (field, not filename-as-contract — filename may copy priority for humans), lane, rail hint, payload pointer, timeout, watchers required, created-at (offset-aware). The file is write-once.

**Claim is kernel-issued, then reflected as a same-volume rename** the kernel performs after asserting queue/running/done/failed/ledger share one volume (boot assertion; `VOLUME_SPLIT` refuses to start). Workers do not claim-by-rename themselves. This keeps the incumbent *observable* claim-by-rename contract (one winner under overlap; command built from the **claimed** path — the pre-rename resolve scar) without giving two ticks a race on a cooperative rename, and without treating a cross-volume rename as atomic (OA API-05 / GEM-11).

Loser of an overlap receives `LOST_CLAIM` and continues. The incumbent abort-the-tick gap (OA API-11) is closed.

**Three worded outcomes, preserved:**

| Child rc | Word | Destination |
|---|---|---|
| 0 | CLEAN | `done\` |
| 2 | FINDINGS | `done\findings\` |
| else | BROKE | `failed\` |

A checker that finds a discrepancy exits 2 and is not "broken" (PLM-44).

**Log-first:** open the job log, write `RUNNING` + the command from the claimed path, then start the child. A crash mid-job is distinguishable from never-started. Timeout writes `RED - TIMED OUT`, never an empty file.

**Report-never-retry:** stale `running\` jobs are reported, never re-executed. Side effects may already have happened.

**Helper convention:** `_` prefix is not claimed, enforced in the runner. Skips are printed by status, never silent.

**Nothing is deleted.** Stage to `_delme`. No `.bat`, ever. One runnable predicate: a file is runnable iff the adapter can build a command for it. Do not reintroduce a second `RUNNABLE` dict.

**Lanes:** named directories under the queue role, regex-guarded (the undocumented path-injection guard is now documented and kept). Per-lane sequencing is a scheduler policy; concurrency is *between* workers the scheduler admits, including multiple workers on one lane when the job set allows. A lane with jobs and no worker is FLAGED (the unrun-queue-looks-empty case). Heartbeats are `runner_heartbeat__<worker>.json` at the lane base, glob-discovered, carrying lane + worker + aware-local + epoch + UTC.

**Ledger:** append-only jsonl with fsync. This is the only artifact that survived FUSE when atomic renames died. Heartbeats and claim *reflections* may be per-file snapshots; they are not the audit record. Do not generalize "the runner is append-only" (OA API-12). The **ledger** is append-only. Full stop.

**SQLite:** permitted only as a **derived index** rebuilt from the ledger (KDash query acceleration). If the DB disagrees with the ledger, the DB is wrong and is discarded. SQLite is never the queue of record (shared mutable file + FUSE concurrent-writer class).

**Priority** is a manifest field the scheduler uses at admission. Filename copies are decorative.

**UTF-8** forced on both ends of every child pipe.

### B.8 DOM lanes live *inside* the scheduler

DOM is the foundation and preferred path: it depends on nothing that can run out (no credit, quota, billing, key expiry, or consent). Vertex thinking billed at output rate is the measured reason reasoning-heavy work belongs here. An API-only COSMOS would be narrower and more fragile than BTS.

**Placement — not a sidecar:**

1. **Rail class `DOM`** is first-class in the registry, alongside CLI, API, CHAT, OTHER.
2. **Lane family `dom/<surface>`** is a scheduler lane family. DOM work is a job: admitted, claimed, watched, outcome-filed, ledgered, like any other job.
3. **Routing policy is data:** default `prefer: DOM` unless the manifest sets `require: API` (short, structured, scriptable) *and* the API probe is live. Policy is evaluated at admit time by the scheduler, not by each tool.
4. **Dispatch path:** admit → spend/probe (DOM probe is a cheap session/page liveness check, not a metered token) → register watcher → hand to a DOM lane worker → validate return → settle (DOM settle is UNPRICED or measured-zero with provenance, never a fake 0 hiding a metered hop).
5. **Watchers:** a DOM dispatch without a watcher does not leave the kernel. No return lands unobserved (DOM "the monitor worked whenever anyone was watching" class, closed).
6. **Probes:** every DOM surface has a dated probe. UNREACHABLE is recorded. Cloud-originated "DOM works" is not a probe.
7. **Credit expiry / dead API mid-run:** if the job has not started side effects, scheduler may re-admit onto DOM with a new event and reason. If side effects started, report-never-retry. Never silent hop.

Cursor, SuperGrok, Copilot, and the BTS bridge are registered surfaces. Their workers run on WRK7.

### B.9 Mail / phone at N>2

Per-worker inbox directories on the mail role (shared surface, resolver-addressed). Messages are immutable uniquely-named files: sender identity + offset timestamp + payload hash. Two senders to one recipient produce two files.

**Typed states, never collapsed:** MISSING (dead phone, non-zero — "THE PHONE IS DEAD," never "no news") · EMPTY · UNREADABLE · STALE (age threshold + unanswered required-ack). Probe prints paths, existence, mtime, size, and the typed state.

**Send is a real path** (incumbent `bts_phone` has OUTBOX declared and never written). Send and receive are separate recorded facts (receipt files). Outbox ≠ inbox. Mirror ≠ source. No literal backslash survives the adapter.

Surface missing → refuse, do not write into cwd.

### B.10 Spend, probe-before-spend, audit

Settled, not re-voted: **breaker lives in the caller** that holds the key: cheap live probe → reserve worst case → deny if reserve fails → call → settle.

Per-rail append-only ledgers. Rails, budgets, spend, quotas tracked in real time. Every number has a measurement date and provenance (estimate / measured / billed). Tracked vs billed discrepancy fails loud. Unpriced is UNPRICED.

**Audit** is not a separate product: `GET /v1/audit` (or CLI equivalent) reads the ledgers and probe table. A scheduled `AUDIT` job lands the same document where it is read. Age is visible because every row already has `as_of`.

MCP is kept. A2A is not introduced.

### B.11 Return watchers and return-validation

Dispatch API: register watcher first, or 4xx. Watcher states: `PENDING`, `OBSERVED`, `VALIDATED`, `REJECTED`, `TIMEOUT`, `RAIL_DEAD`. Callers may not consume a return before `VALIDATED`.

Validation hook: paths against disk (MVP), quotes against sources, DOIs against Crossref — same hook, additional checkers attach. Failed validation is REJECTED, not a used-then-regretted value.

### B.12 Registry-reality, tools, nodes

No `VERIFIED` without a dated behavioral probe. Periodic audit re-probes. The rails matrix is measured, not listed.

Tools registry: 149 contracts by name/verbs/observable behavior. Architecture-wins decisions are rows: `{tool, verb, decision: keep|adapt|replace|abandon, reason, date, successor}`. Drift without a row is a health red.

Nodes/surfaces (WRK7, SRV1, new hardware, cloud, peers): same three questions before they count.

Identity: one identity constant per install; closed writer set; per-worker id on every artifact.

**Federation (KMesh / JMesh / HMesh / peers):** interfaces now — `Peer {identity, home, rails[], last_probe, data_scope_ref}`, `FederationBus {advertise, probe, send, watch}`. **The five blockers are UNKNOWN by name in this packet**; they are architecture work, not go-live. Never reported working until they close. Peer data scoping remains Keith's policy; `data_scope_ref` is the reserved seam.

### B.13 Session / context, BootUP, TidyUP, corrections, scars

`cosmos.session` owns per-stream context and transcript capture. Handoffs have fixed names. Corrections are count-weighted and printed at boot. Scars are a query, not a folder you might forget.

BootUP: sentinel, volume-split check, print corrections, scan unreleased leases / unanswered required-ack mail / overdue rehearsal / probe ages, emit health. A new-tree-only marker is emitted here (runtime-binding gate).

TidyUP: announce and close what the process still holds; durability does not depend on it.

### B.14 KDash and the frontend API — one service

One `COSMOS.svc`, one clock, one ledger, one spend view. Two URL trees, two authz scopes:

| Tree | Audience | Contract |
|---|---|---|
| `/v1/kdash/*` | Existing KDash functionality, extended | Every panel payload carries `as_of` (visible age). Live data, not a file someone copied |
| `/v1/orchestrate/*` | Alternate frontend (Cowork-class: files, dispatch, schedule, review) | Same verbs a UI or a script would call |
| `/v1/voice/*` | Voice in/out, later | Same orchestrate verbs; a voice layer plugs in without rework |
| `/v1/audit`, `/v1/health`, `/v1/rails`, `/v1/jobs`, `/v1/registry/*` | All clients | Shared |

Two processes would split authority (two clocks, two spend pictures) — the "remembering wrong" class. KDash is a live backend *of this service*, not a sibling app with a sync problem.

The custom frontend is a client. It is not in the kernel. Voice is a client. Phone/desktop later are clients.

### B.15 Backup — scheduled kernel job type, not a script, not a daemon

A backup is a scheduled job with a verification, or it is not a backup. One copy on one machine is zero.

**Job types (contracts in the scheduler, implemented as workers, invoked by Task Scheduler + interrupts):**

- `BACKUP` — copy scoped-by-irreplaceability to the configured target set (local / cloud / LAN, any combination; ≥1 off-machine required).
- `BACKUP_VERIFY` — required successor; per-file hash; fail loud; no verify ⇒ backup did not happen.
- `BACKUP_REHEARSE` — restore to a scratch role, compare hashes, leave evidence. Health is RED if rehearsal is outside the configured window.

No dedicated backup daemon (S1: nothing to do between runs that the scheduler does not already do). Not a forgettable tool: missing `BACKUP_VERIFY` or overdue `BACKUP_REHEARSE` is a control failure, not an optional hygiene item.

Current measured off-machine pattern in the pipeline notes (`V:\Ai` → `X:\My Drive\BTS_BACKUP\Ai`) is an *example target*, not a hardcoded path. Targets are installation-record data.

### B.16 Standard subsystems — none dropped

| Subsystem | Placement | Enforcer |
|---|---|---|
| Queue runner + lanes | Scheduler module + FS manifests | Kernel claim + ledger |
| Tree lock | Kernel lock module | Fence on commit |
| Phone / mailbox | Mail module | Probe + typed absence + unique files |
| Health board +/− controls | Health module + `/v1/health` | BootUP + periodic jobs; negative controls required in every selftest |
| Spend gate + per-rail ledgers | Kernel spend + append jsonl | Caller-held breaker |
| Scheduled-task registry | Tasks module | Set-ScheduledTask + read-back; `py_compile` at registration |
| Elevated ops worker | Separate elevated process, kernel-dispatched | One UAC, then scheduler |
| R2 publish | Surface adapter on `publish` role | Location-safe secrets |
| GDX / ODX | Surface adapters + rails | Probe, consent/credit as CREDIT_EXPIRED / UNREACHABLE |
| Identity + peers | Identity module + federation seam | Closed writer set |
| Tools registry + index sync | Registry module + sync job | Decision log; no VERIFIED without probe |

### B.17 Data flows (happy path and the expensive paths)

**Orchestrated call (API or DOM):**
client → authz → spend/probe/reserve → scheduler admit (DOM-first policy) → watcher registered → worker claimed (fence) → platform adapter executes → log-first → return-validate → settle → ledger → panel `as_of` updates.

**Sandbox dispatch:**
sandbox writes ingress envelope (unique, hashed) → directory interrupt (or watchdog tick if interrupt UNREACHABLE) → kernel ingest → job manifest → same path as above. Sandbox never claims.

**Dead rail / expired credit:**
watcher TIMEOUT or probe CREDIT_EXPIRED → rail row dated → if no side effects, optional re-admit to DOM as a new event; else FINDINGS/BROKE, never retry.

**Lying mount:**
io integrity fail or verify-manifest mismatch → TORN_STATE / mount-lie event → refuse commit → health RED. Host re-read required.

**Forgotten carry-over:**
BootUP expected-set minus present-set → NOT_IN_RECORD → RED. Corrections still print.

**Backup:**
timer → BACKUP → BACKUP_VERIFY → ledger. Window check → BACKUP_REHEARSE or RED.

### B.18 Concurrency, containment, clock

Scheduler property, not a script flag. Priority at admission. Locks enforce. Per-worker identity everywhere.

Windows job objects: a timeout that kills the wrapper must record whether descendants died. Unknown descendant outcome is a FINDING, not a clean timeout.

Kernel clock is authority. Worker timestamps are evidence. Heartbeats carry aware-local + epoch + UTC + identity (the five-hour-stale class).

### B.19 Incremental cutover and rollback

- Build on a branch. V:\Ai intact: nothing deleted, nothing staged out of BTS.
- COSMOS lives at the configured root (`V:\A\Ai\COSMOS` on this machine).
- BTS keeps running during port. Compatibility ingress can ingest a BTS queue drop as an envelope (seam, not a second scheduler).
- Elevated ops repointed first (one UAC). Each task: Set-ScheduledTask, read-back, new-tree-only marker. Every reader moves with its writer.
- Cut over only when the runtime-binding gate passes **on this machine**. Cloud reviews certify code, never behavior.
- Rollback rehearsed: tasks repoint to BTS, marker disappears, BTS health green. Staging to `_delme` is not a tested rollback.
- Independent family reviews the PR. Integration run executes all modules together.

### B.20 Cold-machine peer install (counted)

1. Clone the git tree.
2. Run the installer: choose root, write installation record, write sentinel, write identity constant.
3. Install `COSMOS.svc` (Windows Service, or the cloud-home equivalent).
4. One UAC: register elevated ops.
5. Register scheduled tasks; `py_compile`; read-back.
6. BootUP (corrections print; sentinel; probes; new-tree marker).
7. Confirm API serves; add principals Keith names.

Seven steps to a running peer. Federation go-live is not a step in this list.

### B.21 Blast radius

| Bad thing | What it can reach | What stops it |
|---|---|---|
| Bad job | Its claimed paths + its log/ledger lines | Fence, timeout, job object, report-never-retry |
| Bad node | Its own ingress + its registered rails | Probe/UNREACHABLE; not in other nodes' lock namespaces |
| Bad key | Rails that key unlocks | Spend reserve; CREDIT_EXPIRED; principal scope; secrets sibling of publish |
| Bad sandbox | Ingress directory | Cannot commit; host read wins |
| Bad kernel process | The install | Single home; rollback is task-repoint; still one blast radius — that is the honest cost of one arbiter |

---

## (C) REQUIRED QUESTIONS

### 1. Lock enforcement mechanism

**Chosen: lease + monotonic fencing token + append-only lock events, issued and committed by a module of the one resident `COSMOS.svc` (not a second arbiter process; not OS file locks as the authority).**

Against H3:

- Lying mount: fenced commit + hash manifest + integrity I/O + torn-state refuse; append-only events survive FUSE where cooperative files do not.
- Dying session: expiry on **arbiter** clock; takeover ledgered; no cleanup required.
- Two universes: sandbox cannot commit; one kernel; fence required; platform adapter; no path literals.
- Expiring credit / dead rail: not lock problems; spend + watchers handle them. A lock is not a credit.

**Why this earns rent (S1):** H7 already requires a resident served process. The arbiter is that process's enforcement role, not a new daemon. OS locks do not earn a daemon and also do not work across FUSE/native (GEM's own flagged risk). HMAC-without-issuer does not produce a single fence.

### 2. Queue substrate

**Chosen: immutable filesystem job manifests + kernel-issued claim reflected as a same-volume rename + append-only jsonl ledger. SQLite is a derived cache only.**

Against H5: no last-writer-wins shared file; identity on every artifact; scheduler owns admission/priority; overlap has a clean loser.

Against H8: claim-under-overlap, three worded outcomes, log-first, report-never-retry, helper `_`, append-over-rename on mount-exposed state — all remain observable. The incumbent file-is-the-dispatch property is preserved at ingress (a sandbox that can write a file can dispatch) without letting that file be the claim.

SQLite as source of truth is rejected: it is a shared mutable file; concurrent native+FUSE writers are the two-universes / corrupting-mount class; the mesh already paid to learn that append+fsync survives where clever atomicity dies.

### 3. Resolver timing

**Chosen: explicit `Resolver` object, constructed at process entry, zero import-time I/O.**

Against H2: failure is still immediate and loud — at the boot/entry gate, with one line, no fallback, sentinel *content* asserted. Import-time constants cannot prove settability (second non-default root in one process) and couple every importer to one machine layout. Pure call-time-without-a-gate lets a process start and guess later (the defect class). The incumbent's fail-fast *shape* is kept; the *surface* moves from `import` to `main`/`OnStart`/task wrapper.

### 4. Where DOM lanes live

**Inside the scheduler:** rail class `DOM`, lane family `dom/<surface>`, routing policy evaluated at admit, dispatch and watchers on the same kernel path as every other job, cheap dated probes before the surface counts. Not a parallel orchestrator. Not "use DOM if you remember." Cloud may ship DOM *code*; only WRK7 may mark a DOM link anything other than UNREACHABLE.

### 5. KDash live backend + frontend API

**One service, two URL trees (`/v1/kdash/*`, `/v1/orchestrate/*`), plus a reserved `/v1/voice/*` on the same process.**

Why: live age, spend, rails, and audit must be one picture. Two services are two memories. The frontend is a client; voice is a client; KDash panels are views of the kernel, not a second backend.

### 6. Backup subsystem placement

**Scheduled kernel job types (`BACKUP`, `BACKUP_VERIFY`, `BACKUP_REHEARSE`), not a resident backup daemon and not a loose script.**

Restore rehearsal is designed in as a first-class job whose absence (outside the configured window) is a health RED, plus a required verify successor so a copy without a hash check cannot be called a backup. Off-machine target is a boot/health requirement (one machine = zero copies).

---

## (D) MVP CUT-LINE

### Ships in the code phase (stage 6)

- Installer + installation record + sentinel-content resolver + second-root settability test
- Platform adapter (`\\?\`, UTF-8 pipes, canonicalize, job objects) + `cosmos.io` + typed absence
- `COSMOS.svc` as Windows Service (WRK7 home) exposing the HTTP API
- Lock: lease + fence + event log + hash manifest + torn refuse + recorded takeover
- Ingress envelope + sandbox-cannot-commit
- Queue/scheduler: manifests, kernel claim, three outcomes, log-first, report-never-retry, helper `_`, lanes, heartbeats, append-only ledger, same-volume assertion, clean overlap loser
- Mail: per-worker dirs, unique messages, send+receive facts, typed missing/empty/unreadable/stale
- Session/context manager + BootUP/TidyUP + corrections print + scars query
- Return watchers on every dispatch; path-against-disk validator
- Registry + dated probes; rails matrix measured (UNREACHABLE recorded)
- DOM *code path* and `dom/<surface>` lanes; DOM probe/marking **locally** on WRK7
- Spend gate (reserve-deny-call-settle) + per-rail ledgers + UNPRICED
- Authoritative clock; one demonstrated interrupt wakeup; Task Scheduler integration with read-back
- KDash API with `as_of` on every panel (current functionality preserved at API level)
- `/v1/orchestrate/*` and `/v1/voice/*` **contracts** (implemented enough that a client can call them; no custom UI, no STT/TTS)
- Backup + verify + one rehearsed restore to at least one off-machine target
- Health board with +/− controls; task registry; elevated ops repoint
- Tools registry + architecture-wins decision log (four spike tools decided; others as they are ported)
- Identity constant; closed writer set
- Compatibility ingress seam for BTS during cutover
- Selftests with positive **and** negative controls on every spike-class module
- Runtime-binding marker; V:\Ai left intact; rollback rehearsal

### Seams (architecture exists; implementation waits)

- Alternate orchestration **UI** (the API is the MVP surface)
- Voice in/out engine (plug-in behind `/v1/voice/*`)
- Desktop and phone apps
- Federation go-live (KMesh/JMesh/HMesh/peers) — interfaces only; five blockers UNKNOWN by name; never reported working
- Peer data-scoping policy (Keith's; `data_scope_ref` reserved)
- Dual-home / HA (forbidden as two kernels; any other HA is UNKNOWN)
- SQLite derived index (optional acceleration)
- DOI/Crossref and quote-source validators (hook ships; checkers attach)
- R2 / GDX / ODX full surface behavior beyond probe + adapter seam
- W1–W12 (see UNKNOWN)
- Behavioral port of the remaining ~135 modules (cards not in this packet; each keeps contract or gets a decision row)
- Authn mechanism for remote principals (UNKNOWN; principal registry is the seam)

### W1–W12

**UNKNOWN.** The rubric names them. No supplied document defines them. Headroom is the seam set: new rail class, new job type, new panel, new adapter, new principal scope, new validator on the existing hook. A wishlist item that needs a second source of truth is a surgery and reopens architecture.

---

## SOFT CRITERIA (for ranking, not elimination)

- **S1** — One new resident process (`COSMOS.svc`). Task Scheduler already exists. No backup/KDash/lock/voice daemons.
- **S2** — Seven install steps (B.20).
- **S3** — Audit is a read of ledgers and probe rows the system already writes; on-demand and scheduled are the same document.
- **S4** — See B.21. Honest residual: a bad kernel is install-wide.
- **S5** — BTS remains live; COSMOS beside it; ingress compatibility; task-by-task cutover; rehearsed rollback.
- **S6** — W1–W12 UNKNOWN; seams listed rather than invented.

---

## UNKNOWN REGISTER (do not promote to design)

| Item | Why it is unknown |
|---|---|
| W1–W12 definitions, priority, acceptance | Named in rubric only |
| The five federation blockers, by name | Goal says they exist; packet does not list them |
| Remote authn/authz mechanism | "Authorized user" is required; method is not |
| Cloud home SKU / provider | "From the cloud or WRK7" is placement, not a vendor |
| Voice STT/TTS vendor | Provisioned API only |
| Exact KDash panel inventory | "Current functionality preserved" — live tree not in this workspace |
| Remaining 135 module cards | Correctly absent from this packet |
| Interrupt reliability of the live FUSE ingress volume | Must be measured on WRK7; if events do not fire, that volume is interrupt-UNREACHABLE |
| Whether any of 149 tools must be abandoned | Architecture-wins valve exists; count is UNKNOWN |
| GitLab product / grant expiry | Pipeline notes the question as unanswered |
| Cursor billed-vs-export 32× disagreement | If COSMOS ingests Cursor usage it must ingest billed; wiring is later |

---

## ACCEPTANCE MAP (goal "done" → design mechanism)

1. Verified tree at configured root; ported files hash-compared; mismatch loud — installer + `cosmos.io` + decision log.
2. One-root resolver; second non-default root instantiates — boot-gate `Resolver`.
3. Rails matrix measured with dates; UNREACHABLE recorded — registry + probes.
4. Tools answer contracts or have a decision row — registry.
5. Elevated ops first; Set-ScheduledTask + read-back; readers with writers — tasks module.
6. KDash live + age; frontend API answers — one service, two trees.
7. Backup scheduled, off-machine, hash-verified, rehearsal — job types.
8. Remote client; interrupt wakeup demonstrated; one offset-aware clock — API + event port + kernel clock.
9. One-command audit with dates; scheduled audit lands — ledger read.
10. Health green from new tree (new-tree-only marker); task registry 0 red; machine count = registry count; no relative paths or drive literals; control files parse **and** validate.
11. V:\Ai intact; independent family on the PR; integration run; rollback rehearsed.

---

*End of Grok Stage 4 independent return. 2026-08-23.*
