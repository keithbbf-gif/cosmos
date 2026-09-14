# Style Guide — Veneer History & Shop Practice

**Status:** working house rules for this folder only.  
**Voice check:** every draft ships `voice_check: human` only after a pass that kills the banned list.

This pack is magazine writing for people who already take furniture seriously, and for readers who want to. It is history that has to survive a shop, and shop practice that has to survive a historian. It is not a DIY funnel, not a product grid, and not a keyword farm.

Soft brand home is Arkansas hardwood country — Warren and Wilmar, Bradley County — usable later by Bradley Brand Furniture, Saline River Workshop, or the mill-heritage story. The writing stands without the brand. The brand, if it appears, is a place and a shop, not a slogan.

## What a piece is

A draft is a finished magazine essay of **1,200–2,000 words**. It opens on a shop moment, a leaf, a documented object, or a documented practice. It earns one judgment. It does not try to be a textbook chapter with a lede glued on.

Each piece must be publishable alone. A reader who never sees the other forty should still get a complete argument and a picture they can walk into.

The folder is also a **syllabus**. Drafts are numbered and staged so you can read foundation → history → machines → matching → glue → repair. Jump a stage only if you already know why the last one failed on the bench.

## Openings

Start in the room, or start on a named object.

A leaf that crackles when you unroll it. Hide glue on a hammer face. A museum accession you can look up. Sequence numbers stamped on the back of a flitch. A pale wound where someone sanded into the core.

Do not start with a thesis about craft, heritage, or “the maker.” Do not start with a weather report of the industry. Do not start with a question to “you.”

The first sentence names a thing you can hold, hear, or look up.

## Rhythm

Mix short and long. A three-word sentence is allowed if the next one has to carry weight. Cut the sentence that only restates the last one. Cut the paragraph that exists to be the third item in a set of three.

Opinion is welcome when it is paid for by description. “Rotary birch is a useful core face; it is a bad dining-table story” is a judgment. “Veneer matters” is not.

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

Uncertain numbers, dates, moisture targets, museum accession details that have not been re-checked against the current catalog, and shop-specific practices that have not been confirmed on the Wilmar or Warren floor get `[VERIFY]`. Do not invent a meter reading. Do not invent a kiln schedule. Do not invent a family employment story. Do not invent a slicer in a mill that may only have sawn lumber.

Place continuity is fair: hardwood, oak, furniture stock, the Saline River timber geography. Corporate succession is not. Bradley Brand Furniture, LLC is not claimed here as the unbroken successor of Fullerton’s Bradley Lumber Company. Potlatch’s mid-century purchase and the 2008 furniture-company date stay marked unless a later editor cites a primary document.

Historical objects may be named with collection and accession when the catalog is public. If the accession or date is remembered rather than re-read, mark `[VERIFY]`.

CITES, endangered species, and trade bans are legal facts. Do not write a workaround. Do not name a substitute as “the same wood.”

## Brand, lightly

Optional footnotes only:

- https://bradleybrandfurniture.com/heritage
- https://bradleybrandfurniture.com/craft

No keyword stuffing. No “shop our collection.” Named series appear only when the object in the room needs a name. Saline River Workshop is a geographic echo, not a masthead in every piece.

## Photos

Prefer Keith’s library: `D:\BBF\BBF Photos`, plus working-shop and millwork frames from the same owner set. Caption every figure in the draft front matter **and** in `PHOTO_CAPTIONS.md`.

- Credit only what is known. If the file has no photographer in metadata, write `photographer unnamed until file metadata is pulled`.
- Never invent a credit.
- Public-domain or historical images require a license line and a live URL.
- Postcard and commercial-archive images need rights confirmation before any public use — mark them `[VERIFY rights]`.
- Museum collection images: use the museum’s stated license, or mark `needed` and leave the file out of the repo.

This writer pack does **not** embed SVG diagrams or download Commons files. An images agent can add those later without rewriting the prose.

## Front matter (required)

```yaml
title: string
slug: kebab-case
status: draft
voice_check: human
word_count: integer   # body copy only, counted after the last self-edit
dek: one or two sentences, no slogan
series: veneer-history-practice
stage: integer
stage_name: foundation | ancient | cabinet | machines | matching | shop | repair
order: integer
topic: history | practice | materials | shop | repair | culture | tools
figures: list (id, preferred path or URL, caption, credit, license, status)
optional_links: footnote-only, or omit
verify: list of claims still open
```

`status` stays `draft` in this pack. An editor agent will QA grammar and style after drafting. Do not mark a piece `ready` here.

## WordPress

See `WP_IMPORT.md`. Import as **draft** posts only. Do not schedule. Do not set a public publish date in this pack.

## Self-edit before `voice_check: human`

Read the piece aloud in the head. Kill:

1. Any banned word or throat-clear.
2. A paragraph that could sit in any other essay with the names swapped.
3. A list that exists because lists look finished.
4. A closing that restates the dek.
5. A history paragraph that names no object, no shop, and no consequence.

If the piece still feels like a briefing, it is not done.

## Overlap with other packs

`content/furniture-craft-blog/drafts/33-a-skin-of-better-wood.md` already told the short shop truth: veneer is not a confession. This pack does not reprint that essay. It goes into the history, the flitch, the glue, and the repair that essay only pointed at.

Finishing chemistry lives in `content/furniture-finishing-chemistry/`. This pack talks about finish only where a leaf changes the job (sand-through, grain raise into the core, reversible hide). It does not become a second finish syllabus.
