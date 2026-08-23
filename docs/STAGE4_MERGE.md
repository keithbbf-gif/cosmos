# COSMOS STAGE 4 — MERGE OF THREE INDEPENDENT DESIGNS · 2026-08-23 ~04:45
**Designs: GEM (gemini-2.5-pro) · OA (gpt-5.6) · CoPG (Copilot).** Grok PENDING (Cursor key).
⚠ Family caveat: OA and CoPG share model ancestry — treat their agreement as ~2.5 families,
not 3. The Grok addendum matters for exactly this reason.
Rubric: `docs/STAGE4_RUBRIC.md`, committed at `1da27ff` BEFORE dispatch — provably pre-dated.

## UNANIMOUS (3 of 3) — THE STAGE 3 CONTESTED QUESTIONS MOSTLY DISSOLVED
1. **A RESIDENT SERVICE, AND IT EARNS ITS RENT.** All three independently propose one
   resident authority (OA "COSMOS Core" · GEM "Kernel Service" · CoPG registry+arbiter+
   scheduler co-located). All three make the SAME rent argument unprompted: the arbiter is
   not a new daemon — it lives inside the service that must already be resident for the API,
   scheduler, spend gate, and watchers. **Stage 3 contested #1: RESOLVED — arbiter yes.**
2. **LEASES + FENCING TOKENS; ADVISORY LOCKING IS DEAD.** Expiry on the arbiter's clock;
   stale takeover is a recorded event chain, never silent clearing; protected commits
   present a token and stale tokens are REJECTED. (OA adds: workers get no direct write
   capability to protected paths — commits go through a fenced gateway.)
3. **EXPLICIT RESOLVER INSTANTIATION AT BOOT COMPOSITION** — fail-fast preserved (service
   cannot enter READY without sentinel-verified root), import-time side effects dropped.
   **Stage 3 contested #3: RESOLVED.**
4. **APPEND-ONLY LEDGER/JOURNAL AS THE AUTHORITY; everything else is a rebuildable
   projection.** OA: hash-chained framed events. GEM: journal + content-addressed state
   files. CoPG: signed ledgers + read-back probes. A corrupted projection is discarded and
   rebuilt; a corrupted ledger segment REFUSES and raises an incident. **This is H1 made
   structural — carry-over as a property of the store, not of discipline.**
5. **ONE API SURFACE.** KDash is a client/projection of the service API; the alternate
   frontend, voice, and phone/desktop apps are clients of the SAME versioned API. (CoPG
   words it "two components, one API surface" — same design.)
6. **DOM IS A FIRST-CLASS SCHEDULER RAIL** — registered, probed, budget-reserved, watched,
   typed on failure (UNREACHABLE / SESSION_EXPIRED / AUTH_REQUIRED); DOM-first is routing
   POLICY (data), and fallback to API is explicit and audited, never silent.
7. **SHARED RISK, FLAGGED BY ALL THREE:** the service is a single availability point.
   Unanimous mitigation: fail-CLOSED posture, Windows service recovery, durable ledger
   replay — never a second unsynchronized writer.

## RESOLVED BY SYNTHESIS (the disagreement was smaller than it looked)
- **QUEUE SUBSTRATE.** GEM: SQLite as THE queue. OA: immutable manifests + ledger, SQLite
  only as a disposable service-private cache. CoPG: manifests canonical + SQLite index.
  ⇒ All three mediate ALL access through the one service, so the real rule is:
  **canonical state = immutable manifests + ledger events; any database is SERVICE-PRIVATE
  projection/cache, never shared through a mount, never the authority.** GEM's ACID wants
  are satisfied by the service serializing appends. **2-of-3 shape adopted; GEM's concern
  absorbed.**
- **BACKUP PLACEMENT.** OA: core subsystem. GEM: scheduled tool. CoPG: scheduled jobs via
  elevated worker with kernel-integrated rehearsal. ⇒ **Policy, verification state, alerts,
  and rehearsal evidence live IN THE SERVICE; execution runs as scheduled jobs.** Restore
  rehearsal is a first-class scheduled job type (`rehearse-restore`) landing events in the
  ledger. All three requirements met; nobody's design lost anything.

## STRONGEST SINGLE CONTRIBUTIONS — CARRY INTO THE STAGE 5 REVISION
- **OA:** session-closure CONTEXT MANIFESTS (inherited facts, open watchers, active leases,
  handoff recipient — closure without a valid manifest = OPEN_CONTEXT incident). The most
  concrete H1 mechanism offered; adopt.
- **OA:** sandbox ingress envelopes — a mount-visible write is not authoritative until the
  native service verifies bytes/hash/schema/identity and records acceptance. Kills the
  lying-mount class at the boundary.
- **GEM:** content-addressed state files (filename = hash, journal holds the live pointer)
  — integrity check and version history in one move.
- **GEM:** legacy job adapter as an explicit component (file-drop jobs translated into
  scheduler jobs, exit codes mapped to worded outcomes).
- **CoPG:** arbiter signatures/HMAC on ledger anchors for cross-volume claims; opportunistic
  single-volume atomic-rename fast path where no cross-volume coordination is needed.
- **OA:** the compatibility lane — legacy mutable-file tools run SERIALIZED until adapted;
  unrestricted parallelism is earned per tool, not granted by default.

## OPEN AFTER THIS MERGE (stage 5 must close)
1. **Service internals layout** — OA one-process-with-components vs CoPG separable
   registry/arbiter/scheduler: define the internal module boundaries so a later split is
   possible without an API break.
2. **Ledger implementation detail** — framed JSONL (OA) vs SQLite-WAL journal (GEM) vs
   signed JSONL (CoPG): pick one with the mount rules applied (appends only on anything
   mount-visible).
3. **DOM worker containment** — a browser-capable worker's identity, session/profile
   management, and what happens when the browser dies mid-job.
4. **Grok addendum** — fold in when the Cursor lane fires; anything it contests reopens
   only that item, per the qualitative gate.

## VERDICT
No design FAILS a hard criterion. The three agree on every load-bearing decision; the
differences are implementation-level and mostly synthesized above. **Stage 5 = one
revision round: each family receives this merge + both other designs and revises its own.
Then Keith ratifies the synthesis and the spike briefs go out.**
