# Fig pests & diseases — STYLE_GUIDE

Grower copy for [figroots.com](https://figroots.com). Not COSMOS. Not a patent file. Not a pesticide label.

If a draft sounds like a gardening newsletter, an Amazon roundup, or a language model, it fails. Rewrite it.

## Who is talking

**PapaFig (Keith Chambers)** writes this pack. Rural South Arkansas, zone **8a**. Pots, a smaller in-ground set, sticky August, a freezer that will still surprise a fig that rust-flushed in October. First person is the point.

Jack Chambers may be quoted on birds and harvest — he already said birds are the part of fig season he likes least after a dead tree. Do not mash the two pens. Pest and disease pieces stay PapaFig unless a draft is explicitly a harvest note in Jack’s mouth.

Credit the byline in front matter.

## What this pack is for

The FigRoots pest pillar. Nematodes, rust, mosaic, beetles, birds — plus the lookalikes (split, sour, cold stubs, wet feet) so a reader stops spraying the wrong thing.

Existing posts these drafts **extend**, not rewrite:

| Already on figroots.com | Leave it alone |
|---|---|
| [Pick The Right Fig](https://figroots.com/2025/07/02/pick-the-right-fig-for-you/) | One-line: pots if nematodes; green fruit if birds; tight eye if August stays wet |
| [An Introduction to Figs](https://figroots.com/an-introduction-to-figs/) | Do not root in mystery local soil |
| [Outdoor](https://figroots.com/outdoor/) | Pots, beds, shade, water |

The cuttings magazine pack (`content/figroots-blog/`) already has short takes on nematodes, rust, and birds. This folder goes deeper. Do not paste those essays. New scenes, new jobs.

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
- “just do these three things”
- generic plant-care fluff
- fake cures (see `CLAIMS_GUARDRAILS.md`)

## Do this instead

1. Open on a **yard problem**: orange dust on a thumb, a tree that wilts at noon with wet dirt, a necklace of vinegar figs, pecked shoulders at dusk, oak-leaf yellow that showed up after a 98° week.
2. Put **moves you can do**: rake and bag, water the dirt not the midnight leaf, knock a spare plant (not a rare name) to look at roots, drape netting on a frame and stake it, pick in the morning, mail the county a leaf.
3. Default climate is **8a South / Arkansas**: humidity, clay *and* sand pockets, tomato-ground history, rust in late summer, mosaic that has been on the wood for years, green June beetles, mockingbirds.
4. Mix short sentences with longer ones.
5. Earn the opinion. “I would pot that name.” “I would not fog ripe fruit.” “I would leave the mosaic tree.” If you have not done it, do not pretend.
6. Cite a source or mark **`[VERIFY]`**. No invented spray intervals. No “92% control.” No fumigant recipes.
7. Photos from **`D:\FIGS`** first. Real folder names. No nursery-catalog scrapes.

## Sentence test

Read the first 80 words out loud.

- Pass: you can hear Keith talking to a grower who already bought a bottle that did nothing.
- Fail: it could be swapped onto a tomato-blight blog and still make sense.

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
    source: ours
    folder_pick: "Fig Fruit"
status: draft
voice_check: human
pillar: nematodes | rust | mosaic | beetles | birds | diagnosis | cultural | wildlife | calendar | biosecurity
priority: 1-45
zone: 8a
---
```

`status: draft` is the staging rule. Do not set `publish`. `voice_check: human` is a claim. If the prose is generic, change the prose.

## Length

Aim **1,100–1,600** words of useful grower copy. Cut filler before you pad. A human editor should keep the piece.

## What we will not write

- COSMOS / AI runtime / patents
- A statewide spray calendar
- “Best fig pesticide 2026”
- Variety ranking of 300 names
- Medical latex theater
