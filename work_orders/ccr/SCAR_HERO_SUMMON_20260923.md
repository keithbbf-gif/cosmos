# SCAR — HERO summon (measured 2026-09-23)

ROLD: **S-156**. SOP: `SOP_SUMMON_HERO.md`, `SUMMON_BY_HARNESS.md`.

## What happened

TPS-order CCrew pings. Packs were hydrated. Several “failures” were **different classes**. Treating them as one 429 was wrong.

## Classes

1. **Upstream shared pool 429** — not Keith’s OpenRouter weekly cap (`is_free_tier=false`, remaining ~149.8/150). Gemma `:free` → Google AI Studio; Qwen `:free` → ModelRun. `limit_source=upstream_provider_shared_pool`.
2. **COSMOS pin hole** — roster slugs not in `PINNED` → `REFUSED` before HTTP. Laguna, Dots3, Qwen3.7-flash, Qwen3.6-35b, Hy3, Solar Pro 4, MiMo, Qwen omni.
3. **Slug dead** — Ling VL `:free` HTTP 404: use paid `inclusionai/ling-3.0-flash-vl`.
4. **Harness gate** — Inkling `:free` HTTP 403: “only available on agentic harnesses.” Chat dispatch will never ACTIVE.
5. **`:floor` on `:free`** — Nano Omni HTTP 200 with `response_model=None` on `:free:floor`. Catalog id without extra floor binds.
6. **Mouth form** — Hy3 preview and Nemotron 3.5 Lightning HTTP 200 + SKU bound, first line not `NONE` (preamble / CoT). Pack on; not coder-ACTIVE.
7. **Codex Windows** — `sandbox_policy: read-only` despite `--sandbox workspace-write`. Host harvest writes WOMBAT drops.

## Consequence

WOMBAT Agent field and ORC summon must branch on **class**, not retry the same 429. ACTIVE seats today: Nex Mini `:free`, North Mini `:free`, WOMBAT Luna 6 MAX.
