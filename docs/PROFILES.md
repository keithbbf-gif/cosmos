# COSMOS2 profiles (Keith 2026-09-07)

**Product → profile → skin.** COSMOS is the OS. cDeck is a skin. Do not mix
skins across products. Do not start MOTIF on these until Keith says the
code is ready (`CDECK_STUDIO_MOTIF.md`).

**Not every stolen-UI feature.** Forge/Studio extra panes are enough to *set
up* adversarial seats, job tokens, and cost. Time-travel, LangGraph export,
and invented traces stay out.

Each profile owns: pen (own tree), mailbox `writer_id`, hands, Chrome
profile, live vs dark. One occupant per profile. UPS / LEGAL / coding do
**not** share a root.

| # | Product / profile | What it is | Skin | Status |
|---|---|---|---|---|
| 1 | **UPS** | Physics: spectra analyzer including **UPS-JUDGE** (GEM Vertex full-context judge — named load, not search). Own stream/tree. | cDeck UPS | **Needs Keith.** Rebuild from July sessions. Do not invent the app. |
| 2 | **Forge** | Coding: CCr main pane + N parallel adversarial coders. CCr token estimate (24k/8k initial) × model rate card, manual override. Propose ≠ CCr pen. **Orthogonal porosity** (pair vector; disagreement × error mag; tensor DB) is built into every Forge adversarial trial. | cDeck Forge | **Cooking.** Extra-pane Forge tab + `forge.ccr` / `forge.adv_N`. Porosity GET `/api/v1/porosity`. |
| 3 | **Crucible** | Legal: a case evaluated and role-played through stages by adversarial agents/models (plaintiff / defense / judge). `POST /api/v1/crucible`. Grayson’s federated app. | cDeck Crucible | **Named.** Core route exists; 501 if no critics. Own tree per occupant. |
| 4 | **Differentiator** | Medical Crucible: anonymized casefiles in; each model an independent opinion; then they argue. Not Crucible’s Legal tree. Not Legal transcripts. | cDeck Differentiator | **Named in occupancy.** Not built. Anonymize is a gate, not a nicety. |
| 5 | **Diligence** | Fastest profitable clone of the same adversarial engine: a packet in (data room / 10-K / deck); **bull / bear / independent risk** write independently, then argue. Same seats pattern as Crucible. Not Legal. Not Medical. | cDeck Diligence | **Pick for “other.”** See below. |
| 6 | **Docket** | Patents / trademarks / copyrights. MOTIF applied to IP: applicant / examiner / prior-art seats; provisionals; TESS. **Not** the Legal Crucible tree (cases). Filing is Legal + Keith. Research: `docs/research/IP_DOCKET.md`. Provenance split: `docs/PROVENANCE.md`. | cDeck Docket | **Named 2026-09-07.** MOTIF 1 only until DOM returns. |
| 7 | **Spidercaster** | Site MOTIF. Step 1 is the problem prompt. Each of the 9 MOTIF stages is a left-tab **skin**. IMPLEMENT (was IMPROVE) writes a **staged site**, **sandbox**, **publish online** (Keith click — this TUI does not publish), or **Gitur**. Same engine shell as the other profiles. | cDeck Spidercaster | **Cooking.** Extra-pane Profiles tab. Does not start MOTIF. |

## Fifth profile — why Diligence

Keith: *most profitable and quick to adopt an adversarial model.*

The engine we already have is: N named seats, independent first, then argue,
token estimate × rate card, CCr/human dispose. **Diligence** reuses that
without a July rebuild (UPS) and without a new medical-anonymize gate.

- **Quick:** three seats (bull / bear / risk), one packet, same Forge/Crucible
  UI. No new OS. No new ledger.
- **Profitable:** buyers already pay for a second opinion on a deal. Ticket
  size beats volume toys; it does not collide with Crucible (Legal) or
  Differentiator (clinical).
- **Not this tick:** insurance **Claims** (volume, regulated) or cyber
  red/blue (also a clone, later). Do not mix Diligence packets into the
  Legal tree.

## UPS rebuild

July sessions hold the spectra analyzer / UPS-JUDGE. Keith said that app
**might require his help** to rebuild. CCr does not reconstruct it from
guesses. Physics stays on the **UPS** tree, not `V:\A` coding, not Legal.

## Parallel instances (Keith 2026-09-07)

Today that sit is **Grok.com TUI + OpenWork** as two windows. The cDeck
feature is the same pattern **inside** the deck: two native windows, two
profiles, one Core (or later two Cores).

| Now | Later (federation) |
|---|---|
| Forge window + Crucible window, both `http://127.0.0.1:8770` | Crucible window bound to Grayson’s Core when he has a host; Forge stays on Keith’s |
| One API, many clients | Mailbox + lease before any shared write. No shared tree |
| INSTANCE on the CONNECT row | Peer picker is **UNMEASURED / `NO_HOST`** until Keith names an address |

Do **not** spawn a second `cosmos.py serve` to get a second window. Do **not**
mix Forge and Crucible skins in one window as if they were one product.
JACK’S MESH stays on each instance — extra panes do not hide it.

## Consumer ChatBot (not an occupancy profile)

Keith 2026-09-07: phone ChatBot is a **product**, not a seventh occupancy
row. Do not mix it into UPS / Forge / Crucible skins.

| Product | What it is | Skin | Status |
|---|---|---|---|
| **ChatBot phone** | **Freemium free tier.** Named `:free` picker. Pitch **FREE FOREVER — YOU PICK THE MODEL**. Real chat forever; not a trial. Same P13 GitHub drop. May seat **adversarial occupancy** (P05) over remote. | Phone ChatBot (not cDeck) | **DEFINE.** `work_orders/ccr/DEFINE_CHATBOT_PHONE.md`. Not CVM. Not SGH Voice. |
| **ChatBot desktop / remote terminal** | **Freemium install** (free download) + natural **Premium** sit. Terminal is the other remote mouth (TUI / SSH / drop). Same occupancy engine. | Desktop ChatBot or TUI | **Named at BUILD.** Adversarial over remote = terminal **or** phone. Price UNMEASURED. Do not iframe OpenWork Web. |

Occupancy profiles above stay operator / federation skins. ChatBot phone
does not get a `cdeck-instance` profile id until Keith says it is a deck
skin (it is not, today). **Spidercaster** is an occupancy profile (`website`).

## MOTIF engine skins (Keith 2026-09-07)

Every profile sets up the same 9-stage MOTIF engine, each stage a left tab
with that profile's skin. Stage 1 is **PROBLEM STATEMENT / STATED GOAL**.
Stage 8 is **IMPLEMENT** (was IMPROVE). Write dest is **profile-specific**:
Forge/UPS → local / Gitur / cloud drive; Spidercaster → staged / sandbox /
publish / Gitur. SAVE does not start MOTIF. Publish is Keith's click.

## Shared Forge tools (all profiles)

Setting up adversarial agents is a **Forge-class control**, not a reason to
fork Core: add/remove N seats, assign a named model, CCr-provided token
estimate, autocalc cost, override. Each product’s *roles* differ
(coders vs counsel vs clinicians vs bull/bear). The control is the same.
