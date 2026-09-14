---
title: Style Guide — Open-Source AI, 2015–2026
status: draft
voice_check: human
series: open-source-ai-history-2015-2026
---

# Style Guide

This series talks to people who have installed a framework, read a model card at one in the morning, or argued with a license PDF. It is history of the public stack: TensorFlow, PyTorch, Hugging Face, and the LLaMA ecosystem, 2015 through September 2026. It is not a product pitch and not a lab memoir.

## Voice

Write as a person who has hit OOM, waited on a wheel, and learned that “open” is a word companies use more loosely than the Open Source Initiative does. Prefer names, dates, repo titles, license strings, and paper titles over mood. A sentence may be short. A sentence may run if it is carrying a fact.

Speak to the reader as a peer. Do not coach. Do not cheerlead. Do not close with a moral.

First person is allowed when it is a shop observation (“the first `from_pretrained` call I ran cached a tar.gz from S3”). It is not a diary.

## Banned phrasing

Do not use: delve, landscape (metaphorical), robust, leverage, unlock, cutting-edge, game-changer, “In today’s,” “It’s important to note,” Moreover, “Whether you’re,” “In conclusion,” “At the end of the day,” “rich tapestry,” “journey,” “elevate,” “empower,” “seamless,” “holistic,” “unpack,” “nuanced” as filler, “democratize” as cheer, “revolution,” “Cambrian explosion,” “paradigm shift.”

Do not open with a dictionary definition. Do not close with a recap list of “key takeaways.” If a list is a working table (release dates, license names, parameter counts the vendor published), keep it. Decorative bullet stacks are out.

No COSMOS. No process talk about how the draft was written. No private systems, no internal mesh, no unpublished lab notes.

## Facts and citations

Public sources only. Prefer first-party announcements: Google Research / TensorFlow Blog, pytorch.org and GitHub releases, Hugging Face blog and arXiv, Meta AI blog, Mistral news, QwenLM GitHub, DeepSeek GitHub, OpenAI “Introducing gpt-oss,” Google Gemma posts.

A date needs a named artifact: a blog post, a GitHub tag, an arXiv id, a license file. If the day is honestly unknown, say the month. If a story is too good and the paper is thin, mark `[CITE NEEDED]`.

Do not invent a star count, a download total, a valuation, or a private conversation. Vendor marketing language (“most capable,” “frontier”) may be quoted and dated; do not repeat it as the narrator’s claim.

License names are facts. “Open source” is a claim. When Meta, Google, or a startup calls weights “open source,” name the actual license and say whether the Open Source Initiative would recognize it. That distinction is the spine of this series.

## Files

Canonical drafts live in `drafts/<slug>.md`. Slug list: `writer-slugs.json` (46). Do not add a second article tree.

After the lede, paste the matching block from `staged-embeds/<slug>.md` when one exists, or run `python3 scripts/embed_figures.py` to sync from `figure_registry.json`. Figures use HTML `<figure class="oss-stack-figure">`, `<img alt="…">` (SEO-length alt), and `<figcaption>`. Paths are relative to `drafts/`: `../assets/...`. Do not leave production comments in the body except the `<!-- oss-graphics:v1 -->` marker.

## Structure of an article

1. Open on an object a reader can see: a wheel, a tag, a torrent, a license clause, a GGUF filename, a Hub card.
2. Name the people and orgs who shipped it, with dates.
3. Say what the code or weights actually did — graph mode, eager mode, a tokenizer, a KV cache, a gate on a download form.
4. Say what the license permitted and refused.
5. Walk the public aftermath: forks, papers, competing stacks, the next release.
6. Leave the reader with one way to look at a repo, a card, or a `NOTICE` file now.
7. End with sources and cross-links, not a sermon.

One unified essay. No “original” plus a repeating appendix. No recap that restates the lede.

Target 600–1,800 words of body text. Frontmatter, figure captions, HTML comments, and source lists do not count toward the band. Longer is allowed when the file needs it; padding is not.

## Frontmatter (every article)

```yaml
---
title: "Plain title, no colon-stack if you can help it"
slug: kebab-case
series: open-source-ai-history-2015-2026
status: draft
voice_check: human
reading_order: 12
word_target: 600-1800
era: "2015–2026"
stack:
  - pytorch
---
```

WordPress import: `status: draft` only. Do not set publish dates.

## Names and spelling

American spelling in the running text. Keep project names as the projects spell them: TensorFlow, PyTorch, Hugging Face, LLaMA (2023 paper and first release), Llama 2 and later (Meta’s later branding). Use the spelling the artifact used in the year you are writing about, and note the change when it matters.

`from_pretrained`, `torch.compile`, `llama.cpp`, GGUF, PagedAttention: code and format names stay as shipped.

## Numbers

Parameter counts as the vendor published them (7B, 70B, 405B, 671B total / 37B active). Do not convert marketing “equivalent size” claims into facts. Dates: 2015-11-09, or “15 February 2017,” not “the late 2010s,” unless the year is honestly unknown.

## Photos and figures

Editorial SVGs live in `assets/`. Captions stay in `<figcaption>`. Prefer public-domain or first-party diagrams you redrew. Do not paste copyrighted press photos. Rights ledger: `RIGHTS.md`. QA: `python3 scripts/validate_graphics.py`.
