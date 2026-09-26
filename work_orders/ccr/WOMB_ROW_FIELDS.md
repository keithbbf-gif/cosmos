# WOMB row — full field catalog (not the 6-field drop)

**Authority split.** `WOMB_MASTER.jsonl` is a **thin index** (~30–38 keys). The rest
lives in drops, `_write_womb_board.py` SEATS, `docs/PROMPT_CACHE.md`,
`docs/CANON_SPAWN.md`, `live/state/attempts/`, `live/state/porosity/`,
`cosmos_duds.py` (xform / attempt). A filled board row is the **union**.
UNMEASURED until observed. Do not invent scores.

**Prompt location:** drop `Task` / master `task`. Fat prompt = path+hash
(`live/state/attempts/blobs/<sha>`), not a 2MB JSONL cell. Prefix files:
`work_orders/ccr/CREW/IN/PREFIX.md` + `CACHE_RULE.md` (named in PROMPT_CACHE;
CACHE_RULE.md may be missing on disk — UNMEASURED).

**Timestamp:** drop `Timestamp` (ISO+offset). Board FIFO: `fifo_ts`.
PREFIX must **not** contain timestamps (P11).

**Max precache / Size formula (after PREFIX+prompts exist):**
`MAX = context_window − (cached_tokens + prompt_tokens) − 0.20×context_window`
Never 0. `MAX ≤ 0` → refuse. **OPTIMUM** = expected+headroom or `"float"`, never 0.
xAI: also keep **input** under **200k** (2× surcharge). Floors: Luna **1024**;
GF38 Vertex **4096**. Ling window **262144** — never CACHE_FAT.

---

## A. Identity / FIFO (~12)

`n` `order_id` `kind` `source` `folder` `state` `fifo_ts` `Timestamp` `set_id` `ab_pair_id` `arm` `fail_kind`

## B. Location / Where (~8)

`wo_path` `write_path` `output_spec` `output_what` `environment.cwd` `sandbox` `wallet` `pack` (fat|house)

## C. Prompt / preload (the missing “prompt” column) (~12)

`task` (verbatim wish/job) `prompt_sha` `prompt_path` `prompt_hash` `prefix_path` `prefix_hash` `cache_rule_path` `item_tail` `first_line` `naked_first` (bool) `cached_tokens` `cache_write_tokens`

## D. Legend (7 layers + hashes) (~10)

`role` `model` `harness` `wrapper` `skill` `tools_allow` `tools_forbid` `axis` `legend_hash` `hero_pack` `hero_pack_ref`

## E. Crew of 3 (per seat × ~12 = ~36)

For each seat 1..3: `Agent` (Family \| Clade \| Version) `tier` (`free`|`paid-low`) `context_window_tokens` `cache_floor_tokens` `cache_ttl` `cache_prefix` `timeout_s` `tps` `latency_s` `in_usd_per_m` `out_usd_per_m` `pack_path` `output_what` `OPTIMUM_tokens` `MAX_tokens`

`cache_prefix` = `legend+WRAP+STYLE+SKILL` only. **Not** prompting notes. **Not** scars.

WOMBAT prompt-author notes (how to write Task for that slug, plus scar class) live in `WOMBAT_PROMPT_NOTES.json` / WOMBAT pack `PROMPT_NOTES.md`. WOMBAT reads them when writing prompts. They are **not** crew cells, **not** coder PREFIX, **not** latched onto drops.

Mix paid-low vs `:free`. Not free-vs-free only.

## F. Size knobs (~8)

`window_tokens` `prompt_tokens` `cached_tokens` `MAX_tokens` `OPTIMUM_tokens` `cap_tokens` `keep_in_tokens_under` `budget_out_usd_per_m`

## G. Outcomes / next (~10)

`state` `DONE` `COMPLETED` `next_outcome` `wo_partner` `follow_up_oid` `output_path` `output_hash` `empty_output_class` (1–4) `spend`

## H. Judge / scores (~10)

`judge_score_hero` `judge_score_base` `judge_winner` `grader_model` `grader_chair` `verdict` `4C` `needs_second_judge` `authority` `stamps`

## I. Attempts / xform / xfer (~12)

`attempt` `attempt_n` `parent_attempt` `reattempt` `rejected` `prompt_sha` (stable stage-1) `xform` (reprompt **tail only**) `xfer` `STYLE_append` `session_id` `cpu_py_compile` `cpu_fence` `cpu_tokenize`

## J. Porosity / tensor (~12)

`n_obs` `orthogonality` (alias `orth_sketch` / `signed`) `mag` `disagree` `error_mag` `cofail` `xor_err` `rescue` `T[i,j,a]` `C[i,j,a]` `kind` (`MEASURED`|`UNMEASURED`) `profile`

Store: `live/state/porosity/obs.jsonl`. Empty = UNMEASURED, not 0.

## K. Student record (~8)

`job` `chair` `preload_hash` `grader` `verdict_score` `xfer` `stamps` — `live/state/attempts/attempts.jsonl`

---

**Count:** A12+B8+C12+D11+E36+F8+G10+H10+I13+J12+K8 ≈ **140 cells** if crew is expanded. A thin master row is ~30. **Do not flatten 140 into WOMB_MASTER.jsonl** (fat blobs = path+hash).

**No pointers or labels as cells.** `<pointer>`, `see docs/…`, `[read*]`,
`n/a`, `UNASSIGNED`, or a `verified` stamp is not a value. Same as a blank.
Context source = absolute existing paths you can open. Task = full prompt
text. Crew window/tps/MAX = numbers. Timestamp = ISO. If you cannot check
the cell without following a link or trusting a badge, it is empty.

**Latch rule:** a row is not “full” until A–F are typed **values** (identity,
location, prompt text, legend, crew3, size). G–K stay UNMEASURED until the
run/judge/tensor writes them.
