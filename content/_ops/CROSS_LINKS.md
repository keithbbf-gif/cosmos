# Cross-links — theme menus + footer maps (staged)

**Status:** staged ops map only. Not live WordPress/GP/Ocean config. Not COSMOS product docs.

**Upstream:** house rules in [`content/_seo/INDEX.md`](../_seo/INDEX.md); lane detail in [`content/_seo/*-pillars.md`](../_seo/); monthly ship targets in each pack [`INDEX.md`](../figroots-blog/INDEX.md) **Publish queue** section (wired in PR #283).

**Machine import:** optional [`menu-import.json`](menu-import.json) for GeneratePress (GP) and OceanWP (Ocean) primary + footer menu locations. Import is manual — validate URLs on staging before production.

---

## Implementer rules (non-negotiable)

1. **Natural links only.** Body copy links when the sentence needs the next page. Menus list **hubs**; hubs list **clusters**. Clusters link **up** to one hub and at most **two** sibling clusters when the reader’s next job is obvious.
2. **Max two “related” in footer** (per page template). No blogrolls, no “partner” rows, no eight-link SEO footers.
3. **No reciprocal obligation.** If page A links B in prose, B does not owe A a matching block.
4. **Therapy ≠ supplements.** No menu item, footer, or cross-property link between WOW Therapies / SLP WOW and the supplements/herbal lane. Ever.
5. **AI public ≠ COSMOS.** The public AI blog never links to `github.com/keithbbf-gif/cosmos`, GitLab cosmos, KDash, MOTIF, Crucible, patents, or any `docs/` path. Industry/history packs restate this in YAML — menus must not leak internals.
6. **Cross-lane is rare.** See [`content/_seo/INDEX.md`](../_seo/INDEX.md) cross-lane table. Default: stay in-lane.

When a publish-queue row says **gap**, do not invent a menu URL — use a `#` placeholder in JSON or omit until the hub ships.

---

## How menus relate to publish queues

Each pack `INDEX.md` **Publish queue (Oct 2026 – Sep 2027)** names the next hub/cluster to ship. After a piece goes live:

1. Add or unhide the cluster in the **primary** menu only if it is a standing hub (not every blog post).
2. Update the **hub** page’s in-body cluster list (table of contents).
3. Set that hub’s **footer related** (≤2) to the two clusters the queue says are next — not the whole calendar.
4. Refresh this file if the canonical slug changed.

---

## figroots.com

**Theme:** GP or Ocean — shallow primary nav; history split from grow.

### Primary menu (staged)

| Order | Label | URL | Parent | Notes |
| ---: | --- | --- | --- | --- |
| 1 | Home | `/` | — | Tiles stay the door |
| 2 | Grow | `/grow/` | — | **gap** until hub ships; interim target `/an-introduction-to-figs/` |
| 3 | Rooting | `/rooting/` | Grow | Live hub |
| 4 | Pests & disease | `/pest-control/` | Grow | Live hub |
| 5 | Pick a fig | `/2025/07/02/pick-the-right-fig-for-you/` | Grow | Live chooser hub |
| 6 | History | `/2025/02/20/history-of-figs/` | — | Expand to `/history/` when canonicalized |
| 7 | About | `/an-introduction-to-figs/` | — | Optional; collapse into Grow when `/grow/` exists |

Do **not** put all 40 blog slugs in the menu. Draft slugs from [`figroots-blog/INDEX.md`](../figroots-blog/INDEX.md) surface via hub lists and publish month, not nav.

### Footer menu (site-wide, staged)

| Column | Links (max 2 per column) |
| --- | --- |
| Grow | Rooting · Pest control |
| History | History of figs · Types of figs (`/2025/08/17/types-of-figs/`) |
| Trust | Introduction (independence / no affiliates) · Contact if live |

**Cross-lane:** one optional sentence on a **shop-as-building** craft article (furniture) — not in FigRoots footer. **Never** supplements.

### Hub → cluster footer “related” (templates)

| Hub | Related (max 2) |
| --- | --- |
| `/grow/` (future) | `/rooting/` · `/2025/07/02/pick-the-right-fig-for-you/` |
| `/rooting/` | Sanitize protocol (`/2026/02/28/sanitizing-hydrating-and-inoculating-fig-cuttings-prior-to-striking/`) · Potting mix (**gap** → `fig-potting-mix-that-drains` when live) |
| `/pest-control/` | Spider mites cluster (**gap**) · Black fig fly (**gap**) |
| History hub | Ancient-to-today spine · Caprification / types |

---

## slpwow.com (SLP WOW — clinicians)

**Audience:** SLPs, grad students. **Not** the clinic phone in the hero.

### Primary menu (staged)

| Order | Label | URL | Parent | Notes |
| ---: | --- | --- | --- | --- |
| 1 | Home | `/` | — | Three promises: news, talk, resources |
| 2 | News | `/blog/` | — | Purge theme-demo posts first (queue 2026-10) |
| 3 | Free resources | `/free-slp-resources/` | — | Tools hub rewrite (queue 2026-12) |
| 4 | Report templates | `/free-slp-resources/free-slp-report-templates/` | Free resources | Drop cart chrome if empty |
| 5 | Forum | `/forum/` or live path | — | **Hide** from menu if threads are dead |

No “Clinic” top-level item. No supplements. No COSMOS / AI blog.

### Footer menu (staged)

| Column | Links (max 2) |
| --- | --- |
| Tools | Free resources · Report templates |
| About | One About page (**gap**) · ASHA link-out (external) |

**Cross-lane:** About may include **one** link to WOW Therapies as Christina’s practice — not reciprocal sitewide.

### Hub → cluster footer “related”

| Hub | Related (max 2) |
| --- | --- |
| `/blog/` (policy) | ASLP-IC living page · Latest MPFS note |
| `/free-slp-resources/` | Report templates · One research note that changed a template |

Speech-pathology **history pack** essays are **not** menu items unless spun out as a dated “From the archive” post with its own URL on slpwow.com.

---

## wowtherapies.com (clinic — parents & referrals)

**Audience:** caregivers, adult patients, referral sources. **HIPAA-safe.**

### Primary menu (staged)

| Order | Label | URL | Parent | Notes |
| ---: | --- | --- | --- | --- |
| 1 | Home | `/` | — | Mission + access |
| 2 | Services | `#` | — | Parent only until child URLs exist |
| 3 | Early childhood | `/early-childhood/` | Services | **gap** (queue 2026-12) |
| 4 | School age | `/school-age/` | Services | **gap** |
| 5 | Adults | `/adults/` | Adults | **gap** |
| 6 | Do we need therapy? | `/does-my-child-need-speech-therapy/` | — | **gap** (queue 2026-11) — working slug |
| 7 | Contact | `/contact/` | — | Counties, hours, (870) 820-8333 |

Do **not** menu the psychotherapy **history pack** ([`wowtherapies-therapy-history/INDEX.md`](../wowtherapies-therapy-history/INDEX.md)) on the clinic site — wrong lane for parent IA.

### Footer menu (staged)

| Column | Links (max 2) |
| --- | --- |
| Services | Early childhood · Contact |
| Access | About / access page (**gap**) · How to refer (BHSM page when live) |

**Cross-lane:** About may name SLP WOW once for clinician-facing writing. **Never** supplements, FigRoots, furniture, AI blog, COSMOS.

### Hub → cluster footer “related”

| Hub | Related (max 2) |
| --- | --- |
| Early childhood | Parent guide (need therapy?) · Contact |
| School age | Back-to-school “what to ask” (**gap**) · Contact |
| Adults | Swallow eval expectations (**gap**) · Contact |

---

## BBF / bbfur (furniture — Saline River Workshop today)

**Surface:** future `bbfur` IA; Etsy/Instagram checkout until shop hub exists. Packs: [`furniture-craft-blog`](../furniture-craft-blog/INDEX.md), woods, fashion, history.

### Primary menu (staged)

| Order | Label | URL | Parent |
| ---: | --- | --- | --- |
| 1 | Home | `/` | — |
| 2 | Work | `/work/` | — |
| 3 | Woods | `/woods/` | — |
| 4 | Fashion | `/fashion/` | — |
| 5 | History | `/history/` | — |
| 6 | Shop | `/shop/` | — |

All **gap** until first site ship; publish queues in each furniture pack INDEX.

### Footer menu (staged)

| Column | Links (max 2) |
| --- | --- |
| Craft | Work · Woods |
| Room | Fashion · History |

**Cross-lane:** one FigRoots link only on a **shop building / winter bay** article body — not footer. **Never** therapy or supplements.

---

## AI public blog (domain TBD)

Packs: [`ai-industry-blog/INDEX.md`](../ai-industry-blog/INDEX.md), [`ai-history-retrospective/INDEX.md`](../ai-history-retrospective/INDEX.md). Pillars: [`ai-public-pillars.md`](../_seo/ai-public-pillars.md).

### Primary menu (staged)

| Order | Label | URL | Parent | Notes |
| ---: | --- | --- | --- | --- |
| 1 | Home | `/` | — | Two-hub promise |
| 2 | Industry | `/industry/` | — | **gap** (queue 2026-10) |
| 3 | History | `/history/` | — | **gap** (queue 2026-10) |
| 4 | About | `/about/` | — | Scope + **refusals** (no COSMOS) |

No FigRoots, furniture, therapy, supplements in menu.

### Footer menu (staged)

| Column | Links (max 2) |
| --- | --- |
| Read | Industry hub · History hub |
| Boundaries | About (what we do not cover) · External: primary source you cite most often |

### Hub → cluster footer “related”

| Hub | Related (max 2) |
| --- | --- |
| `/industry/` | Latest *What shipped* · Latest *Refusal and error* |
| `/history/` | Previous spine node · Next spine node (series nav only) |

Industry posts link history **only** when the analogy is the point (one in-body link). **Zero** COSMOS/github/gitlab/docs links.

---

## Supplements / R&D + herbal history (domain TBD)

Packs: [`supplements-rd-blog/INDEX.md`](../supplements-rd-blog/INDEX.md), [`herbal-medicine-history-blog/INDEX.md`](../herbal-medicine-history-blog/INDEX.md). Pillars: [`supplements-pillars.md`](../_seo/supplements-pillars.md).

### Primary menu (staged)

| Order | Label | URL | Parent |
| ---: | --- | --- | --- |
| 1 | Home | `/` | — |
| 2 | R&D / lab | `/rd/` | — |
| 3 | Herbal history | `/history/` | — |
| 4 | About | `/about/` | — | Claims guard in first screen |

### Footer menu (staged)

| Column | Links (max 2) |
| --- | --- |
| Methods | R&D hub · One methods cluster |
| History | Herbal history hub · One dated cluster |

**Cross-lane:** fig **history** on FigRoots may link herbal history **once** in prose on the history hub — not grow pages, not footer. **Never** WOW Therapies / SLP WOW. **Never** COSMOS.

---

## Cross-lane matrix (menus + footers)

| From | To | Menu/footer? | Condition |
| --- | --- | --- | --- |
| FigRoots | Furniture | Footer **no** | Body only on shop/climate piece |
| FigRoots | Herbal history | Footer **no** | History hub, one in-body link max |
| SLP WOW | WOW Therapies | Footer **no** | About only, one link |
| WOW Therapies | SLP WOW | Footer **no** | About only, one link |
| Any | AI public | **No** | Unless public cited tool in a news note (one link) |
| Any | Supplements | **No** | Except fig history → herbal history (hub, once) |
| Therapy (either) | Supplements | **Never** | — |
| AI public | COSMOS / mesh | **Never** | — |

---

## GP / Ocean import checklist

1. Create **Primary** and **Footer** menu locations in WP (GP: Appearance → Menus; Ocean: same + theme hook).
2. Import from [`menu-import.json`](menu-import.json) or paste rows manually — JSON uses `theme_notes` per stack.
3. Assign menus to locations; do not auto-add new top-level pages to primary (GP “Auto add pages” off).
4. After each publish-queue month, diff live URLs against pack INDEX **Status** column; update hub related footers only.

---

## Changelog

| Date | Change |
| --- | --- |
| 2026-09-14 | Initial staged menus + footers from SEO pillars and pack publish queues (PR #283 follow-on). |
