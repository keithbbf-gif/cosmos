# P07 — COSMOS Core: sole ledger, fence, tokens

**Kind:** system. **Status:** FILE. **Fee:** US provisional micro $65.

## What it is (in-tree)

One resident service: sole writer of an **append-only, hash-chained, service-signed JSONL** ledger. Dashboards/SQLite = **rebuildable projections**, never authority. **Leases + monotonic fencing tokens.** Workers publish only through a **fenced commit gateway** (token + expected input hashes). Corrupt segment **REFUSES**, never repair-in-place. Ratified `docs/FINAL_ARCHITECTURE.md` 2026-08-23.

## Problem / scar

Two writers, empty-dir identity, advisory locks, “repair the log.” Green dashboards as authority.

## Written description

1. One process is API + scheduler + arbiter + ledger writer.
2. Ledger: framed JSONL, hash chain, service signature. Replay is the rebuild of projections.
3. Projections (queue, KDash, spend totals) may not be written as authority.
4. Workers get a fencing token; commit gateway rejects stale tokens and hash mismatches.
5. Fail-closed on corrupt segment.

## Already public

Architecture text on `cosmos` **2026-08-23**. Predecessor mesh named on `bts-mesh` **2026-08-16**.

## Prior art to name (R3)

Event sourcing (Fowler 2005); CQRS; git; Bitcoin; Kafka; **US11943344B2** Ridgeline (granted 2024 — hash-chained signed events + projections, closest patent); **WO2018217375A1** Microsoft signed log-chain; RFC 6962 Certificate Transparency; Kleppmann fencing tokens 2016; Chubby 2006; Raft 2014; etcd/k8s leases; SCSI-3 PR / STONITH; Temporal; Airflow; n8n; LangGraph. **Combination of all five as an AI-work OS:** UNKNOWN as blocking.

## What this is not

Not blockchain. Not git. Not Temporal. Not “event sourcing exists.”

## Suggested independent idea

An AI-work OS whose authority is a single-writer signed hash-chained JSONL plus fencing-token commit of worker artifacts, with projections never authority.
