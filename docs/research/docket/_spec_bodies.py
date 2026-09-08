# -*- coding: utf-8 -*-
"""Complete written-description bodies for COSMOS-P01..P13.

Attorney work product. Not a filed application. Not claims.
Counsel drafts claims. Inventor legal name is blank.
"""
from __future__ import annotations

PREPARED = "2026-09-07"
LEGEND = (
    "ATTORNEY WORK PRODUCT — NOT A FILED PATENT APPLICATION — "
    "FOR COUNSEL ONLY"
)
INVENTOR_BLANK = (
    "Name of inventor: ________________________________ "
    "(counsel to complete). The source tree discloses the operator "
    "as Keith. This preparer does not sign as inventor."
)

# Appendix to physically attach at each FILE (37 CFR 1.53(c): no add-after).
APPENDIX = (
    "HOW_IT_WORKS.pdf (APP_OS: SCAR, ROLD, carry-over; APP_COSMOS; "
    "APP_CRUCIBLE; APP_BTS_MESH). Duplicate the appendix into this "
    "provisional at filing. A provisional cannot claim benefit of a sister."
)


def _p(*paras: str) -> list[str]:
    return [p.strip() for p in paras if p and p.strip()]


PACKETS: list[dict] = []


def add(**kw) -> None:
    PACKETS.append(kw)


# ---------------------------------------------------------------------------
add(
    id="P01",
    docket="COSMOS-P01",
    file="P01_MOTIF_LOOP.md",
    title="Method for defining a feature as a frozen verbatim prompt and iterating a development loop by returning to definition then research",
    short="MOTIF nine-stage loop (DEFINE first)",
    kind="Method",
    status="FILE",
    fee="$65 micro-entity provisional (37 CFR 1.16(d))",
    fig="FIG. 1 is a flow diagram of the nine-stage MOTIF loop. Stage 1 is DEFINE. Stage 9 ITERATE returns to stage 1, then to RESEARCH, and does not return only to CRITICS.",
    field=_p(
        "The present disclosure relates to computer-implemented methods for developing software with a plurality of generative models, and more particularly to a staged loop in which a feature is frozen as a verbatim prompt before research and in which iteration is required to re-enter that definition and then research."
    ),
    background=_p(
        "Prior multi-agent software-development loops commonly begin with a task statement that each agent is free to paraphrase. Iteration, when present, often returns to testing, critique, or planning, not to an external research stage with returns on disk. A critics-only polish cycle can improve the artifact already built; it cannot re-decide the feature when the wish has moved.",
        "A frozen coder and a frozen architecture stop evolving. New models, new facts, and shifted needs never re-enter. The inventor observed that a missing DEFINE is a process scar: later critics cannot say whether the build is the thing that was decided, because nothing was frozen.",
        "Related systems include staged multi-agent SDLC tools and planner-critic-executor pipelines. Those systems are identified below as information known to the applicant. They are not admitted to be prior art against any particular claim counsel may later draft."
    ),
    summary=_p(
        "A nine-stage method is disclosed. Stage 1 DEFINE writes one clean prompt comprising what, why, acceptance, off-limits, and a live emit to honor. That file is the task text. Every subsequent model receives that exact text. No lane paraphrases it.",
        "Stages 2 through 8 are RESEARCH (returns on disk before BUILD), ARCH, CONSENSUS (comparison and discussion), BUILD, CRITICS (comparison against DEFINE), CONSENSUS (adjudication), and IMPROVE (accept and apply; subtract as well as add).",
        "Stage 9 ITERATE returns to stage 1 DEFINE, then to RESEARCH. It does not skip to CRITICS. Architecture, primary coder, and baselines may be re-decided. The gate of done is a value only the live system can emit (COSMOS-P04)."
    ),
    definitions=[
        ("DEFINE", "A frozen, written prompt that states the feature as what, why, acceptance, off-limits, and live emit, used verbatim by every subsequent model."),
        ("MOTIF", "The nine-stage development loop of this disclosure, encoded in the COSMOS tree as docs/MOTIF.md."),
        ("Lane", "An isolated builder attempt with private context."),
        ("Live emit", "A value only the running system can produce; see COSMOS-P04."),
    ],
    detailed=_p(
        "Receive a work item that is not a one-line implement. If the item is a straight implement, the loop is not required.",
        "DEFINE: write one clean prompt. Persist it as a file. That file is the work-order task text. Every later model (research, architecture, build, critic) is given those exact bytes. Do not paraphrase per lane. Do not start RESEARCH with an unfrozen vibe.",
        "RESEARCH: obtain returns on disk before BUILD. Prefer rails that cannot run out of credit (COSMOS-P08). The same DEFINE text is the research question. Do not skip this stage.",
        "ARCH: publish a decision rubric first. Independent designs. No peeking across designers.",
        "CONSENSUS (comparison and discussion): converge, or mark CONTESTED with both positions and one line to the human disposer. No third model auto-resolves.",
        "BUILD: dual-lane, no shared context (COSMOS-P02). Each spike must run. Same DEFINE text.",
        "CRITICS: a different family from the builders. Judge against DEFINE (is this the thing we decided), not house style. Output is a comparison.",
        "CONSENSUS (adjudication): reconcile critiques. Prior versions are baselines.",
        "IMPROVE: accept and apply. Subtract as well as add. Net complexity and runtime cost should trend down as capability trends up.",
        "ITERATE: return to DEFINE. If the wish moved, re-state the feature. Then RESEARCH. Run the whole cycle again (1 through 9), not 6 through 9.",
        "Gate: runtime-binding (COSMOS-P04). Exit codes and green logs are not done.",
        "Vendor plurality is required. Dual-lane BUILD and different-family CRITICS are seats of this loop (COSMOS-P02, COSMOS-P03, COSMOS-P05).",
        "In a preferred embodiment the loop is driven by a native operating-system clock (approximately fifteen seconds) from a wishlist of directional input. The human names what and why. The mesh decides how. The loop is a process, not an endpoint.",
        "Adversarial mechanics on the loop: DEFINE is the prompt; CRITICS is comparison; CONSENSUS is discussion and adjudication; IMPROVE is accept and apply.",
    ),
    best_mode=_p(
        "The best mode known to the inventor is the COSMOS encoding: docs/MOTIF.md (DEFINE is stage 1; ITERATE re-enters DEFINE), frozen DEFINE files under work_orders/ccr/, dual-lane BUILD through Gitur (GitHub, GitLab, Cursor), and the runtime-binding gate against live Core tree_id=KMesh-COSMOS-live."
    ),
    embodiments=_p(
        "Embodiment A: a coding product (Forge) runs the loop on a named DEFINE file; critics include a Google family model and an OpenRouter value coder; the disposer is a single chief coder.",
        "Embodiment B: the same loop is applied to a legal packet, a diligence packet, or an IP docket by changing the packet, not the loop (skins of COSMOS-P05)."
    ),
    public=_p(
        "keithbbf-gif/cosmos was created 2026-08-23T06:42:12Z. MOTIF.md is in the tracked tree. DEFINE-as-stage-1 was added 2026-09-07. United States inventor grace is about one year from the inventor's disclosure. Absolute-novelty countries may already be at risk for what GitHub enabled. Private-now does not un-publish."
    ),
    prior_art=_p(
        "Related / crowding (information known to applicant, not an IDS, not a novelty opinion): ChatDev arXiv:2307.07924 (waterfall; iterate stays in test); MetaGPT arXiv:2308.00352; AutoGen arXiv:2308.08155; AgentCoder arXiv:2312.13010; MapCoder arXiv:2405.11403 (debug reverts to planning); Twilio US20250165890A1 (planner-critic-executor); CN121436020A (eight-stage agent DevOps); CN121029145B; aiXplain US20260099419A1; Boehm spiral 1988; Scrum inspect-and-adapt.",
        "This search did not find a United States patent whose claims require the last stage to re-enter a research stage with external returns on disk rather than test or critique. Unpublished applications are unknown. Official Patent Public Search remains owed."
    ),
    not_this=_p(
        "This disclosure is not any staged multi-agent SDLC. It is not ChatDev. It is not a patent filing. It is not a bake-off. It is not a claim that the inventor invented multi-agent software development."
    ),
    statement=_p(
        "A development loop that defines the feature as a frozen verbatim prompt before research, and whose iterate step is required to re-enter DEFINE then research (fresh independent designs and new critics), rather than a critics-only polish cycle.",
        "Counsel may draft claims. The foregoing is a statement of invention, not a claim set."
    ),
    appendix=APPENDIX,
)

# ---------------------------------------------------------------------------
add(
    id="P02",
    docket="COSMOS-P02",
    file="P02_DUAL_LANE.md",
    title="Method of dual-lane building with a peeking ban and a single disposer",
    short="Dual-lane BUILD, no shared context",
    kind="Method / occupancy seating",
    status="FILE",
    fee="$65 micro-entity provisional",
    fig="FIG. 1 shows two builder lanes, each with a private workspace and private context, a later compare step, and a single disposer who alone writes the live tree. A dashed prohibition marks peeking.",
    field=_p(
        "The present disclosure relates to seating two generative-model builders on the same decided work so that neither builder reads the other's context until compare, and so that only one disposer writes the live artifact tree."
    ),
    background=_p(
        "Shared-context debate lets a weak agent pollute a strong one. Builder-plus-nanny stacks a second seat hired to agree. OpenAI U.S. Patent No. 12,405,822 teaches a shared workspace — the anti-shape of this disclosure.",
        "N-version programming and parallel contestants who later rank each other are related. They are identified below. This disclosure isolates two full builders, each of which must run, with a peeking ban until compare, plus a single pen."
    ),
    summary=_p(
        "After consensus names the work, spawn two builder attempts. Each attempt has a private workspace and a private context. Neither builder may read the other's context, branch, or intermediate artifacts until compare. Each attempt must produce a running spike. Compare is a later consensus step, not a silent merge by a third model. The live tree has one writer. Builders propose; they do not hold the pen."
    ),
    definitions=[
        ("Peeking ban", "A prohibition on a builder reading another builder's context, branch, or intermediate artifacts until a later compare step."),
        ("Disposer", "The single writer of the live tree. Also called chief coder or CCr in the source tree."),
        ("Propose", "To produce an artifact in a private workspace without writing the live tree."),
    ],
    detailed=_p(
        "After CONSENSUS names the work, spawn two builder attempts (Lane A and Lane B).",
        "Give each attempt a private workspace and a private context. Do not share a transcript. Do not share a branch. Do not share intermediate artifacts.",
        "Enforce the peeking ban until compare. A builder that reads the other lane is out of occupancy.",
        "Each attempt must produce a running spike. A design that does not run is not a dual-lane result.",
        "Compare is a later consensus step. Do not silently merge by a third model.",
        "The live tree has one writer (COSMOS-P05). Builders propose. They do not hold the pen.",
        "In a preferred embodiment Lane A is a Grok-class builder and Lane B is a Cursor-class builder on a branched tree. Gitur (GitHub, GitLab, Cursor) is the BUILD surface. The orchestrator does not author the live-tree implementation in-band.",
        "This is two builders, not builder-plus-checker. A linter or critic seat is COSMOS-P01 CRITICS, not a second builder.",
    ),
    best_mode=_p(
        "Gitur dual-lane as operated 2026-09-04 and following: Lane A Grok 4.6 work-order session; Lane B Cursor Cloud Agent; same DEFINE text; no shared context; CCr disposes after review. Encoded docs/ADVERSARIAL_LOOP.md."
    ),
    embodiments=_p(
        "Forge seats forge.ccr plus forge.adv_N are a product seating of the same occupancy. The chief-coder seat is locked to a named model in a preferred embodiment."
    ),
    public=_p(
        "Dual-lane is described in public cosmos MOTIF (repository created 2026-08-23). Gitur dual-lane (Grok plus Cursor) is operational occupancy, not a secret."
    ),
    prior_art=_p(
        "Related: Galapagos N-version LLM arXiv:2408.09536; N-Version Programming with Coding Agents arXiv:2606.20158; Croto arXiv:2406.08979; IBM US20260252812A1; Avizienis 1985; Knight and Leveson 1986. Anti-shape: Twilio US20250165890A1 and AgentCoder (builder-checker); OpenAI U.S. 12,405,822 B1 (shared workspace); Aider Architect/Editor (executor sees the plan).",
        "This search did not find a granted United States patent that forbids two coding agents from reading each other's context as the inventive occupancy. Unpublished applications are unknown."
    ),
    not_this=_p(
        "Not two agents coding in parallel in a shared chat. Not N-version at runtime with a voter. Not shared-ledger multi-agent. Not builder-plus-linter."
    ),
    statement=_p(
        "Isolating two full builders (each must run) with a peeking ban until compare, plus a single disposer on the live tree."
    ),
    appendix=APPENDIX,
)

# ---------------------------------------------------------------------------
add(
    id="P03",
    docket="COSMOS-P03",
    file="P03_POROSITY.md",
    title="Method of family-axis occupancy using quantified porosity, pairwise orthogonal porosity vectors, and a tensor grid for seating generative models",
    short="Family-axis occupancy; orthogonal Porosity tensor",
    kind="Method / occupancy rule",
    status="FILE",
    fee="$65 micro-entity provisional",
    fig=(
        "FIG. 1 is a schematic of two hole-sets (porosities). Same-family copies leave holes aligned. "
        "A different-mistake overlay covers residual surface faster than stacking copies. "
        "Reason 1990 swiss-cheese is an analogy, not a claimed accident-causation theory. "
        "FIG. 2 is a pair-vector diagram: porosity of model i versus model j is a vector on named axes of interest, not a scalar. "
        "The magnitude of that pair vector equals disagreement frequency times error magnitude. "
        "The more the two models disagree, the more orthogonal the pair vector (aligned holes sit near-parallel). "
        "FIG. 3 is a tensor grid T[i, j, a] stored in a measurement database and used to seat models so as to maximize error discovery per token."
    ),
    field=_p(
        "The present disclosure relates to seating generative models for a task by family and by quantified mistake surface (porosity), including pairwise orthogonal porosity vectors on named axes and a tensor grid of those vectors, so that different-mistake models overlay residual holes faster than copies of the same family, at improved token efficiency."
    ),
    background=_p(
        "N copies of one API bill N times and keep the same holes. Self-consistency and more-agents-is-all-you-need stack copies. Hidden Clones (2026) and LLMs-as-Jury (2026) already measure family-correlated errors. Knight and Leveson 1986: independently written versions do not fail independently.",
        "A single scalar quality score per model cannot tell an occupancy engine which other model punches a different hole. Two high-scoring copies of one family look interchangeable and still leave the same residual surface. Embedding cosine and representation orthogonality measure geometry of weights or activations, not observed task disagreement on the axes the operator cares about.",
        "The inventor names the quality of a coder as porosity (spoken Pourosity): the hole-set or mistake surface of that model (error classes, unseen tools, fabrication modes). Low-quality models with different mistakes, when overlaid, cover surface quickly at a greater-than-linear rate versus stacking copies. Copies of the same family leave holes aligned. This disclosure does not invent an exponent. Convert with a measurement. The measurement is a vector against another model, stored as a tensor, not a single value."
    ),
    summary=_p(
        "Assign each model a family (training house, tool surface, observed failure mode). Quantify each coder's porosity as a hole-set measure and, pairwise, as a vector on named axes of interest, orthogonal to the other seated models. Pair magnitude equals disagreement frequency times error magnitude against the other model. More disagreement makes that pair vector more orthogonal. Persist observations in a measurement database and fold them into a tensor grid T[model i, model j, axis]. When seating votes, the same family does not count twice. Overlay: residual holes of the ensemble approximate the intersection of porosities when mistakes differ, and approximate the first porosity when they align. Prefer adding a different-porosity model, including a low-quality one, over adding a high-quality copy of the same family. Use the tensor to maximize model choices for token efficiency and error discovery. Every adversarial trial in the occupancy engine (Forge and every profile) writes the tensor."
    ),
    definitions=[
        ("Family", "An occupancy class: training house plus tool surface plus observed failure mode. Not a clustering theorem."),
        ("Porosity", "A hole-set measure of a coder (error classes / residual miss surface). Exact metric is an embodiment. Spoken Pourosity."),
        ("Different-mistake overlay", "Seating models whose hole-sets are not aligned, including a low-quality model of another family."),
        ("Orthogonal porosity vector", "The porosity of one model measured against another model on named axes of interest. It is a vector, not a scalar. Orthogonality of the pair rises with observed disagreement."),
        ("Pair magnitude", "The magnitude of an orthogonal porosity vector, equal to disagreement frequency times error magnitude for that pair. Unmeasured until both factors are observed."),
        ("Tensor grid", "The three-index array T[i, j, a] of pair-vector components over models i, j and axes a, stored in a measurement database and used to seat models."),
        ("Axes of interest", "Named task axes on which disagreement and error are scored (for example coding, spec, security; law, facts; bull, bear, risk). A trial scores the axis it is running, not every axis by default."),
    ],
    detailed=_p(
        "Assign each model a family. Occupancy rule, not a clustering theorem.",
        "Quantify each coder's porosity p(m) as a hole-set measure. Embodiments include pass/fail per task class and co-failure beta. Do not put a fake number in this specification.",
        "Further quantify porosity as a pairwise vector. For models i and j and axis a, record whether an adversarial trial on a frozen task statement produced disagreeing ballots, and when known record the error magnitude of the residual hole (an embodiment uses a 1 to 10 scale). Pair magnitude on that axis equals disagreement frequency times mean observed error magnitude. Until error magnitude is observed, frequency may be known while magnitude remains unmeasured. Do not invent either factor.",
        "Orthogonality: the more two models disagree on the axes of interest, the more orthogonal the pair vector. Models that keep the same holes (including same-family copies) sit near-parallel. This is an occupancy measurement of observed task disagreement, not a cosine of embedding vectors.",
        "Persist each observation in a measurement database. An embodiment uses an append-only log as authority for the measurement and a rebuildable relational projection (for example SQLite) as cache. The operating-system ledger remains authority for jobs and spend; the porosity store does not replace it. A read that finds no observations reports unmeasured and does not create storage.",
        "Fold observations into a tensor grid T[i, j, a]. Use the grid to seat models: prefer a candidate whose observed pair orthogonality versus already-seated models is large per token consumed. That is token efficiency together with error discovery. Unmeasured candidates sort last. Several inexpensive models chosen for disagreement can beat a single expensive model on price and on residual-hole cover.",
        "When seating votes (architecture, build, critics): the same family does not count twice.",
        "Overlay: residual holes of the ensemble approximate the intersection of porosities when mistakes differ; they approximate the first porosity when they align.",
        "Prefer adding a different-porosity (different-mistake) model, including a low-quality one, over adding a high-quality copy of the same family. Predicted: surface cover grows faster than the same-family baseline (flat, or linear only in invoice).",
        "Build the measurement into every adversarial trial. The coding profile (Forge) writes pair observations when two named models return on the same frozen statement. Every other occupancy profile (legal, medical, diligence, IP, site, physics) and every occupancy-engine trial (COSMOS-P05) uses the same hook. A silent rotating free-model router is refused: a swap that looks like coverage is a hole.",
        "Dual-lane (COSMOS-P02) and different-family critics (COSMOS-P05) exist to punch different holes, and they feed the tensor.",
        "Hypothesis to measure, not a number in this provisional: coverage versus N for different-family overlays versus same-family copies. Same-family incremental coverage approximates zero. Different-mistake overlay: residual approximates the product of unaligned hole probabilities; cover of the remaining surface is large on the first different overlay. The tensor is how that hypothesis is converted with a packet rather than a fake exponent.",
        "Swiss-cheese is an image (Reason 1990 as analogy). This disclosure does not claim Reason's accident-causation theory as the invention.",
    ),
    best_mode=_p(
        "Encoded docs/MOTIF.md and docs/arch/ORTHOGONAL_POROSITY.md: family-axis occupancy; pairwise orthogonal porosity vectors; JSONL observation log plus SQLite projection under the COSMOS runtime root; Forge facilitate and a shared trial hook; named pins rather than a rotating free-model router (silent swap is a hole that looks like coverage); dual-lane plus different-family critics."
    ),
    embodiments=_p(
        "A coding critic seat uses a Google-family model and an OpenRouter value coder of another family, not two copies of one API. Their pair vector on the coding axis is written when their ballots differ. A later seating pass prefers a third inexpensive model whose tensor slice versus both is large per token.",
        "Forge background free-coders on RESEARCH, ARCH, and CONSENSUS write the tensor from named :free pins. Crucible, Diligence, Differentiator, Docket, and Website GC trials call the same hook. Remote occupancy over a terminal or a phone (COSMOS-P05, COSMOS-P13) writes the same store.",
        "A per-model scalar (errors per 100 lines times severity) may coexist as a fold. It does not replace the pair tensor.",
    ),
    public=_p(
        "Swiss-cheese occupancy language is in MOTIF.md on public cosmos (method text 2026-08-25; swiss cheese 2026-09-07 still in-tree). Family-axis papers of 2026 are their measurements, not this inventor's. Pair-vector / tensor-grid language is inventor-named 2026-09-07 in the COSMOS tree before filing."
    ),
    prior_art=_p(
        "Must name: Reason 1990 / BMJ 2000 (metaphor); Knight and Leveson 1986 and Brilliant, Knight and Leveson 1990 (N-version correlated failures); Kuncheva and Whitaker 2003 (ensemble diversity: Q-statistic, disagreement, double-fault); Jiang et al. ICLR 2022 (disagreement as a signal); Hidden Clones arXiv:2603.17111; CAPA / Great Models Think Alike arXiv:2502.04313; Nine Judges arXiv:2605.29800; LLMs-as-Jury arXiv:2607.10139; N-Version Programming with Coding Agents arXiv:2606.20158; co-failure ceiling arXiv:2606.27288; Wisdom and Delusion of LLM Ensembles arXiv:2510.21513; More Agents Is All You Need arXiv:2402.05120 (anti-shape: same-model copies); Self-consistency arXiv:2203.11171; Mixture-of-Agents arXiv:2406.04692; Self-MoA arXiv:2502.00674 (mixing can hurt); Estornell and Liu NeurIPS 2024; DZone/Cognaptus swiss-cheese AI as safety-stack metaphor; cosine similarity of embeddings or error-profile vectors as a contrast (this disclosure measures observed task disagreement on named axes, not embedding angle).",
        "Patents on this point are thin. No United States patent found that claims same family is one vote, porosity overlay, pairwise orthogonal porosity vectors, or a disagreement-frequency times error-magnitude tensor grid for seating generative models. Unpublished applications are unknown. Official Patent Public Search completeness is unknown without a DOM rail."
    ),
    not_this=_p(
        "Not Reason's aviation model. Not ensembles exist. Not a measured superlinear exponent. Not a clustering theorem. Not cosine of embedding vectors as the invention. Not a fabricated score."
    ),
    statement=_p(
        "Quantified porosity of each coder as a hole-set and as a pairwise orthogonal vector on named axes (magnitude = disagreement frequency times error magnitude), persisted as a tensor grid in a measurement database, with seating and overlay rules so that different-mistake (including low-quality) models cover residual surface faster than same-family copies, including token-efficient seating and a write from every adversarial trial."
    ),
    appendix=APPENDIX,
)

