# kDash

This page is one chapter of the developer book. It does not mean COSMOS is
finished, fully tested, or a completed dashboard. kDash is a static browser
client of the Core HTTP API. It does not run Core, it does not hold the pen,
and it is not cDeck.

## Two pages, no build

The client is two self-contained HTML files under `kdash\`. CSS and script
are in the files. There is no bundler, no package install, and no CDN. A
remote script or stylesheet on the desktop page is `CDN_FORBIDDEN`
(`cosmos\cosmos_kdash.py`).

| File | What it is |
| --- | --- |
| `kdash\index.html` | Desktop page. Title `KDash — COSMOS v2`. |
| `kdash\mobile.html` | Phone page. Title `KDash Mobile — COSMOS`. |

`cosmos\cosmos_kdash.py` is not a second UI. It is the CREATE-panel contract
for the desktop file: known kinds, card fields, and a disk read of
`kdash\index.html`. An unreadable page is `BAD_PAGE`.

cDeck is a different shell. Its pages live under `builds\cdeck\ui` and Core
serves that tree at `/cdeck/`. A deck script named `kdash_native.js` is deck
code. It is not `kdash\index.html` and it is not `kdash\mobile.html`. Do not
treat a cDeck tab as this client.

## How Core serves the shell

`cosmos\cosmos_service.py` keeps an exact-match allowlist. The request path
is a dict key. It is never joined onto a filesystem path. The shell is
served without a bearer because the files contain no ledger rows and no
token. Every `/api/v1/` route still requires the bearer.

| Route | File |
| --- | --- |
| `/`, `/m`, `/mobile` | `mobile.html` |
| `/dash` | `index.html` |
| `/kdash_manifest.webmanifest` | `manifest.webmanifest` |
| `/kdash_sw.js` | `sw.js` |

The same resolver looks for `kdash\<name>` beside the package, then one
directory up, then a flat `kdash_<name>` spike name. Missing file is a 404.
It is not invented.

`serve` prints a banner that points at `kdash\index.html`. That is the
desktop file. The phone default on the HTTP port is `/` (mobile). The
desktop page's API field starts at `http://127.0.0.1:8770`. The bearer
field starts empty. This book does not contain a token. Do not paste
`config\api_token.txt` into the page source, a doc, or a ticket.

The manifest names a phone install: start URL `/m`, scope `/`, standalone,
portrait. Icons are inline. They are not a separate art pipeline.

`kdash\sw.js` caches the app shell only (`/m`, the manifest route, and the
worker). Cache name in the file is `cosmos-shell-v4`. It does not cache
`/api/`. Non-GET requests are not intercepted. A cached API body would be
the frozen-dashboard scar: numbers with no honest age. Mobile registers
`/kdash_sw.js` and ignores a missing `serviceWorker` so the page still
opens.

The allowlist also names `kdash\cosmos-voice.apk` at `/cosmos-voice.apk`.
That binary is not these two HTML pages. This chapter does not treat it as
a finished phone app.

## Token and refresh

Both pages keep the API base and the bearer in a page-memory object for
that load. The desktop footer says settings live in JS memory only. The
mobile page does not write the token to `localStorage`, `sessionStorage`,
cookies, or the URL. Close the tab and the paste is gone. A 401 is the
sentence `UNAUTHORIZED — paste a bearer`. That is not "API unreachable."

The desktop pause button pauses **this page's poll timer**. It is not Core
`PAUSE.flag`. Resume schedules the next snapshot and the event poll
immediately.

Desktop poll periods, from the page:

| Panel | Period |
| --- | --- |
| health, spend, status, jobs, create | 10s |
| rails, audit, tools | 60s |
| live events | 5s |

A panel is stale at three times **its** interval, not a single fixed 30s.
GET polls time out at 8s. `POST /api/v1/voice` uses 70s so the client does
not abort that call on the short GET budget. The mic is a client of that
route. It is not a claim that voice is finished. On the phone page a speech
transcript is shown and placed in the box. It is not sent until the
operator presses SEND.

## What each page asks Core

The pages are clients. They render what the API returns. They are not the
ledger, the spend authority, or the job runner.

Desktop panels and the reads they poll:

| Panel | Route |
| --- | --- |
| HEALTH | `GET /api/v1/health` |
| SPEND | `GET /api/v1/spend` |
| STATUS | `GET /api/v1/status` |
| JOBS | `GET /api/v1/jobs` |
| RAILS MATRIX | `GET /api/v1/rails` |
| AUDIT | `GET /api/v1/audit` |
| TOOLS | `GET /api/v1/tools` |
| CREATE | `GET /api/v1/makers?kind=...` |
| LIVE EVENTS | `GET /api/v1/events?since_seq=` |

The command bar posts `{text}` to `POST /api/v1/command`. The labeled
shortcuts are `status`, `audit`, `jobs`, and `help`. The console keeps a
short in-page list of those replies. It is not a second ledger.

CREATE kinds are `AGENT`, `TOOL`, `CONNECTOR`, and `SKILL`. An unknown kind
refuses in `cosmos_kdash.py` as `UNKNOWN_KIND` instead of looking like an
empty catalog. Cards list where that kind can be made. A maker missing
required card fields is `BAD_ENTRY`.

SPEND can post a cap to `POST /api/v1/spend`. The page reports the write
only after it re-reads `GET /api/v1/spend` and the new cap is what came
back. A raise the server answers as `409` `WIDEN_REQUIRES_CONFIRM` is not
applied on the first push. `allow_widen` is a JSON boolean, not the string
`"true"`. If the server has no such POST, the page says the live gate is
unchanged. The page does not decide the budget. Painting a spend panel is
not a claim that SpendGate is a finished multi-rail desk.

The event strip follows `since_seq`. It is a tail of the append-only
ledger, not a rewrite of it. The feed on the page is a view.

Mobile is the smaller client. It connects, sends a command, and shows
STATUS, EVENTS, JOBS, HEALTH, and SPEND HEADROOM. It uses the same status,
jobs, health, spend, events, and command routes. It does not carry the
desktop rails, audit, tools, or CREATE panels.

## What this is not

kDash does not install a runtime root, write the ledger, or take
`CCR.lease`. Opening the HTML file does not start `serve`. A green panel
is a reading of whatever that API returned at that poll. It is not a
runtime-binding proof that COSMOS is done.
