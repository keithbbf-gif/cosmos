---
id: mmh-12
title: "August 2019: VisualBERT, LXMERT, and a pile-up of BERTs"
slug: 2019-visualbert-lxmert-pileup
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2019"
topics: [VisualBERT, LXMERT, UNITER, pile-up]
voice_check: edited
---

# August 2019: VisualBERT, LXMERT, and a pile-up of BERTs

Li, Yatskar, Yin, Hsieh, and Chang's *VisualBERT* (arXiv:1908.03557)
and Tan and Bansal's *LXMERT* (EMNLP 2019, arXiv:1908.07490) arrived
within days of ViLBERT. A reader in that month could be forgiven for
thinking the field had coordinated. It had not. It had a new toy
(BERT) and a shared visual input (object features) and a shared
ambition (pretrain, then finetune on VQA). The pile-up is the
history.

VisualBERT is the single-stream cousin. Concatenate region features
and word pieces. Let a transformer treat them as one sequence.
LXMERT is more elaborate: object-relationship pretraining, a
cross-modality encoder, a kitchen of auxiliary losses. UNITER
(Chen et al., ECCV 2020, arXiv:1909.11740) will soon argue for a
unified single-stream model with a carefully designed masking
menu. If you are not paid to referee these papers, the deltas are
smaller than the shared skeleton.

What the pile-up taught, in public:

- **Initialization is a method.** Almost everyone started the text
  tower from BERT. Almost everyone started the image side from a
  detector. "Pretraining" meant the *joint* phase, not training
  vision from scratch.
- **Losses proliferate when data is mid-sized.** Mask a token.
  Mask a region. Predict whether the pair matches. Predict an
  object class. The 2019–2020 papers add tasks the way 2000s NLP
  added features. CLIP's later simplicity — one contrastive loss —
  is a stylistic break, not just a data break.
- **Leaderboards compress originality.** VQAv2, NLVR2, Flickr30k
  retrieval, COCO captions. A paper is a row. Rows invite
  incrementalism. Incrementalism is not a sin. It is a phase.

I am not going to pick a 2019 winner. The public record does not
need one. What it needs is a reader who can see a later LLaVA
diagram and not say "multimodal transformers began in 2023." They
began, in the vision-language sense, when BERT met boxes. The 2023
systems will throw away the boxes, swap BERT for a larger decoder
LM, and train on instructions. That is a real change. It is a
change *from* this pile-up, not from a blank page.

If you only open one 2019 PDF, open LXMERT for the diagram or
VisualBERT for the single-stream bet. Then skip to CLIP. The years
in between are more UNITER, OSCAR, VinVL — fusion refined, tags
added, still the same household.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
