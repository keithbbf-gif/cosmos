# COSMOS-P11 — SEED / signed session close (OPEN_CONTEXT)

**Title:** Signed session close as a fail-closed operating-system incident
**Kind:** Method / system (narrow)
**Status:** FILE (narrow)
**Fee:** $65 micro-entity provisional
**Date:** 2026-09-07
**Legend:** ATTORNEY WORK PRODUCT — NOT A FILED PATENT APPLICATION — FOR COUNSEL ONLY
**Inventor:** Name of inventor: ________________________________ (counsel to complete). The source tree discloses the operator as Keith. This preparer does not sign as inventor.

Standalone written description for a US provisional. Not a filed application. Not claims. Not a novelty opinion. Counsel files. Duplicate HOW_IT_WORKS.pdf at filing.

## Cross-reference

Sisters COSMOS-P01 through COSMOS-P13. No claim of benefit of a sister. 37 CFR 1.53(c): no technical add-after.

## Field of the invention

[0001] The present disclosure relates to making session identity of an AI operating system depend on a signed close manifest, such that a missing or invalid close is an incident and start refuses.

## Background of the invention

[0002] Sessions vanish. The next session fabricates continuity. Vendor memory features store facts without a fail-closed close. CONTINUITY arXiv:2609.05269 (2026-09-05) is the closest paper and must be watched by counsel.

## Brief summary of the invention

[0003] close_session must emit a signed manifest covering declared fields (inherited facts, active leases, open watchers, handoff recipient). Absence, length mismatch, or HMAC failure is an incident (OPEN_CONTEXT), not a warning. start_session reads the manifest under its declared length and HMAC before injecting carry-over. An optional auto-resession clock consumes the same seed. A HOLD pause never self-clears.

## Definitions

[0004] As used herein, "SEED" means A signed context manifest written at close (SEED.json plus declared length/HMAC).

[0005] As used herein, "OPEN_CONTEXT" means The incident raised when close lacks a valid manifest.

[0006] As used herein, "HOLD" means A pause that never self-clears.

[0007] As used herein, "Resume gate" means A pause at boot that may auto-resume on a native clock if the operator does not choose.

## Brief description of the drawings

[0008] FIG. 1 shows close_session emitting a signed SEED.json (declared length and HMAC). Absence is OPEN_CONTEXT. start_session refuses NO_SEED, BAD_SEED, and IDENTITY_MISMATCH. A HOLD pause never self-clears; a resume-gate pause may auto-resume on a native clock.

[0009] The drawings are described in prose so that a person of ordinary skill can produce sheet drawings. Sheet drawings may be added by counsel before filing. Do not add new matter after a filing date.

## Detailed description

[0010] close_session must emit a signed manifest covering declared fields: inherited facts, active leases, open watchers, handoff recipient.

[0011] Absence, length mismatch, or HMAC failure is an incident (OPEN_CONTEXT), not a warning.

[0012] start_session reads the manifest under its declared length and HMAC before injecting carry-over. It refuses NO_SEED, BAD_SEED, and IDENTITY_MISMATCH.

[0013] A lightweight session pointer may sit beside the seed (BUCm.toml in the source tree) as one truth, never a competing second handoff.

[0014] Resume gate: after boot loads carry-over, one option (resume all, subset, hold). No affirmative selection implies auto-resume on a native clock. Default is motion.

[0015] A HOLD never self-clears. The two pause kinds are not the same.

[0016] Carry-over is why the OS survives context death. MOTIF is what the clock drives after the seed is accepted.

[0017] This is not ChatGPT memory.

## Best mode

[0018] cosmos_session.close_session / start_session. AD-10. docs/PAUSE_PROTOCOL.md. Native fifteen-second clock (cosmos_watchdog2.py) honors mode in the pause flag.

## Further embodiments

[0019] Auto-resession watermark at about seventy percent of context; hard close at ninety percent; pack to live/state/session_saves/. Improper close: resume from session log and/or running_session_file.toml.

## Disclosure clock (already public)

[0020] AD-10 in public architecture 2026-08-23.

## Information concerning related art (not an IDS; not a novelty opinion)

[0021] CONTINUITY arXiv:2609.05269 (2026-09-05 — signed context manifests plus CLOSE/OPEN receipts; closest paper; watch); Portable Agent Memory arXiv:2605.11032; Context Passport; CRAFT handoff; ctx handover; vendor memory; CRIU; JWT/JWS; US20250259069A1 reconstitutable sessions. Incident-on-missing-close as OS rule: unknown as patented.

## What this disclosure is not

[0022] Not ChatGPT memory. Not CRIU. Not write a notes file.

## Statement of invention (not claims)

[0023] Session identity that must close with a signed manifest; missing close is an incident and start refuses.

[0024] Counsel may draft claims. The foregoing is a statement of invention, not a claim set under 35 U.S.C. 112(b).

## Appendix to attach at filing

[0025] HOW_IT_WORKS.pdf (APP_OS: SCAR, ROLD, carry-over; APP_COSMOS; APP_CRUCIBLE; APP_BTS_MESH). Duplicate the appendix into this provisional at filing. A provisional cannot claim benefit of a sister.
