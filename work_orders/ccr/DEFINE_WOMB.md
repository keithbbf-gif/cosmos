# DEFINE — WOMB (Work Order Main Board)

Keith: WOMBAT runs the WOMB. Every wish/FR/drop (orch, Voice Drop, daemons, email, cDeck CREATE) lands on the board. Then (1) DEFINE the problem (2) choose agent(s) from the **model row** (budget, ctx, OR/API rates, our ratings + public axes, STYLE/xfer, TENSOR). Pair for **high orthogonality** and **low porosity in the target axis**.

## On the board now (live GET 2026-09-17T20:xx)

| Surface | Status |
|---|---|
| GET `/work_orders` | 200 `/1` n_total=217 counts bucket=0 picked=0 assigned=35 completed=25 failed=157 |
| `docs/WISHLIST.md` + `docs/BACKLOG.md` | WD2 15s scans checkboxes → MOTIF six-field drops |
| Voice | GET `/voice` 70s poll in cDeck; Voice Drop is a drop origin |
| GET `/porosity` | MEASURED schema `/5` n_obs live — pair tensor exists |
| GET `/model_rater` | `/6` catalog+seats+preload (ctx → fat/house) |
| cDeck CREATE | kinds **AGENT / TOOL / CONNECTOR / SKILL** only. POST `/makers` + CREATE ORDER → POST `/jobs`. **No ROLE / WRAPPER kinds yet.** |
| WRAP/STYLE/skills | `CREW/IN/WRAP/{WOMBAT,CODER,JUDGE}.md`, `STYLES/`, `skills/*` **propose-only** |
| Periodic wrapper/skill/package reviewer | **UNMEASURED** — no schtask found that reviews WRAP/STYLE/skills |

## Pipeline vs gap

**Have:** drop surfaces, six-field SOP, MOTIF DEFINE-first, model rater row, porosity tensor, farm seating by hand, CREATE for AGENT/TOOL/CONNECTOR/SKILL.

**Missing (this DEFINE):**
1. CREATE kinds **ROLE** and **WRAPPER** (and package-set) — or map ROLE→AGENT + WRAPPER→SKILL without new kinds if occupancy forbids more chips.
2. WOMB **auto-seat**: given DEFINE + target axis, pick pair from model_rater row ∩ GAC line (**Luna Flex $0.10/$0.60 and under**), maximize **`orthogonality`** (porosity fold; aliases `orth_sketch` / `signed`; else `(xor_err − cofail) × mean_err`) / minimize porosity mag on that axis (`GET /porosity`). **Mix paid-low vs :free** — not free-vs-free only. Not a second scheduler — one function WOMBAT calls, then six-field Agent field. NaN/inf/negative `budget_out` is `BAD_INPUT`.
3. Clock that reviews WRAP/STYLE/skills/package sets (native schtask, `--once` pattern like recall). Output = STYLE append / propose skill, not live-tree write.
4. Board ingest from **email** — UNMEASURED unless a daemon already files to `work_orders/drop/`.

Opus T stays `/5`. Pair pick **reads** T, does not rewrite it.

## FIFO — always

WOMB is **FIFO**. Drops are processed in arrival order (Timestamp / Gitur `createdAt`). Do not jump a later DEFINE (WOMB pick_pair, CREATE ROLE) ahead of an earlier pack (Opus AM #1–#8). Chat silos (Desktop pack, this TUI, GitHub PRs, unique HEAD) are **not** a second queue — they join this board in time order. CCr disposes LiT **oldest open PR first**.

## Not

OpenHands-as-OS. SOL/non-flex Luna retap. Iframe OpenWork. Second Core. WOMBAT does not hold the pen.
