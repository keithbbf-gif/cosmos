# Mesh update + comms service (Keith 2026-09-04)

**COSMOS is the OS. Crucible is the application the OS runs.**
Canon expansion: **Carry-Over State Mesh Operating System** (`CLAUDE.md`).
(Keith also said “Session”; carry-over *is* session/SEED. Do not fork the name.)

## Split

| | What | Writes Keith’s live tree? |
|---|---|---|
| **COSMOS** | OS: Core, ledger, leases, CCr, one versioned API, clocks | Only **this** install’s CCr |
| **Crucible** | **Product** (app) on that OS. Profile + **Crucible skin** go with it | No. Runs as `POST /api/v1/crucible` on **that** Core |
| **Other products** | e.g. **medical differentiator** — own profile, own skin | Do not share Crucible’s profile or Cm’s skin |
| **This service** | Communications + **updates** of OS and app to federated installs | No. Meeting point + wire, not a second CCr |

## Where it runs

Keith: can run on **T7920 (T7)** **or** **SRV1** (also written SRVR1). **Not chosen yet.**
Both are F-56 `LAN_NODES` with `host=None`. Do not invent an address. Do not put
Grayson’s PC in this table — he is a **peer**, this is the **hub**.

This is the federation hole named in `federation_blockers()`:

- “no meeting point (LAN NAS does not exist…)”
- “no wire protocol (`cosmos_mail` schema exists; transport does not)”

The service **is** that meeting point + transport, once a host is named and it
actually speaks.

## What it does

1. **Comms** — mailbox between installs (Keith Cm, Grayson Crucible, later peers).
   Same one-writer / lease rule. No shared tree.
2. **Updates** — ship COSMOS (OS) and Crucible (app) to a peer. Peer applies through
   **its** fenced commit / CCr, or refuses. Not a silent overwrite of the peer
   (two-writer deletion scar). Hash + identity on the packet.
3. **Does not** become COW, CCr, or Crucible on the hub.

Until `host` is set and a tick proves reachability, F-56 stays `NO_HOST` /
`federation_ready()==false`. A declared service is not a live wire.

## cDeck: where it lives (Keith 2026-09-04)

cDeck is a **skin** (product → profile → skin). It is not Core.

| Piece | Where | Why |
|---|---|---|
| **Develop** | Keith’s PC, this tree | CCr, keep-her-afloat, ConPTY, OpenWork grants |
| **Keith’s live orch** | **Local PC** (Tauri shell) | OpenWork left + Grok TUI right need *this* machine: folder grants, Chrome profile, coding pane. A service on T7 cannot be that session |
| **Publish / serve skins** | **T7 (T7920)** once host is named — or SRV1 if that is the hub | Update+comms hub ships Crucible / medical / Cm skins. Peer talks to **their** Core. UI may deploy separately; authority may not (decision 7) |

**Yes, cDeck can run as a service on T7920** — as the **deployment origin** (HTTP skin + update packets), not as Keith’s operator desktop and not as a second Core.

**Do not** move live Core `:8770` / `KMesh-COSMOS-live` to T7 just to host a deck. The deck is a client. T7 `NO_HOST` until Keith names it.

## Grayson

His own PC. **Mostly Crucible** (app). COSMOS (OS) underneath, thin.
He **pulls** OS/app updates from this hub (or the hub pushes; same packet).
His critic keys stay his. See `docs/federation/GRAYSON.md`.
