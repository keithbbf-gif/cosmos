# Style guide — Public AI evals and benchmarks

This folder is staged magazine copy for a public-history-and-practice series on how the field measures language, vision, code, and agents. It is not product documentation, not a lab notebook, and not a press kit.

## Voice

Write as a careful magazine writer who has read the papers and sat with a leaderboard long enough to distrust it, not as a model summarizing a syllabus.

- Open on a concrete scene, object, date, paper title, or scoring rule.
- Prefer names, labs, cities, task formats, and pageable citations over abstractions.
- Keep sentences varied. Short ones earn their keep after a long one.
- Allow a dry joke if it is true. Do not manufacture charm.
- Address a curious adult reader. Do not coach, sell, or congratulate them.

The front-matter field `voice_check: human` is a production flag, not a personality. Copy that still sounds like a briefing deck fails the flag.

## Banned habits

Do not use these words or frames:

- delve, landscape (as metaphor), leverage, robust, seamless, tapestry
- “In today’s rapidly evolving…”
- empty “Whether you’re a student or a CEO…” openers
- “It is important to note,” “Importantly,” “Moreover” as throat-clearing
- corporate cheer, thought-leadership cadence, or “the future of X is here”
- fake intimacy (“Let’s dive in,” “Buckle up”)
- invented quotes, invented awards, invented paper titles
- “SOTA” as a personality; if you must name a published number, date it and let it age
- “we propose,” “our method,” or any first-person claim that this series is research

If a sentence could appear in a vendor white paper with the proper nouns swapped, cut it.

Exception: a paper title may contain a banned word (the MMLU-Pro paper uses “Robust” in its title). Quote the title; do not adopt the adjective as house style.

## Facts

- Public record only: published papers, dataset cards, official project sites, conference programs, contemporaneous journalism.
- If a count or a year is disputed, say so and give the competing citations.
- Quote only from published sources. Short quotations, clearly attributed. No reconstructed dialogue.
- Do not mention private systems, unpublished roadmaps, patent dockets, or any house project names. See `NOVELTY_GUARDRAILS.md`.
- Do not reprint a live leaderboard. Describe the scoring rule. Scores move.

## Article types

**Overview essays** walk a problem (what a benchmark is, contamination, arena vs. static files, old n-gram metrics). They may name many instruments; they are not catalogs.

**Benchmark explainers** stay with one published instrument (GLUE, MMLU, HELM, SWE-bench). An explainer may cut away to a predecessor or a critic, then return.

## Front matter

Every article uses YAML:

```yaml
---
voice_check: human
title: "Short magazine title"
slug: kebab-case-id
kind: explainer      # or essay
era: 2018            # paper year, or a span
tags: [tag-one, tag-two]
portrait: null
portrait_status: none
---
```

- `slug` is stable. Do not recycle slugs.
- `portrait` is `null` in this pack. This is an instruments series, not a portrait gallery. Do not generate faces of living authors.
- `kind` is `essay` (problem / history of practice) or `explainer` (one public instrument).

## Figures and SEO captions

Each essay and explainer includes one original schematic under `assets/diagrams/` (see `assets/README.md`). Embed with HTML:

```html
<figure>
  <img src="../assets/diagrams/example.svg" alt="Plain-language alt text naming the benchmark and what the diagram shows" width="720" height="400" loading="lazy" decoding="async" />
  <figcaption><strong>Instrument name (venue/year).</strong> One or two sentences for readers and search: task shape, scoring rule, and what the number refuses to claim—no live leaderboard integers.</figcaption>
</figure>
```

- `alt` is mandatory and should name the benchmark (MMLU, HELM, Chatbot Arena, GLUE, …) plus the diagram topic.
- `figcaption` uses `<strong>` for the instrument line, then prose. Do not paste rotating Elo or “current SOTA.”
- Diagrams are original SVG schematics, not traced paper figures.

## Length and shape

- Target 800–1,400 words. Cut before padding.
- Subheads are allowed; they should be specific (“Nine tasks, one average”), not generic (“How it works”).
- End on a fact or a documented consequence, not a motivational bow.

## Names and spelling

Use the form the authors published under. Keep SuperGLUE’s capital G. Write ImageNet, not “Imagenet,” unless quoting. LMSYS is the research collective; Chatbot Arena is the 2023–2024 platform name in the ICML paper; later public materials also say LMArena / lmarena.ai. Name the rename when it matters; do not pretend there was only ever one noun.

Distinguish **ARC** (Clark et al., AI2 Reasoning Challenge, 2018) from **ARC / ARC-AGI** (Chollet, Abstraction and Reasoning Corpus, 2019). They are not the same test.

## Series stance

This is an explanation of public yardsticks, not a scoreboard and not a buying guide. Saturation, leakage, annotator bias, and dead instruments belong in the story. So do labs outside one coast, when the public record supports them.

Do not flatten evaluation into “the one true leaderboard.” GLUE named a habit. It did not close the subject.
