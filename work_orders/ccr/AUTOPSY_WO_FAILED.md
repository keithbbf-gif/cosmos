# Autopsy — 157 failed work orders (token-economy scar)

Keith: no corpses. Autopsy, reuse, find how we got 200+ dead bodies. Opposite of token economy.

Live GET `/work_orders` n_total=217: **failed 157**, assigned 35, completed 25, bucket 0, picked 0.

## Unique HEAD (what that means)

`git rev-parse` on `V:\A\Ai\COSMOS` = **`8b5ad84e`** (2026-09-06 occupancy commit).
`main...origin/main` = **ahead 37, behind 189**.

**Unique HEAD** = this machine’s last **commit** that is **not** GitHub `main`. Gitur PRs are cut from `origin/main` (`4f8bb074` class). Pulling `main` onto this tree would overlay 189 GitHub commits onto occupancy-165 LiT — forbidden.

On **top** of `8b5ad84e` there is a huge **uncommitted** working tree (KEEP, sandbox, skills, …). So LiT ≠ unique HEAD commit ≠ GitHub. Three silos. That’s how chat/Gitur/Desktop packs never joined FIFO.

## Why they weren’t reassigned or disposed

**No xfer route on FAIL.** Runner `file_done FAILED` when Output missing or Context source is one concatenated path. WOMB never: autopsy → STYLE/prompt fix → attempt 2. Scores weren’t student-records. Failed stayed `live/state/work_orders/failed/` as board rows. Token economy: we paid **112× prepaid-orch grok** + **34× grok-4.6** to spawn, then scored FAIL on empty Output (rc=1) — **119 / 157**.

## Fail kinds (measured)

| n | kind | What actually happened |
|---|---|---|
| **119** | FAILED | “Output file missing or empty (rc is not the predicate)” — grok.exe/gemini spawned, no artifact. |
| **35** | NO_CONTEXT | Context source stored as **one** string with ` · ` — parser treats the whole blob as a missing path. Farm 16:38 today added 12 more of these. |
| **3** | BROKE | Unreadable bucket JSON. |

Oldest corpse: **2026-09-02**. Newest: **2026-09-17T16:38** (this chair, list-CTX bug). Two weeks of no pop.

Agent mix: 112 `prepaid-orch`, 34 `grok-4.6`, 6 GF38, rest noise.

## Where we went wrong

1. **Spawn grok.exe as the WO worker** — extra grok, empty Output, FAIL. Farm pythonw was the fix; we still drop_order’d into bucket and the runner raced.
2. **Context source as prose with middle dots** — 35 deaths, $0 model, 100% process.
3. **FAIL is terminal** — no attempt 2, no GAC re-seat, no STYLE xfer. Board is a graveyard, not a queue.
4. **FIFO never popped** — 157 failed still “on the board” so n_total looks like work. Token economy is **live queue length**, not historical n_total.
5. **Unique HEAD vs GitHub** — Gitur “finished” on `main` while LiT failed copies sat in `failed/`. Two books.

## Use what we can (don’t keep corpses)

- **NO_CONTEXT (35):** salvage Task text; re-drop with **list** Context source; GAC pair; attempt=2 JSONL. Do not spawn grok.exe.
- **Output-empty grok (119):** do **not** re-fire grok. Autopsy Task → if still a wish, six-field FIFO + Gitur/GAC. If already on LiT, close (xfer `superseded`).
- **Assigned 35:** check if DONE-in-name-only; close or attempt 2.
- **Failed folder:** stage to `_delme/work_orders_failed/` after JSONL autopsy rows (never unlink without Keith). Projection n_total drops. CCr does the stage.

## Token economy rule

A FAIL without `cosmos-score-attempt/1` row is a leak. Regrade is attempt N+1. Board shows **bucket+picked only**. Failed is autopsy archive, not WOMB surface.
