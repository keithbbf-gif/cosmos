---
title: Style Guide — Dining Chairs, History and Sitting
status: draft
voice_check: edited
series: dining-chairs-history-design
---

# Style Guide

This series talks to people who sit at dinner, buy chairs, restore them, or draw them next to a table that already exists. Bradley Brand works Arkansas hardwoods. The series teaches how dining chairs were made and how they fit a body at a meal. It does not sell a line.

Sibling pack: `content/american-dining-room-history/` owns the room, the table, and the splat-to-ladder survey. This pack owns the chair as a sitting machine and as a history of forms. Do not rewrite `dining-chairs-splat-to-ladder`, `hitchcock-fancy-chairs`, `midcentury-eames-saarinen`, or `ikea-flatpack-table`. Cross-link them. Do not steal their ledes.

## Voice

Magazine voice, not catalog voice. Write as a person who has sat through a long dinner in a hard chair and then gone under the table to look at the rail. Prefer names, dates, museum objects, pattern-book plates, and measured inches over general claims. A sentence may be short. A sentence may run if it is carrying a fact.

First person is allowed when it is a shop or room observation. It is not a diary.

Speak to the reader as a peer. Do not coach. Do not cheerlead. Do not close with a moral.

## What a piece is

A draft is a finished magazine essay of **1,400–2,200 words** of body copy. Front matter, Sources, and See also do not count. It opens on a chair, a seat, a gap, a failure, or a documented object. It earns one judgment. It is publishable alone.

## Openings

Start in the room or on the chair.

A front rail that hits a thigh. A saber leg that takes a coat. Rush that has gone slack under a Sunday roast. A klismos on a vase that no surviving wood can match. Eighteen inches to the finished floor and a table that was sold as thirty.

Do not start with a thesis about comfort, heritage, or “the dining experience.” Do not start with a question to “you.” Do not open with a dictionary definition.

The first sentence names a thing you can sit on, measure, or see.

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
- “rich tapestry,” “journey,” “elevate,” “empower,” “seamless,” “holistic,” “unpack”
- “nuanced” as filler
- throat-clearing first paragraphs
- fake dualities (tradition vs innovation, art vs science) unless the piece is actually about a real fork
- symmetrical list-filler (three parallel virtues, five “reasons,” seven “tips”)
- invented sitter quotes
- invented shop-floor dialogue attributed to named living people

No COSMOS. No AI. No process talk about how the draft was written.

## Claims and [VERIFY]

Uncertain numbers, dates, accession numbers, factory outputs, and shop-specific practices get `[VERIFY]` or `[CITE NEEDED]`. Do not invent a popliteal percentile. Do not invent a Thonet weekly count. Do not invent a Wilmar seat height as house standard.

BIFMA X5.1 / X10.1 and ISO 9241-5 are **office and computer-use** documents. They may be named as cousins. They are not dining-chair law. Dining is a table-and-chair pair: seat height, table height, apron clearance, and duration of the meal. Stephen Pheasant’s *Bodyspace* (anthropometry) is not Thomas Pheasant the furniture designer. Do not conflate them.

Place continuity is fair: hardwood, oak, furniture stock, Saline River timber geography. Bradley Brand Furniture, LLC is not claimed as the unbroken successor of Fullerton’s Bradley Lumber Company.

## Brand, lightly

These drafts are staged for BBF / Bradley Brand furniture-history SEO. They teach. They do not sell chairs.

Bradley Brand / BBF may appear where Arkansas or southern hardwoods are the actual subject. One or two sentences. No product names (no Lumberjack, RattleSnake, Saline Creek, Moro in the body unless a later editor adds a photographed object). No “our craftsmen.” No call to action.

Optional footnotes only:

- https://bradleybrandfurniture.com/heritage
- https://bradleybrandfurniture.com/craft

## Photos

Caption every figure in the draft front matter **and** in `PHOTO_CAPTIONS.md`.

Prefer:

- museum collection images with a live object URL and a stated license
- public-domain plates (Chippendale, Hepplewhite, Sheraton, Thonet catalogs)
- Keith’s library: `D:\BBF\BBF Photos` — working-shop and millwork frames

Credit only what is known. Never invent a credit. Postcard and commercial-archive images need rights confirmation — mark `[VERIFY rights]`.

## Front matter (required)

```yaml
title: string
slug: kebab-case
series: dining-chairs-history-design
status: draft
voice_check: edited
reading_order: integer
word_count: integer   # body copy only, after last self-edit
dek: one or two sentences, no slogan
topic: history | form | ergonomics | materials | shop | culture | labor
era: string
pillar: dining-chairs
primary_keyword: string   # one slug owns one query
meta_description: ~150 characters, search snippet, not a slogan
seo_intent: informational
figures: list (id, preferred path or URL, caption, credit, license, status)
optional_links: footnote-only, or omit
verify: list of claims still open
```

`status` stays `draft`. Do not mark a piece `ready` here.

## WordPress

See `WP_IMPORT.md`. Import as **draft** posts only. Do not schedule.

## Self-edit before `voice_check: human`

Read the piece aloud in the head. Kill:

1. Any banned word or throat-clear.
2. A paragraph that could sit in any other essay with the names swapped.
3. A list that exists because lists look finished.
4. A closing that restates the dek.
5. A sentence that treats an office chair standard as a dining rule.

If the piece still feels like a briefing, it is not done.
