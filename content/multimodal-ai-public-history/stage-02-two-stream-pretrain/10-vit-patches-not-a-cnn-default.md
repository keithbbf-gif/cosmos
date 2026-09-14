---
id: mmh-10
title: "ViT: images as patches, and the scaling alibi"
slug: vit-patches-not-a-cnn-default
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2020-2021"
topics: [ViT, Dosovitskiy, patches, transformer]
voice_check: edited
---

# ViT: images as patches, and the scaling alibi

Dosovitskiy, Beyer, Kolesnikov, Weissenborn, Zhai, Unterthiner,
Dehghani, Minderer, Heigold, Gelly, Uszkoreit, and Houlsby's *An
Image is Worth 16x16 Words* (ICLR 2021, arXiv:2010.11929) is a
vision paper that multimodal work immediately spent. Cut the image
into patches. Embed the patches. Add a position code. Run a
transformer. Pretrain big. The title is a joke that became a
default.

This set is not a transformer history. The reason ViT is here is
**interface**. Once a photograph is a sequence of tokens, every
language trick is a candidate: masked modeling, contrastive
pairing, concatenating image tokens with text tokens. The 2019
vision-language models were still arguing about two-stream versus
single-stream BERT-on-boxes. ViT makes a third diagram cheap: one
transformer, two kinds of tokens, no convolutional backbone
required.

The paper's own caution is public and usually dropped in slides.
A vanilla transformer underperforms ResNets when data is small.
The win arrives with scale — JFT-scale pretraining in the original
telling, then ImageNet-21k reproductions. "Transformers work for
vision" is true as a 2021 headline and incomplete as a 2020 lab
note. The incomplete version matters, because CLIP's image tower
will be both a ResNet and a ViT in the same paper. The 2021 CLIP
release did not wait for the field to forget convolutions.

Neighbors worth naming without turning this into a catalog:
Carion et al.'s DETR (ECCV 2020) put a transformer on detection;
Touvron et al.'s DeiT showed you could train a ViT on ImageNet-1k
with a teacher. Those papers are public. They changed who felt
allowed to drop a CNN.

For a multimodal reader, keep one mechanical fact. A ViT-L/14, in
CLIP's naming, is a large transformer with 14-pixel patches. Stable
Diffusion's text encoder, in the 2022 model card, is a CLIP
ViT-L/14 text tower. The patch paper and the alt-text paper and
the latent-diffusion paper are three citations that meet in a
single open checkpoint. That meeting is why a 2020 ICLR submission
belongs in a 2022 weight-release story.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
