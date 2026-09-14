# Transformers public history (staged drafts)

**Status:** staged drafts. Not published. Not a textbook. Not a novelty opinion.

This folder is a **public prior-art reading pack** on transformer *architecture* from the first
public appearance of *Attention Is All You Need* (12 June 2017) forward. Each file is a draft
card: one mechanism, one model family, or one systems move, dated by **first public appearance**,
with sources and an explicit "does not claim" fence.

## Why this pack exists

The field routinely mis-dates its own architecture. Conference years silently reorder 2017–2020.
Vendor blogs and arXiv v1 dates are not the same kind of evidence. Closed labs publish
benchmarks and withhold blocks. A useful history has to say **what was specified**, **when it
became public**, and **what remained unpublished**.

This pack is architecture history, not a product catalog. Chatbots, eval leaderboards, and
application write-ups appear only when they changed the *block* (topology, position, sparsity,
cache, routing, or the training-time analogue of those).

## Staging fence

- Public papers, official model cards, official release posts, and readable `config.json` fields
  only.
- No private systems. No COSMOS. No unpublished internal stacks. No analogizing a public block
  to a private product.
- No claims about unreleased weights, leaked diagrams, or "everyone knows they use X".
- Where a lab withholds architecture (GPT-4 is the type case), the draft records the withhold,
  not a reconstruction.

## Date discipline

1. **First public appearance, not venue year.** *Attention Is All You Need* is 12 June 2017
   (arXiv v1), not NeurIPS 2017. BERT is 11 October 2018, not NAACL 2019.
2. **Say what kind of date it is:** `arxiv-v1`, `official-release`, `official-blog`,
   `model-card`, `config-json`, `community-post`.
3. **Flag weak pins.** A Reddit-origin recipe (NTK-aware scaled RoPE) is labeled weaker than an
   arXiv submission-history stamp.
4. **Do not collapse ship date with invention date.** Sliding-window attention is Longformer
   (10 April 2020). Mistral 7B (27 September 2023) is the widely noticed *ship*.

## How to read

Start with `00-reading-rules.md`, then read in filename order. Cross-links use draft ids
(`tph-01` …). A later draft may correct an earlier one; the correction is dated, not silently
back-applied.

`MANIFEST.toml` is the inventory (56 staged drafts in this revision). `validate.py` is the
mechanical check (count, frontmatter, minimum length, source lines, novelty-fence terms).

After an editor pass, numbered drafts carry `voice_check: edited` and `voice_check_date`
(ISO date) in frontmatter. That flag means copy/voice review only — not publication, not a
novelty opinion, and not a factual re-audit of every arXiv stamp.

## Draft index

See `MANIFEST.toml` for the authoritative list. The series is grouped by era, not by vendor.

## What a later pass still owes

- Re-fetch every arXiv abstract page and confirm the v1 submission-history clock (the export
  API `published` field is the v1 timestamp and is what these drafts used; a hostile check
  should still open the abstract page).
- Read `config.json` for every "this model ships X" claim that is not already tied to a card.
- Expand the 2025–2026 sparse / hybrid / linear-attention disagreement (MiniMax, Kimi, DeepSeek,
  Qwen3-Next) once those cards are re-read end to end.
