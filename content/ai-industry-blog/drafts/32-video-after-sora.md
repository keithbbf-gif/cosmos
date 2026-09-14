---
title: "Video after Sora"
slug: video-after-sora
meta_description: "15 February 2024: Sora's minute-long demos. Runway, open video, and physics that still lies."
tags: [sora, video, runway, diffusion, 2024]
era_start: 2024-02
citations:
  - "SORA https://openai.com/index/video-generation-models-as-world-simulators/"
  - "ROMBACH2022 https://arxiv.org/abs/2112.10752"
  - "HO2020 https://arxiv.org/abs/2006.11239"
status: draft
voice_check: human
figures:
  - diagram-multimodal-pipeline
  - industry-milestones-2020-2026
---

On 15 February 2024, OpenAI posted *Video generation models as world simulators* and a reel. Sora, a diffusion transformer over spacetime patches, produced up to a minute of video from text. The Tokyo walk, the paper planes, the "it almost understands objects" claim. The research post is more honest than the reel: glass does not shatter right, food does not change state when eaten, objects appear because the sampler needed them. Red-teamers and a few artists got access first. A product you could type into came later, in stages, under safety and likeness rules that kept moving.

Runway (Gen-2, then Gen-3), Pika, Luma, Kling, and a 2024–25 pile of open and semi-open video models made the category a market before Sora was a SKU. The image-diffusion drop of 22 August 2022 had already taught the industry that a closed reel does not stay closed if the paper is close. Video is heavier — data, compute, legal — so the open file lagged. It did not fail to arrive.

<!-- ai-blog-figures:begin -->
<figure class="blog-figure">
  <img src="../assets/diagram-multimodal-pipeline/fig-02-multimodal-pipeline.svg" alt="Generic multimodal fusion pipeline across text, vision, and audio" width="1200" loading="lazy" />
  <figcaption><strong>Figure 1.</strong> Multimodal products align encoders, fuse in a shared core, then decode to text or media.</figcaption>
</figure>

<figure class="blog-figure">
  <img src="../assets/industry-milestones-2020-2026/timeline.svg" alt="Public AI industry milestones from 2020 to 2026" width="1200" loading="lazy" />
  <figcaption><strong>Figure 2.</strong> Selected milestones in research, products, and policy. <em>Not exhaustive.</em></figcaption>
</figure>

<!-- ai-blog-figures:end -->
## What the model is

Not a game engine. Not a physics engine. A generator that has seen a lot of clips and will continue them in a way that fools a first watch. Temporal consistency is the hard part: a face that stays a face, a hand that stays a hand, a sign that does not melt into new letters on frame 40. Audio is a second model, or a hope. Lip sync is a third problem.

Conditioning got better: image-to-video, video-to-video, camera-path controls, "make this storyboard move." That is where actual film people started to use the tools — not as "type a movie," as a previz and B-roll machine with a human editor at the end. The 2022 image lesson repeats. The workflow is the product. The sampler is the demo.

## Open video, slower than images

Stable Video Diffusion (Stability, November 2023) and the later CogVideo / Hunyuan / Wan-class weights (names move; check the card) are the 2024–25 "file exists" story. They are not August 2022. VRAM, data, and temporal collapse keep the hobbyist ceiling lower. That is why Hollywood's panic in February 2024 was about a *reel*, not about a torrent. The torrent came, thinner.

Runway's business was already a subscription for editors before Sora's post. That is the existence proof that a video company can be a workflow company. A research reel is not a competitor until it has a timeline, a mask, and an export that a colorist will touch.

## Data and likeness

Video on the web is copyrighted, unioned, and full of private faces. Training stories are even less public than for stills. SAG-AFTRA's 2023 strike (14 July – 9 November) already had AI likeness on the table; 2024–26 contracts and state likeness bills are the sequel. `[CITE NEEDED]` the specific rider if you brief a studio. This draft's point is smaller: a photoreal clip of a real private person is a different object from an avocado armchair. Treat it like one.

Deepfakes (see that draft) got cheaper in time. A still face plus an image-to-video model is a scam kit. Watermarks and C2PA credentials are the same incomplete answer they are for images, with a worse distribution path (a compressed vertical file on a phone).

## World simulator, the phrase

OpenAI chose it. It is a research aspiration and a marketing problem. A simulator you cannot query for "what happens if I cut this wire" is a dream. Sora's own limitations list is the assigned reading. Labs that skip that list and sell "Hollywood in a box" will meet an editor who still has a job, and a lawyer who has a new one.

Scientific simulators (weather, protein, CFD) are a different industry. Do not mash them into a text-to-video reel. See the AlphaFold draft.

## What changed for people who make moving pictures

Previz cycles shrank. Stock footage took a hit. Advertising storyboards became something a junior could animate overnight and a creative director could hate by lunch. Feature animation did not vanish. The boring middle — explainers, product loops, social fillers — is where the volume went.

Cost per usable second is the metric, not "photoreal." A clip that needs forty inpainting passes is not cheap.

## Opinion

Sora was the image-model moment for time. The physics is still a vibe. The product that will last is a control surface for editors, with credentials on the file and a human who will put their name on the cut.

If your 2026 video feature cannot say what is generated, you are shipping a liability with a timeline.
