# COSMOS — FINAL ARCHITECTURE SYNTHESIS · stage 5 close · 2026-08-23 ~05:10
**For Keith's ratification.** Three families designed independently (stage 4), critiqued via
merge, revised once (stage 5, Keith's one-iteration rule). **The revisions converged to one
architecture — every open item closed the same way by all three.** Grok's addendum arrives
via Cursor and reopens only what it contests.

## THE ARCHITECTURE, IN ONE PARAGRAPH
One resident Windows service — **COSMOS Core** — is the sole authority: API gateway,
scheduler, lease arbiter with fencing tokens, spend gate, return-watcher owner, registry +
prober, backup-policy coordinator, and the single writer of an **append-only, hash-chained,
service-signed JSONL event ledger** on the verified native volume. Everything else —
queue views, registries, KDash panels, spend totals — is a **rebuildable projection**
(service-private SQLite allowed as cache, never authority, never mount-shared). Large
artifacts live in a **content-addressed store** (filename = hash; the ledger holds the live
pointer). Workers — native, DOM (browser-capable, Job-Object-contained, ephemeral
profiles), and cloud — execute in attempt-private workspaces and publish ONLY through a
**fenced commit gateway** presenting their fencing token + expected input hashes. Mounts
are ingress/egress only: a sandbox write becomes real when the native service verifies
bytes/hash/schema/identity and ledgers INGRESS_ACCEPTED. The service is a **modular
monolith, split-ready**: internal module interfaces (Arbiter, Ledger, Scheduler, Registry,
Validators, Worker Supervisor) are RPC-shaped so any module can later become a process
without breaking the one versioned external API that KDash, the alternate frontend, voice,
and phone/desktop apps all consume.

## DECISIONS, FINAL (unanimous after iteration)
| # | decision |
|---|---|
| 1 | **One resident service** (earns rent: arbiter/scheduler/API are one process anyway). Fail-CLOSED; Windows service recovery; ledger replay. Never a second unsynchronized writer. |
| 2 | **Leases + monotonic fencing tokens + fenced commit gateway.** Advisory locking dead. Stale takeover = recorded event chain. Atomic rename survives only as a single-volume optimization, never authority. |
| 3 | **Ledger = framed, hash-chained, signed JSONL segments** (OA framing + CoPG signatures + GEM content-addressed store). Corrupt segment ⇒ REFUSE + incident, never repair-in-place. |
| 4 | **Queue = immutable manifests + ledger lifecycle events.** SQLite is service-private projection only. GEM conceded on-record. |
| 5 | **Resolver = explicitly instantiated at boot composition**; service cannot go READY without sentinel-verified root + installation record. No import-time side effects; fail-fast preserved. |
| 6 | **DOM = first-class scheduler rail** run by contained DOM workers: own OS identity, ephemeral ACL'd profiles, Job Objects, typed failures (UNREACHABLE / SESSION_EXPIRED / AUTH_REQUIRED / BROKE), report-never-retry unless contract-idempotent. DOM-first is routing policy data; fallback is explicit + audited. |
| 7 | **One versioned API surface.** KDash = projection client; alternate frontend/voice/mobile = clients. UI may deploy separately; authority may not. |
| 8 | **Backup: policy/verification/evidence in Core; execution as scheduled jobs; `rehearse-restore` is a first-class scheduled job type.** Task Scheduler = registered, read-back trigger. |
| 9 | **Compatibility lane**: legacy mutable-file tools run SERIALIZED until behavior-card-backed adaptation earns parallelism. Legacy Job Adapter (GEM) maps file-drop → scheduler jobs, exit codes → worded outcomes. |
| 10 | **Context manifests at session close** (OA): inherited facts, active leases, open watchers, handoff recipient; closure without a valid manifest ⇒ OPEN_CONTEXT incident. Carry-over made structural. |
| 11 | The seven scar-derived primitives are **kernel interfaces** with capability enforcement — workers cannot import around them. |

## HONEST RISKS, CARRIED FORWARD (flagged by all three)
- Core is a single availability point (mitigated, not removed — HA/multi-writer is UNKNOWN
  and outside MVP).
- Fail-closed creates visible refusals; operator override must be explicit and audited.
- Filesystem notification overflow ⇒ loud degraded state + bounded reconciliation scans.
- ~135 tool contracts still UNKNOWN pending the behavioral-card fan-out.
- DOM secret-store technology and browser-hardening depth: UNKNOWN, contract-only for now.

## WHAT HAPPENS ON RATIFICATION
1. **Stage 6a spike briefs** (4) go to GWB: resolver, lock/arbiter protocol, mailbox/IPC,
   scheduler — each spike RUNS against stage 2(a) observed behavior on live Windows.
2. **Cloud agents** (Cursor, on the cosmos repo env) take: test scaffolds, behavioral-card
   slices, and later the 6b bulk port on a branch.
3. **GitLab CI** wired after `glab auth login`: py_compile / import graph / integration run.
4. Stage 7: PR review by non-builder families + the runtime-binding gate on this machine.
