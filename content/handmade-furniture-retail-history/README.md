# Handmade furniture retail history — BBF channel drafts

Staged educational scripts for the BBF channel. Not published. Not a catalog. Not a sales deck.

The job of this set is to teach **how a handmade piece of furniture used to find a home**, and how that pipe changed: craft galleries, trade showrooms, markets, the Etsy era, and the Overstock / Wayfair wholesale-dropship years. The viewer should leave able to read a price, a listing, and a showroom floor without being lied to by vocabulary.

## Voice

Shop-floor first person. Ferdinand, Indiana. A working custom shop that sells through designer showrooms and delivers its own work. Educational. Human. No host-as-influencer. No "in today's fast-paced world." No close that asks for a cart click.

Public, checkable shop facts may be used. Do not invent a specific Overstock or Wayfair contract, a dollar figure we did not earn, or a celebrity job that is not already on the public record. When the industry pipe is the subject, say so. When it is our floor, say so.

## Staging

Every draft in `drafts/` carries YAML frontmatter and `status: staged`.

| Status | Meaning |
| --- | --- |
| `staged` | Ready for Keith's cut. May be read on camera after his edit. |
| `hold` | Missing a fact, a date, or a personal beat only Keith can supply. |
| `cut` | Parked. Do not record. |
| `aired` | Used. Leave the file; do not silently rewrite history. |

This pull request lands the set at **staged**. Keith holds the on-camera pen.

## How to use a draft

1. Read the `educational_claim`. If the episode does not teach that one thing, it is the wrong draft.
2. Read `standalone: true` drafts in any order. Sequence drafts (`standalone: false`) after their `sequence_after` neighbor.
3. Speak it. These are written to be said, not scanned.
4. Keep the verify footer off-camera. It is for the editor, not the viewer.

## Series map

| Stage | Folder prefix | What it teaches |
| --- | --- | --- |
| 00 Frame | `00-` | Why the history, who is talking, the four doors, stolen words |
| 01 Galleries | `01-` | America House, ACC fairs, consignment, studio furniture as art |
| 02 Showrooms | `02-` | To-the-trade, design centers, net/list, samples, trucks |
| 03 Markets | `03-` | High Point, the market order, tear sheets |
| 04 Early web | `04-` | First storefronts, photography as showroom, freight |
| 05 Etsy era | `05-` | 2005, jewelry economics, handmade wars, fees, Etsy Wholesale |
| 06 Platform wholesale | `06-` | Overstock partners, CSN/Wayfair, dropship, SKU flood, MAP |
| 07 After | `07-` | Four prices, what "American made" meant, series close |

Play them in filename order for the long narrative. Lift any `standalone: true` draft for a single episode.

This landing is **44 staged drafts**, about 31,000 spoken words. Machine index: `MANIFEST.json`.

## What this is not

- Not a history of Keith Fritz Fine Furniture as a brand film.
- Not a hit piece on Etsy, Overstock, or Wayfair. The mechanisms are the story.
- Not legal advice, pricing advice, or a wholesale how-to.
- Not COSMOS kernel work. This folder is channel copy sitting in the repo so the drafts have a git home and a PR.

## Historical images (web / SEO)

Each staged draft includes one **Wikimedia Commons** photograph wired with semantic HTML:

- `<figure class="hfrh-figure">`, `<img alt="…">`, and `<figcaption>` (natural SEO captions, not keyword stuffing).
- Files live in `images/`; provenance and licenses are in `RIGHTS.md`.
- No AI-generated imagery; avoid identifiable portrait crops in hero frames.

```bash
python3 content/handmade-furniture-retail-history/fetch_commons_images.py   # refresh downloads from registry
python3 content/handmade-furniture-retail-history/wire_figures.py           # sync figure blocks from registry
python3 content/handmade-furniture-retail-history/validate_images.py
python3 content/handmade-furniture-retail-history/validate_staging.py
```

## Check the set

```bash
python3 content/handmade-furniture-retail-history/validate_staging.py
```
