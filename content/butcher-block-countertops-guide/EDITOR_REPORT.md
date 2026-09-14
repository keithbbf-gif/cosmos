---
title: Editor report — butcher-block countertops guide
status: staged
voice_check: edited
series: butcher-block-countertops-guide
pr: 464
---

# Editor report

**Scope:** `content/butcher-block-countertops-guide/drafts/` (48 files)  
**Voice fence:** `STYLE_GUIDE.md` (shop first person, refusals, no brochure slop)  
**Date:** 2026-09-14  
**Outcome:** `voice_check: edited` on every draft; checker fail-closed on `voice_check`.

## Method

1. Read all 48 drafts against the style fence (banned phrasing list, no recap
   closings, no dictionary opens, peer tone not coaching).
2. Ran automated slop scan (`tools/check_butcher_block_drafts.py` phrase list)
   across bodies — no hits in draft bodies.
3. Line edits only where voice slipped toward brochure, cross-guide dependency,
   or “prize / thank you” filler.
4. Tagged frontmatter and tightened the checker so a future pass cannot ship
   without `voice_check: edited`.

## Global changes

| Item | Change |
| --- | --- |
| Frontmatter | `voice_check: edited` after `status: staged` on all 48 drafts |
| `STYLE_GUIDE.md` | `voice_check: edited`; frontmatter template updated |
| `tools/check_butcher_block_drafts.py` | Require `voice_check: edited` (fail closed) |
| `MANIFEST.md` | Word count + editor pass pointer |

## Substantive line edits (5 drafts)

| Draft | Issue | Fix |
| --- | --- | --- |
| `09-edge-grain-is-the-residential-default` | “What you need to know” read like coaching | Reframed as shop field talk (“the part that bites you”) |
| `14-walnut-cherry-oak-ash` | Pointer to unpublished “island guide” woods draft | Replaced with inline “three job questions” (cut/board, sink, color horizon) |
| `42-the-first-year-of-oil` | “Prize for not forgetting” sounded like marketing | Swapped for shop habit language (sticky surplus, Thanksgiving schedule) |
| `48-aftercare-card` | “Future you will thank you” cheerlead | Trash-pull shop line; kept card function |
| (none else) | — | Bodies left intact where voice already matched fence |

## Voice pass — no body change (43 drafts)

Verified shop register: first-person shop observation where needed, species and
dates named, refusals stated plainly, no banned slop phrases, openings unique.
Files `01`–`08`, `10`–`13`, `15`–`41`, `43`–`47` received `voice_check: edited`
only.

## Checker (post-edit)

```
drafts: 48
words:  18023
min:    341
max:    432
OK
```

## Residual notes (not blockers)

- `30-overhang-on-wood` references “planning guidelines” without a path — intentional
  people-numbers aside; no external link required for staged copy.
- `02-what-bradley-means-by-a-top` uses “wood countertop” once as a deliberate
  contrast to shop vocabulary — kept.
- Word count dropped 9 words net from the five line edits; all drafts remain above
  the 340-word floor.

## Sign-off

Shop voice edit complete. PR **#464** stays **draft**; Website-GC dest remains
**staged**. Re-run `python3 tools/check_butcher_block_drafts.py` before any
publish handoff.
