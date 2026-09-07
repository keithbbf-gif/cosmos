# -*- coding: utf-8 -*-
"""P04-P13 bodies. Imported after _spec_bodies so add() appends."""
from __future__ import annotations

from _spec_bodies import APPENDIX, add, _p

add(
    id="P04",
    docket="COSMOS-P04",
    file="P04_RUNTIME_BIND.md",
    title="Method of binding completion to a live-system-emitted value with fail-closed refusal",
    short="Runtime-binding gate versus green-log",
    kind="Method / selection gate",
    status="FILE",
    fee="$65 micro-entity provisional",
    fig="FIG. 1 shows a claim of done entering a gate. A live emit from the running system passes. An exit code, a critic LGTM, and a dashboard color fail-closed as projections.",
    field=_p(
        "The present disclosure relates to accepting a change to a running computer system only when the running system itself emits a value that only it can produce, and to refusing when that value is missing or contradicts the claim."
    ),
    background=_p(
        "A pipeline reports success because tests exited zero or a critic said it looks good. That is fabricated compliance: a plausible lie that closes the ticket while the running system does not do the thing. The inventor names this the placation class.",
        "Continuous integration as a quality gate is related and, if treated as done, is the opposite occupancy."
    ),
    summary=_p(
        "For a change to be accepted, require an artifact that only the running system can produce (a live API value, a ledger event field, a hash only the true run emits). Treat CI green, critic LGTM, and UI checks as projections, never authority. If the live emit is missing or contradicts the claim, record a refusal (fail-closed). Do not repair a green log in place. The report of the change must carry the live artifact or the refusal."
    ),
    definitions=[
        ("Live emit", "A value only the running system can produce."),
        ("Projection", "A rebuildable view (dashboard, SQLite cache, CI log) that is never authority."),
        ("Fail-closed", "Missing or contradicting evidence is a refusal, not a silent pass."),
        ("Placation", "A plausible claim of compliance that the artifact contradicts."),
    ],
    detailed=_p(
        "For a change to be accepted, require an artifact that only the running system can produce.",
        "Examples of a live emit: an HTTP body from the resident Core bearing tree_id and a field only the true run can emit; a ledger event with a hash chain head; a response.model field that binds the model that actually answered.",
        "Treat CI green, critic LGTM, and UI checks as projections, never authority.",
        "If the live emit is missing or contradicts the claim, record a refusal. Do not repair a green log in place.",
        "The report of the change must quote the live artifact or the refusal. Intention is not evidence.",
        "A negative control may remain red on purpose. Painting it green is placation.",
        "SCAR-derived law: every consequential action emits a machine-checkable artifact. Encoded docs/SCAR_PLACATION.md (2026-08-25) and kernel AD-11.",
    ),
    best_mode=_p(
        "COSMOS MOTIF gate against live Core at http://127.0.0.1:8770, tree_id=KMesh-COSMOS-live. Example: GET /jukebox returns 200 with QUEUED/RUNNING/BROKE/CLEAN counts; that body is the emit, not a test exit code."
    ),
    embodiments=_p(
        "A model rail binds response.model, not the request. allow_fallbacks=false. A silent swap is a failed bind."
    ),
    public=_p(
        "Runtime-binding language is in public MOTIF and architecture (cosmos created 2026-08-23)."
    ),
    prior_art=_p(
        "Related: Proof-or-Stop arXiv:2607.14890; Microsoft Azure 2026-08-29 validate at runtime; The New Stack runtime verification; CI as quality gate (Jenkins, GitHub Actions) as the opposite occupancy if CI is treated as done. No United States patent found that claims only a live-system-emitted value is done. Patent occupancy thin. Paper and engineering occupancy high in 2026."
    ),
    not_this=_p(
        "Not don't-trust-CI as a slogan. Not a test framework. Not a bake-off."
    ),
    statement=_p(
        "Binding finished to a value only the live tree can emit, with fail-closed refusal when that value is absent."
    ),
    appendix=APPENDIX,
)

add(
    id="P05",
    docket="COSMOS-P05",
    file="P05_ADVERSARIAL_ENGINE.md",
    title="Adversarial occupancy engine with isolated proposers, different-family critics, one disposer, and domain skins",
    short="Adversarial occupancy engine (parent)",
    kind="System / occupancy",
    status="FILE (parent of products)",
    fee="$65 micro-entity provisional",
    fig="FIG. 1 shows seats: N isolated proposers, different-family critics, and one disposer writing the live tree. FIG. 2 shows the same engine with interchangeable packets (code, casefile, deal room, IP docket) as skins.",
    field=_p(
        "The present disclosure relates to an occupancy engine for generative-model work: isolated proposers, different-family critics versus what was decided, and one disposer, reused across domains by changing the packet rather than cloning the stack."
    ),
    background=_p(
        "If the orchestrator also holds the only wrench, the system ships a plausible lie. Shared-transcript crews put many agents in one context. Microsoft US20250371498A1 teaches the second agent based on the first — anti-isolation.",
        "The inventor's new way is reliable, scalable AI: independent first, then argue; no shared context between builders; different-family critics; one pen. Products are skins, not new inventions."
    ),
    summary=_p(
        "Name seats: disposer (one writer), N proposers, critics. Proposers run isolated; no shared transcript mid-pass. Critics are a different family from the builders; they judge the decision, not house style. Only the disposer writes the live tree or the grant tree. The same occupancy is reused across domains by changing the packet (code, casefile, deal room, IP docket), not by cloning the stack."
    ),
    definitions=[
        ("Occupancy", "The seating of named models into named seats with isolation and one disposer."),
        ("Skin", "A product that reuses the engine by changing the packet and role names, not the occupancy."),
        ("Packet", "The work object: code change, legal casefile, diligence data room, IP docket, medical casefile."),
    ],
    detailed=_p(
        "Name seats: disposer (one writer), N proposers, critics.",
        "Proposers run isolated. No shared transcript mid-pass (COSMOS-P02).",
        "Critics are a different family from the builders (COSMOS-P03). They judge the decision (COSMOS-P01 DEFINE), not house style.",
        "Only the disposer writes the live tree or the grant tree. Everyone else proposes.",
        "Reuse the occupancy across domains by changing the packet, not by cloning the stack.",
        "MOTIF (COSMOS-P01) is the loop that runs this engine. Dual-lane (COSMOS-P02) is one seating.",
        "Preferred skins: Forge (coding), Crucible (legal packet as occupancy not as a role-triad invention), Diligence (bull/bear/risk), Differentiator (anonymized medical casefile), Docket (IP). UPS is a physics skin that needs the inventor's July pack and is not invented here.",
        "Fail-closed runtime-binding (COSMOS-P04) is the gate. The ledger (COSMOS-P07) is authority. Dashboards are projections.",
    ),
    best_mode=_p(
        "COSMOS Core as the OS; cDeck as a skin; products listed in docs/PROFILES.md; one CCr lease; orchestrator without the COSMOS pen. Encoded docs/CCR.md, docs/ADVERSARIAL_LOOP.md."
    ),
    embodiments=_p(
        "Parallel native windows bound to {profile, core_base, tree_id} are two clients of one Core, not two Cores. A peer Core stays unnamed until the operator names a host."
    ),
    public=_p(
        "CRUCIBLE is named in bts-mesh GitHub description 2026-08-16T10:21:14Z (word not in tracked files of that repo). Adversarial loop in public cosmos MOTIF, repository created 2026-08-23."
    ),
    prior_art=_p(
        "Du 2023 debate; Irving 2018; Liang MAD; MoA; More Agents; Estornell and Liu; WO2025183627A1 (Lemon Inc MAD); US20240104125A1; US20250371498A1 (Microsoft, anti-isolation); AutoGen/ChatDev/MetaGPT/CAMEL/Magentic-One; Avizienis 1985; Knight and Leveson 1986; GitHub CODEOWNERS (VCS analog of one merger).",
        "Combination of isolation plus family critics versus decided plus one disposer plus skins: unknown as blocking. Pieces crowded. This is not a novelty opinion."
    ),
    not_this=_p(
        "Not we invented multi-agent. Not Magentic-One (orchestrator holds the wrench). Not a voter over N-version binaries. Not a plaintiff-defense-judge patent (see COSMOS-P12 HOLD)."
    ),
    statement=_p(
        "One occupancy engine (isolate, different-family critique, one pen) reused as skins across coding, legal, medical, diligence, and IP packets."
    ),
    appendix=APPENDIX,
)

add(
    id="P06",
    docket="COSMOS-P06",
    file="P06_LOCAL_FREE_WEIGHTS.md",
    title="Method of deploying isolated local free-weight models at fixed cost versus a metered S-tier pass",
    short="Local free-weight plurality versus S-tier",
    kind="Method / system of deployment",
    status="FILE",
    fee="$65 micro-entity provisional",
    fig="FIG. 1 shows two or three isolated local free-weight models on one machine (cost = hardware plus power) compared with one S-tier API (cost = tokens). A dashed cloud rail labeled OpenRouter :free is marked as a different rail, not this invention.",
    field=_p(
        "The present disclosure relates to deploying two or three free-weight models of different families, isolated, on the same local machine, at low fixed cost, and comparing that occupancy to a single metered S-tier API pass."
    ),
    background=_p(
        "S-tier is a variable invoice (quota, key, billing). One brain, same porosity. Metered free APIs still run out. Local free weights plus isolation plus family-axis is how cost becomes a cap you can name.",
        "Mixture-of-Agents, FrugalGPT, and blending papers block slogans. Microsoft U.S. 12,524,210 B2 (local GPT versus remote LLM for coding COGS, one local plus one remote) and Google US20240311405A1 (pick one of N models) must be read by counsel. Isolation (no shared context) is the thin element."
    ),
    summary=_p(
        "Select N=2 or 3 models whose weights are free or open and whose families differ (COSMOS-P03). Deploy them on-box. Cost is machine plus power. Run them isolated (COSMOS-P02). Dispose through one writer (COSMOS-P05). Gate on a live emit (COSMOS-P04). Compare dollars and task outcome to a single S-tier API pass on the same task. Measurement is for conversion, not a number in this provisional."
    ),
    definitions=[
        ("Free-weight", "Model weights that may be run locally without a per-token invoice from the weight provider."),
        ("S-tier", "A metered frontier API."),
        ("On-box", "On the operator's machine (llama.cpp / Ollama / vLLM class), not a hosted free API."),
    ],
    detailed=_p(
        "Select N=2 or 3 models whose weights are free or open and whose families differ.",
        "Deploy them on-box. Cost equals machine plus power, not per-token.",
        "Run them isolated: no shared context mid-pass.",
        "Dispose through one writer. Gate on a live emit.",
        "Compare dollars and task outcome to a single S-tier API pass on the same task. Do not invent a bake-off number in this specification.",
        "OpenRouter free APIs are a different rail. The rotator is refused (silent model swap). A phone ChatBot named :free picker is that cloud Freemium free rail (COSMOS-P13 embodiment), not this packet. This packet is on-box weights — later actual unlimited on the user's hardware, and a Premium path of the ChatBot Freemium model.",
        "Self-MoA teaches that mixing can hurt. This disclosure does not claim that mixing always helps.",
    ),
    best_mode=_p(
        "Two or three isolated local free-weight processes on one workstation, family-diverse, disposed by CCr, gated on a live emit, compared to one S-tier pass. Not yet a controlled bake-off."
    ),
    embodiments=_p(
        "Gemma-class plus a different-family local coder plus an optional third family, each in its own process, no shared chat buffer."
    ),
    public=_p(
        "Swiss-cheese price/performance hypothesis in MOTIF.md and an unposted publish pack. Local multiplex as the inventor's 2026-09-07 measurement plan — not a public bake-off."
    ),
    prior_art=_p(
        "Must cite: Mixture-of-Agents arXiv:2406.04692; Blending Is All You Need arXiv:2401.02994; FrugalGPT arXiv:2305.05176; RouteLLM arXiv:2406.18665; Hybrid LLM arXiv:2404.14618; More Agents arXiv:2402.05120; Self-MoA arXiv:2502.00674; LLM-Blender; PrivateGPT / GPT4All / LocalAI / OnPrem.LLM; llama.cpp; Ollama; vLLM; Intelligence per Watt arXiv:2511.07885.",
        "Patents counsel must read: US12524210B2 / WO2024238128A1 Microsoft; US20240311405A1 Google; Citibank US12536406B2; Martian US12314825B2; on-device multi-LM speculative decoding US12505335B2 (shares the decode stream — anti-isolation).",
        "This search found no paper or patent that measures two or three isolated local free-weights versus one S-tier API on a coding task with box dollars versus token dollars. Unknown as blocking. Not a legal conclusion."
    ),
    not_this=_p(
        "Not run Ollama twice. Not FrugalGPT (paid API cascade). Not Together MoA (shared layers, hosted). Not a fake bake-off number. Not OpenRouter :free as unlimited."
    ),
    statement=_p(
        "Family-diverse free-weight models, isolated, on one local machine at fixed cost, selected and gated as occupancy — versus one metered S-tier pass."
    ),
    appendix=APPENDIX,
)
