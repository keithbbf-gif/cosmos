# Core

Working tree on main `501fdee25a581648ee0ddb096bdafa70a2325a71`. The routes below are `cosmos/cosmos_service.py` as it sits. Not a new commit.

## What it is

COSMOS Core is the one resident service: the versioned HTTP API, the scheduler surface, the spend gate, and the single writer of the append-only hash-chained service-signed JSONL ledger. Other state is a rebuildable projection. A corrupt ledger segment refuses. It is not repaired in place.

The path root is one configured root whose `.cosmos-root.json` content says `system=COSMOS` and whose tree id matches the install record when one is supplied. Identity is that sentinel. It is not a drive letter, not a parent walk, and not "the directory exists."

The one pen is `CCR.lease` (`cosmos_ccr.py`). A second acquire refuses. No lease means not CCr. The lease file is a projection. It does not replace the authority ledger.

`cosmos/cosmos_service.py` is that API. Default listen port is 8770 (`cosmos.py serve --port`). Stdlib only. KDash, voice, and other clients share this one surface.

Modules this page covers, all under `cosmos/`:

- `cosmos_resession.py` — Layer B satellite. Closes through the CLI kernel and arms the resume gate. `plan_resession` returns `execute` false for an installed door. Claude is `ANTHROPIC_OFF`. Spawn still does not run. It does not restart Core.
- `cosmos_session_procedures.py` — TidyUP, then TidyUP2, then one BU file. Ask ladder at 75, 80, and 85 percent. A live Grok session closes at 190000 input tokens. The clock does not close unless `engage=True`.
- `cosmos_recall.py` — FTS projection of conversation turns. Owner-scoped. A missing index is `UNMEASURED`. A ledger shorter than the checkpoint is `TRUNCATED`. `refresh()` builds the index. GET does not call it and does not mkdir.
- `cosmos_nlcron.py` — maps a cadence phrase onto schtasks, a detached daemon, or on-logon. Parser only.
- `cosmos_skills.py` — an agent proposes `SKILL.md`. Only CCr `accept()` activates it, and only with the pen. A tampered active file is `TAMPERED`. `list()` is names and descriptions from the ledger fold. It must not mkdir. `propose` and `accept` create directories. GET does not call them.
- `cosmos_approval.py` — fail-closed action gate. No off switch. `HARDLINE` never moves. Grants are single-use and bound to the exact action. No self-approval.
- `cosmos_delegate.py` — child jobs with depth, concurrency, and an iteration budget the caller cannot raise. Report, never retry. `snapshot()` does not mkdir and does not re-run a stale child.
- `cosmos_porosity.py` — per-model hole size and pair orthogonality. JSONL is the observation log. SQLite rebuilds. Scores are not invented.
- `cosmos_packet.py` — tool-output hash plus preview. Bytes go in the existing `state/cas` store. There is no `cosmos_packets.py`.
- `cosmos_stagehand_rail.py` — DOM adapter under `playwright-dom`. It does not replace that gate and it does not attach as a second Core.
- `cosmos_sandbox.py` — attempt workspace under a Job Object by default. Daytona and E2B are transports. Modal is named, not composed. Not a scheduler. `snapshot()` does not mkdir and does not spawn.
- `cosmos_action_chain.py` — action hash chain. Creator, reviewer, and approver must be three different principals.
- `cosmos_spawn.py` — fills Role, Wrapper, Skills, Tools, and Params before a work-order argv. A missing layer is not skipped.
- `cosmos_chamber.py` — room projection of `CHAMBER_*` events. `snapshot` is the read. `join` appends. Deck rooms are Cm, plumbing, physics, and chapter.
- `cosmos_temporal_fold.py` — facts with `valid_at` / `invalid_at`. `snapshot` is the read. `assert_fact` and `invalidate` append. Invalidate is not a delete. There is no `cosmos_temporal.py`.

`GET /api/v1/recall` calls that read: `search` when `q` or `query` is set, otherwise `state_sha`. A bad `limit` is 400 `BAD_LIMIT`. A missing index stays the module's `UNMEASURED`. The read does not mkdir.

`GET /api/v1/skills` calls `SkillRegistry.list` only. The body is `kind: MEASURED` plus the rows, including an empty list. `accept` and `reject` stay off the route. The list must not mkdir.

`GET /api/v1/sandbox` calls `snapshot`. If `modal` is named and not composed, the body sets `modal` to `NOT_COMPOSED`. It does not write a backend config and does not spawn.

`GET /api/v1/delegate` calls `Delegation.snapshot`. It does not spawn.

`GET /api/v1/approvals/pending` calls `ApprovalGate.pending`. GET does not mkdir. `POST /api/v1/approvals/grant` and `/deny` call `grant` and `deny` after the bearer matches. No bearer is 401 `NO_BEARER`. A gate error is JSON, never HTTP 200. The approver is the body string. An unknown id is the gate's refusal.

`GET /api/v1/chamber` calls `snapshot` for `?room=` (default Cm). `join()` is not called. A room off the deck is 400 `STREAM_REFUSED`. GET does not mkdir.

`GET /api/v1/temporal` calls `snapshot`. Optional `?at=` must be a finite unix time, or the response is 400 `BAD_AT`. `assert_fact` and `invalidate` are not called. GET does not mkdir.

`POST /api/v1/chamber` and `POST /api/v1/temporal` stay HTTP 501 with `kind: UNMEASURED` (`CHAMBER_NOT_COMPOSED`, `TEMPORAL_NOT_COMPOSED`) because `join`, `assert_fact`, and `invalidate` append the ledger. `GET` and `POST /api/v1/seats` stay 501 `SEATS_NOT_COMPOSED`. There is no seats module. Verbs those handlers do not name stay on the same 501 table. That table is not the answer for the GETs named above, nor for approval grant and deny.

## Where it lives

Service and modules: `cosmos/`. Runtime root, when configured: `live/` (`state/`, `ledger/`, `queue/`, `registry/`, `config/`, and the rest). The resolver is `cosmos_paths.py`. Contract for the lease: `docs/CCR.md`.

## Entry points

```
py -3.14 cosmos\cosmos.py serve --root <sentinel-root> --port 8770
```

Each module above also has `py -3.14 cosmos\<module>.py --selftest`, except where its docstring names a different flag (`cosmos_resession.py` uses `--root`, `--once`, `--status`). Selftest is not the service. Saving session-kit config does not fire a resession. `plan_resession` does not spawn.

## What it refuses

- A root with no sentinel content, a mismatched tree id, or a hand-built path.
- A second CCr lease, and a publish with no pen.
- A broken, torn, forged, or truncated ledger. History is not rewritten to look short.
- `HARDLINE` actions: delete outside the stage folder, force-push, pipe-to-shell from the network, disk destruction, encoded commands, and writes aimed at the authority ledger or at key material. Silence is not consent.
- A skill that teaches a `HARDLINE` action, an accept without the pen, and a body whose hash is not the accepted hash.
- Delegation past depth, concurrency, or a parent that is not a running job. A child does not receive mail send, work-order propose, seat take, spend admin, approval grant, or principal admin. At max depth it also loses `delegate`.
- Recall queries with no terms, a foreign owner (same shape as unknown), and a truncated chain.
- An unrecognized or ambiguous cadence. Sub-minute work is named `detached_daemon`, never a schtasks minute with a zero interval. The parser does not create the task.
- Porosity rotators and any score that was not observed. `GET` does not mkdir and does not invent.
- A packet with no destination: `UNMEASURED`, no new store.
- Sandbox cwd on a host pen, a remote worker that maps the V: volume, and an unconfigured remote treated as a silent host cwd.
- Spawn of extra `grok.exe` or `grok --single` as a work-order worker (`fail_xfer`). A context source that is a joined ` · ` string is `NO_CONTEXT`.
- Stagehand `browser_run_code_unsafe` (client-denied). `attach_to_kernel` refuses authority unless `boot_compose=True`. It does not spawn `grok.exe`.
- An action chain whose three principals are not distinct, or whose `action_sha` / previous link does not verify (`SOD`, `FORGED`, `BROKEN_CHAIN`).
- Resession that would re-implement seed HMAC. Authenticity stays in `cosmos_session.start_session`. The satellite does not modify kernel, ledger, scheduler, or service. `plan_resession` returns `execute` false for an installed door and does not spawn. Claude is `ANTHROPIC_OFF`. Spawn still does not run.

## What it is not

Not the coding rail, not G47, and not `cosmos_harness`. Not a second ledger writer. Not a drive-letter path root. The CCr lease is the one pen; holding it is not a second ledger.

`seats` has no module: there is no `cosmos_seats.py`. Chamber and temporal exist as the modules above. GET calls `snapshot`. POST does not, because those writes append. There is no `cosmos_temporal.py` and no `cosmos_packets.py`.

`cosmos_nlcron` is not a clock and not an HTTP route. `cosmos_sandbox` is not the scheduler. `cosmos_stagehand_rail` is not `playwright-dom` and not a second Core. `cosmos_porosity` SQLite is not authority. `cosmos_recall` SQLite is not authority. `cosmos_packet` does not open a new content-addressed role. A skills list is not an accept.

## Grade

4C for these modules is not a blanket PASS. House ruff config `cosmos\ruff.toml` exists (select E, F, and I; ignore E501; line length 120; target py314). A core2 pytest of 50 passed. That pytest is not the whole grade. This page does not claim the live server on 8770 was restarted. A root `ruff` or `mypy` scan walks `live/`. Do not run them on the repo root.

The package 4C that passed at this tip is `cosmos_code`, `harness/G47`, and `cosmos_harness`. That result is not a Core grade.
