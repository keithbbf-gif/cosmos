# EDITOR_REPORT — furniture & fashion fads blog

**Pass:** EDITOR (grammar, spelling, style, human voice)  
**Date:** 2026-09-14 (UTC)  
**Base reviewed:** `cursor/furniture-fashion-fads-graphics-46bc` @ `ce5ac6c` (graphics pack; PR #238 scope)  
**Editor agent:** Cloud Cursor (`cursor/fffb-editor-report-4278`)

## Verdict: **HOLD — no article edits this pass**

All 44 drafts in `articles/` are **layout stubs**: front matter, H1, the italic placeholder line *Draft stub — copy and body pending editorial pass. Graphics are staged for layout.*, and embedded `<figure>` blocks pointing at staged SVGs. There is **no body prose** to copyedit without inventing content, which is out of scope for EDITOR.

Per pack rules: improve only articles with real prose; do not polish empty shells.

| Metric | Count |
|--------|------:|
| Articles scanned | 44 |
| With real body prose (editor-ready) | **0** |
| Stub-only (graphics + placeholder) | **44** |
| Articles edited this pass | **0** |
| SVG / `<figure>` embeds touched | **0** |

**Mean word count per file:** ~81 (dominated by YAML, captions, and figure markup—not narrative copy.)

## When to re-run EDITOR

Treat an article as **editor-ready** when **all** of the following hold:

1. The italic stub line is removed (or replaced by intentional dek/lede copy).
2. At least one paragraph of continuous prose exists **between** the title block and the first `<figure>` (or prose continues after figures).
3. Rough floor: **≥400 words** of narrative excluding front matter and figure captions (adjust if WRITER brief specifies otherwise).

On re-run: preserve every `<figure class="fffb-figure">` block and `../assets/<slug>/…svg` path unchanged; edit surrounding prose only.

## Editorial checklist (for the next pass)

Apply to each editor-ready article:

- **Grammar & spelling:** Standard American English unless a piece explicitly uses another register.
- **Style:** Short sentences mixed with longer ones; concrete nouns; no throat-clearing openings (“In today’s world…”, “It’s worth noting…”).
- **Human voice:** Opinion and specificity where the WRITER draft allows; cut hedge stacks (“perhaps”, “ arguably”, “to some extent”).
- **Banned AI habits:** Em dash overuse, numbered “key takeaways” unless the draft already uses that structure, “delve”, “landscape”, “tapestry”, “game-changer”, “elevate”, “robust”, rhetorical questions as section headers, and symmetrical “On the one hand / On the other hand” filler.
- **Figures:** Do not rewrite `alt` text or figcaptions unless they contradict the prose or contain errors; captions are paired to graphics in `GRAPHICS_INDEX.md`.

After a successful pass, set front matter `voice_check: done` (or `edited`) and note the slug in **Articles completed** below.

## Articles completed (prose edited)

_None._

## Stub inventory (awaiting WRITER prose)

Each row: slug — title (`category`, figure count).

### Furniture (19)

| Slug | Title | Figs |
|------|-------|-----:|
| `avocado-green-appliance-era` | Avocado Green and the Appliance Time Stamp | 2 |
| `bean-bag-lounge-cycles` | Bean Bags Never Left, They Just Hid | 2 |
| `boucle-upholstery-wave` | Bouclé: Texture of the Moment | 2 |
| `brutalist-furniture-moment` | Brutalist Furniture's Short Hot Streak | 2 |
| `cloud-couch-trend` | The Cloud Couch and Performative Comfort | 2 |
| `conversation-pit-revival` | Conversation Pits Try Again Every Generation | 1 |
| `farmhouse-chic-cycle` | Farmhouse Chic and the Shiplap Hangover | 2 |
| `ikea-era-flat-pack` | The IKEA Era Changed What We Expect | 2 |
| `mcm-orange-plastic-chairs` | Orange Plastic Chairs: Fun Until Move-Out Day | 1 |
| `mid-century-modern-resurgence` | Mid-Century Modern Keeps Coming Back | 3 |
| `neon-sign-home-decor` | Neon Signs in Bedrooms | 1 |
| `open-shelving-kitchen` | Open Shelving: Pinterest Pretty, Dusty Daily | 2 |
| `rattan-everywhere-phases` | Rattan: Porch Material, Living Room Fad | 2 |
| `shiplap-fatigue` | When Shiplap Became a Punchline | 1 |
| `sunken-living-rooms` | Sunken Living Rooms: Architecture as Status | 2 |
| `terrazzo-tables-fad` | Terrazzo Tables Flooded the Feed | 2 |
| `velvet-sofa-waves` | Velvet Sofas: Glam Returns on a Timer | 2 |
| `waterbed-decade` | Waterbeds: The Ultimate Dateable Fad | 2 |
| `wicker-moment-2020s` | Wicker's 2020s Instagram Renaissance | 1 |

### Fashion (16)

| Slug | Title | Figs |
|------|-------|-----:|
| `athleisure-permanence` | Did Athleisure Break the Fad Clock? | 2 |
| `cargo-pants-resurgence` | Cargo Pants Return (Again) | 1 |
| `coquette-bow-moment` | Coquette Bows and Hyper-Feminine Micro-Trends | 1 |
| `cottagecore-fashion` | Cottagecore: Pandemic Pastoral in Fashion | 1 |
| `logomania-waves` | Logomania Waves and Quiet Backlashes | 1 |
| `low-rise-jeans-cycle` | Low-Rise Jeans: The Cycle Everyone Debates | 1 |
| `mob-wife-aesthetic` | Mob Wife Aesthetic: TV Costume to TikTok Uniform | 1 |
| `neon-athleisure-2010s` | Neon Athleisure and the Gym Selfie Era | 1 |
| `normcore-ironically-timeless` | Normcore: Anti-Trend That Became a Trend | 2 |
| `parachute-pants-80s-90s` | Parachute Pants: Functional to Punchline | 2 |
| `peplum-waistline` | Peplum Waistlines: Short Runway, Long Tail on eBay | 1 |
| `platform-shoes-height-wars` | Platform Shoes and Altitude Inflation | 1 |
| `quiet-luxury-moment` | Quiet Luxury and the Logo Hangover | 2 |
| `shoulder-pads-power-dressing` | Shoulder Pads and the Power Silhouette | 2 |
| `skinny-jeans-death-rumors` | Skinny Jeans 'Death' and Denim Politics | 1 |
| `y2k-fashion-revival` | Y2K Fashion Revival: Nostalgia at Double Speed | 2 |

### Cross (9)

| Slug | Title | Figs |
|------|-------|-----:|
| `fast-furniture-vs-fast-fashion` | Fast Furniture vs Fast Fashion: Same Clock? | 1 |
| `ikea-x-fashion-crossover` | When IKEA Dressed Like a Fashion Label | 1 |
| `maximalism-vs-minimalism-pendulum` | The Maximalism–Minimalism Pendulum | 1 |
| `pinterest-to-purchase-pipeline` | Pinterest to Purchase: Mood Board Economics | 2 |
| `target-design-collabs` | Target Design Collabs and the Drop Calendar | 2 |
| `thrift-resale-era-chart` | Thrift and Resale: The Anti-Fad Infrastructure | 1 |
| `tiktok-shelf-life` | TikTok Shelf Life: Furniture Caught Up to Fashion | 1 |
| `trend-forecasting-industrial-complex` | Who Declares a Trend Dead? | 2 |
| `why-trends-accelerated-after-2010` | Why Trends Accelerated After 2010 | 1 |

## Dependencies

| Upstream | Status |
|----------|--------|
| Graphics (PR #238 / `cursor/furniture-fashion-fads-graphics-46bc`) | **Present** — SVGs embedded in all stubs |
| WRITER prose | **Not landed** — blocks EDITOR |

## Suggested merge order

1. Merge graphics PR when approved (unchanged by this report).
2. WRITER branch adds body copy; removes stub line per article.
3. Re-run EDITOR on changed slugs only; append to **Articles completed** and open a prose-editing PR.
