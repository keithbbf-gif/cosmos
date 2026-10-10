# Builds: sessions

COSMOS is not finished. This chapter is a reading map for three products that
sit on the OS. It is not a second Core, not a ledger writer, and not a claim
that session search, migrate, or the deck are done. None of these trees is
the authority file. Do not commit a runtime root, a catalog, or a transcript
from them.

Run the commands below from the repository root with `py -3.14`, unless a
line says otherwise. Paths in the examples are arguments you supply. There
is no guessed live root.

| Tree | What a developer runs | What it is |
| --- | --- | --- |
| `builds/open_sessions` | `Open_sessions.py` | List and open against the recents projection. First product on the OS. |
| `builds/session-tools` | `session_tools.py` | Scan, load, convert, diff, check, anonymize, crash-recover, migrate, rebind. Not Core. |
| `builds/sessions-page` | `sessions_page.py` | Standalone find, import, export, index, recover, resume, and a loopback page. Its own checkout. |

Open Sessions stays the list and open surface. Session-tools iterates on that
product. The sessions page is a separate program. Core's
`GET` and `POST /api/v1/session_tools` go through
`cosmos/cosmos_session_tools_kit.py`, which loads
`builds/sessions-page/engine.py`. That adapter does not walk transcript
bodies on GET. A missing engine file is `ENGINE_MISSING`, not an empty
success.

## Open Sessions

`builds/open_sessions/Open_sessions.py` lists and opens rows from the
rebuildable recents projection. The file is
`state/cdeck/recents.json` under the runtime root (`cdeck-recents/1`),
written by the cowork-to-OpenWork binder. The same projection is what
`GET /api/v1/recents` and the cDeck RECENTS pane read. This CLI does not
scrape another app's data and does not invent session ids.

`--root` is required and comes before the verb. `--tree-id` is optional and
must match the sentinel when you pass it. Omit `--root` and the process
exits 2. It does not look up an install record and it does not assume a
live directory.

```text
py -3.14 builds/open_sessions/Open_sessions.py --root <runtime-root> list
py -3.14 builds/open_sessions/Open_sessions.py --root <runtime-root> --tree-id <id> list
py -3.14 builds/open_sessions/Open_sessions.py --root <runtime-root> open <id>
py -3.14 builds/open_sessions/Open_sessions.py --root <runtime-root> --json open <id>
```

`<id>` is a recents id such as `cow-<session_id>`. Add `--json` to print a
JSON object. Without it, `list` prints a one-line summary and up to twenty
rows. `open` prints kind, id, title, a text prefix, and an OpenWork focus
note. It does not start `OpenWork.exe`.

Legal stream rows are omitted from the projection. They are counted, not
listed. Opening an omitted id is `NOT_IN_RECENTS`, not a hidden read.

Exit codes:

| Situation | Exit |
| --- | --- |
| `list` and the projection is readable | 0 |
| `list` and the projection file is absent (`NO_SOURCE`) | 0. The line says the projection was not written. That is not a history. |
| `list` and the projection is present but unusable (`TOO_LARGE`, `MALFORMED`, `WRONG_SCHEMA`, or the root itself refuses) | 1 |
| `open` and the session was opened, including an empty or unreadable transcript file (`OPENED`, `NO_TRANSCRIPT`, `TRANSCRIPT_UNREADABLE`) | 0 |
| `open` on a missing projection | 2 |
| `open` when the id is not in the non-legal rows | 2 |

`open` on a missing projection exits 2. A root that was installed and has
no `state/cdeck/recents.json` is that case. The loader kind is `NO_SOURCE`.
`ok` on that body means the list is empty, not that an id was opened. The
CLI therefore does not return 0. Do not treat a green `list` on `NO_SOURCE`
as an opened session.

Hermetic check, from the repository root. It installs a throwaway root. It
does not read the live tree:

```text
py -3.14 builds/open_sessions/test_open_sessions.py
```

## Session-tools

`builds/session-tools/session_tools.py` is the suite. It is a product, not
`cosmos.py`. Success and refusal both print one JSON object
(`cosmos-session-tools-result/1`). Exit 0 is only `OK`, `TRUNCATED`,
`DRY_RUN`, or `VERIFIED`. A typed refusal exits 2. The kind is in the JSON.
Do not scrape a traceback for it.

```text
py -3.14 builds/session-tools/session_tools.py scan --family cowork --store <catalog-dir>
py -3.14 builds/session-tools/session_tools.py scan --family grok_tui --store <sessions-dir>
py -3.14 builds/session-tools/session_tools.py load --id cow-<sid> --store <catalog-dir>
py -3.14 builds/session-tools/session_tools.py load --id grok-<sid> --store <sessions-dir> --out <dir>
py -3.14 builds/session-tools/session_tools.py convert --id <id> --store <dir> --out-dir <dir>
py -3.14 builds/session-tools/session_tools.py diff --left <file> --right <file>
py -3.14 builds/session-tools/session_tools.py check --what catalog --path <store-or-catalog>
py -3.14 builds/session-tools/session_tools.py check --what sqlite --path <db>
py -3.14 builds/session-tools/session_tools.py check --what seed --path <runtime-root>
py -3.14 builds/session-tools/session_tools.py check --what sit --path <sit-file> --sit ccr
py -3.14 builds/session-tools/session_tools.py anonymize --id <id> --store <dir> --out-dir <dir>
py -3.14 builds/session-tools/session_tools.py crash-recover --target <file> --bak <file> --stage <dir>
py -3.14 builds/session-tools/session_tools.py migrate --id grok-<sid> --store <dir> --workspace-id <ws> --directory <ow-dir> --dry-run
py -3.14 builds/session-tools/session_tools.py rebind --id ses_<id> --workspace-id <ws> --directory <ow-dir> --dry-run
```

`scan` with neither `--store` nor `--root` refuses `GUESSED_ROOT` and exits
2. Passing only `--root` is not enough for this slice: each named family
still requires `--store` (`NO_STORE`). Default families, when `--family` is
omitted, are `cowork` and `grok_tui`.

| Family | Scan |
| --- | --- |
| `cowork` | `COW_SESSION_CATALOG.json` in the store directory, or the catalog file itself. Legal stream rows are counted in `n_legal`. |
| `grok_tui` | Directories that contain `summary.json` and `chat_history.jsonl`. |
| `openwork_native` | OpenWork native store. Load ids use the `ow-` prefix. |
| `claude_desktop`, `cursor`, `codex`, `gemini`, `sgh_voice` | `UNMEASURED`. `n` is JSON null, not zero. `load` refuses `UNMEASURED`. |
| any other name | `UNMEASURED`, `path` null, `n` null. |

`load` reads one id. A legal Cowork row refuses `LEGAL_OMITTED` and exits 2.
The text is not returned. `--out` writes the canonical pair
`{id}.ctr.jsonl` and `{id}.ctr.decl.json`. The sidecar is sha and length
only (`hmac` false). It is not the ledger and it is not a seed MAC.
`convert` writes that pair under `--out-dir`. `diff` hashes two payload
files and reports the turn-count delta. `anonymize` writes a redacted copy.
`crash-recover` stages the target and replaces it from a backup. It does
not rewrite a corrupt database page in place.

`check --what` is one of `catalog`, `sqlite`, `seed`, or `sit`. `--path` is
required on every one of them.

`check --what seed` refuses with no root. The command is:

```text
py -3.14 builds/session-tools/session_tools.py check --what seed --path <path>
```

`<path>` is the candidate runtime root. If that path is not a directory, or
`.cosmos-root.json` is not a file in it, the kind is `NO_ROOT` and the
process exits 2. The refusal is before Kernel is imported and before
`config/install_key.bin` is opened. The detail names the missing sentinel.
It does not name the key file. A directory that merely exists is not a
root. There is no install-record fallback and no other tree.

If the sentinel is present and `config/install_key.bin` is not a file, the
kind is `NO_MAC`, still before Kernel. A root that passes both gates is
then checked read-only: `state/SEED.json` plus `state/SEED.decl.json`,
length, sha, and MAC. Missing seed is `NO_SEED`. A bad MAC is `BAD_SEED`.
A seed `tree_id` that is not the sentinel's is `IDENTITY_MISMATCH`. A
verified seed prints `VERIFIED` and exits 0. This verb does not repair the
seed.

`check --what catalog` wants the catalog and its transcript files
(`NO_STORE`, `MISSING_PART`). `check --what sqlite` runs
`integrity_check` and `foreign_key_check` on a file opened read-only.
`check --what sit` defaults to chair `ccr` and expects `bucm/1`. `--sit orc`
expects `burestart/3`. A mixed sit is `SIT_MIXED`.

`migrate` and `rebind` refuse the closed Cowork catalog set with
`DO_NOT_REINGEST`. A `cow-` id, a non-`grok-` id, or a grok id that set
matches is that refusal on `migrate`. `rebind` refuses an id that starts
with `ses_cow_`, `cow-`, or `ow-ses_cow_` the same way. `--dry-run` on a
grok id outside that refusal prints a plan and does not write. A real `migrate` needs an
existing `opencode.db` in `--directory`, copies a backup into a stage
directory first, and inserts a new `ses_grok_*` row. It is not a Core
commit.

Tests use pytest and hermetic fixtures. They do not open the live store:

```text
py -3.14 -m pytest builds/session-tools/tests -q
```

## Sessions page

`builds/sessions-page` is its own repository, checked out at that path. The
program is stdlib only. It does not open the ledger and it does not take
the pen. From that directory the short commands are
`py -3.14 sessions_page.py find` and `py -3.14 test_sessions_page.py`.
From the COSMOS root, use the paths below.

```text
py -3.14 builds/sessions-page/sessions_page.py find
py -3.14 builds/sessions-page/sessions_page.py find --query <text> --harness <name> --cwd <path> --limit 200
py -3.14 builds/sessions-page/sessions_page.py import --id <id> --out <dir>
py -3.14 builds/sessions-page/sessions_page.py export --id <id> --out <dir>
py -3.14 builds/sessions-page/sessions_page.py index --out <file>
py -3.14 builds/sessions-page/sessions_page.py recover --target <file> --bak <file>
py -3.14 builds/sessions-page/sessions_page.py recover --target <file> --bak <file> --apply
py -3.14 builds/sessions-page/sessions_page.py resume --id <id>
py -3.14 builds/sessions-page/sessions_page.py resume --id <id> --launch
py -3.14 builds/sessions-page/sessions_page.py scan --store <dir>
py -3.14 builds/sessions-page/sessions_page.py load --id <id> --store <dir>
py -3.14 builds/sessions-page/sessions_page.py verbs
py -3.14 builds/sessions-page/sessions_page.py serve --port 8786
py -3.14 builds/sessions-page/sessions_page.py serve --port 8786 --no-browser
py -3.14 builds/sessions-page/test_sessions_page.py
```

There is no `sessions_page.py check` subcommand. The seed refusal with no
root is the session-tools command in the previous section. The page
engine can still check a seed file when something POSTs `action=check`,
and that check is length and sha only. `mac_ok` stays null. It does not
apply the sentinel gate and it does not call Kernel. Do not use it as
`check --what seed`.

`find` counts stores and reads headers. It does not read transcript bodies
for the overview. A missing store is `n: null`, not zero. Legal sessions
are counted and their text is not opened. Import of sqlite and zstd stores
stays `UNMEASURED`. Amazon Q stays uncounted unless `AMAZONQ_HISTORY`
points at an export. Factory, Windsurf, and Augment have no documented
transcript path here, so their count stays null. Omit `--out` on `import`
or `export` and the file goes under `var/exports` inside this tree.
`index` writes `sessions-page-index/1`.

`recover` without `--apply` checks the target and does not replace it.
`--apply` copies a verified sibling backup over the target only after the
original is staged under `var/stage`. It does not patch a corrupt sqlite
page in place. `resume` prints the harness argv and does not pass `-p`.
`--launch` starts that argv. No binary is `BINARY_ABSENT` and the process
still exits 0, because that kind is a measured result. OpenWork and Cowork
return `OPENWORK_FOCUS` and do not spawn `OpenWork.exe`. A page error
(`LEGAL_OMITTED` and the other typed kinds) exits 2.

Resume argv by harness, when the row is listed: `grok --resume`,
`claude --resume`, `codex resume`, `agent --resume`, `pi --session`,
`hermes --resume`, `cline --id` for a `*.messages.json` session,
`goose session --resume --session-id`, `qwen --resume`,
`copilot --resume=<id>`, `crush --session`. Factory's `droid --resume` is
documented elsewhere and this tree has no session directory for it, so
those rows are not listed.

`serve` binds `127.0.0.1` only. The default port is 8786. Open
`http://127.0.0.1:8786/`. A bind failure prints `BIND_FAILED` and exits 2.
The first screen is a Blackline overview of drives and default session
locations. Counts stay unmeasured until a pane is opened. Quit on the page
is `POST /api/shutdown`. CORS allows only loopback origins.

The packaged executable needs no Python to run. Double-click it. It opens
the page and no console. Starting it again focuses the page that is
already up. It tries ports 8786 through 8795.

```text
builds\sessions-page\dist\sessions_page.exe
```

The script commands remain the ones to use from a shell. Rebuild is the
spec `builds/sessions-page/sessions_page.spec` (windowed, `ui` bundled).
This chapter does not claim that executable is the supported install path
for a peer.

Harness names the engine knows: `grok`, `claude`, `codex`, `cursor`,
`cowork`, `openwork`, `claude_desktop`, `gemini`, `hermes`, `cline`,
`kilo`, `roo`, `pi`, `copilot`, `continue`, `aider`, `goose`, `qwen`,
`amp`, `openhands`, `crush`, `amazonq`, `dsh`, `factory`, `windsurf`,
`augment`. `verbs` prints that list plus the engine verbs. Engine verbs
include `find`, `preview`, `import`, `export`, `index`, `recover`,
`resume`, `scan`, `load`, `convert`, `diff`, `check`, `anonymize`,
`crash-recover`, `strip`, `strip_dry`, and `doi`. `doi` returns
`UNPROVEN` and does not fetch a citation. `migrate` and `rebind` are not
in that verb list. Posted to this engine, both return `DO_NOT_REINGEST`
and write nothing. That is the same closed set as session-tools, refused
here before any plan.

Later cDeck mount, not wired by this page: `plugin/REGISTER.md`. One
script tag for `plugin/deck_sessions_page.js` and an optional
`#panel-sessions-page`. The script does nothing if that node is absent.
Do not edit `app.js` or `header.js` for that mount. Start `serve` first.

Adapter self-check, which only confirms the engine imports and that GET
shape does not create a temp directory:

```text
py -3.14 cosmos/cosmos_session_tools_kit.py
```

## What these trees do not do

They do not install a runtime root, serve Core, or write the ledger.
`cosmos.py install` and `cosmos.py serve` stay in the install chapter.
They do not turn on spend, dispatch, seats, or voice. They do not share a
pen. A projection under `state/cdeck/` can be deleted and written again.
That does not change the seed, and a missing projection is an exit 2 on
`open`, not a fabricated recents list.
