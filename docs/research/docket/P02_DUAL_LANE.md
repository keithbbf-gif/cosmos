# P02 — Dual-lane BUILD, no shared context

**Kind:** method / occupancy seating. **Status:** FILE. **Fee:** US provisional micro $65.

## What it is (in-tree)

Two builders on the same decided work, **no shared context** (no shared transcript, no peeking at the other lane’s branch). Adversarial: two builders, **not** builder-plus-checker. Compare is a later consensus. Encoded MOTIF stage 4; `docs/ADVERSARIAL_LOOP.md`. Forge seats (`forge.ccr` + `forge.adv_N`) are a product seating.

## Problem / scar

Shared-context debate lets a weak agent pollute a strong one (Wynn, Satija, Hadfield 2025). Builder-plus-nanny is the stacked slice: the second seat is hired to agree. OpenAI **US12,405,822 B1** (granted 2025) *teaches a shared workspace* — the anti-shape.

## Written description

1. After CONSENSUS names the work, spawn **two** builder attempts.
2. Each attempt has a private workspace and a private context. Neither builder may read the other’s context, branch, or intermediate artifacts until compare.
3. Each attempt must produce a running spike.
4. Compare is a later consensus step, not a silent merge by a third model.
5. The live tree has **one** writer (P05). Builders propose; they do not hold the pen.

## Already public

Dual-lane described in public `cosmos` MOTIF (2026-08-23). Gitur dual-lane (Grok + Cursor) is operational occupancy, not a secret.

## Prior art to name (R1)

**Related:** Galápagos N-version LLM arXiv:2408.09536; N-Version Programming with Coding Agents arXiv:2606.20158; Croto arXiv:2406.08979 (independent teams *then* interchange); IBM **US20260252812A1** (parallel contestants who later rank each other); Avizienis 1985; Knight & Leveson 1986. Twilio US20250165890A1 and AgentCoder = builder-checker (**anti-shape**). OpenAI US12,405,822 B1 shared workspace (**anti-shape**). Aider Architect/Editor: plan then edit — executor sees the plan.

**Not found:** a granted US patent that *forbids* two coding agents from reading each other’s context as the inventive occupancy. UNKNOWN unpublished.

## What this is not

Not “two agents code in parallel.” Not N-version at runtime with a voter. Not shared-ledger multi-agent (OpenAI). Not builder-plus-linter.

## Suggested independent idea

Isolating two full builders (each must run) with a peeking ban until compare, plus a single disposer on the live tree.
