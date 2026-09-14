# Style guide — History of AI, Retrospective

This folder is staged magazine copy for a long-arc public history of artificial intelligence. It is not product documentation, not a lab notebook, and not a press kit.

## Voice

Write as a careful magazine writer who has read the papers and the minutes, not as a model summarizing a syllabus.

- Open on a concrete scene, object, date, room, or sentence from a published text.
- Prefer names, labs, cities, instruments, and pageable citations over abstractions.
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

If a sentence could appear in a vendor white paper with the proper nouns swapped, cut it.

## Facts

- Public historical record only: published papers, books, conference programs, contemporaneous journalism, museum and archive catalogs, official prize citations.
- If a date is disputed, say so and give the competing citations.
- Quote only from published sources. Short quotations, clearly attributed. No reconstructed dialogue.
- Do not mention private systems, unpublished roadmaps, patent dockets, or any house project names. See `NOVELTY_GUARDRAILS.md`.

## Article types

**Era / overview essays** walk a stretch of years or a problem (games, speech, winters). They may name many people; they are not mini-biographies.

**Major-figure profiles** stay with one person or a documented pair (McCulloch & Pitts; Newell & Simon). A profile may cut away to a lab or a paper, then return.

## Front matter

Every article uses YAML:

```yaml
---
voice_check: human
title: "Short magazine title"
slug: kebab-case-id
kind: essay          # or profile
era: 1956            # or a span, e.g. 1986–1995
tags: [tag-one, tag-two]
portrait: assets/portraits/name.jpg   # or null
portrait_status: sourced              # sourced | placeholder | none
---
```

- `slug` is stable. Do not recycle slugs.
- `portrait` is a repo-relative path from this folder, or `null`.
- Profiles of documented pairs may list one shared image or two paths in the body.

## Portraits in body copy

Immediately after the lede (or after the first section break), embed:

```markdown
![Caption naming the person, year, and place.](assets/portraits/slug.jpg)

*Credit: Photographer or institution. License. Wikimedia Commons file title.*
```

If rights are unclear, or if a file is a commemorative graphic rather than a period likeness, use the labeled SVG placeholder and the sentence: “No redistributable likeness is included; this panel is not a photograph.” Never generate a fake historical face. A companion graphics layout should reuse these paths, not invent new ones.

## Length and shape

- Target 800–1,400 words. Cut before padding.
- Subheads are allowed; they should be specific (“Bell Labs, 1948”), not generic (“The early years”).
- End on a fact or a documented consequence, not a motivational bow.

## Names and spelling

Use the form the person published under, with a parenthetical if the public spelling varies (Spärck Jones; LeCun). Japanese, Chinese, Russian, and other names follow the published English-language paper unless a standard scholarly romanization is clearly better — then keep it consistent inside the piece.

## Series stance

This is a retrospective, not a scoreboard. Failures, winters, classified work that later entered the public record, and provincial dead ends belong in the story. So do labs outside the United States, when the public record supports them.

Do not flatten the field into a single “father of AI.” Dartmouth named a bet. It did not invent thinking machines, and it did not close the subject.
