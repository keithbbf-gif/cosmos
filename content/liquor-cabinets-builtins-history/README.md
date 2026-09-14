# Liquor cabinets, bars, and built-ins — BBF channel drafts

Staged educational scripts for the BBF channel. Not published. Not a catalog. Not a sales deck.

The job of this set is to teach **how a bottle found a piece of furniture**, and how that object changed: cellarettes under Georgian sideboards, American dining-room coolers, Prohibition concealment, the Art Deco cocktail cabinet, the suburban wet bar, and the contemporary built-in. Then the shop work: bottle geometry, glass rattle, light, finish, stone, the cold machine, and the line between a piece we can put on a truck and a piece of construction.

## Voice

Shop-floor first person. Ferdinand, Indiana. A working custom shop that sells through designer showrooms and delivers its own work. Educational. Human. No host-as-influencer. No "in today's fast-paced world." No close that asks for a cart click.

Public, checkable shop facts may be used. Do not invent a named bar we did not build, a celebrity liquor cabinet that is not already on the public record, or a plumbing license this shop does not hold. When the history is the industry's, say so. When it is our floor, say so.

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
4. Keep the verify notes in `SOURCES.md` off-camera. They are for the editor, not the viewer.

## Series map

| Stage | Folder prefix | What it teaches |
| --- | --- | --- |
| 00 Frame | `00-` | Three objects, stolen words, who is talking |
| 01 Georgian machine | `01-` | Cellarettes, cisterns, Adam pedestals, Hepplewhite/Sheraton, sarcophagus forms, locks |
| 02 American dining | `02-` | The dining room as performance, Sargent's picture, regional coolers, sideboards, Victorian mass, butler's pantry |
| 03 Concealment | `03-` | Pre-Prohibition locks, 1920–1933 as a brief, innocent furniture, Art Deco cabinets, repeal |
| 04 Home bar | `04-` | Fitted cocktail machines, carts, credenzas, rec-room wet bars, 1970s dens, hotel brass |
| 05 Built-in | `05-` | Furniture vs built-in, wet vs dry, pantry revival, kitchen-adjacent bars, contemporary millwork |
| 06 Shop | `06-` | Bottles, glass, light, hardware, finish, tops, refrigeration, climate, trucks, codes |
| 07 Close | `07-` | How to read a room before anyone draws a bar |

Play them in filename order for the long narrative. Lift any `standalone: true` draft for a single episode.

This landing is **44 staged drafts**. Machine index: `MANIFEST.json`.

## What this is not

- Not a catalog of Keith Fritz Fine Furniture bars.
- Not a speakeasy costume film.
- Not plumbing, electrical, or building-code advice. Local code and a licensed trade beat a furniture essay.
- Not COSMOS kernel work. This folder is channel copy sitting in the repo so the drafts have a git home and a PR.

## Check the set

```bash
python3 content/liquor-cabinets-builtins-history/validate_staging.py
```
