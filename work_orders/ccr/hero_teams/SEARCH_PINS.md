# Search pins (rail + nearby seat docs)

Source: `cosmos/cosmos_openrouter_rail.py`. Seat notes from `work_orders/ccr/_summon_or_hero.py` and `hero_teams/*/AGENTS.md`, `spark13/SOP.md`, `PROMPT_OPT.md`. No keys.

## DeepSeek v4.1 Flash

- `DS41_FLASH = "deepseek/deepseek-v4.1-flash"` — undated pin. In `PINNED_VALUE`. Allowed.
- `DS41_FLASH_1017 = "deepseek/deepseek-v4.1-flash-1017"` — rail comment: "1017 is the release date, not a score. Distinct from the undated pin." Also in `PINNED_VALUE`. Not a score.
- Rail allows both. Seat `ds41/AGENTS.md` and `PROMPT_OPT.md` call only the 1017 slug. That is a seat rule, not `model_refused`.

## Luna 6

- `GPT56_LUNA = "openai/gpt-5.6-luna"` — Flex seat (luna6).
- `GPT56_LUNA_PRO = "openai/gpt-5.6-luna-pro"` — MAX seat (luna6max). Rail comment: "Same underlying Luna, reasoning max. Not a swap of `GPT56_LUNA`."
- `OPENAI_FLEX = "openai/flex"`. No `MAX` slug.
- `FLEX_MODELS = frozenset({GPT56_TERRA, GPT56_LUNA, GPT56_LUNA_PRO})`. Terra is in the set; Sol is not.
- No provider tag → `_provider_tag` sets `OPENAI_FLEX`. Wire: `provider.only` and `provider.order` = `["openai/flex"]`, `allow_fallbacks` false. Flex also gets `prompt_cache_key` and explicit cache breakpoint.
- Rail does not set `reasoning.effort`. It copies `payload["reasoning"]` only if the caller sends a dict.
- Summon `--reasoning-effort` is `none|low|medium|high|max` → `reasoning.effort`.
- `luna6max/AGENTS.md`: "reasoning max". `PROMPT_OPT.md`: "reasoning high", still `openai/flex`. Those two seat lines disagree. The rail does not choose.

## Muse Spark 1.3

- `MUSE_SPARK_13C = "meta/muse-spark-1.3-contributor"` — in `CHEAP_CODERS` → `PINNED`. This is the pin.
- No constant and no `PINNED` member for `meta/muse-spark-1.3`. `model_refused` rejects it.
- Summon, only when `model == "meta/muse-spark-1.3-contributor"`: `provider_only = "meta"`. Comment: own endpoint `meta/muse-spark-1.3-contributor-20260902`, not Standard `muse-spark-1.3`.
- Rail does not default Muse to `meta`. `spark13/SOP.md`: provider `meta` only, `allow_fallbacks` false, not the standard slug.
- `family_of` in `cosmos_stations.py` labels `meta/` as family `"meta"`. That is not `provider.only`.

## GLM 5.3 Flash / relace

- `VALUE_CODER = "z-ai/glm-5.3-flash"` — named cheap pin. Not in `FLEX_MODELS`.
- Rail does not set a provider. No tag → no `only` / `order`. `allow_fallbacks` is still false.
- `relace` is not a rail constant and summon does not inject it. Seat files (`glm53/AGENTS.md`, `PROMPT_OPT.md`, `QUALITY.md`) say "provider only relace". That is a pack instruction. A caller that passes `provider_only="relace"` is accepted, because GLM is not a Flex model.

## `FLEX_MODELS` + a non-Flex tag

- `FLEX_PROVIDERS = {"openai/flex", "openai", "openai/fast", "azure", "azure/us", "azure/eu", "amazon-bedrock/us-east-1"}`.
- Flex model and tag not in that set → `_provider_tag` returns `REFUSED:provider '<tag>' is not a Flex pin`. Dispatch: `ok` false, `kind` `"REFUSED"`. Selftest: Luna and Luna Pro with `provider_only="not-a-flex-provider"`.
- `meta` and `relace` are not Flex providers. On Luna or Luna Pro they are refused.
- Unknown `endpoint` uuid → `REFUSED:unknown endpoint uuid — not a named pin`.

## `model_refused` / unpinned

`model_refused(model)` returns a reason string, or `None` if allowed. `_pin_id` drops routing suffixes (`:floor`, `:nitro`, `:exacto`); `:free` and `:batch` stay on the catalog id.

- empty → `"empty model"`
- bad suffix → route-variant error
- `_ROTATING` = `openrouter/free`, `openrouter/auto`, `openrouter/free:free`, or id ending `/free` unless `gemma-4` → `"rotating/unpinned OpenRouter id … (H3 silent swap — named pin only)"`
- `~…` or `…-latest` → `"alias/latest id … is not a named pin"`
- not in `PINNED` (`PINNED_FREE | PINNED_VALUE`) → `"not a pinned OpenRouter id …"`
- `allow_fallbacks=true` is a separate refuse: `"allow_fallbacks=true is H3 silent swap"`. Dispatch always sends `allow_fallbacks: false`.
