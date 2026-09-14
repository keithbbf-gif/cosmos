# Novelty and IP guardrails

Hard constraints for this staged series. They override clever framing.

## Out of scope — do not mention

- COSMOS, KMesh, ModelRater, cDeck, KDash, OpenWork, Gitur, Crucible, ThinkFast, or any house operating system, mesh, rater, dashboard, or product name
- Keith’s private systems, grants, leases, pens, or session machinery
- Unpublished product roadmaps, internal tickets, or work-order queues
- Patent dockets, claim charts, unfiled ideas, “preload” caches, or USPTO language
- Live runtime trees, ledgers, tokens, install paths, or fencing tokens
- Any scoring formula, occupancy digest, porosity tensor, or weighted public average that exists only as private correspondence or an unpublished specification
- Any system that exists only as private correspondence or an unpublished specification

If a sentence would only make sense to someone who has seen a private tree, delete the sentence.

This series is **public-evals copy**. It is not a vehicle for house architecture, and it is not a place to “explain” an unpublished instrument by analogy.

## In scope

- Published papers, datasets, technical reports, and leaderboards with public bibliographic identity
- Conference programs and published proceedings (ACL, EMNLP, NAACL, NeurIPS, ICML, ICLR, AAAI, CVPR, COLM, TMLR)
- Official project sites and dataset cards after they were made public (GLUE, SuperGLUE, HELM, LMSYS / LMArena, ImageNet, SWE-bench, and peers)
- Contemporaneous journalism and later scholarly surveys of evaluation practice
- Public product launches and papers through about 2026 (ChatGPT, GPT-4, LLaMA, Gemini, Claude, the EU AI Act) only as *context for how a public eval was used*, not as vendor copy
- Public criticism of those same evals (contamination, saturation, judge bias, demographic skew)

## Invention ban

Do not invent:

- paper titles
- author lists
- venues or years
- dataset sizes, when a size is stated
- leaderboard scores or “current SOTA” numbers that will rot
- quotations
- lab affiliations
- “internal” evals that do not appear in the public record

If you cannot cite it, leave it out. Uncertainty is allowed: “the paper reports…,” “later write-ups usually give the count as…,” “scores move; the instrument is the point.”

Prefer describing **what an eval asks** and **how it is scored** over reprinting a week’s ranking. A ranking is a weather report. The instrument is the climate.

## Novelty of the series itself

These essays are original magazine prose about a public record. They are not a dump of encyclopedia articles, not a paraphrase of a single blog, and not a rewrite of any house white paper. Where a standard survey is used (Bowman’s GLUE papers; Liang’s HELM paper; Chiang’s Arena paper; Hendrycks’s MMLU and MATH papers), name it in `BIBLIOGRAPHY.md` and do not lift distinctive phrasing.

Do not claim that this series introduces a new benchmark, a new aggregation formula, or a new “true” ranking of models.

## Dual use and harm

This series does not include methods for weapons, pathogens, or offensive cyber operations. Historical mention of military or government funding (DARPA, IARPA, ONR) stays at the level of institutions and published programs. Safety benchmarks (toxicity, bias, jailbreak suites that are already public) are described at the level of published task design, not as attack recipes.

## Review checklist before any later import

1. Search the folder for the out-of-scope names above. Any hit is a fail.
2. Search for banned style words in `STYLE_GUIDE.md`.
3. Confirm every article has `voice_check: human` and a stable `slug`.
4. Confirm no article claims a paper, prize, score, or quotation that is not in `BIBLIOGRAPHY.md` or a standard public catalog.
5. Confirm no article teaches a private scoring method or leaks an unpublished docket.
