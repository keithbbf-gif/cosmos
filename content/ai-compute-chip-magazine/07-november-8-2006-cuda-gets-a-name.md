---
title: "November 8, 2006: CUDA gets a name"
dek: The architecture, the compiler, and the GeForce 8800 were announced the same day. The SDK the rest of us could download came later.
slug: 07-november-8-2006-cuda-gets-a-name
series: AI Compute Chip Magazine
status: staged
kind: standalone-article
scope: public-history
novelty: public-record-only
exclusions: [no-cosmos, no-patents, no-unpublished-claims]
voice_check: edited
---

# November 8, 2006: CUDA gets a name

Santa Clara, November 8, 2006. NVIDIA put two stories on the same calendar day. One was a graphics story: GeForce 8800, DirectX 10, Crysis in the demo room, nForce 680i for Intel’s new quad-cores, a San Jose unveiling aimed at people who still bought PCs to play games. The other was a computing story: CUDA, “a fundamentally new architecture for computing” on NVIDIA GPUs, and “the industry’s first C-compiler development environment for the GPU.”

The computing press release is the hinge. It says CUDA was available that day on the new GeForce 8800 and would come to Quadro. It says the new architecture let GPU cores communicate, synchronize, and share data, which — NVIDIA claimed — earlier stream computing on GPUs could not do. InfoWorld’s write-up the same day translated the pitch for people who did not live in SIGGRAPH: you could do numerical work on a graphics chip instead of relying on a standard processor.

Two calendar facts need to stay un-merged. November 8, 2006 is the public naming of CUDA and the G80 hardware launch. The public CUDA SDK and the 1.0 documentation trail into 2007. Buck has said CUDA 1.0 shipped with the 8800; NVIDIA’s own later timelines and the surviving documentation dates are fussier. Do not pretend the press release was a download link. It was a flag. The flag mattered. After that day you could say “CUDA” in a meeting and not be talking about a research compiler with a campus URL.

The name itself is Compute Unified Device Architecture. It is a mouthful that earned its first word. Unified is the hardware claim: the same cores that shade pixels can run the C you compiled. Device is the software claim: this is still a coprocessor with a memory space, not a CPU. Architecture is the sales claim: you are not buying a trick, you are buying a platform. Whether you like the acronym is irrelevant. It stuck.

Why the same day as a gaming card? Because in 2006 the only volume NVIDIA knew how to ship was GeForce. If CUDA required a special board, it would have been a workstation footnote. If CUDA required the board people were already lining up to buy for Crysis, it could hide in a million living rooms. That is not a conspiracy. That is how you seed a developer base when the developers do not yet exist.

The November 8 gaming release is easy to quote because it is so of its moment. Huang talks about Windows Vista, HD-DVD, Blu-ray, the PC as the premier gaming platform against Wii and PlayStation 3. CUDA is not in that paragraph. CUDA is in the other PDF. Reading both on the same day is the point. NVIDIA did not yet know which story would be the company’s center of gravity. In 2006 it was still a graphics company with a compiler.

A later habit is to treat 2006 as Year Zero of AI chips. That is sloppy. 2006 is Year Zero of a commercial C-on-GPU platform from NVIDIA. Neural nets were not the launch customer. Oil and gas, finance, medical imaging, academic linear algebra — those were the first people who would tolerate a new toolchain. AlexNet is 2012. cuDNN is 2014. The six-year gap is not a plot hole. It is how long it took a graphics compiler to meet a statistical fashion.

If you want a physical object, find a GeForce 8800 GTX: two slots, two six-pin power plugs, the fan that taught a generation of cases about airflow. It is a gaming card. It is also the first card whose box could, without lying, be associated with the word CUDA. The word is the event. The silicon is the reason the word was allowed to exist.

## Sources

- NVIDIA, “NVIDIA Unveils CUDA — The GPU Computing Revolution Begins,” November 8, 2006 (archived).
- NVIDIA GeForce 8800 / nForce 680i launch release, November 8, 2006 (archived).
- Ben Ames, InfoWorld, “Nvidia unveils GPU technology,” November 8, 2006.
- Public CUDA SDK / CUDA 1.0 documentation dates in 2007 (do not collapse into the November 8 naming).
