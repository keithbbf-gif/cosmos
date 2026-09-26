# RUN CONFIG — crank-up seating (2026-09-23, pilot order)

Pause still holds; nothing spawns until release. This file is the seating
authority for the run. Canon: `docs/CANON_AGENT_CALLS.md`,
`docs/CANON_4C_JUDGE.md`, `docs/CACHE_TTL.md`.

## Phase 1 — singles with good answers (52 heroab triples)

| Arm | Seat | Model | Pack | Harness |
|---|---|---|---|---|
| baseline | (on disk) | original agent | — | no spend, judge reads file |
| hero | same as original | 46× grok-4.6, 5× luna, 1× gf38 | `hero_coders/6_grok_gitur` / `hero_luna` / `hero_coders/2_gf38` | grok.exe CLI (SuperGrokHeavy) / codex / Vertex |
| hero2 | `glm` | z-ai/glm-5.3-flash | `hero_coders/1_glm` | cli:pi (fallback OR rail) |

Judge: **not seated.** `state/womb/judge_seat.json` absent (2026-09-24).
Do not treat SOL 6, Luna, or the stations.py roster default as a live Judge.
Scores stay PENDING until Keith names a Judge.

## Phase 2 — no-answer jobs (12 coders: 2 Phase-1 + 10 for first 50 WOs)

## Phase 2 — loose brackets in clusters of 3 (skill + speed)

12-coder plan (pilot 2026-09-23): 4 clusters of 3 coders each.
Organized as a loose bracket based on skill and speed:
- **Bracket A ("Hard Jobs"):** Top-rated frontier coders coding directly against each other.
- **Bracket B ("Slow but Good"):** High-accuracy coding models with proven ELO / coding benchmarks.
- **Always MAX effort:** Every model invoked at its maximum reasoning / effort setting.
- **Context window:** 1M floor across non-Cloudflare hosts; secondary factor on small coding tasks.

### Bracket A: "Hard Jobs" (Top-Rated Coders Coding Against Each Other)

| Cluster | Coder 1 | Coder 2 | Coder 3 | Speed & Skill Profile |
|---|---|---|---|---|
| **C1: Hard Alpha** | `grok` (grok-4.6, local `grok.exe` CLI, SuperGrokHeavy, MAX) | `gf38` (Gemini 3.8 Flash, Kelly Vertex → Joanna, MAX) | `luna6` (GPT-6 Luna, Codex CLI / OR rail, MAX) | Frontier triad. Max speed + max reasoning. |
| **C2: Hard Beta** | `muse13` (Muse Spark 1.3, opencode/OR rail, 80 t/s, MAX) | `hy3preview` (Tencent Hy3 Preview, 69 t/s, 58.8 coding, MAX) | `qwen` (Qwen 3.8 Flash, 48 t/s, OR rail, MAX) | High-speed heavy hitters. Fast turnarounds. |

### Bracket B: "Slow but Good" (High Benchmark Coding & Reasoning)

| Cluster | Coder 1 | Coder 2 | Coder 3 | Speed & Skill Profile |
|---|---|---|---|---|
| **C3: Proven Core** | `glm` (GLM 5.3 Flash, 71.5 coding, ELO 1308, cli:pi, MAX) | `ds0731` (DeepSeek V4 Flash 0731, 69.1 coding, ELO 1240, cli:dsh, MAX) | `qwen37` (Qwen 3.7 Flash, 1M ctx, 44 t/s, reasoning, MAX) | Top coding benchmarks. Deep reasoning core. |
| **C4: Ortho Depth** | `lingvl` (Ling 3.0 Flash VL, 57.0 coding, 46 t/s, OR free, MAX) | `mimo25` (MiMo-V2.5, 56.8 coding, ELO 1269, OR rail, MAX) | `nemo-ultra` (Nemotron 3 Ultra, 49.3 coding, ELO 1152, free, MAX) | High family diversity. Free/cheap depth. |

**Cursor Credits Policy (Keith 2026-09-23):**
Cursor credits are reserved STRICTLY for Gitur (PR reviews, build PRs).
Cursor credits are NOT used for CCrew, WOMBAT, Judge, Scribe, or Final Auditor.
Grok coders run exclusively via local `grok.exe` CLI on SuperGrokHeavy quota.

Keith's list is sorted by TPS (throughput) — honors it in team order:
fastest mouths fire first. TPS from your table: Luna Pro 91 · Inkling 83 ·
Muse 80 · Luna 58 · Qwen3.8-Flash 48 · GLM 5.3-Flash 33 · DS0731 25 ·
Qwen3.8-Omni 23 · Nemotron-3-Ultra 17 · Nemotron-3.5-Lightning 15 ·
MiMo-Flash 12 · MiMo-Pro 6.

Terminology (canon): **OR is a RAIL (wallet/key lane), not a harness.**
Harness = the executing vehicle (codex exec, cli:pi, cli:dsh, vertex, cursor,
opencode, openrouter chat). `via` = which rail/key the harness rides. OR-rail
seats above ride the `openrouter` chat harness by default.

Excluded on purpose: `54mini`/`oss` (openai = Judge family), `terra`/`luna-pro`
reserve (Luna Pro is seated as coder — see below), Inkling stays pen-default
Scribe fallback. Every team mixes ≥3 families or ≥3 lanes; no team shares
Judge's or Auditor's model.

### MAX effort per family

| Family | Max-effort setting |
|---|---|
| OpenAI (luna, luna-pro, sol) | `model_reasoning_effort = "max"` (Codex `-c` / body `reasoning.effort`) |
| Z.ai GLM | `reasoning_effort: "max"` body param (5-min cache: fire teams in-window) |
| DeepSeek | model default (no effort param; thinking per model) |
| Qwen | enable thinking; `enable_thinking: true` |
| NVIDIA Nemotron | `reasoning_effort: "max"` where accepted; else default on |
| Xiaomi MiMo | model default |
| Meta Muse / Gemini GF38 | no effort knob — note MAX unavailable on response |

### Vertex failover (Keith 2026-09-23)

GF38 lane wallet order: **Kelly (`orders.ggn` project-10b3a132) → Joanna
(`joanna.bbf` project-5a33f910)** on error state. Joanna has the next
expiration date. Both keys GREEN (pinged 13:0x). Never print keys.

### Phase-1 singles (unchanged)

| Arm | Seat | Model | Pack | Harness |
|---|---|---|---|---|
| baseline | (on disk) | original agent | — | no spend |
| hero | same as original | 46× grok-4.6, 5× luna, 1× gf38 | `hero_coders/6_grok_gitur` / `hero_luna` / `hero_coders/2_gf38` | Cursor BUILD / codex / Vertex |
| hero2 | `glm` | z-ai/glm-5.3-flash | `hero_coders/1_glm` | cli:pi (fallback OR) |

## Run rules

- WOMBAT (Luna 6.0 MAX) summoned FIRST on release; authors 42 wish drops;
  ORC watches WOMB + returns; WOMBAT manages CCrew seating per team.- 12-coder plan: 2 in Phase 1, 10 for first 50 WOs (4×3 teams) — 3 coders
  per job this run (recorded in `WOMBAT_SEAT.md`).
- 4Cs gate before Judge: extractor receipts in `state/code_checks.db`
  (107/111 grade entries done, 4 in flight — big therapy/blog diffs).
- Cache: prefixes per `docs/CACHE_TTL.md`; GLM/Qwen pairs fire inside one
  5-min window; Luna/SOL bursts inside 30-min windows.
- Auditor grok-4.7 HIGH: bucket-full-only (30), sub-batch 5–9 pairs/call
  (128k window; 30 biggest pairs = 3.4MB — never one call).
- Scribe Muse 1.3: 4-estate sync, 786k ceiling, ACCEPT batches only.
