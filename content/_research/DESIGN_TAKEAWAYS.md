# Design takeaways — OceanWP BBF + GeneratePress shells

**Pass:** 2026-09-14. Sourced from the three teardowns in this folder. Public URLs stay in those files; this page is the **build list**.

**Shells.**

| Shell | Theme | Product | Live cousin |
|---|---|---|---|
| **BBF furniture** | OceanWP + Woo (+ Ocean Sticky Header, Ocean Extra; Elementor only if a section truly needs it) | Workshop furniture / islands / boards | No live BBF storefront in-repo. Taste bar = Moser. Shop bar = VWS + Boos. |
| **GP therapy** | GeneratePress Premium + GenerateBlocks. No Woo. | SLP / practice | None of the peers are GP; steal structure, not themes. |
| **Figs** | Keep **OceanWP** on [figroots.com](https://figroots.com/) (already child + sticky + Woo + Elementor). GP is the *alternate* ecom shell if we split “Learn” (Ocean) from “Shop” (GP) later — do not dual-theme one domain. | Nursery + manual | figroots is the Learn half. OTBP is the Shop half. |

**9.5 bar (one sentence):** a stranger knows the thing, the time, the price or the next human step, and the type does not apologize.

cDeck Website dest stays **staged**. This pack does not publish.

---

## Shared (both shells)

1. **Two typefaces, period.** Display + text. Load two families, four weights max (400/500/600/700). Moser: Benton Modern + Mr Eaves ([thosmoser.com](https://www.thosmoser.com/), Typekit `ihl0gam`). Boos: Ivory LL + Neue Haas Grotesk. VWS: Proza + Work Sans. Therapy peers that feel calm: Inter + Lexend (Idaho Voice) or Source Sans + one serif (Dynamic).  
   **Refuse:** Playfair + Lato “luxury kit,” Chela One on products, Elementor’s 20-family preset list (Care to Speak’s kit).

2. **Sticky means stay, not shrink-to-nothing.** Header remains; announcement may go. Moser `.header-sticky` + PDP `.sticky-element`. Stickley/VWS/Peaceful Heritage: `.shopify-section-header-sticky`. figroots already: `ocean-sticky-header` + `shrink-header` + `fixed-scroll`.  
   **GP:** Elements → Hook `generate_after_header` / sticky bar, or GP Premium sticky. Do not stack Elementor sticky + GP sticky.

3. **Announcement is one job.**  
   - Brand spine (Moser: `HANDMADE AMERICAN FURNITURE`) **or**  
   - Human + phone (VWS: deals | Contact | `(802) 579-1302`) **or**  
   - Capacity (Ms. Paula: teletherapy only).  
   Not an autoplay sale slider (Stickley, 10s). Ocean **Top Bar** can do VWS’s two-column. GP: a one-row Element (or Top Bar in GP Premium).

4. **Primary action in the chrome.** Cart (ecom) or Schedule + `tel:` (therapy). Never “Learn more” as the only header button.

5. **Lead time / capacity is a field**, not a FAQ. Moser 16 weeks on the PDP. VWS “Crafting Time 6–10 weeks.” Boos “Ships in 4–5 weeks” on the card. Dynamic: “do not fill packets until after consult.” OTBP: dated drop.

6. **No slider hero.** One Green World’s Revolution Slider is the failure mode. Moser one piece. Care to Speak one H1. OTBP one line (“Find Your Flavor”).

7. **Whitespace is margin, not empty sections.** Full-bleed photo, then a 640–720px measure for words. figroots `boxed-layout wrap-boxshadow` fights this — turn box-shadow **off** on BBF and on any fig shop templates.

8. **Photography is the product.** Wood grain / joinery / fruit on the tree / a real clinician. Cyclorama + stock oak = instant 6.

---

## OceanWP BBF (furniture)

Map to Customizer / Ocean modules. Do not rebuild Dawn.

### Header

- **Style:** Medium or Default, logo left or center. Logo max ~180px (VWS).
- **Ocean Sticky Header:** on. Shrink height, do not hide. Transparent only if the first hero is a full-bleed wood photo (Moser). figroots already uses `transparent-header` + `effect-ten` — fine for Learn, too glassy for a price-forward furniture PLP. BBF shop pages: **solid header**, sticky.
- **Top Bar:** left = brand line *or* “In the shop now”; right = `tel:` + Contact. Color: a workshop dark (VWS `#263a2f` is the right *idea*, not the right hex unless it matches BBF paint).
- **Mega Menu (Ocean):**  
  - Column 1 — Form (Seating / Tables / Storage / Surfaces)  
  - Column 2 — Room (Dining / Living / Kitchen / Shop)  
  - Column 3 — one photo tile (the current piece or the set)  
  Stickley/VWS prove photo menus work. Boos proves a **short** product-family nav works if BBF is mostly islands/boards — pick one IA, do not run both.

### Type + color (Customizer → Typography)

- Headings: a real display serif (Adobe/Typekit if Keith already pays; else a single paid face — not another Google pair). Body: a grotesque (something in the Haas / Mr Eaves neighborhood). Buttons: same as body, weight 600, little or no tracking.
- Buttons: one fill (dark), one outline. No rounded-pill Woo defaults.

### Home (Elementor once, or Ocean Gutenberg blocks)

Section order, Moser + VWS:

1. Hero — **one piece**, name, one sentence, Shop / See wood.
2. Promise row — three tiles only: Made here / Guarantee / Lead time (VWS).
3. Shop doors — **In the shop now** | **Made to order** (Stickley dual path, Moser Quick Ship).
4. Workshop / maker (not “Our Story” lorem).
5. Journal *last*.

No Labor Day H1. No six stacked campaigns (Boos home) unless there are six true product families.

### Woo PLP

- Boos: **wood filter before the grid** (“Choose your wood”). Ocean Woo filter widgets at the *top*, not a leftover sidebar.
- Cards: photo, name, one sentence, **price range**, lead time if it is not immediate. Quick Shop (Boos) via Ocean Woo Popup *only* if variants are wood/size — not if every piece is a consult.
- Collection intro: 80–120 words (VWS cherry dining PLP; Trees of Antiquity fig PLP).

### Woo PDP (the 9.5 page)

Clone this information architecture, not the Shopify markup:

1. Gallery (large, zoom, wood-change swaps image).
2. Title, maker line.
3. **Sticky buy column** (Ocean Woo sticky or a small custom CSS `position: sticky` on `.woocommerce div.product .summary` — Moser `.sticky-element`).
4. Variant: wood × size. First option is the photographed one. Base price names that config (VWS: “40×72 natural cherry”).
5. **Crafting time** as a labeled row.
6. Add to cart. Secondary: Request sample / Ask a question.
7. Accordion: Specs · Wood & finish · Care · Shipping. Moser order.
8. Guarantee + “one maker” mark.
9. Matching pieces.

**Samples:** a Woo product “Wood sample pack” (VWS “See Samples”). This is the highest-trust widget we can ship without a showroom.

**Quick Ship:** Woo category or tag `in-shop-now`, menu item, home door. Moser collection rules are inventory + tag — do the same so the door never shows empty.

### Chrome to turn off

- Ocean “boxed + box shadow.”
- Woo breadcrumb junk on the hero.
- Related products that are “people also bought” noise. Related = same collection (Moser Pasadena strip).
- Wishlist unless BBF sells boards/oil (Boos).
- Sale badges as a design system.

### Pages that must exist (URLs, not blog posts)

- `/guarantee/` (VWS lifetime page)
- `/lead-times/`
- `/wood/` or `/samples/`
- `/care/`
- `/trade/` if designers buy
- `/shipping/` with white-glove vs freight named (Stickley $299 is the *habit* of naming the number)

---

## GeneratePress therapy

GP Premium Elements + Blocks. No Woo. No Elementor unless a landing is already built — GP can do this cleaner than Care to Speak’s Elementor kit.

### Header Element

- Left: wordmark.
- Center: Services · How it works · Team · Insurance · Client Center.
- Right: `tel:` link + button **Schedule**.
- Optional one-line top bar: accepting / waitlist / telehealth-only (Ms. Paula, Idaho Voice).
- Sticky. Solid background after 8px scroll. Do not transparent-over-a-stock-smile.

### Type

- Inter or Source Sans for UI. One display (Lexend, or a quiet serif for H1 only). Idaho Voice is the calm target. Dynamic’s four-font stack is the ceiling we do not cross.

### Home sections (GenerateBlocks)

1. H1: `{Pediatric / Adult / Lifespan} speech-language therapy in {place}`. Care to Speak’s literal H1 is the template.
2. Credential line: `{Name}, M.S., CCC-SLP · {State} license · [ASHA ProFind](https://www.asha.org/profind/)`. Above the button.
3. Button: Schedule a consult (Calendly / SimplePractice / Jane). Phone repeats.
4. Three or four **modes** that are true (tele / in-home / clinic / school).
5. How it works — four steps (Ms. Paula): Consult → Forms → Eval → Therapy. Dynamic’s rule as helper text: forms **after** consult.
6. Team.
7. Insurance as a short page teaser, not logos of plans you are not on (Expressable is a product company; we are not).

### Client Center (new GP page template)

Copy Dynamic + Ms. Paula, fix the hosts:

1. Schedule consult (embed or outbound scheduler).
2. Pediatric packet | Adult packet — **outbound to FormDr / Jotform HIPAA / SimplePractice**. On-page sentence: vendor name + “encrypted in transit and at rest.”
3. Bold: do not open packets until the consult is done.
4. What happens next (benefits email, timeline).
5. FAQ: cost, medically necessary vs elective, session length.

**Never on GP pages:** DOB, subscriber ID, school, diagnosis textareas, file upload of IEPs. That is PHI. Google Forms is a fail (Ms. Paula adult link on this pass).

### Trust without a chatbot

- NPP and Privacy as footer URLs (Idaho Voice has `/notice-of-privacy`, `/privacy`).
- Named trainings, three max per clinician (Dynamic’s menu is the upper bound).
- Reviews: a count + a link to Google, not a widget that eats the header (Dynamic’s badge is OK *near forms*; Trustindex in the hero is not).

### Do not install

- Woo.
- “Patient portal” plugins on this WP.
- Chatbots that invite a developmental history.
- Shopify (Hummingbird’s consult SKU).

---

## Figs — OceanWP (current) + Woo, or GP shop later

figroots is already OceanWP. Finish the store **on this theme** before anyone proposes a GP rebuild.

### Keep

- Tutorial IA (`/rooting/` and children). Sticky header plugin.
- PapaFig voice. Flavor sentences on fruit photos.

### Change (Customizer / Woo)

- **Unbox** the layout on Shop templates (`boxed-layout` off).
- Replace Chela One on product titles. Instrument Sans (OTBP) or the BBF grotesque if we want one foundry across shells.
- Header Shop + cart. Ocean Woo mini-cart. Learn stays in the mega.

### Woo IA (OTBP + Antiquity)

```
Shop
  Plants
  Cuttings
Learn (existing)
Shipping
Contact
```

Attributes: `flavor`, `origin`, `hardiness`, `form` (plant|cutting), `size`. Facets at the **top** (OTBP sticky toolbar).

Fig PLP: 100–150 word husbandry block, then in-stock first. OOS can remain with **Email when available** (One Green World button). Do not make OOS the default sort (Trees of Joy).

PDP: cultivar, synonym, flavor, zone, ship window, size, qty, waitlist.

**Drops:** a page with a date and a time (OTBP FAQ). Until then, do not advertise 300 varieties.

**Shipping:** contiguous US / no-ship states on the home (OTBP, Freire no-CA). Live plants: “roots moist,” box time, summer holds.

### Split later (only if Learn and Shop fight)

- `figroots.com` = OceanWP Learn.
- `shop.…` = GP + Woo.  
Not two themes on one URL. Not a Freire “store under construction.”

---

## Implementation order (Website Builder, staged)

1. **Tokens** — two fonts, four weights, three colors, one button, header height. Write them in the child CSS, not in a page.
2. **Chrome** — top bar + sticky + primary action. BBF: cart. Therapy: Schedule. Figs: cart.
3. **Home** — one hero, no slider.
4. **BBF PDP + samples + in-shop-now.** Therapy **Client Center** with outbound HIPAA. Figs **plant/cutting fork + one in-stock collection.**
5. **Mega / facets.** After the PDP/intake works.
6. Kill boxed-shadow, extra stickies, and every Google font not in the token file.

Critics: if a mock adds a font, a slider, or a WP intake field, it is not a 9.5 and it is not this pack.

---

## Cross-walk (steal → control)

| Steal | From | OceanWP BBF | GP therapy | Figs |
|---|---|---|---|---|
| One-piece hero | [Moser](https://www.thosmoser.com/) | Home section 1 | — | — |
| Brand-line top bar | Moser announcement | Ocean Top Bar | Optional | Optional |
| Sticky buy column | Moser PDP | `.summary { position: sticky }` | — | Same on Woo PDP |
| In-stock door | Moser Quick Ship, [Stickley Buy Online](https://www.stickley.com/collections/buy-online) | Tag + menu | — | In-stock facet |
| Named delivery $ | [Stickley delivery](https://www.stickley.com/pages/delivery-shipping) | `/shipping/` | — | `/shipping/` |
| Phone in chrome | [VWS](https://vermontwoodsstudios.com/) | Top bar | Header | Header |
| Samples SKU | [VWS Audrey](https://vermontwoodsstudios.com/products/audrey-solid-top-dining-table) | Woo product | — | — |
| Crafting time field | VWS PDP | PDP meta | — | Ship window |
| Wood-first PLP | [Boos furniture](https://www.johnboos.com/collections/furniture) | Filter bar | — | Flavor/origin bar |
| Quick Shop sentence | Boos cards | If variants are simple | — | No — cuttings need the fork |
| Credentials before CTA | [Care to Speak](https://caretospeakspeech.com/) | Maker line | Hero | Grower line |
| Procedures as cards | [Idaho Voice](https://idahovoiceswallowcenter.com/) | — | Services | — |
| Consult then packet | [Dynamic forms](https://dynamicsltherapy.com/client-information/forms/) | — | Client Center | — |
| Numbered Client Center | [Ms. Paula](https://mspaulaslp.com/client-center/) | — | Template | — |
| Flavor + origin nav | [OTBP](https://offthebeatenpathnursery.com/) | Room + form | — | Mega |
| Plant / cutting fork | [OTBP plants+cuttings](https://offthebeatenpathnursery.com/pages/fig-plants-cuttings) | — | — | Two cats |
| Husbandry on PLP | [TOA figs](https://www.treesofantiquity.com/collections/fig-trees) | Collection intro | — | Fig intro |
| Waitlist button | [One Green World](https://onegreenworld.com/) | — | — | OOS |

---

## Out of scope

- Publishing. Keith clicks cPanel.
- Cloning Shopify Liquid into the child theme.
- PHI, portals, FigBid bidding, sale-as-personality.
- A third theme “because the peer used it.”
