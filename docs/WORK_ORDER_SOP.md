# WORK ORDER SOP — for SGH (voice, mobile)

**Reader:** SuperGrok Heavy Chatboxes — **desktop Chat (DT)** and **Android Voice**. Same
SGH, two surfaces. Ara on the phone is Voice. SGH is also **one of the DOM research
rails** (with free Gemini/Google search, ChatGPT chatbot, Perplexity, Bing). Not Grok Code (COW), not Grok Build, not
`sgh-api`. **This is how you assign work to COSMOS.** Do not write a daemon. Do not
install cron. Do not drop `SOP.md` at repo root. Schema: `docs/WORK_ORDER_SPEC.md`.
Keith 2026-09-02.

You **format a JSON work order and drop the file.** A Windows runner on Keith’s desktop picks it up, creates the named agent, and runs it write-private. You do not execute the job. You do not write the live COSMOS tree.

**Voice path (Keith 2026-09-03):** Grok Voice on this SGH phone app **is** how Keith controls COSMOS by voice. CVM (COSMOS Voice / DT CVM) is superseded. Do not ask for a COSMOS Voice app. Drop the work order; Core runs it.

## Format — six fields, all required

One JSON object. No extra required keys. Filename: `wo-<stamp>.json` (example `wo-20260902T103000.json`). **Windows-legal only:** no `: * ? " < > | \` in the name. Do **not** put the timezone in the filename (`wo-…-05:00.json` cannot be checked out on Windows — GitHub Desktop clone fails with `invalid path`). Timestamp timezone belongs in the JSON `Timestamp` field.

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

**Preload SOP (Keith 2026-09-08):** do not drop a naked Task. Context source
must name DHx + `docs/AGENT_BOUNDARIES.md` + (for pane/coding jobs)
`work_orders/ccr/CREW/IN/PREFIX.md` and `CACHE_RULE.md`. The Task paragraph
is the **tail**. Canon: `docs/PROMPT_CACHE.md`. P11.

## Agent — what you may name

| Want | Agent field |
|---|---|
| COSMOS coding / tree proposals (default) | `xAI \| Grok \| grok-4.6` |
| Prepaid orch MOTIF tick (do not flood) | `xAI \| grok \| prepaid-orch` |
| Gemini judge | `Google \| Gemini \| <model>` |
| OpenAI coding (Codex rail) | `OpenAI \| Codex \| gpt-5.3-codex` |
| Headless SSA drop (simple orch background) | `Groq \| gpt-oss \| 20b` (or Agent `SSA` — remaps to groq) |
| **MOTIF RESEARCH** | **Step 1. Do not skip.** Task says `Route: DOM`. Use the **existing BTS/COSMOS Chrome path** (chrome-bridge / Chrome MCP / Chrome CLI / playwright-dom, no window). **LIVE 2026-09-06:** Bing SERP, Cloudflare AI Playground, Copilot CLI. SGH+GEM first when AUTH. Do not rebuild. Not Gitur. Not dump-dom. Ask the tools index. |

**Do not put Cursor in Agent.** The desk refuses that family. Cursor is a **separate coding lane** (Cloud Agent on this GitHub repo). If you want Cursor on a **BUILD**, say `Route: CURSOR` in **Task** and keep Agent as Grok — COW dispatches Cursor; you do not. **Research goes on the DOM rails, not Gitur.**

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
2. **System daemon** (`cosmos/cosmos_sgh_drop_ingest.py`, schtask **COSMOS SGH Drop Ingest**) reads it and files a DROPPED record into the live bucket: `live/state/work_orders/bucket/` (runtime root `V:\A\Ai\COSMOS\live`). You do not need COW for this hop.
3. Schtask **`COSMOS Work-Order Runner`** (~15s) **creates a session of the Agent type** (Grok / Codex / Gemini from the three-part Agent field) in an attempt-private workspace. That session executes the Task. It does not write the live tree.
4. **DONE** = Output file exists. Lands in `live/state/work_orders/assigned/` (the done folder). **FAILED** = no Output.
5. **Checks (BUILD only):** after a **BUILD** deposit, the same Work-Order Runner invokes **Gitur** — one GitHub pass, one Cursor Cloud Agent pass, one GitLab CI pass against the proposal — not against the live tree. Stamps `checks` on the order. **Skip Gitur on RESEARCH orders.** A rail that is not wired is **UNMEASURED**, never invented green.
6. **This TUI orchestrates; CCr disposes (Keith 2026-09-04):** reads Output **and** (for BUILD) the check stamps, reviews/refines, `--accept` or `--reject`. **CCr writes** accepted proposals to the live tree. This TUI does **not** author the implementation, does not execute the job, does not spawn the agent in-chat. It **does** write the work order. It **runs Gitur for BUILD only**. **Research goes on the DOM rails already in BTS-MESH/COSMOS** (ROLD Rule 1; Chrome CLI / chrome-bridge; no window).

Do not mark COMPLETED yourself. Do not assume the GitHub file is the live tree.

## Lanes vs checks (do not conflate)

Cursor is **not** a post-DONE critic. It is an **adversarial parallel coder** (Cloud Agent, Opus 5 / Sonnet class on Ultra). Spec: `docs/ADVERSARIAL_LOOP.md`.

| | When | Family | What |
|---|---|---|---|
| **Lane A — Grok** | Pickup | xAI Grok Code 4.6 | Executes the Task. Writes Output. `Agent` field stays Grok. |
| **Lane B — Cursor** | Pickup, **BUILD** orders only, **no shared context** | Cursor Cloud Agent — **Opus 5 / Sonnet class** (Ultra mix; Composer 2.5 refused) | Independent clone + PR `WO: <task>`. Parallel **coder**. **Not research.** Not the `Agent` field. Wallet = Cursor Ultra, not `claude -p`. |
| **GitHub Actions** | After DONE, before COW | none (CI) | Status checks. UNMEASURED until a workflow exists. |
| **GitLab CI** | After DONE, before COW | none (CI) | `.gitlab-ci.yml` tests. |

Neither lane may read the other's branch, PR, or Output before submitting. Two takes; COW compares. A reviewer (Bugbot / Copilot) is optional and must not replace Lane B. Perfect agreement on a hard task is suspicious — flag it.

COW reads both takes + `Verdict`, then `--accept` / `--reject`.

## Do not

- Invent `cosmos_daemon.py`, Linux cron, or a second 1-minute task.
- Use absolute Output (`V:\…`, `/home/…`).
- Name Cursor or Claude as Agent.
- Write `V:\Ai` (GrokBot’s pen).
- Delete anything. Propose `_delme\` if something must go.
- Collapse DONE into COMPLETED.
- Dump the agent’s code into Chat. The Output file is the deliverable.

## Cursor (parallel builder)

Do **not** put Cursor in the `Agent` field. The desk still refuses that family. On **BUILD** drops the runner launches Lane B as a Cloud Agent (Opus 5 / Sonnet; Composer 2.5 refused). **Do not launch Cursor / Gitur on RESEARCH drops.** Setup: `docs/CURSOR_EXEC.md`. Bugbot may review a BUILD PR; it is not a substitute for Lane B itself.

## Pointers (desktop canon)

- Schema: `docs/WORK_ORDER_SPEC.md`
- Dual-lane: `docs/ADVERSARIAL_LOOP.md`
- Verdict: `docs/VERDICT_SPEC.md`
- Cursor lane: `docs/CURSOR_EXEC.md`
- Boundaries: `docs/AGENT_BOUNDARIES.md`
- DHx: `docs/AGENT_BRIEF.md`
- Routing: `docs/ROUTING.md`
