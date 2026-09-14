# Editor report — `vitamins-history-claims-guarded`

**Pull request:** [#387](https://github.com/keithbbf-gif/cosmos/pull/387)  
**Editor pass:** 2026-09-14 (UTC)  
**Scope:** All forty-seven `VH-*.md` drafts, folder guardrails, `claims_lint.py`  
**Outcome:** `voice_check: edited` on every draft; claims fence tightened in seven essay bodies; lint and pytest green. **Draft PR only — not merged.**

## Mandate

Quality over speed. House rule is **stricter than DSHEA / 21 CFR 101.93**: no disease claims, no classical-deficiency sales lines, no structure/function or well-being pitch in narrator voice, no product or dose instruction. Historical syndrome names stay in the past as puzzles of a year, not uses of a bottle.

## Method

1. Read `CLAIMS_GUARDRAILS.md`, `README.md`, `STAGING.md`, and `MANIFEST.md`.
2. Full-folder grep sweeps for brochure voice, second-person “take / should” lines, structure/function dialect, and implied-use patterns.
3. Close read of high-risk drafts (ships, wards, enrichment, Pauling, structure/function map, pregnancy/B12 corridor).
4. `python3 content/vitamins-history-claims-guarded/tools/claims_lint.py`
5. `python3 -m pytest tests/test_vitamins_history_claims_guarded.py -q`

## Narrative edits (claims / creep)

| Draft | Change | Rationale |
| --- | --- | --- |
| VH-03 | “If you take one habit…” → distanced “If a reader keeps one habit…” | Removes second-person habit line that could read like soft advice adjacent to a dose. |
| VH-04 | “made a deficiency visible” → “made the missing-factor pattern visible” | Avoids deficiency-disease sales echo while keeping milling history. |
| VH-08 | Present-tense “has to eat the factor” → past-tense assay framing | Present-tense need reads like structure/function in narrator voice. |
| VH-08 | “What you might keep” → “The habit worth keeping” | Same: reader-directed takeaway without “you + keep.” |
| VH-23 | “If you take one craft lesson” → “If a reader keeps one craft lesson” | Parallel to VH-03. |
| VH-27 | Carrot / pigment sentence → enzymatic split wording | “Know what to do with a pigment” slid toward body-benefit copy; chemistry stays claim-free. |
| VH-43 | “floor you should ignore” → market-permission framing, refused in our voice | Megadose-adjacent second-person instruction; kept as cultural history only. |

No other drafts required body cuts. Refusals already embedded (Claims desk, quoted period language, statute quotes in VH-35/VH-36) were left intact.

## Furniture / tooling

- **`voice_check: edited`** added to YAML on all forty-seven drafts (after `voice: human`).
- **`README.md`** — documents `voice_check` values (`edited` / `pending`).
- **`CLAIMS_GUARDRAILS.md`** — staging YAML example includes `voice_check: edited`.
- **`tools/claims_lint.py`** — requires `voice_check: edited`; added narrator patterns for megadose-adjacent “you should ignore” + RDA/DV/mg context and bare `floor you should ignore`.

## Voice

- Brochure-term grep: **clean** (no `delve`, `tapestry`, `unlock`, `wellness journey`, etc. in essay bodies).
- Human voice retained: named places, uneven sentences, museum-case quotes for period ads and patents.
- Second-person “you” remains where it is clearly meta (VH-10 deleted “which is why you should”; VH-36 S/F examples as refused shapes; VH-19 “you have left this folder”).

## Verification

```
CLAIMS_LINT PASS  drafts=47 slugs=47
pytest: 3 passed
```

## Residual watchlist (no change this pass)

Counsel not requested. These drafts stay **staged**; promotion is a later human act per `STAGING.md`.

- **Ward-heavy IDs** (VH-16–22, VH-07–08): syndrome names dense; Claims desk must stay explicit on each promotion.
- **VH-36 / VH-45 / VH-46**: structure/function and ad dialect quoted for education; do not paraphrase into narrator endorsement.
- **VH-43**: Pauling / cold culture — disease names refused in our voice; monitor any future caption pull-quotes.

## Sign-off

| Field | Value |
| --- | --- |
| `voice_check` | `edited` (all VH-01–VH-47) |
| `claims_lint` | pass |
| `pytest` | pass |
| Merge | **no** — draft PR #387 only |
