# Luna as JUDGE — eight-layer DUD (researched entries)

**Legend pack (1–7) + Mission pack (8) = DUD. Agent + DUD = HERO.**  
Spawn Luna in HERO mode as JUDGE. **Do not call until Keith says.**

Finished layer files: `work_orders/ccr/hero_luna/L1_ROLE.md` … `L8_MISSION.md`. Worktree legend: `live/work/codex/hero-luna-587/AGENTS.md`. Mission: `TASK.md`. Call (not run): `CALL_LUNA_587.cmd`.

CCr is G46 with the **pen** (dispose only). Composer 2.5 = Cursor **CHECK**, not Grok review, not this Judge. SOL is off.

Fail-closed: empty Role or empty Model after defaults = **no spawn**. Kind-gate: review ≠ coding-write. Subagent would get a **new** DUD, not this one.

---

## 1. Role — `JUDGE`

**Canon.** Spawn Role is `ORC | WOMBAT | CODER | JUDGE | CCR | DAEMON`. Kind from Role: **JUDGE → `review`**. First line of mouth: `KEEP | DROP | NONE | HOLD | UNMEASURED` (`docs/CANON_SPAWN.md` r1, r4.1, r9). One Judge per run (r12). Judge does **not** hold `CCR.lease`. Judge does **not** merge Gitur. P10: agents propose; CCr disposes.

**This occupant.** Role = **JUDGE**. Sid is **this spawn**, not CCr `f47bad79`, not orch `716fbaea`. Parent Role (ORC) **does not leak**. She grades; she does not write LiT; she does not sit WOMBAT (no `ITEM` first line); she does not emit `diff --git` as the product (that is CODER).

**Hole.** `cosmos/WRAP/JUDGE` does not exist (only `WRAP/CODER`, `WRAP/CCR`). Until Gitur adds it, Wrapper (layer 4) fills from CANON_SPAWN r9 + Codex **review** snippet, not from a missing file.

**Refuse.** Spawn with Role empty, Role=`CCR`, or Role=`CODER` on this call.

---

## 2. Model — `gpt-5.6-luna`

**Canon.** Model is GAC / Luna Flex and under unless Keith names quality (`CANON_SPAWN` r4.2). `docs/MODEL_ACCESS.md`: GPT-5.6 Luna id **`gpt-5.6-luna`**, path **oa-api and Codex CLI**. Not `gpt-5.3-codex` (Codex-tuned SKU, $1.75/$14). Not SOL (`gpt-5.6-sol`). Not `gpt-5-codex` (what SOL’s mouth actually was).

**Pricing (OpenAI short context, per 1M).** Standard $0.20 / $0.02 cached / $0.25 write / $1.20 out. **Flex** $0.10 / $0.01 / $0.125 / $0.60. Fast $0.40 / $0.04 / $0.50 / $2.40. Flex = Batch dollars, slower. Cache floor **1024** tokens (`PROMPT_CACHE.md`). GPT-5.6 family: cache **write 1.25×**; TTL **30 min** minimum if 5.6 path, else in-memory 5–10 min if CLI sits an older SKU.

**This occupant.** Pin **`-m gpt-5.6-luna`**. Wallet **oa-api** (`live/config/openai_api_key.txt`). Measure **`model`** on the response. If the CLI serves `gpt-5.3-codex` / `gpt-5-codex` / `gpt-5.4`, **stop and report** — that is not Luna.

**Refuse.** Non-flex Luna was “do not retap” as a **lane** (`CANON_SPAWN` r14). This seat **pins Flex** (layer 3). If Flex is omitted, she is Standard Luna — still Luna, but **say so**; do not pretend Flex rates.

---

## 3. Harness — Codex CLI, kind `review`, Flex lane

**Canon.** Kind from Role: JUDGE → **`review`**. Via from family: OpenAI → **`codex exec`**, not OpenRouter chat, not Vertex, not grok.exe (`CANON_SPAWN` r4.3). Degenerate `mouth:*` only if native via unbound; Codex **is** bound. Digs = Harness + Enviro (nickname only; Harness is still layer 3).

**This occupant.**

- Binary: `codex.cmd exec` (npm). `--ignore-user-config` so ChatGPT login does not steal the wallet.
- Kind gate: **`--sandbox read-only`**. Not `--approve-for-me` (that is CODER write). Not Agent Platform “Create an Agent.”
- Flex: `-c service_tier="flex"`. Codex 0.143–0.151 has **stripped Flex** when the model catalog omits it ([#31562](https://github.com/openai/codex/issues/31562)). **Measure** `service_tier` / usage vs Flex rates. Omitted Flex = Standard Luna inside Codex.
- Prompting guide you pasted is for **`gpt-5.3-codex`**. Do **not** dump that whole starter prompt onto Luna. Let **codex-cli** inject tools; we add WRAP + Mission. Do **not** ask for an upfront plan (guide: she can **stop early**).
- Review jobs: Codex guide “Special user requests / review” — findings first, file:line, severity.

**Call file (not run):** `work_orders/ccr/CALL_LUNA_587.cmd`.

**Refuse.** `grok.exe` / Cursor BUILD / Vertex / OR chat as this Judge. OR Flex Luna is a **mouth**, not this harness.

---

## 4. Wrapper — `WRAP/{Role}` + `STYLES/{Model}`

**Canon.** Wrapper = `WRAP/{Role}.md` + `STYLES/{Model}.md` (append). Missing STYLE → `_TEMPLATE`. PREFIX is not rewritten; STYLE/WRAP are **tails** on the stable prefix (`CANON_SPAWN` r4.4, r15). WRAP question: *What is the intent, and the best execution of this intent?*

**On disk.** `cosmos/WRAP/CODER` (propose_only, pen=none, P10). `cosmos/WRAP/CCR`. **No `WRAP/JUDGE`.** `cosmos/STYLES/_TEMPLATE` only (no `STYLES/gpt-5.6-luna`).

**This occupant (fill, not silent skip).**

- WRAP/JUDGE **fill**: Role=JUDGE; pen=none; propose_only=true (grade, don’t merge); first line KEEP/DROP/NONE/HOLD/UNMEASURED; WRAP question; findings-first review; no plan-as-deliverable; no “don’t modify files” **as a coder gag** — she is read-only via **sandbox**, not via a Judge HOUSE that fights Codex.
- STYLE fill: `_TEMPLATE` (family=default).
- Codex injects `AGENTS.md` as user-role messages (legend). File: `live/work/codex/hero-luna-587/AGENTS.md`.

**Hole to Gitur later:** add `cosmos/WRAP/JUDGE` + `STYLES/gpt-5.6-luna`. Until then this fill is the wrapper. Do not occupancy-write those onto `main`.

---

## 5. Skills — new training, child’s set

**Canon.** Skills = Role defaults + Role[Model] overlays. Propose → **CCr accept** (`SkillRegistry.accept` + `assert_pen`). Child does **not** inherit parent skills. Empty extra = Role defaults only.

**On disk.** Superpowers pack under `work_orders/ccr/skills/` is **propose-only**, not fenced-activated (`WO_SKILL_ACTIVATE.md`). `GET /skills` UNMEASURED until accept. Judge does not `accept`.

**This occupant.** **No extra skills.** Do not attach `verification-before-completion` or `quality-reviewer` without CCr accept. Codex SKILL.md dirs are **not** auto-accepted COSMOS skills. If Codex enumerates `~/.codex` skills, that is **vendor** training, not our Role[Model] overlay — note it in the run record if it fires.

**Refuse.** Self-activate skills. `live/state/skills/active/` writes from this Judge.

---

## 6. Tools — allow-list, then kind-gate

**Canon.** Tools = Role[Model] allow-list, then **kind-gate**: `review` **cannot** take coding-write; review sandbox **read-only**; empty = none (`CANON_SPAWN` r4.6). Gadgets stay **in** the legend (not the Mission pack).

**Codex native (in-distribution):** `rg`, `read_file`, `list_dir`, `glob_file_search`. Guide prefers tools over raw `cmd`. **`apply_patch` is a write gadget** — **kind-gate OFF** for JUDGE. `update_plan` optional; do not end on a plan. `shell` only if no file tool exists; no `git push` / `git merge` / `git reset --hard`.

**This occupant.**

| Allowed | Forbidden |
|---|---|
| `rg`, `read_file`, `list_dir` | `apply_patch`, `--approve-for-me`, workspace-write |
| Read `docs/CANON_PEN.md`, `TASK.md`, `AGENTS.md` | `git push`, merge, extra `grok.exe` |
| | USPTO, unique-head restore |

**Windows.** Codex is better in PowerShell now; still prefer `rg`/`read_file`. Do not block the sandbox into an empty box (SOL scar).

---

## 7. Enviro — house, ctx list, wallet, cache, resume

**Canon.** env, ctx as a **list** (no ` · ` concat — NO_CONTEXT scar), pack **fat|house**, `budget_out` ≤ **$1/M** unless named, `cache_ttl`. BU/SEED resume **here**, before the call (`CANON_SPAWN` r4.7, r7, r8).

**This occupant.**

| Knob | Value |
|---|---|
| cwd / digs (house) | `V:\A\Ai\COSMOS\live\work\codex\hero-luna-587` |
| git | detached `1e1ce71b` = `origin/ccr/canon-pen` — **not** `origin/main` LiT |
| pack | **house** (PR is 46 lines; do not dump `cosmos/`) |
| ctx list | `docs/CANON_PEN.md` `[read*]`, `TASK.md`, `AGENTS.md` — **list**, not concat |
| budget_out | Flex Luna **$0.60/M** (under $1). If Flex omitted: **$1.20/M** — still under named quality, **report** |
| cache | PREFIX = AGENTS.md + WRAP fill (stable, no dates/PR id in legend). Mission pack is **tail**. Floor 1024. Measure `cached_tokens` / `cache_write_tokens`. Precache SOP: first call **writes** prefix |
| cache_ttl | Flex/5.6: aim **30m**; if in-memory, **5–10 min idle**. Hit resets clock |
| wallet | oa-api key; **unset** leftover env that would mix ChatGPT vs Platform (`OPENAI_HANDS`) |
| auth | **not ADC**, not Vertex, not Kelly |
| `--ignore-user-config` | yes |
| resume | no BU/SEED inject for this Judge spawn |

**Refuse.** Empty attempt dir (SOL scar). cwd inside LiT `main` with write. Kelly/Medicine Man. Padding PREFIX with clocks.

---

## 8. Mission pack — this job (not in the legend)

**Canon.** Mission pack = ITEM / task / diff. Volatile. P11: legend prefix-stable; mission is tail. Naked questions out of SOP. WOMBAT: good output **saved for Judge**; this **is** the Judge. After her mouth: `attempts.jsonl` schema `cosmos-score-attempt/1`. PR **stays open** until KEEP. CCr G46 merges only then.

**This dispatch.**

| | |
|---|---|
| Gitur | **PR #587** https://github.com/keithbbf-gif/cosmos/pull/587 |
| File | `docs/CANON_PEN.md` (+46 / −0) |
| Author | orch `716fbaea` — not CCr, not SOL |
| Intent | Pen receipt: disable other writers first. No straight-to-tree. They stay until judged. Boxes, not LiT. WOMBAT save/rerun. |
| Product | First line **KEEP \| DROP \| HOLD** + one sentence. Then findings or **NONE**. |
| Not | merge, push, apply_patch, dump cosmos/, grade 580–586, harvest gf38-001–200 (later mission) |
| Save | `work_orders/ccr/JUDGE_LUNA_PR587.json` + `live/state/attempts/attempts.jsonl` |
| File on disk | `live/work/codex/hero-luna-587/TASK.md` |

**Next Mission packs (same legend, new DUD):** cDeck tab harvest PRs — Composer CHECK in Cursor; this Judge; new TASK.md. Do not glue them onto #587.

---

**DUD = layers 1–8 applied.** No DUD = not a HERO = no spawn. Call ready: `CALL_LUNA_587.cmd`. **Not run.**
