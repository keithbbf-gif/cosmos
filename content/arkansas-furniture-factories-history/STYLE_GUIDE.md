# Style guide — Arkansas furniture factories history

This pack is **staged writing** for Bradley Brand Furniture SEO: Fort Smith and statewide Arkansas furniture-factory history. It is not a shop-joinery pack and not a species pack. Do not retell `content/arkansas-southern-woods-species/` (oak in the factories, gum vs pine) except where a factory essay needs one honest wood sentence. Do not retell `content/furniture-advanced-joinery/` or the craft blog.

**Status:** staged. Every essay stays `status: draft`. Photo slots stay `needed` until a real file is pulled from `D:\BBF` or a rights-cleared archive. Soft brand home is a 65×15 shop in rural South Arkansas — Warren, Wilmar, Bradley County — usable later by Bradley Brand Furniture / Saline River Workshop / the mill-heritage story. The writing stands without the brand.

Read this file before editing. Slug list + counts: `MANIFEST.md`. Photos: `PHOTO_CAPTIONS.md`, `PHOTO_MANIFEST.md`. WordPress: `WP_IMPORT.md`. Sources: `BIBLIOGRAPHY.md`.

## What a piece is

A draft is a finished magazine **history essay** of **1,200–2,000 words**. It opens on a thing you can see: a wagon wheel on Garrison, a labeled drawer in a museum case, a riverfront brick wall after the 1996 tornado, a 1912 table of board feet. It earns one judgment about a factory, a town, or a supply line. It is not a timeline dump and not a tips list.

Each piece must be publishable alone. A reader who never sees the other forty should still walk out knowing what happened, what the evidence is, and why the factory mattered.

Ken Burns tone is **optional**, not required. When it is used, it is documentary: a still frame, a named street, weather, a ledger number. It is not purple. It does not invent a narrator walking through fog with a cello.

## Seven clusters (do not blur them)

1. **Origins** — wagons, Gold Rush outfitting, Civil War diversion, Indiana machinery, Ballman before the merger.
2. **Fort Smith companies** — specialized houses Ballman founded or the row named by the museum: folding beds, couch and bedding, Border Queen, metal products, the 1921 cooperative, Fort Smith Chair / Ayers, the Pratt partnership cases.
3. **Riverside** — Udouj, Twin Rivers, Arkansas Best, the peak, the tornado rebuild, the later move from factory to design/distribution.
4. **Wood and rail** — 1912 Harris–Maxwell numbers, gum and oak, coal/steam/gas, freight, boxes and spinoffs, glass town beside furniture town.
5. **Labor and civic** — who stood at the machines, women on finish lines, unions, Ballman School, the museum.
6. **Statewide** — Harrison church furniture, St. Joe, Petit Jean lecterns, Warren furniture stock (not a succession), pine-belt mills, Monticello hospitality, the folding trade that stayed.
7. **Afterlife** — April 21 1996, import competition, Whirlpool after furniture, what Arkansas still makes.

A piece may touch two clusters. It may not pretend Bradley Brand Furniture, LLC is the unbroken successor of Fullerton’s Bradley Lumber Company.

## Openings

Start in the room, the street, or the photograph.

A stencil on the back of a dresser. Riverfront brick with the windows gone. A Forest Service table from 1912 with red gum in the first row. A Sunday-night tornado warning that arrived after the shift had already gone home.

Do not start with a thesis about heritage, “the maker,” or “Arkansas pride.” Do not start with a question to “you.” Do not start with “Fort Smith was once…” unless the next clause is a fact that earns the once.

The first sentence names a thing you can hold, hear, or see in a still frame.

## Rhythm

Mix short and long. Opinion is welcome when it is paid for by a date, a court record, a board-foot table, or a named building. “Furniture row was a shipping argument that looked like a skyline” is a judgment. “Quality matters” is not.

## Banned language (hard)

Do not use:

- delve, landscape (as metaphor), robust, leverage, unlock, cutting-edge, game-changer
- “In today’s…” / “In an era of…”
- “It’s important to note”
- Moreover / Furthermore stacks
- “Whether you’re a beginner or a pro…”
- “In conclusion”
- “At the end of the day”
- “Not only… but also…” as a tic
- “The key takeaway”
- “Let’s dive in”
- “This article will explore”
- throat-clearing first paragraphs
- fake dualities (tradition vs innovation) unless the piece is actually about a real fork
- symmetrical list-filler (three parallel virtues, five “reasons,” seven “tips”)
- invented maker quotes
- invented worker quotes
- invented customer quotes
- invented shop-floor dialogue attributed to named living people
- “Ken Burns” as a self-description in the body

If a living or recently living person is quoted, the quote must be sourced in `verify` or cut. Higgins, Girard, Spradlin, and encyclopedia authors may be paraphrased with the source named; do not tighten their speech into a prettier sentence and call it a quote.

## Claims and [VERIFY]

Uncertain numbers, founding years, employment counts, and building addresses that have not been confirmed in a cited source get `[VERIFY]`. Do not invent a plant square footage. Do not invent a payroll. Do not invent a filename in `D:\BBF`.

Place continuity is fair: Fort Smith riverfront, Garrison Avenue, Warren–Wilmar timber geography, a 65-foot shop with glass on the long wall. Corporate succession is not.

Do not write as if a public bbfur catalog exists. Saline River Workshop is a shop name (Instagram / Etsy). Optional footnotes only.

The 1912 Harris–Maxwell bulletin is the closest honest statewide wood snapshot. Do not update those percentages into a modern claim.

## Brand, lightly

Optional footnotes only:

- https://bradleybrandfurniture.com/heritage
- https://bradleybrandfurniture.com/craft

No keyword stuffing. No “shop our collection.” Named BBF series (Moro, Caney Creek, Little Red River, Shiloh) appear only when a kitchen-cabinet or butcher-block sentence actually needs a present-tense shop object — and then only as optional, never as the lede.

Bradley Brand Furniture, LLC (Warren, 501 Pennington; organized 2008 in public listings) is a later South Arkansas shop. It is not Ballman-Cummings. It is not Riverside. It is not Bradley Lumber Company of Arkansas.

## Photos

Prefer Keith’s library: `D:\BBF\BBF Photos`, plus working-shop, mill, and any owner-held Fort Smith / Warren documentary frames. Caption every figure in the draft front matter **and** in `PHOTO_CAPTIONS.md`.

Archive photographs from the Fort Smith Museum of History, Fort Smith Historical Society, NWS, Encyclopedia of Arkansas, or newspapers need **rights**. Do not paste those files. A `preferred` slot may name the *kind* of frame (Garrison after the fire, Riverfront brick, a Border Queen cabinet) and stay `needed`.

- Credit only what is known. If the file has no photographer in metadata, write `photographer unnamed until file metadata is pulled`.
- Never invent a credit.
- Never invent a filename. Paths stay descriptive: `D:\BBF\BBF Photos — … (filename pending shop pull)`.
- Missing BBF frames stay `status: needed`. Do not substitute Unsplash or stock.

## Front matter (required)

```yaml
title: string
slug: kebab-case
status: draft
voice_check: human | edited
word_count: integer   # body copy only, counted after the last self-edit
dek: one or two sentences, no slogan
series: arkansas-furniture-factories-history
topic: origins | fort-smith-companies | riverside | wood-and-rail | labor-civic | statewide | afterlife
figures: list (id, preferred path or URL, caption, credit, license, status)
optional_links: footnote-only, or omit
verify: list of claims still open
```

`status` stays `draft` in this pack. `voice_check: human` until an editor pass. Do not mark a piece `ready` here.

## Figures

This pack is **photo-slot first**. Shop and documentary photographs from `D:\BBF` are the default figures. A `<!-- PHOTO: ... -->` HTML comment may sit in the body where the frame should land, matching the front-matter `id`. That is a pull instruction, not a published image.

## WordPress

See `WP_IMPORT.md`. Import as **draft** posts only. Do not schedule.

## Self-edit before `voice_check: human`

Read the piece aloud in the head. Kill:

1. Any banned word or throat-clear.
2. A paragraph that could sit in the woods pack or the joinery pack with the names swapped.
3. A list that exists because lists look finished.
4. A closing that restates the dek.
5. A factory fact you cannot stand behind — mark it `[VERIFY]` or cut it.
6. A sentence that treats “Arkansas-made” as a mood instead of a mill, a rail car, or a payroll.

If the piece still feels like a briefing, it is not done.
