# Furniture competitor UX — toward a 9.5 bar

**Pass:** 2026-09-14. Public storefronts only. HTML + theme CSS fetched; no carts submitted, no accounts created.

**Why these four:** they are the American solid-wood / workshop brands a BBF furniture buyer already compares. Moser is the taste bar. Stickley is the catalog + “buy it this month” bar. Vermont Woods is the honest made-to-order shop. Boos is the SKU machine (islands, tops, boards) that still looks like a brand.

**Stack note:** all four run Shopify. BBF furniture will not. Steal the *behavior*, not the theme. OceanWP + Woo is the BBF shell; see `DESIGN_TAKEAWAYS.md`.

**9.5 here means:** one job per screen, one type pair, photography that looks like the wood, lead time said before pay, a path for “I want it now” and a path for “build mine.” Sale chrome is optional. Craft is not.

---

## Thos. Moser — the bar

- Home: [https://www.thosmoser.com/](https://www.thosmoser.com/)
- PDP (Pasadena Rocker): [https://www.thosmoser.com/product/pasadena-rocker/](https://www.thosmoser.com/product/pasadena-rocker/)
- Quick Ship: [https://www.thosmoser.com/collections/quick-ship](https://www.thosmoser.com/collections/quick-ship)
- Seating PLP: [https://www.thosmoser.com/collections/seating](https://www.thosmoser.com/collections/seating)
- FAQ (lead time, woods, trade): [https://www.thosmoser.com/pages/frequently-asked-questions](https://www.thosmoser.com/pages/frequently-asked-questions)
- Trade: [https://www.thosmoser.com/pages/working-with-designers](https://www.thosmoser.com/pages/working-with-designers)

**Hero.** The first screen is a *piece*, not a lifestyle collage and not a slider. Home headings walk Continuous Arm Chair → “A Promise to You” / “The Signature” → “Designed for the Way You Live.” The photograph is the product. Copy is short. Promo cards (Lounge Sets, Quick Ship, dining-set pricing) come *after* the piece has been named.

**Sticky.** Theme CSS (`theme.css`) defines `.header-sticky` and `.sticky-element`. The header stays; the announcement bar is a single inverse line, not a sale carousel. On the PDP the buy column is a sticky element while the gallery scrolls — you never lose wood + price + add.

**Typography.** Typekit kit `ihl0gam`: **Benton Modern Display** (and condensed/extra cuts) for titles, **Mr Eaves Modern / Mr Eaves Sans** for UI. DM Sans and Playfair appear as fallbacks in CSS, not as the voice. Letterspacing on headings is tight, not “luxury tracking.” Body is quiet. That pair — a real display serif + a drawn sans — is the 9.5 type lesson. Do not fake it with Playfair + Lato.

**Whitespace.** Huge. Collection cards sit in air. The seating PLP uses a small collection hero (`hero--extra-small`) then a grid; it does not dump 80 SKUs against the header. Inverse announcement + light field + one dark wood photo is the whole palette.

**Announcement.** Literal text on 2026-09-14: `HANDMADE AMERICAN FURNITURE`. Not a coupon. That is a brand spine, not a promo slot.

**Shop flow.**

1. Mega-nav is **form** (Seating / Tables / Storage / Beds) then **room** then **collection** (American Bungalow, Bates, Crescent, Cumberland…). A first-time buyer can start from a chair or from a dining room.
2. PDP for the Pasadena Rocker: gallery left, title, one-sentence design credit (David Moser), **wood selector** (Cherry shown; Walnut in the collection strip), price from **$4,950**, inventory (“2 available” on the in-stock style), then the line that matters: *“Our designs are made to order; our current build time is 16 weeks.”* Quick Ship styles get a banner: *“Select Styles Are In-Stock and Ready to Ship.”*
3. Specs / Material & Care / More Information are collapsed sections, not a 2,000-word essay above the button.
4. Below the fold: four craft claims (Sculptor’s Eye, Solid Hardwood, Studio Tradition, Built to Endure), designer bio, collection cross-sell, lifetime guarantee, “One Maker. One Piece. One Signature.”
5. Cart is a **drawer**. Checkout is Shop Pay + cards. Custom work is *not* forced through the PDP — FAQ + consult + trade program take that load.
6. Quick Ship is a real collection (Shopify rules: inventory > 1 + tag `Quick Ship`), sorted by hand, copy: *“Made by Hand, Available Sooner… ship from our Auburn workshop within a week.”* That is the dual path: heirloom wait vs. this-month chair.

**Steal for BBF.** One hero piece. Brand-line top bar, not a sale. Display serif + drawn sans. Sticky buy column. Lead time on the button. A tagged Quick Ship / “in the shop now” collection. Signature / maker mark as a footer ritual, not a blog post.

**Leave.** Showroom city list as chrome (Freeport / Boston / DC / SF) only if BBF has rooms people can sit in. Do not copy the 16-week number; copy the *habit of saying the number*.

---

## Stickley — catalog that still sells this month

- Home: [https://www.stickley.com/](https://www.stickley.com/)
- Buy Online hub: [https://www.stickley.com/collections/buy-online](https://www.stickley.com/collections/buy-online)
- Buy Online by room: [https://www.stickley.com/collections/buy-online-living-room](https://www.stickley.com/collections/buy-online-living-room)
- Express Ship: [https://www.stickley.com/collections/express-ship-collection](https://www.stickley.com/collections/express-ship-collection)
- Delivery: [https://www.stickley.com/pages/delivery-shipping](https://www.stickley.com/pages/delivery-shipping)

**Hero.** Home on 2026-09-14 is a **campaign stack**, not a single piece: Labor Day Sale (“Save 35%”), new lighting, 2026 Collector Edition, Hudson Valley. That is a retailer homepage. The craft story (Als Ik Kan, Made in America, Sustainability) is pushed onto the Buy Online room pages as four equal columns under the grid — history as *proof under SKUs*, not a manifesto above them.

**Sticky.** Dawn-family `.shopify-section-header-sticky`. Header is top-center logo, account + cart. It sticks. Fine. The visual noise is the **announcement slider** (autoplay 10s) plus a mega-menu that is itself a sale billboard.

**Typography.** Typekit kit `mlb2ksa` plus Assistant / Lato in the CSS variables. Headings feel like a house sans, not a foundry display. It is competent, not 9.5. The type does not carry the brand; the Mission photography and the collector rocker do.

**Whitespace.** Tighter than Moser. Cards are denser. The Buy Online hub is four room tiles (Living / Dining / Bedroom / Office) — that *is* good space. The home carousel is not.

**Announcement (live).** Two slides, both linked:

1. “Introducing the 2026 Collector Edition LaSalle Rocker!” → `/products/2026-ce-lasalle-rocker-p`
2. “Shop online for $299 White Glove Delivery!” → `/pages/delivery-shipping`

Promo + logistics. No brand sentence. Mega-menu repeats Labor Day imagery.

**Shop flow.**

1. Nav splits **In Stock by room / by collection** (Saranac, Hudson Valley, Walnut Grove, Nichols & Stone) from **Express Ship** (Leopold’s Chair set, Mission sofas, express leather) from **Sale**. A buyer who wants a Morris chair this quarter does not wade through made-to-order dining.
2. Buy Online is a **second front door**. It is not “the whole catalog with a cart icon.” It is the subset they will actually fulfill from the web, then room-sliced.
3. Delivery cost is a first-class promise ($299 white glove), not a surprise at checkout. That is the Stickley lesson more than the sale.
4. Cart notification (not only a drawer) — “Item added” with View cart. Retailer habit.

**Steal for BBF.** Two catalogs: *Shop now* vs *Build*. Name delivery before checkout. Put heritage copy **under** the grid, not in front of it. Mega-menu can carry one seasonal tile — not four.

**Leave.** Autoplay announcement. Sale as the first H1. Collector-edition merchandising unless BBF actually runs a yearly piece. Dawn’s default “Stay in Touch” footer block.

---

## Vermont Woods Studios — the honest shop

- Home: [https://vermontwoodsstudios.com/](https://vermontwoodsstudios.com/)
- Collections index: [https://vermontwoodsstudios.com/collections](https://vermontwoodsstudios.com/collections)
- About: [https://vermontwoodsstudios.com/pages/about-us](https://vermontwoodsstudios.com/pages/about-us)
- Contact / Stonehurst: [https://vermontwoodsstudios.com/pages/contact](https://vermontwoodsstudios.com/pages/contact)
- Lifetime guarantee: [https://vermontwoodsstudios.com/pages/lifetime-guarantee](https://vermontwoodsstudios.com/pages/lifetime-guarantee)
- Sale: [https://vermontwoodsstudios.com/pages/sale](https://vermontwoodsstudios.com/pages/sale)
- Buying guide: [https://vermontwoodsstudios.com/pages/buying-guide](https://vermontwoodsstudios.com/pages/buying-guide)
- Trade: [https://vermontwoodsstudios.com/pages/designer-trade-program](https://vermontwoodsstudios.com/pages/designer-trade-program)
- Wood samples (from PDPs): [https://vermontwoodsstudios.com/products/audrey-solid-top-dining-table](https://vermontwoodsstudios.com/products/audrey-solid-top-dining-table)
- Cherry dining PLP: [https://vermontwoodsstudios.com/collections/cherry-wood-dining-tables](https://vermontwoodsstudios.com/collections/cherry-wood-dining-tables)
- Mission table PDP: [https://vermontwoodsstudios.com/products/american-mission-solid-top-dining-table](https://vermontwoodsstudios.com/products/american-mission-solid-top-dining-table)

**Hero.** Home is a **mission storefront**: “Uncommon Craftsmanship,” “Small Company, Big Mission,” then three trust tiles — Handcrafted in Vermont / Guaranteed For Life / Customizable — then “Meet Our Craftsmen.” Photography is workshop and farmhouse (Stonehurst), not a New York loft. It is the closest peer to a one-shop BBF: they say *where it is made* and *who makes it* on the first scroll.

**Sticky.** Same Dawn sticky header as Stickley (`.shopify-section-header-sticky`). Logo capped at **180px**. Middle-left header. Cart is a drawer with an empty-state “Continue shopping.” It works. It is not special.

**Typography.** **Proza Display + Proza Libre + Work Sans.** A real pair (display + text of the same family) plus a workhorse UI sans. Warmer and more “Vermont” than Stickley’s Lato. Closer to 9.5 than Stickley; still short of Moser’s foundry display.

**Whitespace.** Home tiles have air. Mega-menu does not: every dropdown is a **visual catalog** (bedroom sets, dining sets, Sierra upholstery, fire-pit sets) with 405px photos. That is the right trade for a shop that sells *sets*. Dense menu, calm page.

**Announcement (live).** Forest green `#263a2f`, two columns:

- Left: “Shop all current deals!” → `/pages/sale`
- Right: “Contact Us | (802) 579-1302”

Phone is in the chrome. Moser hid the 800 number in the footer; VWS puts it next to the deal. For a small shop that *is* the 9.5 move — a human answers.

**Shop flow.**

1. Mega-nav is **room first** (Bedroom / Dining / …) with named collections inside (Astrid, Cherry Moon, Larssen, Vermont Shaker). Plus Showroom furniture as its own path (what you can sit on in Vernon this week).
2. PDP pattern (Audrey / American Mission / Classic Shaker):
   - **Crafting Time 6–10 weeks** next to the price (excludes transit; stain may add).
   - **See Samples** — buy cherry/maple/walnut/oak chips. This is the highest-trust widget on any of the four sites. A $4k table should not be a JPEG guess.
   - Option grids: wood × size × edge. Base price names the *exact* config (“40×72 natural cherry”).
   - Construction bullets: solid hardwood, finish chemistry (water-based urethane / low VOC), “tables ship with legs detached,” white-glove setup.
   - Matching pieces in the same collection.
3. Lifetime guarantee is a **page**, linked from the menu, not a badge PNG.
4. Trade program and buying guide are first-class, not blog posts.

**Steal for BBF.** Phone in the top bar. Crafting time as a labeled field, not a FAQ. Paid wood samples. Base-price-means-this-config. Showroom / “in the shop” as a collection. Guarantee as a URL. Mega-menu photos of *sets*.

**Leave.** Default Dawn “Your cart is empty” chrome. Sale occupying the left half of the announcement if the shop is not actually running 20% off. Copeland-branded collections if BBF is the maker, not a multi-workshop marketplace — VWS sells several Vermont shops; BBF should not look like a reseller.

---

## John Boos — SKU density without looking cheap

- Home: [https://www.johnboos.com/](https://www.johnboos.com/)
- Furniture: [https://www.johnboos.com/collections/furniture](https://www.johnboos.com/collections/furniture)
- Islands: [https://www.johnboos.com/collections/islands](https://www.johnboos.com/collections/islands)
- Tables: [https://www.johnboos.com/collections/tables](https://www.johnboos.com/collections/tables)
- Carts: [https://www.johnboos.com/collections/carts](https://www.johnboos.com/collections/carts)
- Cutting boards: [https://www.johnboos.com/collections/cutting-boards](https://www.johnboos.com/collections/cutting-boards)

**Hero.** Hydrogen / Oxygen storefront (Shopify headless), not Dawn. Home is a **vertical stack of merchandising modules**: Labor Day free standard shipping (through 7 Sep on the day this was pulled — campaign dated), Forbes Vetted “best wooden cutting board,” rustic-edge boards, countertops, maple Newton prep board, workbench tops, then a cherry/walnut board pair with prices on the card ($295.95 / $541.95–$593.95). Each module is a full-bleed photo + two-line claim + one Shop. It is a catalog of *surfaces*, not a story.

**Sticky.** Main header (`_mainHeader_`) + cart aside. Cart actions are `position: sticky` in the drawer. Header spacer (`_headerSpacer_`) keeps content from jumping. No Dawn “sticky section” class — they built it. Mobile is an overlay menu, not a hamburger that dumps 80 links.

**Typography.** **Ivory LL** (serif) + **Neue Haas Grotesk Display / Text**. This is the other 9.5 pair: a display serif used sparingly, a Haas text face for everything else. It reads commercial-kitchen, not lodge. If BBF sells islands / butcher blocks / work tops, this is closer than Moser’s Benton.

**Whitespace.** Modules are full-bleed; the *grid* is tight. Furniture PLP opens with **“Choose your wood”** before “All Products” — filter as a heading, not a sidebar after 40 cards. That is the right density for 100+ islands.

**Announcement.** Campaign-first (free shipping / Labor Day). Fine for a national brand with UPS/FedEx SKUs. Wrong as BBF’s everyday chrome.

**Shop flow.**

1. Nav is **product family**, six words: Cutting Boards / Butcher Blocks / Furniture / Kitchen Countertops / Workbench Tops / Care & Maintenance / Collections / Gift Packs. No “shop by room.” The object *is* the room.
2. PLP cards are **Quick Shop** — title, 2–3 sentences, price range, wood/size still on the card. You can decide maple vs walnut without opening the PDP. Ranges are honest (`$1,957.00—$3,039.00` on Cherry Rustica).
3. Lead time appears on made pieces (“Ships in 4–5 weeks once ordered”) on the card, not only at checkout.
4. Account + favorites + cart in the header. This is a repeat-purchase brand (boards, cream, replacements). BBF furniture is not — do not clone the heart icon unless you sell consumables (oil, cream, samples).
5. Care & Maintenance is in the primary nav. For wood that people *cut on*, that is trust. For a dining table it can live under Guarantee.

**Steal for BBF.** Wood filter *before* the grid. Quick Shop cards with a real sentence and a range. Lead time on the card. Type pair with a text grotesque, not a script. Care as a nav item if BBF sells work surfaces.

**Leave.** Headless complexity. Favorites. Home as six stacked campaigns. “Explore Boos Block” brand-world if you only have one workshop.

---

## Scorecard (this pass — taste, not a rubric)

| Lens | Moser | Stickley | Vermont Woods | Boos |
|---|---|---|---|---|
| Hero | 9.5 — one piece | 6 — sale stack | 8 — mission + tiles | 7.5 — module catalog |
| Sticky | 9 — header + PDP buy | 8 — sticks, noisy bar | 8 — sticks, phone in bar | 8.5 — built, cart sticky |
| Type | 9.5 — Benton + Mr Eaves | 7 — Assistant/Lato | 8.5 — Proza + Work Sans | 9 — Ivory + Haas |
| Whitespace | 9.5 | 7 | 8 | 8 (tight grid, airy modules) |
| Shop flow | 9 — MTO + Quick Ship | 8.5 — In Stock / Express / $299 | 9 — samples + 6–10 wks | 9 — Quick Shop + wood first |
| Toward 9.5 | **the target** | steal dual-path + delivery | steal samples + phone | steal PLP density |

BBF furniture does not need Stickley’s 125-year megamenu. It needs Moser’s first screen, VWS’s samples and weeks, Boos’s wood-first grid, and Stickley’s *named* in-stock door.

---

## Do not

- Clone Shopify Dawn and call it OceanWP.
- Put Labor Day in the H1 of a shop that is not in a sale.
- Hide build time behind “Contact us for lead times.”
- Use Playfair Display + a Google sans and call it Moser.
- Photograph stained pine on a white cyclorama and expect these four to be the comparison set.
