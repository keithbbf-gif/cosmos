# HERO seat (search 2026-10-28)

`V:\A\COSMOS_Harness` is not present. Sources: `V:\A\Ai\COSMOS` (parent `V:\A\Ai` has no second spawn canon).

## Spawn refuse

`docs/CANON_SPAWN.md`. Agent + DUDs = HERO. No DUD = no spawn. A child is a new full legend, not a thinner spawn. `grok.exe` / `grok --single` as WO worker or subagent = refuse. Coding = Gitur/GAC, not grok.exe.

Also refuse: empty Role or empty Model after defaults; Role `DAEMON` as an LLM; ORC on a coding via; native via bound while harness is degenerate `mouth:*`; `MAX <= 0`; written `cap_tokens` / `optimum_tokens` of 0.

`cosmos/cosmos_duds.py` `require_duds`: `LAYERS_INCOMPLETE` if role not in the set, model/harness/wrapper/skills-list/tools.allow/enviro/mission missing, wrapper path not a file, `optimum` is 0, or `l7.what` is not `text|python|no_prose`. `ORC_NO_CODING` if role is ORC and harness contains `cod`.

`work_orders/ccr/_summon_or_hero.py` `verify_pack` exits before HTTP: no `--duds` file; `require_duds` fail; `--model` != `l2_model`; `l3_harness` lacks both `openrouter` and `summon_or_hero`; any of `AGENTS.md` `WRAP.md` `STYLE.md` `SKILL.md` `TASK.md` missing or empty.

## Summon

```
py -3.14 work_orders\ccr\_summon_or_hero.py --pack <dir> --duds <DUDS.json> --model <pinned slug> --out work_orders\ccr\<SLUG>_HERO_last.txt
```

On disk first (`SOP_SUMMON_HERO.md` + script `NEED`): `AGENTS.md` (§1 role, §2 exact SKU, §3 this via, §6 tools), `WRAP.md`, `STYLE.md`, `SKILL.md` or the words `none extra`, isolated cwd, `TASK.md`, and `DUDS.json` (`--duds` is required; the smoke SOP line omits it). System turn is `WRAP.md`. User turn is `TASK.md`. Optional: `--routing off|floor|nitro|exacto`, `--prefill-none`, `--ping`.

`:free` with `--routing` unset becomes `routing=off`. Do not send `openrouter/free`. Unpinned slug is `REFUSED` before HTTP (`cosmos/cosmos_openrouter_rail.py` `model_refused`).

## ACTIVE

`SOP_CCREW_PACK_SMOKE.md` / `SOP_SUMMON_HERO.md`: HTTP ok, first line `NONE` or `diff --git`, and `response.model` matches the SKU. A 200 with a preamble or CoT is not coder-ACTIVE (Hy3, Nemo class 6). `pack_verified` only means the pack passed before the call. Script `hero_ok` is a different check: first line looks like Python (` ``` ` `'''` `#` `import` `from` `def` `class`).

## OpenRouter provider

Rail `dispatch`: `allow_fallbacks: true` on the payload is REFUSED (`H3 silent swap`). Body always sends `provider.allow_fallbacks false`. `_provider_tag`: `provider_only` (or `provider`) becomes `provider.only` and `provider.order`. If unset and the pin is in `FLEX_MODELS` (`openai/gpt-5.6-terra`, `openai/gpt-5.6-luna`, `openai/gpt-5.6-luna-pro`), tag is `openai/flex`. A Flex model with a tag outside `FLEX_PROVIDERS` is REFUSED.

Summon sets `provider_only=meta` only when `--model` is exactly `meta/muse-spark-1.3-contributor` (not `meta/muse-spark-1.3`). It does not set `provider_only` for Luna; the rail defaults Flex. Packs: `hero_teams/luna6/AGENTS.md` (`openai/gpt-5.6-luna`), `hero_teams/luna6max/AGENTS.md` (`openai/gpt-5.6-luna-pro`, reasoning max, still `openai/flex`), `hero_teams/spark13/AGENTS.md` and `spark13/SOP.md`.

## DeepSeek CoT

`SOP_CCREW_CATALOG.md`: `deepseek/deepseek-v4.1-flash` is OpenRouter `--routing off`, plus prefill if the mouth is CoT. `--prefill-none` drops the system turn and prefills assistant `NONE\n`. That slug is not `:free`, so routing off is not automatic. Seat the dated pin `deepseek/deepseek-v4.1-flash-1017` (`hero_teams/ds41/AGENTS.md`). `hero_teams/PROMPT_OPT.md`: an assistant prefill did not stop 1017 from writing the plan in the content channel; do not paste a prefill onto a plan and call it code. Older `deepseek/deepseek-v4-flash` on `dsh` is a different seat (`COSMOS_KB.json`: prefill OFF). Do not mix them.

## Argon / medicineman Vertex

Model id on the seat: `gemini-4-argon` (`hero_teams/argon/AGENTS.md`, `argon/DUDS.json`, `QUALITY.md`). Harness string: `vertex mme medicineman generateContent`. Not the OpenRouter id `google/gemini-4-argon`. Not grok.exe.

Project: `project-cc5302c9-190c-4cdf-87d`. Account: `medicineman.mme@gmail.com`. Key file path only: `V:\Research4\.secrets\vertex_medicineman_key.txt` (`work_orders/ccr/vertex_ping.py`, `tokenctr/cosmos_pay_vertex_rail.py` `CANONICAL_PROJECT`). `vertex_ping.py` ping model is `gemini-2.5-flash`; that constant is not the Argon seat.
