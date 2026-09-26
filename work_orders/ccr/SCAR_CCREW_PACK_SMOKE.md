# SCAR — CCrew pack smoke 2026-09-24

ROLD: **S-156** continues. SOP: `SOP_CCREW_PACK_SMOKE.md`.

## New / re-hit this pass

1. **Default `:floor` on `:free`.** `cosmos_route_variant.py` default priority is `:floor`, so Qwen/Gemma requests became `…:free:floor`. HTTP 429, `response_model=None`. Same class as Nano Omni (S-156 §5). **Do not append `:floor` to `:free` pins.**
2. **North Mini STYLE regression.** 2026-09-23 first line `NONE` (ACTIVE). Today echoed PREFIX as CoT. Pack files present; mouth form failed. Not a 429.
3. **GLM smoked on OR rail.** SOP via is `pi -p` (`CALL_PI_GLM.cmd`). OR dispatch first line CoT. Mixing vias is a scar, not a pack proof.
4. **Nemo 3.5 :free CoT** — same class 6 as 2026-09-23. 200 + SKU, not coder-ACTIVE.

## Still true (S-156)

Upstream 429 on Gemma/Qwen :free ≠ our weekly cap. Unpinned = REFUSED. Inkling 403 harness gate. No `grok.exe` CCrew. Codex `:floor` is Flex for Luna, not a free-tier suffix.

## Do

Summon cheapest PINNED `:free` with catalog id **without** extra `:floor`. GLM on `pi -p`. Record first line + `response.model`. ACTIVE only if both hold.
