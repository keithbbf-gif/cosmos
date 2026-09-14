# Novelty guardrails — what this pack must never publish

This folder is industry education. It is not a product dump, a patent brief, or a COSMOS design note. If a sentence would help a competitor reconstruct an internal system, it does not belong here.

Counsel has not cleared product claims. Default: omit the brands. A waitlist-grade one-liner is the maximum if marketing later insists.

## Never publish

### Internal systems and architecture

- COSMOS Core, live-tree layout, ledger format, hash chain, fencing tokens, lease arbiter, spend gate, return-watcher, registry/prober internals
- `cosmos_paths`, sentinel verification, runtime root vs repo tree, CCR lease mechanics, WD2 / Activity Clock / MOTIF as an executable control loop
- KDash, cDeck, Gitur, Crucible, OpenWork occupancy, rail wiring, worker fencing, commit gateway
- Any file path under `cosmos/`, `live/`, `kdash/`, `docs/FINAL_ARCHITECTURE.md`, or patent/docket trees
- "How we actually run models" diagrams, even if relabeled as "a typical mesh"

### Product internals (even if the name is public someday)

- ModelRater: scoring method, judge mix, contamination handling, arena design, private eval sets
- DailyScar: scar taxonomy, incident pipeline, "placation" encoding as a product feature
- LMNator: tokenizer claims, vocab tricks, training recipe
- BrokenTokn: tokenizer-break tests, adversarial token methods
- Any "our eval is better because…" comparison that reveals a private benchmark

### Legal / IP

- Patent claims, claim charts, novelty statements, reduction-to-practice notes
- Trade secrets, unpublished timestamps, unpublished experiments
- Customer names, spend, tokens, or live configs
- Anything that reads as "we invented X in year Y"

### Fabrication

- Fake screenshots of unreleased products
- Invented quotes from Keith, vendors, or regulators
- Invented metrics ("our arena", "our 2026 score")
- Back-dated "we predicted this" copy

## Allowed

- Public industry history from 1 January 2020 to the present, cited
- Named public papers, models, statutes, executive orders, NIST publications
- High-level safety and eval *concepts* that are already in the open literature (RLHF, RLAIF, contamination, Elo arenas)
- Soft watcher voice: "people who build with these systems have been watching X"
- Waitlist-grade one-liners, if counsel later clears a brand name, with **no mechanism**

Example of a cleared-shape line (do not add until asked):

> We watch how public evals fail. Details later.

Example of a forbidden line:

> Our rater uses a fenced three-judge panel and a private scar ledger.

## Review question before any WP publish

Would a sharp engineer learn something they could only have learned from this company's internals? If yes, delete the sentence.
