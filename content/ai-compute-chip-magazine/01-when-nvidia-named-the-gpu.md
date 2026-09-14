---
title: When a graphics chip got a new job title
dek: In August 1999 NVIDIA did not invent 3D. It invented a word that would outlive the card.
slug: 01-when-nvidia-named-the-gpu
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
---

# When a graphics chip got a new job title

The press release is dated August 31, 1999, Palm Springs. NVIDIA called the GeForce 256 “the world’s first graphics processing unit.” That sentence is marketing. It is also, twenty-seven years later, still how a lot of people date the birth of the GPU. The honest version is less cinematic and more useful: a company that already sold 3D chips decided the next chip deserved a new job title, then defined the title so that only their chip fit.

NVIDIA’s own definition, printed in the launch materials and later quoted everywhere, was a single-chip processor with integrated transform, lighting, triangle setup and clipping, and rendering — and a floor of ten million polygons a second. Hardware transform and lighting was the actual product. The CPU had been doing that geometry work. Moving it onto the card meant the host processor could stop grinding vertices and the frame rate could stop stuttering when a scene got busy. CNN’s write-up the same day put it in plainer English: the main processor would no longer have to share the job of making the picture.

None of this was a computer in the later sense. The GeForce 256 did not run C. It did not train a network. It did not even pretend to. It was a better 3D pipeline with a name that sounded like a peer of the CPU. That was the trick, and it worked. “Accelerator” was a peripheral. “Processing unit” was a colleague.

The card itself shipped in two memory flavors. The SDR version reached stores on October 11, 1999. A DDR version followed in December. The chip was NV10, built at TSMC on a 220-nanometer process, a Direct3D 7 part. If you owned a TNT2, this was the upgrade that made hardware T&L feel like a generation and not a checkbox. If you owned a Voodoo, it was another reminder that the 3D wars were no longer about a Glide-only add-in card.

The comparison NVIDIA liked was a Cray. The launch copy claimed more than fifty gigaflops and invited you to picture a tiny supercomputer on an AGP slot. That number is a period piece. Peak floating-point on a graphics chip in 1999 was not a scientific workload. It was lighting math, matrix work already aimed at triangles. The later habit of quoting GPU teraflops as if they were the same species of flop as a CPU LINPACK run starts here, in the habit of using a supercomputer as a prop.

Jen-Hsun Huang — he still used the hyphen then — said the GPU would “fundamentally transform the 3D medium” and broaden it past game enthusiasts. He was selling to OEMs and to a press that still thought of 3D as a hobbyist tax. The transformation he got, eventually, was not the one on the slide. The word GPU escaped the press release and became the name of a class of machines that would spend most of their lives nowhere near a monitor.

That escape took years. Between 1999 and 2006 the chips got programmable shaders, then more of them, then a compiler that treated those shaders as a place to put ordinary C. People who write the CUDA origin story sometimes start in 2006 and treat the GeForce 256 as folklore. The folklore matters. Before you can ask a graphics chip to be a computer, someone has to insist it is already a processor. NVIDIA did that in public, on a Tuesday, with a definition written to win a category.

A careful reader should keep two facts in the same hand. First: 3D hardware existed before NV10. 3dfx, ATI, S3, and NVIDIA’s own RIVA line had already taught a generation of kids what a 3D card was. Second: “GPU” as an industrial noun is a 1999 branding event that stuck. History is allowed to be both. The magazine mistake is to treat the press release as a scientific first, or to treat the branding as a lie. It was a claim about integration, timed to Direct3D 7, aimed at a CPU that was running out of time to do geometry.

If you want a physical object, find a GeForce 256 SDR card with the big heatsink and the AGP tab. It will not run a modern driver. It will not speak CUDA. It will sit there looking like a graphics card, which is what it was. The job title is the part that survived.

## Sources

- NVIDIA, “NVIDIA Launches the World's First Graphics Processing Unit: GeForce 256,” August 31, 1999 (archived press release).
- CNNfn, “nVidia unveils new computer graphics accelerator,” August 31, 1999.
- NVIDIA corporate timeline, 1999 (GeForce 256 listed as first GPU; Quadro listed November 1999).
- Public GeForce 256 / NV10 product record: announce August 31, 1999; SDR ship October 11, 1999.
