---
title: Style Guide
series: American Arts and Crafts / Mission Furniture
status: staged
voice_check: edited
lane: bbf-furniture
---

# Style Guide

This series is a staged magazine history of **American Arts and Crafts and Mission furniture** for the BBF furniture lane. It is written for a reader who keeps *The Magazine Antiques*, *The Burlington Magazine*, *American Bungalow*, and the long Craftsman reprints — not for a reader who wants ten chairs that changed everything.

It is **not** a rewrite of the single survey chapter “Red House and the Honest Joint” in `content/furniture-history-ancient-blog/`. That chapter is English first and American in a paragraph. This series is American first. Morris, Ruskin, Eastlake, and the Cotswolds appear only as what the United States actually received: books, lectures, imported chairs, and shop talk.

## Voice

Write as a person who has stood in front of the object, or who has at least read the catalog entry, the shop number, and the magazine page. Prefer the particular: a McHugh brand, a Craftsman shop number, a Winterthur box, a Gamble dining-room chair, a *Craftsman* volume and month. Do not open with cosmic time. Do not close with a sermon.

Banned phrasing and habits:

- delve, landscape (as metaphor), robust, leverage, unlock, cutting-edge, game-changer
- tapestry, underscore, seamless, ever-evolving, elevate your space
- “In today’s rapidly…”
- “It’s important to note”
- stacked *Moreover* / *Furthermore*
- “Whether you’re a collector or a casual…”
- “In conclusion”
- throat-clearing first paragraphs
- symmetrical three-item filler (“X, Y, and Z”) used as a substitute for an argument
- fake omniscience: “scholars agree,” “everyone knows,” “the world was forever changed”
- COSMOS, AI, or internal process talk
- buy-buttons, SKU boxes, “shop the look,” affiliate asides, living-manufacturer catalog copy

Allowed: doubt, dealer myth versus museum note, a missing shop number, a later finish, a fumed surface that was later stripped. A claim without a source is marked `[CITE NEEDED]` or `[VERIFY]`. Invented workshop stories are not permitted.

## Openings

Start on an artifact, a dated shop, a room, a catalog page, or a magazine issue. Right:

- “The chair is branded under the front rail: *The McHugh Mission Furniture: Made in New York.*”
- “The first number of *The Craftsman* is dated October 1901.”
- “Harvey Ellis died in January 1904. The inlay chairs still carry his name.”

Wrong: “Since the dawn of time, Americans have wanted honest furniture.”

## Length and shape

Target **1,800–2,600 words** of body text (YAML and the `## Notes` / `## Figure plan` blocks do not count). A piece should have:

1. A concrete opening (object, shop, room, or text)
2. A middle that moves through making, selling, and argument — not a museum walk-through that never chooses
3. A close that leaves a residual fact or tension, not a recap

One essay, one problem. Adjacent chapters may overlap; they should not repeat the same paragraph in different clothes.

## Scholarship

Cite in running prose and in a short notes block: author, short title, year, and page, catalog number, or *Craftsman* issue when known. Prefer:

- shop catalogs and *The Craftsman*
- museum collection records (Met, Art Institute, LACMA, Dallas, Huntington, Gamble House, Cooper Hewitt, Winterthur)
- monographs (Cathers, Tucker, D’Ambrosio, Kaplan, Bosley, Makinson, Cunningham, Clark, Boris, Hewitt)

Popular price guides may appear as evidence of the collector market, not as the only source for 1901.

When a date, attribution, or “first” is contested, say so and name the parties. McHugh’s origin story and the Ellis inlay myth are contested on purpose.

## Figures

Every essay carries a captioned figure plan of **four to seven** images. Prefer Met Open Access (CC0), Smithsonian Open Access (CC0), Huntington / Gamble House pages (note rights), Wikimedia public-domain files whose source museum is named. Each figure needs: suggested filename, object title, museum and accession when known, date, material, license, alt text, and a one- or two-sentence magazine caption.

Full series documentation lives in `PHOTO_CAPTIONS.md`.

## Names and spelling

- **Arts and Crafts** (American movement); *Arts and Crafts* italic only for book titles.
- **Mission** is a trade name and a look, not a Spanish colonial workshop survival. Do not treat California mission sacristies as the source of the through-tenon.
- **Craftsman** is Stickley’s magazine, trademark, and house-plan brand. Do not use it as a synonym for every oak chair.
- Gustav Stickley (1858–1942); Leopold and John George Stickley; Albert Stickley; L. & J.G. Stickley; Stickley Brothers (Grand Rapids).
- *The Craftsman* (periodical, 1901–16). United Crafts (1901). Craftsman Workshops, Eastwood, N.Y.
- Quartersawn white oak (*Quercus alba*). Ammonia fuming. Through-tenon, keyed tenon, pinned tenon.
- Greene and Greene (Charles Sumner Greene, Henry Mather Greene). Gamble House, 1908–09.
- Roycroft, East Aurora; Elbert Hubbard; Dard Hunter.
- Charles Rohlfs, Buffalo.
- Charles P. Limbert, Grand Rapids and Holland, Michigan.
- Shop of the Crafters, Oscar Onken, Cincinnati.
- Byrdcliffe, Woodstock; Rose Valley, Pennsylvania.
- Joseph P. McHugh, The Popular Shop; Walter J. H. Dudley.
- A. J. Forbes chairs for the Swedenborgian Church, San Francisco (A. Page Brown, mid-1890s).

BCE/CE is not needed here. Use 1901, not “the turn of the century,” once a year is known.

## Brand and SEO (BBF lane)

This is **Website-GC staged copy** for the BBF furniture lane. SEO lives in the title, `meta_description`, `tags`, and in natural use of the words a reader actually types: Mission furniture, Arts and Crafts furniture, Craftsman oak, Stickley, quartersawn white oak, Morris chair, settle.

SEO does **not** live in a first paragraph that names every keyword. Do not write “Looking for authentic Mission furniture?” Do not append shop links. Bradley Brand Furniture, Arkansas hardwood, and any living manufacturer appear only in chapter 44, and then as **history of shops that still speak this language**, not as a catalog. Chapters 1–43 do not mention a living maker.

`status` remains `staged` until Keith clears publish. After editor QA, `voice_check: edited` on every file (see `EDITOR_REPORT.md`). `lane: bbf-furniture`.

## Front matter

Every essay file begins with:

```yaml
---
title: "..."
slug: ...
chapter: 01
series: American Arts and Crafts / Mission Furniture
status: staged
voice_check: edited
lane: bbf-furniture
period: ...
regions: ...
word_target: 1800-2600
figures: 5
meta_description: "..."
tags:
  - mission-furniture
  - arts-and-crafts
citations:
  - "Author, Title (Place: Publisher, year)."
---
```

`meta_description` is 140–165 characters, a magazine deck, not a marketing blurb.

## WordPress

Draft / staged only. See `WP_IMPORT.md`. Do not mark any essay `publish`.

## Editor pass

A separate editor will QA grammar, spelling, and style after this draft set. Do not clean the voice into brochure English. Keep the grain of a human sentence. After editor QA, set `voice_check: edited` on every file in this folder and add or update `EDITOR_REPORT.md` at the series root. The staging validator accepts `voice_check: human` (pre-editor) or `voice_check: edited` (post-editor).
