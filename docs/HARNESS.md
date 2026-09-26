# HARNESS — one book (legend, DUDs, HERO, vias, Size, Gitur)

**Short rules (fail-closed):** `docs/CANON_SPAWN.md`  
**This file:** everything related to harnesses from G46 orch `716fbaea` (2026-09-17 → 2026-09-18 this TUI, plus the prior G46 days on the same sid) and the packs on disk. Not occupancy. Core spawn still **proposed**, not on `origin/main`.

WRAP: What is the intent, and the best execution of this intent?

**Intent:** Every spawned occupant sits in a **harness whose kind follows Role**. Only code-related roles get a **coding** via. COSMOS owns the pack (legend + mission). The **family** owns the loop. No extra `grok.exe`. No DUD → not a HERO → **no spawn**.

---

## 0. Provenance (read these, then this book)

| Source | What it holds |
|---|---|
| G46 orch TUI `716fbaea-a18f-41af-b9cb-e7ecbd164c66` 2026-09-17 | Unique-head kill; one-head; TidyUP packs; occupancy scars |
| Same sid 2026-09-18 (prior turns) | DUDs named; CCrew seats; Luna JUDGE pack; six CODER packs; WOMBAT GF38; Hermes **parked**; Size remainder → MAX/OPTIMUM |
| Same sid 2026-09-18 (this continuation) | Compaction cancelled; TidyUP checkpoint; Size 20% margin; `optimum="float"` never 0; dsh / Pi / OpenCode **installed**; HERO packs revised |
| CCr G46 `f47bad79` | Pen, `CCR.lease`, grok pid 77372. Disposes LiT. Not a Coder-N. |
| Compaction segments | `…\716fbaea-…\compaction\segment_000..002.md` |
| Session memory | `~/.grok/memory/cosmos-4adad16a/sessions/2026-09-17..19-interval-716fbaea.md` |

Keith 2026-09-18: **approved the Role×agent seats** in `work_orders/ccr/CCREW_SEATS.md`. Not called until named.

---

## 1. Vocabulary (do not conflate)

| Word | Meaning |
|---|---|
| **Harness** | The **runner** — the loop that calls the model with tools until a final message. Kind from Role. Via from Model family. |
| **Kind** | `orch` · `board` · `review` · `coding` · `dispose`. DAEMON is not an LLM. |
| **Via** | Which binary/API: `codex-cli`, `cli:dsh`, `cli:pi`, `cli:opencode`, `cursor-gitur`, `vertex-coding`, `mouth:openrouter` (degenerate). |
| **Legend pack** | Seven layers on the occupant: Role → Model → Harness → Wrapper → Skills → Tools → Enviro. Prefix-stable (P11). |
| **Mission pack** | This job (ITEM / diff / PR). Volatile tail. Fills Output **Where**; may name **What** and **OPTIMUM**. |
| **DUDs** | **Deployment bUnDle** = legend + mission. Slang for a **sharp outfit**, not a loser. Keith 2026-09-18. |
| **HERO** | **Agent + DUDs**. Spawn in HERO mode = apply the DUDs. No DUD = not a HERO = no spawn. |
| **Digs** | Nickname for Harness + Enviro (city + house). **Not** an apply-order slot. |
| **Degenerate harness** | Raw chat completion, tools empty (`mouth:*`). Allowed only if native via **unbound**. If bound, `warn3` then **refuse**. |
| **Wrapper** | `WRAP/{Role}.md` + `STYLES/{Model}.md` (append). Missing STYLE → `_TEMPLATE`. Tails, not PREFIX. |
| **Skills** | New training. Role defaults + Role[Model] overlays. Propose → CCr accept. Child’s set, not parent’s. Lazy, not PREFIX bloat. |
| **Gadgets** | Tools. **In** the legend (Role[Model] allow-list), not a side kit. ORC without write tools is a different legend than CODER with files. |

Google (2026-09-18): Legend = structure on the launchpad; Tail = vector; Legend + Tail = Deployment. **Adopted.** Do **not** keep: legend as an immutable container image; gadgets in an “Operational Kit” beside the dossier.

---

## 2. Creation rules (apply on **that** occupant, then spawn)

Anytime an agent **or subagent** is called/spawned/created:

1. Define and apply layers **in this order** (defaults fill holes; never skip).
2. Then BU / session preload / resume (**in Enviro**, before the model call).
3. Then write PREFIX + prompts.
4. Then compute **Size** (MAX hard, OPTIMUM aim).
5. Then spawn.

```
Role → Model → Harness → Wrapper → Skills → Tools → Enviro
                 \__________ digs nickname __________/
Legend (1–7)  +  Mission pack  =  DUDs
Agent + DUDs  =  HERO
```

### 2.1 Fail-closed

COSMOS does **not spawn** any agent or subagent unless all seven layers are applied on **that** occupant. Empty Role or empty Model after defaults = **refuse**.

No path around this: WO runner, Gitur launch, farm `_code_or_seat`, Cursor dispatch, TUI `spawn_subagent` / SSA, OpenWork child, `grok --single`, ORC sit.

- `grok.exe` / `grok --single` as WO worker or as a **subagent** = refuse.
- ORC in a coding via = refuse.
- Role=`DAEMON` + LLM = refuse.
- Context source must be a **list** of existing `[read*]` paths. Concat ` · ` strings → `NO_CONTEXT` (scar).
- Unique HEAD ≠ GitHub `main`. Gitur proposes on `main`; CCr disposes LiT.

**100%** = this canon **in Core spawn** (refuse if layers missing) + cDeck page editing Role[Model] defaults. WRAP/skills on disk as propose-only do **not** stop grok.exe today.

### 2.2 Subagent = new legend

All seven layers, same order, on the **child**. Not a subset. Parent Role does **not** leak (ORC launching a CODER yields a CODER). Parent may pass a **brief** (context list + task). Nested children obey the same rule. Headless does not exempt. Each spawn is a **new sid**.

### 2.3 First lines (mouth contract)

| Role | First line |
|---|---|
| CODER | `NONE` or `diff --git` |
| WOMBAT | `ITEM` or `NONE` |
| JUDGE | `KEEP` \| `DROP` \| `NONE` \| `HOLD` \| `UNMEASURED` |

FAIL → JSONL attempt N + `wo_partner` + follow-up. Never a corpse on WOMB (`bucket+picked` only). Empty Output = WOMBAT error (state / choose / prompt / follow-up), not as-is retry.

### 2.4 Kind by Role

| Role | Kind | May write | Tools (default) | Not |
|---|---|---|---|---|
| **ORC** | `orch` | mailbox, WOs, Gitur launch, BU | drop / Gitur / SSA / read | LiT, extra grok.exe, CCr pen |
| **WOMBAT** | `board` | `work_orders/drop` ITEMs, DEFINE | read rater/porosity/wishlist | LiT, Gitur BUILD |
| **JUDGE** | `review` | scores JSONL, KEEP/DROP/HOLD | read diff/pack, **read-only sandbox** | LiT, PR merge |
| **CODER** | `coding` | attempt-private clone → Gitur PR | files, tests, bound CLI | LiT dispose, extra grok.exe |
| **CCR** | `dispose` | LiT after review (one lease) | Gitur merge, fenced commit | sit ORC, extra grok.exe |
| **DAEMON** | not an LLM | native clock only | schtask / WD2 | any model spawn |

Kind-gate: `orch`/`board`/`review` cannot take coding-write; `review` sandbox read-only; `coding` cannot take CCr dispose; empty tools = none.

**ORC is the load-bearing yes.** Cowork was the right orch in a **coding** harness — it coded the live tree (Claude-solo). P9 broke because the **kind** was wrong. Intended orch via = **GFO** (OpenWork + GF38), WRAP/ORC, **no COSMOS folder grant**. Folder grant = pen. Not seated.

---

## 3. Size (Output target — part of the DUD)

Role defaults fill **What** only (`text` | `python` | `no_prose`). **Size is two knobs.**

**Order:** write preload (cache PREFIX) and prompts **first** → compute Size → **then** spawn.

```
margin = 0.20 × context_window          # thinking + errors
MAX    = context_window − cached_tokens − prompt_tokens − margin
```

| Knob | Rule |
|---|---|
| **MAX** | Reply `max_tokens`. **Cannot float. Cannot be 0.** Set API to MAX every spawn. `MAX ≤ 0` → refuse (preload ate the window). |
| **OPTIMUM** | Aim, not the API cap. If expected output known: expected + headroom (10k tokens of `.py` → **15000**), must be **> 0** and `≤ MAX`. If unknown: `optimum = "float"` — **never write 0**. |
| **cap_tokens** | Omit, or a **positive** count. `cap_tokens = 0` is spawn-refuse. |

**Shoot OPTIMUM when it is a positive count. Always obey MAX.**

`python` = code/diff/object, no wrapping essay. `text` = harness loop until a final assistant message. `no_prose` = machine record only.

**xAI / G46:** **2× surcharge above 200k input**. Cheaper to start a new session. Keep PREFIX+ITEM **under 200k** even if the vendor window is 2M. Do not stuff MAX up to the window on Grok. Luna/GLM/GF38/dsh/Pi/OpenCode are not this surcharge; they still compute MAX with the 20% margin.

Thinking/reasoning counts as output (GF38; the 20% margin is that cushion). PREFIX ≥ 4096 on GF38 is the **cache floor**, not the output cap.

**Scar:** baking `max_tokens = 2048|4096|8192` in the legend as if it were the window. Killed 2026-09-18.

TOML shape (every HERO pack):

```toml
[legend.output]
what = "python"          # or "text" / "no_prose"
size_mode = "max_minus_margin"
window_margin_frac = 0.20
optimum = "float"        # or a positive int, never 0
```

---

## 4. Family via (CODER kind) — installed 2026-09-18

| Family | Via | Binary (proved) | Isolated home | Key |
|---|---|---|---|---|
| Grok 4.6 | `cursor-gitur` | Cursor Cloud Agent | Gitur branch from `origin/main` | Cursor wallet. **No extra grok.exe.** Keep in < 200k. |
| OpenAI Luna / Sol | `codex-cli` | `codex exec` Flex | `live/work/codex/hero-*` | `openai_api_key.txt` |
| Gemini GF38 | `vertex-coding` | Kelly Vertex `global` apikey | worktree | `vertex_coding.json`. No `_fire_gf38` loop. |
| GLM | **`cli:pi`** | `pi 0.85.1` | `live/work/pi-home` | `ZAI_API_KEY` or OpenRouter fallback |
| DeepSeek | **`cli:dsh`** | `dsh 0.1.5-rc.2` | `live/work/dsh-home` | `DEEPSEEK_API_KEY` (missing) |
| Ling | **`cli:opencode`** | `opencode 1.18.31` | `live/work/opencode-home` | OpenRouter |
| Anthropic | Gitur vendor wallets only | — | — | Anthropic **OFF** the route |

Degenerate `mouth:openrouter` only if that family’s native via is unbound.

**Not installed:** ZCode desktop ADE (GLM’s *official* harness by homepage title — Electron, extra occupancy). Hermes (`DEFINE_HERMES_POOLS.md` WISHLIST). Claude Code. `dsh web`. OpenHands-as-OS.

### 4.1 Spawn commands (do not cwd LiT)

**JUDGE Luna (Flex, read-only)** — `work_orders/ccr/CALL_LUNA_587.cmd` (not fired until named):

```bat
cd /d V:\A\Ai\COSMOS\live\work\codex\hero-luna-587
codex.cmd exec --ignore-user-config --skip-git-repo-check --sandbox read-only --json --color never -m gpt-5.6-luna -c service_tier="flex" --output-last-message V:\A\Ai\COSMOS\work_orders\ccr\JUDGE_LUNA_PR587_last.txt "Read AGENTS.md and TASK.md. Grade docs/CANON_PEN.md. First line KEEP or DROP or HOLD."
```

Coder Codex write jobs: populated worktree + `--approve-for-me` only. **`--full-auto` is invalid with `--sandbox`.** `--approve-for-me` cannot combine with `--sandbox`. Empty attempt cwd was a scar.

**CODER-1 GLM / Pi:**

```bat
set PI_CODING_AGENT_DIR=V:\A\Ai\COSMOS\live\work\pi-home
REM preferred:
pi -p --provider zai --model glm-5.3-flash --exclude-tools ask_question -- "ITEM"
REM fallback (proved 2026-09-18):
pi -p --provider openrouter --model z-ai/glm-5.3-flash --exclude-tools ask_question -- "ITEM"
```

Proved: `pi --list-models glm-5.3-flash` → `openrouter/z-ai/glm-5.3-flash` context **1.0M** / max-out **131.1K**.

**CODER-3 DeepSeek / dsh:**

```bat
set DSH_HOME=V:\A\Ai\COSMOS\live\work\dsh-home
dsh --profile headless "ITEM"
```

Proved: `dsh -V` → `0.1.5-rc.2`; `dsh --profile headless --help` exit 0. Live job needs `DEEPSEEK_API_KEY`.

**CODER-5 Ling / OpenCode:**

```bat
set OPENCODE_CONFIG=V:\A\Ai\COSMOS\live\work\opencode-home\opencode.json
set OPENCODE_CONFIG_DIR=V:\A\Ai\COSMOS\live\work\opencode-home
set OPENCODE_DATA_DIR=V:\A\Ai\COSMOS\live\work\opencode-home\data
opencode run --dir WORKTREE -m openrouter/inclusionai/ling-3.0-flash -- "ITEM"
```

Proved catalog: `openrouter/inclusionai/ling-3.0-flash` (and VL/fin/sante variants). Window **262144**.

**CODER-6 Grok:** Cursor Gitur BUILD, `autoCreatePR`, must commit. Composer 2.5 = **CHECK**, not BUILD. CCr TUI ≠ this BUILD spawn.

Launchers on disk, **not fired:** `CALL_LUNA_587.cmd`, `CALL_GLM_587.py`, `CALL_PI_GLM.cmd`, `CALL_OPENCODE_LING.cmd`.

---

## 5. Wrapper (layer 4)

Canon: `WRAP/{Role}` + `STYLES/{Model}` (append). PREFIX is **not** rewritten. STYLE/WRAP/params are tails.

**Hole on LiT:** `cosmos/WRAP/` has CODER and CCR; **JUDGE is missing**. Pack fill: `work_orders/ccr/hero_luna/L4_WRAPPER.md` until Gitur lands `cosmos/WRAP/JUDGE`.

Shared CODER wrap (`work_orders/ccr/hero_coders/_CODER_WRAP.md`):

```
role = CODER
pen = none
propose_only = true
merge = false
first_line = NONE | diff --git
wrap = What is the intent, and the best execution of this intent?
isolated_worktree = true
kind = coding
```

JUDGE wrap fill:

```
role = JUDGE
pen = none
propose_only = true
merge = false
first_line = KEEP | DROP | NONE | HOLD | UNMEASURED
wrap = What is the intent, and the best execution of this intent?
review = findings first, severity, file:line; summary after; NONE if empty
no_plan_as_product = true
```

Do **not** reimplement `while True` + `chat.completions.create` tool loops. The **via** is the runner (`codex exec`, `dsh`, `pi -p`, `opencode run`). Codex injects `AGENTS.md` as user messages — that file must not contain dates, PR numbers, or commit hashes (Mission pack).

Prompt shape (every call): stable PREFIX (byte-identical, no dates/UUIDs) + volatile ITEM tail + return shape in the tail. Measure `cached_tokens`. Naked first query is out of SOP.

ITEM tail template:

```
Repo: keithbbf-gif/{cosmos|cdeck}  Branch: ccr/<slug>
Reuse: <existing files>
Do: <one behavior>
Bite: <typed refuse + all_bite>
Must not: ballot, GET /forge, leftover PRs, skins buildout, Cowork-home rewrite
Keep stub: data-stub=profile-skin
Return: unified diff first
```

If the agent empty-branches or ramble-answers, **the ITEM failed**. Shorten. Fix the prompt; do not add a second review panel.

---

## 6. Skills (layer 5)

Skills = **new training**, not PREFIX. Propose → CCr accept. Child’s set, not inherited.

Vendor analogs (steal shape, not a second OS):

| Family | Skill shape | COSMOS |
|---|---|---|
| DeepSeek dsh | `skill` tool; catalog `$DSH_HOME`, `~/.agents`, project roots; lazy load by name | Skills layer; do not dump 70 tools into a Judge |
| GLM / ZCode | `SKILL.md` at `~/.zcode/skills/<name>/` or workspace `.zcode/skills/`; invoke `$`; frontmatter `name`+`description` ≤1024; plugins bundle skills+commands+MCP+hooks | Same `SKILL.md` shape when CCr accepts |
| GLM official pack | [zai-org/GLM-skills](https://github.com/zai-org/GLM-skills) via Clawhub | Not installed (multimodal OCR not Coder-1) |
| Ling | cookbook `ling-gui-agent-skill` only | None extra |
| Z.AI best practice | long-lived rules in project files; this job in the prompt; repeated workflows as Skills; **one session per task** | PREFIX vs Mission; new sid per spawn |

Do not bind COSMOS WD2 / 15s clock to dsh Schedule or Hermes cron.

---

## 7. CCrew seats (Keith approved 2026-09-18)

| Seat | Role | Model | Via | Pack | Seated? |
|---|---|---|---|---|---|
| Luna | JUDGE | `gpt-5.6-luna` Flex | `codex-cli` | `hero_luna/` | Pack ready. `CALL_LUNA_587.cmd` **not run**. #587 still OPEN. |
| Coder-1 | CODER | `glm-5.3-flash` | `cli:pi` | `hero_coders/1_glm/` | Bound. Need `ZAI_API_KEY` for native; OR fallback proved. |
| Coder-2 | CODER | `gemini-3.8-flash` | `vertex-coding` | `hero_coders/2_gf38/` | Pack. Kelly ~$57/300. No `_fire_gf38`. |
| Coder-3 | CODER | `deepseek-v4-flash` | `cli:dsh` | `hero_coders/3_ds/` | Bound. Need `DEEPSEEK_API_KEY`. |
| Coder-4 | CODER | `gpt-5.4-mini` | `codex-cli` | `hero_coders/4_54mini/` | Pack. Not Judge Luna. Window 272k. |
| Coder-5 | CODER | `inclusionai/ling-3.0-flash` | `cli:opencode` | `hero_coders/5_ling/` | Bound. OR key present. |
| Coder-6 | CODER | `grok-4.6` | `cursor-gitur` | `hero_coders/6_grok_gitur/` | Pack. `keep_in_tokens_under=200000`. |
| WOMBAT-1 | WOMBAT | `gemini-3.8-flash` | `vertex-coding` fat PREFIX | `hero_wombat_gf38/` | **After** JUDGE + Coders 1–6. Same model as Coder-2, **different Role/sid/kind=`board`**. |

CCr G46 = **pen**, not Coder-N. Composer 2.5 = Cursor **CHECK**. Partners on Mission #587 (optional): `hero_glm/`, `hero_gf38/` mouths.

Jobs stay until judged. Gitur PR stays OPEN until Luna KEEP, then CCr merges. Do not occupancy-apply to main. Scar: #580–#586 merged without Judge; #588 mixed SOL KEEP diffs with P12/P13 onto `3d7c0483`.

---

## 8. Full DUD examples (on disk)

### 8.1 JUDGE Luna — `work_orders/ccr/hero_luna/DUD.toml`

```toml
[legend]
role = "JUDGE"
model = "gpt-5.6-luna"
harness_kind = "review"
harness_via = "codex-cli"
service_tier = "flex"
wrapper = "work_orders/ccr/hero_luna/L4_WRAPPER.md"
style = "STYLES/_TEMPLATE"
skills = []

[legend.tools]
allow = ["rg", "read_file", "list_dir", "glob_file_search"]
forbid = ["apply_patch", "git_push", "git_merge", "git_reset_hard", "grok.exe"]
sandbox = "read-only"

[legend.enviro]
cwd = "V:\\A\\Ai\\COSMOS\\live\\work\\codex\\hero-luna-587"
pack = "house"
wallet = "oa-api"
ignore_user_config = true
budget_out_usd_per_m = 0.60
context_window_tokens = 1100000

[legend.output]
what = "text"
size_mode = "max_minus_margin"
window_margin_frac = 0.20
optimum = "float"

[mission]
id = "gitur-pr-587"
item = "docs/CANON_PEN.md"
author = "orch-716fbaea"

[mission.output]
where = [
  "work_orders/ccr/JUDGE_LUNA_PR587.json",
  "work_orders/ccr/JUDGE_LUNA_PR587_last.txt",
  "live/state/attempts/attempts.jsonl",
]
what = "text"
size_mode = "max_minus_margin"
window_margin_frac = 0.20
optimum = "float"
```

### 8.2 CODER-1 GLM / Pi — `hero_coders/1_glm/DUD.toml`

```toml
[legend]
role = "CODER"
model = "glm-5.3-flash"
harness_kind = "coding"
harness_via = "cli:pi"
pi_provider = "zai"
pi_fallback_provider = "openrouter"
pi_fallback_model = "z-ai/glm-5.3-flash"
pi_home = "V:\\A\\Ai\\COSMOS\\live\\work\\pi-home"
wrapper = "work_orders/ccr/hero_coders/_CODER_WRAP.md"
skills = []

[legend.tools]
allow = ["read", "bash", "powershell", "edit", "write", "grep", "find", "ls"]
forbid = ["git_push", "git_merge", "grok.exe"]
sandbox = "worktree"

[legend.enviro]
pack = "house"
wallet = "zai"
budget_out_usd_per_m = 0.25
context_window_tokens = 1000000

[legend.output]
what = "python"
size_mode = "max_minus_margin"
window_margin_frac = 0.20
optimum = "float"

[mission]
id = "unseated"
item = "filled per Gitur WO"
spawn = "pi -p --provider zai --model glm-5.3-flash --exclude-tools ask_question"
```

`live/work/pi-home/auth.json` (no secrets — env interpolation):

```json
{
  "openrouter": { "type": "api_key", "key": "$OPENROUTER_API_KEY" },
  "zai": { "type": "api_key", "key": "$ZAI_API_KEY" }
}
```

### 8.3 CODER-3 DeepSeek / dsh — `hero_coders/3_ds/DUD.toml`

```toml
[legend]
role = "CODER"
model = "deepseek-v4-flash"
harness_kind = "coding"
harness_via = "cli:dsh"
dsh_profile = "headless"
dsh_home = "V:\\A\\Ai\\COSMOS\\live\\work\\dsh-home"
wrapper = "work_orders/ccr/hero_coders/_CODER_WRAP.md"

[legend.enviro]
wallet = "deepseek-official"
pack = "house"
budget_out_usd_per_m = 0.16
context_window_tokens = 1000000
```

### 8.4 CODER-5 Ling / OpenCode — `hero_coders/5_ling/DUD.toml`

```toml
[legend]
role = "CODER"
model = "inclusionai/ling-3.0-flash"
harness_kind = "coding"
harness_via = "cli:opencode"
opencode_model = "openrouter/inclusionai/ling-3.0-flash"
opencode_home = "V:\\A\\Ai\\COSMOS\\live\\work\\opencode-home"

[legend.enviro]
wallet = "openrouter"
pack = "house"
budget_out_usd_per_m = 0.063
context_window_tokens = 262144
```

`live/work/opencode-home/opencode.json`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "openrouter/inclusionai/ling-3.0-flash",
  "enabled_providers": ["openrouter"],
  "provider": {
    "openrouter": {
      "models": {
        "inclusionai/ling-3.0-flash": {},
        "z-ai/glm-5.3-flash": {}
      }
    }
  }
}
```

### 8.5 CODER-6 Grok Gitur — `hero_coders/6_grok_gitur/DUD.toml`

```toml
[legend]
role = "CODER"
model = "grok-4.6"
harness_kind = "coding"
harness_via = "cursor-gitur"

[legend.tools]
allow = ["cursor_cloud_agent"]
forbid = ["grok.exe", "grok --single", "composer_build"]
sandbox = "cursor-cloud"

[legend.enviro]
wallet = "cursor"
pack = "house"
context_window_tokens = 2000000
xai_surcharge_after = 200000
keep_in_tokens_under = 200000

[mission.output]
where = ["GitHub PR (open until Luna KEEP)"]
what = "python"
```

### 8.6 WOMBAT GF38 — `hero_wombat_gf38/DUD.toml`

```toml
[legend]
role = "WOMBAT"
model = "gemini-3.8-flash"
harness_kind = "board"
harness_via = "vertex-coding"
wrapper = "work_orders/ccr/hero_wombat_gf38/L4_WRAPPER.md"

[legend.tools]
allow = []
forbid = ["apply_patch", "git_push", "grok.exe", "_fire_gf38", "thinkingLevel.HIGH"]

[legend.enviro]
wallet = "kelly-vertex-coding"
location = "global"
auth = "apikey"
pack = "fat"
context_window_tokens = 1048576
budget_out_usd_per_m = 3.75

[mission.output]
where = ["work_orders/drop/", "live/state/attempts/attempts.jsonl"]
what = "text"
```

Coder-2 GF38 and Coder-4 mini DUDs live beside these (`vertex-coding` house pack; `codex-cli` 272k window, `apply_patch` allowed).

---

## 9. Vendor harness map (what they ship vs what we run)

DeepSeek’s sentence **Agent = Model + Harness** is our DUD + occupant.

| Vendor | They ship | COSMOS spawn | Notes |
|---|---|---|---|
| **DeepSeek** | [deepseek.com/harness](https://www.deepseek.com/harness/en/) `dsh`. Cordis. Everything is a plugin. Modes: Standard / Code (PTC) / Minimal / Creator. Profiles: `headless`, `web`, `sdk`, `acp`. | `dsh --profile headless` | Not `dsh web`. SDK example `max_tokens=49152` is **their** cap — we still compute MAX. Developer preview, no audit. One writer on `DSH_HOME`. |
| **GLM / Z.AI** | **ZCode** ADE (“Official Harness for GLM-5.3”), AutoClaw (office), Pi CLI, GLM-skills, retarget Claude Code/OpenCode | **`pi -p`** | ZCode `.exe` not installed. Pi is the documented **terminal** harness. `ZAI_API_KEY` or OR. |
| **Ling** | No first-party CLI. Integrations: Claude Code, Hermes, OpenCode, OpenClaw. SWE-Bench they published: OpenHands. | **`opencode run`** | Claude Code not installed (Anthropic off). Hermes WISHLIST. |
| **OpenAI** | Codex CLI | `codex exec` | Luna JUDGE Flex read-only; Coder-4 write + `--approve-for-me`. |
| **Google** | Vertex / Gemini CLI | `vertex-coding` Kelly `global` apikey | WOMBAT fat PREFIX ≥4k cache floor. |
| **xAI / Grok** | this TUI + Cursor | Cursor Gitur BUILD | 200k/2×. No extra grok.exe. |
| **Nous Hermes** | AIAgent, credential pools, ACP | **WISHLIST** | Analog parked in `DEFINE_HERMES_POOLS.md`. No install. `fill_first`. `ignore: ["deepinfra"]`. Do not bind WD2 to Hermes cron. `HERMES_HOME` one writer. |

Hermes prompt assembly **stable → context → volatile** = P11 legend PREFIX vs Mission tail. API modes: GLM/OR `chat_completions`; Luna/Codex **`codex_responses`**; `anthropic_messages` **OFF**. Daytona is a Hermes terminal backend — COSMOS Daytona is HOLD. Compaction archives `active=0` (like `_delme`).

---

## 10. Proposed PRs / Gitur WOs (P10 — not on main unless CCr merged)

These are **propose** packs. One job, one PR, from `origin/main`. Not unique-head. Composer CHECK. Luna KEEP then CCr merge. Do not occupancy-apply.

| Pack | Branch (from main) | Repo | Title / job |
|---|---|---|---|
| `GITUR_CANON_SPAWN.md` | `ccr/canon-spawn-layers` | cosmos | `WO: CANON spawn layers Role Wrapper Skills Tools Params` — `cosmos_spawn.py` `SpawnSpec`, `defaults`, `apply`, refuse grok.exe, `NO_CONTEXT` on ` · ` concat, `--selftest` |
| `GITUR_HARNESS_SEAT.md` | `ccr/harness-seat` | cosmos | `WO: every agent is a harness; kind by role; ORC=orch not coding` — add `harness_kind`/`harness_via` to SpawnSpec; kind-gate; degenerate mouth only if unbound; ORC default via GFO; CODER+Luna → `codex-cli` |
| `GITUR_CDECK_SPAWN_PAGE.md` | `ccr/spawn-form-page` | **cdeck** | `WO: cDeck SPAWN form Role×Model layers` — extra pane `deck_spawn.js`; seven fields in apply order; GET `/api/v1/spawn/defaults`; never iframe |
| `GITUR_MAKERS_ROLE_WRAPPER.md` | `ccr/makers-role-wrapper` | cosmos | `WO: makers ROLE+WRAPPER kinds` — `MAKER_KINDS += ROLE, WRAPPER`; GET `/makers?kind=ROLE` never mkdir |
| `GITUR_CANON_PEN.md` | `ccr/canon-pen` | cosmos | **PR #587 OPEN** — `docs/CANON_PEN.md` (+46). GF38 Kelly KEEP `cached=0`. Luna not seated. **Do not merge unjudged.** |
| `GITUR_CANON_SPAWN.md` (docs) | (canon file untracked/local) | — | `docs/CANON_SPAWN.md` is the short rules; this book is the rest |

Older `GITUR_CANON_SPAWN.md` SpawnSpec listed `role, model, wrapper_paths[], skill_names[], tools[], params{}` **without** harness fields. **`GITUR_HARNESS_SEAT.md` supersedes** that hole (kind+via). Implementers must ship **both**: layers exist, **and** Harness is layer 3.

`--selftest` expected (from GITUR_HARNESS_SEAT):

- ORC → kind `orch` not `coding`
- JUDGE → `review` read-only
- CODER+Luna → `codex-cli`
- CODER+`mouth:*` while native via bound → refuse

cDeck occupancy: fold pins; extra pane in `deck_*.js` not `app.js`; no new pin if an existing CREATE check can extend.

---

## 11. Core spawn shape (proposed — not on `origin/main`)

From the Gitur packs, the intended Python surface:

```python
# cosmos/cosmos_spawn.py  (PROPOSE — CCr disposes)
@dataclass
class SpawnSpec:
    role: str                    # ORC|WOMBAT|CODER|JUDGE|CCR|DAEMON
    model: str | None            # empty after defaults = refuse (except DAEMON)
    harness_kind: str            # orch|board|review|coding|dispose
    harness_via: str             # codex-cli|cli:dsh|cli:pi|cli:opencode|cursor-gitur|vertex-coding|mouth:*
    wrapper_paths: list[str]     # WRAP/{Role} + STYLES/{Model} or _TEMPLATE
    skill_names: list[str]       # child's set
    tools: list[str]             # then kind-gate
    params: dict                 # env, pack, budget, cache_ttl, output Where/What/Size

def defaults(role: str, model: str) -> SpawnSpec: ...
def apply(spec: SpawnSpec) -> SpawnSpec:
    """Fill missing layers. Never silent skip. Kind-gate tools."""
    ...
def preflight_session(paths) -> dict:
    """If SEED/BU says resume → {need_resume: true}. GET never mkdir."""
    ...
```

Kind fills from Role. Via fills from Model family (table in §4). Degenerate `mouth:*` only if native via unbound.

Size at spawn (after PREFIX exists):

```python
MARGIN = 0.20
max_tokens = window - cached - prompts - int(MARGIN * window)
if max_tokens <= 0:
    raise Refuse("MAX<=0")
if optimum == "float":
    api_max = max_tokens          # obey MAX; do not invent a 4k aim
else:
    if optimum <= 0:
        raise Refuse("OPTIMUM zero illegal")
    api_max = max_tokens          # still MAX on the wire
    # wrapper steers toward min(optimum, max_tokens)
```

---

## 12. What is not done

- Core `cosmos_spawn.py` **not** on `origin/main` (`3d7c0483` / #588).
- cDeck SPAWN form **not** shipped.
- `cosmos/WRAP/JUDGE` **missing** on LiT (pack fill only).
- Luna JUDGE **not seated** on #587.
- WOMBAT **not seated** (after 1–6).
- Hermes **not installed**.
- ZCode desktop **not installed**.
- `DEEPSEEK_API_KEY` / `ZAI_API_KEY` **not** in `live/config` (OR fallback works for Pi/OpenCode).
- Jobs **not called** until Keith names them.
- PAUSE.flag may still be **hold** from the TidyUP checkpoint — say if WD2 should move.

---

## 13. Pointers (do not fork a second book)

| File | Role |
|---|---|
| `docs/CANON_SPAWN.md` | Short fail-closed rules |
| `docs/HARNESS.md` | This book |
| `docs/AGENT_PROMPTING.md` | CCr style book / ITEM tail / cache |
| `docs/PROMPT_CACHE.md` | P11 |
| `docs/ORCH_SEAT.md` | GFO orch harness |
| `docs/CANON_PEN.md` | One writer; PR #587 |
| `work_orders/ccr/DEFINE_HARNESS_SEAT.md` | Kind by role |
| `work_orders/ccr/DEFINE_LEGEND.md` | 007 → layers |
| `work_orders/ccr/DEFINE_VENDOR_HARNESS.md` | dsh / ZCode / Pi / OpenCode / Ling |
| `work_orders/ccr/DEFINE_HERMES_POOLS.md` | Parked pools; no install |
| `work_orders/ccr/CCREW_SEATS.md` | Approved seats |
| `work_orders/ccr/hero_*/` | HERO packs |
| `work_orders/ccr/GITUR_*.md` | Proposed PRs |

**Not:** Ori as one legend for every family. Extra `grok.exe`. ORC legend with a COSMOS folder grant. Brief in PREFIX. USPTO. Fire Gitur while unjudged PRs skip Judge. `_fire_gf38` tab farm. Unique-head `8b5ad84e`.
