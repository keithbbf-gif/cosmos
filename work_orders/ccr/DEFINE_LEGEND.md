# DEFINE — the legend (007 package)

Keith 2026-09-18: *Let's say you were calling in 007, and give him a new ID, a new job (coverstory), new gadgets, new mission, new house, in a new city... what would you call that "package"?* Then: *new training (skills)*. Also: *Digs?* And: *See how much of [that] you can apply once you start calling subagents.*

WRAP: What is the intent, and the best execution of this intent?

**Name: legend pack.** Tradecraft for the constructed identity you insert. Not “digs” (that is only house + city). Not “seat” (already a model pin). Not “pack” (already fat|house in Enviro).

**Mission pack** = this job (was brief/tail). **Legend pack + Mission pack = DUDs** (Deployment bUnDle). Slang for a **sharp outfit**, not a loser. **Agent + DUDs = HERO.** Spawn in HERO mode = apply the DUDs (seven layers + this mission).

Google (2026-09-18) after seeing the table: Legend = structure on the launchpad; Tail = vector; **Legend + Tail = Deployment.** That split is right.

Keith later packet **AGENT DEPLOYMENT BUNDLE**: Legend + Tail = the fire-time whole. **Adopted name:** **deployment bundle** = legend + brief. Short: **DUD** (Deployment bUnDle). **Agent + DUDs = HERO.** No DUD = not a HERO = no spawn. Verb remains **spawn**. **Dispatch** is the same object if we say it in orch talk.

Subagent = new HERO, new DUD. Parent may hand a brief; parent legend does not leak.

**Keep from that packet:** Tail out of Legend (P11). Gadgets in Legend, not a side kit. Digs = Harness + Enviro as a *nickname*.

**Do not keep:** Legend as an immutable container image. STYLE appends and skill accept change the blueprint across attempts. Each spawn gets a **new sid** and an attempt-private Enviro (resume/BU inject is state). “100 identical 007s” means 100 hydrations of the **same Role×Model defaults**, each a new legend instance + its own brief — not one shared occupant. Digs is **not** an apply-order slot: apply remains Role → Model → **Harness** → Wrapper → Skills → Tools → **Enviro**. Harness is 3; Enviro is 7. Bundling them in a diagram does not move Enviro up.

Mission is **not** in the legend. Mission is the **brief** (P11 tail). Mixing them is the cache killer (dates, this PR, this ITEM in the prefix).

**Size (Keith 2026-09-18):** two knobs. Write preload (cache PREFIX) and prompts **first**, then:

- **MAX** (reply limit, **cannot float**, **cannot be 0**): `MAX = context_window − (cache + prompts) − 0.20×context_window`. The 20% is thinking + errors. Set API `max_tokens = MAX`. `MAX ≤ 0` → refuse.
- **OPTIMUM** (aim, **may float**, **cannot be 0**): if expected output is known, shoot for it with headroom (10k tokens of `.py` → 15k), must be **> 0** and `≤ MAX`. If unknown, `optimum = "float"` — never write `0`. Same for `cap_tokens`: omit or a positive count, never `0`. **Shoot OPTIMUM when it is a positive count; always obey MAX.**

**xAI 200k / 2× (Keith 2026-09-18):** Grok mouths **2× surcharge above 200k**. Cheaper to start a new session. G46 coding does not need a huge load — keep PREFIX+ITEM under 200k even if the window is larger. Do not fill MAX up to the window on xAI.

Google’s first cut put gadgets in an “Operational Kit” beside a “Legend Dossier.” **Wrong for this OS.** Tools are Role[Model] allow-list — who he is allowed to be, not this week’s mission. Q issues kit *with* the identity. ORC without write tools is a different legend than CODER with files. Gadgets stay **in** the legend.

## 007 → spawn layers (apply order)

| 007 | Layer | In the legend? |
|---|---|---|
| New ID | **Role** (+ child sid; not inherited) | yes |
| Who he is when he talks | **Model** | yes |
| New city / service | **Harness** (kind + via) | yes — part of the digs |
| Cover job | **Wrapper** (`WRAP/{Role}` + `STYLES/{Model}`) | yes |
| **New training** | **Skills** — Role defaults + Role[Model] overlays; propose→CCr accept. Child's set, not the parent's. | yes |
| New gadgets | **Tools** (kind-gated allow-list) | yes |
| New house | **Enviro** (workspace, ctx list, pack, budget, resume) | yes — rest of the digs |
| New mission | **Mission pack** (task / diff / ITEM) | **no** — not in legend; with legend = DUD |

**Digs** = Harness + Enviro (city + house). Useful slang, not the package name.

## Subagents

**All of it.** A child gets a **new legend**, 7/7 layers, same order. Parent may hand a brief. Parent legend does not leak.

This TUI `spawn_subagent`, Cursor kid, Gitur Cloud Agent, farm Popen, OpenWork SSA, `grok --single` — each one is 007 in a new city. No thinner “just a mouth.” Degenerate `mouth:*` only if native via unbound.

## Not

Ori as one legend for every family. Extra `grok.exe`. ORC legend with a COSMOS folder grant. Putting the brief in PREFIX. USPTO. Fire Gitur while **#580–#586** are open.

Canon: `docs/CANON_SPAWN.md`. Gitur (later): `GITUR_HARNESS_SEAT.md`.
