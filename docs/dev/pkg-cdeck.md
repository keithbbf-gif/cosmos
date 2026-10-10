# cDeck

cDeck is the submodule `builds/cdeck` ([keithbbf-gif/cdeck](https://github.com/keithbbf-gif/cdeck.git)). This page is a reading map of that package. It does not paste the UI. cDeck is not finished, and COSMOS is not finished. The deck is not fully integrated. The wishlist is not done, and it is not fully tested.

The parent repository records the submodule as a gitlink, not as ordinary files. The pointer in the index is `151016a1222f8787498151ffe2abe9e0970028b1`. The working tree under `builds/cdeck` also has uncommitted edits, including files in `ui/`. Read the files on disk. A clean checkout of that gitlink alone is not the loader this page describes. Do not commit from this chapter.

Product version in `builds/cdeck/package.json` and `builds/cdeck/src-tauri/Cargo.toml` is `0.2.2`. The native crate is Tauri 2. `frontendDist` is `../ui`. The window title is Jack's Mesh Command.

## Two ways it opens

| Host | What starts | What it can see |
| --- | --- | --- |
| Native shell | `py -3.14 cosmos\cosmos.py deck` starts `builds\cdeck\src-tauri\target\release\cdeck.exe` when that file exists (`cosmos/cosmos_cdeck_launch.py`). A missing file is `EXE_MISSING`. | The `ui/` directory, plus Rust commands such as `api_request`, `read_projection`, `local_get`, and `load_install_token`. |
| Browser on Core | `GET /cdeck` redirects to `GET /cdeck/`. The shell is an exact-name allowlist in `cosmos/cosmos_service.py` (`_CDECK_UI_FILES`). No bearer, no ledger, no token in those files. | Only names on that list. Same-origin `/api/v1/*` is the browser data path. A foreign origin is not given a CORS header. |

`ui/header.js` defaults the API base to `http://127.0.0.1:8770`. Port 8770 is live Core. Port 8791 is the trial kernel. `tree_id` is whatever `GET /api/v1/status` answered in that window. It is not copied from the opener and it is not filled in with a default. The footer chip is the place that fact is shown.

The profile names in `header.js` (`forge`, `crucible`, `diligence`, `docket`, `ups`, `differentiator`, `website`) are skins on one Core. A profile window is not a second Core.

A bundled `cdeck.exe` is a build output. This page does not claim that the exe on disk matches the current `ui/` tree.

## How the pages load

`ui/index.html` is the document. At the end it statically includes only three scripts: `deck_sfx.js`, `header.js`, and `kdash_native.js`.

`header.js` is the loader. It fetches `deck_more.html`, then injects `deck_tabs.js` and the other page scripts, then `app.js` last. The `pages` array in `header.js` is the `deck_*.js` list. A script that fails to load does not stop the rest (`onerror` continues). Do not copy that list into this book. It moves.

`ui/deck_tabs.js` is the left rail of extra panes. It does not own the beige header. Tab ids and hints live there. The Cluster tab's hint is `ORC · stacked agents · seven cards`.

`ui/deck_home.js` does not paint home or session. It forwards those names to `window.cdeckPaint` in `app.js`.

Core's static allowlist is not the whole `ui/` directory. `header.js` loads these six page scripts, and `_CDECK_UI_FILES` does not name them:

- `deck_cluster.js`
- `deck_hud.js`
- `deck_code.js`
- `deck_accounts.js`
- `deck_watch.js`
- `deck_chart.js`

A `GET /cdeck/` request for a name that is not on the list is not the static shell. The native window reads `frontendDist` and is not that allowlist. Opening the deck in a browser on Core and opening `cdeck.exe` are not the same set of pages. That split is still open.

`builds/cdeck/README.md` still describes serving `ui/` from Core as a proposal. The route above is in `cosmos_service.py` now. The README is not the route table. The allowlist is still not the whole UI, so the browser deck is not finished either.

## Header token strip

The strip is `#tokStrip`, painted by `renderTokStrip` in `ui/header.js`. The window math is the same fold as `meter_window` in `cosmos/cosmos_meter_window.py`. That Python module does not open the ledger, the meter file, or the wall clock. The strip does not either.

Rows are the `.fevent` nodes already in `#feed` (each node's `__ev`). They are whatever that page already holds. The strip does not re-read `authority.jsonl` and it does not call `GET /api/v1/spend`.

Counted event names are `SPEND_SETTLED`, `RUN_SETTLED`, and `RUN_UNPRICED`. These names are skipped and not summed: `BUDGET_SET`, `SPEND_RESERVED`, `SPEND_RELEASED`, `SPEND_DENIED`, `RUN_FAILED`, `CREDIT_PURCHASED`, `CREDIT_GRANTED`, `TOLL_ACCRUED`, `QUOTA_HIT`.

Two windows are painted: the current UTC day, and the seven UTC dates that end today (today plus the six days before it). A stamp exactly on midnight belongs to the day that starts then.

The strip folds on-page priced rows. It looks for a row that already has both a token field and a price field (`measured_usd`, `usd`, `cost`, or provenance, beside a token count). Without that pair it stays `UNMEASURED`. It does not invent `0`. An empty window is the string `UNMEASURED`. A count the row does not carry stays `UNMEASURED` for that window. A `0` the row actually carried stays `0`. Dollars sum only rows that carried a price. If none did, `usd` is `UNMEASURED`.

Cap is not an input. Core `settled_usd` is not an input. `cosmos_meter_window.py` does not read `settled_usd`. The spend panel's rail audit (`GET /api/v1/spend`, field `settled_usd`, and `cosmos_spend_meter.py`) is a different number. Do not add the strip to that total, and do not treat the strip as that total.

`builds/cdeck/tests/header_meter_fold.js` loads `meterWindow` and `renderTokStrip` out of `header.js`. It uses no browser and no Core. It is not one of the five probes below, and a pass there would not refresh them.

## What it reads

The deck is a dashboard over the live HTTP API. The panel matrix, the age chips, and the transport table are in `builds/cdeck/README.md` and `builds/cdeck/SPEC.md`. Those files are notes in the submodule. They are not a claim that every panel is measured, and they are not a claim that the deck is done. Where a number has no source, the UI is supposed to say `UNMEASURED` or `UNAVAILABLE`, not `0`.

Native-only reads go through `read_projection`. The allowlist is three names: `fleet`, `drive`, `registry`. The root is checked by sentinel content before the read. A browser cannot do that read. No root means no invented fleet.

Python binders next to the UI (`cosmos_fleet_panel.py`, `cosmos_spend_panel.py`, `cosmos_jukebox_panel.py`, `cosmos_nodemap_panel.py`, `cosmos_recents_panel.py`, `cosmos_local_get.py`) are the measurement those panels fold. Core dispatches fleet, nodemap, jukebox, and recents onto their `handle_get`. A panel Core has not composed is not an empty board. HTTP `501` with `kind` `UNMEASURED` stays that body.

`GET /api/v1/spend` is the measured rail read. `cosmos_spend_panel.py` can call `SpendGate` on a root you pass. That does not mean Core's HTTP spend route is the write, and it does not mean SpendGate is bound. It is not Token Center. Human-posted Claude / Grok pools stay in deck config. They are not measured COSMOS spend.

The bearer is an in-memory argument. This book does not contain it. Do not paste `live\config\api_token.txt` into a doc.

## Five browser probes

Five browser probes wrote a size map of the files directly in `ui/` and the suites that read those artifacts fail when the map is not the directory now on disk. A stale number is not evidence. The check is file name to size, not a hash, and it does not walk subfolders such as `planets/` or `skins/`. The check text says byte for byte. The comparison is the size map.

Against this tree, each of the five artifacts still names only `app.css`, `app.js`, `cdeck.webmanifest`, `index.html`, and `sw.js`. `ui/` now has 56 files at that level. The maps are not equal. Those suites still fail the stale check. This page did not re-run Chromium. The old JSON is not a measurement of the current pages. Do not edit the JSON so the check goes green, and do not weaken the check.

| Probe | Artifact | Suite that fails the stale check |
| --- | --- | --- |
| `builds/cdeck/feature_probe.py` | `FEATURE_PROBE.json` (`ui_files`) | `test_deck_features.py` |
| `builds/cdeck/follow_probe.py` | `FOLLOW_PROBE.json` (`ui_sizes`) | `test_follow_tail.py` |
| `builds/cdeck/live_tier_probe.py` | `LIVE_TIER_PROBE.json` (`ui_files`) | `test_live_tier.py` |
| `builds/cdeck/mobile_probe.py` | `MOBILE_PROBE.json` and `MOBILE_PROBE_DOWN.json` (`ui_files`) | `test_mobile_layout.py` |
| `builds/cdeck/pwa_probe.py` | `PWA_PROBE.json` (`ui_files`) | `test_pwa.py` |

Re-running the probe is how that suite gets a new artifact. This chapter does not claim that re-run has been done, and it does not claim those probes pass.

Those five probes are Chromium. They do not exercise the Tauri host. `events_probe.mjs` and `transport_probe.mjs` are separate Node scripts. They are not these five.

## Where to read next

- `builds/cdeck/README.md` — transports and the panel matrix, with the stale "serving is a proposal" sentence noted above.
- `builds/cdeck/SPEC.md` — the original brief. It is not the current allowlist.
- `builds/cdeck/PARITY_AUDIT.md` and `builds/cdeck/KDECK_BACKLOG.md` — earlier measurement notes. Not current evidence while the probes above are stale.
- `ui/header.js` — loader and token strip.
- `ui/deck_tabs.js` — pane rail.
- `cosmos/cosmos_service.py` — `/cdeck/` allowlist and the panel dispatch.
- `cosmos/cosmos_meter_window.py` — the UTC fold the strip copies.
- `cosmos/cosmos_cdeck_launch.py` — `cosmos.py deck`.

## Not claimed

- The deck is finished, integrated, or wishlist-complete.
- COSMOS is finished or fully tested.
- The header strip is Core settled spend. It does not sum `settled_usd`.
- The five browser probes describe the current `ui/` tree.
- The native exe, the Core allowlist, and the files `header.js` injects are one set.
