---
title: BERT, GPT-2, and the card
slug: bert-gpt2-model-cards
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 18
word_target: 600-1800
era: "2018–2020"
stack:
  - huggingface
---

# BERT, GPT-2, and the card

Google’s BERT paper (Devlin, Chang, Lee, Toutanova, arXiv:1810.04805, October 2018) and OpenAI’s GPT-2 technical report (Radford et al., February 2019) are not Hugging Face documents. They became Hugging Face objects because the library’s job was to make a checkpoint a callable. The **model card** — Mitchell et al., 2019, “Model Cards for Model Reporting” — is not a Hugging Face invention either. It became a Hub noun. This chapter is about that meeting: two famous weight releases, a documentation genre, and a website that turned both into a page you scroll.

<!-- oss-graphics:v1 -->
<figure class="oss-stack-figure">
<img src="../assets/hub-as-distribution/card.svg" alt="Annotated Hugging Face Hub model card showing license string, files, pipeline tags, gating, and what the card does not disclose." width="960" height="240" loading="lazy" decoding="async" />
<figcaption>Figure 5. What a Hub card is asked to carry. It will not carry the training dump.</figcaption>
</figure>

## BERT as a public checkpoint

Google released BERT checkpoints for `bert-base` and `bert-large`, cased and uncased, plus multilingual and Chinese variants. The license on those early files was not a community acceptable-use PDF; it was a research-friendly release in the older Google style, with the paper as the real documentation. Hugging Face’s archive map pointed at copies on their S3. The conversion to PyTorch was the library’s first miracle and first maintenance burden.

Fine-tuning BERT on GLUE was the 2019 homework. A thousand repos still contain a `BertForSequenceClassification` and a learning rate of 2e-5. That homework is how the research default (`pytorch-1-research-default`) and the 2018 wheel (`transformers-library-2018`) fused into a habit.

## GPT-2 as a staged release

OpenAI released GPT-2 in stages, citing misuse risk, with the 1.5B “large” weights arriving later in 2019. The public argument — should you ship a language model — is an ancestor of every later Llama gate. Hugging Face hosted the files people were allowed to have. The library grew a GPT-2 module. The moral argument did not get a module. It got blog posts.

When people say “OpenAI never open-sourced,” they are erasing GPT-2 and, later, `gpt-oss` (`gpt-oss-august-2025`). When people say “OpenAI always open-sourced,” they are erasing GPT-3 and the API years. The card is how you stay accurate: name the file, name the year, name the license.

## The card as a genre

Mitchell et al. asked for intended use, metrics, limitations, ethical considerations — a datasheet’s cousin for models. Hugging Face made a markdown file in a repo a first-class page. Some cards are serious. Some are a copied template and a leaderboard screenshot. The genre’s existence is still a gain. A 2016 `.caffemodel` had a filename and a prayer.

What the card will not reliably contain: the training data. What it sometimes contains: a license string that is optimistic. What it should contain: whether the download is gated, whether the architecture is a fine-tune, whether the eval is the vendor’s.

## DistilBERT and the company as a model author

Hugging Face’s own DistilBERT paper made the company a producer of weights, not only a porter. The card for `distilbert-base-uncased` is a different object from the card for `bert-base-uncased`. One is a derivative with a paper. The other is a port of Google. The Hub later filled with derivatives that did not have papers. The genre strained.

## 2026 look

A Llama 4 card and a BERT card are the same HTML template around incompatible legal objects. The template flattened the difference. This series un-flattens it. Read the license file, not the badge color.

If you want objects: arXiv:1810.04805, the GPT-2 reports, Mitchell et al. 2019, and any early `bert-base-uncased` card snapshot you can still find. The S3 URLs in `v0.1.2` are the larval cards: a name and a link, no ethics section.

## GLUE as a social protocol

A 2019 BERT fine-tune that did not report GLUE looked unfinished. The Hub later made GLUE a dataset card and a widget. Metrics as a social protocol are older than cards (see ImageNet). Cards made the protocol a markdown table. Tables lie. They also allow comparison. This series prefers a named table to a vibe.

Token limits — 512 for BERT — trained a generation to think in windows. GPT-2’s 1024 was a different window. 128K in 2024 is a different species. The card should say the window. Many still do not.

## Staged release as a parent of the gate

OpenAI’s staged GPT-2 release is the ancestor of “we might not ship the large one.” Meta’s LLaMA form is a cousin. Gemma’s terms are a cousin. The parent is the same fear: a language model in the wrong hands. The child is a PDF. Whether the PDF works is a later chapter. That the fear produced a *process* is this chapter.

## How to read a 2019 card in 2026

The template is thin. The license line may be a guess. The eval may be a screenshot. The files may have migrated from `pytorch_model.bin` to `safetensors`. Prefer the commit that has the conversion PR. Prefer the paper over the card for BERT and GPT-2. Prefer the card over the paper for a 2024 remix that has no paper.

Mitchell et al. 2019 is still the genre’s conscience. Most cards fail it. The genre is still better than a filename.

## Intended use as the line people skip

Mitchell et al. asked for intended use and out-of-scope use. GPT-2’s staged release was an out-of-scope argument in public. BERT’s card, in practice, was “fine-tune on your classification set.” The genre’s conscience and the field’s habit diverged early. The Hub later made the conscience a template and the habit a like button. Read the intended-use paragraph anyway. Write one if you upload.

## Sources

Devlin et al., BERT, 2018. Radford et al., GPT-2, 2019. Mitchell et al., “Model Cards for Model Reporting,” 2019. Sanh et al., DistilBERT. Wolf et al., arXiv:1910.03771.

See: `transformers-library-2018`, `hub-as-distribution`, `licenses-that-are-not-open`, `gpt-oss-august-2025`.
