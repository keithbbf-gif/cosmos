# sessions

Three products on COSMOS. None of them is Core. Legal sessions are refused: counted or omitted, text not opened. The rebind of the 666 Cowork sessions is already done. Do not re-ingest them.

## What it is

**Open Sessions** (`builds\open_sessions`) is the first product (Keith 2026-09-05). It lists and opens sessions. The projection is cDeck recents (`cosmos_recents_panel.handle_get`, the same fold as `GET /api/v1/recents`). Legal rows stay out. It does not invent ids.

**session-tools** (`builds\session-tools`) is the suite on that product: scan, load, convert, diff, check, anonymize, crash-recover, plus migrate and rebind. Canonical files are `{id}.ctr.jsonl` and `{id}.ctr.decl.json` (sha and length only). Measured adapters: `cowork`, `grok_tui`, `openwork_native`. `claude_desktop`, `cursor`, `codex`, `gemini`, and `sgh_voice` scan as UNMEASURED. A missing family is UNMEASURED with `n: null`, not zero.

**sessions-page** (`builds\sessions-page`, pin `178e31eb`) is its own repository. It finds local harness sessions, imports and exports a canonical file, indexes, recovers from a sibling `.bak`, and prints a resume command. `serve` is loopback only (`http://127.0.0.1:8786/`). Counts stay unmeasured until a pane is opened. A missing store is `n: null`. sqlite and zstd import stays UNMEASURED. Amazon Q stays uncounted unless `AMAZONQ_HISTORY` points at an export. Factory, Windsurf, and Augment have no documented transcript path, so `n` stays null. Core `cosmos_session_tools_kit.py` calls this engine. Packaged `dist\sessions_page.exe` opens that loopback page and does not open a console.

## Where it lives

- `builds\open_sessions\Open_sessions.py` and `test_open_sessions.py`
- `builds\session-tools\` — `session_tools.py`, `verbs.py`, `schema.py`, `refusals.py`, `adapters\`
- `builds\sessions-page\` — `sessions_page.py`, `engine.py`, `ui\`, `plugin\deck_sessions_page.js`
- cDeck hosts the same verbs as panels (`#panel-sessions-page`, `#panel-st-*`). Those panels are the deck, not a second writer.

## Entry points

```
py -3.14 builds\open_sessions\Open_sessions.py --root <live> list
py -3.14 builds\open_sessions\Open_sessions.py --root <live> open <id>
py -3.14 builds\session-tools\session_tools.py scan|load|convert|diff|check|anonymize|crash-recover|migrate|rebind ...
py -3.14 builds\sessions-page\sessions_page.py find|import|export|index|recover|resume|serve
py -3.14 builds\sessions-page\test_sessions_page.py
```

Open Sessions requires `--root`. It does not guess a live path. `open` returns the recents body (transcript plus OpenWork focus). It does not spawn `OpenWork.exe`.

session-tools `check` is `catalog`, `sqlite`, `seed`, or `sit`. Crash-recover copies a verified sibling aside and does not rewrite a corrupt page in place. Resume on the page prints the harness command (`grok --resume`, and the matching flag for the other listed harnesses). `--launch` starts that command. It does not pass `-p`. OpenWork and Cowork return an id to focus.

## What it refuses

- Legal load is `LEGAL_OMITTED` (Cowork stream `legal`; OpenWork title or directory marks). The page raises the same kind and does not open the text. Scan may count `n_legal` and still omit the body.
- Cowork ids and any id already in the 666 set are `DO_NOT_REINGEST` on migrate. `rebind` refuses `ses_cow_`, `cow-`, and `ow-ses_cow_`. On the page, `migrate` and `rebind` return `DO_NOT_REINGEST` and stay closed.
- session-tools scan without `--store` or `--root` is `GUESSED_ROOT`. Unknown id prefixes are `NOT_FOUND`.
- `check --what seed` on a path with no COSMOS sentinel is `NO_ROOT`, before Kernel and before the install key. That check was not run against the live root.
- Migrate without `--workspace-id` and `--directory` is `WORKSPACE_UNKNOWN`. A failed write restores the staged `opencode.db`. A count mismatch is `VERIFY_MISMATCH` and restores the copy.
- The page does not decompress DeepSeek `dsh` zstd. It counts those files only. Recovery does not patch a sqlite page in place.

## What it is not

Not a second kernel. Not a Legal reader. Not a re-ingest of the 666 Cowork sessions. `clone.py` only refuses an identical text tail. It is not a clone-session planner. Open Sessions is list and open. The other verbs live in session-tools and the page.

## Grade

sessions-page pin `178e31eb`. Its checker is the script `test_sessions_page.py`, not pytest. A later run from `builds\sessions-page` reported `68/68`, exit 0 (`C:\Users\Papa\AppData\Local\Temp\c4-h13-result.md`). That is the script grade, not a four-tool 4C pass. `dispatch("recover")` and the recover command now pass no bak unless one was named, so a corrupt newest sibling is skipped and an older good `.bak` is used. This note did not re-run the script.

session-tools pytest reached 30 passed, including a `NO_ROOT` refusal when `check --what seed` is handed a root that is not a COSMOS root. `check --what seed` was not run against the live root. Open Sessions script `test_open_sessions.py` later reported 5/5, exit 0 (`C:\Users\Papa\AppData\Local\Temp\c4-h14-result.md`). Pytest collected nothing (exit 5, functions are `t_*`). `open` exits 0 only for `OPENED`, `NO_TRANSCRIPT`, or `TRANSCRIPT_UNREADABLE`. A missing projection exits 2. List of `NO_SOURCE` still exits 0. The 666 sessions were not re-ingested. This note did not re-run the script.
