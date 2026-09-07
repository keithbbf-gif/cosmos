# COSMOS-P09 — Spend gate; confirm-to-widen

**Title:** Fail-closed spend cap that cannot silently widen without typed confirm and ledgered refusal
**Kind:** Method / system
**Status:** FILE
**Fee:** $65 micro-entity provisional
**Date:** 2026-09-07
**Legend:** ATTORNEY WORK PRODUCT — NOT A FILED PATENT APPLICATION — FOR COUNSEL ONLY
**Inventor:** Name of inventor: ________________________________ (counsel to complete). The source tree discloses the operator as Keith. This preparer does not sign as inventor.

Standalone written description for a US provisional. Not a filed application. Not claims. Not a novelty opinion. Counsel files. Duplicate HOW_IT_WORKS.pdf at filing.

## Cross-reference

Sisters COSMOS-P01 through COSMOS-P13. No claim of benefit of a sister. 37 CFR 1.53(c): no technical add-after.

## Field of the invention

[0001] The present disclosure relates to gating spend on AI rails so that a cap cannot silently widen, a refused widen is itself recorded, and over-cap work does not run.

## Background of the invention

[0002] OpenAI removed hard budget limits (notify-only). Admin APIs that raise max_budget without a two-step confirm. Silent fallback reroute that spends a different rail. Those are the scars.

## Brief summary of the invention

[0003] Each rail has a signed cap. A request that would raise the cap without a confirm token is refused (typed 409). The stored cap is unchanged. Widen requires an explicit confirm on the same cap object; ledger the grant or the refusal. Fail-closed: over-cap work does not run.

## Definitions

[0004] As used herein, "Confirm token" means An explicit operator confirmation bound to the same cap object.

[0005] As used herein, "WIDEN_REQUIRES_CONFIRM" means The typed refusal when a widen is requested without confirm.

## Brief description of the drawings

[0006] FIG. 1 shows a request that would raise a spend cap. Without a confirm token the gate returns a typed 409 WIDEN_REQUIRES_CONFIRM. The stored cap is unchanged. A signed ledger event records the refusal.

[0007] The drawings are described in prose so that a person of ordinary skill can produce sheet drawings. Sheet drawings may be added by counsel before filing. Do not add new matter after a filing date.

## Detailed description

[0008] Each rail has a signed cap.

[0009] A request that would raise the cap without a confirm token is refused. Preferred embodiment: HTTP 409 WIDEN_REQUIRES_CONFIRM. The stored cap does not move on the 409.

[0010] Widen requires an explicit confirm on the same cap object.

[0011] Ledger BUDGET_SET or SPEND_CAP_REFUSED. The refusal itself is evidence.

[0012] Fail-closed: over-cap work does not run.

[0013] Silent fallback to another rail that spends is also a widen and is refused unless confirmed.

## Best mode

[0014] Measured in the COSMOS tree (docs/CHANGELOG_2026-08-30_CC_AUDIT.md). Signed BUDGET_SET / SPEND_CAP_REFUSED on the ledger.

## Further embodiments

[0015] A POST to a budget route without confirm never moves the cap. A subsequent GET shows the old cap. That GET body is the live emit (COSMOS-P04).

## Disclosure clock (already public)

[0016] Architecture and changelog in public cosmos tree (2026-08-23 and following).

## Information concerning related art (not an IDS; not a novelty opinion)

[0017] LiteLLM virtual keys / tag budgets (admin can raise); Cloudflare AI Gateway spend limits 2026-06; Anthropic workspace limits; LangSmith evaluator weekly cap; US20250299128A1 multi-cloud budget throttle; EP4381451A1; PCI dual-control; 21 CFR 11.10. OpenAI hard-cap removal is the scar, not a teaching of confirm-to-widen. Combination (AI-rail cap plus no silent widen plus typed confirm plus signed ledger): unknown as blocking.

## What this disclosure is not

[0018] Not AWS Budgets alerts. Not circuit breaker exists.

## Statement of invention (not claims)

[0019] An AI-rail spend cap that cannot move without a typed confirm, with the refusal itself ledgery.

[0020] Counsel may draft claims. The foregoing is a statement of invention, not a claim set under 35 U.S.C. 112(b).

## Appendix to attach at filing

[0021] HOW_IT_WORKS.pdf (APP_OS: SCAR, ROLD, carry-over; APP_COSMOS; APP_CRUCIBLE; APP_BTS_MESH). Duplicate the appendix into this provisional at filing. A provisional cannot claim benefit of a sister.
