# Gitur BUILD — Chamber JOIN from ORC CHAT pane (paint presence, no iframe)

**Repo (PRIVATE):** `keithbbf-gif/cosmos`
**Branch:** `ccr/chamber-orc` from GitHub `main`. Not unique HEAD `8b5ad84`.
**Lane B:** Cursor Cloud Agent, Opus 5 / Sonnet class. Composer 2.5 / Auto refused. Do not change Opus T.
**Pane job:** preload `work_orders/ccr/CREW/IN/PREFIX.md` + `CACHE_RULE.md`. Tail is this ticket.
**P10:** PROPOSE only. CCr writes CORE. Chamber is a **projection**, not a mesh daemon.
**Do not:** spawn grok.exe, pull 8b5ad84, merge leftover PRs (cdeck 6/16/17/68, cosmos 30/32/36/37/38), USPTO, iframe OpenWork/Grok, invent GET /chamber (it exists), take occupancy below 163.

FIRST read `docs/AGENT_BRIEF.md` and `docs/AGENT_BOUNDARIES.md`. Then `docs/STEAL_MAP.md` order item 5 and PREFIX occupancy rules.

## Already on this tree (do not re-build)

- `cosmos/cosmos_chamber.py` — rooms `Cm` `plumbing` `physics` `chapter`; **legal refused** (`STREAM_REFUSED`). `join` / `snapshot` / fold of `CHAMBER_*`. Selftest **3/3**. Empty snapshot `kind=UNMEASURED`. GET never mkdir.
- `GET /api/v1/chamber` **200** UNMEASURED on live `:8770` (`cosmos_service.py` GET only; query `room=`).
- `join(ledger, room, principal, family)` appends `CHAMBER_JOIN`. **No HTTP POST** on that path yet.
- ORC CHAT extra pane: `builds/cdeck/ui/deck_orc.js` + `#panel-orc` in `deck_more.html`. Paints `GET /api/v1/seats`, `GET /api/v1/approvals/pending`, `GET /api/v1/recall?q=`. **Does not paint `/chamber`.** No iframe. No pen.
- Occupancy pin: `builds/cdeck/test_kdash_working.py` **163/163**. Must stay green (**163+**). Host `cdeck.exe`.

PREFIX extra-pane list is stale vs live `/chamber`; do not invent a new GET name. Use the GET that already returns 200.

## Job

Chamber JOIN from the ORC CHAT pane.

1. **Paint presence** from `GET /api/v1/chamber?room=Cm` (and the stream chip if ORC already has one). Empty → UNMEASURED, never fake occupants. legal never offered.
2. **JOIN** from that pane: button/chip calls `cosmos_chamber.join`. If Core has no POST, propose **POST `/api/v1/chamber`** on the **same path** as the GET (body `room`, `principal`, `family`). GET stays snapshot. Do not invent `/api/v1/chamber/join`. P9: ORC has no pen; JOIN is a presence event, not a CORE write of code. Refuse legal.
3. **No iframe.** Do not embed OpenWork, grok.com, or a second chat origin. Occupancy is no-iframe.
4. Occupancy tests: add a pin that ORC CHAT paints `/chamber` and has no iframe; **do not regress** existing 163. `test_kdash_working.py` pass count **163+**.
5. Chamber stays a ledger fold. No daemon. No second scheduler.

PREFIX "No new GET/POST" means do not invent unshipped GETs. `/chamber` GET is live. POST on that same path is the JOIN wire, not a new product.

## Bite

- GET /chamber empty → 200 `kind=UNMEASURED`, no mkdir (already).
- legal room → STREAM_REFUSED / 400.
- Pane: `GET /api/v1/chamber` appears in `deck_orc.js`; `createElement("iframe")` still absent; `#panel-orc` still in FILL_TABS.
- `py -3.14 builds/cdeck/test_kdash_working.py` **163+** pass, 0 fail.

## Output

Unified diffs FIRST (service POST if needed, `deck_orc.js`, `deck_more.html`, occupancy pin), then 3-line verify. Empty proposal if paint+JOIN already work — do not rewrite working code. Under `proposals | CHAMBER_ORC.json`. PR `WO: chamber JOIN ORC CHAT`. Gitur BUILD. autoCreatePR.
