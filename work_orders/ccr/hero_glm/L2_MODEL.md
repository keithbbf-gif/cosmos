# Layer 2 — Model

**Value:** `z-ai/glm-5.3-flash` (`VALUE_CODER` in `cosmos_openrouter_rail.py`)

Volume coder on the A-team (~71.5 COD, **$0.075 in / $0.25 out**). Under $1/M out. Not GLM-5.3 full unless Flash 429s and Keith names the swap.

**Scar:** OpenRouter often routes Flash to **DeepInfra**; **HTTP 429** `engine_overloaded` / `upstream_provider_shared_pool`. That is not our OR key. Measure `model` on the response. If 429: **do not as-is retry** — partner path is GF38 or wait; do not retap Qwen Max.

Cache: OR auto-cache; `tag_preload` + `prompt_cache_key` from `cache_family`. Measure `cached_tokens`. No Flex lane.
