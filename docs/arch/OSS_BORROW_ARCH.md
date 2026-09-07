# ARCH — OSS borrow (after R1_CODE)

**DEFINE:** `DEFINE_OSS_BORROW.md`. **RESEARCH:** `work_orders/ccr/CREW/OUT/OSS/R1_CODE.md`.

Rubric: one Core, ledger authority, cDeck is a client, free = already on the machine, H8 subtract.

## Decision

Do **not** vendor their runtimes. Apply three ADAPTs onto live emits:

1. **HITL bind (LangGraph interrupt + checkpointer).** A FINDINGS / Review wait is not done until a ledger (or signed heartbeat) names it. Missing artifact = refuse (P04), not a green Review chip.
2. **Wait-without-spinning (n8n putExecutionToWait).** Long pause = drop box + daemon, never the LLM. Review/Talk chrome may show the drop path as the resume surface (our `$execution.resumeUrl`).
3. **Two clocks (Temporal / LangGraph TimeoutPolicy).** Wall vs idle already exist as timeout BROKE vs stale RUNNING. Painters must not list stale or BROKE as in-flight (pane-fns DEFINE). No new retry loop.

## Not this ARCH

LangGraph MOTIF, Temporal worker, Postgres saver, LangFlow iframe, checkpoint fork, auto-retry.

## BUILD next (Gitur, after this consensus)

Docs + Review/Talk copy if missing "waiting for CCr" / drop path. Core only if live GET `/jukebox` shows RUNNING with no `stale_flag` when heartbeat is dead — measure first (P04).
