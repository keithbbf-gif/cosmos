---
title: Power, water, and the building as the limit
dek: After a point the chip is fine. The substation and the cooling loop are the product managers.
slug: 41-power-water-building-as-limit
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
---

# Power, water, and the building as the limit

The DGX-1’s 3200 watts in 3U was already a facility joke in 2016. A modern NVIDIA rack, as sold in 2024 public slides, is a number you discuss with an electrician and a mechanical engineer before you discuss it with a researcher. Google’s TPU pods, from the first public photos, have the pipes in the shot on purpose. The pipes are not decoration. They are how a systolic array stays a systolic array.

This is a chip-history article because the chips asked for it. TDP on a Tesla C870 was about 170 watts. TDP on a later SXM GPU is a multiple of that, and the node has eight of them, and the rack has several nodes, and the row has a PDU story. At some point “we will just add GPUs” becomes “we will add a building.” Hyperscalers said that out loud in earnings calls. National labs said it in environmental assessments. Newspapers said it next to pictures of data centers in dry places.

Water is the part the industry learned to mention after people asked. Evaporative cooling is cheap until the watershed is a political object. Closed loops and chillers are expensive until you count the alternative, which is not running the chips. None of this is confidential engineering. It is in facility designs, in LEED brochures, in local-news fights about a campus. A magazine that prints H100 photos without pipes is doing fashion.

The public paper trail is already thick. Hyperscalers publish sustainability reports with water-usage effectiveness next to power-usage effectiveness. Municipal filings for large campuses list megawatts and acre-feet. The Green500 list, for years a niche sibling of TOP500, suddenly had a popular audience because the popular machines were the hot ones. You do not need a leaked cluster map. You need a PDF a city already posted.

I care about this because it changes what a generation means. Blackwell’s rack-scale pitch is partly a cooling pitch. Hopper’s density is a cooling problem that A100 already previewed. AMD’s dense Instinct nodes are the same problem in a different logo. The TPU pod aisle is the same problem with better photography. When every vendor’s diagram includes a CDU (coolant distribution unit), the CDU is part of the architecture.

There is a research tradition here that predates AI: the power wall in CPUs, the Green500 list, the joules-per-flop papers. AI did not invent the building as a limit. AI made the building’s limit a mainstream headline because the buyers were suddenly not only national labs. They were companies whose names people know, putting up campuses whose water permits people can read.

If you want a physical object, a flow meter on a cooling loop is more honest than a GPU. Second choice: a rack rear with manifolds. Third: a utility bill. The chip is in there somewhere.

This piece will not give you a megawatt number for a secret cluster. It will say that after 2016, a serious article about compute chips that ignores power and water is a product brochure. The building is the last layer of the machine. The last layer is starting to show up in the first slide. That is the history.

## Sources

- NVIDIA DGX-1 launch spec: 3200 W, 3U (2016).
- NVIDIA public GB200 NVL / rack-scale cooling materials (2024).
- Google public TPU pod photography and Cloud facility writing.
- Green500 and public hyperscaler energy disclosures (context, not a single cited wattage).
- Earlier CPU “power wall” literature as the pre-AI version of the same limit.
