# xtalk

## What it is

The agent stream Core already serves. One hash-chained JSONL (`schema` `cosmos-msg/1` on each record, fold `cosmos-xtalk/1`). GET peeks. POST Transport B appends the Core-local stream. Transport A is a typed hole: Core does not inject into a harness. Commit `9ed8d97e`. A later local grade of `cosmos\cosmos_xtalk.py` is in `C:\Users\Papa\AppData\Local\Temp\c4-h10-result.md`.

## Where it lives

- `cosmos\cosmos_xtalk.py` — snapshot, send, chain check, CLI.
- `builds\xtalk\` — static page (`index.html`, `xtalk.js`, `xtalk.css`). Core serves it at `/xtalk/` on the same origin as the API (port 8770). No iframe. Empty reads as UNMEASURED.
- `builds\xtalk-plugin\` — host tools `xtalk.get`, `xtalk.send`, `xtalk.roles`. Same Core routes. No second writer.
- cDeck tab: `builds\cdeck\ui\deck_xtalk.js` and `#panel-xtalk`. The page does not require cDeck.
- Local stream: `live/state/xtalk.jsonl` plus `roles.json`, unless `live/config/xtalk.json` names another stream. OpenWork bind reads `V:\OpenWork\XTalk\live\state\xtalk.jsonl` and does not write it. Pointer `V:\Streams\XTalk\BUxt.toml` is not this writer.

## Entry points

- `py -3.14 cosmos\cosmos_xtalk.py --selftest`
- `py -3.14 cosmos\cosmos_xtalk.py [--root LIVE] [--bind openwork] send|inbox|verify|roles|get`
- `py -3.14 cosmos\cosmos.py xtalk` forwards to the same CLI and does not boot a Kernel.
- HTTP: `GET /api/v1/xtalk` and `POST /api/v1/xtalk` in `cosmos_service.py`.
- `snapshot` folds tail (1..200), optional role inbox, optional `verify`. `send` appends one Transport B line under a lock. A repeated nonce in the last 100 lines returns `duplicate` and does not append. Body text is cut at 8000 characters.

Fence: a role with owner `server` or `none`, or not alive, is Transport A. A live owner is Transport B. The roles fold returns harness, owner, alive, transport, and reason. It does not echo session ids.

## What it refuses

- GET never creates `xtalk.jsonl` and never advances a cursor. A missing file is `UNMEASURED`, not an empty invention.
- POST with `bind` set is `BIND_READONLY`. The OpenWork stream is not writable from here.
- Missing `from`, `to`, or `body` is `BAD_MSG`. An unknown role is `BAD_ROLE`, not a fake inject.
- Transport A without `inject` is `DRY_RUN` and does not append. `inject` true is `NOT_COMPOSED` (the module documents that HTTP face as 501). Inject stays in the OpenWork `cosmos_msg.py` CLI.
- A bad tail is `BAD_TAIL`. A stuck stream lock is `LOCK`. A missing paths object for the local stream is `NO_PATHS`.

## What it is not

Not a second ledger, not OpenWork, not a harness runner, not cDeck. Chain verify reports problems; it does not rewrite a broken line. The plugin does not store a bearer of its own; the host env supplies `COSMOS_CORE_URL` and the API token.

## Grade

Commit `9ed8d97e` is the landed pin. A later local grade, `C:\Users\Papa\AppData\Local\Temp\c4-h10-result.md`, reports py_compile 0, ruff 0, mypy 0, and pytest 4 passed on `tests\test_xtalk.py`. `node --check` on `builds\xtalk\xtalk.js` exited 0. This note did not re-run those commands. A `null` line stays in the chain walk. A broken tail refuses append with `CHAIN`, and that snapshot head is `UNMEASURED`. A non-object role row is `BAD_ROLE`. The page no longer replaces the log with `innerHTML`, and a `DRY_RUN` is a notice, not a failed read. That grade is not a claim that the page is finished.
