# Style guide — living-room chests and storage history (BBF)

Staged educational essays for the BBF channel. Not a catalog. Not a showroom walk-through. Not a “ten chests that changed everything” list.

This pack is a history of **boxes that hold things in the room people sit in**. The living room is a late American name. The chest is older than the name, older than the parlor, older than the sofa. The job of the series is to teach a reader how to see a lid, a drawer, a lock, and a long low cabinet without being lied to by vocabulary.

## Voice

Shop-floor first person. A working custom shop that has built chests, credenzas, bookcases, and the odd trunk that wanted to be a coffee table. Educational. Human. Speak as someone who has hung a lid, fitted a till, and watched a client try to store a television in a piece that was born as a linen press.

Do not host-as-influencer. Do not close with a cart. Do not invent a named commission, a celebrity job, or a dollar figure this shop did not earn. When the industry pipe is the subject, say so. When it is our floor, say so. Public, checkable shop facts only (see `SHOP_GUARDRAILS.md`).

Write as a person who has stood in front of the object, or who has read the catalog entry and the shop drawing. Prefer the particular: a Met accession, a Lane serial read backwards, a Westminster dendro date, a High Point SKU year. Do not open with cosmic time. Do not close with a sermon.

## Banned phrasing and habits

- delve, landscape (as metaphor), robust, leverage, unlock, cutting-edge, game-changer, seamless, tapestry, underscore, ever-evolving
- “In today’s rapidly…” / “In an era of…”
- “It’s important to note”
- stacked *Moreover* / *Furthermore*
- “Whether you’re a collector or a casual…”
- “In conclusion” / “At the end of the day” / “The key takeaway”
- “Let’s dive in” / “This article will explore”
- “elevate your space”
- throat-clearing first paragraphs
- symmetrical three-item filler used as a substitute for an argument
- fake omniscience: “scholars agree,” “everyone knows,” “the world was forever changed”
- fake dualities (tradition vs innovation) unless the piece is actually about a real fork
- invented maker quotes, invented client quotes
- COSMOS, AI, or internal process talk
- SKU boxes, “shop the collection,” coupon closes

Allowed: doubt, a missing measurement, a replaced lid, a later stand that does not belong to the cabinet, two excavators who disagree. A claim without a source is marked `[VERIFY]`. Invented excavation stories are not permitted.

## Openings

Start on an artifact, a dated workshop, a room, a lock, or a document.

Right: “The Metropolitan’s Hadley chest-with-drawer (10.125.682) is oak and pine, 1690–1710, Connecticut River Valley, and the lid is the part that usually lies.”

Wrong: “Since the dawn of time, humans have needed a place to put their things.”

Do not start with a question to “you.” Do not start with a weather report of the industry.

## Length and shape

Target **1,100–1,700 words** of body text (YAML, disclaimer, notes, and figure lists do not count). A piece should have:

1. A concrete opening (object, site, shop, or text)
2. A middle that moves through making, use, and argument — not a museum walk-through that never chooses
3. A close that leaves a residual fact or tension, not a recap

One essay, one problem. Adjacent chapters may overlap; they should not repeat the same paragraph in different clothes. A reader who never sees the other forty should still get a complete argument.

## Scholarship

Cite in running prose and in the YAML `citations` array: author, short title, year, and page, catalog number, or accession when known. Prefer museum catalogs, monographs (Eames, Pickvance, Heckscher, Kirk, Clunas, Heineken, Koizumi), and dated trade reporting. Popular surveys may orient; they may not be the only source.

When a date, find-spot, or attribution is contested, say so and name the parties.

## Figures

Every essay carries a captioned figure plan of three to six images in a `## Figure plan` block. Prefer Met Open Access (CC0), Smithsonian Open Access (CC0), V&A / British Museum pages with the live license named, and Wikimedia files whose source museum is named. Keith’s shop photographs (`D:\BBF\BBF Photos`) may be suggested for making-shots; do not invent a credit.

Each figure needs: suggested filename, object title, museum and accession when known, date, material, license, alt text, and a one- or two-sentence caption.

## Names and spelling

Use the form current in the holding institution’s catalog, then give a common alternative once if needed: *cassone*; *bandaji*; *isho-dansu*; *kas* / *kast*; commode. Place names: Çatalhöyük, Altavista, Wethersfield, Sendai, Ferdinand.

BCE/CE for ancient dates. Do not write “BC/AD” unless quoting.

## Brand

This is BBF channel copy sitting in the repo so the drafts have a git home. It is not a Keith Fritz Fine Furniture brand film and not a Bradley Brand Furniture catalog. Do not fuse an Indiana custom shop with an Arkansas mill letterhead. Soft place-continuity is fair: hardwood, a bench, a lid that binds in August. Named living series and SKUs stay out unless the object in the room needs a historical name (Lane, Stickley, Eames ESU).

No product language. A last chapter may stand in a shop and talk about what a living-room chest is *for* now. That is still history of use, not a price list.

## Adjacent packs — do not steal

Other writers own liquor cabinets/built-ins, desks/entryway, bunk/youth, dining tables, Arts & Crafts as a deep series, and healthcare casework. This pack may *touch* a cellarette, a secretary, or a Stickley sideboard when the living-room storage argument needs them. It may not become those series.

## Front matter

Every draft begins with:

```yaml
---
id: lrcs-01
title: ...
slug: kebab-case
stage: 00-frame | 01-ancient-medieval | 02-marriage-travel | 03-drawers | 04-cupboards | 05-asia | 06-modern | 07-shop
status: staged
voice: shop-floor-first-person
form: essay
channel: BBF
voice_check: human
standalone: true
educational_claim: one sentence the piece must teach
word_target: 1100-1700
era_focus: ...
citations:
  - "Author, Title (Place, year), pages or accession."
verify: []
topics: [chests, living-room, ...]
---
```

`status` stays **`staged`**. Keith holds the publish pen. Do not mark `publish` or `aired`.

## WordPress

Draft-only staging. See `WP_IMPORT.md`.

## Self-edit before `voice_check: human`

Read the piece aloud in the head. Kill:

1. Any banned word or throat-clear.
2. A paragraph that could sit in any other essay with the names swapped.
3. A list that exists because lists look finished.
4. A closing that restates the dek.

If the piece still feels like a briefing, it is not done.
