---
title: "TPU pods: when the network is the machine"
dek: After v1, Google's public TPU story stops being a board in a disk slot and becomes a room that trains.
slug: 36-tpu-pods-the-network-is-the-machine
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
portrait: null
figures:
  - ../assets/36-tpu-pods-the-network-is-the-machine/historical-timeline.svg
  - ../assets/36-tpu-pods-the-network-is-the-machine/architecture-diagram.svg
---
# TPU pods: when the network is the machine

TPU v1 was an inference sled. The next public generations — v2 and v3, announced as Cloud TPUs and described in Google papers and cloud docs — are training machines, and they come in pods. A pod is not a cute name for a server. It is a number of TPU chips wired with a custom interconnect so that a model can be sharded across a room without pretending Ethernet is the native tongue. Google’s published v2/v3 paper (“A Domain-Specific Supercomputer for Training Deep Neural Networks,” among other public write-ups) and the Cloud TPU documentation are the sources. The details of the torus-like topology and the exact chip counts per pod generation are in those documents; if you cite a number, cite them, not a keynote gif.



<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/36-tpu-pods-the-network-is-the-machine/historical-timeline.svg" alt="Timeline of public milestones for TPU pods: when the network is the machine: dated anchors from press releases, papers, and product records — not live benchmark scores." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 1. Calendar anchors for this piece. Years follow the essay; verify against Sources before publication.</figcaption>
</figure>


The conceptual move is the one NVIDIA would later make with NVSwitch racks: the network is part of the computer. On a TPU pod, the interesting failure is often a link or a scheduling constraint, not a single MXU. The interesting success is a batch that would not have fit, or a time-to-train that makes a research idea cheap enough to try. Google’s own translations, search, and later large-language-model work were trained on this class of machine. That is public. The exact internal cluster maps are not, and do not belong here.

Cloud TPUs, announced around the 2017 I/O season and then sold as a product, are how the rest of us were invited into a building we do not own. You do not buy a v2 board at Newegg. You request a slice, you compile with XLA, you pay by the hour, you hit a quota. That is a different political economy from CUDA on a card you can hold. It is closer to a supercomputing center with a credit card. The invitation is real. The ownership is not.

v4, v5e, v5p, and later public names (Trillium, Ironwood — treat marketing names as marketing names) keep the pod idea and change the memory, the chip, the optics. A staged draft should not pretend to be a 2026 product matrix. It should say the idea stabilized: Google sells and uses rooms of systolic-array chips with a first-class interconnect, and the software assumes the room.

Why a standalone article from the v1 piece? Because a sled that serves search ads and a pod that trains a model are different historical objects. One is specialization for latency. The other is specialization for throughput at scale. They share a brand and an MXU ancestry. They do not share a job.

If you want a physical object, you probably want a photograph of a TPU pod aisle from a Google I/O or Next keynote: cabinets, pipes, a human for scale. The human is important. These machines are buildings. The disk-slot board was a guest in a building. The pod is the building’s point.

I have written “the network is the machine” about too many systems. Here it is literal. The TPU without the pod network is a fast matrix unit. The TPU with the pod network is how Google chose to train at a size that made the rest of the industry buy NVIDIA rooms to keep up. That last clause is not a diss. It is the 2017–2024 plot.







<!-- chip-magazine-graphics:v1 -->

<figure class="chip-figure">
<img src="../assets/36-tpu-pods-the-network-is-the-machine/architecture-diagram.svg" alt="Architecture diagram for TPU pods: when the network is the machine: illustrative GPU or datacenter shape from the public record, not an official vendor block diagram." width="760" height="460" loading="lazy" decoding="async" />
<figcaption>Figure 2. Illustrative system shape for the argument — protocol and architecture, not scraped silicon photography unless noted.</figcaption>
</figure>
## Sources

- Google Cloud TPU documentation (v2/v3/v4/v5 public product pages; pod topologies as published).
- Jouppi et al. and follow-on Google papers on TPU v2/v3 as a training supercomputer (including CACM-facing write-ups).
- Google I/O / Next public Cloud TPU announcements (2017 onward).
- TPU v1 ISCA 2017 paper as the inference predecessor (not the pod).
