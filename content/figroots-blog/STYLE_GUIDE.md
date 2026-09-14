# FigRoots voice — STYLE_GUIDE

This folder is evergreen grower copy for [figroots.com](https://figroots.com). It is **not** COSMOS core, not AI-runtime docs, and not a patent file.

If a draft sounds like a gardening newsletter or a language model, it fails. Rewrite it.

## Who is talking

Two pens. Do not mash them into one bland narrator.

**Jack Chambers** writes cuttings, storage, rooting failures, and the seasonal calendar. He is concrete first: length, nodes, lignified vs green, moisture you can feel in your hand. He already defined the industry cutting on FigRoots as **6–8 inches and three nodes**. He told The Fig Jam: wash the cuttings, wrap long-term wood in parafilm, double-bag, crisper. He ranks figs by eye, size, and what they taste like in South Arkansas, not by hype.

**PapaFig (Keith Chambers)** writes climate, soil, pots vs ground, flavor, pests, and true-to-type. Rural South Arkansas, zone **8a**. Hundreds of pots, a smaller in-ground set, fertigation, raised-bed dirt that still roots a stick. He will say he is not a fan of a variety yet. He will say wait. He will not invent a success rate.

Credit the byline in front matter. First person is allowed. “We” is fine when it is the two of them.

## The existing posts these drafts extend

Do not rewrite these. Link them. Fill the holes they left.

| Already on figroots.com | What it already said |
|---|---|
| [Pick The Right Fig](https://figroots.com/2025/07/02/pick-the-right-fig-for-you/) | One-page checklist: GDD, tight eye, breba, pots, flavor families, birds, South shade + water. These drafts **unpack** those bullets. |
| [An Introduction to Figs](https://figroots.com/an-introduction-to-figs/) | Flavor surprise, trusted sources, 1–3 years to prove type, Promix / field capacity, scams. |
| [Lets Talk About Fig Cuttings](https://figroots.com/2025/12/23/lets-talk-about-fig-cuttings/) | 6–8" / 3 nodes. Lignified vs dormant vs green. Fridge is for dormant wood. |
| [Fig Pop Method](https://figroots.com/fig-pops/) | Coir damp-not-wet (squeeze, then add ~30% dry). Heat mat **with a thermostat**, about 75–78°F. Pencil-thick wood. |
| [Coco Coir vs DE A/B](https://figroots.com/2026/02/10/rooting-fig-cuttings-coco-coir-vs-diatomaceous-earth-de-lessons-from-my-a-b-test/) | Their 2023 test. Cite those numbers. Do not invent a new trial. |
| [Outdoor](https://figroots.com/outdoor/) | Pots and raised beds. Shade. Water once or twice a week on bulk starts. |

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
- generic plant-care fluff (“give your plant love”)
- symmetrical three-tips filler that could apply to tomatoes

## Do this instead

1. Open on a **real grower problem**: split fruit after an August storm, a cutting that leafed and then melted, a “Black Madeira” that fruited as a brown turkey, a pot cooked on black plastic in July.
2. Put **numbers you can act on**: 6–8 inches, 3 nodes, 70% field capacity, heat mat 75–78°F on a thermostat, 3-gallon pot-up before June, 6–8 hours of sun, crisper not the freezer shelf.
3. Default climate is **Arkansas / Southeast**: heat, humidity, clay, tight-eye varieties, afternoon shade, fruit souring after rain + heat. Northern full-sun advice is the exception, and you say so.
4. Mix short sentences with longer ones. Do not march in identical paragraph lengths.
5. Earn the opinion. “I would root it now.” “I would not buy that off a marketplace.” “We still have Celeste in the ground because we give a variety a long trial.” If you have not done it, do not pretend.
6. Cite a source or mark **`[VERIFY]`**. No fake A/B tests. No fake “92% of our customers.” No invented fridge-month guarantees. The coir/DE percentages already published on FigRoots may be cited as *that* test, not as a universal law.
7. Prefer photos from **`D:\FIGS`** on KC-PC. Use the real folder names in `PHOTO_MANIFEST.md` (Fig Fruit, Breba 2025, Bulk Cuttings, DE vs CC, Fig Labels, Greenhouse photos, FigRoots, …). Skip `.dtrash`. Stills over video. Public-domain fills only from USDA or Wikimedia Commons **PD / CC0**, with URL + license in `SOURCES.md`. No nursery-catalog scrapes.

## Sentence test

Read the first 80 words out loud.

- Pass: you can hear Jack or Keith talking to a grower who already killed a tray of cuttings.
- Fail: it could be swapped onto a succulent blog and still make sense.

## Front matter (required)

```yaml
---
title: ...
slug: ...
meta_description: ...   # one or two sentences, no hype verbs from the ban list
author: Jack Chambers | PapaFig
tags: []
images:
  - path: "D:\\FIGS\\Fig Fruit"   # real KC-PC folder; see PHOTO_MANIFEST.md
    caption: "..."
    source: ours            # ours | pd
    folder_pick: "Fig Fruit"
    license: ""             # required if source: pd
status: draft
voice_check: human
pillar: climate | fruit | culture | propagation | identity
priority: 1-12
---
```

`voice_check: human` is a claim. If the prose is generic, change the prose. Do not leave the flag on a bad draft.

## Length

Aim 900–1600 words of useful grower copy. Cut filler before you pad. Quality beats quota.

## What we will not write

- COSMOS / AI runtime / patents
- Medical or chemical safety theater. Diluted bleach / H2O2 mentions stay at the level already on FigRoots (wash, dilute, dry). No “kills all pathogens” claims.
- Caprifig wasp culture as if it were an Arkansas backyard project. Common figs only, unless explaining why.
- Live WordPress publish steps. Drafts stay drafts. See `WP_IMPORT.md`.
