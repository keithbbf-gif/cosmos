# COSMOS-P03 — Family-axis occupancy; orthogonal Porosity tensor

**Title:** Method of family-axis occupancy using quantified porosity, pairwise orthogonal porosity vectors, and a tensor grid for seating generative models
**Kind:** Method / occupancy rule
**Status:** FILE
**Fee:** $65 micro-entity provisional
**Date:** 2026-09-07
**Legend:** ATTORNEY WORK PRODUCT — NOT A FILED PATENT APPLICATION — FOR COUNSEL ONLY
**Inventor:** Name of inventor: ________________________________ (counsel to complete). The source tree discloses the operator as Keith. This preparer does not sign as inventor.

Standalone written description for a US provisional. Not a filed application. Not claims. Not a novelty opinion. Counsel files. Duplicate HOW_IT_WORKS.pdf at filing.

## Cross-reference

Sisters COSMOS-P01 through COSMOS-P13. No claim of benefit of a sister. 37 CFR 1.53(c): no technical add-after.

## Field of the invention

[0001] The present disclosure relates to seating generative models for a task by family and by quantified mistake surface (porosity), including pairwise orthogonal porosity vectors on named axes and a tensor grid of those vectors, so that different-mistake models overlay residual holes faster than copies of the same family, at improved token efficiency.

## Background of the invention

[0002] N copies of one API bill N times and keep the same holes. Self-consistency and more-agents-is-all-you-need stack copies. Hidden Clones (2026) and LLMs-as-Jury (2026) already measure family-correlated errors. Knight and Leveson 1986: independently written versions do not fail independently.

[0003] A single scalar quality score per model cannot tell an occupancy engine which other model punches a different hole. Two high-scoring copies of one family look interchangeable and still leave the same residual surface. Embedding cosine and representation orthogonality measure geometry of weights or activations, not observed task disagreement on the axes the operator cares about.

[0004] The inventor names the quality of a coder as porosity (spoken Pourosity): the hole-set or mistake surface of that model (error classes, unseen tools, fabrication modes). Low-quality models with different mistakes, when overlaid, cover surface quickly at a greater-than-linear rate versus stacking copies. Copies of the same family leave holes aligned. This disclosure does not invent an exponent. Convert with a measurement. The measurement is a vector against another model, stored as a tensor, not a single value.

## Brief summary of the invention

[0005] Assign each model a family (training house, tool surface, observed failure mode). Quantify each coder's porosity as a hole-set measure and, pairwise, as a vector on named axes of interest, orthogonal to the other seated models. Pair magnitude equals disagreement frequency times error magnitude against the other model. More disagreement makes that pair vector more orthogonal. Persist observations in a measurement database and fold them into a tensor grid T[model i, model j, axis]. When seating votes, the same family does not count twice. Overlay: residual holes of the ensemble approximate the intersection of porosities when mistakes differ, and approximate the first porosity when they align. Prefer adding a different-porosity model, including a low-quality one, over adding a high-quality copy of the same family. Use the tensor to maximize model choices for token efficiency and error discovery. Every adversarial trial in the occupancy engine (Forge and every profile) writes the tensor.

## Definitions

[0006] As used herein, "Family" means An occupancy class: training house plus tool surface plus observed failure mode. Not a clustering theorem.

[0007] As used herein, "Porosity" means A hole-set measure of a coder (error classes / residual miss surface). Exact metric is an embodiment. Spoken Pourosity.

[0008] As used herein, "Different-mistake overlay" means Seating models whose hole-sets are not aligned, including a low-quality model of another family.

[0009] As used herein, "Orthogonal porosity vector" means The porosity of one model measured against another model on named axes of interest. It is a vector, not a scalar. Orthogonality of the pair rises with observed disagreement.

[0010] As used herein, "Pair magnitude" means The magnitude of an orthogonal porosity vector, equal to disagreement frequency times error magnitude for that pair. Unmeasured until both factors are observed.

[0011] As used herein, "Tensor grid" means The three-index array T[i, j, a] of pair-vector components over models i, j and axes a, stored in a measurement database and used to seat models.

[0012] As used herein, "Axes of interest" means Named task axes on which disagreement and error are scored (for example coding, spec, security; law, facts; bull, bear, risk). A trial scores the axis it is running, not every axis by default.

## Brief description of the drawings

[0013] FIG. 1 is a schematic of two hole-sets (porosities). Same-family copies leave holes aligned. A different-mistake overlay covers residual surface faster than stacking copies. Reason 1990 swiss-cheese is an analogy, not a claimed accident-causation theory. FIG. 2 is a pair-vector diagram: porosity of model i versus model j is a vector on named axes of interest, not a scalar. The magnitude of that pair vector equals disagreement frequency times error magnitude. The more the two models disagree, the more orthogonal the pair vector (aligned holes sit near-parallel). FIG. 3 is a tensor grid T[i, j, a] stored in a measurement database and used to seat models so as to maximize error discovery per token.

[0014] The drawings are described in prose so that a person of ordinary skill can produce sheet drawings. Sheet drawings may be added by counsel before filing. Do not add new matter after a filing date.

## Detailed description

[0015] Assign each model a family. Occupancy rule, not a clustering theorem.

[0016] Quantify each coder's porosity p(m) as a hole-set measure. Embodiments include pass/fail per task class and co-failure beta. Do not put a fake number in this specification.

[0017] Further quantify porosity as a pairwise vector. For models i and j and axis a, record whether an adversarial trial on a frozen task statement produced disagreeing ballots, and when known record the error magnitude of the residual hole (an embodiment uses a 1 to 10 scale). Pair magnitude on that axis equals disagreement frequency times mean observed error magnitude. Until error magnitude is observed, frequency may be known while magnitude remains unmeasured. Do not invent either factor.

[0018] Orthogonality: the more two models disagree on the axes of interest, the more orthogonal the pair vector. Models that keep the same holes (including same-family copies) sit near-parallel. This is an occupancy measurement of observed task disagreement, not a cosine of embedding vectors.

[0019] Persist each observation in a measurement database. An embodiment uses an append-only log as authority for the measurement and a rebuildable relational projection (for example SQLite) as cache. The operating-system ledger remains authority for jobs and spend; the porosity store does not replace it. A read that finds no observations reports unmeasured and does not create storage.

[0020] Fold observations into a tensor grid T[i, j, a]. Use the grid to seat models: prefer a candidate whose observed pair orthogonality versus already-seated models is large per token consumed. That is token efficiency together with error discovery. Unmeasured candidates sort last. Several inexpensive models chosen for disagreement can beat a single expensive model on price and on residual-hole cover.

[0021] When seating votes (architecture, build, critics): the same family does not count twice.

[0022] Overlay: residual holes of the ensemble approximate the intersection of porosities when mistakes differ; they approximate the first porosity when they align.

[0023] Prefer adding a different-porosity (different-mistake) model, including a low-quality one, over adding a high-quality copy of the same family. Predicted: surface cover grows faster than the same-family baseline (flat, or linear only in invoice).

[0024] Build the measurement into every adversarial trial. The coding profile (Forge) writes pair observations when two named models return on the same frozen statement. Every other occupancy profile (legal, medical, diligence, IP, site, physics) and every occupancy-engine trial (COSMOS-P05) uses the same hook. A silent rotating free-model router is refused: a swap that looks like coverage is a hole.

[0025] Dual-lane (COSMOS-P02) and different-family critics (COSMOS-P05) exist to punch different holes, and they feed the tensor.

[0026] Hypothesis to measure, not a number in this provisional: coverage versus N for different-family overlays versus same-family copies. Same-family incremental coverage approximates zero. Different-mistake overlay: residual approximates the product of unaligned hole probabilities; cover of the remaining surface is large on the first different overlay. The tensor is how that hypothesis is converted with a packet rather than a fake exponent.

[0027] Swiss-cheese is an image (Reason 1990 as analogy). This disclosure does not claim Reason's accident-causation theory as the invention.

## Best mode

[0028] Encoded docs/MOTIF.md and docs/arch/ORTHOGONAL_POROSITY.md: family-axis occupancy; pairwise orthogonal porosity vectors; JSONL observation log plus SQLite projection under the COSMOS runtime root; Forge facilitate and a shared trial hook; named pins rather than a rotating free-model router (silent swap is a hole that looks like coverage); dual-lane plus different-family critics.

## Further embodiments

[0029] A coding critic seat uses a Google-family model and an OpenRouter value coder of another family, not two copies of one API. Their pair vector on the coding axis is written when their ballots differ. A later seating pass prefers a third inexpensive model whose tensor slice versus both is large per token.

[0030] Forge background free-coders on RESEARCH, ARCH, and CONSENSUS write the tensor from named :free pins. Crucible, Diligence, Differentiator, Docket, and Website GC trials call the same hook. Remote occupancy over a terminal or a phone (COSMOS-P05, COSMOS-P13) writes the same store.

[0031] A per-model scalar (errors per 100 lines times severity) may coexist as a fold. It does not replace the pair tensor.

## Disclosure clock (already public)

[0032] Swiss-cheese occupancy language is in MOTIF.md on public cosmos (method text 2026-08-25; swiss cheese 2026-09-07 still in-tree). Family-axis papers of 2026 are their measurements, not this inventor's. Pair-vector / tensor-grid language is inventor-named 2026-09-07 in the COSMOS tree before filing.

## Information concerning related art (not an IDS; not a novelty opinion)

[0033] Must name: Reason 1990 / BMJ 2000 (metaphor); Knight and Leveson 1986 and Brilliant, Knight and Leveson 1990 (N-version correlated failures); Kuncheva and Whitaker 2003 (ensemble diversity: Q-statistic, disagreement, double-fault); Jiang et al. ICLR 2022 (disagreement as a signal); Hidden Clones arXiv:2603.17111; CAPA / Great Models Think Alike arXiv:2502.04313; Nine Judges arXiv:2605.29800; LLMs-as-Jury arXiv:2607.10139; N-Version Programming with Coding Agents arXiv:2606.20158; co-failure ceiling arXiv:2606.27288; Wisdom and Delusion of LLM Ensembles arXiv:2510.21513; More Agents Is All You Need arXiv:2402.05120 (anti-shape: same-model copies); Self-consistency arXiv:2203.11171; Mixture-of-Agents arXiv:2406.04692; Self-MoA arXiv:2502.00674 (mixing can hurt); Estornell and Liu NeurIPS 2024; DZone/Cognaptus swiss-cheese AI as safety-stack metaphor; cosine similarity of embeddings or error-profile vectors as a contrast (this disclosure measures observed task disagreement on named axes, not embedding angle).

[0034] Patents on this point are thin. No United States patent found that claims same family is one vote, porosity overlay, pairwise orthogonal porosity vectors, or a disagreement-frequency times error-magnitude tensor grid for seating generative models. Unpublished applications are unknown. Official Patent Public Search completeness is unknown without a DOM rail.

## What this disclosure is not

[0035] Not Reason's aviation model. Not ensembles exist. Not a measured superlinear exponent. Not a clustering theorem. Not cosine of embedding vectors as the invention. Not a fabricated score.

## Statement of invention (not claims)

[0036] Quantified porosity of each coder as a hole-set and as a pairwise orthogonal vector on named axes (magnitude = disagreement frequency times error magnitude), persisted as a tensor grid in a measurement database, with seating and overlay rules so that different-mistake (including low-quality) models cover residual surface faster than same-family copies, including token-efficient seating and a write from every adversarial trial.

[0037] Counsel may draft claims. The foregoing is a statement of invention, not a claim set under 35 U.S.C. 112(b).

## Appendix to attach at filing

[0038] HOW_IT_WORKS.pdf (APP_OS: SCAR, ROLD, carry-over; APP_COSMOS; APP_CRUCIBLE; APP_BTS_MESH). Duplicate the appendix into this provisional at filing. A provisional cannot claim benefit of a sister.
