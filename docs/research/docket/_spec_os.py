# -*- coding: utf-8 -*-
"""P07-P13 bodies."""
from __future__ import annotations

from _spec_bodies import APPENDIX, add, _p

add(
    id="P07",
    docket="COSMOS-P07",
    file="P07_CORE_LEDGER_FENCE.md",
    title="Single-writer AI-work operating system with signed hash-chained ledger, fencing tokens, and projections that are never authority",
    short="COSMOS Core: sole ledger, fence, tokens",
    kind="System",
    status="FILE",
    fee="$65 micro-entity provisional",
    fig="FIG. 1 shows one resident service writing a hash-chained signed JSONL ledger. Workers present a fencing token at a fenced commit gateway. Dashboards and SQLite are projections. A corrupt segment refuses.",
    field=_p(
        "The present disclosure relates to an operating system for AI work whose authority is a single-writer append-only hash-chained service-signed ledger, with leases and fencing tokens, and with dashboards as rebuildable projections that are never authority."
    ),
    background=_p(
        "Two writers, empty-dir identity, advisory locks, and repair the log are measured failures. Green dashboards as authority are placation. Event sourcing, git, Kafka, and blockchains are related and are not this occupancy as an AI-work OS."
    ),
    summary=_p(
        "One resident process is API, scheduler, arbiter, and ledger writer. The ledger is framed JSONL, hash-chained, service-signed. Replay rebuilds projections. Projections may not be written as authority. Workers receive a fencing token; the commit gateway rejects stale tokens and hash mismatches. A corrupt segment refuses; it is not repaired in place."
    ),
    definitions=[
        ("Ledger", "Append-only, hash-chained, service-signed JSONL. Authority."),
        ("Projection", "A rebuildable view. Never authority."),
        ("Fencing token", "A monotonic token proving the holder still owns the lease."),
        ("Fenced commit gateway", "The only path by which a worker publishes; demands token plus expected input hashes."),
    ],
    detailed=_p(
        "One process is API plus scheduler plus arbiter plus ledger writer. Fail-closed. Never a second unsynchronized writer.",
        "Ledger: framed JSONL, hash chain, service signature. Replay rebuilds projections. Corrupt segment implies REFUSE plus incident, never repair-in-place.",
        "Queue is immutable manifests plus ledger lifecycle events. SQLite is service-private projection only.",
        "Workers run in attempt-private workspaces (native, DOM, cloud) and publish only through the fenced commit gateway presenting fencing token and expected input hashes.",
        "Large artifacts live in a content-addressed store (filename equals hash; the ledger holds the live pointer).",
        "The service is a modular monolith, split-ready: module interfaces are RPC-shaped so any module can later become a process without breaking the one versioned external API.",
        "Scar-derived primitives are kernel interfaces. Workers cannot import around them (AD-11).",
        "This OS is not MOTIF. MOTIF (COSMOS-P01) is how the OS builds the next organ. The house is the ledger, the fence, the resolver (COSMOS-P10), the seed (COSMOS-P11), the spend gate (COSMOS-P09), and the DOM rail (COSMOS-P08).",
    ),
    best_mode=_p(
        "COSMOS Core as ratified 2026-08-23, docs/FINAL_ARCHITECTURE.md, live tree_id=KMesh-COSMOS-live, serve on port 8770. Encoded cosmos/cosmos_service.py and related modules."
    ),
    embodiments=_p(
        "Windows service recovery. Backup policy in Core; execution as scheduled jobs; rehearse-restore is first-class. Compatibility lane: legacy mutable-file tools serialized until they earn parallelism."
    ),
    public=_p(
        "Architecture text on cosmos created 2026-08-23T06:42:12Z. Predecessor mesh named on bts-mesh created 2026-08-16T10:21:14Z."
    ),
    prior_art=_p(
        "Event sourcing (Fowler 2005); CQRS; git; Bitcoin; Kafka; US11943344B2 Ridgeline (hash-chained signed events plus projections, closest patent); WO2018217375A1 Microsoft signed log-chain; RFC 6962 Certificate Transparency; Kleppmann fencing tokens 2016; Chubby 2006; Raft 2014; etcd/k8s leases; SCSI-3 PR / STONITH; Temporal; Airflow; n8n; LangGraph.",
        "Combination of all five as an AI-work OS: unknown as blocking. Not a novelty opinion."
    ),
    not_this=_p(
        "Not blockchain. Not git-as-authority. Not Temporal. Not event sourcing exists as a slogan."
    ),
    statement=_p(
        "An AI-work OS whose authority is a single-writer signed hash-chained JSONL plus fencing-token commit of worker artifacts, with projections never authority."
    ),
    appendix=APPENDIX,
)

add(
    id="P08",
    docket="COSMOS-P08",
    file="P08_DOM_FIRST.md",
    title="Scheduler routing that prefers a contained DOM rail because it cannot exhaust credit",
    short="DOM-first unmetered rail",
    kind="Method / routing policy",
    status="FILE",
    fee="$65 micro-entity provisional",
    fig="FIG. 1 shows a scheduler. The preferred rail is a contained DOM worker. Metered APIs are an explicit audited fallback. Typed failures UNREACHABLE, SESSION_EXPIRED, AUTH_REQUIRED, BROKE are shown.",
    field=_p(
        "The present disclosure relates to routing work in an AI operating system by preferring a browser-DOM rail because that rail does not depend on credit, quota, billing, key, or consent that can lapse, with metered APIs as explicit fallback."
    ),
    background=_p(
        "API-only agents die when the key, quota, or vendor dies. DOM is usually a tool, not the preferred unmetered path. Computer-use products are commonly metered."
    ),
    summary=_p(
        "Register DOM workers as a scheduler rail, not a one-off script. Routing policy data: DOM first, API second; fallback is explicit and ledgery. Typed failures; report-never-retry unless contract-idempotent. Prefer this rail for RESEARCH because returns must not depend on prepaid remaining."
    ),
    definitions=[
        ("DOM rail", "A contained browser worker with its own OS identity, ephemeral profile, and Job Object."),
        ("Typed failure", "One of UNREACHABLE, SESSION_EXPIRED, AUTH_REQUIRED, BROKE — not a generic exception."),
    ],
    detailed=_p(
        "Register DOM workers as a scheduler rail, not a one-off script.",
        "Contained workers: own OS identity, ephemeral ACL'd profiles, Job Objects.",
        "Routing policy data: DOM first, API second. Fallback is explicit and audited on the ledger.",
        "Typed failures: UNREACHABLE, SESSION_EXPIRED, AUTH_REQUIRED, BROKE. Report-never-retry unless the contract is idempotent.",
        "Prefer this rail for RESEARCH (COSMOS-P01) because returns must not depend on prepaid remaining.",
        "Dumping the DOM is not the rail. Interaction (evaluate, fill, send) is the rail.",
        "A rotating free-model API is not this rail and is refused as a silent swap (COSMOS-P03 hole).",
    ),
    best_mode=_p(
        "COSMOS AD-6. Playwright-class contained workers. Live 2026-09-06 surfaces included Bing SERP, Cloudflare AI Playground, Copilot CLI. GEM via a named Chrome profile, never a banned URL. Ask the tools index before writing anything. Do not rebuild."
    ),
    embodiments=_p(
        "Research returns written to disk from SGH and GEM in parallel (ROLD Rule 1). API is fallback."
    ),
    public=_p(
        "DOM-first in public architecture 2026-08-23."
    ),
    prior_art=_p(
        "Playwright; Playwright MCP; browser-use; Stagehand; Skyvern; Magentic-One WebSurfer; US12101373B2 (browser RPA); CN119248379B (LLM plus Playwright scheduler); computer-use / Operator-class metered products. Distinctive prefer DOM because it cannot run out of credit as routing policy: unknown as patented. Ops folklore is widespread."
    ),
    not_this=_p(
        "Not browser automation exists. Not WICG scheduler.postTask. Not OpenAI Operator (metered)."
    ),
    statement=_p(
        "Scheduler routing that prefers a contained DOM rail because it cannot exhaust credit, with typed failures and audited API fallback."
    ),
    appendix=APPENDIX,
)

add(
    id="P09",
    docket="COSMOS-P09",
    file="P09_SPEND_GATE.md",
    title="Fail-closed spend cap that cannot silently widen without typed confirm and ledgered refusal",
    short="Spend gate; confirm-to-widen",
    kind="Method / system",
    status="FILE",
    fee="$65 micro-entity provisional",
    fig="FIG. 1 shows a request that would raise a spend cap. Without a confirm token the gate returns a typed 409 WIDEN_REQUIRES_CONFIRM. The stored cap is unchanged. A signed ledger event records the refusal.",
    field=_p(
        "The present disclosure relates to gating spend on AI rails so that a cap cannot silently widen, a refused widen is itself recorded, and over-cap work does not run."
    ),
    background=_p(
        "OpenAI removed hard budget limits (notify-only). Admin APIs that raise max_budget without a two-step confirm. Silent fallback reroute that spends a different rail. Those are the scars."
    ),
    summary=_p(
        "Each rail has a signed cap. A request that would raise the cap without a confirm token is refused (typed 409). The stored cap is unchanged. Widen requires an explicit confirm on the same cap object; ledger the grant or the refusal. Fail-closed: over-cap work does not run."
    ),
    definitions=[
        ("Confirm token", "An explicit operator confirmation bound to the same cap object."),
        ("WIDEN_REQUIRES_CONFIRM", "The typed refusal when a widen is requested without confirm."),
    ],
    detailed=_p(
        "Each rail has a signed cap.",
        "A request that would raise the cap without a confirm token is refused. Preferred embodiment: HTTP 409 WIDEN_REQUIRES_CONFIRM. The stored cap does not move on the 409.",
        "Widen requires an explicit confirm on the same cap object.",
        "Ledger BUDGET_SET or SPEND_CAP_REFUSED. The refusal itself is evidence.",
        "Fail-closed: over-cap work does not run.",
        "Silent fallback to another rail that spends is also a widen and is refused unless confirmed.",
    ),
    best_mode=_p(
        "Measured in the COSMOS tree (docs/CHANGELOG_2026-08-30_CC_AUDIT.md). Signed BUDGET_SET / SPEND_CAP_REFUSED on the ledger."
    ),
    embodiments=_p(
        "A POST to a budget route without confirm never moves the cap. A subsequent GET shows the old cap. That GET body is the live emit (COSMOS-P04)."
    ),
    public=_p(
        "Architecture and changelog in public cosmos tree (2026-08-23 and following)."
    ),
    prior_art=_p(
        "LiteLLM virtual keys / tag budgets (admin can raise); Cloudflare AI Gateway spend limits 2026-06; Anthropic workspace limits; LangSmith evaluator weekly cap; US20250299128A1 multi-cloud budget throttle; EP4381451A1; PCI dual-control; 21 CFR 11.10. OpenAI hard-cap removal is the scar, not a teaching of confirm-to-widen. Combination (AI-rail cap plus no silent widen plus typed confirm plus signed ledger): unknown as blocking."
    ),
    not_this=_p(
        "Not AWS Budgets alerts. Not circuit breaker exists."
    ),
    statement=_p(
        "An AI-rail spend cap that cannot move without a typed confirm, with the refusal itself ledgery."
    ),
    appendix=APPENDIX,
)

add(
    id="P10",
    docket="COSMOS-P10",
    file="P10_RESOLVER.md",
    title="Boot identity of an AI runtime root by sentinel content where existence of a directory is not identity",
    short="Resolver: sentinel root; existence is not identity",
    kind="System (narrow)",
    status="FILE (narrow)",
    fee="$65 micro-entity provisional",
    fig="FIG. 1 shows a boot resolver reading sentinel file content (.cosmos-root.json system and tree_id). An empty directory that exists is marked NOT IDENTITY. Parent-walk and drive-literal fallbacks are marked FORBIDDEN.",
    field=_p(
        "The present disclosure relates to identifying a runtime root of an AI operating system by sentinel file content rather than by path existence, parent-walking, or a fallback ladder of drives."
    ),
    background=_p(
        "Empty-dir scar: a path that exists is treated as the install. Fallback ladders silently pick the wrong tree. Two writers on two roots. That is a deletion class when the wrong tree is overwritten."
    ),
    summary=_p(
        "At boot, resolve one root by reading a sentinel file content, not by path existence. Match declared system and tree_id; refuse READY on mismatch or missing install record. Do not walk parents, do not try a list of drives, do not treat an empty directory as identity."
    ),
    definitions=[
        ("Sentinel", "A file whose content (not its path) identifies the runtime root."),
        ("READY", "The service state that may serve. Forbidden without sentinel match."),
    ],
    detailed=_p(
        "At boot, resolve one root by reading a sentinel file content, not by path existence.",
        "Preferred sentinel: .cosmos-root.json declaring system=COSMOS and a tree_id. Preferred live tree_id: KMesh-COSMOS-live.",
        "Match declared system and tree_id against the install record. Refuse READY on mismatch or missing install record.",
        "Do not walk parents. Do not try a list of drives. Do not treat an empty directory as identity.",
        "No import-time side effects. The resolver is instantiated at boot composition.",
        "Two roots must not be conflated: the repo tree (tracked code) and the runtime root (live/). Existence of a folder is not identity of either.",
        "Every path resolves through a declared role under that root. Nothing assembles a path by hand from a drive letter.",
    ),
    best_mode=_p(
        "cosmos_paths resolver. Service cannot go READY without sentinel-verified root. AD-5. Encoded cosmos/cosmos_paths.py."
    ),
    embodiments=_p(
        "A unit test plants an empty directory at a tempting path and asserts the resolver refuses it."
    ),
    public=_p(
        "Resolver rules in public architecture 2026-08-23."
    ),
    prior_art=_p(
        "OCI digest versus tag; Nix require-sigs / sandbox-fallback (fallback is the anti-pattern); git objects; chroot (path, not content); systemd-nspawn --root-hash; SLSA/in-toto/Cosign; HSTS fail-closed. No close patent found on JSON sentinel plus refuse empty-dir plus no parent-walk as AI-OS boot identity. Unknown as blocking. Narrow."
    ),
    not_this=_p(
        "Not chroot. Not Docker tags. Not a new hash algorithm."
    ),
    statement=_p(
        "Boot identity of an AI runtime root by sentinel content, where existence of a directory is not identity and fallback ladders are forbidden."
    ),
    appendix=APPENDIX,
)

add(
    id="P11",
    docket="COSMOS-P11",
    file="P11_SEED.md",
    title="Signed session close as a fail-closed operating-system incident",
    short="SEED / signed session close (OPEN_CONTEXT)",
    kind="Method / system (narrow)",
    status="FILE (narrow)",
    fee="$65 micro-entity provisional",
    fig="FIG. 1 shows close_session emitting a signed SEED.json (declared length and HMAC). Absence is OPEN_CONTEXT. start_session refuses NO_SEED, BAD_SEED, and IDENTITY_MISMATCH. A HOLD pause never self-clears; a resume-gate pause may auto-resume on a native clock.",
    field=_p(
        "The present disclosure relates to making session identity of an AI operating system depend on a signed close manifest, such that a missing or invalid close is an incident and start refuses."
    ),
    background=_p(
        "Sessions vanish. The next session fabricates continuity. Vendor memory features store facts without a fail-closed close. CONTINUITY arXiv:2609.05269 (2026-09-05) is the closest paper and must be watched by counsel."
    ),
    summary=_p(
        "close_session must emit a signed manifest covering declared fields (inherited facts, active leases, open watchers, handoff recipient). Absence, length mismatch, or HMAC failure is an incident (OPEN_CONTEXT), not a warning. start_session reads the manifest under its declared length and HMAC before injecting carry-over. An optional auto-resession clock consumes the same seed. A HOLD pause never self-clears."
    ),
    definitions=[
        ("SEED", "A signed context manifest written at close (SEED.json plus declared length/HMAC)."),
        ("OPEN_CONTEXT", "The incident raised when close lacks a valid manifest."),
        ("HOLD", "A pause that never self-clears."),
        ("Resume gate", "A pause at boot that may auto-resume on a native clock if the operator does not choose."),
    ],
    detailed=_p(
        "close_session must emit a signed manifest covering declared fields: inherited facts, active leases, open watchers, handoff recipient.",
        "Absence, length mismatch, or HMAC failure is an incident (OPEN_CONTEXT), not a warning.",
        "start_session reads the manifest under its declared length and HMAC before injecting carry-over. It refuses NO_SEED, BAD_SEED, and IDENTITY_MISMATCH.",
        "A lightweight session pointer may sit beside the seed (BUCm.toml in the source tree) as one truth, never a competing second handoff.",
        "Resume gate: after boot loads carry-over, one option (resume all, subset, hold). No affirmative selection implies auto-resume on a native clock. Default is motion.",
        "A HOLD never self-clears. The two pause kinds are not the same.",
        "Carry-over is why the OS survives context death. MOTIF is what the clock drives after the seed is accepted.",
        "This is not ChatGPT memory.",
    ),
    best_mode=_p(
        "cosmos_session.close_session / start_session. AD-10. docs/PAUSE_PROTOCOL.md. Native fifteen-second clock (cosmos_watchdog2.py) honors mode in the pause flag."
    ),
    embodiments=_p(
        "Auto-resession watermark at about seventy percent of context; hard close at ninety percent; pack to live/state/session_saves/. Improper close: resume from session log and/or running_session_file.toml."
    ),
    public=_p(
        "AD-10 in public architecture 2026-08-23."
    ),
    prior_art=_p(
        "CONTINUITY arXiv:2609.05269 (2026-09-05 — signed context manifests plus CLOSE/OPEN receipts; closest paper; watch); Portable Agent Memory arXiv:2605.11032; Context Passport; CRAFT handoff; ctx handover; vendor memory; CRIU; JWT/JWS; US20250259069A1 reconstitutable sessions. Incident-on-missing-close as OS rule: unknown as patented."
    ),
    not_this=_p(
        "Not ChatGPT memory. Not CRIU. Not write a notes file."
    ),
    statement=_p(
        "Session identity that must close with a signed manifest; missing close is an incident and start refuses."
    ),
    appendix=APPENDIX,
)

add(
    id="P12",
    docket="COSMOS-P12",
    file="P12_CRUCIBLE.md",
    title="Crucible as a skin of occupancy applied to a legal packet (HOLD — do not file as plaintiff-defense-judge)",
    short="Crucible legal seats — HOLD",
    kind="Method / application of COSMOS-P05",
    status="HOLD",
    fee="$65 only if counsel files occupancy-not-roles",
    fig="FIG. 1 (if filed) shows P05 occupancy applied to a legal packet. Role names plaintiff, defense, and judge are labeled EMBODIMENT, not independent invention. A HOLD legend marks this packet not for filing as a role-triad.",
    field=_p(
        "The present disclosure, if filed, relates to applying the occupancy engine of COSMOS-P05 to a legal packet. It does not relate to inventing an AI plaintiff, defense, and judge."
    ),
    background=_p(
        "The plaintiff-defense-judge triad is crowded: SimuCourt/AgentsCourt 2024, AgentCourt 2024, CN119168059B granted 2025-07-15, US20260037351A1 claim 21. File only as occupancy applied to a legal packet. Roles are embodiments.",
        "Public bts-mesh GitHub description (2026-08-16) says CRUCIBLE method. Tracked files in that repo: zero hits for the word CRUCIBLE. The public date is a name, not a method disclosure in code."
    ),
    summary=_p(
        "HOLD. Do not claim AI plaintiff, defense, and judge. If counsel files, the specification is P05 occupancy applied to a legal packet: isolate, different-family, one disposer, runtime-bind, ledger. Role names are embodiments."
    ),
    definitions=[
        ("Crucible", "A product skin of COSMOS-P05 applied to a legal packet. Not a TM clearance."),
    ],
    detailed=_p(
        "Do not claim AI plaintiff, defense, and judge as the invention.",
        "If filed: apply COSMOS-P05 occupancy to a legal packet. Isolated proposers. Different-family critics. One disposer. Runtime-binding gate. Ledger authority.",
        "Role names (plaintiff, defense, judge) are embodiments of seats, not independent claims.",
        "Spend-gated critics. Vendor-plural.",
        "Marks: CrucibleTech RN 8043152 (games); Star Lab CRUCIBLE RN 5023199 (OS); Crucible Discovery; Destiny PvP fame. Not a TESS clearance.",
        "The twelfth sixty-five-dollar slot is taken by COSMOS-P13. This packet stays HOLD unless counsel files occupancy-not-roles as an extra application.",
    ),
    best_mode=_p(
        "In-tree POST /api/v1/crucible. 501 if no critics. Own tree per occupant. Product profile docs/PROFILES.md. Do not mix with medical Differentiator or Diligence packets."
    ),
    embodiments=_p(
        "A federated sit: a Crucible window bound to another operator's Core when that operator has a host. Until a host is named, peer is NO_HOST."
    ),
    public=_p(
        "Name CRUCIBLE method on GitHub About 2026-08-16T10:21:14Z. United States grace for what that string disclosed is thin (a name, not a spec)."
    ),
    prior_art=_p(
        "BLOCKING for role-triad claims: SimuCourt/AgentsCourt arXiv:2403.02959; AgentCourt arXiv:2408.08089; LegalSim; SAMVAD; PROCLAIM arXiv:2603.28488; 3-Ply arXiv:2606.30906; CN119168059B granted; US20260037351A1; US20250148558A1 (jury-side). Products: Jury Simulator, Juries.ai, Trial AI."
    ),
    not_this=_p(
        "Not we invented mock trial AI. Not a TM clearance. Not a twelfth slot while P13 is FILE."
    ),
    statement=_p(
        "If filed: Crucible as a skin of P05, not a PDJ patent. Else fold into P05."
    ),
    appendix=APPENDIX,
)

add(
    id="P13",
    docket="COSMOS-P13",
    file="P13_THINKFAST_DROP.md",
    title="Voice or chat client drop of a typed work order onto a reachable inbox executed by a host OS daemon that instantiates a named agent and audits by timestamps and a signed ledger",
    short="ThinkFast drop-box daemon; ChatBot phone Freemium embodiment",
    kind="System / method",
    status="FILE (twelfth $65 slot; P12 remains HOLD)",
    fee="$65 micro-entity provisional",
    fig="FIG. 1 shows a client that cannot mount the live root writing a typed JSON work order to a GitHub folder. A native OS daemon lists the drop, files DROPPED, instantiates a named agent WRITE-PRIVATE to Output, and records timestamps. GitHub objects are never deleted. GitHub Actions is not the executor. FIG. 2 shows a consumer ChatBot phone as a mouth: named :free model picker, Freemium free forever, funnel to Desktop ChatBot, optional Premium. FIG. 3 shows two remote mouths — a terminal and a phone — either of which may seat the adversarial occupancy engine (COSMOS-P05) through the same drop box.",
    field=_p(
        "The present disclosure relates to ingress of work from a voice, chat, phone, or remote-terminal client that cannot see an authority runtime root, via a typed work order on a reachable repository folder, executed by a host operating-system daemon that creates a named agent or the adversarial occupancy engine of COSMOS-P05, collects output, and writes a timestamped audit, without deleting the repository object and without letting the client write the live tree."
    ),
    background=_p(
        "If the human is the wire, voice work dies when the chat dies. If GitHub Actions runs the job, the audit is a vendor log and the agent is not fenced. If the phone could write the live root, that is a second writer (two-writer deletion scar).",
        "The inventor observed that the combination — client cannot mount live; typed JSON on GitHub; host OS daemon not Actions; named agent; done equals output file exists; timestamps plus signed ledger; never delete the drop — was not found as a blocking United States claim set. Pieces are crowded. This is not a novelty opinion. Patent Public Search remains owed."
    ),
    summary=_p(
        "An operator (voice, Chatbox, phone, or remote terminal) who cannot see the live runtime root writes a typed JSON work order to a GitHub folder that they can reach. A native system daemon on the host monitors that drop box, files the order into the live bucket, creates a session of the named agent or seats the adversarial occupancy engine (N isolated proposers, different-family critics, one disposer), collects Output, and records results with timestamps and an audit trail. GitHub files are never deleted. The LLM does not poll itself. GitHub Actions is not the executor. Dispose of live-tree writes remains one chief coder. A consumer ChatBot phone is an embodiment mouth: named OpenRouter :free picker, Freemium (free forever phone, free Desktop install, optional Premium). Adversarial AI over remote (terminal or phone) is an embodiment of COSMOS-P05 through this ingress, not a fourteenth provisional."
    ),
    definitions=[
        ("Drop box", "A GitHub path work_orders/drop/ on a named repo and branch. Not the live tree. Not repo root."),
        ("Six fields", "Agent; Context source; Task; Target and scope; Timestamp; Output."),
        ("WRITE-PRIVATE", "The agent may write only its Output folder or filename."),
        ("Freemium", "Free forever usable phone chat on named :free models; free Desktop install; optional Premium. Not a trial. Not crippleware. Not a claim that a vendor free API is infinite."),
        ("Remote mouth", "A terminal (TUI / SSH / drop) or a phone (ChatBot / Voice) that reaches this ingress without mounting the live root."),
    ],
    detailed=_p(
        "Inbox the client can reach equals GitHub path work_orders/drop/ on a named repo and branch. Not the live tree. Not repo root. One JSON object, six fields. Filename Windows-legal.",
        "A native OS clock (Windows Scheduled Task plus a pythonw daemon in the preferred embodiment) lists the drop, parses, and files DROPPED into the live bucket. It does not execute the Task.",
        "Seen-set is append-only (sha). GitHub objects stay. Seen-set is not authority.",
        "A second native runner picks DROPPED, creates a session of the named Agent, passes Task plus read-only context, WRITE-PRIVATE to Output only.",
        "Collect: DONE if and only if the Output file exists; else FAILED. File the order into the assigned or done folder with timestamps.",
        "Audit: daemon heartbeats (last_run_epoch), ISO timestamps on the order, ledger events when Core is composed. Dashboards are projections (COSMOS-P07).",
        "Voice speech-to-speech (Grok Voice Think Fast 2.0 in the operator embodiment) is one mouth. Chatbox is the same inbox. Return path may be a drive the phone can read without mounting live/.",
        "Dispose of live-tree writes remains one chief coder. The daemon does not hold the pen (COSMOS-P05).",
        "Consumer embodiment — ChatBot phone: the mouth runs on OpenRouter named :free models (low latency). The human picks a named model. Rotating ids openrouter/free and openrouter/auto are refused. Runtime bind equals response.model (COSMOS-P04).",
        "Freemium: Free forever is real chat on named :free models, no trial clock, no invented quota from the operator. Install (free) is Desktop ChatBot. Premium is optional (named paid models, desktop hands, later COSMOS-P06 on-box weights). Price is named by the operator, not in this specification.",
        "Vendor :free caps remain (in the preferred OpenRouter embodiment, twenty requests per minute; fifty per day until ten dollars lifetime credits, then one thousand per day). Do not sell unlimited :free as Premium. Do not print no usage limit as a warranty of vendor capacity.",
        "The phone never mounts live/. A remote terminal is a mouth, not a second writer on the runtime root. cosmos-voice.apk remains a draft seed, not this product. This is not CVM. This is not a thirteenth provisional.",
        "Adversarial over remote (the inventor: terminal or phone): the Agent field may name the occupancy engine (a seat-set) rather than one model. The runner then creates N isolated sessions under the peeking ban (COSMOS-P02). Critics are a different family. One disposer still writes the live tree. Free-tier single-model chat on the phone remains usable; adversarial N-seat is occupancy through the same mouths, not a shared chat on the device.",
    ),
    best_mode=_p(
        "Measured loop: Think Fast 2 (phone) to keithbbf-gif/cosmos work_orders/drop/*.json to ingest clock (about fifteen seconds, schtask COSMOS SGH Drop Ingest, cosmos_sgh_drop_ingest.py) to live/state/work_orders/bucket/ to Work-Order Runner creating an Agent session WRITE-PRIVATE; Output exists equals DONE; assigned folder plus heartbeat JSON plus ISO timestamps. CCr --accept / --reject remains the only live-tree writer. DEFINE files: DEFINE_THINKFAST_DROP.md and DEFINE_CHATBOT_PHONE.md."
    ),
    embodiments=_p(
        "Operator mouth: SGH Android Voice plus Grok Voice Think Fast 2.0 (tabled as voice refine; still the operator path).",
        "Consumer mouth: ChatBot phone Freemium as defined above. Desktop binary named at build (OpenWork desktop versus a COSMOS desktop ChatBot). Do not iframe OpenWork Web. Do not charge OpenWork Web fifty dollars as this funnel.",
        "Remote terminal mouth: a TUI or SSH session that can write GitHub and cannot mount live/. Same six-field drop. Same daemon. May seat one agent or the adversarial engine.",
    ),
    public=_p(
        "Work-order SOP and work_orders/drop/ exist on public cosmos after 2026-08-23. Voice loop named in wishlist and routing. GitHub date for the method as a voice-to-daemon-to-agent-to-audit loop is thinner than Core's 2026-08-23 architecture dump. FILE before another public article."
    ),
    prior_art=_p(
        "GitHub Issues / PR templates as inbox; GitHub Actions on push; ChatOps (Slack to Jenkins); cron plus file drop; n8n / Zapier / Make webhooks; Temporal / Airflow / Luigi; Siri Shortcuts / Alexa skills calling HTTP; Twilio US20250165890A1; voice-to-ticket SaaS.",
        "Combination not found as a blocking United States claim set: voice or chat client that cannot mount the authority root drops a typed work order on GitHub; a host OS daemon (not Actions) monitors, instantiates a named AI agent, collects a single Output file as DONE, and writes a timestamped COSMOS audit while never deleting the GitHub drop and never letting the agent write the live tree. Unpublished applications unknown. DOM research of Patent Public Search still owed."
    ),
    not_this=_p(
        "Not GitHub Actions. Not a mobile backend. Not a mobile frontend. Not CVM. Not we invented work queues. Not cron. Not the MOTIF loop (COSMOS-P01). Not the ledger primitive (COSMOS-P07). Not a claim that OpenRouter :free has no rate limit. Not a thirteenth sixty-five-dollar slot."
    ),
    statement=_p(
        "A voice-reachable or terminal-reachable GitHub drop box, executed by a local OS daemon that creates a fenced agent or seats the adversarial occupancy engine, with DONE equal to Output file and authority equal to timestamps plus signed ledger, operator out of the execution wire; optionally a Freemium phone ChatBot mouth on named free models that funnels to a desktop install."
    ),
    appendix=APPENDIX,
)
