# DEFINE — COSMOS learns agent wrappers

Keith: wrappers / skills / Prompt_style per model are **another thing COSMOS learns**. Not a second memory product. Not Letta. Not a new Core.

## What is learned

Failed (or KEEP) farm turns:

`prompt → outcome → judge → xfer → prompt′ → outcome′`

The **xfer** is the learning step: append-only `STYLES/<model>.md` (preferred), or WRAP hunk if every model shares the quirk, or harness (`cosmos_sandbox.py` / `_code_or_seat.py`) if the wrapper is code. PREFIX is not rewritten (P11).

Chairs (WOMBAT / CODER / JUDGE) stay WRAP files. Models stay STYLE files. Skills name the chair; they do not bake in one vendor.

## Authority — student record, never overwrite

**Type: append-only JSONL** (same ethic as the COSMOS ledger). Not a mutable SQLite gradebook. SQLite / Model Rater `preload.json` is a **projection** for WOMB queries (ctx, rates, last score) — rebuildable from JSONL. A rejected job that is regraded is a **new row** (`attempt` 2, 3, …), not an UPDATE of attempt 1.

Each attempt stores: job/slug, chair (WOMBAT|CODER|JUDGE), model, pack, prompt bytes or path+hash, mouth `text`, http/reason, **score** (free-checker + judge ballot), xfer (style append / rate_limit / skip_slug), `attempt`, `parent_attempt` (null on first), `rejected` bool, stamps (`docs/AGENT_AUDIT.md`).

Rescore route: DROP/FAIL → xfer → prompt′ → mouth′ → score′. Keep **both** scores. Like a student: the transcript is the product.

Files: `CREW/OUT/TRANSFER/roster.jsonl`, `loops/*.jsonl`, `JUDGE_BALLOTS*.jsonl`, `ATTEMPTS.jsonl`. Schema `cosmos-score-attempt/1`.

## What WOMBAT-PE trains on

Those tuples. WOMBAT (WOMB) then writes better ITEMs; STYLE files are the weights COSMOS keeps on disk. CCr accepts skills; STYLE appends do not need a skill accept (they are tails).

## Not

A second scheduler, a second SEED, Graphiti-as-product, in-process cron, yolo. Do not retap SOL / non-flex Luna to “learn faster.”
