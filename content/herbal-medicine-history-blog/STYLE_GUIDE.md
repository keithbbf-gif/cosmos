# Style Guide — Herbal History Pack

Write as if a patient editor at a serious monthly will read this aloud and stop at the first false note. The subject is already dramatic. You do not need to inflate it.

## Voice check (non-negotiable)

Every draft carries `voice_check: human` (writer) or `voice_check: edited` (after EDITOR pass) in the front matter. That is a promise, not a badge. If a paragraph could have been generated as "thought leadership," cut it.

### Banned furniture

Do not use these words or moves, even ironically:

- delve, landscape (metaphorical), leverage, robust, seamless, tapestry, underscore, multifaceted
- ever-evolving, rapidly evolving, in today's world, in today's rapidly evolving…
- "it's important to note," "it goes without saying," "needless to say"
- "Whether you're a… or a…" and other fake intimacy
- three-item corporate parallels ("innovative, inclusive, and impactful")
- "journey," "space" (as in "the wellness space"), "unpack," "navigate the complexities"
- "From ancient times to the modern day" as an opening or a thesis
- "humans have always…" unless you then name a dated find
- exclamation points in body copy
- rhetorical questions that the next sentence answers with a platitude

If you catch a banned word in revision, rewrite the sentence. Do not swap in a synonym of the same fluff.

### What to do instead

- **Open on a thing.** A tablet number, a river crossing, a bottle label, a statute's short title, a garden plot, a man's pocket of fungus. Time and place in the first four lines.
- **Vary the sentences.** A short fact after a long clause. Then a name. Then a judgment you can defend.
- **Earn the opinion.** "This was a better book than Galen's" needs a reason (organization, field notes, what later copyists kept). "DSHEA was a compromise" needs who sat in the room.
- **Prefer proper nouns.** Plants with Latin binomials on first botanical mention, then the name the essay's people used. Texts with conventional English titles and original titles once. Statutes with year and popular name.
- **Keep the reader adult.** No "fun facts." No "you might be surprised." Surprise is a structure, not a promise.

## Register

Magazine-serious, not academic-footnote voice and not wellness-blog warmth. Think *Smithsonian* long feature or a *LRB* piece that has been told to keep the plants visible. Second person is rare and only when the reader is physically doing something historical (reading a label, standing in a garden). Never address "your health."

Humor is allowed when it is dry and attached to a source (Pinkham's verse ads; Clark Stanley's snake-killing act). Do not joke about poisoning, addiction, or colonial extraction.

## Structure of a draft

1. **Front matter** (YAML): `voice_check`, `title`, `slug`, `summary`, `tags`, `era`, `region`, `sources_notes`, `photo`, `legal_frame`.
2. **Hed / dek** in the body: H1 matches `title`. First paragraph is the dek in spirit — it is not labeled "dek."
3. **Photo slot** after the lede or at the first natural break. Format:

   ```
   > **Photo:** [what we want]  
   > **Caption:** [one or two sentences, specific]  
   > **License note:** [PD / museum / request; see PHOTO_NOTES.md]
   ```

4. **Sections** with short H2s. No "Introduction," "Conclusion," "In Summary."
5. **Close** on a concrete remainder (a book still in print, a statute still in force, a plant still on a shelf with a new legal name). No moral bow.

Suggested length: 700–1,200 words of body copy after the YAML. That is a web-magazine feature, not a journal article. Density is the test: names, dates, plants, statutes. Under 650 is a stub; expand or kill. Over 1,500 needs a reason (two archives, not padding). Do not inflate a tight 800-word piece with a third restatement of the hed.

## Claims tone

History and education. Folklore is labeled as folklore. Clinical evidence is labeled as trial, monograph, or absence. "Was used for" is not "treats." See `CLAIMS_GUARDRAILS.md`.

When a famous story is wrong or half-wrong (the Countess of Chinchón; "Hippocrates said let food be thy medicine" as a quote; Shennong as a datable man), say so in the essay. Do not bury the correction in a footnote the CMS will strip.

## Names, dates, transliteration

- Chinese: pinyin, tone marks optional; give characters once for book titles where useful (*Bencao Gangmu* 本草綱目).
- Arabic / Persian: common scholarly forms (Ibn Sīnā / Avicenna on first mention; Ibn al-Bayṭār).
- Sanskrit: IAST or a stable popular form, consistent inside the piece (Caraka / Charaka: pick one after the first line).
- Japanese: Hepburn (Kampō or Kampo; stay consistent).
- Plant names: *Genus species* italic, authority omitted unless the essay is about naming fights.
- Years: BCE/CE. Do not write "BC" unless quoting.

## Sources in the draft

Do not dump a bibliography at the foot of every essay. Two to five named sources in `sources_notes` plus one or two in the prose where a claim is sharp. The pack bibliography is the authority file. If you cannot find a real citation, flag the line (`[soft: need page]`) rather than inventing a journal and a year.

## Hed writing

Titles should be able to sit on a print cover line. Prefer objects and verbs over "The History of X." Subheads can be slightly more explanatory. Slugs are lowercase kebab-case, stable, no dates in the slug unless the statute *is* the subject (`pure-food-1906`).

## What "human" sounds like here

A human writer remembers that people chewed, boiled, taxed, faked, and banned these plants. A human writer gets tired of the word "tradition" and uses a specific school, shop, or ship instead. A human writer will sometimes say a famous doctor was wrong, or that a law was written for grocers as much as for patients.

If a paragraph only restates the hed in softer words, delete it.
