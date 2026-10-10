# API

COSMOS is not finished. This page is not a completion claim. It lists HTTP routes that `cosmos/cosmos_service.py` actually branches on (`do_GET`, `do_POST`, and the allowlists those methods look up). It does not add routes, and it does not paste the handlers.

A path this file does not name is `404` `NOT_FOUND`. This file implements GET and POST only. There is no second public API beside this one.

The behavior word is the status that branch sends, or `UNMEASURED` when that is the JSON `kind` rather than an HTTP status:

- `200` — that branch sends HTTP 200 on the path described.
- `401` — bearer refusal.
- `501` — the handler sends 501.
- `UNMEASURED` — the body says nothing has been observed. An empty snapshot can still be HTTP 200.

Rows marked **test** are assertions already in the tree (`tests/test_orc_compose.py`, `tests/test_pilot_womb_http.py`). This page did not bind port 8770 and did not read the live ledger. Other numbers are what the handler is written to send, not a fresh capture from a running Core.

## How a path is matched

Static shells and `/kill` run before the bearer check. Later GET branches that compare `self.path` to a string do not strip the query. A `?` on those paths misses the branch. Branches that use `urlparse(...).path` keep the query. POST `/api/v1/kill`, `/control/resume`, `/spend`, `/voice`, `/command`, `/crucible`, `/jobs`, and `/makers` also compare `self.path` whole. Later POST branches parse the path.

`_ORC_UNMEASURED` is the 501 table at the bottom of both methods. A read that already returned does not fall through to it. Seats have no earlier branch, so they stay on that table. GET chamber and GET temporal call snapshot and return above it. POST chamber and POST temporal do not, so they stay 501.

## Bearer

After the shell and the kill routes, a failed `_authed` check is `401` `UNAUTHORIZED`. Loopback trust can let `127.0.0.1` through that gate with no bearer. The code default is guarded. That pass is not approval to grant.

`POST /api/v1/approvals/grant` and `POST /api/v1/approvals/deny` check the bearer again. No matching bearer is `401` `NO_BEARER`, including when the first gate already passed. **Test:** both files, no `Authorization` header, status 401, kind `NO_BEARER`, and not 200. A grant with no bearer is 401.

JSON bodies need `Content-Length`. Missing or bad length is `400`. Over the cap is `413`. That is the body gate, not a route.

## Shell

No bearer. Fixed allowlist. The request path is a dict key, not a filesystem join. A missing file is `404` `SHELL_FILE_MISSING`, not an empty page. These rows were not re-checked on disk here. Present file means the handler sends `200`.

| Method | Path | Behavior | What it is |
|---|---|---|---|
| GET | `/` | 200 | `mobile.html` |
| GET | `/m` | 200 | same mobile page |
| GET | `/mobile` | 200 | same mobile page |
| GET | `/dash` | 200 | desktop KDash `index.html` |
| GET | `/kdash_manifest.webmanifest` | 200 | manifest allowlist entry |
| GET | `/kdash_sw.js` | 200 | service worker at the root scope |
| GET | `/cosmos-voice.apk` | 200 | Android package on this port. No token in the file. |
| GET | `/cdeck` | 302 | redirect to `/cdeck/` |
| GET | `/cdeck/` | 200 | `builds/cdeck/ui/index.html` |
| GET | `/xtalk` | 302 | redirect to `/xtalk/` |
| GET | `/xtalk/` | 200 | `builds/xtalk/index.html` |

Each name in `_CDECK_UI_FILES` is `GET /cdeck/<name>` (200 if that file is on disk, else 404): `index.html`, `app.js`, `app.css`, `cdeck.webmanifest`, `sw.js`, `header.js`, `header.css`, `kdash_native.js`, `deck_more.html`, `deck_more.css`, `deck_tabs.js`, `model_rater.js`, `deck_profiles.js`, `deck_settings.js`, `deck_studio.js`, `deck_forge.js`, `deck_gitur.js`, `deck_xtalk.js`, `deck_orc.js`, `deck_pilot.js`, `deck_womb.js`, `gitur_launch.js`, `deck_backup.js`, `deck_session_kit.js`, `deck_sessions_page.js`, `deck_jukebox.js`, `deck_clock.js`, `deck_open.js`, `deck_tools.js`, `deck_spawn.js`, `deck_surfaces.js`, `deck_review.js`, `deck_voice.js`, `deck_runs.js`, `deck_system.js`, `deck_jobs.js`, `deck_home.js`, `deck_create.js`, `deck_audit.js`, `deck_nodemap.js`, `deck_fleet.js`, `deck_portfolio.js`, `deck_portfolio_store.js`, `deck_portfolio_stages.js`, `deck_portfolio_cost.js`, `deck_orders.js`, `deck_sfx.js`, `openwork.svg`, `skins/forge-engineroom.jpg`, `skins/crucible-chamber.jpg`, `skins/diligence-dealroom.jpg`, `skins/docket-archive.jpg`, `skins/ups-lab.jpg`, `skins/differentiator-clinic.jpg`, `skins/website-studio.jpg`, `planets/jupiter.mp3`, `planets/mars.mp3`, `planets/venus.mp3`, `planets/mercury.mp3`, `planets/saturn.mp3`, `planets/uranus.mp3`, `planets/neptune.mp3`.

`GET /xtalk/index.html`, `GET /xtalk/xtalk.js`, and `GET /xtalk/xtalk.css` are the same rule for the XTalk allowlist.

## Kill

No bearer. The switch only reduces capability (mic off, clear queue). If `kill_token.txt` is set, a wrong token is `403` `BAD_KILL_TOKEN`. A matching or absent token is `200`.

| Method | Path | Behavior | What it is |
|---|---|---|---|
| GET | `/kill` | 200 | optional `client_id` and `token` query |
| POST | `/api/v1/kill` | 200 | optional JSON `client_id` and `token`. Compared with `self.path`, so a query misses it. |

## GET `/api/v1`

Success on these branches is HTTP 200 unless the note says otherwise. Module errors on the same branch are often `400`. This is not a claim that every projection has data.

| Method | Path | Behavior | What it is |
|---|---|---|---|
| GET | `/api/v1/control` | 200 | pause / mic / queue flags for `client_id`. Not spend-gated. Control failure is 500. |
| GET | `/api/v1/status` | 200 | ready, root, tree id, ledger head. **Test** 200. Exact `self.path`. |
| GET | `/api/v1/audit` | 200 | `kernel.audit()`. Exact `self.path`. |
| GET | `/api/v1/jobs` | 200 | scheduler states. Exact `self.path`. |
| GET | `/api/v1/health` | 200 | `HealthBoard.run()`. Exact `self.path`. |
| GET | `/api/v1/spend` | 200 | spend audit. Does not change a cap. **Test** 200. Not a claim that the spend gate is bound. Exact `self.path`. |
| GET | `/api/v1/tools` | 200 | tool-contract report. Exact `self.path`. |
| GET | `/api/v1/tools_kit` | 200 | components and callables snapshot. Does not mutate. |
| GET | `/api/v1/voice_loop` | 200 | voice-loop status snapshot. Does not POST `/voice`. |
| GET | `/api/v1/events` | 200 | prefix match. `since_seq` and optional `tail` (1..100). Bad cursor is 400. |
| GET | `/api/v1/rails` | 200 | registry matrix. No registry is 503 `REGISTRY_NOT_COMPOSED`. Same branch as nodes. Exact `self.path`. |
| GET | `/api/v1/nodes` | 200 | same handler as `/rails`. |
| GET | `/api/v1/surfaces` | 200 | surfaces report. No map is 503 `SURFACES_NOT_COMPOSED`. |
| GET | `/api/v1/surfaces_kit` | 200 | surfaces kit snapshot. Does not mutate. |
| GET | `/api/v1/fleet` | 200 | cDeck fleet panel code. Import or call failure in this handler is 503. |
| GET | `/api/v1/nodemap` | 200 | cDeck nodemap panel. On panel 200, empty disk rows can be overlaid from `kernel.registry`. Failure is 503. |
| GET | `/api/v1/jukebox` | 200 | cDeck jukebox panel code, or 503. |
| GET | `/api/v1/recents` | 200 | cDeck recents panel. Query is passed through. Failure is 503. |
| GET | `/api/v1/makers` | 200 | exact path only. Other `/api/v1/makers...` is 404. No map is 503. A known empty kind is 200 with `makers: []` (UNMEASURED-as-empty). Bad filter is 400. |
| GET | `/api/v1/gitur` | 200 | git projection. `GiturError` is 400. |
| GET | `/api/v1/crew` | 200 | crew roster snapshot. |
| GET | `/api/v1/cred` | 200 | key LEDs. The handler does not echo the secret. |
| GET | `/api/v1/agents` | 200 | agent presence snapshot. |
| GET | `/api/v1/mcp` | 200 | named MCP servers. Does not spawn. |
| GET | `/api/v1/research_call` | 200 | research envelope snapshot. Does not fetch. |
| GET | `/api/v1/studio` | 200 | studio snapshot. Does not start MOTIF. |
| GET | `/api/v1/profiles` | 200 | profile snapshot. `?profile=` optional. Profile error is 400. |
| GET | `/api/v1/backup` | 200 | backup fold. Does not run a backup. |
| GET | `/api/v1/session_kit` | 200 | session kit snapshot. Does not fire a resession. |
| GET | `/api/v1/session_tools` | 200 | session-tools snapshot. Does not mutate. |
| GET | `/api/v1/orc` | 200 | BootUP inspect. Does not spawn OpenWork. **Test** 200. |
| GET | `/api/v1/pilot` | 200 | pilot transcript snapshot. Bad tail is 400. **Test** 200 after turns exist (`kind` MEASURED). |
| GET | `/api/v1/xtalk` | 200 | xtalk fold. Missing file is UNMEASURED in the body. Bad query is 400. |
| GET | `/api/v1/runs_ops` | 200 | runs ops fold. Does not mutate. |
| GET | `/api/v1/review` | 200 | review fold. `window` query. Does not mutate. |
| GET | `/api/v1/work_orders` | 200 | work-order list. `id`, `state`, `limit`. Order error is 400. |
| GET | `/api/v1/ccr/duty` | 200 | duty report. No merge. |
| GET | `/api/v1/stations` | 200 | stations snapshot. |
| GET | `/api/v1/head` | 200 | head record. |
| GET | `/api/v1/openrouter/routing` | 200 | saved routing priority. |
| GET | `/api/v1/model_rater/roles` | 200 | named roles. |
| GET | `/api/v1/model_rater` | 200 | catalog snapshot. Rater error is 400. |
| GET | `/api/v1/porosity` | 200 | porosity snapshot. The module comment says UNMEASURED until a pair is observed. The handler still sends 200. |
| GET | `/api/v1/womb/seat` | 200 | 200 only when the record `kind` is MEASURED. Otherwise 404 with that record (UNMEASURED if no pair). Bad `budget_out` is 400. **Test** status is 200 or 404, and the schema is not the board. |
| GET | `/api/v1/womb/board` | 200 | board tail. Missing file is HTTP 200 and **test** `kind` UNMEASURED. Bad tail is 400. |
| GET | `/api/v1/usage` | 200 | usage fold. The module comment says UNMEASURED until a dispatch is recorded. |
| GET | `/api/v1/cvm/pull` | 200 | needs `client_id`, else 400. Projection. Does not append the ledger. Identity errors are 400; other `CvmError` is 500. |
| GET | `/api/v1/recall` | 200 | search, or `state_sha` when the query is empty. Does not call `refresh()`. **Test:** `q=hello` is 200, `kind` UNMEASURED, `results` null, not `RECALL_NOT_COMPOSED`. Bad `limit` is 400. |
| GET | `/api/v1/skills` | 200 | registry list. **Test** 200, `kind` MEASURED, not the 501 table. |
| GET | `/api/v1/sandbox` | 200 | sandbox snapshot. **Test** 200, modal `NOT_COMPOSED`. Does not configure a remote backend. |
| GET | `/api/v1/delegate` | 200 | delegation snapshot. **Test** 200. Does not spawn. |
| GET | `/api/v1/approvals/pending` | 200 | pending list. **Test** 200. POST of this path is 501 (below). |
| GET | `/api/v1/chamber` | 200 | snapshot for `?room=` (default `Cm`). Does not call `join()`. **Test:** `Cm` and `plumbing` are 200 with `kind` UNMEASURED (empty presence, posts, tickets). `room=legal` is 400 `STREAM_REFUSED`. Not 501. |
| GET | `/api/v1/temporal` | 200 | temporal snapshot. Optional `?at=` must be a finite number, else 400 `BAD_AT`. **Test:** no `at`, and `at=1500`, are 200 with `kind` UNMEASURED. Not 501. |

## GET that stays 501

These GET paths are only on `_ORC_UNMEASURED`. If `_authed` fails first, the client sees 401 instead.

| Method | Path | Behavior | What it is |
|---|---|---|---|
| GET | `/api/v1/seats` | 501 | `kind` UNMEASURED, error `SEATS_NOT_COMPOSED`. No seats module. **Test** (`?stream=Cm`) 501. Seats stay 501. |
| GET | `/api/v1/approvals/grant` | 501 | no GET decide handler. Stub `APPROVALS_NOT_COMPOSED`. |
| GET | `/api/v1/approvals/deny` | 501 | same stub. |

## POST `/api/v1`

| Method | Path | Behavior | What it is |
|---|---|---|---|
| POST | `/api/v1/control/resume` | 200 | clears kill and pause. Does not reset the day spend lane. Bad JSON is 400. |
| POST | `/api/v1/spend` | 200 | cap or breaker change via spend admin. The module comment in this file: a widen without literal `allow_widen: true` is 409 `WIDEN_REQUIRES_CONFIRM`. Not a claim that the spend gate is bound. |
| POST | `/api/v1/voice` | 200 | spoken turn. Several refusals are also HTTP 200 with `refused` set (control, duplicate, spend). That 200 is not proof a model ran. Oversized text is 400. Voice refine is not claimed done. |
| POST | `/api/v1/command` | 200 | text in, commander result out. Bad text is 400. |
| POST | `/api/v1/crucible` | 501 | 501 `CRUCIBLE_NOT_RUNNABLE` when no critic dispatchers are composed. When they are, a queued round is 201. Empty source is 400. This 501 is not the seats table. |
| POST | `/api/v1/research_call` | 200 | file or ingest. Does not fetch. Bad body is 400. |
| POST | `/api/v1/studio` | 200 | save studio config. Does not start MOTIF. |
| POST | `/api/v1/usage` | 200 | generation fetch. Handler sends 200 only when the record says `ok`, else 400. |
| POST | `/api/v1/porosity` | 200 | pair, trial, or recommend. Bad body is 400. |
| POST | `/api/v1/profiles/bg` | 200 | background profile step. Bad body is 400. |
| POST | `/api/v1/profiles` | 200 | save a profile skin. |
| POST | `/api/v1/orc` | 200 | session start for `{stream}`. Does not spawn OpenWork. **Test:** stream `nope` is 400 `BAD_STREAM`. |
| POST | `/api/v1/xtalk` | 200 | append one transport-B message. Helper `NOT_COMPOSED` is 501. Other helper errors are 400. |
| POST | `/api/v1/surfaces` | 200 | catalog add or remove. Does not invent reachability. |
| POST | `/api/v1/backup` | 200 | `surface_test`, `search`, `restore`, `generate`. Restore and generate refuse without bak and dest. Not a silent full-tree backup. |
| POST | `/api/v1/session_tools` | 200 | session verbs. Bad body is 400. |
| POST | `/api/v1/voice_loop` | 200 | `new_sop` or `drop`. Does not run the agent. |
| POST | `/api/v1/session_kit` | 200 | save kit config. Does not fire a resession. |
| POST | `/api/v1/work_orders/picked` | 201 | first `order_id` appends and returns 201. The same id again is 200. Missing id is 400. |
| POST | `/api/v1/jobs` | 201 | submit `{command, priority}`. Bad body is 400. Exact `self.path`. |
| POST | `/api/v1/makers` | 201 | add one maker. No map is 503. Unknown or bad body is 400. Exact `self.path`. |
| POST | `/api/v1/cvm/snapshot` | 200 | land a phone snapshot. Does not append the ledger. |
| POST | `/api/v1/cvm/push` | 200 | phone turn, then stamps pull `audio_owner=desktop`. Does not append the ledger. |
| POST | `/api/v1/stations` | 200 | wish, seat, board, release, floors, rotation, audit. Station error is 400. |
| POST | `/api/v1/openrouter/routing` | 200 | set priority. Bad value is 400. |
| POST | `/api/v1/head` | 200 | set head. Bad value is 400. |
| POST | `/api/v1/model_rater/refresh` | 200 | pull catalog. `NO_KEY` or `AUTH_REQUIRED` is 401. `UNREACHABLE` is 503. Other rater errors are 400. |
| POST | `/api/v1/model_rater/seat` | 200 | assign, add, or remove a rater seat. Same error map as refresh. Not the Core spend gate. |
| POST | `/api/v1/model_rater/cap` | 200 | per-model rater cap. Same error map. |
| POST | `/api/v1/model_rater/porosity` | 200 | record one rater sample. Same error map. |
| POST | `/api/v1/model_rater/policy` | 200 | favored and banned models. Same error map. |
| POST | `/api/v1/model_rater/estimate` | 200 | token times rate card. Same error map. |
| POST | `/api/v1/model_rater/job_estimate` | 200 | save or reset a job estimate. Same error map. |
| POST | `/api/v1/cred` | 200 | set, delete, grab, custom, or a fold. Does not echo the secret. Cred error is 400. |
| POST | `/api/v1/approvals/grant` | 401 | no matching bearer is 401 `NO_BEARER`. **Test.** With a bearer, a pending grant is 200; unknown id is 403 `NO_REQUEST`; an already-decided id is 403. A gate error is not HTTP 200. |
| POST | `/api/v1/approvals/deny` | 401 | same bearer rule. **Test** 401 with no bearer. With a bearer, a pending deny is 200; unknown id is 403. |
| POST | `/api/v1/pilot` | 200 | one captain turn. The handler forces `role` to captain. `PEN_REFUSED` is 403. This branch is after the 501 table, so pilot is not a stub. **Test** 200 `ACCEPTED`. |

## POST that stays 501

`_orc_unmeasured` sends 501, `kind` UNMEASURED, and the error name below. GET of chamber, temporal, recall, skills, sandbox, delegate, and approvals pending is the 200 table above. POST of those paths is this table. Seats are here for both methods.

| Method | Path | Behavior | Error on the 501 body |
|---|---|---|---|
| POST | `/api/v1/seats` | 501 | `SEATS_NOT_COMPOSED`. No seats module. Same table as GET. |
| POST | `/api/v1/approvals/pending` | 501 | `APPROVALS_NOT_COMPOSED`. Pending is a GET. |
| POST | `/api/v1/chamber` | 501 | `CHAMBER_NOT_COMPOSED`. **Test** 501, `kind` UNMEASURED. `join` appends the ledger and is not this route. |
| POST | `/api/v1/temporal` | 501 | `TEMPORAL_NOT_COMPOSED`. **Test** 501, `kind` UNMEASURED. `assert_fact` and `invalidate` are not this route. |
| POST | `/api/v1/skills` | 501 | `SKILLS_NOT_COMPOSED`. accept and reject are not this route. |
| POST | `/api/v1/sandbox` | 501 | `SANDBOX_NOT_COMPOSED`. |
| POST | `/api/v1/delegate` | 501 | `DELEGATE_NOT_COMPOSED`. Does not spawn. |
| POST | `/api/v1/recall` | 501 | `RECALL_NOT_COMPOSED`. `refresh` is not this route. |

Anything else named in that dict is already listed. A POST path that is neither a handler nor that dict is 404.
