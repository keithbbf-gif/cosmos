# CANON — spawn layers (smallest rules)

Keith: anytime an agent or subagent is called/spawned/created, these layers are **defined and applied first** (defaults if unset). Then check BU / session preload / resume.

cDeck page shows the same form. COSMOS code enforces it. CCr preloads defaults per Role×Model.

## Rules (all of them)

1. No spawn without a **Role**: `WOMBAT` | `CODER` | `JUDGE` | `DAEMON` (daemon is not an LLM).
2. No LLM spawn with Role=`DAEMON`.
3. No extra `grok.exe`. Coding = Gitur/GAC. MOTIF drive = WD2. Judge = one fat prefix per run.
4. **Form on spawn (in this order):**
   1. Role
   2. Model (GAC / Luna Flex and under unless Keith names quality)
   3. Wrapper = `WRAP/{Role}.md` + `STYLES/{Model}.md` (append; missing STYLE → `_TEMPLATE.md`)
   4. Skills = Role defaults + Role[Model] overlays (propose→CCr accept)
   5. Tools = Role[Model] allow-list (empty = none)
   6. Parameters = env, ctx, pack fat|house, budget_out ≤ $1/M unless named, cache_ttl
5. **Fail-closed:** COSMOS does **not spawn** any agent/subagent unless layers **Role → Model → Wrapper → Skills → Tools → Enviro** are **applied** (defaults fill holes; empty Role or empty Model after defaults = **refuse**, no call). No path around this (WO runner, Gitur launch, farm `_code_or_seat`, Cursor dispatch, subagent). `grok.exe` / `grok --single` as WO worker = refuse.
6. **BU / session:** if `BUCm.toml` or `state/SEED.json` says preload/resume, run `session start` / inject **before** the model call.
7. Context source is a **list** of existing `[read*]` paths. Concat ` · ` strings are invalid (NO_CONTEXT scar).
8. Coder first line `NONE` or `diff --git`. WOMBAT first line `ITEM` or `NONE`. Judge first line `KEEP|DROP|NONE|HOLD|UNMEASURED`.
9. FAIL → JSONL attempt N + `wo_partner` + follow-up. Never a corpse on WOMB (`bucket+picked` only).
10. Empty Output = WOMBAT error (state / choose / prompt / follow-up). Not as-is retry. (1) prove full or (2) restate + two agents + new prompt.
11. One Judge per run. If cache dead and `n_board` < 20, **do not sit**. Sit at 20–40 WOs.
12. FIFO. Unique HEAD ≠ GitHub `main`. Gitur proposes on `main`; CCr disposes LiT.
13. Do not retap SOL / non-flex Luna. Mix paid-low vs `:free`.
14. PREFIX is not rewritten. STYLE/WRAP/params are tails.

## Not 100% yet

WRAP/skills on disk as propose-only do **not** stop grok.exe. **100%** = this canon **in Core spawn** (refuse if layers missing) + cDeck page editing Role[Model] defaults. That is the Gitur WO. If Judge (GLM Flash / this chair) disagrees with a rule above, **ask Keith** — do not silently pick.
