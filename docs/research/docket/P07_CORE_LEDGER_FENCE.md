# COSMOS-P07 — COSMOS Core: sole ledger, fence, tokens

**Title:** Single-writer AI-work operating system with signed hash-chained ledger, fencing tokens, and projections that are never authority
**Kind:** System
**Status:** FILE
**Fee:** $65 micro-entity provisional
**Date:** 2026-09-07
**Legend:** ATTORNEY WORK PRODUCT — NOT A FILED PATENT APPLICATION — FOR COUNSEL ONLY
**Inventor:** Name of inventor: ________________________________ (counsel to complete). The source tree discloses the operator as Keith. This preparer does not sign as inventor.

Standalone written description for a US provisional. Not a filed application. Not claims. Not a novelty opinion. Counsel files. Duplicate HOW_IT_WORKS.pdf at filing.

## Cross-reference

Sisters COSMOS-P01 through COSMOS-P13. No claim of benefit of a sister. 37 CFR 1.53(c): no technical add-after.

## Field of the invention

[0001] The present disclosure relates to an operating system for AI work whose authority is a single-writer append-only hash-chained service-signed ledger, with leases and fencing tokens, and with dashboards as rebuildable projections that are never authority.

## Background of the invention

[0002] Two writers, empty-dir identity, advisory locks, and repair the log are measured failures. Green dashboards as authority are placation. Event sourcing, git, Kafka, and blockchains are related and are not this occupancy as an AI-work OS.

## Brief summary of the invention

[0003] One resident process is API, scheduler, arbiter, and ledger writer. The ledger is framed JSONL, hash-chained, service-signed. Replay rebuilds projections. Projections may not be written as authority. Workers receive a fencing token; the commit gateway rejects stale tokens and hash mismatches. A corrupt segment refuses; it is not repaired in place.

## Definitions

[0004] As used herein, "Ledger" means Append-only, hash-chained, service-signed JSONL. Authority.

[0005] As used herein, "Projection" means A rebuildable view. Never authority.

[0006] As used herein, "Fencing token" means A monotonic token proving the holder still owns the lease.

[0007] As used herein, "Fenced commit gateway" means The only path by which a worker publishes; demands token plus expected input hashes.

## Brief description of the drawings

[0008] FIG. 1 shows one resident service writing a hash-chained signed JSONL ledger. Workers present a fencing token at a fenced commit gateway. Dashboards and SQLite are projections. A corrupt segment refuses.

[0009] The drawings are described in prose so that a person of ordinary skill can produce sheet drawings. Sheet drawings may be added by counsel before filing. Do not add new matter after a filing date.

## Detailed description

[0010] One process is API plus scheduler plus arbiter plus ledger writer. Fail-closed. Never a second unsynchronized writer.

[0011] Ledger: framed JSONL, hash chain, service signature. Replay rebuilds projections. Corrupt segment implies REFUSE plus incident, never repair-in-place.

[0012] Queue is immutable manifests plus ledger lifecycle events. SQLite is service-private projection only.

[0013] Workers run in attempt-private workspaces (native, DOM, cloud) and publish only through the fenced commit gateway presenting fencing token and expected input hashes.

[0014] Large artifacts live in a content-addressed store (filename equals hash; the ledger holds the live pointer).

[0015] The service is a modular monolith, split-ready: module interfaces are RPC-shaped so any module can later become a process without breaking the one versioned external API.

[0016] Scar-derived primitives are kernel interfaces. Workers cannot import around them (AD-11).

[0017] This OS is not MOTIF. MOTIF (COSMOS-P01) is how the OS builds the next organ. The house is the ledger, the fence, the resolver (COSMOS-P10), the seed (COSMOS-P11), the spend gate (COSMOS-P09), and the DOM rail (COSMOS-P08).

## Best mode

[0018] COSMOS Core as ratified 2026-08-23, docs/FINAL_ARCHITECTURE.md, live tree_id=KMesh-COSMOS-live, serve on port 8770. Encoded cosmos/cosmos_service.py and related modules.

## Further embodiments

[0019] Windows service recovery. Backup policy in Core; execution as scheduled jobs; rehearse-restore is first-class. Compatibility lane: legacy mutable-file tools serialized until they earn parallelism.

## Disclosure clock (already public)

[0020] Architecture text on cosmos created 2026-08-23T06:42:12Z. Predecessor mesh named on bts-mesh created 2026-08-16T10:21:14Z.

## Information concerning related art (not an IDS; not a novelty opinion)

[0021] Event sourcing (Fowler 2005); CQRS; git; Bitcoin; Kafka; US11943344B2 Ridgeline (hash-chained signed events plus projections, closest patent); WO2018217375A1 Microsoft signed log-chain; RFC 6962 Certificate Transparency; Kleppmann fencing tokens 2016; Chubby 2006; Raft 2014; etcd/k8s leases; SCSI-3 PR / STONITH; Temporal; Airflow; n8n; LangGraph.

[0022] Combination of all five as an AI-work OS: unknown as blocking. Not a novelty opinion.

## What this disclosure is not

[0023] Not blockchain. Not git-as-authority. Not Temporal. Not event sourcing exists as a slogan.

## Statement of invention (not claims)

[0024] An AI-work OS whose authority is a single-writer signed hash-chained JSONL plus fencing-token commit of worker artifacts, with projections never authority.

[0025] Counsel may draft claims. The foregoing is a statement of invention, not a claim set under 35 U.S.C. 112(b).

## Appendix to attach at filing

[0026] HOW_IT_WORKS.pdf (APP_OS: SCAR, ROLD, carry-over; APP_COSMOS; APP_CRUCIBLE; APP_BTS_MESH). Duplicate the appendix into this provisional at filing. A provisional cannot claim benefit of a sister.
