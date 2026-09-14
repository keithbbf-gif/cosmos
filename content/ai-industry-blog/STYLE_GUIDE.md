# Style guide — AI industry blog pack

Editorial voice for every draft under `content/ai-industry-blog/`. This is a peer brief, not a content mill. If a sentence would survive a LinkedIn carousel, cut it.

## Ban list (never publish)

Do not use these words or constructions, including close cousins:

- Throat-clearing: "In today's rapidly evolving…", "In this article, we will…", "Let's explore…", "As we navigate…"
- Hedging filler: "It's important to note", "It goes without saying", "Needless to say"
- Stock verbs/nouns: "delve", "landscape", "robust", "leverage", "unlock", "empower", "utilize"
- Hype: "cutting-edge", "game-changer", "revolutionary", "transformative" as an empty adjective
- Fake closers: "In conclusion", "To sum up", "At the end of the day"
- Stacked connectives: "Moreover" / "Furthermore" / "Additionally" used to glue paragraphs that have no argument
- Fake inclusion: "Whether you're a beginner or an expert…"
- Empty dualities: "not only X but also Y" when Y adds nothing; "on the one hand / on the other hand" as decoration
- Fake rhetorical questions that the next sentence answers on cue
- Symmetrical three-item lists written because three feels complete
- Bullet dumps that replace an argument
- "Unlock the potential", "the future of AI", "exciting times"

If a banned word is the only accurate term of art (rare), rewrite the sentence.

## Do this instead

1. **Open on a fact.** A ship date, a paper, a court filing, a price, a benchmark score, a statutory article. Not a thesis slogan.
2. **Then say what changed.** One paragraph that a working engineer can disagree with. Earn the opinion.
3. **Mix sentence length.** Short after long. Do not write every sentence at the same cadence.
4. **Name versions and months.** GPT-3 (May 2020 paper; June 2020 API), Llama 2 (18 July 2023), GPT-4o (13 May 2024). Vague eras are a fail.
5. **Cite or mark thin ice.** Prefer primary papers, vendor posts, EUR-Lex, Federal Register, NIST. If the fact is second-hand, write `[CITE NEEDED]`.
6. **Admit uncertainty.** "We do not have a public training recipe" is better than a confident guess.
7. **One opinion per piece.** Not a sermon. "This mattered because…" once, then stop pressing.
8. **Cut 15%.** After the first pass, delete throat-clearing, repeated dates, and any paragraph that restates the previous one.
9. **Sound like a founder writing to peers.** Assume the reader has shipped software. Do not tutor them on what a transformer is unless the piece needs the mechanism.

## Brand and IP

Public pack = industry education. Soft watcher's voice is allowed ("we have been tracking this since the API era"). Do **not** describe internal products, patents, ledgers, fences, or "our system does X." See `NOVELTY_GUARDRAILS.md`.

If a Keith-cluster brand appears at all: waitlist-grade one-liner, or omit. Default: omit.

## Front matter

Every draft YAML includes `status: draft`. After the writer pass: `voice_check: human`. After the editor pass: `voice_check: edited`.

## Self-edit checklist (run on every file)

- [ ] First sentence is a date, ship, paper, filing, or market fact
- [ ] No banned words (search the file)
- [ ] At least one named paper or law with a URL/DOI in `citations`
- [ ] Uncertainty marked where the public record is thin
- [ ] Closing is a judgment or next fact, not "In conclusion"
- [ ] Word count roughly 1,000–1,600 after cuts (quality beats quota)
- [ ] `voice_check: human` after writer pass; `voice_check: edited` after editor pass
