# P09 — Spend gate fail-closed; confirm-to-widen

**Kind:** method / system. **Status:** FILE. **Fee:** US provisional micro $65.

## What it is (in-tree)

A spend cap **cannot silently widen**. POST without explicit confirm → **HTTP 409 `WIDEN_REQUIRES_CONFIRM`**. Cap does not move on the 409. Signed `BUDGET_SET` / `SPEND_CAP_REFUSED` on the ledger. Measured `docs/CHANGELOG_2026-08-30_CC_AUDIT.md`.

## Problem / scar

OpenAI removed hard budget limits (notify-only). Admin APIs that raise `max_budget` without a two-step confirm. Silent fallback reroute that spends a different rail.

## Written description

1. Each rail has a signed cap.
2. A request that would raise the cap without a confirm token is refused (typed 409). The stored cap is unchanged.
3. Widen requires an explicit confirm on the same cap object; ledger the grant or the refusal.
4. Fail-closed: over-cap work does not run.

## Already public

Architecture / changelog in public cosmos tree (2026-08-23+).

## Prior art to name (R3)

LiteLLM virtual keys / tag budgets (admin can raise); Cloudflare AI Gateway spend limits 2026-06 (block by default; Dynamic Route can reroute); Anthropic workspace limits; LangSmith evaluator weekly cap; **US20250299128A1** multi-cloud budget throttle; EP4381451A1; PCI dual-control; 21 CFR 11.10. OpenAI hard-cap **removal** is the scar, not a teaching of confirm-to-widen. Combination (AI-rail cap + no silent widen + typed confirm + signed ledger): **UNKNOWN as blocking.**

## What this is not

Not AWS Budgets alerts. Not “circuit breaker exists.”

## Suggested independent idea

An AI-rail spend cap that cannot move without a typed confirm, with the refusal itself ledgery.
