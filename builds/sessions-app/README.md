# sessions-app

**Sessions as its own app.** Product on COSMOS, not CORE. Same data the cDeck
Sessions tab renders — Core's `GET /api/v1/recents` — with its own shell, its own
port, and the `session-tools` verb suite as its engine.

Plan and compatibility notes: `docs/arch/SESSIONS_APP_ARCH.md`.

```
py -3.14 builds/sessions-app/sessions_app.py list
py -3.14 builds/sessions-app/sessions_app.py open cow-<sid>
py -3.14 builds/sessions-app/sessions_app.py verbs
py -3.14 builds/sessions-app/sessions_app.py verb scan --store <catalog-dir>
py -3.14 builds/sessions-app/sessions_app.py timeline --root V:\A\Ai\COSMOS\live
py -3.14 builds/sessions-app/sessions_app.py serve --root V:\A\Ai\COSMOS\live --store <catalog-dir> --port 8785
```

Shell: `http://127.0.0.1:8785/sessions/` — SESSIONS · VERBS · ROLLED TIMELINE.

## Additive, by construction

Nothing under `cosmos/` changes; `builds/cdeck` and `builds/session-tools/` are
untouched. Core is read over HTTP **server-side**, so the app needs no Core route
and no CORS header, and cDeck keeps rendering the identical projection. This app
writes nothing under the runtime root and appends nothing to the ledger.

## Surfaces

| Route | Is |
|---|---|
| `/sessions/` `app.css` `app.js` | the shell (exact-match allowlist, no bearer, loopback only) |
| `/api/sessions` | `sessions-app-list/1` — id-stable rows, legal counted not opened |
| `/api/sessions/open?id=` | `sessions-app-open/1` — one session, over Core |
| `/api/verbs` | the verb set with per-verb bind status |
| `/api/verbs/scan` | the one BOUND verb, against the store declared at `serve` |
| `/api/timeline` | `sessions-app-timeline/1` over the `rolled-event/1` feed |

## Typed states

`UNMEASURED` is `null`, never `0` — Core down, no feed, or a count Core did not
report. A measured empty feed *is* `0`. Legal rows are **counted, not opened**
(`omission.opened` is 0 by construction). A blank or duplicated row id is
`ID_UNSTABLE`; no id is ever minted from a `seq`. One malformed `rolled-event/1`
line refuses the whole timeline naming the line.

Canonical transcript stays `{id}.ctr.jsonl` + `{id}.ctr.decl.json` (sha-only),
owned by `builds/session-tools/`.

Verb bind status this slice: **scan BOUND**, the other seven DECLARED
(`VERB_NOT_BOUND`) — a route is not a proof.

Tests: `tests/test_sessions_app.py`
