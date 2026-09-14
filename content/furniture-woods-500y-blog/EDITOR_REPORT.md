---
title: Editor report — Woods in Furniture, 1500–Present
status: draft
voice_check: edited
series: furniture-woods-500y
---

# Editor report

**Pass:** EDITOR (grammar, spelling, human voice, AI-habit ban)  
**Branch:** `cursor/furniture-woods-500y-editor-0c81` (stacked on writer `cursor/furniture-woods-500y-blog-23c0`)  
**Scope:** 46 canonical drafts in `drafts/` per `writer-slugs.json`  
**Date:** 2026-09-14  

## Summary

| Check | Result |
| --- | --- |
| Drafts edited | 46 / 46 |
| `voice_check: edited` in frontmatter | 46 / 46 |
| Figure embeds (`![…](../assets/…)`) preserved | 81 figures across 46 files; paths and captions unchanged |
| `[CITE NEEDED]` markers | 99 retained; no invented citations or numbers |
| Species+ / re-check notes | 33 mentions retained; no new Janka or CITES figures |
| STYLE_GUIDE banned phrases scan | No hits (delve, Moreover, Whether you're, In conclusion, landscape, robust, leverage, etc.) |
| Production comments in body | None (`staged embed`, `paste into drafts`) |

## Editorial method

1. Read against `STYLE_GUIDE.md` (American running text; historical trade terms unchanged: wainscot, deal, carcase, ébéniste).
2. Harmonized American spellings where the writer had mixed British forms: **molding** (was moulding), **mold** (was mould), **paneling**, **plowed**, **leveler**, **catalog** / **catalogs**.
3. Light voice pass: removed a repeated plantation-teak paragraph in `conservation-today`; capitalized **Gothic** where it names the style (`walnut-queen-anne`).
4. Did **not** rewrite ledes, add takeaway lists, or touch Sources / cross-link slugs unless fixing spelling inside a sentence.

## Per-slug notes

Slugs with **spelling harmonization** only (no other body edits): see script log in commit; includes `beech-bentwood-thonet`, `dutch-golden-age-shipping`, `ebony-inlay-keys`, `english-oak-great-furniture`, `mahogany-chippendale`, `mahogany-federal-america`, `plywood-and-core-stock`, `rosewood-gothic-revival`, `rosewood-victorian`, `veneer-versus-solid`, `walnut-queen-anne`, `workability-hand-tools`, and catalog/catalogs updates in the factory, CITES, and catalog-heavy chapters.

Slugs with **voice_check only** (prose already clean; metadata updated): remaining drafts including `intro-500-year-timber`, `glossary-grain-and-cut`, all CITES chapters, `janka-hardness-explained`, `moisture-wood-movement`, species hours (oak, walnut, mahogany, rosewood, teak, etc.), and technical chapters (`density-weight-shipping`, `flatsawn-panel-figure`, `rift-cut-flooring`, `veneer-versus-solid`, `workability-hand-tools`).

**Substantive voice edit:** `conservation-today` — merged duplicate plantation-teak / certified-*Swietenia* paragraph; kept permit disclaimer and all legal dates.

## Figures

Every draft retains at least one series figure block from `staged-embeds/` (relative paths `../assets/…`). Figure numbers in captions were not renumbered. No images added or removed.

## Not done (intentional)

- Species+ appendix status at publication (writer left explicit re-check notes, e.g. `padauk-modernist-accents`, `cedar-lining-chests`).
- Filling `[CITE NEEDED]` placeholders (editor does not invent port-book lines, APHIS case names, or factory manuals).
- `MANIFEST.md` word counts (unchanged; body edits are minor).

## Handoff

Writer branch content is unchanged except through this stacked editor PR. Merge writer first, then editor, or merge editor into writer for a single publication branch.
