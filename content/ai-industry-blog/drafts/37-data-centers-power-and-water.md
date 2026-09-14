---
title: "Data centers, power, and water"
slug: data-centers-power-and-water
meta_description: "2023–26: training clusters as power contracts. IEA-class numbers, local fights, and what a token actually costs."
tags: [energy, data-centers, climate, 2024, 2026]
era_start: 2023-01
citations:
  - "IEA2025 https://www.iea.org/reports/energy-and-ai"
  - "KAPLAN2020 https://arxiv.org/abs/2001.08361"
  - "HOFFMANN2022 https://arxiv.org/abs/2203.15556"
  - "IEA2025_ES https://www.iea.org/reports/energy-and-ai/executive-summary"
  - "CEG_TMI https://investors.constellationenergy.com/news-releases/news-release-details/constellation-launch-crane-clean-energy-center-restoring-jobs"
status: draft
voice_check: edited
figures:
  - infographic-training-inference-cost
  - compute-and-scaling-2020-2026
---

On 10 April 2025 the International Energy Agency published *Energy and AI*. The executive summary's load-bearing integers: data centres used about 415 TWh in 2024, roughly 1.5% of world electricity; the Base Case more than doubles that to about 945 TWh by 2030 (a bit more than Japan's electricity use today, in their comparison). The US was 45% of the 2024 data-centre load, China 25%, Europe 15%. A later IEA follow-up (*Key Questions on Energy and AI*) restated the 2030 neighborhood around 950 TWh and put 2025 closer to 485 TWh. Quote the edition you hold. Do not mix the two tables in one slide. The direction is not in dispute: training and especially *serving* large models is now a grid story, not a laptop story.

Kaplan (23 January 2020) treated compute as a scalar. A scalar that has to live in a county with a substation, a water permit, and a neighbor who can see the steam. 2023–26 is when that scalar grew a ZIP code.

<!-- ai-blog-figures:begin -->
<figure class="blog-figure">
  <img src="../assets/infographic-training-inference-cost/infographic-training-inference.svg" alt="Schematic of training versus inference costs in a model lifecycle" width="1200" loading="lazy" />
  <figcaption><strong>Figure 1.</strong> Training capex and serving opex dominate different parts of the lifecycle. <em>Illustrative.</em></figcaption>
</figure>

<figure class="blog-figure">
  <img src="../assets/compute-and-scaling-2020-2026/timeline.svg" alt="Compute and scaling narrative from 2020 to 2026" width="1200" loading="lazy" />
  <figcaption><strong>Figure 2.</strong> Training scale, hardware cycles, and serving economics entered mainstream discourse.</figcaption>
</figure>

<!-- ai-blog-figures:end -->

## Training vs serving

A frontier pretrain is a spike: tens of thousands of GPUs, weeks to months, a power draw that looks like a mill. There are few of these runs. They matter. They are not the 2026 bill for most companies.

Inference is the bill. ChatGPT-class traffic, Copilot-in-every-IDE, image gen, now video and voice. Always-on. The IEA-class analyses that break out AI inside data-center load are the ones to prefer over a tweet that says "one prompt equals N bottles of water." Water numbers in particular are site-specific (evaporative cooling vs air, reuse, climate). A single viral integer is usually a press error. The *local* water fight in a dry county is still real.

Google, Microsoft, Amazon, and Meta all published sustainability pages that tried to square net-zero pledges with a new AI capex. One named deal: on 20 September 2024, Constellation announced a 20-year power-purchase agreement with Microsoft to restart Three Mile Island Unit 1 as the Crane Clean Energy Center (~835 MW, targeted 2028, NRC and other permits still required). SEC 8-K that same day. That is a PPA you can name. It is not a running reactor yet. The engineering fact: a 24/7 training cluster wants 24/7 firm power. Intermittent renewables plus no storage is a press release, not a cluster.

## Training-time vs the IEA curve

A single GPT-4-class pretrain has been estimated, in secondary literature, in the tens of GWh. Those estimates disagree. Do not print a fake precision. Do print this: one pretrain is a rounding error next to *years* of serving a popular consumer model. The IEA-class warning is about the serve curve and the parallel build-out of ordinary cloud, not about one paper's FLOP count.

Water: a 2024–25 Google and Microsoft disclosure fight (WUE numbers, location-based) is the document trail. Use the companies' own sustainability PDFs, dated, or do not use an integer. A viral "one prompt, one bottle" graphic is almost always a category error (training amortized wrong, or a cooling number from one site applied to all sites).

## The municipal layer

Northern Virginia, Dublin, Singapore's moratoria-and-caps, Chilean and Dutch local fights, US county zoning — the map changes. The pattern does not: a data-center developer arrives with a tax-abatement story; the grid operator says "not this year"; the community asks about water and noise; the model lab is three time zones away and does not attend the hearing.

If you are a builder, this is not your hearing. It is your *latency and region* constraint. "Deploy in us-east-1" is now a political sentence.

Export-controlled chips and domestic-content power stories also tangle. A cluster in a jurisdiction that will not sell you H100s still needs megawatts. DeepSeek's efficiency claims (see that draft) get read as an energy story as much as a chip story. Maybe. We do not have their utility bill.

## What a product team can actually change

Routing. Do not send the easy tokens to a 671B. Small models and caches are energy policy you can ship this quarter (see small-models and token-economics).

Batching and utilization. An idle reserved GPU is a pure waste. vLLM-class serving is an environmental control in the boring sense.

A "don't generate video in a loop" budget. Video and long reasoning traces are the fat requests.

Honesty. If you do not have a measured joules-per-request, do not put a leaf icon on the app. A leaf icon without a number is the 2020s version of a greenwashed PDF.

## Opinion

The scaling papers licensed a culture of "more." The grid is the first adult "no" that does not come from a safety blog. 2026 architecture that ignores the county is not ambitious. It is unfinished.

Measure the request. Route the easy ones down. Leave the leaf icon off until you can defend it in that county's units.
