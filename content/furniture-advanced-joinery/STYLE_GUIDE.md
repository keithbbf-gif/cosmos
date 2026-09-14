# Style guide — Advanced furniture joinery (case studies)

This pack sits **beyond** `content/furniture-craft-blog/`. That pack already taught the shoulder, the pin waste, the breadboard slot, the sliding dovetail on a square case, hide glue, and a chair that racks. Do not retell those lessons. If a basic joint appears here, it appears because the geometry got compound, the work got curved, or the piece has to come apart in a hallway.

**Status:** staged writing. Every essay stays `status: draft`. Photo slots stay `needed` until a real file is pulled from `D:\BBF`. Soft brand home is the same as the craft pack: a 65×15 shop in rural South Arkansas — Warren, Wilmar, Bradley County — usable later by Bradley Brand Furniture / Saline River Workshop / the mill-heritage story. The writing stands without the brand.

Read this file before editing. Slug list + counts: `MANIFEST.md`. Photos: `PHOTO_CAPTIONS.md`, `PHOTO_MANIFEST.md`, `PHOTO_NOTES.md`. Graphics: `GRAPHICS_INDEX.md`, `RIGHTS.md`, `SEO_MAP.md`. WordPress: `WP_IMPORT.md`.

## What a piece is

A draft is a finished magazine **case study** of **1,200–2,000 words**. It opens on a shop moment you can hold: a hopper side that will not stand square, a secret-miter dry-fit that still shows a hairline, a tusk tenon you can pull with two fingers, steam still in a crest rail. It earns one judgment about a **hard** joint. It is not a textbook chapter and not a tips list.

Each piece must be publishable alone. A reader who never sees the other forty should still walk out knowing how the joint is laid out, where it fails, and what the shop would do next time.

## Three clusters (do not blur them)

1. **Compound dovetails** — tails and pins that are not square to the box. Hoppers, cants, hex cases, bow fronts, secret miters, houndstooth, compound sliding sockets.
2. **Curved work** — the joint after the wood has been bent, laminated, coopered, brick-laid, kerfed, or scribed to a radius.
3. **Knocked-down systems** — the joint that is supposed to come apart. Tusk tenons, bed bolts, campaign hardware, barrel nuts, inserts, honest 32mm, and the hardware that is not a joint.

A piece may touch two clusters. It may not pretend a pocket-hole apron is advanced work.

## Openings

Start in the room.

A bevel gauge locked on a hopper side. Chalk on a secret-miter shoulder that still winks. A crest rail in a steam box, dripping. A bed rail hook that will not drop until you lift and slide. The smell of hide on a fox wedge you will never see again.

Do not start with a thesis about mastery, heritage, or “the maker.” Do not start with a question to “you.” Do not start with “advanced joinery is…”

The first sentence names a thing you can hold or hear.

## Rhythm

Mix short and long. Opinion is welcome when it is paid for by description. “A cam lock is a clamp you leave in the cabinet” is a judgment. “Quality matters” is not.

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
- invented customer quotes
- invented shop-floor dialogue attributed to named living people

If a living person is quoted, the quote must be sourced in `verify` or cut.

## Claims and [VERIFY]

Uncertain numbers, dates, moisture targets, bit angles, and shop-specific practices that have not been confirmed on the Wilmar or Warren floor get `[VERIFY]`. Do not invent a meter reading. Do not invent a commission that did not happen. Do not invent a filename in `D:\BBF`.

Place continuity is fair: hardwood, oak, walnut, pecan, the Saline River timber geography, a 65-foot shop with glass on the long wall. Corporate succession is not. Bradley Brand Furniture, LLC is not claimed as the unbroken successor of Fullerton’s Bradley Lumber Company.

Do not write as if a public bbfur catalog exists. Saline River Workshop is a shop name (Instagram / Etsy). Optional footnotes only.

## Brand, lightly

Optional footnotes only:

- https://bradleybrandfurniture.com/heritage
- https://bradleybrandfurniture.com/craft

No keyword stuffing. No “shop our collection.” Named series appear only when the object in the room needs a name.

## Photos

Prefer Keith’s library: `D:\BBF\BBF Photos`, plus working-shop and millwork frames from the same owner set. Caption every figure in the draft front matter **and** in `PHOTO_CAPTIONS.md`.

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
series: furniture-advanced-joinery
topic: compound-dovetails | curved-work | knockdown | hybrid
figures: list (id, preferred path or URL, caption, credit, license, status)
optional_links: footnote-only, or omit
verify: list of claims still open
```

`status` stays `draft` in this pack. `voice_check: human` until an editor pass. Do not mark a piece `ready` here.

## Figures

Each draft ships **four** `<figure>` blocks (IMAGE + SEO pass):

1. **Figure 1** — pack schematic: `assets/<slug>/joinery-diagram.svg` (`graphics[]` in front matter, class `faj-figure`).
2. **Figure 2** — museum or Commons plate where assigned (`faj-figure faj-museum`). Rights in `RIGHTS.md`.
3. **Photos 3–4** — shop slots from `D:\BBF` (`figures[]`, class `faj-figure faj-shop-pending` until a real file exists).

Keep `<img alt="…">`, `width`, `height`, `loading="lazy"`, and `<figcaption>` together. Alt-text rules: `SEO_MAP.md`. Do not paste stock art or invent SVG paths that are not in the tree. No AI-generated images.

Legacy `<!-- PHOTO: fig-0N … -->` comments were converted to figures; new shop pulls replace only the pending shop `<img>` src and `figures[].status`.

## WordPress

See `WP_IMPORT.md`. Import as **draft** posts only. Do not schedule.

## Self-edit before `voice_check: human`

Read the piece aloud in the head. Kill:

1. Any banned word or throat-clear.
2. A paragraph that could sit in the basic craft pack with the names swapped.
3. A list that exists because lists look finished.
4. A closing that restates the dek.
5. A fake job you cannot stand behind — mark it `[VERIFY]` or cut it.

If the piece still feels like a briefing, it is not done.
