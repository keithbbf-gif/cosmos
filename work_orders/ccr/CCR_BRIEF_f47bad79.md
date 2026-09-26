# CCr brief — what to do, and why

> **SUPERSEDED 2026-09-18.** Unique-head is **dead**. LiT is `origin/main` `4ebc4efd`.  
> **Read `work_orders/ccr/CCR_ORC_NOW.md`.** The “do not pull main” block below is stale and will wreck the tree if you follow it.

For **`f47bad79`** (pen holder). Keith will point you here.
Author: orch chair `716fbaea` (no pen). Read-only check 2026-09-17T19:28-05:00.
Longer dump: `work_orders/ccr/SUCCESSION_f47bad79.md`.

You already hold `live/state/control/CCR.lease` (sid `f47bad79-25a6-461c-baa6-064801f4e042`, token **4**, pid 77372). Unique HEAD **`8b5ad84`**. Occupancy **165/165**. Core `:8770` ready.

---

## Do these

### 1. Do not merge Gitur PRs onto unique HEAD

| PR | Why not |
|---|---|
| cosmos **#564** Daytona | Built on GitHub `main` where `cosmos_sandbox.py` did not exist. Sets `HOST_PEN` = whole `V:\`, which would refuse Job-Object cwd under `live/work`. Live already has the facade (`job_object\|daytona\|e2b`, no key → `UNCONFIGURED`). Selftest **12/12**. GET `/sandbox` MEASURED `composed=job_object`. |
| cosmos **#563** plugin-waist | Same *name* (48 bodies + shims). Different *tree*. Unique HEAD already has 31 `_fail_*` + 17 `_bite_*` in `tools/` + shims. Merging overlays `main` occupancy (163-era). |
| cdeck **#320** chamber | *Adds* `deck_orc.js` because `main` had no pane. Unique HEAD already paints GET/POST `/chamber`. Occupancy 165 vs Gitur’s 163 pins. A merge would drop pins. |

All three still **OPEN**, not merged. Leave them as reviews of `main`. Cherry-pick **tests/fixtures only** if unique HEAD is thinner (Daytona GET-never-mkdir / spawn-count=0; chamber 404/UNMEASURED browser fixtures). Not the `HOST_PEN=V:\` hunk.

Recall Gitur (`bc-1e2315b8`) defaulted `--once` wrong. Live `standup()` is the clock. Ignore that mouth.

### 2. Do not pull `origin/main`

Unique HEAD is ahead/behind GitHub on purpose. A pull would clobber occupancy 165 and the uncommitted KEEP work.

### 3. Keep the uncommitted KEEP work (not Gitur jobs)

These never went through Gitur. No dual-implementation fight:

- HITL bind (`cosmos_review.py` / `cosmos_studio.py` / Review paint): unbound = `MISSING_HITL_ARTIFACT`, not a green pack.json chip. steal-http **21/21**.
- Stagehand wire on the existing adapter (not a second class).
- Tool-output packets (`cosmos_packet.py`) on OR/Vertex large dumps.
- Inflight excludes `stale_flag` / `stale_reported`.
- ApprovalGate on OpenRouter/Vertex `kind=shell|git|install` (same as Cursor).
- Skill accept appends SoD ACTION after `SKILL_ACCEPTED`.

Prove if you want: commands in `SUCCESSION_f47bad79.md`. Occupancy gate already **165/165**.

### 4. Bounce Core once when you want `/action_chain` to leave n=0

Live GET `/action_chain` is **UNMEASURED n=0** — this Core process loaded `skills.py` **before** the ACTION wire. Next `accept` after bounce writes the chain. Do not bounce just to “install” sandbox: GET `/sandbox` is already MEASURED.

Loopback stays **legacy** until Keith says bearer.

### 5. Do not redo, compose, or farm-dump

- Daytona/E2B **live vendor** — HOLD until Keith pastes keys. No key → `UNCONFIGURED` is correct.
- DeerFlow, NL cron, Pi, PydanticAI, OpenHands-as-OS — SKIP (SGH vet).
- Remaining Superpowers SKILL.md — activate **one** at a time under your fence, not a farm dump. `verification-before-completion` is already **v2** MEASURED.
- Don’t bust farm caches (job pack, no patent, closest-to-job in ITEM tail).
- Pair coding is a marathon: keep two seated coder caches.
- Judges: don’t mint a new 80% write per judge. Exception: **same pack, three seats rotate** coder A / coder B / judge with role in the **tail only** — fills the porosity pair matrix. Vertex GF38 WOMBAT ≠ OpenRouter cache family.
- **Pair coding is a marathon.** Keep two seated coder caches; don’t sprint-rotate the whole crew.
- **Judges:** don’t mint a new 80% write per judge. Exception: **same pack, three seats rotate** coder A / coder B / judge with role in the **tail only**. That fills the porosity pair matrix without extra cache writes. Vertex GF38 WOMBAT is a different cache family than OpenRouter.

### 6. Gitur — **everything goes through this pen (`f47bad79`)**

Orch chair `716fbaea` opened KEEP ports onto GitHub **without your pen**. That was out of sequence again. They are **proposals only**. You dispose: keep, rewrite, close, or merge to `main`. Unique HEAD `8b5ad84` is not updated by merging them.

| PR | Job | Note |
|---|---|---|
| https://github.com/keithbbf-gif/cosmos/pull/568 | HITL bind | review + studio vs `main` |
| https://github.com/keithbbf-gif/cosmos/pull/569 | packets + OR/Vertex guard | |
| https://github.com/keithbbf-gif/cosmos/pull/570 | Stagehand / Playwright | **large playwright deletion vs `main` — look before merge** |

Composer CHECK `bc-1a03db14` is on those three. **#563 / #564 / cdeck #320** still OPEN; you already judged them vs unique HEAD.

Going forward: Cursor **BUILD** = grok-4.6. **CHECK** = Composer 2.5, not Auto. Branch from `origin/main`. **You** launch or accept Gitur. Orch drops the WO; it does not `git push`. Never extra `grok.exe`. Never `V:\Ai`.

---

## Why this shape

Gitur and unique HEAD mostly built **different artifacts under the same steal-map names**. Gitur had more eyes on **`main`**. Unique HEAD is what Core executes. Merging the PRs would replace live modules with `main`-shaped ports (empty sandbox, empty ORC pane, 163 pins).

Orch chair `716fbaea` wrote some KEEP files straight to the tree (uncommitted). That was not Gitur. You own dispose now: keep, revert, or rewrite — don’t pull Gitur on top of them unless you have compared the hunk.

---

## Live snapshot (this probe)

| Check | Value |
|---|---|
| Occupancy | **165/165** |
| Lease | `f47bad79-25a6-461c-baa6-064801f4e042` token 4 |
| `/status` | 200 ready |
| `/skills` | MEASURED v2 |
| `/sandbox` | MEASURED job_object; daytona/e2b/modal named not composed |
| `/review` | 200 blockers OK |
| `/action_chain` | UNMEASURED n=0 (bounce) |
| `/chamber` | UNMEASURED empty fold (painter exists) |
| Gitur 563/564/320 | still OPEN |

Fences: one CCr, `V:\A` only, occupancy fold-don’t-drop, extra panes in `deck_*.js` not `app.js`, no JACK’S MESH / `drawCore`, no iframe OpenWork, never delete (stage `_delme`), Opus T frozen, 700k frozen.
