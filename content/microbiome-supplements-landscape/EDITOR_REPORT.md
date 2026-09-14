# Editor report — `microbiome-supplements-landscape`

**Pull request:** [#438](https://github.com/keithbbf-gif/cosmos/pull/438)  
**Editor pass:** 2026-09-14 (UTC)  
**Scope:** All forty-four drafts, `CLAIMS_GUARDRAILS.md`, `qa/check_pack.py`  
**Outcome:** `voice_check: edited` on every draft; one claims-distancing fix in draft 40; pack QA green. **Draft PR only — not merged.**

## Mandate

Quality over speed. Essays teach how microbiome and live-microbe *research* is built and limited. They must not read as structure/function copy, disease indications, kit-to-cart scripts, or dosing advice. `CLAIMS_GUARDRAILS.md` is the fence; hospital and drug rows stay described as regulation, not borrowed for aisle copy.

## Method

1. Read `CLAIMS_GUARDRAILS.md`, `README.md`, `INDEX.md`, `MANIFEST.md`, and `STYLE_GUIDE.md`.
2. Full-folder grep sweeps: brochure bans, disease-SKU dialect, psychobiotic/FMT/lean-microbe winks, second-person dose lines, and the word `landscape` in prose (folder path excepted).
3. Close read of high-risk drafts: 10 (AGA rows), 16 (GG / AAD synthesis), 33–34 (gut-brain / metabolic), 36–38 (NEC / FMT / DSHEA vs LBP), 31–32 (kits / uBiome), 40–44 (GRAS/NDI, COA, buyer file).
4. `python3 content/microbiome-supplements-landscape/qa/check_pack.py`
5. `python3 -m pytest tests/test_microbiome_supplements_landscape_pack.py -q`

## Narrative edits (claims / creep)

| Draft | Change | Rationale |
| --- | --- | --- |
| 40 | "genome you should have sequenced / before the photoshoot" → safety-file framing ("should include" / "should already be in the folder") | Removes second-person instruction that could read like QC advice adjacent to a SKU; aligns with distanced editor voice used in sibling packs. |

No other drafts required body cuts. Refusals, quoted disease language in disclaimers, and structure/function *shapes* taught as refused examples (drafts 10, 17, 38) were left intact.

## Furniture / tooling

- **`voice_check: edited`** on YAML for all forty-four drafts.
- **`INDEX.md`**, **`README.md`**, **`MANIFEST.md`**, **`STYLE_GUIDE.md`** — document `edited` as the post-editor gate.
- **`qa/check_pack.py`** — requires `voice_check: edited`; adds reader-dose and psychobiotic-treatment grep guards alongside existing disease-SKU and brochure bans.

## Voice

- Brochure-term grep on essay bodies: **clean** (no `delve`, `landscape`, `unlock`, `gut health journey`, etc.).
- Human voice retained: named papers, GRADE rows, statute shapes, uneven sentences.
- Second-person "you" remains where it is clearly meta (reading habits, red-pen exercises, founder desk checks) or points to clinicians (drafts 33, 34, 36).

## Verification

```
PACK QA
  drafts=44
  word_min=1004 (24-prebiotics-gibson-definition.md)
  word_max=1337 (02-metchnikoff-yogurt-what-he-did-not-prove.md)
  word_mean=1065
  slugs=44
PASS
```

## Residual watchlist (no change this pass)

Counsel and science/QA seats remain empty per `README.md`. Do not invent them on-site.

- **`[CITE NEEDED]` / `[VERIFY]` flags** (drafts 08, 10, 16, 21, 26, 28, 32, 34, 36, 39, 42): resolve from primary PDFs before any public promotion — not decoration.
- **Drafts 33–34, 36–37**: disease nouns appear only as refused teaching; monitor captions and pull-quotes on import.
- **Expand blocks** (`<!-- expand -->` in several wave-2/6 pieces): intentional density for editor staging; trim on WordPress import if a post runs long.

## Sign-off

| Field | Value |
| --- | --- |
| `voice_check` | `edited` (drafts 01–44) |
| `check_pack.py` | pass |
| `pytest` | pass |
| Merge | **no** — draft PR #438 only |
