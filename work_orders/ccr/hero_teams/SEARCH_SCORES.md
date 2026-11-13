# Seating stores

Paths under `V:\A\Ai\COSMOS`. Keys only. No note or mouth text.

## Append

Append a new seating score to `live/state/model_rater/judge_ours.jsonl`.
`cosmos/cosmos_model_rater.py` `load_ours` joins that file only. Schema must be `cosmos-model-rater-ours/1`.

`work_orders/ccr/hero_teams/SEATING.jsonl` is the same 10 keys (58/58 rows also sit in judge_ours). No code loads it.

A fail still needs numeric `score` (`0` = measured miss). Missing or null `score` is dropped and stays UNMEASURED.
Also keep `schema`, `at`, `model`, `axis`, `n`, `note`, `source`, `scar`, `sop`.
All 9 score-0 SEATING rows have those 10 keys. Do not invent a score for an ungraded mouth.

## judge_ours.jsonl

`live/state/model_rater/judge_ours.jsonl` — 275 lines.
Keys: `at`, `axis`, `model`, `n`, `note`, `scar`, `schema`, `score`, `sop`, `source`.
Early rows omit `scar` and `sop`. Axes: `hero_seat`, `hero_judge`, `coding`, `hero_reliable`, `raw_coding`, `game_design`, `orchestration`, `mobile_coding`, `judge_form`.

## porosity trial

Example: `live/state/porosity/trials/forge-coding-gitur-r1.json` (`cosmos-porosity-trial/1`).
Keys: `axis`, `criteria_id`, `criteria_text`, `disagree`, `error_mag`, `fail_a`, `fail_b`, `http_a`, `http_b`, `judge_id`, `judge_model`, `model_a`, `model_b`, `mouth_a`, `mouth_b`, `note`, `ok_a`, `ok_b`, `output_a`, `output_a_sha256`, `output_b`, `output_b_sha256`, `profile`, `prompt`, `prompt_sha256`, `schema`, `tab`, `trial_id`, `usd_a`, `usd_b`, `who_erred`.

`_porosity_pair_save.py` writes a different shape into the same folder: `cosmos-porosity-pair/2` with `judge`, `judgement`, `input_a`, `input_b`.

## Prompt / scar notes

Index names `work_orders/ccr/WOMBAT_PROMPT_NOTES.json` as the per-model prompt section (`cosmos-wombat-prompt-notes/1`).
Top keys: `schema`, `for`, `not`, `cache_prefix_stays`, `by_slug`.
Each slug: `prompting_notes`, `scar_ids`, `scar_note` (`scar_note` not on every slug).

`work_orders/ccr/MODEL_NOTES/*.md` (118 files) is the per-slug page. Heads: Catalog, Harness, Prompt notes (WOMBAT_PROMPT_NOTES), Scars observed, History (points at BAKEOFF70).

## HERO_SEAT_INDEX.md

`work_orders/ccr/HERO_SEAT_INDEX.md`

- SOP: `SOP_SUMMON_HERO.md`, `SUMMON_BY_HARNESS.md`, `SOP_CCREW_PACK_SMOKE.md`, `SOP_CCREW_CATALOG.md`, `HERO_BLUEPRINT.md`, `docs/CANON_SPAWN.md`
- Notes: `WOMBAT_PROMPT_NOTES.json`, `CCREW_SEATS.md`, `live/state/model_rater/seats.json`
- Fail path: `cosmos/cosmos_duds.py` xform, `cosmos/cosmos_code_checks.py` fails_of, `CODER_ALTERNATES.md` (trial + `xfer_function`), `DEFINE_JUDGE_RUN.md`
- Scores: `live/state/model_rater/` including `judge_ours.jsonl`
- Scars: `SCAR_HERO_SUMMON_20260923.md`, `SCAR_MODEL_CALL_20260925.md`, `SCAR_CCREW_CATALOG.md`, `SCAR_CCREW_PACK_SMOKE.md`, `docs/SCARS_2026-09.md`
- Summon logs named there: `BAKEOFF70.jsonl`, `CCREW_PACK_SMOKE.jsonl`

## Summon success / fail jsonl

- `work_orders/ccr/BAKEOFF70.jsonl` (871). Keys: `applied`, `args`, `file_runs`, `first_line`, `grade`, `l1_wrap_style`, `label`, `layers`, `model`, `rc`, `scar`, `seat`, `served`, `set`, `sku_bound`, `try`. `grade` is ACTIVE / PASS / FAIL-* / HTTP / MOUTH / SKIP. Door writers set `scar` empty only when `grade` is ACTIVE.
- `work_orders/ccr/CCREW_PACK_SMOKE.jsonl` (63). Keys: `first_line`, `grade12`, `hero_ok`, `kind`, `model`, `name`, `note`, `ok`, `out`, `pass`, `rc`, `via`. Pass/fail is `ok` plus `hero_ok`. Rows do not share every key.
- Same `ok` / `hero_ok` shape: `CCREW_CATALOG_SMOKE.jsonl`, `CCREW_POKE.jsonl`, `CCREW_DOCFIX_SMOKE.jsonl`, `CCREW_DOCFIX2.jsonl`, `CCREW_DOCFIX3.jsonl`.
- Harness step log (`_summon_or_hero.py`): `hero_teams/{ds41,luna6,luna6max,spark13}/harness_log.jsonl`. Keys: `step`, `http`, `n_tools`, `detail`. HTTP only, not the grade. Pack grade is `grade.json`: `applied`, `layers`, `first_line`, `model_returned`, `note`.
