# CANON — spawn layers (smallest rules)

Book (examples, DUDs, vias, Gitur WOs): `docs/HARNESS.md`.

Keith: anytime an agent **or subagent** is called/spawned/created, these layers are **defined and applied first** (defaults if unset), **in this order**, on **that** occupant. Then check BU / session preload / resume.

The seven layers **Role → Model → Harness → Wrapper → Skills → Tools → Enviro** are the occupant's **legend pack**. The **Mission pack** is this job (task / diff / ITEM; was brief/tail). It fills **Output Where** and may name **What** and an **OPTIMUM** Size (never above **MAX**). **Legend pack + Mission pack = DUDs** (Deployment bUnDle — slang for a **sharp outfit**, not a loser). **Agent + DUDs = HERO.** Spawn in HERO mode = apply the DUDs. No DUD = not a HERO = no spawn. P11: legend is prefix-stable; brief is volatile. Gadgets stay in the legend. **Digs** = Harness + Enviro (nickname only — not a layer; apply order unchanged). Each spawn is a new sid; not a shared immutable image. A child HERO gets a new DUD (full legend + own brief).

cDeck page shows the same form. COSMOS code enforces it. CCr preloads defaults per Role×Model. A child is a **new legend**, not a thinner spawn.

## Rules (all of them)

1. No spawn without a **Role**: `ORC` | `WOMBAT` | `CODER` | `JUDGE` | `CCR` | `DAEMON` (daemon is not an LLM).
2. No LLM spawn with Role=`DAEMON`.
3. No extra `grok.exe`. Coding = Gitur/GAC. MOTIF drive = WD2. Judge = one fat prefix per run. ORC is not a coding harness.
4. **Apply on spawn, in this order** (each layer may fill from the ones above; never skip):
   1. **Role** — `ORC` | `WOMBAT` | `CODER` | `JUDGE` | `CCR` | `DAEMON`. Empty after defaults = refuse.
   2. **Model** — GAC / Luna Flex and under unless Keith names quality. Empty after defaults = refuse. DAEMON has no model.
   3. **Harness** — kind from Role, via from Model family.
      - kind: `ORC→orch` · `WOMBAT→board` · `JUDGE→review` · `CODER→coding` · `CCR→dispose`
      - via (coding only): Grok→Gitur Cursor BUILD · OpenAI→`codex exec` · GF38→Kelly/Gemini CLI when bound · GLM→`pi -p` · DeepSeek→`dsh --profile headless` · Ling→`opencode run` · Anthropic→Gitur vendor wallets
      - via (orch): OpenWork/GFO, no COSMOS folder grant
      - degenerate `mouth:*` only if native via unbound; warn3 then refuse if bound
   4. **Wrapper** — `WRAP/{Role}.md` + `STYLES/{Model}.md` (append). Missing STYLE → `_TEMPLATE.md`.
   5. **Skills** — **new training.** Role defaults + Role[Model] overlays (propose→CCr accept). Child's set, not inherited from the parent.
   6. **Tools** — Role[Model] allow-list, then **kind-gate** (orch/board/review cannot take coding-write; review sandbox read-only; empty = none).
   7. **Enviro** — env, ctx (**list**, no ` · ` concat), pack fat|house, budget_out ≤ $1/M unless named, cache_ttl. **Output target** (canon, part of the DUD): **Where** (path list — boxes, not LiT), **What** (`text` | `python` | `no_prose`), **Size**. Role defaults fill **What** only. **Size is two knobs: MAX (hard) and OPTIMUM (aim).** Order: write preload (cache PREFIX) and prompts **first**; **then** compute Size; **then** spawn. **MAX** (reply `max_tokens`, never floats): `MAX = context_window − (cached_tokens + prompt_tokens) − 0.20×context_window`. The 20% is margin for thinking tokens and errors. `MAX ≤ 0` → refuse (preload ate the window; xAI: cheaper new-session). **OPTIMUM** (aim, not the API cap): if expected output is known, shoot for it with headroom (expect ~10k tokens of `.py` → 15k), clamped to `≤ MAX`. If OPTIMUM is unknown, **it floats** — do not invent a 2k/4k/8k target. **Shoot OPTIMUM when known; always obey MAX.** `text` = harness loop until a final assistant message (required first line for JUDGE). `python` = code/diff/object only, no wrapping essay. `no_prose` = machine record only. The **Harness** is the runner (Codex `exec`, not a hand-rolled `gpt-4o` tool loop). If BU/SEED says resume, `session start` / inject **here**, before the call.
5. **Fail-closed:** COSMOS does **not spawn** any agent **or subagent** unless layers **Role → Model → Harness → Wrapper → Skills → Tools → Enviro** are **applied** on **that** occupant (defaults fill holes; empty Role or empty Model after defaults = **refuse**, no call). No path around this: WO runner, Gitur launch, farm `_code_or_seat`, Cursor dispatch, TUI `spawn_subagent` / SSA, OpenWork child, `grok --single`, ORC sit. `grok.exe` / `grok --single` as WO worker or as a **subagent** = refuse. ORC in a coding via = refuse.
6. **Subagent = new legend.** All seven layers, same order, on the **child**. Not a subset. Parent Role does **not** leak (ORC launching a CODER yields a CODER, not a second ORC). Parent may pass a **brief** (Context source as a list + task). The child still gets its own harness, wrapper, skills, tools, enviro. Nested children obey the same rule. Headless does not exempt. Digs (house+city) are only Enviro+Harness — not the whole legend.
7. **BU / session:** if `BUCm.toml` or `state/SEED.json` says preload/resume, run `session start` / inject **in Enviro**, before the model call.
8. Context source is a **list** of existing `[read*]` paths. Concat ` · ` strings are invalid (NO_CONTEXT scar).
9. Coder reply is python only. First line is a python statement or a module docstring. No fence. No `diff --git`. WOMBAT first line `ITEM` or `NONE`. Judge first line `KEEP|DROP|NONE|HOLD|UNMEASURED`.
10. FAIL → JSONL attempt N + `wo_partner` + follow-up. Never a corpse on WOMB (`bucket+picked` only).
11. Empty Output = WOMBAT error (state / choose / prompt / follow-up). Not as-is retry. (1) prove full or (2) restate + two agents + new prompt.
12. One Judge per run. If cache dead and `n_board` < 20, **do not sit**. Sit at 20–40 WOs.
13. FIFO. Unique HEAD ≠ GitHub `main`. Gitur proposes on `main`; CCr disposes LiT.
14. Do not retap SOL / non-flex Luna. Mix paid-low vs `:free`.
15. PREFIX is not rewritten. STYLE/WRAP/params are tails.
16. **Size after preload. MAX cannot float. OPTIMUM can — but neither may be zero.** Do not bake `max_tokens=2048|4096|8192` as MAX. After PREFIX + prompts exist, before the call: `MAX = window − (cache + prompts) − 0.20×window`. Set API `max_tokens` to **MAX** every spawn. `MAX ≤ 0` → refuse. If expected return is known, **OPTIMUM** = that plus headroom (10k py → 15k), must be **> 0** and `≤ MAX`. If unknown, `optimum = "float"` — **never `0`**. A written `cap_tokens` / `optimum_tokens` of **0 is illegal** (refuse spawn). Shoot OPTIMUM when it is a positive count; always obey MAX.
17. **xAI 200k / 2×.** Grok (this TUI, Coder-6 Cursor BUILD, any `grok-4.6` mouth) **2× surcharge above 200k tokens**. Cheaper to **start a new session** than pay 2×. Coding should not need a huge load for excellent G46 results — keep PREFIX+ITEM judiciously under 200k; do not stuff the window because MAX remainder would allow it. Luna/GLM/GF38 are not this surcharge; they still compute MAX with the 20% margin.
18. **Answer every question directly and concisely.** One question, one answer. No preamble. CODER still obeys python-only.

## Not 100% yet

WRAP/skills on disk as propose-only do **not** stop grok.exe. **100%** = this canon **in Core spawn** (refuse if layers missing) + cDeck page editing Role[Model] defaults (seven fields, Harness included). Gitur: `GITUR_HARNESS_SEAT.md` / `GITUR_CDECK_SPAWN_PAGE.md`. If Judge disagrees with a rule above, **ask Keith** — do not silently pick.
