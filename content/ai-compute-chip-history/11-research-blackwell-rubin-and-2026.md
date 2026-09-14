# Research: Blackwell, Rubin, and the year this was written

Write this stretch in pencil. Vendor peaks move. The *shape* of the
story is stable.

## Blackwell (announced 2024, deployed into 2025)

NVIDIA's Blackwell generation is a two-die GPU glued by a very fast
chip-to-chip link, sold as one GPU. Public marketing talks about
208 billion transistors, TSMC custom processes, FP4, and rack-scale
systems: GB200 NVL72 (36 Grace CPUs + 72 Blackwell GPUs in one
NVLink domain), later GB300 / Blackwell Ultra for inference-heavy
racks. Treat the "30×" and "65×" slide factors as what they are:
configured-system marketing against a chosen baseline.

The historical fact underneath the adjectives: **the unit of sale
became the rack.** A programmer still says "GPU." A datacenter
buyer says "NVL72."

## Rubin (CES January 2026)

NVIDIA announced the Rubin platform as six chips designed together:
Vera CPU, Rubin GPU, NVLink 6 Switch, ConnectX-9, BlueField-4,
Spectrum-6. The company said Rubin was in production, with partner
products in the second half of 2026. Claimed directions (again:
vendor-peak): much lower cost per inference token versus Blackwell,
fewer GPUs to train mixture-of-experts models, 50 petaflops NVFP4
inference on the GPU slide.

As of this writing (September 2026), Rubin is a public platform
launch, not yet the default card a random researcher rents. The
honest sentence is: Blackwell is the installed generation; Rubin is
the named successor arriving through partners.

## The other 2026 fact

Google, the same spring, split TPU into 8t and 8i and said Google
Cloud would also offer NVIDIA's Vera Rubin systems. That pairing is
worth a quiet line in the essay. Even the company that spent a
decade proving you do not *need* a GPU still plans to sell you one.

## How to write this without becoming a catalog

Do not list SKUs. Teach three moves:

1. Precision keeps falling (FP16 → TF32/BF16 → FP8 → FP4) so the
   same watts buy more "AI FLOPS" on a slide.
2. Memory and NVLink grow because the models do.
3. The package keeps getting bigger: die, then two dies, then a
   board, then a rack, then a building's worth of liquid cooling.

If a reader remembers only those three, the 2024–2026 chapter
worked.
