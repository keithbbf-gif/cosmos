# COSMOS — STAGE 1 GOAL (v5) — APPROVED BY KEITH 2026-08-23
*Node-readable render of `COSMOS_STAGE1_GOAL_v5_2026-08-23.docx` (the signed artifact).*

## WHAT COSMOS MUST DO
Replace BTS_MESH as the operating system for a multi-AI mesh: real-time communication and
coordination of multiple AIs from all major vendors. BTS was the bridge; COSMOS is what the
bridge reached.

- **TOTAL CONNECTIVITY AS A RESOURCE.** Every available rail — CLI, API, DOM, CHAT, and any
  other interface that can be made to communicate — installed and working, in every
  direction: node↔node, node↔surface, surface↔node. Every working link is registered and
  exposed as a system resource. DOM is the foundation and preferred path; the API is the
  fallback; chat surfaces are lanes.
- **CARRY-OVER STABILITY.** Corrections (count-weighted, printed at boot), scars as a query,
  fixed-name handoffs, BootUP and TidyUP. Every expensive incident has been the system
  forgetting or remembering wrong — never a compute failure.
- **SETTABLE ROOT, LIKE ANY NORMAL SOFTWARE INSTALL.** V:\A\Ai\COSMOS here; D:\Ai\Cosmos on
  another machine. Set at install, sentinel-verified, resolved by role everywhere. No drive
  letter or hardcoded path in code.
- **TOOL CONTRACTS PRESERVED — WITH AN ARCHITECTURE ESCAPE VALVE.** Every registered tool
  (149 today) keeps its functional contract: same name, same verbs, same observable behavior
  (LSSsr still reads the screenshots folder from the last one previously read). Implementations
  are free to be new. Where a contract conflicts with the new architecture, THE ARCHITECTURE
  WINS: adapt, replace, or abandon the tool — recorded as a decision, never drifted.
- **KDASH BECOMES A LIVE BACKEND.** Current functionality preserved and extended: a real
  service with an API, live data with visible age on every panel, improved backend support,
  richer options and interface.
- **AN ALTERNATE ORCHESTRATION FRONTEND.** A custom frontend, independent of the Claude and
  Grok apps, from which the end user orchestrates the mesh with Cowork-class capabilities —
  file operations, dispatch, scheduling, review — and fewer platform limitations where
  possible. Shares one API with the KDash backend.
- **VOICE CONTROL, PROVISIONED.** Voice in and voice out as a feature/option: the frontend
  API is designed so a voice layer plugs in without rework.
- **INTEGRATED SYSTEM BACKUP — A REQUIREMENT, NOT A SCRIPT.** Local, cloud, and LAN targets
  in any combination; scheduled, hash-verified per file, scoped by irreplaceability, failing
  loudly, restore REHEARSED. A backup is a scheduled job with a verification, or it is not a
  backup. One copy on one machine is zero; off-machine or it does not count.
- **SERVED, NOT JUST INSTALLED.** COSMOS runs as a service from the cloud or from the WRK7
  workstation, accessed remotely by Keith and by others he names — from other machines now,
  and by desktop and phone apps built later. The API is the product surface from day one.
- **REAL-OS HOOKS.** First-class integration with the system clock (one authoritative time
  source), the task scheduler, and INTERRUPTS — event-driven wakeups on file change, timer,
  and signal, not poll-only loops.
- **REALTIME TRACKING AND AUDIT.** Rails, budgets, spend, and quotas tracked in real time,
  auditable ON DEMAND and on a schedule. Every number carries its measurement date; a
  discrepancy between tracked and billed fails loudly. An unpriced call is UNPRICED, never 0.
- **STANDARD SUBSYSTEMS CARRY FORWARD** — none dropped: queue runner with lanes · tree lock
  (enforcing) · phone/mailbox · health board with positive and negative controls · spend
  gate and per-rail ledgers · scheduled-task registry · elevated ops worker · R2 publish
  surface · GDX and ODX surfaces · identity and peers · tools registry with index sync.
- **PROBE BEFORE SPEND.** Every node and rail tested with a cheap live probe before
  appreciable spend. The breaker lives in the caller: reserve worst case, deny if reserve
  fails, call, settle. Settled; not up for re-vote.
- **FULLY MULTITHREAD CAPABLE BY DESIGN.** Concurrency is a property of the scheduler; locks
  enforce; per-worker identity in every artifact; no shared mutable file whose last writer
  wins.
- **DISTRIBUTABLE.** A peer stands COSMOS up on a cold machine: an installer, a git-hosted
  tree, one identity constant, a settable root.

## EVIDENCE AND INTEGRITY — OS PRIMITIVES, NOT ADD-ONS (mined from 154 scars)
- **Integrity-verified I/O:** critical reads check bytes-declared vs bytes-consumed; host
  reads are authoritative over sandbox reads, in code.
- **Event system with return watchers:** every dispatch registers a watcher; no return
  lands unobserved.
- **Return-validation subsystem:** DOIs against Crossref, quotes against sources, paths
  against disk — BEFORE any return is used.
- **Registry-reality reconciliation:** no verified status without a dated behavioral probe;
  the periodic audit re-probes.
- **Session/context manager:** per-stream contexts, OS-owned transcript capture.
- **Platform adapter layer:** encoding, quoting, path length, line endings owned by one
  layer; no tool touches shell semantics directly.
- **Typed absence in every API:** NOT FOUND ≠ OUT OF CLOCK ≠ NOT IN CORPUS ≠ NOT IN RECORD.
- Plus, as build gates: number provenance (estimate/measured/billed), delivery tracking,
  pointer integrity, mirror age discipline.

## DESIGNED FOR NOW — DELIVERED WHEN GATED. Nothing is out of architectural scope.
- **FEDERATION** (KMesh/JMesh/HMesh/peers): the five blockers are ARCHITECTURE WORK; design
  interfaces now, go live when blockers close, never reported working until then.
- **PEER DATA SCOPING:** the policy remains Keith's; the architecture reserves the seam.
- **WRK7 / SRV1 / new hardware:** registered as nodes/surfaces in the same registry, same
  three questions (reachability, measured throughput, mesh addressability) before counting.
- **VOICE and the ALTERNATE FRONTEND** are in this class: provisioned now, delivered when
  built.

## WHAT "DONE" MEANS — the acceptance test, not a feeling
1. COSMOS tree at the configured root as a verified build; every ported file hash-compared;
   loud failure on mismatch.
2. Resolver resolves every role from ONE configured root; a second test install at a
   NON-default root resolves and runs — settability proven.
3. THE RAILS MATRIX IS MEASURED, NOT LISTED: every link probed live, recorded with result
   and date; UNREACHABLE recorded, never assumed.
4. Every carried tool answers its contract from the registry; every adapted/replaced/
   abandoned tool has a recorded decision.
5. Elevated ops repointed first (one UAC click); every task follows via Set-ScheduledTask
   verified by read-back; every reader moved with its writer.
6. KDash live backend serving current + added functionality; every panel shows its own age;
   the frontend API answers.
7. Integrated backup running on schedule to at least one off-machine target, hash-verified,
   one REHEARSED restore.
8. A served instance answers a remote client from a second machine/device by an authorized
   user; an event-driven wakeup DEMONSTRATED (interrupt, not poll); one authoritative,
   offset-aware clock source.
9. The audit answers: one command returns current rails/budget/spend/quota state with
   measurement dates; a scheduled audit runs and lands where it is read.
10. Health green from the new tree, proven by a new-tree-only marker; task registry zero
    red, machine count = registry count, no relative paths or drive literals; every control
    file parses AND validates.
11. V:\Ai intact as the prior floor — nothing deleted, nothing staged. An independent family
    reviewed the PR; an integration run executed all modules together; rollback rehearsed.

## HARD BOUNDARIES THAT GOVERN THE BUILD
Never delete — stage to _delme. The mesh and dissertation corpus are never deleted at any
cost level. D:\ is read-only. No .bat, ever. Build on a branch; cut over only when the
runtime-binding gate passes on this machine. American English throughout.

**Signed: Keith — approved in session, 2026-08-23 ("OK. Approved.")**
