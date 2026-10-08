# Day-one distribution review

Date of the read: 2026-10-01. The live tree `V:\A\Ai\COSMOS` was not modified.
Proposals are under `V:\streams\federation\proposals`. The story that ties
them together is `rehearse.py`. `py -3.14 -m pytest tests/test_rehearse.py`
passes: it builds a peer root in a scratch directory and the report contains
ids only.

Public source: `github.com/keithbbf-gif/cosmos`, default branch `main`,
pushed HEAD `05fef7816d19197e5a968e36c063f346de7af032`, 2800 git tree
entries, tree not truncated. Rechecked the same day. The checkout on this
machine is `ccr/seed-archive-stamp` at `1f21c08`, dirty, and is not what a
stranger clones.

## The two minutes

The clock starts when the installer file is already on disk. It ends when
`http://127.0.0.1:8770/dayone` is showing a live model reply, or a typed
refusal that a key is still required.

`proposals/package` budgets 120 seconds: 90 for software and 30 for the
person to paste one key. The software steps unpack an embeddable CPython,
create the root, mint the local bearer and install key, record the account,
bind loopback, and open the chat page. They do not run npm, cargo, git
clone, or a compiler. cDeck's Tauri tree stays out.

`proposals/runtime` names the zip to pack before that clock:
`python-3.14.8-embed-amd64.zip`. If that zip is missing and Python is
missing, the plan refuses `RUNTIME_MISSING` instead of downloading during
install.

## What a clone gives someone today

`cosmos.py install --root <dir> --tree-id <id>` writes `.cosmos-root.json`,
the role directories, `config/install_key.bin`, and `config/install_record.json`.
A different tree id on an existing root refuses `IDENTITY_MISMATCH`.
Install does not mint `api_token.txt`, does not open a ledger, and does not
open a chat window.

`cosmos.py serve` binds `127.0.0.1:8770` unless `--remote`. A missing bearer
is minted only on loopback (`token_urlsafe(24)`, mode `0o600`). A remote bind
refuses to invent one. `--no-auth` with `--remote` is refused. The banner
tells the operator to open `kdash/index.html`. That page is telemetry.

There is no root `pyproject.toml`. README still says "Pre-implementation".
The `cosmos/` package is an implemented kernel.

## Blocker 1 — the public default branch contains a live root

`main` contains `live/` (14 paths). These three matter:

| Path | Size | What it is |
|---|---|---|
| `live/.cosmos-root.json` | 78 | `system=COSMOS`, `tree_id=KMesh-COSMOS-live`, schema 1 |
| `live/config/install_record.json` | 111 | `root` is `V:\A\Ai\COSMOS\live`, same tree id |
| `live/config/install_key.bin` | 32 | the install key `install()` writes |

The key bytes were not read. `.gitignore` already denies `/live/`,
`install_key.bin` is not named there as its own rule, and the blobs are on
`main` anyway. A public 32-byte install key is the HMAC material for that
root's ledger. Replace that key on the live machine, then remove `live/`
from the published tree. A peer install mints its own key
(`proposals/secrets`) and refuses the taken id `KMesh-COSMOS-live`
(`proposals/identity`, `cosmos_federation.check_tree_id`).

`api_token.txt` is not on `main`. Other name hits (`CREDENTIALS_NEEDED.md`,
`credential_manifest.py`, `*_secrets_against_old*`) are docs and old
fixtures, not that key file. They still should not ride along in an installer.

## Blocker 2 — paths that belong to this machine

Identity has to be the sentinel, not a drive. `cosmos_voice_hardening.py`
sets `BU_MD_PATH = r"V:\Ai\BU.MD"` and `cosmos_service.py` imports that
module while loading. A clean machine has no such file. The day-one page
does not read it. CCr points that constant through the path resolver before
a peer import of the service can be the product.

`proposals/pathscan` scanned that surface again on 2026-10-01: 261 files,
one secret-named module skipped, 195 hits in 81 files. `cosmos/*.py` has
191. `docs/federation` has 4. `README.md`, `serve.bat`, and `kdash/*.html`
have none. Counts: drive letter 91, UNC 1, `V:\A\Ai\COSMOS` 55, `V:\Ai` 42,
`D:\R2Cloner` 0, `KMesh-COSMOS-live` 6. The earlier 92nd drive hit was
`if n:\n` in `cosmos_refusals.py`, a newline escape, and it is no longer
counted. A non-empty scan refuses the installer package. The fix is
sentinel-relative roles, not a rewrite of this checkout into the installer.

The shared classifier
`repo_disposition` plus `proposals/shipset` is the ship/dev/deny rule.
`measured_gaps()` lists 16 holes against `.gitignore`. The one that changes
a real file's class: `docs/CREDENTIALS_NEEDED.md` is marked `DENY` because
the basename starts with `credentials`, while gitignore only excludes
`credentials*.json`. That markdown file is a ship document. Narrow the rule
when the classifier is edited. The other holes are live-state names, virtualenvs,
queue directories, and editor junk that are `DEV` at the repo root and `SHIP`
if they sit under `cosmos/`, `docs/`, or `kdash/`.

## Blocker 3 — the process and the libraries

Day one assumes Windows amd64. The installer carries CPython 3.14.8
embeddable so `py -3.14` is not a prerequisite. `proposals/runtime` refuses
a plan that downloads.

Census of `cosmos/*.py` (`proposals/deps`): third-party import roots are
`cryptography`, `vosk`, `watchdog`, and `tools`. `tools.surface` is an
in-repo module, not a pip package. The other three are lazy:

- `cryptography` is imported inside the TLS helper in `cosmos_service.py`
  (around the self-signed cert), not at import.
- `watchdog` is imported inside `cosmos_sched.py` and the code already
  falls back to polling when it is absent.
- `vosk` is imported inside `cosmos_stt.py` and a missing wheel is
  `STT_NONE`.

Loopback HTTP can import without those wheels. The proposed pyproject
requires Python `>=3.14` and lists the four roots so the first TLS, watch,
or speech call is not a surprise. Pack a `cryptography` wheel only in the
installer that offers TLS. Leave vosk and watchdog for a later optional
component. Do not `pip install` during the 120 seconds.

## Blocker 4 — `serve` is not a closed file list

`proposals/package` `members()` is the payload sketch: the embed zip, 13
kernel modules, `kdash/index.html`, the wizard files, and `app/dayone.html`.
That list is not enough to execute `cosmos.py serve`. `cosmos_service.py`
imports `cosmos_cvm_projection` and `cosmos_voice_hardening` at import time.
`cosmos.py serve` also imports `cosmos_crucible_critics`. Those modules are
not in `members()`.

The landing copy is every `cosmos/*.py` whose disposition is `SHIP`, plus
the embed zip, the wizard, and the day-one page. It is not a hand-picked
subset, and it is not `builds/cdeck/src-tauri`.

## Blocker 5 — accounts, keys, and the window

A stranger does not receive Keith's satisfied keys. `proposals/credcat`:

| Phase | Files |
|---|---|
| DAY_ONE | `api_token.txt`, `install_key.bin` (minted here), `openrouter_api_key.txt`, `xai_api_key.txt` |
| LATER | R2, Tailscale (a login, no file), Cursor, OpenAI Codex, Firecrawl, kill token |
| REFUSED | Anthropic, anything under `D:\R2Cloner` |

`proposals/wizard` order: root label, tree id, display name, door, key paste,
cap, bind. Loopback goes straight to confirm. Remote stops until `tls=yes`,
or it refuses `REMOTE_PLAIN`. The paste is checked and dropped. The wizard
keeps a credential id. `repr` does not contain the paste.

`proposals/wizardhtml` is the static page. It posts same-origin to
`/api/v1/dayone/setup`, offers `openrouter` and `xai`, clears the key field,
and does not put the key in browser storage or the query string.

`proposals/secrets` mints the bearer the way loopback serve does, plus the
32-byte install key, writes both with mode `0o600`, and `acknowledge` clears
the material from the object. A remote bind must not mint. Live serve
already refuses that case as `TOKEN_MISSING`.

`proposals/bindpol` allows `127.0.0.1:8770` with bearer auth and no TLS.
`no_auth` refuses on every interface, including loopback (`OPEN_AUTH`).
That is stricter than today's serve, which still allows `--no-auth` on
loopback. The distributed app should not ship an open console. Remote
requires TLS. `0.0.0.0` requires the remote flag.

`proposals/chatwindow` is the page Core does not serve yet. The transcript
starts empty. The installer opens `http://127.0.0.1:8770/dayone`. A one-time
nonce (`NONCE_TTL_S` is 60) redeems into an httpOnly loopback cookie.
Remote, mismatch, replay, and expiry refuse. The HTML does not contain the
bearer or the vendor key.

`proposals/routes` lists 115 paths that exist on `cosmos_service.py` and
three that do not: `GET /dayone`, `POST /api/v1/dayone/setup`,
`POST /api/v1/dayone/chat`. Those three are the landing work on the service.

## Blocker 6 — a live agent on the first turn

DOM stays the preferred path once a person already has a vendor browser
session. A clean machine does not. `proposals/domdefer` `choose` returns
`api` / `DAY_ONE` when a key id exists, and `none` / `NEED_KEY` otherwise.
It never returns DOM. `ask_scrape` refuses `SCRAPE`. The installer does not
read a browser profile, collect a password, or automate a login.
`later(True)` is the separate, post-install door.

`proposals/seat` builds the JSON `OpenRouterRail._dispatch_body` already
posts: `model`, `messages`, `max_tokens` 1024, `stream` false,
`provider.allow_fallbacks` false. The bearer stays in the header, which this
module does not accept. The OpenRouter pin is the rail's `DEFAULT_MODEL`,
`google/gemma-4-26b-a4b-it:free`, priced at $0 in that module. A 2026-10-01
seating walk recorded HTTP 429 `pool_hold` on that pin. The first turn has
to show that refusal in the window. It must not invent a reply, and it must
not silently switch models (`allow_fallbacks` stays false). The xAI pin in
this proposal is `grok-4.6` from `cosmos_cursor_rail.py`, because there is
no `cosmos_*xai*rail.py`. A native xAI chat body is still landing work.
Anthropic pins refuse.

`proposals/spendcap` is the check before that call. Default cap is $0.25
(`250_000` micro-dollars). The policy ceiling is $1. Over the cap, a
duplicate event id, and a settle without a reserve all refuse. The fold is
memory. Core's ledger stays the authority. If the fold and the chain
disagree, the chain wins.

`proposals/ledgerboot` writes `ledger/genesis.jsonl` with `INSTALL` then
`CAP_SET` at the default cap, hash-linked. The same tree id is idempotent.
A different tree id refuses `IDENTITY_MISMATCH`. Core owns the real ledger
filename. This file is the cold-start proposal, not a copy of the live chain.

`proposals/account` stores a display name, a door, and a credential id.
`proposals/identity` stores `host=None`, `mesh_id=UNASSIGNED`,
`product=dayone-chat`. Grayson in `docs/federation/GRAYSON.md` remains one
named person whose product was Crucible and whose host is still unnamed.
This card does not assign him an address or `GMesh`.

`proposals/updater` checks a later packet: signer id present, tree id
matches, version increases, sha256 matches. `stage` writes the payload
under `updates/<version>/` and does not replace the running tree. That
matches `docs/federation/UPDATE_SERVICE.md`: the hub does not overwrite a
peer.

## What stays out of the two minutes

Phone voice, Tailscale, R2, Crucible, the cDeck Tauri shell, Cursor, Codex,
Firecrawl, a second ledger, and this machine's `live/` root. `proposals/credcat`
marks those `LATER` or `REFUSED`.

## Where the code is

| Slice | Role |
|---|---|
| `cosmos_federation/` | Refusals, path jail, caps, doors, ship class |
| `proposals/shipset` | Classifier plus the 16 measured gaps |
| `proposals/coldroot` | Sentinel, roles, install record without key material |
| `proposals/secrets` | Bearer and install key, show once |
| `proposals/wizard` and `wizardhtml` | Account and security questions |
| `proposals/credcat` | Which files are day one |
| `proposals/account`, `identity` | Person and peer card |
| `proposals/domdefer` | API now, DOM later, scrape refused |
| `proposals/seat`, `spendcap` | One pin, one cap, no key in the JSON |
| `proposals/chatwindow`, `routes`, `bindpol` | The window and the bind |
| `proposals/ledgerboot` | Cold-start chain |
| `proposals/runtime`, `package`, `deps` | Embed, clock, import census |
| `proposals/updater` | Signed packet, no silent overwrite |
| `rehearse.py` | Runs that order in a scratch directory |

A second pass re-ran every slice. `check4.py` exited 0 on each. These
proposal bugs were fixed in that pass:

- `pathscan` no longer treats a non-raw `\n` escape as a drive letter.
- `wizard.accept_key` refuses an Anthropic marker anywhere in the paste
  or the credential id, including a leading space or a `Bearer` wrapper.
- `account` classifies a long secret-shaped display name as `SECRET`.
- `spendcap` replay refuses a hold that was over the cap even if a later
  release brings the folded total back under.
- `updater.stage` re-hashes the payload it is about to write. A same-length
  swap after `verify` is `BAD_HASH`. A second stage of the same version
  stays `PRESENT`.
- `chatwindow.page` refuses the words nonce and bearer in the document,
  not only the `Bearer ` header shape.
- `package.missing_for_serve` names the two import-time modules the
  payload list still omits: `cosmos_cvm_projection.py` and
  `cosmos_voice_hardening.py`.

`tests/test_rehearse.py` passed after those edits. The public tree
findings did not change.
