# Fig nursery / garden ecom peers

**Pass:** 2026-09-14. Public catalog and home pages. No checkouts, no FigBid bids, no account creates.

**Home tree:** [https://figroots.com/](https://figroots.com/) is already **OceanWP + child + Elementor + WooCommerce + Ocean Sticky Header** (`transparent-header`, `shrink-header`, `fixed-scroll`, boxed + box-shadow). Type: Lato / Chela One / Josefin Sans. It is an **informational** fig-growing manual (rooting, pest, up-potting, prune, winter). The `<title>` says so. Woo is installed; the home does not shop. That gap is the job.

**Peers below** are who a collector opens in another tab when they want a *tree*, not a tutorial.

---

## figroots.com — what we actually ship today

- Home: [https://figroots.com/](https://figroots.com/)
- Rooting hub: [https://figroots.com/rooting/](https://figroots.com/rooting/)
- Example protocol: [https://figroots.com/author/buster/](https://figroots.com/author/buster/) (PapaFig)

**What works.** Tutorial IA is a real curriculum: sanitize/hydrate/inoculate → seven rooting methods (Fig pop, Coir+D.E., Tree pop, D.E., Coir in bin, Outdoor, Air layer) → potting, pest, water, mulch, prune, winter. Hero line “DELICIOUS & EASY TO GROW / Grow Fruit! STEP-by-STEP” is a teacher’s voice. Ocean sticky + transparent header already exist — do not replace the plugin, restyle it.

**What fails the nursery-ecom bar.**

- No primary **Shop** in the extracted nav. A collector cannot buy a cutting from the first screen.
- Woo is a dormant engine. Peers who sell have a cart in the chrome.
- Display type is Chela One (party script). Fine for a hobby journal; wrong next to OTBP’s Instrument Sans or Trees of Antiquity’s farm serenity.
- Boxed + `wrap-boxshadow` fights full-bleed plant photography.
- Flavor language is in the *fruit* captions (“Ripe Adriatic Fig strawberry jam taste”) — that belongs on SKUs, not only on a blog card.

**Split to keep:** tutorials stay; shop is a sibling, not a replacement. OTBP and Trees of Antiquity both teach *on the collection page* without making the store a blog.

---

## Off the Beaten Path Nursery — the fig-ecom bar

- Home: [https://offthebeatenpathnursery.com/](https://offthebeatenpathnursery.com/)
- Plants + cuttings split: [https://offthebeatenpathnursery.com/pages/fig-plants-cuttings](https://offthebeatenpathnursery.com/pages/fig-plants-cuttings)
- Plants: [https://offthebeatenpathnursery.com/pages/fig-tree-plants](https://offthebeatenpathnursery.com/pages/fig-tree-plants)
- Cuttings FAQ / sale rules: [https://offthebeatenpathnursery.com/pages/cuttings-faq](https://offthebeatenpathnursery.com/pages/cuttings-faq)

**Stack:** Shopify. Type in `styles.css`: **Instrument Sans** + a little Courier New. Announcement bar + header + **always-on cart drawer** (`cart-summary--drawer-always`). Sticky filter / toolbar classes: `.product-list-toolbar--sticky`, `.cc-product-filter--sticky`. Mobile nav is `position: fixed`.

**Hero.** *“Find Your Flavor”* / “Featuring 300+ fig varieties from 30+ countries.” Then three facts: grown organically, shipping contiguous US only, rooted in Lancaster, PA. In-person sales **by appointment only** — said twice (home + note). New-items module. This is a collector site that admits it is a farm, not a big-box.

**IA (the steal).** Mega-nav is how fig people think:

- **Form:** Plants + Cuttings / Cuttings / Variety packs / Plants
- **Flavor:** Adriatic, Bordeaux, Dark Berry, Exotic Berry, Honey, Sugar
- **Origin:** France, Greece & Malta, Italy, Middle East & North Africa, Portugal & Azores, Spain
- Then the rest of the farm (pawpaw, pomegranate, …)

A Black Madeira buyer and a “I want honey-sweet” buyer both have a door.

**Shop flow.**

1. Landing `/pages/fig-plants-cuttings` is a **fork**, not a mixed grid: Plants » vs Cuttings ». Different season, different perishability, different price. Mixing them in one Woo category is how orders go wrong.
2. Annual sale is a **dated event** (FAQ: preview window, then 8:00pm EDT open, limited qty). Inventory is a drop, not an always-on Amazon.
3. Sunday-night restock language (plants page, prior season) — collectors learn the rhythm. Publish the rhythm.
4. Sticky filters on the grid so a 300-SKU catalog is usable on a phone.
5. Contact is for “is this variety actually available,” with an explicit “we’re in the middle of a sale, be patient.”

**Steal.** Flavor + origin taxonomies. Plant/cutting fork. Seasonal drop calendar. Sticky filters. Appointment-only visits. Contiguous-US shipping said on the home, not at checkout error.

**Leave.** Shopify Dawn leftovers. “Left” / social SVG junk in the title (their `<title>` is messy — do not copy). Purple fill-in-the-blank brand color unless it is ours.

---

## Trees of Antiquity — teaching on the PLP, commodity-clear price

- Home: [https://www.treesofantiquity.com/](https://www.treesofantiquity.com/)
- Fig collection: [https://www.treesofantiquity.com/collections/fig-trees](https://www.treesofantiquity.com/collections/fig-trees)

**Stack:** Shopify. Classes `#main-header-sticky`, `#hero`, `#announcement-bar`. Wallet chrome in the title (Apple Pay / Shop Pay / etc. concatenated — a theme bug; don’t).

**Hero.** Farm journal, not a drop. “Discover Fruit Trees For Your Home & Small Farm,” then a tile grid of **crops** (Apple, Apricot, Fig, Jujube…). Story block: certified organic, boy-in-the-garden origin, 40+ years shipping. Testimonials as named quotes (Dave’s Garden language on the home). This is a **general fruit nursery** that happens to do figs well.

**Fig PLP (the steal).** The collection is not a naked grid. It opens with a **husbandry paragraph**: own-root, self-fertile, breba vs main, 2–3 ft at ship, 15°F line, espalier, “bare roots must stay moist.” Then the SKUs at a **single clear price** ($39.95 on this pass for Italian Honey, Violette de Bordeaux, Brown Turkey, White Genoa, Black Jack, Peter’s Honey, Texas Everbearing, White Kadota, Verte, Panache, Conadria, Black Mission, Osborne Prolific, Flanders…). Variety is the differentiator; price is not a treasure hunt.

**Sticky.** `#main-header-sticky` + `#main-header-toolbar` (search / cart / contact). Collection grid header stays in play (`sticky-top` on the fig PLP).

**Steal.** Write 120 words of *how this plant ships and lives* above the fig grid. One price if the stock is one size. Crop tiles on the home if figroots ever sells more than figs. Organic / own-root as a fact, not a badge farm.

**Leave.** Wallet names in the `<title>`. A 400-variety fruit IA if we only sell figs — their home is a department store; ours should not pretend.

---

## Trees of Joy — depth of catalog, weakness of store

- Home: [https://treesofjoy.com/](https://treesofjoy.com/)
- Figs: [https://treesofjoy.com/product-category/figs/](https://treesofjoy.com/product-category/figs/)
- About: [https://treesofjoy.com/about/about-us/](https://treesofjoy.com/about/about-us/)
- Shipping: [https://treesofjoy.com/shipping-info/](https://treesofjoy.com/about/ — shipping is linked from nav as “Shipping info”)

**Stack:** WordPress + **Page Builder Framework** + Elementor + WooCommerce. Type: Roboto / Helvetica / Verdana. Pre-header + cart icon (`wpbff-cart`). Built by iO Agency (footer).

**What they have that figroots does not:** a real Shop, a fig **archive of named cultivars** (Figo Sofeno Escuro, Maltese Beauty, Naples White, Portuguese Long, Sequoia, Black Mission, Desert King, I-258, Improved Celeste, Jack Lilly, LSU Red…), waitlist on OOS, sale stickers, Bethlehem PA / zone 6 origin story, appointment visits.

**What fails.**

- Home is a **category dump** (Figs, jujube, other fruit, mulberry, pawpaw, kiwi, Uncategorized, gooseberry, Aronia, On Sale) with typos (“Producs,” “and and”).
- Fig archive on this pass is a wall of **Out of stock** + waitlist emails. A collector learns to bounce.
- No flavor/origin facets like OTBP. Alpha soup.
- Pre-header + Elementor + Woo chrome stacks the way figroots already stacks — do not add a third header.

**Steal.** Cultivar-level Woo products. Waitlist. Zone and “by appointment” in About. Shipping as a nav item (live plants die in a box — say how).

**Leave.** Uncategorized. Sale-as-IA. Shipping a collector to a 200-row OOS list with no filter.

---

## Peaceful Heritage Nursery — regional, sold-out honest, KY

- Home: [https://peacefulheritage.com/](https://peacefulheritage.com/)
- Figs: [https://peacefulheritage.com/collections/figs](https://peacefulheritage.com/collections/figs)

**Stack:** Shopify Dawn. Type: **Caprasimo** display + Open Sans. Sticky header. Home tiles: Pawpaw / Premium Fig Trees / Fruit-Berries-Nuts / Scion & Cuttings / Natives. “Naturally Grown,” pesticide-free, Non-GMO, Stanford, KY, `(859) 319-9228`. “As Seen On” logos. Collection: **44 products**, Filter + Sort, many **Sold out** with compare-at prices still visible.

**Steal.** Separate **scion/cuttings** tile from potted trees (same fork as OTBP). Region/conditions menu (“Deep South Fruit Varieties”) — useful if figroots sells cold-hardy vs. Coastal. Sold-out stays on the grid (teaches the catalog) *if* a restock alert exists.

**Leave.** Caprasimo (costume display). “As Seen On” until someone has actually seen us. AI-looking cart related-product classnames in their Dawn sections — a tell. Do not run that.

---

## Freire Figs — brand site, shop elsewhere

- Home: [https://freirefigs.com/](https://freirefigs.com/)
- Public seller list on FigBid (marketplace; we did not bid): [https://figbid.com/Listing/Browse?Seller=FreireFigs](https://figbid.com/Listing/Browse?Seller=FreireFigs)

**Stack:** site-builder (Great Vibes + Lato), `#header_stickynav`. Home H1: “Bringing the Old World to your door.” History (Azores → one tree → ~200 varieties). Goals. **No CA shipping.** “Soon through our own store (under construction).” Cart widget points at `/store?olsPage=cart`. Featured Products exist; the economic engine they name is **FigBid**.

**Lesson.** A pretty fig story without a working cart trains people to leave. figroots already has the story and the tutorials. If Woo is dark, we are Freire with better articles.

---

## FigBid — the collector marketplace (fetch blocked)

[https://figbid.com/](https://figbid.com/) returned **403** (Cloudflare challenge) to this pass. It remains the public auction/fixed-price board the fig forums use (Freire, Peaceful Heritage, and dozens of growers list there). Treat it as a **channel**, not a UX to clone: bid timers, seller feedback percentages, listing IDs, “paused auction” states. A COSMOS/Woo shop should not look like an auction house. It should be so clear on variety + size + ship window that a collector does not *need* to bid.

---

## Garden ecom quality checks (not fig-only)

- **One Green World** [https://onegreenworld.com/](https://onegreenworld.com/) — Woo + Revolution Slider home, Roboto/Raleway, “Shop Now” + cart total in the header, **Select options** + **Email me when available** on every card. The waitlist button is the pattern. The RevSlider home is the anti-pattern (do not).
- **Logee’s** [https://www.logees.com/](https://www.logees.com/) — Shopify, tropical/fruiting plant store, 1.2 MB home. Proof that a specialty plant shop can be a real cart. Too big and too general to copy.
- **Just Fruits and Exotics** [https://justfruitsandexotics.com/](https://justfruitsandexotics.com/) — 403 this pass; still a named Southern peer, re-check before citing IA.

---

## Scorecard

| | Story | Shop | Taxonomy | Season / stock honesty | Type / chrome |
|---|---|---|---|---|---|
| figroots | 9 — the manual | 2 — Woo asleep | 3 — methods, not cultivars | n/a | Ocean sticky exists; script display |
| OTBP | 8 | **9.5** | **9.5** flavor+origin | **9.5** dated drops | 8 Instrument Sans |
| Trees of Antiquity | 8.5 farm | 8.5 | 7 crop tiles | 8 husbandry on PLP | 7 (title bugs) |
| Trees of Joy | 6 | 6 (OOS wall) | 4 alpha soup | 5 waitlist, no season | 5 |
| Peaceful Heritage | 7 | 7 | 7 region + cuttings | 7 sold-out visible | 6 |
| Freire | 7 | 3 (store TBD) | 5 variety list | 4 | 5 script + Lato |

---

## Shop IA to build (Woo, either OceanWP or GP)

1. **Nav:** Shop · Plants · Cuttings · Learn · Shipping · Contact. Cart icon always.
2. **Attributes:** flavor (honey / berry / sugar / adriatic / bordeaux / dark), origin, cold-hardiness, plant-vs-cutting, pot size, in-stock.
3. **Fig PLP intro:** 100–150 words (own-root, ship size, zone, “roots must stay moist”).
4. **PDP:** cultivar name, synonym, flavor sentence, ship window, size, zone, qty, waitlist if 0.
5. **Drops:** a dated page, not a surprise empty cart.
6. **Learn** stays figroots’ existing tutorial tree — do not delete it to “look like a store.”

---

## Do not

- Auction UI.
- A 300-row OOS archive as the Shop home.
- California ship surprises (Freire says it on the home; so should we if we cannot ship there).
- Chela One on product titles.
- Mixing unrooted cuttings and 3-gal trees in one add-to-cart without a fork.
