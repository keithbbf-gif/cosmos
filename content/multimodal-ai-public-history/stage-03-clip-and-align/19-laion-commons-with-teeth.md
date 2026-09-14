---
id: mmh-19
title: "LAION-400M and LAION-5B: a commons with teeth"
slug: laion-commons-with-teeth
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2021-2022"
topics: [LAION, Schuhmann, LAION-5B, Common-Crawl]
voice_check: edited
---

# LAION-400M and LAION-5B: a commons with teeth

Schuhmann and colleagues' LAION-400M (2021) and LAION-5B (2022)
are not photograph archives in the COCO sense. They are
**index releases**: URLs, text strings, CLIP-based similarity
scores, and metadata, assembled from Common Crawl, so that a
lab can try to download the images. The 5B paper and blog
present a bilingual, billion-scale public alternative to locked
image-text sets. Stability AI's later model cards will say, in
writing, that Stable Diffusion trained on a LAION-derived
subset. That sentence is why this draft sits on the CLIP-to-
diffusion spine.

A commons with teeth means two things at once.

First, it worked. People trained OpenCLIP models. People trained
diffusion models. Researchers measured aesthetic filters,
watermark scores, language subsets. The 2022 LAION-5B release
is one of the reasons 2022–2023 open multimodal work exists in
the form it does, rather than as a pile of citations to
inaccessible industrial crawls.

Second, it bit. Because the index points at the live web, it
points at whatever the web had: copyrighted stills, medical
photographs, personal images, CSAM that later audits and a
December 2023 takedown made into international news. The
Stanford Internet Observatory report and LAION's own withdrawal
of LAION-5B pending a revised release are **public events**. A
history that mentions only the scale is a brochure.

How to read an index dataset, as a practice:

- An index is not a guarantee the file is still there.
- A CLIP similarity filter is not a consent filter.
- "We released metadata" is not the same as "we released
  pixels," and also not a way to dodge the fact that the
  intended use is to fetch the pixels.
- Aesthetic scores are model opinions. They became training
  knobs anyway (see the v1.4 model card's "laion-aesthetics
  v2 5+" line).

This set will not litigate the lawsuits. It will not pretend
the commons was only a gift. It will say that **open
multimodal pretraining in 2022 had a named corpus**, and that
the name now carries a public controversy the 2021 CLIP paper
never had to put on a download page. Stage 08 comes back to
artists and opt-out. This draft is the object those fights
were about.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
