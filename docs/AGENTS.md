# AGENTS.md — Cosmos Repository Instructions

This file is read by native GitHub agents (GitHub Copilot code review, Copilot coding agent, Cursor Bugbot/Cloud Agents, GitLab Duo if mirrored) on every pull request and agent run.

## Project
Cosmos is a multi-agent orchestrator mesh. Grok (Ara / Grok Code 4.6) is the primary rail. Work orders live in work_orders/drop/ as JSON. Verdicts are written back into the same file under a Verdict object.

## Verdict rules (see docs/VERDICT_SPEC.md)
- Status: applied | rejected | pending
- On rejection, the verdict MUST include:
  - objection: one-line reason
  - fix: exact file path, line number, and the concrete change needed
- Never approve silently. Always name the file and line.

## Code review focus
1. Runtime-binding gate: prove the machine executes the NEW tree, not a cached snapshot.
2. Windows service: COSMOS Core must run as a real always-on resident process (scheduler, ledger, API, lease arbiter).
3. Work-order loop: claim detection, verdict write-back, session notification.
4. Federation: five blockers must be resolved before peer meshes go live.
5. D-deck UI: panels must be draggable AND resizable with snap-to-grid on release.

## Do not
- Invoke Claude or Cursor as the primary agent.
- Touch the live tree without a proposal in proposals/.
- Merge without a human or Grok Code verdict.

## Context docs
- docs/VERDICT_SPEC.md
- docs/ARA_POLL.md
- docs/ARA_STATUS_PROTOCOL.md
- docs/WORK_ORDER_SOP.md
