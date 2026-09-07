# COSMOS-P04 — Runtime-binding gate versus green-log

**Title:** Method of binding completion to a live-system-emitted value with fail-closed refusal
**Kind:** Method / selection gate
**Status:** FILE
**Fee:** $65 micro-entity provisional
**Date:** 2026-09-07
**Legend:** ATTORNEY WORK PRODUCT — NOT A FILED PATENT APPLICATION — FOR COUNSEL ONLY
**Inventor:** Name of inventor: ________________________________ (counsel to complete). The source tree discloses the operator as Keith. This preparer does not sign as inventor.

Standalone written description for a US provisional. Not a filed application. Not claims. Not a novelty opinion. Counsel files. Duplicate HOW_IT_WORKS.pdf at filing.

## Cross-reference

Sisters COSMOS-P01 through COSMOS-P13. No claim of benefit of a sister. 37 CFR 1.53(c): no technical add-after.

## Field of the invention

[0001] The present disclosure relates to accepting a change to a running computer system only when the running system itself emits a value that only it can produce, and to refusing when that value is missing or contradicts the claim.

## Background of the invention

[0002] A pipeline reports success because tests exited zero or a critic said it looks good. That is fabricated compliance: a plausible lie that closes the ticket while the running system does not do the thing. The inventor names this the placation class.

[0003] Continuous integration as a quality gate is related and, if treated as done, is the opposite occupancy.

## Brief summary of the invention

[0004] For a change to be accepted, require an artifact that only the running system can produce (a live API value, a ledger event field, a hash only the true run emits). Treat CI green, critic LGTM, and UI checks as projections, never authority. If the live emit is missing or contradicts the claim, record a refusal (fail-closed). Do not repair a green log in place. The report of the change must carry the live artifact or the refusal.

## Definitions

[0005] As used herein, "Live emit" means A value only the running system can produce.

[0006] As used herein, "Projection" means A rebuildable view (dashboard, SQLite cache, CI log) that is never authority.

[0007] As used herein, "Fail-closed" means Missing or contradicting evidence is a refusal, not a silent pass.

[0008] As used herein, "Placation" means A plausible claim of compliance that the artifact contradicts.

## Brief description of the drawings

[0009] FIG. 1 shows a claim of done entering a gate. A live emit from the running system passes. An exit code, a critic LGTM, and a dashboard color fail-closed as projections.

[0010] The drawings are described in prose so that a person of ordinary skill can produce sheet drawings. Sheet drawings may be added by counsel before filing. Do not add new matter after a filing date.

## Detailed description

[0011] For a change to be accepted, require an artifact that only the running system can produce.

[0012] Examples of a live emit: an HTTP body from the resident Core bearing tree_id and a field only the true run can emit; a ledger event with a hash chain head; a response.model field that binds the model that actually answered.

[0013] Treat CI green, critic LGTM, and UI checks as projections, never authority.

[0014] If the live emit is missing or contradicts the claim, record a refusal. Do not repair a green log in place.

[0015] The report of the change must quote the live artifact or the refusal. Intention is not evidence.

[0016] A negative control may remain red on purpose. Painting it green is placation.

[0017] SCAR-derived law: every consequential action emits a machine-checkable artifact. Encoded docs/SCAR_PLACATION.md (2026-08-25) and kernel AD-11.

## Best mode

[0018] COSMOS MOTIF gate against live Core at http://127.0.0.1:8770, tree_id=KMesh-COSMOS-live. Example: GET /jukebox returns 200 with QUEUED/RUNNING/BROKE/CLEAN counts; that body is the emit, not a test exit code.

## Further embodiments

[0019] A model rail binds response.model, not the request. allow_fallbacks=false. A silent swap is a failed bind.

## Disclosure clock (already public)

[0020] Runtime-binding language is in public MOTIF and architecture (cosmos created 2026-08-23).

## Information concerning related art (not an IDS; not a novelty opinion)

[0021] Related: Proof-or-Stop arXiv:2607.14890; Microsoft Azure 2026-08-29 validate at runtime; The New Stack runtime verification; CI as quality gate (Jenkins, GitHub Actions) as the opposite occupancy if CI is treated as done. No United States patent found that claims only a live-system-emitted value is done. Patent occupancy thin. Paper and engineering occupancy high in 2026.

## What this disclosure is not

[0022] Not don't-trust-CI as a slogan. Not a test framework. Not a bake-off.

## Statement of invention (not claims)

[0023] Binding finished to a value only the live tree can emit, with fail-closed refusal when that value is absent.

[0024] Counsel may draft claims. The foregoing is a statement of invention, not a claim set under 35 U.S.C. 112(b).

## Appendix to attach at filing

[0025] HOW_IT_WORKS.pdf (APP_OS: SCAR, ROLD, carry-over; APP_COSMOS; APP_CRUCIBLE; APP_BTS_MESH). Duplicate the appendix into this provisional at filing. A provisional cannot claim benefit of a sister.
