# COSMOS-P01 — MOTIF nine-stage loop (DEFINE first)

**Title:** Method for defining a feature as a frozen verbatim prompt and iterating a development loop by returning to definition then research
**Kind:** Method
**Status:** FILE
**Fee:** $65 micro-entity provisional (37 CFR 1.16(d))
**Date:** 2026-09-07
**Legend:** ATTORNEY WORK PRODUCT — NOT A FILED PATENT APPLICATION — FOR COUNSEL ONLY
**Inventor:** Name of inventor: ________________________________ (counsel to complete). The source tree discloses the operator as Keith. This preparer does not sign as inventor.

Standalone written description for a US provisional. Not a filed application. Not claims. Not a novelty opinion. Counsel files. Duplicate HOW_IT_WORKS.pdf at filing.

## Cross-reference

Sisters COSMOS-P01 through COSMOS-P13. No claim of benefit of a sister. 37 CFR 1.53(c): no technical add-after.

## Field of the invention

[0001] The present disclosure relates to computer-implemented methods for developing software with a plurality of generative models, and more particularly to a staged loop in which a feature is frozen as a verbatim prompt before research and in which iteration is required to re-enter that definition and then research.

## Background of the invention

[0002] Prior multi-agent software-development loops commonly begin with a task statement that each agent is free to paraphrase. Iteration, when present, often returns to testing, critique, or planning, not to an external research stage with returns on disk. A critics-only polish cycle can improve the artifact already built; it cannot re-decide the feature when the wish has moved.

[0003] A frozen coder and a frozen architecture stop evolving. New models, new facts, and shifted needs never re-enter. The inventor observed that a missing DEFINE is a process scar: later critics cannot say whether the build is the thing that was decided, because nothing was frozen.

[0004] Related systems include staged multi-agent SDLC tools and planner-critic-executor pipelines. Those systems are identified below as information known to the applicant. They are not admitted to be prior art against any particular claim counsel may later draft.

## Brief summary of the invention

[0005] A nine-stage method is disclosed. Stage 1 DEFINE writes one clean prompt comprising what, why, acceptance, off-limits, and a live emit to honor. That file is the task text. Every subsequent model receives that exact text. No lane paraphrases it.

[0006] Stages 2 through 8 are RESEARCH (returns on disk before BUILD), ARCH, CONSENSUS (comparison and discussion), BUILD, CRITICS (comparison against DEFINE), CONSENSUS (adjudication), and IMPROVE (accept and apply; subtract as well as add).

[0007] Stage 9 ITERATE returns to stage 1 DEFINE, then to RESEARCH. It does not skip to CRITICS. Architecture, primary coder, and baselines may be re-decided. The gate of done is a value only the live system can emit (COSMOS-P04).

## Definitions

[0008] As used herein, "DEFINE" means A frozen, written prompt that states the feature as what, why, acceptance, off-limits, and live emit, used verbatim by every subsequent model.

[0009] As used herein, "MOTIF" means The nine-stage development loop of this disclosure, encoded in the COSMOS tree as docs/MOTIF.md.

[0010] As used herein, "Lane" means An isolated builder attempt with private context.

[0011] As used herein, "Live emit" means A value only the running system can produce; see COSMOS-P04.

## Brief description of the drawings

[0012] FIG. 1 is a flow diagram of the nine-stage MOTIF loop. Stage 1 is DEFINE. Stage 9 ITERATE returns to stage 1, then to RESEARCH, and does not return only to CRITICS.

[0013] The drawings are described in prose so that a person of ordinary skill can produce sheet drawings. Sheet drawings may be added by counsel before filing. Do not add new matter after a filing date.

## Detailed description

[0014] Receive a work item that is not a one-line implement. If the item is a straight implement, the loop is not required.

[0015] DEFINE: write one clean prompt. Persist it as a file. That file is the work-order task text. Every later model (research, architecture, build, critic) is given those exact bytes. Do not paraphrase per lane. Do not start RESEARCH with an unfrozen vibe.

[0016] RESEARCH: obtain returns on disk before BUILD. Prefer rails that cannot run out of credit (COSMOS-P08). The same DEFINE text is the research question. Do not skip this stage.

[0017] ARCH: publish a decision rubric first. Independent designs. No peeking across designers.

[0018] CONSENSUS (comparison and discussion): converge, or mark CONTESTED with both positions and one line to the human disposer. No third model auto-resolves.

[0019] BUILD: dual-lane, no shared context (COSMOS-P02). Each spike must run. Same DEFINE text.

[0020] CRITICS: a different family from the builders. Judge against DEFINE (is this the thing we decided), not house style. Output is a comparison.

[0021] CONSENSUS (adjudication): reconcile critiques. Prior versions are baselines.

[0022] IMPROVE: accept and apply. Subtract as well as add. Net complexity and runtime cost should trend down as capability trends up.

[0023] ITERATE: return to DEFINE. If the wish moved, re-state the feature. Then RESEARCH. Run the whole cycle again (1 through 9), not 6 through 9.

[0024] Gate: runtime-binding (COSMOS-P04). Exit codes and green logs are not done.

[0025] Vendor plurality is required. Dual-lane BUILD and different-family CRITICS are seats of this loop (COSMOS-P02, COSMOS-P03, COSMOS-P05).

[0026] In a preferred embodiment the loop is driven by a native operating-system clock (approximately fifteen seconds) from a wishlist of directional input. The human names what and why. The mesh decides how. The loop is a process, not an endpoint.

[0027] Adversarial mechanics on the loop: DEFINE is the prompt; CRITICS is comparison; CONSENSUS is discussion and adjudication; IMPROVE is accept and apply.

## Best mode

[0028] The best mode known to the inventor is the COSMOS encoding: docs/MOTIF.md (DEFINE is stage 1; ITERATE re-enters DEFINE), frozen DEFINE files under work_orders/ccr/, dual-lane BUILD through Gitur (GitHub, GitLab, Cursor), and the runtime-binding gate against live Core tree_id=KMesh-COSMOS-live.

## Further embodiments

[0029] Embodiment A: a coding product (Forge) runs the loop on a named DEFINE file; critics include a Google family model and an OpenRouter value coder; the disposer is a single chief coder.

[0030] Embodiment B: the same loop is applied to a legal packet, a diligence packet, or an IP docket by changing the packet, not the loop (skins of COSMOS-P05).

## Disclosure clock (already public)

[0031] keithbbf-gif/cosmos was created 2026-08-23T06:42:12Z. MOTIF.md is in the tracked tree. DEFINE-as-stage-1 was added 2026-09-07. United States inventor grace is about one year from the inventor's disclosure. Absolute-novelty countries may already be at risk for what GitHub enabled. Private-now does not un-publish.

## Information concerning related art (not an IDS; not a novelty opinion)

[0032] Related / crowding (information known to applicant, not an IDS, not a novelty opinion): ChatDev arXiv:2307.07924 (waterfall; iterate stays in test); MetaGPT arXiv:2308.00352; AutoGen arXiv:2308.08155; AgentCoder arXiv:2312.13010; MapCoder arXiv:2405.11403 (debug reverts to planning); Twilio US20250165890A1 (planner-critic-executor); CN121436020A (eight-stage agent DevOps); CN121029145B; aiXplain US20260099419A1; Boehm spiral 1988; Scrum inspect-and-adapt.

[0033] This search did not find a United States patent whose claims require the last stage to re-enter a research stage with external returns on disk rather than test or critique. Unpublished applications are unknown. Official Patent Public Search remains owed.

## What this disclosure is not

[0034] This disclosure is not any staged multi-agent SDLC. It is not ChatDev. It is not a patent filing. It is not a bake-off. It is not a claim that the inventor invented multi-agent software development.

## Statement of invention (not claims)

[0035] A development loop that defines the feature as a frozen verbatim prompt before research, and whose iterate step is required to re-enter DEFINE then research (fresh independent designs and new critics), rather than a critics-only polish cycle.

[0036] Counsel may draft claims. The foregoing is a statement of invention, not a claim set.

[0037] Counsel may draft claims. The foregoing is a statement of invention, not a claim set under 35 U.S.C. 112(b).

## Appendix to attach at filing

[0038] HOW_IT_WORKS.pdf (APP_OS: SCAR, ROLD, carry-over; APP_COSMOS; APP_CRUCIBLE; APP_BTS_MESH). Duplicate the appendix into this provisional at filing. A provisional cannot claim benefit of a sister.
