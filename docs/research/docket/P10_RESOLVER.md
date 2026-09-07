# COSMOS-P10 — Resolver: sentinel root; existence is not identity

**Title:** Boot identity of an AI runtime root by sentinel content where existence of a directory is not identity
**Kind:** System (narrow)
**Status:** FILE (narrow)
**Fee:** $65 micro-entity provisional
**Date:** 2026-09-07
**Legend:** ATTORNEY WORK PRODUCT — NOT A FILED PATENT APPLICATION — FOR COUNSEL ONLY
**Inventor:** Name of inventor: ________________________________ (counsel to complete). The source tree discloses the operator as Keith. This preparer does not sign as inventor.

Standalone written description for a US provisional. Not a filed application. Not claims. Not a novelty opinion. Counsel files. Duplicate HOW_IT_WORKS.pdf at filing.

## Cross-reference

Sisters COSMOS-P01 through COSMOS-P13. No claim of benefit of a sister. 37 CFR 1.53(c): no technical add-after.

## Field of the invention

[0001] The present disclosure relates to identifying a runtime root of an AI operating system by sentinel file content rather than by path existence, parent-walking, or a fallback ladder of drives.

## Background of the invention

[0002] Empty-dir scar: a path that exists is treated as the install. Fallback ladders silently pick the wrong tree. Two writers on two roots. That is a deletion class when the wrong tree is overwritten.

## Brief summary of the invention

[0003] At boot, resolve one root by reading a sentinel file content, not by path existence. Match declared system and tree_id; refuse READY on mismatch or missing install record. Do not walk parents, do not try a list of drives, do not treat an empty directory as identity.

## Definitions

[0004] As used herein, "Sentinel" means A file whose content (not its path) identifies the runtime root.

[0005] As used herein, "READY" means The service state that may serve. Forbidden without sentinel match.

## Brief description of the drawings

[0006] FIG. 1 shows a boot resolver reading sentinel file content (.cosmos-root.json system and tree_id). An empty directory that exists is marked NOT IDENTITY. Parent-walk and drive-literal fallbacks are marked FORBIDDEN.

[0007] The drawings are described in prose so that a person of ordinary skill can produce sheet drawings. Sheet drawings may be added by counsel before filing. Do not add new matter after a filing date.

## Detailed description

[0008] At boot, resolve one root by reading a sentinel file content, not by path existence.

[0009] Preferred sentinel: .cosmos-root.json declaring system=COSMOS and a tree_id. Preferred live tree_id: KMesh-COSMOS-live.

[0010] Match declared system and tree_id against the install record. Refuse READY on mismatch or missing install record.

[0011] Do not walk parents. Do not try a list of drives. Do not treat an empty directory as identity.

[0012] No import-time side effects. The resolver is instantiated at boot composition.

[0013] Two roots must not be conflated: the repo tree (tracked code) and the runtime root (live/). Existence of a folder is not identity of either.

[0014] Every path resolves through a declared role under that root. Nothing assembles a path by hand from a drive letter.

## Best mode

[0015] cosmos_paths resolver. Service cannot go READY without sentinel-verified root. AD-5. Encoded cosmos/cosmos_paths.py.

## Further embodiments

[0016] A unit test plants an empty directory at a tempting path and asserts the resolver refuses it.

## Disclosure clock (already public)

[0017] Resolver rules in public architecture 2026-08-23.

## Information concerning related art (not an IDS; not a novelty opinion)

[0018] OCI digest versus tag; Nix require-sigs / sandbox-fallback (fallback is the anti-pattern); git objects; chroot (path, not content); systemd-nspawn --root-hash; SLSA/in-toto/Cosign; HSTS fail-closed. No close patent found on JSON sentinel plus refuse empty-dir plus no parent-walk as AI-OS boot identity. Unknown as blocking. Narrow.

## What this disclosure is not

[0019] Not chroot. Not Docker tags. Not a new hash algorithm.

## Statement of invention (not claims)

[0020] Boot identity of an AI runtime root by sentinel content, where existence of a directory is not identity and fallback ladders are forbidden.

[0021] Counsel may draft claims. The foregoing is a statement of invention, not a claim set under 35 U.S.C. 112(b).

## Appendix to attach at filing

[0022] HOW_IT_WORKS.pdf (APP_OS: SCAR, ROLD, carry-over; APP_COSMOS; APP_CRUCIBLE; APP_BTS_MESH). Duplicate the appendix into this provisional at filing. A provisional cannot claim benefit of a sister.
