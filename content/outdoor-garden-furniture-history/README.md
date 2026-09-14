# Outdoor and garden furniture — history and materials (BBF-adjacent drafts)

Staged educational scripts for the BBF channel. Not published. Not a catalog. Not a patio-set brochure.

The job of this set is to teach **how sitting outdoors became furniture**, and what the weather does to the materials that try. Peristyles and villa stone. English benches and Coalbrookdale iron. The American porch, the Adirondack plank, wicker, postwar aluminum. Then the shop map: teak, cedar, ipe, oak, pressure-treated, cast and wrought and powder-coat, rattan and the plastic that stole its name, stone, sling, cushions, fasteners, finish, winter.

BBF collections sit **beside** this history. This shop builds indoor casegoods and tables that leave on our own trucks. Outdoor is adjacent — the same duties (joinery, finish, honesty about a job) under a harder climate. We do not invent a garden line, a lead time, or a warranty. We teach the century and the material so a collection page, a designer, or a homeowner can stop lying about weather.

## Voice

Shop-floor first person. Ferdinand, Indiana. A working custom shop. Educational. Human. No host-as-influencer. No "in today's fast-paced world." No close that asks for a cart click.

Public, checkable history may be used. Do not invent a named outdoor suite this shop did not build. When the history is the industry's, say so. When it is our floor — indoor wood, finish, trucks — say so.

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
| 00 Frame | `00-` | Weather as client, three climates, who is talking, stolen words |
| 01 Old world | `01-` | Peristyle, Rome, courtyard, Chinese garden seat, Italian villa stone |
| 02 European garden | `02-` | French theater, English bench, Coalbrookdale, Victorian display, conservatory |
| 03 American porch | `03-` | Porch as room, rocker, Adirondack, Mission, wicker, patio, aluminum |
| 04 Wood | `04-` | Teak, cedar/cypress, ipe, oak, pressure-treated, outdoor joinery |
| 05 Metal | `05-` | Cast iron, wrought vs mild steel, aluminum, powder coat |
| 06 Woven | `06-` | Rattan, wicker as method, all-weather weave, Lloyd Loom |
| 07 Other | `07-` | Stone, concrete, sling/mesh, cushions |
| 08 Shop | `08-` | Fasteners, finish, winter, reading a patio, collections adjacent |

Play them in filename order for the long narrative. Lift any `standalone: true` draft for a single episode.

This landing is **44 staged drafts**. Machine index: `MANIFEST.json`.

## What this is not

- Not a catalog of Keith Fritz Fine Furniture outdoor SKUs. There is no invented garden line here.
- Not a brand film for teak oil or "all-weather" resin.
- Not a building-code, accessibility, or structural-engineering brief. Local code and a licensed trade beat a furniture essay.
- Not COSMOS kernel work. This folder is channel copy sitting in the repo so the drafts have a git home and a PR.

## Check the set

```bash
python3 content/outdoor-garden-furniture-history/validate_staging.py
python3 content/outdoor-garden-furniture-history/validate_staging.py --write-manifest
```
