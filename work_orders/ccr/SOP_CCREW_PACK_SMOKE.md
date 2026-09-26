# SOP — CCrew pack smoke (cheapest → dearest)

**When:** Keith says summon/verify CCrew. Not WOMBAT board-fill. Not grok.exe.

**HERO** = Agent + DUDs (legend AGENTS+WRAP+STYLE+SKILL + mission TASK).
No DUD = no spawn. Canon: `docs/CANON_SPAWN.md`. Companion: `SOP_SUMMON_HERO.md`.

## Order

1. **`$0 :free`** named pins in `PINNED_FREE` (`cosmos_openrouter_rail.py`).
2. **Paid-low** `CHEAP_CODERS` / `PINNED_VALUE` (GLM Flash, DS Flash, Ling paid, Hy3 preview, …).
3. **Never** `grok.exe` as CCrew. Grok = Gitur Cursor BUILD only.
4. **Never** Cursor credits for CCrew.
5. Skip **unpinned** slugs (scar: REFUSED before HTTP).

## Correct summon (OpenRouter coder)

```
py -3.14 work_orders\ccr\_summon_or_hero.py ^
  --pack <hero pack dir> ^
  --model <exact PINNED slug> ^
  --out work_orders\ccr\<SLUG>_HERO_last.txt
```

- Named pin only. Not `openrouter/free`. Not `:floor` on `:free` (Nano Omni scar).
- PREFIX = AGENTS+WRAP+STYLE+SKILL (no dates, no WO ids). TASK = volatile ping.
- Smoke TASK: first line `NONE` (or `diff --git`). Second line `HERO_OK <slug>`.
- Runtime bind = `response.model`. `allow_fallbacks=false`.
- ACTIVE = HTTP ok **and** first line `NONE`|`diff --git` **and** SKU bound.
- 200 + preamble/CoT = pack on, **not** coder-ACTIVE (Hy3 / Nemo class 6).

## Other vias (do not mix)

| Seat | Via |
|---|---|
| GLM Flash | `pi -p --provider zai --model glm-5.3-flash` |
| DeepSeek | `dsh --profile headless` |
| Ling paid | `opencode run` |
| GF38 | Kelly Vertex → Joanna failover |
| Luna WOMBAT/Judge | Codex isolated `CODEX_HOME`, no `--ignore-user-config`, `-m …:floor` MAX |

## Scar classes (S-156)

1. Upstream shared-pool **429** (Gemma/Qwen :free) — not our weekly cap.
2. **REFUSED** unpinned.
3. **404** dead :free slug.
4. **403** agentic-harness gate (Inkling).
5. `:floor` on `:free` → `response_model=None`.
6. Mouth form (first line not NONE).
7. Codex Windows sandbox read-only → host harvest.

Log: `CCREW_PACK_SMOKE.jsonl`. New scars: `SCAR_CCREW_PACK_SMOKE.md`.
