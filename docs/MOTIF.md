# THE MOTIF — COSMOS's default development method (lite)

**Consumer:** COSMOS / nodes. Narrative governance. **Encoded 2026-08-25 at Keith's
order:** *"FORMALIZE and ENCODE it as a lite Motif — the default development method."*

The Motif is the COSMOS seven-stage pipeline (that built COSMOS itself) compressed to a
repeatable loop for building ONE tool or feature. COW orchestrates; the nodes do the work;
GitLab is where code lands and where a gate actually executes.

## THE SOP — the mail-carrier route + 9-stage cycle (the fundamental heart of COSMOS development)
**COW is a mail carrier on a route.** **Keith 2026-09-05:** the background cycle is the **system clock**; **Gitur is BUILD only**. **Research goes on the DOM rails.** This TUI **reviews and applies**. Open wishes and needed features are **work orders** (MOTIF 1–9), not in-band coding. Work EVERY item on the route — `docs/WISHLIST.md` open wishes, `docs/BACKLOG.md`, the DHx
open assignments, `MOTIF_TRACKER.md` incomplete rows, returns to read. For each item: **IMPLEMENT
it** — unless you can state a LEGITIMATE ISSUE, or it is OBSOLETE / SUPERSEDED. When it is not a
straight implement, run the 9-stage cycle below; never skip it silently. **When the route is
clear, hunt lost mail — first this session, then other sessions — until Keith says stop.** Never
idle (Watchdog2 enforces the ≤30s rule).

## The 9-stage cycle (run on any item that isn't a straight implement)

**Keith 2026-09-07:** adversarial model is DEFINE → research → … → comparison → discussion →
adjudication → accept → apply. **Keith 2026-09-07:** stage 1 is **PROBLEM STATEMENT /
STATED GOAL** (was DEFINE; on-disk pack key remains `define`). The prompt that leaves
stage 1 is **verbatim** to every model. No peeking. RESEARCH does not start until the
statement is on disk.

1. **PROBLEM STATEMENT / STATED GOAL** — freeze the **feature** as one clean prompt: WHAT, WHY, acceptance, off-limits,
   live emit to honor. Write it to disk. That file **is** the work order Task text. Every
   subsequent model (research, arch, build, critic) gets **that exact text**. Do not
   paraphrase per lane. Do not start RESEARCH with a vibe. A missing statement is a
   process scar (the GEM/GLM extra-pane pass that had no frozen prompt).
   **Preload SOP (Keith 2026-09-08):** each stage call is PREFIX + CACHE_RULE +
   the frozen statement, then the stage instruction as tail. No naked queries.
   `docs/PROMPT_CACHE.md`. P11.
2. **RESEARCH** — **Do not skip. Do not start BUILD until returns are on disk.** **DOM rails**, already on the mesh. ROLD Rule 1 + MESH CHARTER §4–5: SGH and GEM first, both, in parallel; write the return to file. Surfaces include **SGH**, **free Gemini / Google search**, **ChatGPT chatbot**, **Perplexity**, **Bing**. **LIVE 2026-09-06** (playwright-dom + JS, not dump-dom): **Bing SERP**, **Cloudflare AI Playground** (`glm-4.7-flash`), **Copilot CLI**. Grok.com / ChatGPT / Perplexity / Google SERP = AUTH or bot-wall until Keith signs the COSMOS Chrome profile. GEM = P7 Profile 2 + Alt+G, never `gemini.google.com/app`. Drive with the **existing Chrome path** (`cosmos_playwright_rail` + `browser_evaluate` / chrome-bridge / Chrome MCP — **no window**, Keith's screen off limits). **Ask `V:\Ai\00_TOOLS_INDEX.md` before writing anything.** Do not rebuild. **Not Gitur. Not this TUI. Not APIs.** UNKNOWN not guess.
3. **ARCH** — decision rubric FIRST, then each node designs independently (no peeking). Same DEFINE text.
4. **CONSENSUS** — **comparison + discussion.** Converge, or mark CONTESTED (both positions, one line to Keith). No third model resolves.
5. **BUILD** — code it on a branch; competing spikes for the hard part; each must RUN.
   **Cooking now (Keith 2026-09-04):** COSMOS self-build + cDeck. Voice refine **TABLED**
   (SGH Voice / Grok Voice Think Fast 2.0 fills the phone endpoint).
   **Dual-lane (Keith 2026-09-04):** Lane A = Grok 4.6 **work-order session**
   (not this orch TUI authoring `cosmos/`). Lane B = **Cursor Cloud Agent**
   (Opus 5 / Sonnet-class on Cursor Ultra, $0 marginal). Same task, **no
   shared context**. **BUILD** (this stage only) runs **through Gitur** (branched trees / PRs). Research does not. This TUI
   writes the work order, runs **Gitur for BUILD**, reviews/refines, then **CCr writes** the
   live tree. That is the
   **Adversarial Loop** (`docs/ADVERSARIAL_LOOP.md`) — two builders, not
   builder-plus-checker. Does not lift COSMOS `ANTHROPIC_OFF` (`claude -p`
   stays off). GitLab credits run the **gate** (CI) and Duo as a proposer;
   Copilot **reviews** PRs (coding-agent assignee is invalid). Composer 2.5
   refused.
6. **CRITICS** — different-family review of the build vs. **DEFINE** ("is this the thing we decided," not "is this good code"). **Output comparison.** Cursor-Opus may sit here as a family vote when it was not Lane B on this item. GEM 3.1 Pro (`vertex-coding` $300) and an OpenRouter value coder are seats when named.
7. **CONSENSUS** — **adjudication.** Reconcile the critiques; agree the fixes. No third model auto-resolves.
8. **IMPROVE** — **accept + apply.** Subtract as well as add.
9. **ITERATE** — return to stage **1 PROBLEM STATEMENT / STATED GOAL** (re-state the feature if it shifted; else reread the frozen prompt) then RESEARCH. Run the whole cycle again (1→9), **not** 6→9. Each iteration re-states the problem if the wish moved, RE-RESEARCHES — new findings, fresh independent designs, new critics — not merely re-applying fixes. Iterate until it passes the **runtime-binding gate**: proven by a value only the live tree can emit — never an exit code, never a green log.

## Iterate re-decides everything (Keith, 2026-08-25)
**The goal is intelligent variability and flexibility in the iterations** — not a rote replay of the
same loop, but a cycle that intelligently varies its approach (architecture, primary coder, models,
scope, what it compares against) by what the work needs now. Sameness is a smell; a loop that does
the identical thing every pass has stopped thinking.

**Variation is the point, and more of it means faster evolution.** Recombination in biology exists
*for* variation — that is the actual purpose it serves — and variation is what selection acts on.
COSMOS is the same engine: vendor-plurality, changing coders, and re-research are the
**recombination** that generates variation; the stage-5 critics and the runtime-binding gate are the
**selection**. Variation + selection is evolution — and *more* variation means *faster* evolution:
the design improves quicker the more genuinely different the candidates are. A monoculture — one
family, one coder, a frozen loop — gives selection nothing to choose between, and stops evolving.
This is why vendor-plural is a *requirement*, not a preference.

**Swiss cheese (Keith 2026-09-07).** One AI leaves holes. Two is much better, and still
leaves holes. Three is better still — **only if they are from different families.** Same
family is the same holes stacked. The method gets more powerful as (a) the **axis of
difference** between the models grows and (b) the **number** of models grows. Several
inexpensive models, chosen for disagreement, can **beat the single best model on price
and on performance.** A monoculture of the “best” model is the expensive way to keep
the same holes. Dual-lane BUILD and different-family CRITICS exist to punch different
holes, not to vote twice.

**Orthogonal porosity (Keith 2026-09-07; spoken Pourosity).** Porosity is a **vector**,
measured against the other seated models on the **axes of interest**, not a single
value. Pair magnitude = **disagreement frequency × error magnitude**. More
disagreement → more orthogonal that pair. Observations live in a **database** and
fold into a **tensor grid** used to seat models for token efficiency and error
discovery. Built into **Forge** and **every adversarial trial** in COSMOS or any
profile. UNMEASURED until observed. DEFINE `DEFINE_ORTHOGONAL_POROSITY.md`.
ARCH `docs/arch/ORTHOGONAL_POROSITY.md`. Docket COSMOS-P03.

Re-entering at stage 1 **PROBLEM STATEMENT / STATED GOAL** each cycle gives COSMOS the freedom to **re-state the feature**,
then change the architecture, incorporate new models and new information, re-scope to current
needs — keep what worked, replace what didn't. The design is never frozen; the loop re-decides it.
This is exactly why ITERATE returns to DEFINE then RESEARCH, not to CRITICS: a critics-only loop
(6→9) can only polish the thing already built; a define-then-research loop (1→9) can *replace* it.
New model on the market, new benchmark, a shifted need — the next iteration picks it up. The
DEFINE file is the verbatim prompt; paraphrasing it per model is a hole.

Two things iterate can change, beyond the architecture:
- **The PRIMARY CODER can change each iteration.** The lead builder is chosen per cycle from the
  competency matrix (`docs/COMPETENCY.toml`) — G46 now, F5 or Cursor or OAi next — by what fits the
  task and what worked last time. No coder is a permanent default; a stuck build is a reason to
  switch hands.
- **Prior versions are BASELINES, compared explicitly.** Each iteration's build is kept, not
  discarded. **Stage 3 (CONSENSUS)** weighs the new design against the prior one; **stage 5/6
  (CRITICS → CONSENSUS)** compares the new build against prior versions. So "keep what worked,
  replace what didn't" is *measured* — is this actually better than the last iteration? — never
  merely asserted. A regression against a prior version is a finding, not a silent loss.

## Standing rules (every stage)
- **Nothing is impossible. Nothing is new.** Every capability has a path and a precedent;
  RESEARCH finds it. "Impossible" is a research failure, not an answer. "It's async only"
  is a starting point, not a verdict.
- **Vendor-plural by requirement** — SGH and GW are the same family: three families, not
  four votes. Swiss cheese: more AIs help only when they differ; cheap plural can beat
  one expensive model.
- **A node that fails mid-run is a FINDING**, reported — never a silent absence.
- **Assert the packet contains what it claims** before reasoning about it.
- **Verify every URL/DOI a node returns.**
- **COW orchestrates, verifies, synthesizes — COW does not code** (beyond trivial glue).
- **Never delete — stage to `_delme\`.**
- **Improvement is not bloat.** Each iteration adds capability AND removes weight — dead code,
  duplication, needless abstraction. Net complexity and runtime cost trend DOWN as features go UP.
  Elegance and efficiency (speed, memory, line count, readability) are gate criteria; the stage-5
  critics judge them. A feature that leaves the code bigger, slower, or harder to read is a tax, not
  an improvement.

## Invocation
A tool-dev task names its TARGET and runs the loop. **Research** dispatches to the
**DOM rails already in BTS-MESH/COSMOS** (ROLD Rule 1; Chrome CLI / chrome-bridge; no window). Stage-5 critique may use API judges
(GEM Vertex / OA / Llama / Nova) — that is not research. **Build dual-lane:**
Grok 4.6 + Cursor Cloud (Opus/Sonnet class) **on Gitur**. GitLab CI is the
runtime-binding gate wallet (Keith 2026-09-04: ~$200 credit — bind before quoting).
COW/CCr records each stage's return to disk and synthesizes.
