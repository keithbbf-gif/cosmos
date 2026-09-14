---
title: Furniture finishing chemistry — staged drafts
slug: furniture-finishing-chemistry
status: draft
series: furniture-finishing-chemistry
stage: 0
stage_name: index
order: 0
topic: [index, shop-safe]
audience: shop
safety: shop-safe
voice: human
---

# Furniture finishing chemistry

These are **drafts**. They are staged on purpose: you can read them in order and
build a mental model before you open a can, or you can jump a stage when you
already know why the last one failed.

This is shop writing. The chemistry is here because the shop lies to itself
when it skips it. The practice is here because chemistry that never meets a
rag is homework.

## What this series is

Five finish families, plus the work that decides whether they look like
themselves:

1. **Oil** — linseed, tung, wiping oils, hardwax. They polymerize. They do
   not "dry" the way water dries.
2. **Varnish** — alkyd, oil-modified polyurethane, spar, wipe-on. A cooked
   or blended film. Thickness is a choice with consequences.
3. **Shellac** — a bug resin in alcohol. Sealer, finish, diplomat, and a
   poor exterior candidate.
4. **Waterborne** — polymer particles that have to *knit*, not just lose
   water. Grain raise is not a moral failing.
5. **Milk paint** — casein and lime, unless the can quietly became acrylic.
   Chalk is chemistry. Chip can be too.

Around those: surface, stain, compatibility, repair, maintenance, shop air,
and the sentences you owe a client.

## Shop-safe fence

This series stays inside **legal furniture-shop practice**.

It will talk about:

- how commercial finishes behave on wood
- how to read a label and a film
- ventilation, rags, and the ordinary fire that oil rags can start
- why old paint on a flea-market piece is a test-first problem
- how to dispose of solvent waste the way a household or shop is supposed to

It will **not** teach:

- how to cook, distill, concentrate, or synthesize solvents or resins
- how to mix your own metallic driers, isocyanate systems, or formaldehyde
  catalysts from raw chemistry
- how to make explosives, fuels, or anything that is not furniture finishing
- how to dodge hazmat rules, dump waste, or strip lead without protection
- "food safe" as a license to put an uncured film on a cutting board and
  call it dinner

If a draft mentions a dangerous commercial class (conversion varnish,
methylene chloride stripper, spray lacquer), it names the class and the
reason a small shop should leave it in the can or take it to someone with
the booth. It does not become a formulation notebook.

## How to read (staged)

| Stage | Name | Drafts | What you should be able to say after |
| --- | --- | --- | --- |
| 1 | Foundation | 01–05 | What a finish *is*, and what this series refuses |
| 2 | Oil | 06–12 | Why a rag stays warm, and why "tung" on a can is not a lab result |
| 3 | Varnish | 13–18 | Oil length, recoat windows, amber vs plastic |
| 4 | Shellac | 19–24 | Cuts, wax, blush, and the honest limits |
| 5 | Waterborne | 25–30 | Emulsion, coalescence, grain raise, stacking |
| 6 | Milk paint | 31–35 | Casein, bonding, chalk, chip |
| 7 | Practice | 36–45 | Sand, stain, repair, air, clients |

Read a stage, then do one small board. The board is the critic.

## Voice

No "comprehensive guide." No "whether you're a beginner or a pro." If a
sentence could sit on the back of a big-box can, it does not belong here.
A claim without a shop consequence is cut.

## File map

See [`MANIFEST.md`](MANIFEST.md) for slugs, stages, and topics.

Drafts are numbered so the folder *is* the syllabus.

## Figures, photos, rights

Each draft (01–45) embeds a **shop diagram** (SVG) and a **PD/CC photograph** with SEO `alt` text and `<figure>` captions. House rules: [`STYLE_GUIDE.md`](STYLE_GUIDE.md). Photo list: [`PHOTO_CAPTIONS.md`](PHOTO_CAPTIONS.md). **Licenses and attribution:** [`RIGHTS.md`](RIGHTS.md). Diagram index: [`GRAPHICS_INDEX.md`](GRAPHICS_INDEX.md) (generated).

Regenerate pipeline:

```bash
python3 tools/generate_furniture_finishing_chemistry_graphics.py
python3 tools/fetch_furniture_finishing_chemistry_photos.py
python3 tools/embed_furniture_finishing_chemistry_figures.py
```
