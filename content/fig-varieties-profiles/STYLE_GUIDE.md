# Fig variety profiles — STYLE_GUIDE

Evergreen cultivar copy for [figroots.com](https://figroots.com). Not COSMOS. Not a catalog. Not a nursery sell sheet.

If a draft could be swapped onto a succulent blog and still make sense, it fails.

## Who is talking

**PapaFig (Keith Chambers)** writes these. Rural South Arkansas, zone **8a**. Hundreds of pots, a smaller in-ground set. He will say he is not a fan of a variety yet. He will say wait. He will graft before he throws a live hole away.

**Jack Chambers** is on the record for cuttings and for a short plate list (Red Sicilian, Navid’s Unk Dark Greek, Syrian Dark #2, Jack Lilly, Nuestra Señora del Carmen, Negra d’Agde). Cite that list. Do not put Jack’s ranking on a fig he did not name.

First person is allowed. “We” is the two of them. Do not invent a third narrator.

On-record source: [Interview With A Fig Grower: Keith and Jack Chambers](https://www.thefigjam.co/p/interview-with-a-fig-grower-keith), The Fig Jam, 25 Jul 2025.

## What this pack is

One cultivar. One grower problem. Enough botany to keep a neighbor from buying the wrong plant. Enough climate to keep an 8a tree from being judged by a California photo.

The how-to pack (`content/figroots-blog/`) already unpacked GDD, tight eye, breba, pots, rust, nematodes. **Link those ideas. Do not rewrite those essays.**

Live FigRoots pages to cite, not restage:

- [Pick The Right Fig](https://figroots.com/2025/07/02/pick-the-right-fig-for-you/)
- [An Introduction to Figs](https://figroots.com/an-introduction-to-figs/)
- [Types of Figs](https://figroots.com/2025/08/17/types-of-figs/) — Jack’s common / San Pedro / Smyrna primer
- [Fig Reviews](https://figroots.com/fig_reviews_archive/) — Red Sicilian, Negra d’Agde, LSU Jack Lily scores already on the site

## Ban list

Kill the draft if any of these show up:

- “In today’s rapidly evolving…”
- “It’s important to note”
- “delve” / “delving”
- “landscape” (unless dirt)
- “robust”
- “leverage”
- “unlock”
- “journey”
- “Whether you’re a beginner or…”
- “In conclusion”
- “Moreover” / “Furthermore” stacks
- “essential for success”
- “game-changer”
- “supercharge”
- “tips and tricks”
- “tapestry”
- “nestled”
- “boasts”
- generic plant-care fluff
- a flavor wheel that never names an ostiole
- a claim that we plated a fig Keith or Jack has not named

## Do this instead

1. Open on a **real grower problem**: a tag that is a pile, a wasp you do not have, a gold fig that finishes in October, a berry fig that splits after an August storm, a California shipping photo sold as an Arkansas tree.
2. Put **numbers you can act on** when they are sourced: 6–8 hours of sun, #3 before June, ~15–17°F as a dieback conversation (extension, not a guarantee), LSU release years, Condit’s synonym counts.
3. Default climate is **Arkansas / Southeast**: heat, humidity, clay, tight-eye varieties, afternoon shade, souring after rain + heat. Northern full-sun advice is the exception, and you say so.
4. Name the **horticultural type**: common (persistent), Smyrna (caducous), San Pedro, caprifig. Jack already defined these on FigRoots. A Smyrna in 8a without a wasp is a leaf bush.
5. Treat **names as claims**. Brown Turkey, Improved Celeste, Black Madeira, “LSU” on a marketplace listing — wait for fruit. Caption the clone we have.
6. Cite a source or mark **`[VERIFY]`**. No fake A/B tests. No “92% of growers.” No invented fridge-month guarantees. No invented ripening date for Saline County unless we wrote it down.
7. Prefer photos from **`D:\FIGS`**. Named folders are not proof of type. Skip `.dtrash`. Stills over video. Public-domain fills only from USDA or Wikimedia Commons **PD / CC0**, with URL + license. No nursery-catalog scrapes.

## Sentence test

Read the first 80 words out loud.

- Pass: you can hear Keith talking to a grower who already bought the wrong “Turkey.”
- Fail: it could sit under a stock photo of a grocery fig.

## Front matter (required)

```yaml
---
title: ...
slug: ...
meta_description: ...
author: PapaFig
tags: []
images:
  - path: "D:\\FIGS\\Fig Fruit"
    caption: "..."
    source: ours            # ours | pd
    folder_pick: "Fig Fruit"
    license: ""             # required if source: pd
status: draft
voice_check: human
pillar: identity
priority: 1-46
cultivar: ...
fig_type: common | smyrna | san-pedro | caprifig | disputed
---
```

`voice_check: human` is a claim. If the prose is generic, change the prose.

## Length

Aim 1,100–1,500 words of useful grower copy. Cut filler before you pad. A human editor should keep the piece.

## What we will not write

- COSMOS / AI runtime / patents
- Medical or chemical safety theater
- Caprifig wasp culture as an Arkansas backyard project. Explain the type. Do not write a how-to for *Blastophaga* in Bradley County.
- Live WordPress publish steps. Drafts stay drafts. See `WP_IMPORT.md`.
- A second Celeste-versus-Brown-Turkey essay. Those two get their own deep profiles here; the comparison already exists in the how-to pack.
