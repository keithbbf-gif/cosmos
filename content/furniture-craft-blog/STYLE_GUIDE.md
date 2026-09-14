# Style Guide — Furniture Craft Blog Pack

**Status:** working house rules for this folder only.  
**Voice check:** every draft ships `voice_check: human` only after a pass that kills the banned list.

This pack is magazine writing for people who already take furniture seriously, and for readers who want to. It is not a DIY funnel, not a product grid, and not a keyword farm. Soft brand home is Arkansas hardwood country — Warren and Wilmar, Bradley County — usable later by Bradley Brand Furniture, Saline River Workshop, or the mill-heritage story. The writing stands without the brand. The brand, if it appears, is a place and a shop, not a slogan.

## What a piece is

A draft is a finished magazine essay of **1,200–2,000 words**. It opens on a shop moment, a tool, a joint, or a documented practice. It earns one judgment. It does not try to be a textbook chapter with a lede glued on.

Each piece must be publishable alone. A reader who never sees the other forty should still get a complete argument and a picture they can walk into.

## Openings

Start in the room.

A proud tenon cheek. Chalk on a shoulder. Steam still coming off a bent slat. Raking light on 80-grit swirls someone hoped 180 would hide. The glue pot ticking on a hot plate.

Do not start with a thesis about craft, heritage, or “the maker.” Do not start with a weather report of the industry. Do not start with a question to “you.”

The first sentence names a thing you can hold or hear.

## Rhythm

Mix short and long. A three-word sentence is allowed if the next one has to carry weight. Cut the sentence that only restates the last one. Cut the paragraph that exists to be the third item in a set of three.

Opinion is welcome when it is paid for by description. “Dowels are fine in a cabinet side; they are a gamble in a chair rail” is a judgment. “Joinery matters” is not.

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
- fake dualities (tradition vs innovation, art vs science) unless the piece is actually about a real fork in the work
- symmetrical list-filler (three parallel virtues, five “reasons,” seven “tips”)
- invented maker quotes
- invented customer quotes
- invented shop-floor dialogue attributed to named living people

If a living person is quoted, the quote must be sourced in `verify` or cut.

## Claims and [VERIFY]

Uncertain numbers, dates, moisture targets, historical employment figures, and shop-specific practices that have not been confirmed on the Wilmar or Warren floor get `[VERIFY]`. Do not invent a meter reading. Do not invent a kiln schedule. Do not invent a family employment story.

Place continuity is fair: hardwood, oak, furniture stock, the Saline River timber geography. Corporate succession is not. Bradley Brand Furniture, LLC is not claimed here as the unbroken successor of Fullerton’s Bradley Lumber Company. Potlatch’s mid-century purchase and the 2008 furniture-company date stay marked unless a later editor cites a primary document.

## Brand, lightly

Optional footnotes only:

- https://bradleybrandfurniture.com/heritage
- https://bradleybrandfurniture.com/craft

No keyword stuffing. No “shop our collection.” Named series (Lumberjack, RattleSnake, Saline Creek, Moro) appear only when the object in the room needs a name. Saline River Workshop is a geographic echo, not a masthead in every piece.

## Photos

Prefer Keith’s library: `D:\BBF\BBF Photos`, plus working-shop and millwork frames from the same owner set. Caption every figure in the draft front matter **and** in `PHOTO_CAPTIONS.md`.

- Credit only what is known. If the file has no photographer in metadata, write `photographer unnamed until file metadata is pulled`.
- Never invent a credit.
- Public-domain or historical images require a license line and a live URL.
- Postcard and commercial-archive images (Curt Teich, mid-century plant cards) need rights confirmation before any public use — mark them `[VERIFY rights]`.

## Front matter (required)

```yaml
title: string
slug: kebab-case
status: draft
voice_check: human
word_count: integer   # body copy only, counted after the last self-edit
dek: one or two sentences, no slogan
series: furniture-craft
topic: joinery | tools | finish | materials | millwork | shop | culture | repair
figures: list (id, preferred path or URL, caption, credit, license, status)
optional_links: footnote-only, or omit
verify: list of claims still open
```

`status` stays `draft` in this pack. An editor agent will QA grammar and style after drafting. Do not mark a piece `ready` here.

## Figures (diagrams + photos)

- **Diagrams** are cream/ink SVG in `assets/<asset-slug>/`. Each draft embeds one or two `<figure class="craft-figure">` blocks after the opening graf(s), before the first `##` section. Captions come from the graphics pack; do not swap in stock art.
- **`graphics` in front matter** lists the asset slug(s) and paths for importers. **`figures`** lists **shop photo** slots only — paths under `D:\BBF`, staged and credited before publish. Missing BBF frames stay `status: needed`; do not substitute Unsplash.
- Regenerate SVGs: `python3 tools/generate_furniture_craft_blog_graphics.py`. Re-apply prose↔asset mapping: `python3 tools/merge_furniture_craft_blog_pack.py` (see `GRAPHIC_MAP.yaml`).

## WordPress

See `WP_IMPORT.md`. Import as **draft** posts only. Do not schedule. Do not set a public publish date in this pack.

## Self-edit before `voice_check: human`

Read the piece aloud in the head. Kill:

1. Any banned word or throat-clear.
2. A paragraph that could sit in any other essay with the names swapped.
3. A list that exists because lists look finished.
4. A closing that restates the dek.

If the piece still feels like a briefing, it is not done.
