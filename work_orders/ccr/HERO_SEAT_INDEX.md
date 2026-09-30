# HERO Seat Index — single pointer for seating + testing coders

**Authority:** live tree. This file is the index; the files below stay where they are.
**Rule:** propose-only outside `V:\A\Ai\COSMOS`. CCr disposes onto live. No second live tree.

## 1. SOP — how to seat (read in order)
- `SOP_SUMMON_HERO.md` — full install per layer (L1 AGENTS §1 … L7 isolated cwd + ctx list, Mission TASK.md). Confirm ACTIVE via `--ephemeral` / new chat.
- `SUMMON_BY_HARNESS.md` — ACTIVE = first line matches Role AND SKU bound. HTTP 200 ≠ ACTIVE. Per-class symptom table.
- `SOP_CCREW_PACK_SMOKE.md` — smoke order cheapest→dearest; `$0 :free` first; named pin only; smoke TASK first line `NONE`.
- `SOP_CCREW_CATALOG.md` — model → harness SOP → pack dir table (Keith paste 2026-09-24).
- `HERO_BLUEPRINT.md` — legend (L1-L7) + tail (L8) JSON → runner mapping (this file).
- `docs/CANON_SPAWN.md` — spawn 5 (ROLE WRAP SKILLS TOOLS PARAMS); STYLE + CONTEXT are fills; MODEL is DUD L2.
- `docs/HARNESS.md`, `docs/DUD.md` (AA mirror: `V:\A\COSMOS_Harness\AA\COSMOS_Harness\AA\docs\`) — product + Legend/Tail definitions.
- `docs/REVIEW_HOLD.md` — HOLD verdict: keep refuse spine, don't merge as product until draft consumes Shot-1 IR.

## 2. Prompt notes per model (CCrew)
- `WOMBAT_PROMPT_NOTES.json` — `by_slug` prompting_notes + scar_note per model (Nex Mini, North Mini, Hy3-preview, Qwen3.8-flash, DS-0731, Nemotron Lightning, Gemini 3.8, Muse Spark 1.3, grok-4.6). **This is the per-model prompt section.**
- `CCREW_SEATS.md` — JUDGE Luna, CODERS 1-6, WOMBAT Luna MAX. Order + MAX/OPTIMUM token rules.
- `CREW/IN/` — WRAP/, STYLES/, CODING_GUIDELINES.md, GF38_MOUTH.md, ELEGANT_TASK.md.
- `live/state/model_rater/seats.json` — seated inventory.

## 3. xfer / xFORM (fail path)
- `cosmos/cosmos_duds.py:249 xform()` — correction tail only; stage-1 bytes never rewritten. `ATTEMPT_CAP = 3`.
- `cosmos/cosmos_code_checks.py:302 fails_of()` — error text WOMBAT pastes into xFORM.
- `CODER_ALTERNATES.md` — trial row field 6 `xfer_function` = `fails_of()` text; saved to `live/state/porosity/trials/<id>.json`. 3-strike rotation ladder + alternates matrix.
- `DEFINE_JUDGE_RUN.md` — `fail_xfer(order)`: FAIL → JSONL attempt + partner autopsy + GAC re-seat or `superseded`. PR #591 open/unjudged.

## 4. Model Rater
- `live/state/model_rater/` — catalog.json, seats.json, porosity.json, preload.json, prices.db, judge_ours.jsonl.
- `V:\cosmos_props\2026-09-10_P23-Irbe-audit_stamps_and_Model-Rater-join.md` — rater joins catalog + seats + porosity + pair tensor + stamps.
- `DEFINE_WOMB.md` — auto-seat: pick pair from rater ∩ GAC, max orthogonality, paid-low vs :free.
- `CODER_ALTERNATES.md` § Data Trail — porosity math: Porosity P(both wrong), Orthogonality P(exactly one wrong), Rescue P(B correct|A failed).

## 5. Doors (hero_unify.BIND) + cheats
- `work_orders/ccr/hero_unify.py` — BIND: openrouter, pi, opencode, dsh, vertex, codex, cosmos-code. `PACK_BY_HARNESS.md` rule: thin pack on strong door, fat pack on weak/none.
- `work_orders/ccr/harness_cheats/` — README + per-door cards (cosmos-code, pi, opencode, dsh, gemini, codex, openrouter, grok) + CORE_REVEAL.md.
- `V:\Streams\cosmos_code\harness_examples\ABSORB.md` — what COSMOS CODE keeps / refuses. Working set, not a port.
- Scaffold (spine): `V:\A\COSMOS_Harness\code\cosmos_code_scaffold\` (canonical) + Streams mirror `ours/cosmos_code_scaffold\`.

## 6. Hero packs on disk
- `work_orders/ccr/hero_coders/` — 27 stubs (1_glm … 27_qwen37) + README + skills.
- `work_orders/ccr/hero_luna/` — JUDGE Luna complete (L1-L8 + DUD.toml + worktree).
- `work_orders/ccr/hero-wombat-luna/` — seated WOMBAT (GF38 DUD retired).
- AA mirror: `V:\A\COSMOS_Harness\AA\COSMOS_Harness\AA\cosmos_code\hero_luna\` + STYLES/ + WRAP/.

## 7. Scars (read before seating)
- S-156 `SCAR_HERO_SUMMON_20260923.md` — 7 failure classes (upstream 429, pin hole, dead slug, 403 gate, :floor-on-:free, mouth form, Codex read-only).
- `SCAR_MODEL_CALL_20260925.md` — CALL-001..008 (stale SOP, OR_CHAT, EMPTY_HOUSE, STDIN_OPEN, HUNG_SPAWN, LOG_IS_NOT_MODEL, PACK_NOT_APPLIED, PUBLIC_TRACES).
- `SCAR_CCREW_CATALOG.md`, `SCAR_CCREW_PACK_SMOKE.md` — catalog + smoke scars.
- `docs/SCARS_2026-09.md` — occupancy scars (two heads/pens, zombie grok.exe, concat CTX, FAIL terminal, judge-on-empty-WOMB…).

## 8. Today's learnings (2026-09-28/29)
- Seated `sonnet-5` STYLE pin in AA scaffold (`cosmos_code/STYLES/sonnet-5`); `defaults('CODER','sonnet-5')` now resolves pinned file, not `_TEMPLATE`. No regression: `prove` still 11/12, single FAIL `HERO is 8 UNMEASURED slots, not MODEL, not CCr`. Spine 9/9 green.
- Paste-list triage: 17 embeddings REFUSED as coder mouths (`EMBED_NOT_CODER` — vector ≠ first-line contract). 5 generative: `gpt-oss-20b` + `gpt-oss-120b` pinned (CHEAP_CODERS, OR door); GPT-5 Nano, GPT-4.1 Nano, Gemini 2.5 Flash Lite UNPINNED → REFUSED until CCr pins.
- Roster scale: ~70 pinned (17 free + 53 value: 32 CHEAP_CODERS + 3 Flex + 18 extras). Measured ACTIVE 2026-09-23: Nex Mini :free, North Mini :free, Luna 6 floor. Expect ~1/3 ACTIVE per pass (429 pool, dead slugs, gates, mouth-form).
- Bakeoff loop: Rater picks pair → hero pack seats → fails_of/xform on fail → trial + xfer_function saved → porosity updated.
- Smoke-12 (same day, `_summon_or_hero.py --routing off --ping`): 5 ACTIVE (nemo35f, lagunas, solarpro4, qwen37, mimo25 — first line NONE + HERO_OK). 2 mouth-form (northmini essay, hy3preview dropped NONE). 3 REFUSED stale-slug (nexmini missing :free, gemma431b missing -it, qwenomni slug drift — PACK vs PINNED). 2 upstream-429 (lagunaxs, qwen27f). Rows in `CCREW_PACK_SMOKE.jsonl` (pass=smoke12). New scars: OR-PACK-NO-TOOLS (no [legend.tools] in OR PACKs; CALL_*.cmd also missing --duds), STALE-SLUG hole.
- F1 free-tier set (12 seats, ladder to 7 tries): 5 ACTIVE — ultra + northmini + nanoomni on t1, super on t2 (prefill), lightning on t6 (FizzBuzz TASK; ping mouth gibberish). 7 SKIP: gemma26/31bf upstream-429, lingvl 404 dead-free (paid live), inklings 403 agentic-gate, nexmini/nexpro 404 free-gone (nexmini was ACTIVE hours earlier — same-day slug pull, paid live). Every attempt in `BAKEOFF70.jsonl`.
- F2 free-tier set (5 + lagunas FizzBuzz retest): 4 ACTIVE — spacebunny t1 (new seat), lagunasf t3 (pool cooled mid-ladder), dots3 t1 (surprise: catalog said 400, live 200 + NONE), lagunas-fizz EXACT t1. 2 SKIP on hot pool: qwen27f, lagunaxsf (429 ×4 each — revisit when cool). Free tier stands 10 ACTIVE / 7 open (pool: gemma26/31, lagunaxsf; gate: inklings ×2 → agentic door; dead-free: lingvl, nexmini/pro → paid slugs). Revisit pass: qwen27f seated (pool cooled).
- Value tier V1–V5 (52 seats, clone): 42 fully ACTIVE (ping + FizzBuzz exact), 7 ping-ACTIVE/fizz-FAIL (nemolight, maverick, qwen3-vl-8b/32b, qwen37flash, gemma31b-it, inkling-paid — FIZZ-15LINE class), 3 SKIP (muse11c dead slug, scout pinned-unserved, seed tool-mouth). Grok-4.6 via OR door (refusal-form broken with reasoning-low). Luna line all ACTIVE via OR, no codex needed. 150 rows in `BAKEOFF70.jsonl`. New scars: REASON-DOUBLE-400, REFUSAL-FORM, MINISTRAL-DROPS-NONE, INKLING-NO-NEWLINE, SEED-TOOL-MOUTH, DEFAULT-ROUTE-SUFFIX.
- FREE-CLOSE (clone, 49 rows): laguna-xs-free SEATED (t10 ping NONE+HERO_OK after FizzBuzz-exact t6). gemma pair still pool-hot. Inklings: no agentic door exists (codex 400 not-supported + OR 403 — HARNESS_GATE proven with evidence). Nex paid twins are LIVE on /models but UNPINNED — CCr pin owed, then smoke. New scars: HARNESS_GATE-codex, UNPINNED-NEEDS-PIN, SKU-ECHO caveat.
- FIZZ70 (clone, 64 rows, 49 seats): 41 byte-exact PASS. 8 FAIL: dots3 + hy3 + qwen38b (mouth essays), nemoultra + qwen330b (15LINE class), nanoomni + spacebunny (transient upstream/empty — revisit), qwen27f (429). Notable: qwen37flash PASSED despite V4 fizz history — probe beats history.
- N1/N2 new list (22 seats, clone, 161 rows): 0 seated — ALL pin-refused pre-HTTP by the rail gate (`not a pinned OpenRouter id`), zero spend, zero probes. 21 have valid catalog entries; ds-pro-0423 unlisted. Rotators ×2 + hy3-nonpreview refused without calling. Rule learned: check PINNED membership FIRST before any ladder — the rail, not the catalog, is the blocker. CCr pins owed: 21 slugs + nex twins.
- WRITE true-acceptance test: 7 filed executing programs (seed, qwen32b, inkling-paid, dots3, qwen8b-vl, gemma31b-it + 1), NONE replies, L2-L7 bound — applied=false on all (see GRADER-CONTRADICTION).
- GO9 (10 seats): nanoomni + spacebunny ping-ACTIVE; maverick, qwen38b, qwen330b, dots3, hy3 SEATED-BY-EVIDENCE (write-tool programs execute, NONE replies). Pool still hot: gemmas, qwen27f re-pooled.
- DEV-DIRECT (dev mode, pin gate bypassed): 14 of 25 unpinned SEATED — seed-code, seed-turbo, ds-flash-vision, longcat, minimax-m3, nex-mini/pro (paid twins live), perceptrons, qwen36-flash, qwen37-plus, step37, inkling-small-paid, glm-flashx. Plus DEV2/3: command-a, glimmer (reason-minimal), qwen36-plus (max2048), qwen36-27b + bare-1.1 (reason-minimal). Combined: 79 seated (653 rows).
- DEV3N round (21 new, no batch): seated command-a, glimmer, qwen36-plus, qwen36-27b, bare-1.1 (reason-minimal/max-fixes), gpt-4.1-nano via opencode-write (TOOL-MOUTH: files exact ping + fizzbuzz, never chats). Terminal form-fails: trailing-space class (reka, nova-micro, gpt-4o-mini, lunaris, nemo, llama-3.x) + leading-space mythomax — stern backfires (drops NONE). Fencers + essays hold. qwen2.5-7b unlisted-invalid. Pools hot.
- MUST round: grok-4.7 + ds-v3.2 fully seated; gemma-3-4b + mimo-25-pro form-class; mimo25pro PRESSURE-DECAY.
- PROSPECT top-12 by code-ELO: seated opus-5, sonnet-5, kimi-k3, glm-5.1, glm-5-turbo, qwen37max (easy+med+fizz). HARD tier (mergesort file must execute, opencode door): opus-5, sonnet-5, kimi-k3 all run clean. Still open: opus-4.6 (empty ×3), gemini-3.5 (code-wrap ×2), gemini-3.7 (400s vary), muse-spark-1.3 ITSELF (empty ×3 — my own mouth fails the harness; noted). 111 seated (835 rows).
- Exact IDs (464 catalog): ds-v4-pro bare seated; qwen2.5-7b dead; batch out of scope.
- OPC door sweep: 6 ping-seated (command-r-plus, mistral-small, qwen35+, nova-micro, nemo, gpt-4o-mini); mistral-small + nemo FizzBuzz-exact. NO-TOOL-ENDPOINTS scar (minimax-01, llama-3.2-3b).
- REST2 re-run with packs verified (agents:true): opus-4.6, gemini-3.5/3.7, muse-spark-1.3 (self, seated), gpt-4o-mini, qwen35+, mimo-25-pro — all FizzBuzz EXACT. Naked-pack scar: first REST pass ran 7 seats with no AGENTS.md (path mismatch) — `_summon_opencode.py` now REFUSEs packs with neither AGENTS.md nor WRAP.md. 117+ seated.
- GATE BROKEN → HARNESS FIXED: `_summon_opencode.py` (AGENTS.md bind, `-m openrouter/<slug>`, ping/fizz grades, DOOR2 rows) seats inkling:free BOTH — ping-exact + instruction-only FizzBuzz EXACT. Cheat updated. 81 seated.
- COPILOT door built (`_summon_copilot.py`): authenticated, ping-exact + FizzBuzz-exact on auto. Next: enumerate --model names.
- Parent docs: pi needs ZAI_API_KEY (or /login) for native GLM, DEEPSEEK_API_KEY for dsh — neither on box; OR fallback carries them until Keith logs in.
- GRADER-CONTRADICTION scar (blocking 95%): `_py_first` demands python-opening first line while the hero contract demands NONE-first — no reply can satisfy both, so applied=true is UNREACHABLE for NONE-first coders. 7 seats marked SEATED-BY-EVIDENCE (set=WRITE2). Fix owed (CCr): grade_pack must accept NONE-first when mission output.what=text, or coder missions go python-first. Maverick preached again (genuine mouth fail); spacebunny empty-transient.
