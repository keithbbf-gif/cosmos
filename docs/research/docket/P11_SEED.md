# P11 — SEED / signed session close (OPEN_CONTEXT)

**Kind:** method / system (narrow). **Status:** FILE (narrow). **Fee:** US provisional micro $65.

## What it is (in-tree)

Close of a session writes a **signed** context manifest (`SEED.json` + declared length/HMAC). Inherited facts, active leases, open watchers, handoff recipient. Close **without** a valid manifest ⇒ **OPEN_CONTEXT** incident. Start refuses NO_SEED / BAD_SEED / IDENTITY_MISMATCH. AD-10. Not ChatGPT “memory.”

## Problem / scar

Sessions vanish. The next session fabricates continuity. Memory features store facts without a fail-closed close.

## Written description

1. `close_session` must emit a signed manifest covering declared fields.
2. Absence, length mismatch, or HMAC failure is an **incident**, not a warning.
3. `start_session` reads the manifest under its declared length/HMAC before injecting carry-over.
4. Optional: auto-resession clock that consumes the same SEED (embodiment).

## Already public

AD-10 in public architecture 2026-08-23.

## Prior art to name (R3)

**CONTINUITY** arXiv:2609.05269 (2026-09-05 — signed context manifests + CLOSE/OPEN receipts; **closest paper; watch**); Portable Agent Memory arXiv:2605.11032; Context Passport; CRAFT handoff; ctx handover; vendor memory; CRIU; JWT/JWS; **US20250259069A1** reconstitutable sessions. Incident-on-missing-close as OS rule: **UNKNOWN as patented.**

## What this is not

Not ChatGPT memory. Not CRIU. Not “write a notes file.”

## Suggested independent idea

Session identity that *must* close with a signed manifest; missing close is an incident and start refuses.
