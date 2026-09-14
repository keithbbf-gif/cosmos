---
title: "The other house on the board: ATI, then AMD"
dek: GPU history is often told as an NVIDIA monologue. The other house shipped cards, bought a company, and spent years trying to make compute a second language.
slug: 03-ati-radeon-the-other-house
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# The other house on the board: ATI, then AMD

Walk into a PC shop in 2002 and the graphics wall was not a monologue. ATI’s Radeon 9700 Pro sat next to NVIDIA’s GeForce 4, then GeForce FX, and the arguments were about DirectX 9, anisotropic filtering, and which driver would crash Unreal Tournament less often. ATI had come out of Toronto with the Rage line and then, with Radeon, a name that stuck. The 9700 was the card that made a lot of people say the other house had the better chip that year. That sentence is allowed. It does not require a later morality play.

ATI’s public story is a company that could win a generation and still not own the platform. They shipped the Radeon 8500 into the DirectX 8 fight, then the 9700 into DirectX 9, then a long Radeon X and HD sequence after AMD announced in 2006 that it would buy ATI. The deal closed that October. From then on the graphics house was a division inside a CPU company that needed a discrete GPU story and, later, an APU story, and, still later, a datacenter GPU story.

The acquisition is the hinge. AMD paid for graphics because Intel had the CPU market and the next fight looked like a combined chip. The living-room version of that idea became the APU: CPU and GPU on one die, cheap laptops, consoles. The Xbox 360 and then the later consoles kept ATI-descended graphics in living rooms even when the enthusiast PC forums had crowned someone else. Console silicon is a different magazine, but it is public and it matters. A lot of the world’s GPUs in the late 2000s were not GeForce cards. They were SoCs in boxes under TVs.

Compute is where the other house kept arriving late to a language NVIDIA already spoke. ATI Stream and Close-to-Metal were the early attempts to let developers treat Radeon as a calculator. Then OpenCL, which AMD publicly championed when Khronos ratified 1.0 in December 2008. Then ROCm in 2016, and HIP as a CUDA-shaped dialect. Each of those is its own article. The point here is occupancy: there was always another stack, and it was not a thought experiment. It shipped drivers, SDKs, and cards you could buy.

Why tell this as a standalone piece instead of a footnote in an NVIDIA biography? Because the GPU as a cultural object was a two-house market for a long time, and the compute era did not erase that. It rearranged the scores. NVIDIA took the research lab and then the datacenter. AMD kept a share of the gaming wall, took a share of consoles, and — years later — put Instinct accelerators into Frontier and El Capitan, machines that topped the public TOP500 lists. Those wins are real and dated. They do not retroactively make 2004 a tie.

A fair article also admits the driver jokes. ATI’s Catalyst suite, then AMD’s Software: Adrenalin, lived in a different reputation economy than NVIDIA’s GeForce driver. Some of that was forum lore. Some of it was crash logs. Magazine writing should not launder lore into fact, but it should not pretend reputation is invisible. Buyers voted with warranty returns and with “just works” advice on forums that still exist in archives.

The other house is easy to flatten into “the OpenCL company” or “the console company.” Both slogans are lazy. ATI/AMD spent a quarter century shipping rasterizers, then GCN compute units, then RDNA gaming architectures, then CDNA compute architectures — names AMD put on slides for a reason. Gaming and compute were split because the customers split. That split is public product strategy, not a secret.

If you want a physical object, find a Radeon 9700 Pro with the copper-colored cooler. Hold it next to a GeForce 4 Ti 4600. Those two cards are the argument this article is about. Neither is a TPU. Neither speaks CUDA. Both are why “GPU” became a category people could shop, return, and review — a two-vendor aisle, not a single inventor’s monument.

## Sources

- Public ATI Radeon product record, especially Radeon 8500 (2001) and Radeon 9700 (2002).
- AMD announcement and close of the ATI acquisition, 2006.
- Khronos OpenCL 1.0 ratification, December 8/9, 2008, with AMD comment in the Khronos release.
- AMD ROCm public launch, 2016; HIP as published ROCm documentation.
- Public TOP500 records for Frontier and El Capitan (AMD Instinct).
