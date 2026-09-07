# Appendix — How COSMOS works

**Kind:** written description / drawings-in-prose for Legal to attach to US provisionals.
**Status:** not a USPTO filing. Not legal advice. Not a novelty opinion.
**Source of truth:** `docs/FINAL_ARCHITECTURE.md` ratified 2026-08-23 (`docs/RATIFIED.md`);
live Core `tree_id=KMesh-COSMOS-live` on this machine.
**Maps to packets:** P07 (ledger + fence), P10 (resolver), P11 (SEED), P08 (DOM-first),
P09 (spend). MOTIF (P01) is how the OS builds the next organ — not the OS.
See **Appendix — COSMOS is the OS** (SCAR, ROLD, carry-over).

## One paragraph (the invention as an OS)

One resident Windows service — **COSMOS Core** — is the sole authority: API gateway,
scheduler, lease arbiter with fencing tokens, spend gate, return-watcher, registry +
prober, and the single writer of an **append-only, hash-chained, service-signed JSONL
ledger** on a verified native volume. Everything else — queue views, registries, dashboards
(KDash / cDeck), spend totals — is a **rebuildable projection** (service-private SQLite
allowed as cache, never authority). Large artifacts live in a **content-addressed store**
(filename = hash; the ledger holds the live pointer). Workers (native, DOM, cloud) run in
attempt-private workspaces and publish only through a **fenced commit gateway** that
demands a fencing token and expected input hashes. The service is a **modular monolith,
split-ready**: module interfaces are RPC-shaped so any module can later become a process
without breaking the one versioned external API that cDeck, voice, and other clients
consume.

COSMOS is the **operating system**. Products (Forge, Crucible, Diligence, Docket, UPS,
Differentiator) are **skins** on that OS, not second Cores.

## What a later claim must be able to point at

A person of ordinary skill, given this appendix plus the live tree, can build:

1. A single process that is API + scheduler + arbiter + ledger writer.
2. A framed JSONL ledger with hash chain and service signature; replay rebuilds
   projections; a corrupt segment **REFUSES** rather than repairing in place.
3. A boot resolver that takes **one** install-configured root, verified by sentinel
   **content** — existence of an empty directory is not identity.
4. Workers that cannot write the live tree except through the fenced commit gateway.
5. One versioned HTTP API (`/api/v1/...`) as the only external surface.
6. DOM as a first-class rail (unmetered path) with API as fallback, both audited.
7. A spend gate that will not silently widen a cap.
8. A signed session-close manifest (SEED) so carry-over is structural.

## Decisions (ratified 2026-08-23)

| # | Decision |
|---|---|
| 1 | One resident service. Fail-closed. Never a second unsynchronized writer. |
| 2 | Leases + monotonic fencing tokens + fenced commit gateway. Advisory locking is dead. |
| 3 | Ledger = framed, hash-chained, signed JSONL. Corrupt segment ⇒ REFUSE + incident. |
| 4 | Queue = immutable manifests + ledger lifecycle events. SQLite is projection only. |
| 5 | Resolver instantiated at boot; service cannot go READY without sentinel-verified root. |
| 6 | DOM is a first-class scheduler rail (contained workers, typed failures). |
| 7 | One versioned API. UI may deploy separately; authority may not. |
| 8 | Backup: policy/verification in Core; execution as scheduled jobs; rehearse-restore is first-class. |
| 9 | Compatibility lane: legacy mutable-file tools SERIALIZED until they earn parallelism. |
| 10 | Context manifests at session close. Closure without a valid manifest ⇒ OPEN_CONTEXT. |
| 11 | Scar-derived primitives are kernel interfaces; workers cannot import around them. |

## Two roots (do not conflate)

- **Repo tree** — tracked code and governance (`cosmos/`, `docs/`, `tests/`).
- **Runtime root** — the running instance (`live/`: state, ledger, queue, registry, config).
  Identified by `.cosmos-root.json` (`system=COSMOS`, `tree_id=KMesh-COSMOS-live`).

The resolver takes one configured root. No drive literal as identity, no parent-walking
fallback ladder, no import-time side effects.

## Method that builds the OS (MOTIF)

COSMOS builds itself on directional input. The loop is eight stages:
RESEARCH → ARCH → CONSENSUS → BUILD → CRITICS → CONSENSUS → IMPROVE → ITERATE
(back to RESEARCH). Dual-lane BUILD: two builders, **no shared context**, different
families. Critics judge *is this the thing we decided*, not house style. One disposer
(CCr) writes the live tree. The runtime-binding gate is a value **only the live tree
can emit** — never an exit code, never a green log.

## What this is not

Not a second blockchain. Not git-as-authority. Not “event sourcing exists.” Not a
dashboard that is itself the OS. Not OpenWork (orch harness) and not cDeck (skin).
cDeck is a client of `/api/v1`. OpenWork is a separate app/window.

## Already public (clock)

GitHub `cosmos` created 2026-08-23T06:42:12Z. Ratification record that day.
Predecessor mesh named on GitHub `bts-mesh` 2026-08-16. July 2026 operation is
**local BTS-MESH run records**, not that GitHub date. See appendix How BTS-MESH works.

## Attach to

FILE packets P01, P04, P07, P08, P09, P10, P11 at minimum. Duplicate this PDF into
each provisional so each filing is enabling on its own (a provisional cannot claim
benefit of a sister provisional).
