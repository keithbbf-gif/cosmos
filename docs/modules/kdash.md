# kDash

## What it is

The files under `kdash\` that this note read: `index.html`, `mobile.html`, and `sw.js`. Each one is a static file on disk. None of them is a server template. This page lists the `/api/` strings in those three files. It does not say Core implements them, and it does not say COSMOS is finished.

kDash and cDeck are separate apps. This note does not join them.

## Where it lives

- `kdash\index.html` — static HTML (`<!DOCTYPE html>`). Title `KDash — COSMOS v2`. Style and script are inline. No service-worker registration in this file.
- `kdash\mobile.html` — static HTML. Its header says it is one self-contained file: no CDN, no external script, style, or font. It links `/kdash_manifest.webmanifest` and registers `/kdash_sw.js`. Those two paths are not `/api/` paths.
- `kdash\sw.js` — static JavaScript service worker, not an HTML page. Cache name `cosmos-shell-v4`. The shell allowlist is `/m`, `/kdash_manifest.webmanifest`, and `/kdash_sw.js`. The file says that allowlist has no `/api/` path.

Both HTML pages build a request as the operator base plus the path, with `Authorization: Bearer` when a token is in memory, and `cache: "no-store"`. The token is not written to storage by these pages. This note did not open a token file.

## Paths that are fetched

`index.html` (static HTML). `apiGet` is GET. `apiPost` is POST.

| Path string | Method in this file |
|---|---|
| `/api/v1/health` | GET (`refreshAll`) |
| `/api/v1/spend` | GET (`refreshAll`, and the re-read after a push) |
| `/api/v1/status` | GET |
| `/api/v1/jobs` | GET |
| `/api/v1/rails` | GET |
| `/api/v1/audit` | GET |
| `/api/v1/tools` | GET |
| `/api/v1/makers?kind=` | GET. The kind is appended in the client (`AGENT`, `TOOL`, `CONNECTOR`, `SKILL`). |
| `/api/v1/events?since_seq=` | GET. `lastSeq` is appended. |
| `/api/v1/command` | POST. Body is `{text}`. The command box and the mic both go here. The mic only fills the box. |
| `/api/v1/spend` | POST. Body is `{rail, cap_usd, client_id}` and, only on a confirming push, `allow_widen: true`. |

`mobile.html` (static HTML).

| Path string | Method in this file |
|---|---|
| `/api/v1/status` | GET |
| `/api/v1/jobs` | GET |
| `/api/v1/health` | GET |
| `/api/v1/spend` | GET, including the re-read after a push |
| `/api/v1/events?since_seq=` | GET. `lastSeq` is appended. |
| `/api/v1/voice` | POST. Body is `{transcript, mode:"voice"}` plus `session_id` and `confirm_id` when the page already holds them. |
| `/api/v1/spend` | POST. Same cap body shape as the desktop page (`client_id` is set in this file too). |

`sw.js` does not fetch an API path. On GET, if `pathname` starts with `/api/`, the worker returns and does not cache. Non-GET is not intercepted.

## Strings that are not fetches

These `/api/` strings are in the files. They are not `apiGet`, `apiPost`, or `apiCall` targets.

- `index.html`: `/api/v1/voice` is only the 70s timeout branch (`path === "/api/v1/voice"`) and a comment. This file does not call that path. The mic does not post it.
- `mobile.html` header comment: `POST /api/v1/command`. The send function does not call it. Send posts `/api/v1/voice`. The same header comment also names the GETs that the page does call, and `GET /api/v1/events?since_seq=N`.
- `mobile.html`: `/api/v1/*` in the service-worker comment (do not cache). `/api/v1/voice` is also named in the timeout comment and the session comment, and that path is a real POST in this file.
- `sw.js` comments: anything under `/api/`, `/api/v1/*`, and `POST /api/v1/command` as an example of a non-GET. The command path is not requested here.

The spend error text in both HTML files says `GET /spend`. The fetch path beside that text is `/api/v1/spend`. `/spend` alone is not an `/api/` string.

## Not in these three files

No other `/api/` string is in `index.html`, `mobile.html`, or `sw.js`.

Not in `mobile.html` or `sw.js`: `/api/v1/makers`, `/api/v1/rails`, `/api/v1/audit`, `/api/v1/tools`. Those four are only in `index.html`, as GETs.

Not a fetch in any of the three: `/api/v1/command` is fetched only from `index.html`. `mobile.html` and `sw.js` mention it in comments.

Not a fetch in `index.html` or `sw.js`: `/api/v1/voice` is fetched only from `mobile.html`. `index.html` only compares that path for the timeout. `sw.js` does not name it.

Anything else (seats, recall, skills, chamber, temporal, xtalk, or a cDeck route) was not in these three files. This note does not add it.

## What it is not

Not cDeck. Not a second service. Not a claim that the routes above answer, and not a claim that COSMOS is finished. `sw.js` is not a page. No HTML was edited for this note.
