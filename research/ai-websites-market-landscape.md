# AI websites: market landscape and opportunity brief

**Status:** research brief, not a product spec  
**Research date:** 2026-09-14  
**Scope:** products that help people **build, host, or operate websites with AI** — builders, landing-page tools, CMS/content sites, SEO/site agents, no-code generators, redesign/audit tools, and adjacent prompt-to-app builders when they are used for sites.  
**Not:** legal, investment, or financial advice. Figures below are cited as published; several TAM numbers are **soft** (paywalled syndicated reports with inconsistent methodology). Prefer company filings and first-party product pages over those estimates.

---

## How to use this brief

1. Treat **generation of a first site** as commoditized. Incumbents (Wix, Squarespace, Hostinger, WordPress.com, GoDaddy) already ship prompt-to-site plus hosting, domain, and a free-to-paid gate.
2. Treat **post-launch operation** (editability, SEO/AEO, brand uniqueness, code ownership, agency throughput) as the contested layer.
3. Ranked opportunities in §7 are **hypotheses**. §8 is the cheapest way to kill or confirm them.

---

## 1. Category map — what “AI websites” means

“AI websites” is not one product. It is a **stack of jobs** that used to be separate (design, copy, CMS, hosting, SEO, analytics) now sold as a conversation plus a hosted site.

### 1.1 Subsegments

| Subsegment | Job | Typical output | Examples (not exhaustive) |
|---|---|---|---|
| **Incumbent AI builders** | First site for a person or SMB, then lock into a hosted OS | Hosted site + apps (store, bookings, email) | Wix Harmony / Aria; Squarespace Blueprint AI; Hostinger AI Builder; GoDaddy Airo; WordPress.com AI Website Builder |
| **Design-first site platforms** | High-taste marketing / brand sites with a visual canvas | Hosted marketing site + CMS | Framer Agents; Webflow AI site builder + Flowkit |
| **AI-first SMB launchers** | “Site in 30 seconds” plus lightweight business ops | Simple site + CRM / invoicing / bookings | Durable |
| **WordPress / portable CMS AI** | Generate a real CMS site you can leave with | WordPress install, often on vendor hosting | 10Web; Elementor AI / Site Planner; ZipWP; Bluehost AI |
| **Agency production tools** | Brief → sitemap → components → many client sites | Figma/Webflow/Relume host, or white-label CMS | Relume; Duda Vibe; 10Web Agency |
| **Motion / experiential** | Scroll, 3D, campaign microsites | Hosted visual site | Dora |
| **Ecommerce OS + AI** | Store, not brochure | Checkout + catalog + ops | Shopify Sidekick / Magic; Wix/Squarespace stores |
| **Prompt-to-app (used for sites)** | Landing page *or* full-stack product | React/Next code, often GitHub + hosted preview | Lovable; v0; Bolt.new; Replit Agent; Wix Base44; Hostinger Agentic / Horizons; Cursor / Claude Code |
| **Headless / enterprise experience layer** | Marketers edit a live app on an existing design system | Visual CMS on your repo | Builder.io |
| **SEO / AEO / site agents** | Make an *existing* site findable and maintainable | Fixes, content, schema, crawler access | Surfer; Alli AI; Framer/Webflow AEO features; Durable SEO & GEO |
| **Audit / redesign / clone** | Diagnose or restyle a live URL | Report, or a new generated site | 10Web redesign/clone agents; generic PageSpeed/Lighthouse; agency audit products |

### 1.2 Adjacent but different

- **AI copy/image tools** (Jasper, Canva, Adobe Firefly) feed sites; they are not site products.
- **Traditional CMS** (Contentful, Sanity, WordPress.org) are adding AI; the buyer job is still “operate content,” not “get a site today.”
- **IDE agents** (Cursor, Claude Code, Codex) are the high-skill path to *owning* a site. Framer now treats them as **external agents** that can edit a Framer project without burning Framer AI credits ([Framer, 2026-06-16](https://www.framer.com/blog/ai-credits-simpler-plans-and-lower-prices/)).

### 1.3 The real competitive axis

Not “does it have AI?” — almost all do. The axis is:

```
Speed to first draft  ──────────────────────────────────►  Durable site you can operate
Template + LLM        Design system + canvas             Code + Git + your host
Hosted lock-in        Hybrid visual + chat               Export / WordPress / repo
```

Most consumer products optimize the left. The white space is the **right two-thirds after week one**.

---

## 2. Market size and growth (cited; flag soft numbers)

### 2.1 What we can treat as hard-ish

These are **company-reported** (still not audited line items for “AI websites” as a category):

| Signal | Figure | Date / source |
|---|---|---|
| Wix Q2 2025 revenue | **$489.9M**, +12% y/y; FY 2025 revenue outlook **$1.975–2.000B** | Wix Q2 2025 results, filed 2025 ([SEC exhibit](https://www.sec.gov/Archives/edgar/data/1576789/000162828025038117/secondquarter2025.htm)) |
| Wix Q2 2026 revenue | **$563.1M**, +15% y/y; total ARR **$1.963B** (+15% y/y) | Wix Q2 2026 results, 2026-08-04 ([SEC exhibit](https://www.sec.gov/Archives/edgar/data/1576789/000162828026052108/secondquarter2026results.htm)) |
| Wix Partners (agencies / resellers) | Q2 2026 **$213.8M**, +17% y/y | Same filing |
| Wix Base44 (vibe-coding / apps, acquired 2025) | Management: **$40–50M ARR** by end of 2025 (from “a few million” at acquisition) | Wix Q2 2025 earnings call transcript, Motley Fool dated 2025-12-23 ([transcript](https://www.fool.com/earnings/call-transcripts/2025/12/23/wix-wix-q2-2025-earnings-call-transcript/)) |
| Lovable ARR / funding | **$200M ARR** (2025-11); **$330M Series B at $6.6B** (company blog); **~$400M ARR** (Feb 2026, confirmed to TechCrunch); **$500M annualized run rate** (2026-06) | [Bloomberg 2025-11-18](https://www.bloomberg.com/news/articles/2025-11-18/lovable-hits-200-million-arr-and-raising-funds-above-6-billion-valuation); [Lovable Series B](https://lovable.dev/blog/series-b); [TechCrunch 2026-03-11](https://techcrunch.com/2026/03/11/lovable-says-it-added-100m-in-revenue-last-month-alone-with-just-146-employees/); [TechCrunch 2026-06-09](https://techcrunch.com/2026/06/09/lovable-says-it-has-hit-500m-in-annualized-revenue-with-1-million-new-projects-a-week/) |

**Uncertainty:** Lovable figures are **company-disclosed ARR / run-rate**, not a 10-K. Wix does **not** break out “AI website builder” revenue separately from Creative Subscriptions. Base44 is **apps**, not classic sites — relevant as the incumbent’s answer to Lovable, not as a TAM for brochure sites.

Wix’s own commentary is useful as a **direction signal**, not a TAM: “Demand for AI-powered online creation continues to accelerate” and vibe coding is framed as a 2026+ growth driver (Q2 2025 CEO remarks, same SEC exhibit).

### 2.2 Syndicated “AI website builder market” estimates — **soft**

These reports **disagree with each other** on 2025 size by more than $1B and on 2033–2035 endpoints by >2×. Treat as **order-of-magnitude / marketing-grade**, not planning numbers.

| Publisher | 2025 | 2026 | Far year | CAGR | Source date |
|---|---|---|---|---|---|
| Precedence Research | **$2.69B** | **$3.24B** | **$17.43B (2035)** | 20.55% (2026–2035) | Updated **2026-02-25** ([report page](https://www.precedenceresearch.com/ai-powered-website-builder-market)) |
| Custom Market Insights | **$2.87B** | **$3.41B** | **$14.78B (2035)** | 17.7% (2026–2035) | Published **2026-08-14** ([report page](https://www.custommarketinsights.com/report/ai-powered-website-builder-market/)) |
| The Business Research Company (via Research and Markets) | **$3.51B** | **$4.19B** (19.7% y/y) | **$8.66B (2030)** at 19.9% | Historic + forecast | Report dated **May 2026** ([listing](https://www.researchandmarkets.com/reports/6241469/ai-powered-website-builder-global-market-report)) |
| Market.us | **$3.17B (2023)** | — | **$31.5B (2033)** | 25.8% (2024–2033) | [Report page](https://market.us/report/ai-powered-website-builder-market/) (accessed 2026-09-14) |
| WiseGuyReports | **$3.75B (2025)**; also cites **$3.1B (2024)** — and elsewhere on the same page **$1.5B (2024)** | — | **$25B (2035)** | 20.9% | [Report page](https://www.wiseguyreports.com/reports/ai-website-builder-market) (accessed 2026-09-14; **internally inconsistent**) |
| Technavio (via GII) | Incremental **$10.88B** over 2024–2029 | — | — | 32.8% | Published **2026-01-19** ([GII listing](https://www.giiresearch.com/report/infi1915631-global-ai-powered-website-builder-market.html)) |

**Why they are soft**

- Definitions mix **hosted website SaaS**, **AI feature attach**, **agency tools**, and sometimes **vibe-coding app builders** (Precedence’s company list includes Lovable and Bolt.new).
- CMI says AI builders were **23.6% of the “total website builder market” in 2024**, up from ~**11% in 2022** ([CMI, 2026-08-14](https://www.custommarketinsights.com/report/ai-powered-website-builder-market/)). That share claim is **not independently audited** here. It also sits awkwardly next to other CMI pages that put the *entire* website-builder software market in a similar billions band — a sign the TAMs are not a single consistent census.
- Cloud/SaaS shares (Precedence ~**81%** cloud in 2025; CMI ~**87%**) are plausible as *direction* (almost all products are SaaS) but should not be used as precision.

**What is safe to say**

- The **category is growing quickly** (high-teens to ~20% CAGRs are the cluster; 25–33% is the optimistic tail).
- **North America** is the largest reported region (Precedence ~**43%** in 2025; CMI **38%** in 2025). **Asia-Pacific** is the usual “fastest CAGR” call-out.
- **SME / business sites** dominate volume (Precedence: business websites ~**57%** in 2025; CMI: SMEs ~**49%** in 2025). Ecommerce is the usual “fastest application” call-out.
- **Installed-base gravity** still sits with WordPress + Wix + Squarespace, not with 2024-vintage AI startups. Statista’s 2024 website-builder share table (published 2025-11-28) ranks **WordPress.org first**, then Wix and Squarespace — percentages paywalled ([Statista](https://www.statista.com/statistics/818598/worldwide-website-builders-market-share/)).

### 2.3 Adjacent money that *is* real

The vibe-coding / prompt-to-app market is **larger and faster** than “AI brochure sites” in disclosed revenue, but it is a **different buyer** (founders shipping apps, not dentists needing a phone number). Do not add Lovable’s run-rate to a website-builder TAM. Do use it as evidence that **credit-metered, Git-exportable, conversational web creation** has proven willingness to pay.

---

## 3. Notable players — positioning

Prices are **as retrieved 2026-09-14** unless a source date is given. They move; confirm on the live pricing page before any commercial use.

| Player | Positioning | Who they sell to | AI motion | Hosting / export | Pricing pattern (indicative) | Notes |
|---|---|---|---|---|---|---|
| **Wix** (Harmony, Aria; ADI retired) | All-in-one business OS. Hybrid **vibe + drag-and-drop**. | Consumer, SMB, Wix Studio partners | Prompt → production-ready site; Aria in editor + dashboard; marketing agent | **Wix-hosted**; no meaningful code export | Free → Light **$17/mo** … Business Elite **$159/mo** annual ([Wix blog](https://www.wix.com/blog/how-much-is-a-wix-website); [Website Builder Expert 2026 AI list](https://www.websitebuilderexpert.com/website-builders/wix-ai-features/)) | **ADI sunset 2024-11-10** ([Wix Help](https://support.wix.com/en/article/adi-sites-no-longer-supported)). Harmony announced **2026-01-21** ([Search Engine Journal](https://www.searchenginejournal.com/wix-introduces-harmony-ai-website-builder/565505/)). Base44 is the app/vibe flank. |
| **Squarespace** | Design-taste + Blueprint AI as *guided* first draft | Creatives, service SMBs, some ecommerce | Questionnaire / brand personality → draft; AI Writer | **Squarespace-hosted** | Blueprint AI **free to generate**; **paid plan to publish** ([Squarespace AI page](https://www.squarespace.com/websites/ai-website-builder)) | Positions against “generic and cluttered” AI sites. Desktop-only AI flow as of retrieval. |
| **Framer** | Designer-grade canvas + **Agents** + CMS + hosting | Designers, startups, agencies | Wireframer / Workshop (2025-05); Agents + credits (2026-06) | **Framer-hosted**; custom domain on paid; external agents via MCP | Free; Basic **$10/mo**; Pro **$30/mo**; editors **$20**; 1k/3k AI credits ([pricing](https://www.framer.com/pricing); [blog 2026-06-16](https://www.framer.com/blog/ai-credits-simpler-plans-and-lower-prices/)) | [Business Wire 2025-05-21](https://www.businesswire.com/news/home/20250521574932/en/Framer-Launches-AI-Features-to-Supercharge-Web-Design-Democratizing-How-Stunning-Websites-are-Built). Strong AEO/SEO product surface. |
| **Webflow** | Professional site + **design system (Flowkit)** + CMS | Agencies, marketing teams, enterprise | Prompt → multi-page draft on Flowkit; AI Assistant (sections, CMS) | **Webflow-hosted**; custom domain on paid Site plan | Site plans (confirm live); AI often bundled / credit-limited | AI Assistant announced **2024-10-15** ([Webflow Updates](https://webflow.com/updates/webflow-ai-assistant)). Explicit **AEO** product line. |
| **Hostinger** | Cheap hosting bundle + AI Builder (manual + **agentic vibe**) | Price-sensitive SMBs, global long-tail | Prompt → site; chat to change; SEO assistant | **Hostinger-hosted**; agentic mode claims source-code access | Intro **$2.99/mo** / 48-mo Premium; **renews ~$10.99/mo** ([Hostinger AI page](https://www.hostinger.com/ai-website-builder)) | Classic **intro-price GTM**. Credits for prompts. |
| **Durable** | Fastest SMB launch + **site as the front door to ops** | Local / service businesses | ~30-second questionnaire site | **Durable-hosted** | Company pages have listed **Starter ~$12/mo** and **Business ~$20/mo** annual, and elsewhere **Launch ~$25/mo** — **pricing is inconsistent across Durable URLs**; confirm [durable.co/pricing](https://durable.co/pricing) | Claims “10M+ sites built” on marketing pages (unverified). SEO & GEO product. |
| **10Web** | **Agentic WordPress**: generate, clone, Figma, redesign; speed + hosting | SMBs + **agencies (white-label)** | Questionnaire / vibe + Elementor-class editor | **WordPress**; SFTP/SSH; portable-ish | AI Starter **$10/mo** annual; agency tiers to **~$2.50/site** ([pricing](https://10web.io/pricing-platform/)) | Strongest **ownership + reseller** story in the AI-WP lane. |
| **Relume** | Brief → sitemap → wireframe → **library** → Figma/Webflow **or Relume host** | Designers, Webflow agencies | Structure + components + specialist agents | Export **and** `relume.live` / custom domain hosting | Free; Pro from **~$14/mo**; hosting Starter from **~$18/mo** ([pricing](https://www.relume.ai/pricing)) | Evolved from “not a host” to a **hybrid**. |
| **Duda** | Agency / SaaS **white-label** web OS | 22k+ orgs, ~1M sites (company claim, Jul 2026) | AI site gen + Copilot + **Vibe** (apps) | Duda-hosted, client permissions | Agency contracts; Vibe credits after 2026-08-03 ([Duda, 2026-07-22](https://www.duda.co/product-updates/meet-duda-vibe-build-anything-with-ai); [2026-07-15](https://blog.duda.co/duda-expands-ai-2026)) | The agency incumbent most startups forget. |
| **Dora** | Motion / 3D / scroll brand sites | Campaign and brand teams | Prompt + canvas | **dora.run** / paid custom domain | Review sites cite free + ~$14–25/mo; **confirm live** (alpha history) | Weak ecommerce/SEO vs Framer/Webflow. |
| **Bookmark (AiDA)** | Early conversational AI builder | Non-technical SMBs | Chat setup | Hosted | Legacy / simpler plans | Rarely wins 2026 bake-offs; limited customization/SEO in third-party reviews. |
| **GoDaddy Airo** | Domain + hosting **default path** | Domain buyers, solopreneurs | Sub-minute site | **GoDaddy lock-in** (site dies if you stop paying — Elementor comparison) | Websites + Marketing from ~**$10.99/mo** ([Elementor comparison 2026](https://elementor.com/blog/godaddy-airo/)) | Distribution via domains, not design quality. |
| **WordPress.com** | Chat → new WP.com site | Bloggers, freelancers, simple businesses | 30 free prompts, then plan | WP.com host; domain connect | Premium **$96/yr** / Business **$300/yr** for AI-built publish ([TechCrunch 2025-04-09](https://techcrunch.com/2025/04/09/wordpress-com-launches-a-free-ai-powered-website-builder/)) | **New sites only** at launch. No advanced ecommerce in the first version. |
| **Elementor** | WP professionals | Agencies, WP builders | Site Planner + AI credits + Angie | **Your WordPress** | Plugin ~**$60/yr**; Elementor One **$168/yr** with AI credits ([Elementor 2026](https://elementor.com/blog/godaddy-airo/)) | Ownership story vs hosted AI. |
| **Shopify** | Commerce OS | Merchants | Sidekick (launch + operate); Magic for content | Shopify-hosted store | Included in Shopify plans | Sidekick 2.0 autonomous admin workflows reported mid-2026 ([Ecommerce Times](https://ecommerce-times.com/shopifys-new-ai-powered-sidekick-2-0-is-forcing-merchants-to-rethink-their-app-stack/)). Not a brochure-site competitor. |
| **Lovable** | Conversational **full-stack** web apps | Founders, teams | Chat → React + Cloud/Supabase + Git | **Code you own**; GitHub/GitLab sync; download on paid | Free daily credits; Pro from **$25/mo** (100 credits) ([Lovable docs](https://docs.lovable.dev/introduction/subscription-plans)) | Used for landing pages **and** products. Credit = build *and* run. |
| **v0 (Vercel)** | UI / Next / shadcn quality | Developers, product teams | Prompt → React/Next | Deploy on Vercel; code in repo | Free credits; Premium ~**$20/mo** (third-party 2026 summaries; confirm v0.app) | Repositioned toward fuller web apps in 2026. |
| **Bolt.new** | In-browser WebContainer IDE | Prototypers | Prompt → runnable stack | Bolt host / Git / Netlify integrations | Credit / plan based (changes often) | Strong for “see it run now.” |
| **Cursor / Claude Code / Codex** | High-skill site ownership | Developers | Repo agents | **Your host** | IDE / API subscriptions | Framer and others now **import** this skill rather than replace it. |
| **Builder.io** | Visual + agents **on your codebase / design system** | Mid-market / enterprise marketing + eng | Agentic CMS + visual edits as PRs | Your stack | Enterprise sales | The “don’t fork the brand” answer. |
| **Alli AI / Surfer** | Operate visibility after the site exists | SEO teams, agencies, enterprise | Agents, prerender for AI crawlers, content ops | Plugin / SaaS on existing CMS | SEO-tool pricing | Competes with *builders’* shallow SEO checklists. |

**Also-rans / watch list:** Jimdo, IONOS, Mixo, B12, Typedream, Super.so, Dorik, ZipWP, TeleportHQ (code export), Unbounce / Landingi (landing pages + CRO), Mutiny (personalization).

---

## 4. Pricing and GTM patterns

### 4.1 The dominant funnel

Almost every hosted builder uses the same machine:

1. **Free generation** (wow in <5 minutes).
2. **Subdomain + badge** until you pay.
3. **Custom domain** is the real conversion event (Framer, Wix, Squarespace, Relume hosting, WordPress.com).
4. **Annual prepay** and, for hosts, **48-month intro rates** (Hostinger **$2.99 → ~$10.99** renew).
5. **Feature gates**: ecommerce, collaborators, analytics, removing branding, developer platform.

AI did not change this. It **increased top-of-funnel** and made the free tier more valuable (a complete draft, not a blank editor).

### 4.2 New meter: credits

2025–2026 products increasingly **unbundle inference**:

| Pattern | Who | Implication |
|---|---|---|
| Credits for agents / generation | Framer, Lovable, Hostinger, Relume, Duda Vibe, Elementor AI | **Maintenance is metered.** Users report tiny edits burning credits ([r/webdesign, 2026](https://www.reddit.com/r/webdesign/comments/1tjar1p/ai_website_builders_are_great_until_you_need_to/)). |
| Visual editor is “free” after generation | Wix, Squarespace, Webflow, 10Web | Safer for ongoing SMB use. |
| BYO model / external agents | Framer MCP → Cursor, Claude Code, Codex | Pushes inference cost **off** the site vendor. |
| Seat + site + add-on | Framer editors $20; localization $20/locale; A/B $50/500k events | Classic PLG → team expansion. |
| Per-site agency | 10Web, Duda | Resell margin, white-label, Stripe/PayPal billing. |
| Credits pay for **runtime** too | Lovable Cloud | Confuses “build budget” with “traffic bill.” |

### 4.3 Three GTMs

| Motion | Offer | CAC style | Risk |
|---|---|---|---|
| **Consumer / SMB PLG** | Free site, ads, YouTube, hosting attach | Performance marketing, intro price | Race to $3/mo; high churn; generic output |
| **Agency / partner** | Multi-site, white-label, client login | Sales + partner programs | Wix Partners already **$214M/qtr**; Duda owns the “pro” slot |
| **Developer / founder PLG** | Credits, GitHub, Discord, Twitter | Viral demos, Product Hunt | Credit stickiness; quality ceiling; support load |

### 4.4 Hosted vs export is a **pricing** decision

- **Hosted-only** (Wix, Squarespace, Durable, GoDaddy, most Framer): high LTV, hostage website.
- **Export / WP / Git** (10Web, Elementor, Relume→Webflow, Lovable, v0, Cursor): lower lock-in, must win on **workflow** or **taste**.
- **Hybrid** (Relume host + export; Framer external agents; Hostinger agentic “source access”) is where 2026 products are drifting.

---

## 5. Tech stack trends

### 5.1 Template + LLM is still the volume engine

CMI attributes **~43%** of 2025 AI-builder revenue to **template-based AI** (soft). It matches what ships: a finite section library, LLM-filled copy/images, brand-color pass. Guardrails beat open generation for non-designers (Squarespace says this out loud).

### 5.2 Design systems are the quality fork

- **Webflow Flowkit** — AI output is a **system** (utilities, components, variables), not a one-off page ([Webflow AI site builder](https://webflow.com/ai-site-builder)).
- **Relume library** — hundreds of sections; Figma + Webflow; Client-First compatibility.
- **Framer components + Workshop** — generated components that pick up site tokens.
- **v0 / shadcn / Tailwind** — developer-native system; same “SaaS gradient” risk.
- **Builder.io** — *your* system, not theirs.

Without a system, multi-prompt sessions **drift** (spacing, type, SEO regressions). This is the most repeated practitioner complaint in 2026 Reddit threads ([r/SaaS](https://www.reddit.com/r/SaaS/comments/1ue570z/gaps_in_ai_website_builders/)).

### 5.3 CMS is the “is this a real site?” test

A generated homepage is a demo. A **collection + template + localized locales** is a product. Framer and Webflow compete here; Durable and Bookmark mostly do not. Agentic CMS (Builder: “publish with prompts”) is the enterprise version of the same idea.

### 5.4 Hosting lock-in, domains, and performance

- Custom domain + SSL + CDN is table stakes and the **upgrade hook**.
- Incumbents sell **uptime / multi-cloud** (Wix quotes 99.99%) because AI generation made *creation* cheap; *keeping it up* is the remaining fear.
- Core Web Vitals are a **positioning** claim (Duda, 10Web “90+ PageSpeed”) because AI HTML is often heavy.
- **AEO / AI crawlers** (GPTBot, ClaudeBot, Perplexity) are the 2025–2026 add-on: `llms.txt`, prerender, schema, robots. Webflow and Framer productize this; Alli AI treats it as the whole company.

### 5.5 Two generation architectures

| Architecture | How it works | Strength | Failure |
|---|---|---|---|
| **Constrained composer** | LLM picks sections from a kit, fills slots | Consistent, editable, fast | Same-y sites |
| **Open codegen** | LLM writes HTML/React/WP | Unique layouts, apps | Messy code, credit burn, hard edits |
| **Hybrid (2026 winners)** | Generate into a kit, then visual + chat with shared state | Wix Harmony’s explicit bet | Hard to build; editor/AI desync |

Wix Harmony is the clearest incumbent statement of the hybrid: Aria and drag-and-drop must **share one document** so neither blows up the other ([TechRadar, 2026-01-22](https://www.techradar.com/pro/website-building/wix-launches-harmony-a-hybrid-approach-to-vibe-coding-and-visual-design)).

### 5.6 Inference cost is now a product constraint

Wix Q2 2026: Base44 entered the year at **near-zero non-GAAP gross margin**; they shipped a **purpose-built model (Base 1)** and guided **~60% GM in 2H 2026** ([SEC exhibit](https://www.sec.gov/Archives/edgar/data/1576789/000162828026052108/secondquarter2026results.htm)). That is a tell: **open-ended site/app generation is not a default high-margin SaaS** until you own the model or meter credits tightly.

---

## 6. Buyer jobs-to-be-done and pain

### 6.1 Jobs

| Buyer | Job | What “done” looks like | What they will not do |
|---|---|---|---|
| **Local / service SMB** | Be findable and bookable this week | Domain, NAP, hours, form/booking, looks “real” | Learn Webflow; manage a repo |
| **Founder / indie** | Ship a landing page or MVP that does not look like a template | Convert waitlist / payments | Pay an agency $8k |
| **Marketer** | Campaign pages without a sprint ticket | Live URL, on-brand, analytics | Wait on engineering |
| **Designer / freelancer** | Compress discovery → client-ready structure | Sitemap + wireframes in a day | Rebuild 80 sections by hand |
| **Agency** | Throughput × margin × client login | 10 sites/month, white-label, retainers | Babysit vibe-code spaghetti |
| **SEO / content team** | Traffic from Google **and** AI answers | Rankings, citations, clean HTML | Rebuild the CMS |
| **Developer / product** | Ownable code on a real stack | GitHub + deploy + design system | Another closed editor |
| **Enterprise brand** | Pages on *our* components, with approval | PR + preview + brand tokens | Shadow IT Lovable site |

### 6.2 Pain (repeated across reviews and forums)

1. **Speed is solved; uniqueness is not.** Prompt-to-site defaults to “SaaS startup”: big hero, gradient, three feature cards. Local businesses get a venture-backed costume ([r/ai_website_builder](https://www.reddit.com/r/ai_website_builder/comments/1tgjevo/are_websites_made_from_ai_website_builders/); [r/nextjs](https://www.reddit.com/r/nextjs/comments/1nnnolv/ai_web_builders_are_ruining_the_status_of_design/)).
2. **The last 20%.** Integrations, edge-case logic, real brand, legal pages, multilingual, accessibility. Harmony / Framer / Webflow exist because open vibe tools stall here.
3. **Editability vs credits.** Chat-only products tax every title-tag tweak. Users batch edits or flee to Webflow/HTML export ([r/webdesign](https://www.reddit.com/r/webdesign/comments/1tjar1p/ai_website_builders_are_great_until_you_need_to/)).
4. **Context loss.** Prompt 17 forgets the type scale from prompt 3. Practitioners ask for a **persistent design contract**, not a longer chat ([r/SaaS](https://www.reddit.com/r/SaaS/comments/1ue570z/gaps_in_ai_website_builders/)).
5. **SEO / AEO theater.** Meta tags exist; semantic HTML, crawlable content (not client-only), schema, CWV, and editable controls do not always. Gap is “looks live” vs “can rank / be cited” ([r/AiBuilders](https://www.reddit.com/r/AiBuilders/comments/1tlac18/the_seo_quality_gap_between_ai_website_builders/)).
6. **Ownership.** Hosted AI = you rent the site. WordPress/Git paths exist but quality or UX is weaker. Agencies fear three-year lock-in cost ([third-party comparisons, 2026](https://champxdigital.ae/blog/ai-website-builders)).
7. **Generic copy and stock-ish AI images.** Fine for a weekend launch; toxic for YMYL and competitive categories.
8. **Distribution.** Domain + hosting incumbents (GoDaddy, Hostinger) win *default*, not *best*.

### 6.3 Willingness-to-pay sketch (qualitative)

- **$0–15/mo:** “I need a URL.” Hostinger / WP.com / free Wix.
- **$15–40/mo:** “This is my business.” Wix Core, Squarespace, Durable, Framer Basic/Pro, 10Web.
- **$25–200+/mo credits:** “I’m building a product.” Lovable / v0 / Bolt.
- **Agency seats / per-site:** Relume, Duda, 10Web Agency — sold on **hours saved**, not AI magic.
- **Enterprise:** Builder, Webflow, Wix Enterprise — sold on **governance**, not generation.

---

## 7. Competitive gaps — ranked opportunity hypotheses

Scoring is **research judgment**, not a forecast. Higher rank = clearer pain × weaker incumbent product × plausible wedge. All assume you do **not** try to out-distribute Wix/Hostinger/GoDaddy on generic “site in 30 seconds.”

### Rank 1 — Post-launch **site operating agent** (SEO + AEO + hygiene)

**Hypothesis:** Generation is a feature; **week-4 to year-3 operation** is an underserved product. Buyers already have a URL (WordPress, Wix, Webflow, custom). They need titles, internal links, schema, CWV, broken links, freshness, and **AI-crawler readability** without a retainer.

**Why now:** Builders advertise SEO; specialists (Surfer, Alli AI) are pivoting to AI-search visibility. Fortune-100-style “AI can’t read 28% of the page” claims ([Alli AI](https://www.alliai.com/)) show the new job. Framer Agents already list “audit broken links / a11y / style inconsistency” — but only **inside Framer**.

**Rationale:** Attach to the installed base instead of winning a greenfield bake-off. Clear ROI story (traffic, citations). Can start as a WordPress plugin + crawler, expand to Webflow/Shopify.

**Risks:** Google/OpenAI ranking opacity; over-automation can tank sites; crowded SEO-tool graveyard; Alli/Surfer/Semrush can bundle you out.

### Rank 2 — **Design-system contract** + visual editor + optional Git export

**Hypothesis:** The product people describe in forums (“persistent tokens, components, and rules the model must obey”) is not fully shipped as a **simple SMB/founder tool**. Webflow/Relume/Builder have pieces; vibe tools do not enforce them.

**Why now:** Harmony, Flowkit, Relume, and Framer tokens all point the same way. Open codegen without a contract is how sites become unmaintainable.

**Rationale:** Differentiates on **quality and editability**, not speed. Export path (Next + design tokens, or WP block theme) attacks lock-in without giving up a hosted upsell.

**Risks:** Hard product; looks like “yet another Framer.” If export is real, hosting LTV drops — need usage or agency pricing.

### Rank 3 — **SEO-preserving redesign / migration** of existing sites

**Hypothesis:** The valuable customer already has traffic. 10Web’s redesign/clone agents and Hostinger “create from URL” prove the *demo*. The gap is **preserving URLs, redirects, content, analytics, and rankings** while restyling — a migration product, not a pretty clone.

**Why now:** Years of AI-generated *and* human-ugly sites. Switcher features (Framer “Switch,” WP.com “existing sites later”) are still shallow.

**Rationale:** High willingness to pay (agencies charge thousands). Measurable success (rankings, CWV). Natural path into Rank 1 (operate after migrate).

**Risks:** Legal/ToS issues on “clone any URL”; content theft optics; one bad migration destroys trust; incumbents can add “import my Wix.”

### Rank 4 — **Agency production OS** (brief → structure → brand → client handoff)

**Hypothesis:** Relume + Webflow + Duda + 10Web cover a lot — but agencies still stitch **Figma + builder + SEO + billing + vibe apps**. A tighter “one brief in, client-ready site + change log out” with **predictable (non-credit-chaotic) economics** still has room, especially outside Webflow-native shops.

**Why now:** Duda Vibe (2026-07) and Relume hosting show agencies want AI **without** losing client permissions and white-label. Wix Partners is a $200M+/qtr reminder the buyer is real.

**Rationale:** Better economics than SMB PLG. Features that matter are boring: roles, staging, components, invoices.

**Risks:** Direct collision with Duda/10Web/Wix Studio. Sales-led. Credit models anger the exact buyer.

### Rank 5 — **AEO / answer-engine layer** sold to *any* CMS

**Hypothesis:** “Show up in ChatGPT / Perplexity / Google AI Overviews” is a 2026 budget line. Builders bolt on checklists; few own **rendering for bots + structured facts + citation hygiene** across a portfolio.

**Why now:** Webflow and Durable already message AEO/GEO. Alli AI is purpose-built. The category is young enough that a focused wedge (e.g. local SMB schema + GBP + `llms.txt`) can beat a generic SEO suite.

**Rationale:** Complements Rank 1; can be a module rather than a full builder.

**Risks:** Platforms change crawler rules; “GEO” is hype-prone; hard to prove causation.

### Rank 6 — **Vertical local OS** (deeper than Durable)

**Hypothesis:** Durable proved “site + CRM + invoice + reviews” for generic services. Vertical packs (HVAC, dental, chambers, vacation rentals — Precedence cites Staycy / Flataway.ai, **$800k pre-seed, October 2025**, via [Short Term Rentalz](https://shorttermrentalz.com); not independently re-verified here) still look under-automated: intake, compliance copy, booking rules, review ask, Google Business.

**Why now:** Horizontal AI sites look like startups. Verticals need **category-specific IA and trust**.

**Rationale:** Defensible data + workflow; not a design contest vs Framer.

**Risks:** Niche TAM; Durable/Wix/Jobber/Housecall Pro adjacency; support-heavy.

### Rank 7 — **Credit-free maintenance** as the wedge (even if generation is credited)

**Hypothesis:** A hosted or export site whose **day-2 editor is visual and unmetered**, with AI as an optional boost, wins retention. This is Wix/Squarespace’s silent advantage over Horizons/Lovable-for-sites.

**Why now:** Forum anger at credit drain is a gift. Framer’s external-agent escape hatch admits the problem.

**Rationale:** Simple message: “Generate once. Edit forever.”

**Risks:** Not a standalone company if that’s the only idea — it’s a **pricing/UX requirement** for Ranks 2–4.

### Rank 8 — Enterprise “AI on *our* design system” ( crowded )

Builder.io, Webflow Enterprise, Adobe, Contentful, Sanity, and internal design-system MCP tools already fight here. Only enter with a **distribution or repo-native** unfair advantage.

### Do not fund (unless you *are* a host or domain registrar)

- Another generic consumer prompt-to-site.
- “30-second website” without ops, SEO, or export.
- Pure landing-page AI (Unbounce / Carrd / Framer already own this).
- Competing with Shopify on checkout.

---

## 8. Validation next steps

### 8.1 Customer interviews (n ≈ 15–20, two weeks)

Talk to **five of each**, not a convenience sample of founders:

| Segment | Screen | Ask | Kill criterion |
|---|---|---|---|
| Local SMB who launched on Durable/Hostinger/Wix AI in the last 18 months | Paid custom domain | What broke after launch? Who updates the site? Did they rank? | If they are happy and never think about the site, Rank 1/6 is weak |
| Agency lead (Webflow **or** WP) | ≥8 sites/year | Hours on IA vs polish vs SEO vs revisions; credit pain | If Relume+Duda already “solved it,” Rank 4 dies |
| Founder who used Lovable/v0/Bolt **for a marketing site** | Shipped a public URL | Why not Framer? Did they export? Credit bill? | If they only needed a page once, no retention |
| SEO / content lead | Owns organic + cares about AI answers | Tools today; what they still hire humans for | If Semrush+Surfer is “good enough” |
| Someone who **migrated off** an AI builder | Switched in last year | Trigger, cost, ranking impact | Gold for Rank 3 |

Record the **artifact** they open (Search Console, invoice, Figma, Webflow) — not opinions.

### 8.2 Competitive teardown (one week, same brief)

Use **one** 5-page brief (e.g. local HVAC company with existing Google Business and 20 blog URLs) and run:

1. Wix Harmony / Aria  
2. Squarespace Blueprint AI  
3. Framer Agents  
4. Webflow AI  
5. Hostinger Manual + Agentic  
6. Durable  
7. 10Web (generate + clone of a real URL)  
8. Relume → Figma/Webflow  
9. Lovable or v0 (marketing site only)  
10. WordPress.com AI builder  

Score (0–5) with screenshots: time-to-draft, brand uniqueness, IA completeness, visual-edit without AI, SEO controls, CWV (PageSpeed on a published URL), AEO basics (indexability, schema, not JS-only content), export/lock-in, credit cost for **10 realistic post-launch edits**.

**Do not** trust vendor “90+ PageSpeed” claims without your own published URL.

### 8.3 MVP angles (smallest test that could work)

| If Rank… survives interviews | Smallest MVP | Success metric (4 weeks) |
|---|---|---|
| **1** | WP plugin + crawl: weekly issues, one-click approved fixes, `llms.txt` + schema | 20 sites; ≥5 paying; measurable GSC impression lift **or** qualitative “I stopped paying an SEO” |
| **2** | Constrained kit (20 sections) + token file the model must read + visual editor + zip/Git export | 10 founders finish a site they are willing to put a real domain on **and** edit week 2 without chat |
| **3** | Import sitemap + HTML, propose redirect map, restyle home + 5 templates | One paid migration where 14-day ranking drop < agreed bound |
| **4** | Brief → sitemap → Relume-class wireframe → client comment link; no hosting | 5 agencies pay; cited hours saved vs their last project |
| **5** | AEO scanner + fix PR for Next/WP | 10 audits → 3 retainers |
| **6** | One vertical (e.g. dental): site + booking + review ask + GBP fields | 15 practices; booking events > “site looks nice” |

### 8.4 What to measure that vendors will not tell you

- **Day-30 and day-90 edit rate** (are people operating the site?).
- **Credit $ per published change** after launch.
- **Share of pages that are indexable text** (view-source, not the screenshot).
- **Unique visual distance** from a “default SaaS” embedding (even a crude CLIP/cluster test).
- **Export completeness** (CSS, CMS, forms, 301s).

### 8.5 Decision rule

- If interviews show **operation and uniqueness** pain and teardown shows **credit + lock-in** pain → prioritize Rank 1 + 2.  
- If agencies cannot name a gap vs Duda/Relume → do not build Rank 4.  
- If SMBs only want cheaper Hostinger → **do not enter**; you cannot win distribution.

---

## 9. Implications (if this were a build, not a brief)

These are **not** COSMOS product requirements. They are the research conclusion in one paragraph:

A new “AI website” should not be a generator. It should be a **system that remembers brand and structure**, lets humans edit without a meter, can **leave** (export/Git/WP), and earns keep by **operating findability** after publish. Incumbents will keep winning first-draft and hosting. The open wedge is everything that happens after the screenshot.

---

## Sources

Accessed **2026-09-14** unless the item has its own date.

### Company / official

- Wix, “ADI Sites No Longer Supported,” effective 2024-11-10 — https://support.wix.com/en/article/adi-sites-no-longer-supported  
- Wix, AI website builder / Harmony marketing — https://www.wix.com/ai-website-builder  
- Wix, “Wix Harmony Editor: Creating a Site with AI” — https://support.wix.com/en/article/wix-harmony-editor-creating-a-site-with-ai  
- Wix, “How much is a Wix website?” — https://www.wix.com/blog/how-much-is-a-wix-website  
- Wix Q2 2025 results — https://www.sec.gov/Archives/edgar/data/1576789/000162828025038117/secondquarter2025.htm  
- Wix Q2 2026 results (2026-08-04) — https://www.sec.gov/Archives/edgar/data/1576789/000162828026052108/secondquarter2026results.htm  
- Squarespace, Blueprint AI — https://www.squarespace.com/websites/ai-website-builder  
- Framer pricing — https://www.framer.com/pricing  
- Framer AI — https://www.framer.com/ai/  
- Framer, “AI credits, simpler plans, and lower prices,” 2026-06-16 — https://www.framer.com/blog/ai-credits-simpler-plans-and-lower-prices/  
- Framer, Business Wire AI features, 2025-05-21 — https://www.businesswire.com/news/home/20250521574932/en/Framer-Launches-AI-Features-to-Supercharge-Web-Design-Democratizing-How-Stunning-Websites-are-Built  
- Webflow AI site builder — https://webflow.com/ai-site-builder  
- Webflow, “Introducing the Webflow AI Assistant,” 2024-10-15 — https://webflow.com/updates/webflow-ai-assistant  
- Hostinger AI Website Builder — https://www.hostinger.com/ai-website-builder  
- 10Web pricing — https://10web.io/pricing-platform/  
- 10Web AI Website Builder — https://10web.io/ai-website-builder/  
- Relume pricing — https://www.relume.ai/pricing  
- Durable AI website builder / pricing references — https://durable.com/ai-website-builder ; https://durable.co/pricing  
- Lovable Series B — https://lovable.dev/blog/series-b  
- Lovable subscription plans — https://docs.lovable.dev/introduction/subscription-plans  
- WordPress.com, “Try Our New AI Website Builder for Free,” 2025-04-09 — https://wordpress.com/blog/2025/04/09/ai-website-builder/  
- Duda Vibe, 2026-07-22 — https://www.duda.co/product-updates/meet-duda-vibe-build-anything-with-ai  
- Duda AI expansion, 2026-07-15 — https://blog.duda.co/duda-expands-ai-2026  
- Shopify Sidekick — https://www.shopify.com/sidekick  
- Builder.io — https://www.builder.io/  
- Alli AI — https://www.alliai.com/ ; https://www.alliai.com/seo-ai-agent  
- Surfer — https://surferseo.com/  
- Elementor, “GoDaddy Airo vs Elementor AI,” 2026 — https://elementor.com/blog/godaddy-airo/  

### Press / independent

- TechRadar, Wix AI builder explainer — https://www.techradar.com/pro/what-is-the-wix-ai-website-builder-everything-we-know-about-the-wix-ai-website-builder  
- TechRadar, Wix Harmony, 2026-01-22 — https://www.techradar.com/pro/website-building/wix-launches-harmony-a-hybrid-approach-to-vibe-coding-and-visual-design  
- Search Engine Journal, Wix Harmony, 2026-01-21 — https://www.searchenginejournal.com/wix-introduces-harmony-ai-website-builder/565505/  
- Website Builder Expert, “Wix’s AI Features: A Complete List for 2026” — https://www.websitebuilderexpert.com/website-builders/wix-ai-features/  
- TechCrunch, WordPress.com AI builder, 2025-04-09 — https://techcrunch.com/2025/04/09/wordpress-com-launches-a-free-ai-powered-website-builder/  
- TechCrunch, Lovable $200M ARR, 2025-11-19 — https://techcrunch.com/2025/11/19/as-lovable-hits-200m-arr-its-ceo-credits-staying-in-europe-for-its-success/  
- TechCrunch, Lovable $400M ARR, 2026-03-11 — https://techcrunch.com/2026/03/11/lovable-says-it-added-100m-in-revenue-last-month-alone-with-just-146-employees/  
- TechCrunch, Lovable $500M run rate, 2026-06-09 — https://techcrunch.com/2026/06/09/lovable-says-it-has-hit-500m-in-annualized-revenue-with-1-million-new-projects-a-week/  
- Bloomberg, Lovable $200M ARR, 2025-11-18 — https://www.bloomberg.com/news/articles/2025-11-18/lovable-hits-200-million-arr-and-raising-funds-above-6-billion-valuation  
- Motley Fool, Wix Q2 2025 transcript, 2025-12-23 — https://www.fool.com/earnings/call-transcripts/2025/12/23/wix-wix-q2-2025-earnings-call-transcript/  
- Motley Fool, Wix Q2 2026 transcript, 2026-08-11 — https://www.fool.com/earnings/call-transcripts/2026/08/11/wix-wix-q2-2026-earnings-call-transcript/  

### Market reports (**soft TAM**)

- Precedence Research, AI Powered Website Builder, updated 2026-02-25 — https://www.precedenceresearch.com/ai-powered-website-builder-market  
- Custom Market Insights, AI-Powered Website Builder, 2026-08-14 — https://www.custommarketinsights.com/report/ai-powered-website-builder-market/  
- Research and Markets / TBRC, AI-Powered Website Builder Global Market Report 2026, May 2026 — https://www.researchandmarkets.com/reports/6241469/ai-powered-website-builder-global-market-report  
- Market.us, AI-Powered Website Builder — https://market.us/report/ai-powered-website-builder-market/  
- WiseGuyReports, AI Website Builder — https://www.wiseguyreports.com/reports/ai-website-builder-market  
- Technavio via GII, 2026-01-19 — https://www.giiresearch.com/report/infi1915631-global-ai-powered-website-builder-market.html  
- Statista, website builders market share 2024 (published 2025-11-28) — https://www.statista.com/statistics/818598/worldwide-website-builders-market-share/  

### Practitioner / teardown (anecdotal)

- Reddit r/SaaS, “Gaps in AI website builders?” — https://www.reddit.com/r/SaaS/comments/1ue570z/gaps_in_ai_website_builders/  
- Reddit r/ai_website_builder, generic design — https://www.reddit.com/r/ai_website_builder/comments/1tgjevo/are_websites_made_from_ai_website_builders/  
- Reddit r/nextjs, formulaic AI UI — https://www.reddit.com/r/nextjs/comments/1nnnolv/ai_web_builders_are_ruining_the_status_of_design/  
- Reddit r/AiBuilders, SEO quality gap, 2026-05-23 — https://www.reddit.com/r/AiBuilders/comments/1tlac18/the_seo_quality_gap_between_ai_website_builders/  
- Reddit r/webdesign, credit drain on updates — https://www.reddit.com/r/webdesign/comments/1tjar1p/ai_website_builders_are_great_until_you_need_to/  

---

## Changelog

| Date | Change |
|---|---|
| 2026-09-14 | Initial brief from public web sources. No primary interviews or paid report purchases. |
