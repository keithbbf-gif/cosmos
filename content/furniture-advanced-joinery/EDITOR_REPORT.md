---
title: Editor report — Furniture Advanced Joinery
status: draft
voice_check: edited
series: furniture-advanced-joinery
editor_pass: 2026-09-14
pr: 320
---

# Editor report

Editor pass on `content/furniture-advanced-joinery/` for PR #320. Criteria: **shop case-study voice** (magazine case study per `STYLE_GUIDE.md` — open in the room, no pack-meta throat-clear), `voice_check: edited` on all series markdown.

## Scope

| Item | Count |
|------|------:|
| Draft articles (`drafts/*.md`) | 44 |
| Series files (INDEX, MANIFEST, STYLE_GUIDE, BIBLIOGRAPHY, PHOTO_CAPTIONS, PHOTO_MANIFEST, WP_IMPORT) | 7 |
| `[VERIFY]` markers (unchanged; intentional gaps) | retained per draft |

Word band 1,200–2,000: all 44 drafts remain in band (body total **65,934** words after this pass; net −6 from meta trims).

## Principles applied

1. **Shop case-study voice** — Ledes already opened on bench moments; editor work focused on second paragraphs that stepped out of the room (“this essay exists…”, “the brief asked for”, “this pack is…”).
2. **No meta sell** — Removed SEO-map and “pack” framing from article bodies; kept optional craft footnotes in front matter only.
3. **Cross-pack pointers** — Left intentional “craft pack already…” bridges where they orient the reader; cut only when the sentence was about the editorial project, not the joint.
4. **Banned phrasing** — Full-series scan: no hits on STYLE_GUIDE banned list in draft bodies (style guide list itself excluded).
5. **Mechanical** — Fixed figure caption grammar in `two-rows-of-teeth`; recounted `word_count` in front matter after edits.

## Substantive edits (drafts)

| Slug | Change |
|------|--------|
| `two-rows-of-teeth` | Figure caption: “It also the one” → “It is also the one” |
| `a-lamination-into-a-leg` | Replaced “This essay is the test” with shop judgment on mortise vs. laminated cheeks |
| `thirty-two-and-the-hole` | Cut pack/brief meta; kept grid-as-joint argument in first person |
| `a-cam-that-is-not-a-joint` | Cut “essay the brief asked for”; tightened knockdown honesty; removed “this pack” from sales-caption line |
| `iron-under-a-slab` | “This pack is joinery” → shop voice; D:\BBF pull note: SEO map → bench honesty on epoxy river |
| `a-confirmat-in-ply` | “Belongs next to the 32mm essay” → same-world shop paragraph without index talk |

## `voice_check`

All series `.md` under `content/furniture-advanced-joinery/`: `voice_check: human` → `voice_check: edited` (44 drafts + INDEX, MANIFEST, EDITOR_REPORT, and pack docs that carried the field).

## Not in this pass

- Photograph pulls from `D:\BBF` (figures remain `status: needed`).
- WordPress publish (`WP_IMPORT.md` still draft-only).
- Resolving `[VERIFY]` shop claims.
- Retelling basic craft-pack lessons (still deferred to `content/furniture-craft-blog/`).

## QA checklist

- [x] 44 slugs present; MANIFEST table matches front-matter `word_count`
- [x] `status: draft` on all articles
- [x] Shop case-study voice on knockdown/meta outliers (see table)
- [x] No new banned phrasing in bodies
- [x] `EDITOR_REPORT.md` added; INDEX/MANIFEST note editor pass

## See also

- `STYLE_GUIDE.md` — openings, banned language, front matter
- `MANIFEST.md` — per-slug word counts and topics
- `PHOTO_CAPTIONS.md` — staged figure copy
