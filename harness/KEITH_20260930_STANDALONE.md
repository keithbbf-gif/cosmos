# Keith 2026-09-30 — COSMOS CODE standalone and 4C

**Speaker:** Keith, this ORC session.  
**Status:** Settled product definition. Supersedes the 4C guess and the standalone guess in `COSMOS_CODE_ARCHITECTURE_AND_BUILD_PLAN.md` §10 items 2 and 6, and in `BUharness.md` decisions 2 and 4.  
**Scope:** `V:\streams\cosmos_code`. This file does not authorize a write to `V:\A\Ai\COSMOS`.

## 4C

4C is the free checker suite: **pytest**, **ruff**, and the **legacy code checkers (free)**.

On the Python package already in `product\cosmos_code`, the free legacy checkers are `py_compile` and `mypy`. Other languages keep the same shape: the test runner, the linter, and that language’s free legacy checkers. A missing checker is `UNAVAILABLE`. It is not a pass.

4C is the grade. Claude, Codex, AGY, DeepSeek, Cursor, and Z-code are optional native harnesses. They are not 4C.

## Standalone

COSMOS CODE is an integral part of COSMOS, pulled out as its own package so it can be compared directly with Hermes and Claude Code.

It is a basic coding app in the Hermes sense:

- The core is the **COSMOS Harness**. It seats HERO agents from any model. The product bar is better results than Claude Code, Codex, and the other native harnesses, in every case. The bakeoff pack is the evidence that bar requires.
- A TUI with the options and features of a Hermes-class coding app.
- Account setup, token-center account integration, and our interface with the payment portal.
- The 4Cs.
- The user chooses which installed harness seats the agent.
- Optional native harnesses, installed only if the user wants them: Claude, Codex, AGY, DeepSeek, Cursor, Z-code. The COSMOS Harness remains the superior seat in every case.

## Spend sidebar

The TUI shows spend in realtime in a sidebar.

- Daily, weekly, and monthly running totals, in tokens and in dollars.
- A token log in the OpenRouter style: input, cache hit, output, cost, and the same class of fields.
- Quota left on every API, quota, and subscription account.
- When each account expires or renews.
- Where usage sits against the prorata point. Keith’s example: 50% of the quota used at the halfway point in the period.

The sidebar reads the token center. It is the same account surface the app integrates with. It is not a second ledger.

## Plugins

COSMOS CODE takes plugins later. The app is built with a plugin seam. Two named plugins come after the basic app:

1. **SESSIONS.** The Sessions product already sketched on COSMOS: `builds/session-plugin` (MCP skeleton) and `builds/sessions-app` (its own shell over Core recents). Same Core data. The plugin brings that product into COSMOS CODE.
2. **CLUSTERS.** A TUI for overseeing clusters of agents. Section of record: `V:\streams\Cosmos_clusters\01_CLUSTERS.md`.

## Still open

1. Legal coder contract: `Role` × `output.what` × first line. `HARNESS.md` and `CANON_SPAWN.md` still disagree.
2. Windows sandbox backend. Prove filesystem, network, environment, and process-tree containment. `policy_only` stays blocked. Generated code waits on that proof.
3. Which native door is first, and the approved small spend cap for a live call.
4. CCr picks the clean Gitur base before any implementation work order.
