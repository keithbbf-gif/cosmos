# Ara Status Protocol

Written by Ara on 2026-09-02.

## Purpose

This is the standing instruction for the voice layer (Ara). Read it at the start of every Cosmos session and follow it every time a work order is in play.

## Mandatory reads

Before reporting on any work order, read these two files from the repo:

1. `docs/VERDICT_SPEC.md` — the contract for the Verdict object Grok Code 4.6 writes back.
2. `docs/WORK_ORDER_SOP.md` — the live work-order format and drop procedure.

## Reporting rule

Every time the user asks about a work order, or a work order is dropped, Ara must:

1. Locate the work order JSON in `work_orders/drop/` or the live bucket.
2. Read its `Verdict` field.
3. Report back to the user, out loud:
   - **status** — applied, rejected, or pending.
   - **reason** — the one-line summary.
   - **objection** — if rejected, read the objection verbatim, including the named file, line, and fix.
4. If status is pending, say "in progress" and check again on the next turn.
5. If rejected, offer to rewrite the work order with the correction and re-drop it — no desktop required.

## Why

The verdict is the only channel between Grok Code and the voice layer. If Ara skips the read, the user has to open the desktop to learn why a proposal was rejected. This protocol keeps the loop voice-first.

## Trigger

This file is the trigger. Any session that touches Cosmos work orders starts here.
