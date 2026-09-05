# Cursor Execution for Cosmos Work Orders

Cursor is **Lane B**: adversarial parallel coder on Cloud Agents. **Model pinned 2026-09-02: `claude-opus-5`** (GET /v1/models displayName Claude Opus 5). Composer 2.5 / Auto was the GitHub token burn (cache-read of the whole repo, ~2M tokens/min × 7 agents). Not a post-DONE check.

**This TUI does not code** (Keith 2026-09-04). It writes the work order, launches
this lane, reviews/refines the PR, then CCr writes the live tree.

## Goal

Use Cursor Cloud Agents as an **alternate executor** for the same work order Grok Code 4.6 runs. Independent clone. No peeking. PR against main titled `WO: <task>`.

## How to trigger

1. Work orders stay JSON in `work_orders/drop/` (same six fields as Grok).
2. Preferred: GitHub Issue `WO: <task>` with JSON in the body, label `cursor-execute`.
3. Desktop runner should also launch Lane B at **pickup** (same Task text, no Grok Output in the prompt).
4. Workaround if Cloud Agent lacks Issues scope: paste work-order content into the agent prompt. PAT `GH_TOKEN` with Issues read/write if using the issue path.

## Output contract

- PR against main (or the branch named in the work order).
- On merge/close, verdict still follows `docs/VERDICT_SPEC.md` — Grok writes `Verdict`; a third-family reviewer writes `Comparison`.
- Enable Bugbot on the repo for automatic review of the Cursor PR (reviewer, not a second Composer).

Full loop: `docs/ADVERSARIAL_LOOP.md`.
