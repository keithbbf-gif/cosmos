# P01 — MOTIF nine-stage loop (DEFINE first; iterate returns to DEFINE)

**Kind:** method. **Status:** FILE. **Fee class:** US provisional, micro $65 / small $130 / large $325.

## What it is (in-tree)

A nine-stage development method for AI-built software: **DEFINE** → RESEARCH → ARCH → CONSENSUS → BUILD → CRITICS → CONSENSUS → IMPROVE → ITERATE. **DEFINE is stage 1** (Keith 2026-09-07): freeze the feature as one clean prompt; that text is **verbatim** to every model. **ITERATE re-enters DEFINE**, then RESEARCH, not critics. Encoded `docs/MOTIF.md` 2026-08-25; DEFINE added 2026-09-07. Vendor-plural required. Dual-lane BUILD and different-family CRITICS are seats of this loop (see P02, P03, P05). Adversarial mechanics on the loop: DEFINE = prompt; CRITICS = comparison; CONSENSUS = discussion + adjudication; IMPROVE = accept + apply.

## Problem / scar

A critics-only loop (stages 5–8) can only polish the thing already built. A frozen coder and a frozen architecture stop evolving. New models, new facts, and shifted needs never re-enter.

## Written description (outline for Legal)

1. Receive a work item that is not a one-line implement.
2. DEFINE: write one clean prompt (WHAT, WHY, acceptance, off-limits, live emit). That file is the Task text. Every later model gets it verbatim. No paraphrase per lane.
3. RESEARCH: returns on disk before BUILD; prefer rails that cannot run out of credit (see P08). Same DEFINE text.
4. ARCH: rubric first; independent designs; no peeking.
5. CONSENSUS: comparison + discussion; converge or mark CONTESTED (both positions, one line to the human). No third model resolves.
6. BUILD: dual-lane, no shared context (P02). Each spike must run. Same DEFINE text.
7. CRITICS: different family; judge against DEFINE; output comparison.
8. CONSENSUS: adjudication; reconcile; prior versions are baselines.
9. IMPROVE: accept + apply; subtract as well as add.
10. ITERATE: return to DEFINE (re-state if the wish moved) then RESEARCH. Re-decide architecture, primary coder, baselines.
11. Gate: runtime-binding (P04). Exit codes and green logs are not DONE.

## Already public

`keithbbf-gif/cosmos` created **2026-08-23**. MOTIF.md in the tracked tree. US grace ~1 year from inventor disclosure. Absolute-novelty countries: already at risk for what GitHub enabled.

## Prior art to name (R1)

**Related / crowding:** ChatDev arXiv:2307.07924 (waterfall; iterate stays in test); MetaGPT arXiv:2308.00352 (SOP + shared pool); AutoGen arXiv:2308.08155; AgentCoder arXiv:2312.13010; MapCoder arXiv:2405.11403 (debug reverts to *planning*, not research); Twilio **US20250165890A1** (planner–critic–executor); **CN121436020A** (eight-stage agent DevOps; Retrain→Prompt); **CN121029145B** (waterfall MAS); aiXplain **US20260099419A1** (refine-the-config loop); Boehm spiral 1988; Scrum inspect-and-adapt.

**Not found:** a US patent whose claims *require* the last stage to re-enter a *research* stage (external returns on disk) rather than test/critique. UNKNOWN unpublished apps.

## What this is not

Not “any staged multi-agent SDLC.” Not ChatDev. Not a patent filing. Not a bake-off.

## Suggested independent idea (not a claim set)

A development loop that **defines the feature as a frozen verbatim prompt before research**, and whose iterate step is required to re-enter DEFINE then research (fresh independent designs and new critics), rather than a critics-only polish cycle.
