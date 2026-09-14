---
title: "HBM: stacking DRAM until the package screamed"
dek: High Bandwidth Memory is a plumbing story: through-silicon vias, interposers, and a thermal bill.
slug: 40-hbm-stacking-dram
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
---

# HBM: stacking DRAM until the package screamed

GDDR, the memory of gaming cards, is a set of chips around a GPU, talking over a wide, fast, power-hungry interface on a PCB. High Bandwidth Memory, HBM, is a stack of DRAM dies with through-silicon vias, sitting on an interposer next to the GPU (or the TPU, or the Instinct, or the Xe HPC tile), talking a shorter, wider, calmer-looking talk. JEDEC standardized it. SK Hynix, Samsung, and Micron shipped it. AMD put it on the Fiji consumer GPU in 2015 and made a lot of people stare at a package. NVIDIA put it on the Tesla P100 in 2016 and made a lot of people reorder their datacenters. The later letters — HBM2, HBM2e, HBM3, HBM3e — are the same idea with more speed and more heat arguments.

The magazine image is a cross-section. Dies like a club sandwich. Vias like elevators. An interposer like a city block. The GPU is the expensive building on the block. The stacks are the apartment towers that exist only to feed it. When a keynote says “8 TB/s,” that number is this sandwich plus physics plus a lot of yield anxiety.

Yield anxiety is the un-cinematic part. A stack is several chances to fail. An interposer is a large, expensive piece of silicon that does not compute. CoWoS and its cousins at TSMC became bottlenecks as famous as the GPU dies they carried. Public earnings calls and reporting in 2023–2024 treated packaging capacity as a first-class constraint. That is new in the popular story. It is old in the packaging-engineering story. HBM made packaging a headline.

Thermals are the other un-cinematic part. You have put hot DRAM next to a hot GPU under a lid that has to talk to a cold plate. The stack cannot just “be thinner” because the bits have to live somewhere. Liquid cooling in later racks is partly an HBM story. People who only talk about SM clocks are talking about the wrong thermometer.

Consumer cards mostly did not follow. HBM is expensive. Gamers want capacity at a price, and GDDR keeps being good at that. The 2015 Fiji experiment (Radeon R9 Fury X and friends) is the public reminder that you can put HBM on a game and still not make it the default. The datacenter made it the default because the alternative was lying about bandwidth.

Capacity and bandwidth are different sales. Early HBM stacks were sometimes smaller in gigabytes than the GDDR cards they sat next to. Labs accepted the smaller suitcase because the door was wider. Later stacks grew the suitcase — 80 GB A100, then the Hopper and Blackwell numbers in the public product pages — until capacity and bandwidth were the same purchase. That growth is why “how much HBM” became a cluster-planning noun, the way “how much RAM” was a PC-planning noun in 1998.

If you want a physical object, a delidded P100 or MI-series package in a lab photo is the one — or, more legally, a vendor cross-section slide. Look at how little of the expensive rectangle is “the GPU” in the old sense. The package is the product.

Skip the JEDEC recitation. The reason Pascal looked different, the reason A100 80 GB meant something, the reason a TPU pod’s per-chip memory is a sentence in a cloud doc. Stacked DRAM is how the decade answered the decade’s boss. The scream in the title is thermal and economic. Both were audible.

## Sources

- JEDEC HBM/HBM2/HBM3 public standard announcements.
- AMD Fiji / Radeon R9 Fury public HBM launch (2015).
- NVIDIA Tesla P100 HBM2 (2016); later A100 HBM2e, H100 HBM3 public specs.
- Public reporting on CoWoS / advanced packaging as a 2023–2024 constraint.
