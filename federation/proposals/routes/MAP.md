# Routes

The table in `routes.py` is the day-one route proposal. It does not change Core.

## What was read

`CONTRACT.md` slot `routes`, `README.md`, and `ROUTE_PAGE`, `ROUTE_SETUP`, and `ROUTE_CHAT` in `cosmos_federation/product.py`. The live handlers are `do_GET`, `_do_GET`, and `do_POST` in `V:\A\Ai\COSMOS\cosmos\cosmos_service.py`, plus the allowlists those methods look up: `_STATIC_ROUTES`, `_CDECK_ROUTES`, `_XTALK_ROUTES`, `_CDECK_PANEL_MOD`, and `_ORC_UNMEASURED`. The file has no `do_PUT`, `do_DELETE`, `do_PATCH`, or `do_HEAD`. The strings `/dayone`, `/api/v1/dayone/setup`, and `/api/v1/dayone/chat` do not appear in that file.

## What is already true

Core serves a bearer-free static shell. `GET /` , `GET /m`, and `GET /mobile` are `mobile.html`. `GET /dash` is kdash `index.html`, which is telemetry, not a first-run wizard. `GET /cdeck` redirects to `GET /cdeck/`. `GET /xtalk` redirects to `GET /xtalk/`. `GET /kill` and `POST /api/v1/kill` are the off switch and do not require the bearer. Bearer reads include `GET /api/v1/status`, `GET /api/v1/health`, `GET /api/v1/spend`, and `GET /api/v1/agents` (`agents_snapshot`). `POST /api/v1/spend` changes caps. `POST /api/v1/control/resume` clears kill and pause and does not reset the day spend lane. Paths in `_ORC_UNMEASURED` answer 501 from both `do_GET` and `do_POST`. A path that both handlers name is two rows. cDeck and XTalk file routes are built as `/cdeck/` plus a filename and `/xtalk/` plus a filename. Those full paths are not exact strings, so the table does not invent them. It does list the exact roots `/cdeck/` and `/xtalk/`.

## What this proposal adds

Three `DAY_ONE` rows, using the product constants:

- `GET /dayone` is the chat page on `127.0.0.1`.
- `POST /api/v1/dayone/setup` redeems the one-time loopback nonce.
- `POST /api/v1/dayone/chat` is the live turn.

The chat window and the wizard need this route and Core does not have it yet. Every `DAY_ONE` `why` is that sentence. No `EXISTS` row uses those paths.

## Refusal codes

`table()` returns the frozen tuple. Construction and the duplicate check fail closed.

- `BOUND` — method, path, phase, or why is empty, too long, or not text.
- `METHOD` — the method is not `GET` or `POST`.
- `PHASE` — the phase is not `EXISTS` or `DAY_ONE`.
- `PATH` — the path is not one absolute path with no query, space, or parent segment.
- `ROUTE` — a duplicate method and path, a day-one path marked `EXISTS`, an unknown day-one path, a day-one why that is not the gap sentence, or a missing day-one row.
- `SECRET` — method, path, or why matches a secret shape. The table stores no key material.

## How CCr lands it later

Add the three branches on the loopback handler. Serve `GET /dayone` as a fixed page with no bearer and no model key in the body, in the same family as the static shell. `POST /api/v1/dayone/setup` stays loopback-only, redeems one nonce, and sets an httpOnly cookie. `POST /api/v1/dayone/chat` is the capped turn on `openrouter` or `xai`. Leave `GET /cdeck`, `GET /api/v1/agents`, and the kdash shell in place. The day-one window is not the cDeck Tauri shell and it is not `kdash/index.html`.
