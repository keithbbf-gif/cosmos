# cDeck

## What it is

The COSMOS operator deck: a Windows Tauri shell (`cdeck.exe`) plus the same UI over browser `fetch`. It reads Core on port 8770 and a few on-disk projections. It states which transport it actually got. A number with no source stays UNMEASURED. It does not invent meter totals.

`ORCH_HOME_SPEC.md` is the spec-before-code note from the session that wrote it (2026-09-05/06). It is not a map of what the deck runs. The deck that is in the tree is the lifted KDash wall plus later pages. The Cowork-like home in that spec is not the product identity. cDeck stays its own window. OpenWork is not embedded.

## Where it lives

Submodule `builds\cdeck`, pin `a4e0ad21` (`keithbbf-gif/cdeck`). UI under `builds\cdeck\ui\`. Python binders sit beside it (`cosmos_fleet_panel.py`, `cosmos_spend_panel.py`, `cosmos_jukebox_panel.py`, `cosmos_recents_panel.py`, and the node-map panel). Native shell is `src-tauri\`. Core may also serve the UI; a page on another origin can be `CROSS_ORIGIN_BLOCKED` because Core sends no CORS header. The deck names that; it does not pretend the server is down.

## Entry points

The wall in `ui\index.html` and `ui\app.js`: status, health, spend, jobs, jukebox, rails, makers, audit, tools, command bar, node map, batteries, fleet, caps, the CVM voice panel, channels, surfaces, human-posted pools, and an append-only event tail. Fast GETs abort at 8s. `POST /api/v1/voice` is allowed 70s.

Later pages in `ui\deck_more.html`: sessions, tools, CREATE, clocks, ORC seats, XTalk, Gitur, orders, studio, runs, review, the cluster floor (`#panel-cluster-orc`, stack, cards), the code chair, accounts, settings, profiles. Header loads `deck_hud.js` and `deck_chart.js`.

Accounts rail: Profile, Activity (lime), Logs, Credits, Keys. Activity is the upper-right ACTIVITY HUD. Logs generations render only when call rows exist. Upstream, Sessions, Videos, and Batches stay UNMEASURED until Core sends them. Cluster cards are a deck-local roster (ORC, stacked agent panes, seven device cards). A card with no measured seats says UNMEASURED. Preview strikes are labeled PREVIEW and are not Core totals.

The header token strip (`renderTokStrip` in `ui\header.js`) folds meter rows the page already holds on `#feed .fevent`. It does not sum `settled_usd` from `GET /api/v1/spend`. Cap and settled dollars are not inputs. If no on-page row has both a token field and a price field, every slot stays the text `UNMEASURED`. A missing count stays `UNMEASURED`, not `0`. A carried `0` stays `0`. The placeholder in `ui\index.html` is `IN UNMEASURED · OUT UNMEASURED · $ UNMEASURED`. The fold follows UTC today and the trailing seven UTC days, the same rules as `cosmos\cosmos_meter_window.py`. The cDeck pass reported that fold matched the parent fixtures 15/15. A later browser-free run, `node builds\cdeck\tests\header_meter_fold.js`, reported `assertions 102 passed` and `checks 7 passed, 0 failed` (`C:\Users\Papa\AppData\Local\Temp\c4-h29-result.md`). `ui\header.js` was not changed for that test. This note did not re-run it. The strip is of rows on the page, not a claim that the ledger was read.

Fleet and drive batteries read allowlisted projections (`feed`, `drive`, `registry`) after the root sentinel matches. No root means UNAVAILABLE, not an empty fleet and not zero.

## What it refuses

- Bearer stays in memory. It is not written to `deck.json`.
- Shell HTTP is origin-only, `/api/v1/*`, GET or POST, no redirect follow.
- Spend PUSH LIVE CAP is not success on HTTP 2xx. The deck re-reads `GET /spend`. A cap that does not come back is `WRITE_NOT_VISIBLE`. `cosmos_spend_panel.py set` refuses `ROUND_TRIP_UNVERIFIED` unless a fresh `SpendGate` reads the cap back. A cap below settled plus reserved refuses unless the operator passes the allow flag.
- Human-posted Claude/Grok pools are not sent to `/spend`. Voice session/day/rate caps are not on `GET /spend` and are not painted as zero.
- Credits does not charge. Keys are LED (PRESENT, LIVE, or NO_SOURCE) and do not echo secrets.
- Jukebox has no cancel, hold, or retry. An unread queue is UNAVAILABLE, not empty. CREATE files a job. QUEUED is not created.
- Mic on the command bar stages text. It does not auto-run.
- The cluster floor has no pen and is not the CODE Clusters plugin.

## What it is not

Not Core, not the ledger, not OpenWork, not a second phone, not a website. `8791` is the trial kernel, not live. The footer `tree_id` is whatever the server emitted.

## Grade

Pin `a4e0ad21`. There are 24 test files (19 at `builds\cdeck\test_*.py` and 5 under `builds\cdeck\tests\`). The second cDeck pass finished. Pytest on that local list was 5 failed, 33 passed in 1.67s (`C:\Users\Papa\AppData\Local\Temp\c4-cdeck2-result.md`). The five failures are stale probe JSON. Each probe needs Chromium, a live token, and an upstream server. The JSON was not regenerated and was not hand-edited. Day and week stay `UNMEASURED` until the page holds a real priced meter row. `node --check` on `ui\header.js` exited 0. Ruff on `header.js` and `index.html` is not a Python grade.
