# Steal map — mechanisms, not a second OS

**SGH 2026-09-17.** Drive pack = the Claude 9-17 review (same as Desktop).
Claude compared COSMOS only to **NousResearch/hermes-agent**. That is not
`rkchoudary/hermes`. Do not conflate them. CCr checked this against unique
HEAD `8b5ad84` + live `:8770`. Nothing here replaces Core.

## Two Hermes

| Repo | What it is | COSMOS use |
|---|---|---|
| **NousResearch/hermes-agent** | Learning-loop agent (approval, delegate, FTS5 recall, SKILL.md) | Already rebuilt COSMOS-shaped: `cosmos_approval.py` `cosmos_delegate.py` `cosmos_recall.py` `cosmos_skills.py`. Tests **46/46**. No yolo, no off, no in-process cron, no self-editing live skills. |
| **rkchoudary/hermes** | Staged delivery, sha256-chained state log, WORM, dual-control, SoD (creator ≠ reviewer ≠ approver) | Steal **SoD + action-level chain**. Analog of CCr + fenced commit + ledger. **Do not install as a second Core.** OpenFang Merkle-of-actions is the same idea. |

## Already on this tree (do not re-recommend)

- Approval / delegate / recall / skills modules (Hermes-the-agent four).
- Ledger head-cache + `fold_cached` + mac_v 2 (disk; live Core process not bounced).
- P0 exposure patches on disk: resume does not reset day cap; `wallet=api` metered; CCr lease on Arbiter; loopback guard with `live/config/loopback_trust.txt=legacy` (Keith propped the port).
- Playwright MCP satellite `playwright-dom` GATE PASS. Stagehand is the missing hybrid on top — not wired.
- Attempt-private workspaces: `cosmos_workspace.assert_not_live` / `refuse_tree_cwd`. Still on `V:\` (`live/work`). Docker/Daytona is the wipe lesson not yet true.
- Occupancy **163/163**. Core bounced 2026-09-17: `:8770` ready, ledger seq **15503** `mac_v: 2`, `authority.jsonl.head.json` seq matches. Live GET `/seats` `/approvals/pending` `/recall` `/skills` `/chamber` `/temporal` **200**. Porosity still `/5`.

## Order (improvement is not bloat)

1. Bounce Core so P0 + mac_v 2 + `/seats` actually execute. Runtime-bind: `BOOT_VERIFIED` with `mac_v: 2` and `authority.jsonl.head.json` seq match.
2. Wire the four Hermes modules: HTTP/MCP, `ApprovalGate.guard` on coding rails before shell/git/install, cDeck cards, recall refresh on a **native** clock.
3. Sandbox isolation that cannot reach host pens (`V:\Ai`, repo tree). Job-Object + Daytona/E2B backends. OpenHands **split**, not OpenHands as scheduler.
4. Stagehand on `cosmos_playwright_rail` / `cosmos_dom`. DOM-first. Gitur stays BUILD.
5. Chamber / agent-comms as a **projection** on DHx / queue / ORC CHAT. P9/P10 stay.
6. Superpowers SKILL.md pack (agentskills.io) on MOTIF DEFINE-first + CRUCIBLE. Format already exists; do not invent another.
7. Graphiti as a **fold** of ledger+CAS (`valid_at`/`invalid_at`). Not Letta Server + Postgres (H8).
8. DeerFlow research pack on DOM rails only. Children through `cosmos_delegate.py`.
9. Plugin-ize lanes (DeepSeek Harness waist). Subtract `_fail_*` / `_bite_*` scratch.

NL cron = Hermes **job language** on schtasks + WD2, not an in-process thread.
Profile isolation = tree grant + `CCR.lease`, not a second live copy.

## Do not borrow

LangGraph / Temporal / n8n / TrueForge / Dify as Core. Letta Server. MCP Memory /
Sequential Thinking as a competing SEED. CrewAI / AutoGen as the mesh. OpenClaw
free-reign / yolo. ruflo 98-agent zoo. A second scheduler, second live tree,
second memory product, or second spend authority.

Gitur reviewers (Macroscope / CodeRabbit / Qodo / Copilot) stay satellites.
Default Gitur reviewer is already Cursor Other Models Sonnet 5; CCr is Grok.
Aider stays HOLD (`MESH_ADDITIONS`). ACP is the BUILD interop; COSMOS does not
own Cursor/Codex loops.

Every steal still needs runtime binding, fail-closed, one CCr, never-delete,
net complexity down.
