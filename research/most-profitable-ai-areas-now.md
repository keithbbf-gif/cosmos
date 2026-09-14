# Most profitable areas in AI now

**As-of date:** 14 September 2026 (latest public filings and press through early September 2026).  
**Scope:** Evidence-backed ranking of where AI is making money *today*, versus where revenue is growing without disclosed profit. Isolated research note; not COSMOS product documentation.

**Not investment, legal, or financial advice.** Figures below are citations of public company filings, management metrics, journalist-reviewed documents, and surveys. Private-company ARR and “run rate” numbers are especially noisy. Do not treat this as a recommendation to buy, sell, or build any security or company.

---

## How to read this report

Three different questions get collapsed into “AI is profitable”:

1. **Who is printing cash now?** Public semiconductor, cloud, and some enterprise-software franchises with GAAP or free-cash-flow profit.
2. **Where is willingness-to-pay exploding?** Coding agents, model APIs, vertical workflow software — often **run-rate revenue**, not profit.
3. **Where can a small operator take cash in months?** Implementation, narrow vertical agents, and productized services — smaller dollars, faster time-to-cash.

Those three maps are **not the same**. The largest *profits* sit in chips, memory, custom ASICs, and hyperscaler clouds. The fastest *application* traction sits in coding tools and workflow software. The best *small-team* fit is usually a narrow paid workflow, not a foundation model.

**Metric hygiene (do not mix these):**

| Label | What it actually is | Risk |
| --- | --- | --- |
| GAAP revenue / net income | Audited or reviewed, period-recognized | Best evidence |
| ARR / ACV | Annualized *contracted* recurring value | Scope changes (Salesforce “Agentforce ARR” now includes Slackbot) |
| Annualized run rate | Extrapolated recent sales × 12 | Can jump or stall in a month; not booked FY revenue |
| Survey spend | Buyer-reported or bottoms-up models | Method-dependent; Menlo excludes chips and hyperscaler inference |

---

## 1. What “profitable” means here

For this note, a segment ranks higher when **more of these are true at once**. No single metric is enough.

| Dimension | Why it matters | Small operator vs big tech |
| --- | --- | --- |
| **Cash / GAAP profit** | Revenue without margin is a transfer to GPUs and talent | Big tech can lose money for years; a small team cannot |
| **Revenue growth with conversion** | Growth plus production use, not pilots | Small teams need paid pilots that convert in weeks |
| **Willingness-to-pay** | Seats, usage, or outcome fees that survive CFO review | SMBs pay for a saved FTE or recovered cash; enterprises pay for risk reduction and velocity |
| **Gross-margin shape** | Software-like vs token-pass-through vs hardware | Token-heavy products can look like SaaS and behave like a reseller |
| **Capital intensity** | Fabs, data centers, robot factories vs laptop + APIs | Chips/cloud/robotics are closed to small operators |
| **Competitive intensity** | Labs, hyperscalers, and incumbents entering the same UI | Horizontal chat is already lost; workflow + distribution still open |
| **Time-to-cash** | Invoice this quarter vs multi-year infra build | Services and PLG tools win on speed; platforms win on scale |
| **Buyer concentration** | One hyperscaler vs many SMBs | Concentration is a scale privilege and a risk |

**Working definition used for ranking**

- **Profit-now (scale):** disclosed operating income, net income, or free cash flow, plus durable demand.  
- **Traction-now:** large, growing paid usage even if the vendor is loss-making.  
- **Operator-now:** a small software/agent team can reach paid customers without a fab, a $1B training run, or a 200-person enterprise sales army.

Gartner’s May 2026 forecast is the cleanest *spend* map (not profit): worldwide AI spending **$2.596 trillion in 2026** (+47% YoY), of which **AI infrastructure $1.432T**, **AI services $586B**, **AI software $453B**, **AI models only $33B**, **AI cybersecurity $51B**. Gartner’s own comment: spending is still driven by vendors and hyperscalers; enterprises “have yet to really flex their spending potential.” ([Gartner, 19 May 2026](https://www.gartner.com/en/newsroom/press-releases/2026-05-19-gartner-forecasts-worldwide-ai-spending-to-grow-47-percent-in-2026))

Menlo Ventures’ enterprise survey (narrower: genAI apps + model APIs + some infra, **excluding chips and hyperscaler inference**) put 2025 enterprise genAI spend at **$37B**, of which **$19B applications** and **$18B infrastructure/APIs**. ([Menlo Ventures, 9 Dec 2025](https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/))

McKinsey’s 2026 State of AI survey: adoption and scaling are up, but **only ~37% of respondents attribute any EBIT impact to AI** (flat vs 2025), and **~6%** are “high performers” with ≥5% of EBIT tied to AI. That gap is the live market: **buyers will pay for measured workflow results; they will not indefinitely fund unmeasured copilots.** ([McKinsey via FM Magazine, Sep 2026](https://www.fm-magazine.com/news/2026/sep/companies-financial-value-from-ai-holds-firm-in-2026/); [The Register, 25 Aug 2026](https://www.theregister.com/ai-and-ml/2026/08/25/mckinsey-says-enterprise-ai-is-finally-on-the-road-to-roi/5292388))

---

## 2. Ranked landscape (what actually holds up)

Two rankings. The first is **where profit is realized today**. The second is **where paid traction is hottest**. A later section ranks **small-operator fit**.

### 2.1 Profit-now ranking (cash / GAAP at scale)

| Rank | Segment | Evidence of profit (not just revenue) | Capital intensity | Small-team fit |
| --- | --- | --- | --- | --- |
| 1 | Accelerators, HBM, custom ASICs | NVIDIA FY26 GAAP net income **$120.1B** on **$215.9B** revenue, **71.1%** GAAP GM; SK hynix 1Q26 **72%** operating margin; Broadcom Q3 FY26 **$13.7B** FCF and **$16.7B** AI semiconductor revenue | Extreme | None |
| 2 | Hyperscaler cloud + inference capacity | Google Cloud Q2’26 operating income **$8.8B** (35.6% OM) on **$24.8B**; AWS Q2’26 **$42.2B** sales, **39.4%** OM; Microsoft FY26 operating income **>$155B**, Azure **>$100B** for the year | Extreme (capex) | None as a cloud; yes as a *customer* of APIs |
| 3 | Incumbent software with AI attach | Adobe Q3 FY26 record **$6.76B** revenue, non-GAAP OM guided ~**45%**; Microsoft 365 Copilot **>30M** paid seats; CrowdStrike FCF **$377M** in one quarter | Medium (R&D + sales) | Weak vs incumbents; possible in a niche they ignore |
| 4 | Enterprise AI platforms that operationalize models | Palantir Q2’26 **$1.935B** revenue, **62%** adjusted operating margin, GAAP EPS **$0.41** | High (forward-deployed + ontology) | Weak; this *is* the expensive integration layer |
| 5 | Cybersecurity platforms (AI as tailwind) | CrowdStrike Q2 FY27 revenue **$1.47B** (+26%), ARR **$5.84B**, raising FY27 revenue guide to ~**$6.0B**; Gartner AI-cyber spend **$51B** in 2026 | High (telemetry, brand, SOC) | Weak at platform layer; possible in a control niche |
| 6 | Creative / marketing tools with product-market fit | Adobe AI-first ARR **+150% YoY** (company); Midjourney repeatedly described as **self-funded and profitable** (secondary; not audited) | Low–medium | Possible at a niche; generic image gen is crowded |
| 7 | Voice / CX agents (revenue real; profit mixed) | Sierra company-stated **$100M ARR** (Nov 2025); later press **~$200M** (May 2026, secondary). ElevenLabs Sacra estimate **~$600M ARR** (Jun 2026). Profit disclosed only in secondary profiles | Medium (voice stack + enterprise sales) | Mid-market verticals yes; Fortune 50 no |
| 8 | Vertical workflow SaaS | Harvey press **>$400M ARR** (Sep 2026, TNW); Abridge **$100M+ ARR** by May 2025. **Profit generally not disclosed**; one industry compilation says Harvey’s cofounder confirmed it is **unprofitable** | Medium (sales + compliance) | Yes **below** BigLaw / epic-health-system layer |
| 9 | Coding agents / IDEs | Anthropic said Claude Code run rate **>$2.5B** (Feb 2026, company via Reuters). Cursor **$2B–$4B** run-rate reports conflict. **Profit not disclosed**; inference COGS is the open question | Medium (GPU + talent) | Competing with labs is poor; **niche SDLC tools** remain open |
| 10 | Foundation model APIs | OpenAI booked **$13.07B** revenue and **$20.92B** operating loss in 2025 (audited docs via Ars/FT). Anthropic run rate **$65B** (Jul 2026, sources) with **preliminary** Q2 profit claims — unverified | Extreme | No |
| 11 | AI implementation / services | Accenture FY25 advanced-AI revenue **$2.7B**, bookings **$5.9B**, on a ~**16%** company operating-margin franchise. Gartner 2026 AI *services* **$586B** (broad definition) | Low–medium (people) | **Best time-to-cash** if productized |
| 12 | Labeling / evals / observability | Scale: Sacra **~$2B** 2025 revenue estimate (private). Observability is a real budget line but **no reliable category P&L** | Medium (labor) / low (software evals) | Evals/obs software yes; labeling at Scale’s scale no |
| 13 | Robotics / physical AI | Figure **$3.5B** GPU commit vs **~$1.9B** lifetime raise (Forbes, Sep 2026). Unitree is the rare **disclosed profit** case (China filings / press). Western humanoids are capex stories | Extreme | No (except software/data around robots) |
| 14 | GPU neoclouds | CoreWeave Q2’26 revenue **$2.575B**, GAAP net loss **$626M**, interest **$640M**; FY26 capex guide **$35–39B** | Extreme | No |

**Bottom line:** the only AI layer with *unambiguous, enormous, current* profit is **picks-and-shovels silicon and the clouds that rent it**. Application profit exists, but it is either (a) an attach on an already-profitable franchise (Adobe, Microsoft, CrowdStrike, Palantir) or (b) a small, often private company whose profitability is reported, not filed.

### 2.2 Traction-now ranking (paid demand, 2025–2026)

Menlo’s 2025 application split remains the best **buyer-dollar** map for software (not chips):

| Application bucket (Menlo, CY2025) | Spend | Notes |
| --- | --- | --- |
| Horizontal copilots | **$8.4B** | ChatGPT / Gemini / M365-class; huge, contested |
| Departmental AI, of which **coding $4.0B** | **$7.3B** | Coding is the killer use case; 50% of developers daily |
| Vertical AI, of which **healthcare ~$1.5B**, legal **$650M**, scribes **$600M** | **$3.5B** | Healthcare admin leads; legal second |

([Menlo Ventures, 9 Dec 2025](https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/))

**2026 updates that still hold after source-checking:**

- **Coding agents are the strongest application WTP signal in 2026**, with company-stated Claude Code run rate and multiple Cursor run-rate prints (conflict flagged below).
- **Cloud AI consumption is the strongest *recognized* revenue signal** (Azure, GCP, AWS disclosures).
- **Outcome-priced CX agents and ambient clinical documentation** show real enterprise conversion, not just pilots.
- **Generic “AI wrapper” marketing tools** did not hold up as a standalone profit pool; value accrued to Adobe, Canva-class suites, and a few self-serve hits (Gamma, Midjourney — see §3.6).

---

## 3. Segment dossiers

Each dossier: who pays, unit-economics *signals* (not invented margins), competition, moats, small-team vs scale.

### 3.1 Infra / chips / cloud inference — **profit champion, closed to small operators**

**Who pays:** hyperscalers, frontier labs, sovereign AI programs, and (increasingly) enterprises buying GPU-hours or tokens. NVIDIA said FY26 Data Center revenue was **$193.7B** (+68% YoY); Q4 Data Center **$62.3B**. Hyperscalers were “just above 50%” of the mix; sovereign AI “exceeding $30B” in FY26 (company commentary). ([NVIDIA FY26 Q4 release, 25 Feb 2026](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2026/default.aspx); [NVIDIA Newsroom](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-fourth-quarter-and-fiscal-2026))

Q1 FY27 (calendar spring 2026): NVIDIA revenue **$81.6B**, Data Center **$75.2B**, GAAP GM **74.9%**. ([NVIDIA Q1 FY27](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-First-Quarter-Fiscal-2027/))

**HBM / memory:** SK hynix 1Q26 revenue **KRW 52.5763T**, operating profit **KRW 37.6103T**, **72%** operating margin — company attributes this to AI demand (HBM, server DRAM, eSSD). ([SK hynix, 22–23 Apr 2026](https://news.skhynix.com/en/q1-2026-business-results/))

**Custom ASICs:** Broadcom Q3 FY26 AI semiconductor revenue **$16.7B** (+221% YoY, +54% QoQ); Q4 AI semiconductor guide **$21.7B**. Consolidated Q3 revenue **$29.6B**, FCF **$13.7B**. ([Broadcom, 2 Sep 2026](https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial))

**Cloud / inference (recognized, profitable at the *segment* level):**

| Vendor | Latest cited print | Profit signal | Caveat |
| --- | --- | --- | --- |
| Microsoft | Azure **>$100B** FY26, +41%; Microsoft Cloud Q4 **$59.3B**, +27%; FY26 operating income **>$155B**. AI business **>$37B annual run rate**, +123% (Q3 FY26, *management metric*) | Entire company is highly profitable; AI is a growth vector *and* a capex sink | $37B is **not** an audited segment. Q4 FY26: M365 Copilot **>30M** paid seats ([Microsoft FY26 Q4](https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast); [FY26 Q3](https://www.microsoft.com/en-us/investor/earnings/fy-2026-q3/press-release-webcast)) |
| Alphabet | Google Cloud Q2’26 **$24.8B**, +82%; Cloud OI **$8.814B**. Cloud backlog **$514B**. Gemini App **950M MAU** (CEO remarks) | Cloud is now a large, profitable AI vehicle | Gemini *standalone* revenue is **not** disclosed ([Alphabet Q2’26 8-K](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm); [Pichai remarks, 22 Jul 2026](https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q2-2026/)) |
| Amazon | AWS Q2’26 **$42.2B**, +37% (fastest in 18 quarters). Jassy: AWS **AI** and **chips** businesses each **>$25B annual run rate** | AWS OM **39.4%** in the quarter | “AI business” is a management cut ([Amazon Q2’26](https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Second-Quarter-Results/)) |
| CoreWeave | Q2’26 revenue **$2.575B**; backlog **~$104B**; FY26 revenue guide **$12.4–13.2B** | Adjusted OI **$128M**; GAAP net loss **$626M**; interest **$640M** | Demand is real; **GAAP profit is not** ([CoreWeave, 11 Aug 2026](https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-Second-Quarter-2026-Results/default.aspx)) |
| Fireworks | CNBC: **>$1B** annualized revenue, **$17.5B** valuation (Jul 2026) | Not disclosed | Cursor was once “over half” of revenue — concentration risk ([CNBC, 16 Jul 2026](https://www.cnbc.com/2026/07/16/fireworks-nvidia-cloud-ai-startup-value.html)) |

**Unit-economics signals:** 70%+ semiconductor gross margins (NVIDIA recovered to ~75% by Q4 FY26 after a China/H20 charge dragged FY26 GM to 71.1%). Cloud AI is profitable *as part of* Azure/GCP/AWS, but incremental GPU depreciation, power, and networking can compress *incremental* AI margins — Microsoft and peers are spending **hundreds of billions** of capex (Microsoft calendar-2026 capex plan widely reported near **$190B**; treat as management outlook, not a profit figure).

**Competition:** NVIDIA vs custom silicon (Google TPU, Amazon Trainium, Broadcom XPUs). Capacity, not demand, is the bottleneck (TSMC CoWoS / HBM — widely reported as sold through).

**Moats:** process + packaging + CUDA/software + allocation of scarce HBM/CoWoS. These are **physical and contractual** moats.

**Small team:** **do not build here.** Use it. The operator move is *arbitrage of inference price* (OpenRouter, open weights, reserved capacity), not owning GPUs.

### 3.2 Foundation model APIs — **huge revenue, profit unproven or negative**

**Who pays:** enterprises (API + seats), developers, consumers. OpenAI CFO Sarah Friar (Aug 2026): enterprise is now **majority of revenue**, having crossed a prior 60/40 consumer tilt. ([CNBC, 14 Aug 2026](https://www.cnbc.com/2026/08/14/openai-cfo-friar-tells-investors-that-enterprise-bigger-than-consumer.html))

**Revenue vs profit (do not confuse):**

| Company | Booked / run-rate | Profit evidence | Uncertainty |
| --- | --- | --- | --- |
| OpenAI | Audited **$13.07B** revenue in **2025**; operating loss **$20.92B**; R&D **$19.18B** (incl. **$10.59B** to Microsoft); COGS **$7.5B**. Net loss headline ~**$39B** includes ~**$30B** one-time accounting charge (FT). Run rate **>$40B** by mid-Aug 2026 (sources) | **Not profitable.** Company has talked 2029–30. 900M WAU / ~50M paid (Ars) | Run rate ≠ FY revenue. 2026 loss forecasts in blogs are **not** audited ([Ars Technica, 16 Jun 2026](https://arstechnica.com/ai/2026/06/leaked-financial-docs-show-openai-is-losing-billions-of-dollars-a-year/); [Bloomberg, 13 Aug 2026](https://www.bloomberg.com/news/articles/2026-08-13/openai-s-revenue-run-rate-tops-40-billion-ahead-of-ipo)) |
| Anthropic | YE2025 run rate ~**$9B**; Feb 2026 company **$14B** run rate; Jul 2026 sources **$65B** run rate. Claude Code **>$2.5B** run rate (Feb 2026, **company said**) | Secondary reports of **preliminary Q2’26 adjusted operating profit** — **not confirmed in an S-1**. Treat as **unverified** | Run-rate explosion in 2026 is extraordinary; methodology (month × 12 vs ARR) is not public ([Reuters, 12 Feb 2026](https://www.reuters.com/technology/anthropic-valued-380-billion-latest-funding-round-2026-02-12/); [Reuters, 17 Aug 2026](https://www.reuters.com/technology/anthropic-revenue-run-rate-tops-65-billion-source-says-2026-08-17/)) |
| Google / xAI / others | Gemini not broken out. xAI figures in blogs are **not used here** | Alphabet is profitable; Gemini P&L is opaque | Do not invent a Gemini revenue line |

**Unit-economics signals:** OpenAI 2025 COGS was **57% of revenue** ($7.5B / $13.07B) *before* R&D — that is **not** a SaaS gross-margin story. Token price wars and “enterprise balking at token billing” are already in the Ars/FT writeup. Ramp’s Aug 2026 index: share of businesses on **model-serving / open-weight** platforms is rising; Anthropic vs OpenAI share **flips** as models ship — **switching costs are lower than the valuations imply**. ([Ramp AI Index, Aug 2026](https://ramp.com/data/ai-index-august-2026); [TechCrunch, 20 Aug 2026](https://techcrunch.com/2026/08/20/openai-is-gaining-on-anthropic-with-business-users-new-data-indicates/))

**Competition:** brutal, few-player, capital-unlimited. Chinese open weights compress price.

**Moats:** model quality (months, not years), distribution (ChatGPT, Claude, Gemini), enterprise trust, data flywheels. Weak vs a new frontier model.

**Small team:** **do not train a frontier model.** Build *on* APIs. If you sell “a wrapper on GPT/Claude,” you are the labs’ future feature.

### 3.3 Vertical SaaS + AI (legal, health admin, accounting, sales, support)

**Who pays:** law firms and GC (Harvey, Legora, Clio, Spellbook); health systems / Epic-attached clinicians (Abridge, Ambience, Nuance DAX); finance teams (Ramp is mostly **card interchange**, not AI SaaS — do not mis-label); sales teams (Clay et al.); CX orgs (Sierra, Fin, Salesforce, ServiceNow).

**Evidence that holds up:**

- Menlo 2025: vertical AI **$3.5B**; healthcare **~$1.5B** (43%); ambient scribes **$600M** (+2.4×); legal **$650M**. Enterprises now **buy 76%** of AI use cases (vs 53% in 2024). AI deal conversion to production **47%** vs **25%** for traditional SaaS. ([Menlo, 9 Dec 2025](https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/))
- **Harvey:** Sacra **$195M ARR** YE2025; TNW (Sep 2026) **ARR past $400M**, **>3,000** organizations, **$550M** round at **$15.6B**. Seat-price chatter of $100–$2,000/attorney/month is **secondary** — treat as rumor. ([Sacra](https://sacra.com/research/harvey-at-195m-arr/); [TNW](https://thenextweb.com/news/harvey-550m-round-15-6bn-guardrails-acquisition))
- **Abridge:** multiple research notes put **$100M+ ARR by May 2025**, Epic-attached, 250+ health systems. **2026 booked ARR is not in a company 10-K.** ([Benchmark-style writeup](https://sevaustinov.me/hypergrowth-research/companies/abridge.html))
- **Sales / support incumbents (recognized):** Salesforce Q2 FY27 **Agentforce ARR >$1.5B** (+240% YoY) — **definition now includes Slackbot and Headless 360**, so YoY is not clean. Combined Agentforce + Data 360 ARR **~$3.9B**. Salesforce also agreed to buy **Fin** (Intercom) for **~$3.6B** (Jun 2026). ([Salesforce, 26 Aug 2026](https://investor.salesforce.com/news/news-details/2026/Salesforce-Delivers-Record-Second-Quarter-Fiscal-2027-Results/default.aspx)) ServiceNow AI portfolio **>$1B ACV** in 2026 is widely reported; use company filings if you underwrite it.

**Unit-economics signals:** high ACV, multi-year seats, workflow lock-in (Epic, DMS, CRM). **Valuation multiples of 30–80× ARR are not profits.** New Market Pitch’s compilation states Harvey’s cofounder recently confirmed the company is **unprofitable** — that is a **secondary** source; flag it. ([New Market Pitch](https://newmarketpitch.com/blogs/news/ai-infrastructure-profitable-startups))

**Competition:** every vertical now has 5–15 funded AI natives **plus** the system of record (Clio, Epic, Intuit, Salesforce).

**Moats that survive a better base model:** system-of-record integration, liability/insurance, evaluation on *that* firm’s documents, switching cost of workflow, regulatory clearance.

**Small team:** **do not attack Harvey’s AmLaw list or Abridge’s Epic install base.** Do attack **one painful workflow** in a profession with budget and a measurable hour-saving (medical billing denial appeals, construction bid takeoff, insurance FNOL, mid-market bookkeeping close, immigration packet assembly). Menlo’s “industries underserved by software” point still stands.

### 3.4 Coding agents / developer tools — **strongest application WTP; profit opaque**

**Who pays:** individual developers (PLG), then engineering orgs (enterprise). Menlo: coding **$4.0B** in 2025 departmental spend; Cursor reached **$200M** before a single enterprise AE. 27% of AI app spend is PLG (4× traditional SaaS). ([Menlo, 9 Dec 2025](https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/))

**2026 evidence (conflict flagged):**

| Product | What was *actually* disclosed | Conflict |
| --- | --- | --- |
| Claude Code | Anthropic **said** run-rate **>$2.5B** in Feb 2026; business subs **4×** since Jan; enterprise **>50%** of Claude Code revenue | Later company-wide run rate jumped to **$65B**; Claude Code’s 2026 share is **not** updated ([Reuters, 12 Feb 2026](https://www.reuters.com/technology/anthropic-valued-380-billion-latest-funding-round-2026-02-12/)) |
| Cursor (Anysphere) | Bloomberg (21 May 2026): annualized revenue **$3B** in late April; **>3,000** customers at **≥$100k**. Dealroom (9 Jun 2026): **$4B**, ~**75%** enterprise — both “person familiar” | Mid-2025 figures in blogs still say **$500M**. **Do not pick one number.** Range: **high hundreds of millions to low single-digit billions**, growing fast ([Bloomberg](https://www.bloomberg.com/news/articles/2026-05-21/cursor-hits-3-billion-annual-sales-rate-ahead-of-spacex-deal); [Dealroom](https://dealroom.co/news/134107-cursor-tops-4b-annualized-revenue/)) |
| GitHub Copilot | Microsoft: **4.7M paid subscribers** (FY26 Q2, 28 Jan 2026), +75% YoY. **No official Copilot revenue.** Analyst reconstructions **~$0.45–1.1B** | Wide range; treat as **seat-count fact + revenue estimate** |

**Unit-economics signals:** developers pay monthly *and* burn tokens. Usage-based billing (GitHub’s 2026 AI Credits shift) is the honest model. **Gross margin is the unknown** — Fireworks’ Cursor concentration shows how much of “IDE ARR” can be inference pass-through.

**Competition:** Anthropic, OpenAI Codex, Google, Microsoft, Cursor, JetBrains, Amazon Q — **highest competitive intensity of any application category.**

**Moats:** repo context, team defaults, evals on *their* codebase, enterprise admin, habit. Fragile if a lab ships a better agent into the terminal.

**Small team:** **do not build “another Cursor.”** Build **narrow SDLC products** with a measurable KPI (flaky-test quarantine, SOC2-aware codegen, mainframe/COBOL, game-engine shaders, FHIR mapping, hardware verification). The category validates WTP; the *horizontal IDE* is taken.

### 3.5 Marketing content / creative tools — **incumbent attach wins; a few profitable niches**

**Who pays:** creative pros (Adobe), mid-market marketing teams, prosumers (Midjourney, Canva), sales-enablement (Gamma).

**Evidence:**

- Adobe Q3 FY26 (ended 28 Aug 2026): revenue **$6.76B** (+13%), total ARR **$27.50B**, **AI-first ARR +150% YoY**. FY26 revenue target **~$26.6B**. This is a **profitable** company adding AI as attach, not a science project. ([Adobe / Business Wire, Sep 2026](https://www.businesswire.com/news/home/20260910832552/en/Adobe-Reports-Record-Q3-Results))
- Firefly “approaching **$300M** ARR” was **management commentary around the Jun 2026 call**, relayed by trade press — **not** repeated as a line item in the Q3 release. Flag as **Q2 commentary**. ([Digital Applied summary](https://www.digitalapplied.com/blog/ai-image-generation-statistics-2026-data-points))
- Midjourney: Forbes/PitchBook-based profiles describe **~$300M FY2024** revenue, **self-funded, profitable**. 2025 “$500M” figures on stat sites are **unsourced**. Use: **likely profitable, sub-scale vs Adobe, numbers unverified**. ([New Market Pitch compilation](https://newmarketpitch.com/blogs/news/ai-infrastructure-profitable-startups))
- Menlo 2025: marketing departmental AI **$660M**; creator vertical **$360M** — real, not the whole software market.
- Generic copy tools (the 2023 Jasper-class) **did not become the profit pool**. Value moved into **suites + workflow** (campaign, brand kit, rights, CMS).

**Unit-economics signals:** credit packs and seats; Adobe-class **~45%** non-GAAP operating margin is the *incumbent* benchmark, not a startup’s.

**Competition:** Adobe, Canva, Google, Meta, Apple, Midjourney, open models.

**Small team:** brand-specific generation, rights-cleared enterprise, or **ops** (brief → asset → approval → CMS) beats another text-to-image demo.

### 3.6 Voice / contact center — **real enterprise budgets; sales-heavy**

**Who pays:** Fortune 1000 CX (Sierra), banks and fintechs (ElevenLabs agents at Revolut/Klarna — Sacra), mid-market outbound (Bland and peers).

**Evidence:**

- Sierra (company blog, **21 Nov 2025**): **$100M ARR**, seven quarters after Feb 2024 launch; 50% of customers **>$1B** revenue; outcome-based pricing; multi-channel including phone. ([Sierra](https://sierra.ai/blog/100m-arr))
- Later **$200M / $15.8B valuation** figures are **press citing sources** (May–Aug 2026). Use as **directional**, not audited.
- ElevenLabs: Sacra estimate **$600M ARR (Jun 2026)** from **$330M** YE2025 — **estimate**. Forbes **$116M profit in 2025** appears only in secondary compilations. ([Sacra](https://sacra.com/c/elevenlabs/))
- Salesforce–Fin (**~$3.6B**, Jun 2026) is a **price signal** that agentic CX is strategic to the CRM incumbents.

**Unit-economics signals:** outcome / per-resolution pricing aligns vendor and buyer **if** containment is real. Voice COGS (telephony + STT + LLM + TTS) can destroy margin on long calls.

**Competition:** Sierra, Decagon, Cresta, Bland, Five9/NICE, Genesys, Amazon Connect, Google CCAI, Salesforce, ServiceNow.

**Moats:** telephony reliability, compliance (HIPAA/PCI), eval harnesses, brand voice, CRM write-back.

**Small team:** **yes for one vertical’s phone workflow** (clinics, property management, auto dealers, collections with legal constraints). **No for “we’ll replace the Fortune 50 contact center.”**

### 3.7 Cybersecurity AI — **profitable incumbents; hard new-logo category**

**Who pays:** CISOs, with budget that **expands** as agents multiply (more identity, more endpoints, more untrusted code).

**Evidence:**

- CrowdStrike Q2 FY27 (ended 31 Jul 2026): revenue **$1.47B** (+26%), subscription **$1.40B**, ARR **$5.84B** (+25%), net-new ARR **$333M**, FCF **$377M**. FY27 revenue guide **~$5.99–6.01B**. CEO: “AI adoption needs security.” ([CrowdStrike 8-K exhibit](https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm))
- Gartner: AI cybersecurity spend **$25.9B (2025) → $51.3B (2026) → $86.0B (2027)**. ([Gartner, 19 May 2026](https://www.gartner.com/en/newsroom/press-releases/2026-05-19-gartner-forecasts-worldwide-ai-spending-to-grow-47-percent-in-2026))
- Palantir is adjacent (see §3.8): commercial AI *operations*, not Falcon-class EDR.

**Unit-economics signals:** subscription + module attach; CrowdStrike is **FCF-positive**. New AI-security startups are usually **pre-profit**.

**Competition:** CrowdStrike, Palo Alto, Microsoft, Wiz-class CNAPP, incumbents adding “AI SOC.”

**Moats:** telemetry graph, detections that are wrong-rarely, installed base, MSSP channel.

**Small team:** **poor** as a platform. **Possible** as a specific control (prompt-injection testing, agent-permission graph, MCP allowlists, AI-BOM). Buyers will still ask “why not the vendor I already pay?”

### 3.8 Enterprise AI operations (Palantir-class) — **profit + growth; not a startup pattern**

Palantir Q2 2026: revenue **$1.935B** (+93% YoY), U.S. commercial **$764M** (+149%), adjusted operating income **$1.19B** (**62%** margin), FY26 revenue guide **$8.150–8.158B** (~82% growth). Management attributes commercial acceleration to AIP. ([Palantir Q2’26 exhibit 99.1](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000039/a2026q2ex991pressrelease.htm); [shareholder letter](https://www.palantir.com/q2-2026-letter/en/))

**Who pays:** U.S. commercial enterprises and government that want **ontology + governance + agents on their data**, not a chatbot.

**Small team:** this is the opposite of PLG. The *lesson* for a small team is the **product shape** (governed actions on private data), not the go-to-market.

### 3.9 Robotics / physical AI — **capital sink with a few hardware exceptions**

**Who pays today:** auto OEMs (BMW–Figure pilots), warehouses (Agility Digit / Amazon), Hyundai (Boston Dynamics Atlas committed 2026 production), China/export humanoid buyers (Unitree).

**Evidence of capital intensity, not profit:**

- Figure: lifetime raise ~**$1.9B**; **$3.5B** compute commitment to Nscale for up to **100k** GPUs (Forbes, **9 Sep 2026**). That single commit can exceed equity raised. ([Forbes](https://www.forbes.com/sites/jonmarkman/2026/09/09/figure-ai-commits-35-billion-to-nscale-for-up-to-100000-nvidia-gpus/))
- Tesla Optimus production targets are **guidance**, not external revenue.
- Unitree 2025 figures circulating in trade press (~**¥1.7B** revenue, profitable) are the **exception that proves the rule**: lower-cost hardware in China can make money **before** Western “general humanoid labor” stories do. Treat CNY figures as **press**, confirm against filings before underwriting.

**Small team:** **no** on robots. **Maybe** on data, teleop software, or a single industrial cell.

### 3.10 AI services / implementation agencies — **where small operators actually invoice**

**Who pays:** enterprises (Accenture/Deloitte/PwC) and SMBs (boutiques).

**Evidence:**

- Accenture FY25 (ended 31 Aug 2025): generative/agentic AI revenue **$2.7B** (3× YoY), bookings **$5.9B**. **Explicitly excludes** data, classical AI, and AI used in delivery. Company adjusted OM stays mid-teens. ([Accenture FY25 shareholder letter](https://www.accenture.com/content/dam/accenture/final/accenture-com/document-4/Accenture-2025-Letter-To-Shareholders.pdf))
- Accenture later **stopped breaking out** advanced-AI revenue as it “embedded” — a tell that AI is becoming **the delivery motion**, not a side bet.
- Gartner 2026 **AI services $586B** is a **wide** bucket (includes hyperscaler professional services, SI, support). Do not read it as “agency TAM.”
- Promethean Research: digital agencies **~13%** after-tax net margin (2025). Specialist AI-automation shops *claim* **50–70% gross / 20–35% net**; those are **operator blogs**, not audited panels. Use as a **hypothesis to test**, not a fact. ([Promethean](https://prometheanresearch.com/2026-state-of-digital-services-digital-agency-industry-research/); [Automaton](https://automatonagency.com/insights/ai-automation-agency-economics))

**Unit-economics signals:** time-to-cash in **weeks** if the offer is a fixed-scope workflow (inbox → CRM, claims packet, close checklist). Margin dies when the offer is “AI strategy.”

**Moats:** none unless you **productize** (templates, evals, a thin app). Pure hours do not compound.

**Small team:** **highest near-term cash**, lowest terminal value unless the service becomes software.

### 3.11 Data labeling / evals / observability — **necessary spend; split market**

**Who pays:** labs and enterprises that cannot ship agents without traces, scores, and human review.

**Evidence:**

- Scale: Sacra **~$2B revenue in 2025** (from **$870M** 2024) — **estimate**, company private. Applications sub-business **$200–300M** by Sep 2025 (interim CEO, via Sacra). ([Sacra](https://sacra.com/c/scale-ai/))
- Menlo: incumbents (Datadog, Snowflake, Databricks) still take **56%** of *enterprise infra* spend; AI-native DBs/obs grow but do not displace.
- Software evals/obs (LangSmith, Langfuse, Arize, Braintrust, Datadog LLM) have **clear willingness-to-pay** (tokens + traces are a cost center CFOs can see) but **no reliable public category revenue**.

**Small team:** **evals + agent observability + policy** for a regulated niche is one of the few infra-ish wedges that is still software-shaped.

### 3.12 Other segments the evidence supports

| Segment | Signal | Profit? | Small-team? |
| --- | --- | --- | --- |
| **Workflow automation platforms** (n8n, etc.) | Menlo cites n8n community → contract path | Not public | Yes (plugins, vertical templates) |
| **AI-native finance/ERP** (Rillet, Campfire, Numeric) | Menlo: startups **91%** of that departmental slice; dollars still small | Unlikely | Possible down-market |
| **Compliance / GRC** (Vanta cited at **$300M ARR** Apr 2026 in trade press) | Security questionnaires are a budgeted pain | Unknown | Crowded |
| **Search / knowledge** (Glean-class) | High ACV, long sales | Unknown | Hard vs Microsoft/Google |
| **Ads on AI surfaces** | OpenAI nascent ads cited in Aug 2026 run-rate stories | Too early | No |

---

## 4. Where money is made today vs hype / unprofitable growth

### Money is made today (high confidence)

1. **Selling scarce AI compute and memory** — NVIDIA, SK hynix, Broadcom, and the profitable cloud segments. This is the only layer where **tens of billions of GAAP profit** are on the record.
2. **Selling more of an already-profitable software suite because of AI** — Adobe, Microsoft Cloud / Copilot seats, CrowdStrike modules, Salesforce/ServiceNow attach (attach can be real even when the *metric definition* is slippery).
3. **Selling governed operationalization of models on proprietary data** — Palantir’s commercial print is the cleanest public “AI platform” P&L.
4. **Selling implementation** — Accenture-scale SI and long-tail boutiques. Lower glamour, real invoices.
5. **A handful of capital-light consumer/pro tools** — Midjourney/Gamma-class, *if* you believe the secondary profitability reports.

### Revenue is real; profit is not (or not shown)

1. **Frontier labs** — OpenAI’s 2025 audited operating loss **exceeded** revenue. Anthropic’s 2026 run-rate is stunning; **durable GAAP profit is not established**.
2. **Neoclouds** — CoreWeave’s backlog is a demand proof and a **leverage** proof.
3. **Most vertical AI unicorns** — ARR and multiples are disclosed; **margins almost never are**.
4. **Coding IDEs at multi-billion run-rate** — WTP is proven; **whether inference leaves a software margin** is the 2026–27 question.
5. **Humanoid robotics (West)** — deployments in the hundreds, GPU bills in the billions.

### Hype / weak economic evidence

- **“95% of genAI projects fail”** (MIT 2025) vs Menlo’s **47% production conversion** — both can be true if they measure different things (transformational programs vs purchased tools). Do not use either as a single truth.
- **Horizontal chat wrappers** and **undifferentiated content mills**.
- **TAM slides for humanoid labor ($9T by 2050)** — not 2026 cash.
- **Equating run rate with a year of revenue** (Anthropic $65B, OpenAI $40B, Cursor $3–4B). These are **instantaneous extrapolations**.
- **Calling interchange businesses “AI SaaS”** (parts of fintech).

McKinsey + Gartner rhyme: **conviction and spend are running ahead of enterprise EBIT**. That is the definition of a market that will **pay for ROI-shaped products** and **starve science-fair agents**.

---

## 5. Geographic and distribution notes

**United States — the profit and price center**

- Palantir: U.S. is **>81%** of Q2’26 revenue; U.S. commercial is the growth engine.
- Stanford HAI 2026 AI Index (via secondary): U.S. private AI investment **$285.9B** vs China **$12.4B** in 2025 — China figure **understates** state funds. Use as **direction**: the priced software market is still U.S.-led. ([Axis Intelligence citing Stanford HAI, Apr 2026](https://axis-intelligence.com/corporate-ai-spending-statistics/))
- Ramp (70k+ U.S. businesses, tech-skewed): **~56%** paid for AI by Jul 2026; Anthropic and OpenAI **trade share**; median firm spends only **~$12 per employee / month** on AI, while the top 1% spend **~$7,400 per employee**. **Power-law spend.** ([Ramp, Aug 2026](https://ramp.com/data/ai-index-august-2026); [TechCrunch](https://techcrunch.com/2026/08/20/openai-is-gaining-on-anthropic-with-business-users-new-data-indicates/))
- **U.S. SMB:** Federal Reserve 2026 employer-firm data (via secondary) — **46%** use AI, but credit/cash constrains full rollout. SMB wants **packaged outcomes**, not platforms.

**Enterprise global**

- Microsoft: nearly **90%** of FY26 cloud revenue from customers **outside** frontier-model companies — i.e. **real economy**, not just lab circularity. ([Microsoft FY26 Q4 call](https://www.microsoft.com/en-us/investor/events/fy-2026/earnings-fy-2026-q4))
- Google: **~90% of Fortune 100** on Gemini Enterprise (company).
- Sierra: U.S. consumer-touch coverage claims (Black Friday, healthcare families) — **company marketing**, but the buyer set is clearly **U.S. + UK retail/FS**.
- Cursor chose **London** as EMEA HQ (Jun 2026 press) for regulated-industry demand — EU data residency is a **feature**, not a footnote.

**Europe**

- **EU AI Act** already covers GPAI obligations (from Aug 2025) and can apply to **U.S. vendors whose output is used in the EU** (Art. 2(1)(c)). High-risk Annex III timing was **moved** (press: toward Dec 2027) via 2026 “Digital Omnibus” — **verify the official text** before building a compliance product; this is **not legal advice**. ([Overview](https://www.regulatoryai.eu/eu-ai-act-usa/))
- Legal AI: Harvey vs Legora is an **EU/UK battlefield** (Sacra).

**China and open weights**

- DeepSeek-class models matter as a **price ceiling**, not (yet) as a U.S. SMB default. Ramp: first-time U.S. buyers still start on U.S. labs; **advanced spenders** add serving platforms.
- Physical AI hardware profit (Unitree) is more **China-shaped** than U.S.-shaped.

**Implication for a shipper:** default to **U.S. SMB and mid-market**, English-first, outcome-priced; add EU residency if the vertical is regulated; do not build a China go-to-market as a first motion unless you already have it.

---

## 6. Ranked opportunity shortlist for someone who can ship software / agents

Assumption: you are **not** building a fab, a frontier lab, or a humanoid. You can ship agents, integrate systems, and sell.

| Rank | Opportunity | Why now | Why money | Risks | Why not #1 forever |
| --- | --- | --- | --- | --- | --- |
| **1** | **Narrow vertical workflow agents with a CFO metric** (one profession, one job: denials, close, claims, bid, intake) | Menlo: buy>build, 47% production conversion; McKinsey: EBIT impact only for workflow redesign; Gartner: 2026 is the “inflection” for *tactical* enterprise spend | High WTP when hours or cash recovered are obvious; can start services-led | Domain sales cycle; incumbents; liability | Labs add “industry GPTs”; you must own **data + workflow + eval** |
| **2** | **Productized implementation → thin software** (fixed-scope agent in 4–6 weeks + $2–15k/mo managed) | Accenture cannot serve the long tail; SMB AI use is rising; time-to-cash is weeks | Cash this quarter; 2026 agency economics favor specialists *if* scoped | Services trap; utilization; key-person | Does not scale until packaged |
| **3** | **Agent evals, observability, and policy for a regulated niche** | Agents are moving to production; Gartner AI-cyber **2×** in 2026; every board asks “what did the agent do?” | Budget sits in security + platform; usage-priced traces | Datadog/Microsoft swallow the horizontal | Must stay **deeper than APM** (eval quality, domain rubrics) |
| **4** | **Mid-market voice / async CX in one vertical** | Sierra proved Fortune-scale WTP; phone is still how SMBs lose money; outcome pricing is teachable | Deflection and after-hours coverage have line-item budgets | Telephony COGS; incumbents; brand-risk of a bad call | Crowded; need a **distribution** channel (PMS, EHR-lite, dealer DMS) |
| **5** | **SDLC picks-and-shovels, not another IDE** (evals, release gates, legacy stacks, compliance codegen) | Coding is the only serious “killer app”; $4B+ and climbing; enterprises will pay to *control* agents | Developers already have cards; PLG works | Anthropic/OpenAI/MSFT/Cursor | Horizontal coding is **the** kill zone |
| **6** | **Sales/ops research & enrichment beside the CRM** | Menlo: startups took **78%** of sales-AI departmental spend in 2025 (Clay-class) | Clear ROI on pipeline | Salesforce Agentforce + Fin; Clay already there | Crowded; need a **data advantage** |
| **7** | **Creative ops (not raw generation)** | Adobe showed attach works; rights and workflow still hurt | SMB marketers pay for finished campaigns | Model quality commoditizes pixels | Weak moat without brand/rights |

**Explicitly deprioritize**

- Foundation models, GPU clouds, robotics hardware.  
- Generic chat, generic image gen, generic “AI employee.”  
- Horizontal cybersecurity platforms.  
- Anything whose only moat is “we called the API first.”

**Why this list, now:** the 2025–26 data says **enterprises will buy** (Menlo 76%), **will convert if the use case is near-term productivity** (47%), **will not show EBIT** unless workflows change (McKinsey), and **will spend most of the world’s AI dollars on infra they do not own** (Gartner). A small shipper captures profit by **owning a workflow and an outcome**, while renting intelligence that is getting cheaper.

---

## 7. What would falsify each opportunity — and next validation steps

| Opportunity | Falsifiers (any two = walk away) | Next validation (cheap, ordered) |
| --- | --- | --- |
| **1. Narrow vertical agent** | 10 design-partner calls, zero budget owner; incumbent ships the workflow inside the SoR; inference + human-review COGS > **30%** of price at target quality; 90-day paid pilot does not renew | 1) Pick one KPI (e.g. $ recovered / hour saved). 2) Shadow 5 practitioners for a day. 3) Manual-plus-model **concierge** for 3 logos at a **paid** $3–8k/mo. 4) Measure quality vs junior human on a **held-out** week. 5) Only then automate. |
| **2. Productized implementation** | Cannot name a **repeatable** 4-week package; three projects, three codebases; net margin < **15%** after owner pay; no inbound after 20 case-study outbound | 1) Sell **one** package (e.g. “after-hours clinic phone”). 2) Deliver twice in <30 days. 3) Publish a before/after number the buyer signs. 4) Productize the third copy. |
| **3. Evals / obs / policy** | Security buyer says “Datadog/Purview is enough” in 8/10 calls; you cannot detect a **real** agent failure mode they already had; CAC > 12 months of ACV | 1) Instrument **your own** agent and dogfood. 2) Offer a 14-day **failure-finding** engagement. 3) Charge for the **rubric + traces**, not a dashboard. |
| **4. Vertical voice CX** | Containment < **40%** on live calls; one PR-level failure; telco+model COGS > **40%** of fee; no PMS/EHR/DMS distribution after 15 partner meetings | 1) Record 50 real calls (consent). 2) Human-in-the-loop first. 3) Price per **resolved** contact. 4) Kill if QA fails a legal/safety rubric. |
| **5. Niche SDLC tool** | 50 PLG signups, **<5%** week-4 retention; Copilot/Claude/Cursor ships your feature; you cannot show a CI metric (MTTR, flake rate, audit findings) | 1) Dogfood on an ugly repo. 2) $20–50 PLG, then $20k team. 3) Publish an eval vs the default agent. |
| **6. Sales enrichment** | Enrichment accuracy < incumbent; legal (scraping) risk; Salesforce bundle undercuts price by **50%** | 1) Win 5 AE users on **meetings booked**, not “rows enriched.” 2) Check counsel on data sources **before** scale. |
| **7. Creative ops** | Buyer uses Adobe/Canva natively; brand-safety incident; credits unprofitable at list | 1) One agency, one brand kit, 20 assets, paid. 2) Compare cycle time to their current stack. |

**Cross-cutting falsifiers for the whole thesis**

- Frontier **usage prices** fall so far that buyers do everything in ChatGPT/Claude/Gemini and stop buying apps — *unless* you own workflow, liability, or proprietary data.  
- **Enterprise EBIT attribution** stays stuck at ~37% *and* budgets freeze (McKinsey stall + CFO winter).  
- **Regulation** (EU high-risk, U.S. state, sector rules) makes your vertical uninsurable.  
- You cannot show a **number only the live system can emit** (containment %, $ recovered, hours returned). Intention is not evidence.

---

## Appendix A — Source list (title, date, URL)

Primary / official

1. NVIDIA — *Financial Results for Fourth Quarter and Fiscal 2026*, 25 Feb 2026 — https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-Fourth-Quarter-and-Fiscal-2026/default.aspx  
2. NVIDIA — *Financial Results for First Quarter Fiscal 2027* — https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-Financial-Results-for-First-Quarter-Fiscal-2027/  
3. Microsoft — *FY26 Q4 earnings*, 29 Jul 2026 — https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast  
4. Microsoft — *FY26 Q3 earnings* (AI run rate $37B) — https://www.microsoft.com/en-us/investor/earnings/fy-2026-q3/press-release-webcast  
5. Alphabet — *Q2 2026 Exhibit 99.1* — https://www.sec.gov/Archives/edgar/data/1652044/000165204426000066/googexhibit991q22026.htm  
6. Sundar Pichai — *Alphabet earnings call Q2 2026 remarks*, 22 Jul 2026 — https://blog.google/company-news/inside-google/message-ceo/alphabet-earnings-q2-2026/  
7. Amazon — *Second Quarter 2026 Results*, 30 Jul 2026 — https://ir.aboutamazon.com/news-release/news-release-details/2026/Amazon-com-Announces-Second-Quarter-Results/  
8. Broadcom — *Q3 FY2026 financial results*, 2 Sep 2026 — https://investors.broadcom.com/news-releases/news-release-details/broadcom-inc-announces-third-quarter-fiscal-year-2026-financial  
9. SK hynix — *1Q26 Financial Results*, 22 Apr 2026 — https://news.skhynix.com/en/q1-2026-business-results/  
10. Palantir — *Q2 2026 press release (SEC exhibit)* — https://www.sec.gov/Archives/edgar/data/1321655/000132165526000039/a2026q2ex991pressrelease.htm  
11. Palantir — *Q2 2026 Letter to Shareholders* — https://www.palantir.com/q2-2026-letter/en/  
12. CrowdStrike — *Q2 FY27 exhibit 99.1*, Aug 2026 — https://www.sec.gov/Archives/edgar/data/1535527/000153552726000029/crwd-20260826xex991.htm  
13. Salesforce — *Q2 FY27 results*, 26 Aug 2026 — https://investor.salesforce.com/news/news-details/2026/Salesforce-Delivers-Record-Second-Quarter-Fiscal-2027-Results/default.aspx  
14. Adobe — *Q3 FY2026 results* (Business Wire), Sep 2026 — https://www.businesswire.com/news/home/20260910832552/en/Adobe-Reports-Record-Q3-Results  
15. CoreWeave — *Q2 2026 results* — https://investors.coreweave.com/news/news-details/2026/CoreWeave-Reports-Strong-Second-Quarter-2026-Results/default.aspx  
16. Accenture — *FY2025 Letter to Shareholders* — https://www.accenture.com/content/dam/accenture/final/accenture-com/document-4/Accenture-2025-Letter-To-Shareholders.pdf  
17. Sierra — *Sierra hits $100M ARR milestone in 7 quarters*, 21 Nov 2025 — https://sierra.ai/blog/100m-arr  
18. Gartner — *Forecasts Worldwide AI Spending to Grow 47% in 2026*, 19 May 2026 — https://www.gartner.com/en/newsroom/press-releases/2026-05-19-gartner-forecasts-worldwide-ai-spending-to-grow-47-percent-in-2026  
19. Menlo Ventures — *2025: The State of Generative AI in the Enterprise*, 9 Dec 2025 — https://menlovc.com/perspective/2025-the-state-of-generative-ai-in-the-enterprise/  

Journalism / documents

20. Ars Technica — *Leaked financial docs show OpenAI is losing billions…*, Kyle Orland, 16 Jun 2026 — https://arstechnica.com/ai/2026/06/leaked-financial-docs-show-openai-is-losing-billions-of-dollars-a-year/  
21. Bloomberg — *OpenAI’s Revenue Run Rate Tops $40 Billion Ahead of IPO*, 13 Aug 2026 — https://www.bloomberg.com/news/articles/2026-08-13/openai-s-revenue-run-rate-tops-40-billion-ahead-of-ipo  
22. CNBC — *OpenAI CFO Friar… enterprise bigger than consumer*, 14 Aug 2026 — https://www.cnbc.com/2026/08/14/openai-cfo-friar-tells-investors-that-enterprise-bigger-than-consumer.html  
23. Reuters — *Anthropic clinches $380 billion valuation…* (Claude Code >$2.5B), 12 Feb 2026 — https://www.reuters.com/technology/anthropic-valued-380-billion-latest-funding-round-2026-02-12/  
24. Reuters — *Anthropic revenue run rate tops $65 billion, source says*, 17 Aug 2026 — https://www.reuters.com/technology/anthropic-revenue-run-rate-tops-65-billion-source-says-2026-08-17/  
25. Bloomberg — *Cursor Hits $3 Billion Annual Sales Rate…*, 21 May 2026 — https://www.bloomberg.com/news/articles/2026-05-21/cursor-hits-3-billion-annual-sales-rate-ahead-of-spacex-deal  
26. CNBC — *Fireworks hits $17.5 billion valuation and $1B in annualized revenue*, 16 Jul 2026 — https://www.cnbc.com/2026/07/16/fireworks-nvidia-cloud-ai-startup-value.html  
27. TNW — *Harvey closes a $550M round at a $15.6bn valuation…* — https://thenextweb.com/news/harvey-550m-round-15-6bn-guardrails-acquisition  
28. Forbes — *Figure AI Commits $3.5 Billion To Nscale…*, 9 Sep 2026 — https://www.forbes.com/sites/jonmarkman/2026/09/09/figure-ai-commits-35-billion-to-nscale-for-up-to-100000-nvidia-gpus/  
29. TechCrunch — *OpenAI is gaining on Anthropic with business users…*, 20 Aug 2026 — https://techcrunch.com/2026/08/20/openai-is-gaining-on-anthropic-with-business-users-new-data-indicates/  
30. Ramp — *August 2026 Ramp AI Index* — https://ramp.com/data/ai-index-august-2026  

Surveys / secondary (flagged in body)

31. McKinsey State of AI 2026 coverage — https://www.fm-magazine.com/news/2026/sep/companies-financial-value-from-ai-holds-firm-in-2026/ and https://www.theregister.com/ai-and-ml/2026/08/25/mckinsey-says-enterprise-ai-is-finally-on-the-road-to-roi/5292388  
32. Dealroom — *Cursor tops $4B annualized revenue*, 9 Jun 2026 — https://dealroom.co/news/134107-cursor-tops-4b-annualized-revenue/  
33. Sacra — Harvey, ElevenLabs, Scale pages — https://sacra.com/research/harvey-at-195m-arr/ — https://sacra.com/c/elevenlabs/ — https://sacra.com/c/scale-ai/  
34. New Market Pitch — *Which AI startups are actually profitable?* — https://newmarketpitch.com/blogs/news/ai-infrastructure-profitable-startups  
35. Promethean Research — *2026 State of Digital Services* — https://prometheanresearch.com/2026-state-of-digital-services-digital-agency-industry-research/

---

## Appendix B — Confidence legend

| Claim type | Confidence |
| --- | --- |
| Public-company GAAP / segment tables cited above | **High** |
| Management run-rate / “AI business” metrics (Microsoft $37B, AWS AI $25B) | **Medium** (real, definition opaque) |
| Private ARR via Reuters/Bloomberg “sources” | **Medium** (directionally important, not underwritable) |
| Sacra / blog reconstructions | **Low–medium** |
| Agency margin anecdotes | **Low** |
| Humanoid TAM / 2050 labor replacement | **Not used for ranking** |

*Compiled 14 September 2026. Re-check NVIDIA, Microsoft, Alphabet, Amazon, Broadcom, Palantir, CrowdStrike, and the Anthropic/OpenAI S-1s when they land — those filings will retire several “source says” lines in this note.*
