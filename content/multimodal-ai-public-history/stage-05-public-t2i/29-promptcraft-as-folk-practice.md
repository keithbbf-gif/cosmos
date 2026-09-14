---
id: "29"
slug: promptcraft-as-folk-practice
title: Promptcraft as folk practice
stage: 05-public-t2i
stage_title: Public text-to-image
status: draft
voice: human
novelty_safe: true
public_record_only: true
primary_public_sources:
  - "Public community documentation (e.g. open prompt guides, AUTOMATIC1111 / ComfyUI docs) as folk sources"
  - "CLIP paper prompt templates (the research ancestor)"
  - "Ho and Salimans CFG (the knob the folk used)"
does_not_claim:
  - "a first author of any incantation"
  - "that folk tricks are unpublished lab secrets"
last_reviewed: 2026-09-14
---

# Promptcraft as folk practice

Promptcraft is not a paper. That is the point.

By mid-2022, people who had never trained a model were teaching each other how to talk to one. They wrote lists. They sold lists, which was embarrassing and inevitable. They discovered that `highly detailed` does a thing, that `octane render` does a thing, that naming a camera does a thing, that naming a living artist does a thing you might later regret. They discovered **negative prompts**: a second sentence to steer away from. `deformed, extra fingers, watermark, text` became a kind of prayer.

I call it folk practice because it has the structure of folklore. Anonymous or semi-anonymous authors. Variants. A craft that is tested in public and kept when it works. No single ablation. Lots of superstition. Some of the superstition later turned out to be real — word order can matter in a cross-attention model — and some of it was CFG frying a cosine. Distinguishing those, in the moment, was impossible. Distinguishing them now is still partly guesswork. A novelty-safe draft has to live in that fog.

The research ancestor is smaller and named. CLIP’s prompt templates — “a photo of a {label}” — are promptcraft with an academic ID. The templates exist because the *string is the classifier*. Once the string is also the generator’s condition, the folk just keep writing. There is no phase break, only a change of stakes: a wrong template on ImageNet costs you a point. A wrong prompt on a Friday night costs you a picture you wanted to post.

A few public genres, so this is not only vibes:

- **Quality tokens.** Words that used to be SEO or competition captions (`award winning`, `trending on ArtStation`). They work, when they work, because the pair datasets are full of those words next to pretty pictures. You are not invoking quality. You are invoking a *cluster*.
- **Medium tokens.** `oil painting`, `Polaroid`, `35mm`. These are closer to honest. The cluster is a look.
- **Artist tokens.** The ugly genre. A name as a style handle. The ethics are a later courtroom and a present-tense courtesy. Historically: it worked often enough to become default, then it became a fight.
- **Weight syntax.** `(word:1.3)`, extra parentheses, model-specific dialects. Folk interfaces on top of a sentence that was never meant to have a compiler.
- **Negative lists.** CFG’s child. A difference you subtract.

Automatic1111 and ComfyUI — public UIs, public repos — turned folk practice into **nodes and checkboxes**. That is a familiar historical move. Oral culture becomes a tool. The tool then teaches a new oral culture (people share `.json` graphs the way they shared prompt strings). I will not document every checkbox. I will say that a checkbox labeled “restore faces” is a confession that the joint failed on a region and a second model is being asked to lie locally.

There is a vision–language lesson hiding in the kitsch. The folk discovered, without writing a VQA paper, that **language priors are visual priors**. If your prompt says `queen` you may get a European crown unless you say more. If your prompt says `doctor` you may get a man. The banana was yellow again, this time in pixels. The 2017 VQA correction had no power here. There was no complementary image pair. There was only a person adding words until the prior broke.

I do not romanticize this. A lot of promptcraft is junk, and a lot of it is people trying to get a model to do something it cannot do (spell, count, keep a face across a story). The later move to *image conditions* — ControlNet, image prompts, IP-Adapters — is, among other things, an admission that language is a bad bus for spatial intent. “On the left” was always a hope.

Still: folk practice is how a method becomes a culture. If this series only had papers, 2022 would look like a sequence of arXiv IDs. It was also a sequence of shared incantations. I would rather a historian of 2030 have those incantations, even the tacky ones, than a clean diagram that nobody used.

Next: the split that decided *who* got to use them — API publics and weights publics, waitlists and wget, two cities in one year.
