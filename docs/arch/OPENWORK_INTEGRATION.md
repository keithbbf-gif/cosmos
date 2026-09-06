# OPENWORK × COSMOS INTEGRATION

**CCr G46 2026-09-05.** Keith: *OpenWork has too much of what we need to ignore.* How they join. Not a Core rewrite. Not an iframe.

Vendor: https://openworklabs.com/docs/start-here/get-started  
Bind: `docs/OPENWORK_BIND.md` · Seat: `docs/ORCH_SEAT.md` · Frame: `builds/cdeck/ORCH_HOME_SPEC.md` P5

## One sentence

**COSMOS is the OS. OpenWork is the orch harness.** They integrate by **contracts** (API, mailbox, C0, recents), not by stuffing Electron into cDeck.

## Already joined (do not rebuild)

| Contract | COSMOS | OpenWork | Bound |
|---|---|---|---|
| **Process C0** | cDeck `open_openwork` / `openwork_status` | `OpenWork.exe` + loopback `/health` | Focus or launch. LIVE chip. No second spawn (H7). |
| **Sessions** | `GET /api/v1/recents`, `builds/open_sessions/` | pack + `ses_*` | List/open; click focuses OpenWork. Legal omitted. |
| **Migrator** | CCr Gitur side-job | `cowork_to_openwork` | Seed, not the suite. Do not re-ingest 666. |
| **Mailbox** | CCr harvests | `cm\` under GFO grant | File drop. Core `/api/v1/mail` is 404. |
| **Pens** | CCr writes `V:\A` | GFO writes grant tree | GFO **reads** engine room; no COSMOS root grant. |
| **Desk now** | Left HP 24N this TUI | Right HP 24N GFO fullscreen | Stands. Surface-merge with cDeck is off this occupancy. |

## Target join (this occupancy)

**Keith 2026-09-06:** *kDash → cDeck is too different to integrate with OpenWork — at least at this point.* **Keep them as separate apps and windows for now.** OpenWork = session. cDeck = COSMOS_2 backend (KDash visual: health, nodes, surfaces, lanes). Code in `builds/cdeck`, Gitur BUILD. Link = C0 + mailbox + recents + later MCP. Not one chrome. Do not copy cDeck into the grant. Do not hide the wall.

**Prior target (P5 2026-09-04), deferred:** cDeck as the frame with OpenWork main-left. That is the integration he just parked.

**Occupancy possibilities (Keith 2026-09-05 — not edicts):** sidebar / pop-out; or cDeck as a linked dashboard beside OpenWork. They sit under the 2026-09-06 bound (separate products).

**Embed stays last / off this occupancy.** Official desktop is Electron — no HTML origin. OpenWork Web is Cloud ($50/member) — **not** the GFO sit, **not** an iframe. Copilot’s Tauri-webview **conflicts**. The honest join is already **C0 + contracts**.

## Four pipes (this is the integration)

```
 GFO / OpenWork                 COSMOS Core :8770              This TUI / cDeck
 ----------------               -------------------            ----------------
 skills, MCP, browser,          ledger, leases, clocks,        CCr dispose,
 connectors, session groups  →  recents, spend, Gitur     ←    Gitur PRs
        |                              |                          |
        +-- MCP/HTTP to /api/v1/* -----+                          |
        +-- cm\ mailbox -------------- harvest -------------------+
        +-- C0 OPEN/LIVE ---------------------------------------+
        +-- recents click → focus OpenWork ----------------------+
```

1. **OpenWork → Core (MCP or HTTP).** Core already has one versioned API (`/api/v1/*`). COSMOS does **not** have an MCP server today (`cosmos_service` has no MCP). Next BUILD: a **thin MCP adapter** in `builds/` (side job, Gitur branch) that exposes status, recents, mailbox-ack — **read/propose**, not ledger write. OpenWork Connect / custom MCP points at loopback. Fail-closed: no COSMOS root grant.

2. **OpenWork → CCr (mailbox).** Already the orch path. GFO drops WOs in `cm\`. CCr harvests, runs Gitur, disposes.

3. **cDeck → OpenWork (C0).** Already. Recents click = same OPEN. Do not iframe.

4. **OpenWork hands stay OpenWork.** Skills, plugins, Library, browser, Drive/Gmail connectors, session groups, Automations UI — **GFO uses them**. COSMOS clocks stay native Windows. Do not clone Automations as a 27th CLOCKS row. Do not clone Library as a COSMOS skill OS.

## What we do not do

- Iframe `OpenWork.exe` or OpenWork Web.
- Grant OpenWork the COSMOS repo.
- Recode `cowork_to_openwork` as ORC; if CCr changes it → Gitur branch of its own.
- Rebuild Open Sessions in place (LIVE; iterate on a branch).
- Mix wallets / click Cloud billing / paste Web instance URLs.
- Sit Legal from this TUI (GFO + Keith, right monitor).
- Dump integration onto `main`. One job, one branch, one PR.

## Gitur order (organized)

| # | Job | Branch shape | Notes |
|---|---|---|---|
| 0 | This arch | `ccr/openwork-integrate` | this file |
| 1 | Core-as-MCP (read/propose) | `ccr/cosmos-mcp` | `builds/` side job; not kernel rewrite |
| 2 | Recents → C0 completeness | `ccr/cdeck-recents-open` | cDeck submodule = **its** Gitur job |
| 3 | Bind OpenWork Browser as named DOM rail | `ccr/ow-browser-rail` | beside GEM/SGH; do not replace them |
| 4 | Skills/Library consume notes | mailbox + GFO | no CORE clone |
| 5 | Embed / surface-merge | **off this occupancy** (Keith 2026-09-06: kDash→cDeck too different) | do not BUILD |

Keith running this TUI on the left and GFO fullscreen on the right **is** the integration this occupancy. Pipes + link, not one window. Not the GFO daily-wheel handoff until Keith says so.
