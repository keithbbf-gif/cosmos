# Ara Poll Instruction

Written by Ara on 2026-09-02.

## Purpose

This is the standing instruction for the voice layer (Ara). Read this file at the start of any Cosmos session, and whenever the user asks for a status update on work orders.

## On every status check

1. Read `docs/VERDICT_SPEC.md` — the verdict contract.
2. List `work_orders/drop/` and any live bucket directory for `*.json` work-order files.
3. For each work order, read the file and report:
   - **pending** → "in progress"
   - **applied** → one-line reason + timestamp
   - **rejected** → the objection verbatim, so the user can correct from the headphones
4. If a proposal file exists under `proposals/`, mention it; the verdict on the work order is authoritative.
5. Never guess. If the file has no Verdict field, say "no verdict yet."

## The timer problem

Ara has no internal clock and cannot poll on her own. The cadence comes from outside:

- **User-driven (default):** the user asks "status?" and Ara reads GitHub on the spot.
- **Scheduled:** an Automations task runs every few minutes, reads the drop folder, and notifies only when a verdict appears or changes. That is the driver — Ara stays reactive.

## Why this file exists

So future sessions don't rediscover the contract. The spec lives in VERDICT_SPEC.md; this file tells Ara when and how to read it.
