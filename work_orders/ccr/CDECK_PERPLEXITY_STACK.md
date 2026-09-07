# CCr dispose — Perplexity cDeck stack (free-only)

**Keith 2026-09-07.** Input from Perplexity. *You evaluate what should or
should not be implemented.* *Only to the degree it's free.*

This is **CCr dispose of a vendor proposal**, not BUILD. Frozen against
canon: `docs/FINAL_ARCHITECTURE.md` (one Core, ledger authority, SQLite
projection never authority), `docs/PROFILES.md` (time-travel / LangGraph
export / invented traces **stay out**), `CDECK_STUDIO_MOTIF.md` (extra
panes map onto **live Core**, not a second graph engine), MESH_ADDITIONS
**n8n REJECT** as scheduler (H2/H8), OpenWork bind (cDeck is native
`cdeck.exe`, not Chrome, not a second Cowork).

Perplexity proposed: React + Vite + admin template + LangFlow + LangGraph
+ Temporal + Postgres + FastAPI, with MOTIF/COW as LangGraph graphs and
cDeck as a new SPA under `V:\a\ai\cosmos\cdeck`.

**"Free" here means OSS license + self-host.** That is **not** free of a
second operating system. Hardware + a new orchestrator + LLM API bills
are not the ChatBot "FREE FOREVER" seat. H8: net complexity must trend
down. A second Core fails that even at $0 license.

## Ruling (do / do not)

| Piece | Free license? | Implement? | Why |
|---|---|---|---|
| Extra-pane **UX steal** already decided (Studio / Runs / Review / Prompts / Surfaces) painted from Core `:8770` | n/a | **KEEP** | Already DEFINE'd. Live emit = jukebox / surfaces / gitur. Not this stack. |
| Native **`cdeck.exe` (Tauri)** | yes (our tree) | **KEEP** | Keith: cDeck is its own window, not Chrome. |
| Core `/api/v1` + JSONL ledger + SQLite **projection** | yes | **KEEP** | Authority is the ledger (P07). Dashboards rebuild. |
| Named OpenRouter `:free` picker (ChatBot) | $0/token, vendor RPM/RPD | **KEEP** (product, not cDeck OS) | Freemium mouth. Not LangGraph. |
| **LangGraph** as MOTIF / COW | OSS | **DO NOT** | MOTIF is P01 (DEFINE first, iterate → DEFINE). LangGraph would be a second loop. `PROFILES.md`: LangGraph export stays out. |
| **LangFlow** embed / canvas as the editor | OSS | **DO NOT** | Second UI. Extra-pane Studio is the steal, mapped onto Core. Do not iframe a workflow product. |
| **Temporal** (self-host) as durable workflow | OSS | **DO NOT** | Same reject class as n8n (H2/H8): Core already schedules (Pulse, WD2, schtasks, work-order runner). Human-in-the-loop is CCr `--accept`, not a Temporal signal. |
| **PostgreSQL** as run/state/prompt authority | OSS | **DO NOT** | Projections may be SQLite. Postgres as the store of runs/steps/snapshots is a second authority. Ledger is authority. Time-travel snapshots stay out. |
| **FastAPI** second API in `cdeck/backend` | OSS | **DO NOT** | One versioned API is Core. cDeck is a client. |
| **React + Vite + admin template** replacing Tauri | OSS | **DO NOT** | Rebuilds the deck as a SPA. Occupancy host is `cdeck.exe`. |
| New repo path `V:\a\ai\cosmos\cdeck` | n/a | **DO NOT** | Product is `builds/cdeck` / GitHub `keithbbf-gif/cdeck`. No dual tree. |
| Fork-from-here / re-run-from-step / per-step traces | n/a | **DO NOT** | Time-travel and invented traces stay out (`PROFILES.md`, Studio DEFINE). |
| Review queue **annotation POST** / Temporal resume | n/a | **DO NOT** | Review = FINDINGS + stale RUNNING from `/jukebox`. Dispose is CCr. No annotation POST. |
| Surfaces browser as GET `/surfaces` | already Core | **KEEP** | UNMEASURED if Core did not send the row. Do not invent a Postgres surfaces registry. |
| Prompts as GET model_rater / Prompts tab | already Core | **KEEP** | Do not stand a Vellum clone. |
| A/B experiment tables | n/a | **DO NOT** (this tick) | Invented bake-off. P06 says do not put a number in the spec. |

## What Perplexity got right (keep the wish, drop the stack)

- Extra panes should look like a run explorer / review list / surfaces list.
  That is **already** Studio / Runs / Review / Prompts / Surfaces on Core.
- Durable long-running work exists. That is **already** schtasks + work-order
  runner + SEED/carry-over (P11, P13), not Temporal.
- Human gate exists. That is **CCr one pen**, not a signal.
- Surfaces are first-class. They are **Core `/surfaces`**, not a new table.

## What "only to the degree it's free" allows

Free **and** already on the machine: Core, cDeck Tauri, named `:free`
OpenRouter pins, GitHub drop, Windows clocks. Those stay.

Free **license** that would still tax the OS (second scheduler, second
API, second DB authority, second UI): **refuse**. Cost is complexity and
a two-writer / two-authority scar, not the invoice.

## Off-limits (unchanged)

Do not auto-MOTIF Forge/Studio. Do not merge cDeck #6 / #16. Do not merge
#31 until FINISHED and retargeted onto `main`. Do not write `V:\Ai`. Do
not file USPTO. Do not publish. Do not stand Temporal/Postgres/LangGraph
as COSMOS2.

## THIS TEXT

CCr ruling. Copy into any lane that asks "should we build the Perplexity
stack?" The answer is no, except the extra-pane paint already in flight.
