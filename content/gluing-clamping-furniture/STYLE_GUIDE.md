# Style guide — Gluing & clamping furniture

This pack is **shop practice**, not joinery theory and not a catalog of bottles.
It sits **beside** `content/furniture-craft-blog/` and **below**
`content/furniture-advanced-joinery/`.

The craft pack already taught the hide pot (`the-pot-on-the-hot-plate`) and the
quiet after clamps (`clamps-then-quiet`). Do not retell those two essays. If
hide or a dry-run appears here, it appears because a *different* problem is on
the bench: a grade of PVA, a urea pot, a chair that racks under the fourth
clamp, a breadboard you glued too far, a smear that only shows under oil.

**Status:** staged writing. Every essay stays `status: staged`, `voice: human`.
Photo slots stay `needed` until a real file is pulled from `D:\BBF`. Soft brand
home is a 65×15 shop in rural South Arkansas — Warren, Wilmar, Bradley County —
usable later by Bradley Brand Furniture / Saline River Workshop. The writing
stands without the brand.

Read this file before editing. Sequence: `STAGE.md`. Slug list: `_manifest.toml`
and `INDEX.md`. Photos: `PHOTO_CAPTIONS.md`.

## What a piece is

A draft is a finished shop essay of **700–1,200 words**. It opens on a thing
you can hold or hear: a bottle that gelled in the truck, a caul that is still
crowned the wrong way, black rings from a pipe on wet cherry, a tenon that
pumped back out of a mortise. It earns one judgment about glue or clamp
practice. It is not a tips list and not a data-sheet paraphrase.

Each piece must be publishable alone. A reader who never sees the other forty
should still walk out knowing what to do next time, and what not to do.

## Five stages (do not blur them)

1. **choose** — name the glue and the clock. PVA grades, hide after the pot
   essay, urea, epoxy, polyurethane, CA, temperature, shelf life, creep.
2. **fit** — the rehearsal that is the glue-up. Cauls, pads, panels, cases,
   chairs, frames, breadboards, alignment helpers.
3. **spread** — how it goes on. Starved, drowned, cheeks vs puddles, end grain,
   squeeze-out, winter skin, August flash.
4. **press** — how it gets held. Pressure, clamp kinds, handscrews, bands,
   vacuum, the banana panel, the racked chair, two sessions.
5. **cure** — after the quiet. Unclamp vs machine, scrape, stain, split-don't-
   fill, mixed religions, humidity, fumes, the bench after.

A piece may touch two stages. It may not pretend a pocket-screw apron is a
glue lesson.

## Openings

Start in the room.

A bottle that will not pour. A caul with a smile. Glue that flashed on a
sun-hot rail. A clamp pad printed into pine. The smell of urea that is not
hide.

Do not start with a thesis about craft. Do not start with a question to “you.”
Do not start with “glue-up is…”

The first sentence names a thing you can hold or hear.

## Rhythm

Mix short and long. Opinion is welcome when it is paid for by description.
“A biscuit is a spline you hope nobody measures” is a judgment. “Clamping
matters” is not.

## Banned language (hard)

Do not use:

- delve, landscape (as metaphor), robust, leverage, unlock, cutting-edge,
  game-changer
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
- fake dualities (tradition vs innovation) unless the piece is actually about
  a real fork
- symmetrical list-filler (three parallel virtues, five “reasons,” seven
  “tips”)
- invented maker quotes
- invented customer quotes
- invented shop-floor dialogue attributed to named living people

If a living person is quoted, the quote must be sourced in `verify` or cut.

## Claims and [VERIFY]

Uncertain numbers — psi, open times, pot temperatures, bloom grams, mix
ratios, moisture targets — get `[VERIFY]` unless they are read off a sheet
in the shop that day. Do not invent a meter reading. Do not invent a
commission. Do not invent a filename in `D:\BBF`.

Place continuity is fair: oak, walnut, pecan, cherry, the Saline River timber
geography, a 65-foot shop with glass on the long wall. Corporate succession
is not. Bradley Brand Furniture, LLC is not claimed as the unbroken successor
of Fullerton’s Bradley Lumber Company.

Do not write as if a public bbfur catalog exists. Optional footnotes only.

## Brand, lightly

Optional footnotes only:

- https://bradleybrandfurniture.com/heritage
- https://bradleybrandfurniture.com/craft

No keyword stuffing. No “shop our collection.” Named series appear only when
the object in the room needs a name.

## Photos

Prefer Keith’s library: `D:\BBF\BBF Photos`, plus working-shop frames from the
same owner set. Caption every figure in the draft front matter **and** in
`PHOTO_CAPTIONS.md`.

- Credit only what is known. If the file has no photographer in metadata,
  write `photographer unnamed until file metadata is pulled`.
- Never invent a credit.
- Never invent a filename. Paths stay descriptive:
  `D:\BBF\BBF Photos — … (filename pending shop pull)`.
- Missing BBF frames stay `status: needed`. Do not substitute Unsplash or stock.

## Front matter (required)

```yaml
id: d01
title: string
slug: kebab-case
status: staged
stage: choose | fit | spread | press | cure
voice: human
voice_check: edited   # editor read-aloud pass; writer leaves this unset
cluster: glue | rehearsal | application | clamps | aftermath
series: gluing-clamping-furniture
dek: one or two sentences, no slogan
word_count: integer   # body copy only
topics: [list]
figures: list (id, preferred, caption, credit, license, status)
verify: list of claims still open
```

`status` stays `staged` in this pack. `voice: human` is a writer pass.
`voice_check: edited` is the magazine-floor editor stamp after read-aloud and
guardrail pass. Do not mark a piece `published` here.

## Figures

This pack is **photo-slot first**. Shop photographs from `D:\BBF` are the
figures. A `<!-- PHOTO: ... -->` comment may sit in the body where the frame
should land, matching the front-matter `id`. That is a pull instruction, not
a published image.

## Self-edit before `voice: human`

Read the piece aloud in the head. Kill:

1. Any banned word or throat-clear.
2. A paragraph that could sit in the craft pack with the names swapped.
3. A list that exists because lists look finished.
4. A closing that restates the dek.
5. A fake job you cannot stand behind — mark it `[VERIFY]` or cut it.

If the piece still feels like a briefing, it is not done.
