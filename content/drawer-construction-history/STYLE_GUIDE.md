# Style guide — Drawer construction history

This pack sits **beside** `content/furniture-craft-blog/` and `content/furniture-advanced-joinery/`. The craft pack already has a seasonal-bind essay (`the-drawer-that-does-not-bind`). The advanced pack already has a bow-front dovetail case study (`a-drawer-that-bows`). Do not retell those. If bind or a curve appears here, it appears because the **history** of the box, the runner, or the trade practice is the argument.

**Status:** staged writing. Every essay stays `status: draft`. Photo slots stay `needed` until a real file is pulled from `D:\BBF`. Soft brand home is a 65×15 shop in rural South Arkansas — Warren, Wilmar, Bradley County — usable later by Bradley Brand Furniture / Saline River Workshop / the mill-heritage story. The writing stands without the brand.

Read this file before editing. Slug list + counts: `MANIFEST.md`. Photos: `PHOTO_CAPTIONS.md`, `PHOTO_MANIFEST.md`. WordPress: `WP_IMPORT.md`.

## What a piece is

A draft is a finished magazine essay of **1,200–2,000 words**. It opens on a shop moment you can hold: a mule-chest till that still wants a lid, a Knapp scallop you can date with a thumbnail, a slip that widened the wear, a back that is allowed to be pine. It earns one judgment about **how drawers were made, and how a shop still makes them**. It is not a textbook chapter and not a tips list.

Each piece must be publishable alone. A reader who never sees the other forty should still walk out knowing what the joint is, when it showed up (with hedges), where it fails, and what this shop would do next time.

History is earned. A date without a source is a green log. Mark it `[VERIFY]` or cut it. Shop practice is allowed to argue with the museum — say which is which.

## Four clusters (do not blur them)

1. **Dating and trade** — mule chests, side-hung grooves, London piecework, Knapp, machine dovetails, factory clocks.
2. **The box** — half-blind fronts, tails on the sides, slips vs grooves, bottoms, backs, secondary wood, thickness.
3. **The case and the fit** — web frames, dustboards, kickers, runners, stops, plane-to-opening, rack, wax.
4. **Traditions and hardware** — Shaker, Federal, Arts & Crafts, campaign, tansu, kitchen slides, locks, pulls, lips.

A piece may touch two clusters. It may not pretend a pocket-screwed false front is period work.

## Openings

Start in the room.

A groove in a 17th-century side that still rides a runner. Chalk on a half-blind socket. A Knapp cove you can feel with a thumbnail. Hide glue on a slip. The smell of paraffin on a worn oak runner.

Do not start with a thesis about heritage or “the maker.” Do not start with a question to “you.” Do not start with “drawers have a long history…”

The first sentence names a thing you can hold or hear.

## Rhythm

Mix short and long. Opinion is welcome when it is paid for by description. “Tails live on the sides because the pull lives on the front” is a judgment. “Quality matters” is not.

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

Uncertain numbers, dates, patent numbers used as dating clocks, moisture targets, and shop-specific practices that have not been confirmed on the Wilmar or Warren floor get `[VERIFY]`. Do not invent a meter reading. Do not invent a commission that did not happen. Do not invent a filename in `D:\BBF`.

Do not flatten chronology. English slips, American grooves, Hayward’s 19th-century slip moulding, and the 1788 London Book of Prices line for “slipping drawers” are related, not identical. Say which witness you are standing on.

Place continuity is fair: hardwood, oak, walnut, pecan, pine, poplar, the Saline River timber geography, a 65-foot shop with glass on the long wall. Corporate succession is not. Bradley Brand Furniture, LLC is not claimed as the unbroken successor of Fullerton’s Bradley Lumber Company.

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
- Historical / public-domain images require a live URL and a license line. Postcard and commercial-archive images need `[VERIFY rights]` before any public use.

## Front matter (required)

```yaml
title: string
slug: kebab-case
status: draft
voice_check: human
word_count: integer   # body copy only, counted after the last self-edit
dek: one or two sentences, no slogan
series: drawer-construction-history
topic: dating-trade | the-box | case-and-fit | tradition-hardware
figures: list (id, preferred path or URL, caption, credit, license, status)
optional_links: footnote-only, or omit
verify: list of claims still open
```

`status` stays `draft` in this pack. `voice_check: human` until an editor pass. Do not mark a piece `ready` here.

## Figures

This pack is **photo-slot first**. Shop photographs from `D:\BBF` are the figures. A period photograph may be slotted only with a real URL and a license. Diagrams may be added later; do not paste stock art.

A `<!-- PHOTO: ... -->` HTML comment may sit in the body where the frame should land, matching the front-matter `id`. That is a pull instruction, not a published image.

## WordPress

See `WP_IMPORT.md`. Import as **draft** posts only. Do not schedule.

## Sibling packs — do not retell

- `content/furniture-craft-blog/drafts/06-the-drawer-that-does-not-bind.md` — seasonal clearance, feeler stick, June bind.
- `content/furniture-advanced-joinery/drafts/04-a-drawer-that-bows.md` — bow-front half-blinds on a curve.

This pack owns **history of the sliding box** and the ordinary shop practices that history left on the bench.

## Self-edit before `voice_check: human`

Read the piece aloud in the head. Kill:

1. Any banned word or throat-clear.
2. A paragraph that could sit in the craft pack or the advanced pack with the names swapped.
3. A list that exists because lists look finished.
4. A closing that restates the dek.
5. A fake date, patent, or job you cannot stand behind — mark it `[VERIFY]` or cut it.

If the piece still feels like a briefing, it is not done.
