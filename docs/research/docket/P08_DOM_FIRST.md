# P08 — DOM-first as first-class unmetered rail

**Kind:** method / routing policy. **Status:** FILE. **Fee:** US provisional micro $65.

## What it is (in-tree)

The **browser/DOM** is a first-class scheduler rail and the **preferred** rail because it depends on nothing that can run out (credit, quota, billing, key, consent). Metered APIs are explicit, audited fallback. Contained DOM workers: own OS identity, ephemeral profiles, Job Objects, typed failures UNREACHABLE / SESSION_EXPIRED / AUTH_REQUIRED / BROKE. AD-6.

## Problem / scar

API-only agents die when the key, quota, or vendor dies. DOM is usually a *tool*, not the preferred unmetered path.

## Written description

1. Register DOM workers as a scheduler rail, not a one-off script.
2. Routing policy data: DOM first, API second; fallback is explicit and ledgery.
3. Typed failures; report-never-retry unless contract-idempotent.
4. Prefer this rail for RESEARCH (P01) because returns must not depend on prepaid remaining.

## Already public

DOM-first in public architecture 2026-08-23.

## Prior art to name (R3)

Playwright; Playwright MCP; browser-use; Stagehand; Skyvern; Magentic-One WebSurfer; **US12101373B2** (browser RPA); **CN119248379B** (LLM + Playwright scheduler); computer-use / Operator-class **metered** products. Distinctive “prefer DOM **because it cannot run out of credit**” as routing policy: **UNKNOWN** as patented. Ops folklore is widespread.

## What this is not

Not “browser automation exists.” Not WICG `scheduler.postTask`. Not OpenAI Operator (metered).

## Suggested independent idea

Scheduler routing that prefers a contained DOM rail *because* it cannot exhaust credit, with typed failures and audited API fallback.
