---
title: Style Guide
series: American Bedroom Furniture
status: draft
voice_check: human
---

# Style Guide

This series is written for a reader who will stand in front of a Philadelphia high chest, a Stickley bed, or a factory suite and want to know what they are looking at. It is chronological and thematic. It is not “ten beds that changed everything,” and it is not a product grid.

Bradley Brand Furniture sits next to the later chapters the way a shop sits next to a mill town: as a place that still works hardwood, not as a sponsor. The writing stands without the brand.

## Voice

Write as a person who has opened a drawer, sighted a tester rail, or read the catalog entry and the shop bill. Prefer the particular: an accession number, a Grand Rapids plant, a patent year, a Fulton Street address, a kiln-dried oak from Bradley County. Do not open with cosmic time. Do not close with a sermon.

First person is allowed when it is a shop observation. It is not a diary.

Banned phrasing and habits:

- delve, landscape (as metaphor), robust, leverage, unlock, cutting-edge, game-changer
- “In today’s rapidly…” / “In an era of…”
- “It’s important to note”
- stacked *Moreover* / *Furthermore*
- “Whether you’re a collector or a casual…”
- “In conclusion” / “At the end of the day” / “The key takeaway”
- “Let’s dive in” / “This article will explore”
- throat-clearing first paragraphs
- symmetrical three-item filler used as a substitute for an argument
- fake omniscience: “scholars agree,” “everyone knows,” “the world was forever changed”
- COSMOS, AI, or internal process talk
- “rich tapestry,” “journey,” “elevate,” “empower,” “seamless,” “holistic,” “unpack”

Allowed: doubt, a contested attribution, a missing measurement, a later mattress that does not belong to the rails. A claim without a source is marked `[CITE NEEDED]`. Invented shop dialogue and invented customer quotes are not permitted.

## Openings

Start on an artifact, a dated workshop, a room, or a document.

Right:

- “Met 18.110.4 stands ninety-one and three-quarter inches in Gallery 752, mahogany over yellow pine, tulip poplar, and northern white cedar.”
- “The Craftsman Farms daughters’ beds never got a catalog number.”
- “Berkey & Gay’s 1876 Centennial chamber suites were a sales idea with carved posts.”

Wrong: “Since the dawn of time, humans have needed a place to sleep.”

## Length and shape

Target 1,800–2,800 words of body text (front matter, notes, and figure lists do not count). A piece should have:

1. A concrete opening (object, shop, factory, or text)
2. A middle that moves through making, use, and argument
3. A close that leaves a residual fact or tension, not a recap

One essay, one problem. Adjacent chapters may overlap; they should not repeat the same paragraph in different clothes.

## Scholarship

Cite in running prose or in a short notes block: author, short title, year, and page or catalog number when known. Prefer museum catalogs, shop bills, factory catalogs, and standard monographs (Downs, Heckscher, Hornor, Montgomery, Kenny, Cathers, Cooper, Ames, Grier, Anderson, Cooke). Popular surveys may appear as orientation, not as the only source.

When a date, attribution, or plant history is contested, say so and name the parties.

## Figures

Every essay carries a captioned figure plan of three to eight images. Prefer:

- Metropolitan Museum of Art Open Access (CC0)
- Smithsonian / Cooper Hewitt Open Access (CC0)
- Winterthur, MFA Boston, Yale, RISD, Philadelphia Museum — check current license
- Stickley Museum at Craftsman Farms collection pages
- Wikimedia Commons public-domain files whose source museum is named
- Keith’s shop library (`D:\BBF\BBF Photos`) only in late, BBF-adjacent chapters; credit only what is known

Each figure needs: object title, museum and accession when known, date, material, license, alt text, and a magazine caption.

Full series documentation lives in `PHOTO_CAPTIONS.md`.

## Brand (BBF-adjacent, not a catalog)

Chapters 1–35 do not mention Bradley Brand Furniture, Wilmar, or living product names. A soft bridge is reserved for chapters 36, 42, 43, and 45: Arkansas hardwood, Warren and Wilmar, Bradley County, the Saline bottoms, a shop that still names oak.

Rules carried from the craft pack:

- Bradley Brand Furniture, LLC is not claimed as the unbroken successor of Fullerton’s Bradley Lumber Company.
- Potlatch’s mid-century purchase and the 2008 furniture-company date stay marked `[CITE NEEDED]` unless a primary document is cited.
- Optional footnotes only: https://bradleybrandfurniture.com/heritage and https://bradleybrandfurniture.com/craft
- Named series (Lumberjack, RattleSnake, Saline Creek, Moro) appear only when the object in the room needs a name.
- No “shop our collection.” No buy-button language.

## Front matter

Every essay file begins with:

```yaml
---
title: ...
slug: ...
chapter: 01
series: American Bedroom Furniture
status: draft
voice_check: human
period: ...
regions: United States
word_target: 1800-2800
dek: one or two sentences, no slogan
figures: 3-8
---
```

## Staging and WordPress

Canonical working files live in `drafts/`. After the self-edit, the same essay is copied to `staged/` for WordPress **draft** import. See `WP_IMPORT.md` and `staged/STAGING.md`.

Do not mark any essay `publish`. `status` stays `draft`.

## Editor pass

A separate editor will QA grammar, spelling, and style after this draft set. Do not clean the voice into brochure English during that pass. Keep the grain of a human sentence.
