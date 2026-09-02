# WORK ORDER SOP — for SGH (voice, mobile)

**Reader:** SuperGrok Chat / voice / Ara on phone. **This is how you assign work to COSMOS.** Do not write a daemon. Do not install cron. Do not drop `SOP.md` at repo root. Schema: `docs/WORK_ORDER_SPEC.md`. Keith 2026-09-02.

You **format a JSON work order and drop the file.** A Windows runner on Keith’s desktop picks it up, creates the named agent, and runs it write-private. You do not execute the job. You do not write the live COSMOS tree.

## Format — six fields, all required

One JSON object. No extra required keys. Filename: `wo-<stamp>.json` (example `wo-20260902T103000.json`).

| Field | What you put |
|---|---|
| **Agent** | Exactly three parts: `Family \| Clade \| Version` |
| **Context source** | File(s) the agent may **read**. Mark `[read*]`. Never write-mode. |
| **Task** | What to do. First line: read DHx + boundaries (below). |
| **Target & scope** | What it may produce, and the fence. |
| **Timestamp** | ISO local when you drop it (include offset). |
| **Output** | `folder \| filename` **relative** (workspace only). No `V:\`, no `/`, no `..`. |

```json
{
  "Agent": "xAI | Grok | grok-4.6",
  "Context source": "docs/WORK_ORDER_SPEC.md [read*]",
  "Task": "FIRST read docs/AGENT_BRIEF.md and docs/AGENT_BOUNDARIES.md. P10: PROPOSE only. Never write the live tree. <the job in one paragraph>",
  "Target & scope": "proposals under Output only; never kernel/ledger/sched/service",
  "Timestamp": "2026-09-02T10:30:00-05:00",
  "Output": "proposals | RESULT.json"
}
```

**Task first lines are mandatory.** The work-order runner does not auto-attach DHx; if you omit them, the agent will not have the rules.

## Agent — what you may name

| Want | Agent field |
|---|---|
| COSMOS coding / tree proposals (default) | `xAI \| Grok \| grok-4.6` |
| Prepaid orch MOTIF tick (do not flood) | `xAI \| grok \| prepaid-orch` |
| Gemini judge | `Google \| Gemini \| <model>` |
| OpenAI coding (Codex rail) | `OpenAI \| Codex \| gpt-5.3-codex` |

**Do not put Cursor in Agent.** The desk refuses that family. Cursor is a **separate coding lane** (Cloud Agent on this GitHub repo). If you want Cursor, say `Route: CURSOR` in **Task** and keep Agent as Grok — COW dispatches Cursor; you do not.

**Do not put Anthropic / Claude / Sonnet / SSA in Agent.** Off the route.

## Where to drop (what you can reach from voice/mobile)

You can write GitHub. You cannot see `V:\A\Ai\COSMOS\live` from the phone.

**Drop here:**

`https://github.com/keithbbf-gif/cosmos`  
**path:** `work_orders/drop/<filename>.json`  
**branch:** default (`main`)

That folder is the SGH inbox. One JSON file per order. Do not put Python, SOP rewrites, or cron notes in this folder.

**Not a drop:** repo root, `docs/`, `cosmos/`, `live/` (you cannot see live from GitHub). A root `cosmos-test.txt` is a probe, not a work order.

## What happens after you drop

1. File exists on GitHub under `work_orders/drop/`.
2. COW files it into the desktop bucket the runner already watches: `live/state/work_orders/bucket/` (resolver path, runtime root `V:\A\Ai\COSMOS\live`).
3. Schtask **`COSMOS Work-Order Runner`** (~15s) → `PICKED_UP` → agent runs in `live/work/orders/<id>/` (not the live tree).
4. **DONE** = your Output file exists. **FAILED** = no Output. **COMPLETED** = COW accepted. You do not mark COMPLETED.
5. Tree changes land only if COW disposes a proposal. Agents never commit the live tree.

A GitHub file is **not** picked up by the runner until it is in the live bucket. Do not assume instant execution.

## Do not

- Invent `cosmos_daemon.py`, Linux cron, or a second 1-minute task.
- Use absolute Output (`V:\…`, `/home/…`).
- Name Cursor or Claude as Agent.
- Write `V:\Ai` (GrokBot’s pen).
- Delete anything. Propose `_delme\` if something must go.
- Collapse DONE into COMPLETED.
- Dump the agent’s code into Chat. The Output file is the deliverable.

## Cursor (so you do not misuse it)

Cursor is **not** this desk. It is overflow coding on **this GitHub repo** (`keithbbf-gif/cosmos`): Cloud Agents open a branch / PR (GitLab CI follows). Ultra is included on SuperGrok Heavy. It cannot be the work-order `Agent` field. It cannot write the Windows live root. If the job is “edit the GitHub tree / open a PR,” say `Route: CURSOR` in Task. If the job is “propose for the live COSMOS tree,” keep Agent Grok.

## Pointers (desktop canon)

- Schema: `docs/WORK_ORDER_SPEC.md`
- Boundaries: `docs/AGENT_BOUNDARIES.md`
- DHx: `docs/AGENT_BRIEF.md`
- Routing: `docs/ROUTING.md`
