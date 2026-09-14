---
title: Editor Report — Furniture Finishing Chemistry
status: draft
voice_check: edited
series: furniture-finishing-chemistry
editor_branch: cursor/furniture-finishing-chemistry-editor-ea80
writer_branch: cursor/furniture-finishing-chemistry-adc2
writer_pr: https://github.com/keithbbf-gif/cosmos/pull/303
date: 2026-09-14
---

# Editor report

Editor pass on the writer pack in PR #303 (`cursor/furniture-finishing-chemistry-adc2`). This branch stacks on that branch; prose and front matter only — no assets or COSMOS core changes.

## Scope

| Area | Count |
|------|------:|
| Staged drafts (`01`–`45`) | 45 |
| Pack meta (`README.md`, `MANIFEST.md`) | 2 |
| **Total markdown in folder** | **48** |

All 45 numbered drafts now carry `voice_check: edited` in YAML front matter. `README.md` and `MANIFEST.md` remain `voice_check: human` (index/meta split).

## Method

1. Full read of the series against the shop-safe fence in `05-the-shop-safe-fence.md` and the README fence block — commercial products, ventilation/rags/waste, refusal language for distillation, home catalysts, methylene chloride how-to, and kitchen chemistry.
2. Automated scan for banned AI lexicon (delve, landscape-as-metaphor, Moreover/Furthermore stacks, “comprehensive guide,” “whether you're a beginner or a pro”) — **no hits** in draft bodies (README quotes those bans intentionally).
3. Line edit and grammar pass on all 45 drafts; fixed issues only where flagged.
4. **Hazmat creep audit:** searched for home formulation, solvent cocktails, still/distill instructions, and procedural stripper chemistry. Negation and “use as labeled” framing held; no new how-to added. Existing fence paragraphs in `03`, `11`, `12`, `14`, `19`, `23`, `28`, `31`, `37`, `39`, `42`, `43`, and `38` left intact.
5. **Cross-references:** internal “draft NN” pointers checked against `MANIFEST.md` — consistent.

## Notable edits

### Grammar / usage

- **04-why-some-woods-drink-and-some-spit:** “cut a offcut” → “cut an offcut”.

### Voice / meta

- No fourth-wall closers removed; intentional series voice (e.g. shellac title “That is the whole romance”) kept.
- **20-cuts-flakes-and-why-dewaxed-exists:** “shellac in a can can esterify” left as written (noun + verb, not a duplicate-word error).

### Front matter

- Added `voice_check: edited` to all 45 staged drafts (`voice: human` unchanged).
- Added `voice_check: human` to `README.md` and `MANIFEST.md`.

## Shop-safe fence (sign-off)

| Check | Result |
|-------|--------|
| Distill / synthesize / home drier or isocyanate mixing | Refused in fence + drafts; not introduced |
| Methylene chloride / lye / heat-gun strip how-to | Named as hazards or refused (`05`, `39`) |
| Commercial strip/bleach/coalescent products | “As labeled” / product-class only |
| Rag fire / ventilation / waste | Consistent with `05`, `41`, oil drafts |
| Food contact | Claims framed as cure + use (`42`); no kitchen recipes |

## Out of scope (by instruction)

- Fact-checking manufacturer claims or adding citations.
- Scheduling, WordPress import, or publish.
- Merging writer PR #303.

## Commits on this branch

Stacked editor commits (grammar/voice/`voice_check`/`EDITOR_REPORT.md`) on top of writer PR #303. See `git log cursor/furniture-finishing-chemistry-editor-ea80` for the list.

## Sign-off

- **Fence:** shop-safe boundary preserved; no hazmat how-to creep introduced.
- **Voice:** human shop register; README voice rules honored.
- **Coverage:** all 45 drafts `voice_check: edited`.
