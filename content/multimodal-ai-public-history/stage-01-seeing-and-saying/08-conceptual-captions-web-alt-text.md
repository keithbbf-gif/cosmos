---
id: mmh-08
title: "Conceptual Captions, 2018: the web as a caption factory"
slug: conceptual-captions-web-alt-text
series: multimodal-ai-public-history
stage: draft
status: staged
publish: false
novelty: public-record
era: "2018"
topics: [Conceptual-Captions, Sharma, alt-text, Google]
voice_check: edited
voice_check_date: 2026-09-14
---

# Conceptual Captions, 2018: the web as a caption factory

Sharma, Ding, Goodman, and Soricut's *Conceptual Captions* (ACL 2018)
is the public dataset that made alt-text look like a training plan.
The authors harvested image-caption pairs from the web, then filtered
and hypernym-substituted the text so that raw HTML alt attributes
became something a captioning model could swallow. About 3.3 million
pairs in the released training split. Not COCO's five careful
sentences. Not Visual Genome's graph. A pipeline.

The educational move is economic. Human captioning does not scale to
the style of pretraining people already wanted in language. The web
already wrote something under a lot of images: accessibility text,
SEO text, lazy filenames cleaned into phrases. Conceptual Captions
says: **that something is a dataset if you are willing to clean**.
Cleaning is the paper. Substitution of named entities, frequency
filters, the decision to publish a split instead of a scrape recipe
that would rot.

Later ALIGN and LAION will make this look small. Three million is
not four hundred million. That is the point of putting 2018 on the
timeline. There is a year when "web captions" still meant a Google
research release with a name, a workshop track, and a leaderboard
that looked like COCO's. The field practiced noisy supervision at a
size you could finetune on one lab's accelerators. Then the sizes
jumped, and the cleaning got less polite.

Problems that were already public in the 2018 paper and the later
use-reports:

- Alt-text is **not a description**. It is a function. Sometimes it
  is empty. Sometimes it is a stock-photo ID. Sometimes it is a
  marketing sentence that does not mention the visible object.
- Hypernym substitution **erases the proper name** on purpose. That
  helps generalization. It also deletes the very string a later
  OCR-heavy model will be asked to read.
- A filtered web is still a web. Brand images, Western interiors,
  English syntax. Conceptual Captions is not a census of seeing.

CLIP's WIT data is not public. Conceptual Captions is. That
asymmetry is why this draft exists. When a 2021 paper says "we
collected 400 million pairs," a reader who has held Conceptual
Captions in their hands knows what *pair* means and what *collected*
hides. The 2018 release is the teaching version. The later corpora
are the industrial version. Same family. Different locked doors.

---

**Stage:** draft. **Claim type:** public-record recap. This piece does
not propose a new method or a new research result.
