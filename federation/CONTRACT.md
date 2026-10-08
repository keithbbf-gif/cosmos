# Contract for every federation proposal

Read this file before writing code. The live COSMOS tree is read-only.
Write only inside `V:\streams\federation\proposals/<your-slug>/`.

Do not edit `CONTRACT.md`, `README.md`, `cosmos_federation/`, `tests/`,
`check4.py`, `pyproject.toml`, `conftest.py`, or any other proposal.

## Product

A peer on a clean Windows machine runs one installer and, within 120 seconds
of double-click (installer file already on disk), sits in a chat window with
a live agent. The live tree `V:\A\Ai\COSMOS` is the behavior source. GitHub
`keithbbf-gif/cosmos` is what a stranger can clone. This folder is the
proposal for the gap between those two and a day-one chat.

Measured facts you must not contradict:

- `cosmos.py install --root <dir> --tree-id <id>` writes `.cosmos-root.json`,
  the role directories in `cosmos_federation.ROLES`, `config/install_key.bin`
  (32 random bytes), and `config/install_record.json`. A second install with
  a different tree id refuses `IDENTITY_MISMATCH`. Install does not mint
  `api_token.txt`, does not open a ledger, and does not open a chat window.
- `cosmos.py serve` binds `127.0.0.1:8770` unless `--remote`. A missing
  `config/api_token.txt` is minted only on loopback, with `secrets.token_urlsafe(24)`
  and mode `0o600`. A remote bind refuses to mint (`TOKEN_MISSING`). An empty
  token is `BLANK_TOKEN`. `--no-auth` with `--remote` is refused.
- The serve banner points at `kdash/index.html`. That page is telemetry, not
  a first-run wizard.
- There is no root `pyproject.toml` or `requirements.txt`. Kernel imports in
  `cosmos/*.py` are mostly the standard library. Confirm that in `deps` rather
  than assuming a third-party stack.
- README still says "Pre-implementation". The tree is an implemented kernel.
- `.gitignore` is deny-by-default. The GitHub repo is public.
- Anthropic is off the route. Day-one doors are `openrouter` and `xai` only.
- DOM is the preferred path once a person already has a vendor browser
  session. The installer must not collect passwords, scrape a browser profile,
  or automate a vendor login. That is `SCRAPE` and it refuses.
- Identity is sentinel content. No drive literal, no parent walk, no fallback
  root. `KMesh-COSMOS-live` and `GMesh` are taken names.
- Do not copy Keith's keys, `live/`, BU seat files, or `D:\R2Cloner`.
- Spend authority stays one append-only ledger. A day-one cap is a fold of
  events, not a second wallet.
- cDeck under `builds/cdeck` is a Tauri skin. It is not the day-one window.
  A clean machine does not compile Rust inside 120 seconds.

## Laws

- Fail closed. Unknown door, empty allow, missing credential id, blank token,
  remote without TLS, and a cap above one dollar all refuse.
- No network, socket, subprocess, thread, or sleep, except the `shipset` and
  `runtime` slots, which may read public docs. No slot calls a model.
- Do not call `exec`, `eval`, `pickle`, or `subprocess` from proposal code
  that ships to a peer. `check4.py` is the only runner.
- Secrets are ids in objects that get `repr`'d. Refuse raw key material
  (`sk-…`, `api_key=`, `Bearer …`, `xai-…`). `repr` of every public object
  stays free of those shapes. Compare with `cosmos_federation.const_eq`.
- Paths go through `cosmos_federation.PathJail` when a test writes.
- Bound strings with `bound_text` and ints with `bound_int` or the product
  checkers (`check_tree_id`, `check_door`, `check_cap`).
- The policy cap is `MAX_CAP_USD_MICROS`. Do not raise it.
- Deterministic. Timestamps and random bytes are arguments. No `datetime.now`,
  no `os.urandom`, no `time.time` inside library code.
- Type every function. Frozen dataclasses with slots. A module-level
  `SCHEMA = "cosmos-federation-<slug>/1"`.
- Public names go in `__all__`.
- Tests use the `scratch` fixture from `conftest.py`. Do not use `tmp_path`.
- Import only `cosmos_federation` and the standard library. Do not import a
  sibling proposal and do not import `V:\A\Ai\COSMOS`.
- Comments explain why a refusal or a packaging choice exists. Do not narrate
  an assignment.

## Files you write

- `proposals/<slug>/MAP.md` — what you read, what is already true in the live
  tree, what this proposal adds, refusal codes, and how CCr would land it
  later. Affirmative sentences. No secrets.
- `proposals/<slug>/<slug>.py` — the implementation.
- `proposals/<slug>/test_<slug>.py` — pytest.

Extra files (HTML, CSS, JS, a proposed toml) may sit in the same directory.
Name them in `MAP.md`.

## 4C

From `V:\streams\federation`, fix your slug until this exits 0:

```
py -3.14 check4.py <slug>
```

A missing checker is MISSING (exit 127). pytest exit 5 is NO_TESTS, not a pass.
`mypy --strict` must pass on your files.

## Slots

Implement only the slot named in your task. Keep the function names.

### shipset

Read-only. You may run `gh` against `keithbbf-gif/cosmos` (default branch
`main`) and read `V:\A\Ai\COSMOS\.gitignore`. Do not print file bodies that
look like secrets.

`classify(rel: str) -> Classified` uses `repo_disposition` and adds a `why`
string a reviewer can read. `Classified` is a frozen dataclass: `rel`, `kind`
(`SHIP`, `DEV`, or `DENY`), `why`.

`measured_gaps() -> tuple[str, ...]` lists rules the shared classifier is
missing, based on what you actually saw in gitignore and on GitHub. If you
found none, return an empty tuple. Do not edit the shared classifier.

MAP.md records: default branch, whether `live/` is absent on GitHub, top-level
directories, and any public file that should have been DENY.

### coldroot

`plan(tree_id: str, now: int) -> InstallPlan` describes sentinel JSON
(`system`, `tree_id`, `schema_version`), the role directory names, and the
install-record keys. The record stores `tree_id` and `installed_epoch`. It
does not store a drive letter as identity. `now` is a caller epoch int.

`apply(jail: PathJail, tree_id: str, now: int) -> InstallPlan` creates the
role directories, writes `.cosmos-root.json` and `config/install_record.json`,
and does not write key material. A sentinel with a different tree id raises
`Refuse("IDENTITY_MISMATCH", ...)`. The same tree id is idempotent.

Live `install()` also writes `install_key.bin`. Say that in MAP.md. This slot
leaves the key to `secrets` so the two writers do not both own the file.

### pathscan

`scan_text(rel: str, text: str) -> tuple[Hit, ...]` finds drive letters,
UNC paths, `V:\A\Ai\COSMOS`, `V:\Ai`, `D:\R2Cloner`, and `KMesh-COSMOS-live`
in source text. `Hit` has `rel`, `line`, `kind`, `excerpt`. The excerpt is
passed through `redact` and capped at 120 characters.

`scan_root(root: Path) -> tuple[Hit, ...]` reads `cosmos/*.py`, `README.md`,
`serve.bat`, `kdash/*.html`, and `docs/federation/*.md` under the given root.
Skip `live`, `.git`, `node_modules`, `__pycache__`, `src-tauri`, `_delme`.
Never open a file whose name contains `key`, `token`, `secret`, or `.env`.

Run it once against `V:\A\Ai\COSMOS` and summarize counts by kind in MAP.md.
Do not paste raw hit lines that still contain a secret shape.

### deps

`classify_module(name: str) -> str` returns `STDLIB`, `THIRD`, or `LOCAL`.

`census(root: Path) -> tuple[ImportRow, ...]` parses `import` / `from` lines
in `cosmos/*.py` only (not `builds/`). `ImportRow` has `module`, `kind`, and
`used_by` (a tuple of filenames).

`dayone_pyproject() -> str` returns the text of a pyproject for the day-one
installer. Require Python `>=3.14`. Dependencies are only the third-party
modules the census actually found, and an empty list is an acceptable
answer. Also write that text to `proposals/deps/pyproject.proposed.toml`.

### runtime

`plan(facts: Facts) -> tuple[Step, ...]` returns ordered steps with integer
seconds. `Facts` has `os_name`, `py_major`, `py_minor`, `launcher` (bool),
`embed_present` (bool).

When `embed_present` is true, the sum of seconds is at most
`SOFTWARE_BUDGET_S` and no step downloads. When Python is missing and the
embed zip is missing, raise `Refuse("RUNTIME_MISSING", ...)`. You may look
up the current CPython 3.14 Windows embeddable zip name from python.org and
record that filename in MAP.md. Do not download it.

### wizard

Pure state machine. `begin(now: int) -> Wizard`. `submit(wizard, field, value, now) -> Wizard`.
Fields in order: `root`, `tree_id`, `name`, `door`, `cap`, `bind`. A field
submitted out of order raises `Refuse("STEP", ...)`.

`accept_key(wizard, raw, credential_id, now) -> Wizard` runs after `door` and
before `cap`. It checks the door, refuses Anthropic, refuses a value that is
not `secret_shape`, and stores `credential_id` only. `repr(wizard)` must not
contain `raw`.

`bind` accepts `loopback` or `remote`. `remote` raises
`Refuse("REMOTE_PLAIN", ...)` until `submit(..., "tls", "yes")` has been
recorded. Root is a non-empty label, not a path the wizard opens.

`ready(wizard) -> bool` is true only on the confirm step with every answer set.

### wizardhtml

Static `wizard.html`, `wizard.css`, `wizard.js`. No framework and no build.
The page posts to same-origin `/api/v1/dayone/setup` and then shows the chat.
The key field is cleared after submit. The script does not put the key in
`localStorage`, `sessionStorage`, or the query string. Help links may be
`https://openrouter.ai/keys` and the xAI console only. No Anthropic link.

`page_text() -> str` returns the HTML. Tests read the three files from disk
and assert those rules as substrings.

### secrets

`mint(draw, now) -> Mint`. `draw(n: int) -> bytes` supplies the random bytes.
Produce a bearer compatible with `token_urlsafe` (url-safe, no padding issues)
and a 32-byte install key. `Mint` shows the bearer on `show_token` until
`acknowledge(mint) -> Mint`, which sets `show_token` to `None` and keeps
`token_id` and `key_id` (sha256 prefixes, 12 hex chars). `repr` never
contains the bearer or the key bytes.

`write_files(jail, token, key) -> None` writes `config/api_token.txt` and
`config/install_key.bin` with `os.open(..., 0o600)`. Refuse empty token or a
key that is not 32 bytes. This matches loopback serve, which mints with
`token_urlsafe(24)` only when the file is absent, and refuses to mint on a
remote bind. Say that in a comment.

### account

`open_account(name, door, credential_id, now) -> Account`. Refuse an empty
name, a credential id that `secret_shape` matches, and any door other than
the two day-one doors. `Account` holds the name, the door, the credential id,
and `created_epoch`. It does not hold key bytes.

### seat

`suggested_pin(door: str) -> str` returns one concrete model id you found by
reading the live rails (`cosmos_openrouter_rail.py` and the xAI rail if one
exists). If a rail has no single default, pick the cheapest documented chat
model and say why in MAP.md.

`bind(door, credential_id, pin, cap_usd_micros) -> Seat` refuses an empty pin,
an Anthropic-looking pin (`anthropic/` or `claude`), a bad credential id, and
a bad cap.

`user_turn(seat, text) -> Turn` bounds the text at 4000 characters.

`request_body(turn) -> dict` builds the JSON a later sender would POST. It
contains the pin and the user text. It does not contain an `Authorization`
value or any key. Read the live rail's request shape and match the field
names it already uses. Comment the file and function you copied the shape from.

`fake_reply(turn, reply_text, usd_micros) -> Reply` is the test double. It
refuses a cost above the seat cap.

### chatwindow

`page() -> str` is a single HTML document with the CSS and script inlined.
The transcript starts empty. The empty state does not invent a model sentence.
Sending posts JSON to `ROUTE_CHAT`. A reply object `{role, text, usd_micros}`
appends one assistant line.

`issue_nonce(draw, now) -> Nonce` and `redeem(nonce, presented, now, remote) -> Cookie`.
Redeem refuses a remote caller, a mismatch (`const_eq`), a second redeem, and
a nonce older than `NONCE_TTL_S`. The cookie is httpOnly, loopback, and is
not the long-term bearer. The HTML contains neither the nonce nor a bearer.

Write `dayone.html` as the same document `page()` returns.

### bindpol

`decide(host, port, remote, tls, no_auth) -> Bind`. Default shape is
`127.0.0.1` port `8770`, remote false, tls false, no_auth false, and that
one is allowed. Refuse `no_auth` always (`OPEN_AUTH`). Refuse remote without
tls (`REMOTE_PLAIN`). Refuse `0.0.0.0` unless remote is true. Refuse a port
outside 1..65535. `Bind` records the host, port, scheme (`http` or `https`),
and `auth="bearer"`.

### spendcap

In-memory event fold. `open_book(cap_usd_micros) -> Book`. `reserve(book, micros, now, event_id) -> Book`.
`settle(book, event_id, micros, now) -> Book`. `release(book, event_id, now) -> Book`.
Refuse a reserve that would pass the cap (`OVER_CAP`). The same `event_id`
twice is `DUP_EVENT`. Settle only a reserved id. This fold is the day-one
check. MAP.md says Core's ledger remains the authority when CCr lands it;
if the fold and the chain disagree, the chain wins.

### package

`steps() -> tuple[Step, ...]` and `total_seconds() -> int`. The total equals
`INSTALL_BUDGET_S` or less. Include the key-paste step at
`KEY_PASTE_BUDGET_S` and keep software steps at or under `SOFTWARE_BUDGET_S`.
No step runs npm, cargo, git clone, or a compiler.

`members() -> tuple[Member, ...]` is the installer file list (relative names).
Every member's `repo_disposition` is `SHIP` or the member is an installer-built
path under `runtime/`, `app/`, or `wizard/` that the installer creates and
that is not a secret name. A member that `repo_disposition` calls `DENY`
raises when `members()` is called. Do not include `live/`, BU files, or keys.

### updater

`verify(packet, *, local_tree_id, local_version, now) -> UpdateOk`. The packet
mapping needs `tree_id`, `version` (int), `sha256` (hex of payload), `payload`
(bytes), and `signer_id` (id, not a key). Refuse `UNSIGNED` when `signer_id`
is empty, `TREE_MISMATCH` when the tree id differs, `DOWNGRADE` when version
is not greater, `BAD_HASH` when sha256 does not match. A matching packet
returns the new version and the byte length.

`stage(jail, packet, *, local_tree_id, local_version, now) -> Path` writes
`updates/<version>/payload.bin` only after verify. It does not replace a
running tree. That is the fenced apply, owned by the peer's own writer later.

### identity

`peer_card(tree_id, display_name) -> Card`. `Card` has `tree_id`, `display_name`,
`host=None`, `mesh_id="UNASSIGNED"`, `product="dayone-chat"`. Refuse a bad
tree id and a secret-shaped display name. Do not invent an IP address.
MAP.md distinguishes this general card from `docs/federation/GRAYSON.md`,
which is one named person whose product was Crucible.

### credcat

`catalog() -> tuple[Cred, ...]`. Each `Cred` has `name`, `phase` (`DAY_ONE`,
`LATER`, `REFUSED`), `filename` or `None`, and `why`.

DAY_ONE is the bearer (`api_token.txt`), the install key (`install_key.bin`),
and one model key file whose name you choose (`openrouter_api_key.txt` or
`xai_api_key.txt`). LATER is R2, Tailscale, Cursor, OpenAI Codex, Firecrawl,
and the kill token. REFUSED is Anthropic and any path under `D:\R2Cloner`.
Read `docs/CREDENTIALS_NEEDED.md` so the phases match the live filenames,
then re-phase them for a stranger. Keith's "SATISFIED" rows are not shipped.

### routes

Read `cosmos/cosmos_service.py` `do_GET` and `do_POST`. `table() -> tuple[Route, ...]`
lists real paths you saw with phase `EXISTS`, and the three proposed day-one
routes with phase `DAY_ONE`. `Route` has `method`, `path`, `phase`, `why`.
A test must find `/api/v1/agents` and `/cdeck` marked `EXISTS`, and
`/api/v1/dayone/chat` marked `DAY_ONE`. Do not mark a path `EXISTS` unless
you saw it in that file.

### domdefer

`choose(has_key_id, has_browser_profile, ask_scrape) -> Choice`. `ask_scrape`
true raises `Refuse("SCRAPE", ...)`. A key id selects `via="api"` and
`phase="DAY_ONE"`. No key id selects `via="none"` and `phase="NEED_KEY"`,
even if a browser profile exists. A profile without a scrape request returns
`via="dom"` and `phase="LATER"` only when `has_key_id` is false and
`has_browser_profile` is true and the caller passes `allow_later=True` on a
separate function `later(has_browser_profile) -> Choice`. The two-minute
chooser never returns DOM.

### ledgerboot

`genesis(tree_id, now) -> tuple[Event, ...]`. Events, in order: `INSTALL`,
`CAP_SET`. Each event has `seq`, `event`, `tree_id`, `epoch`, `prev`, and
`hash` (sha256 of the canonical JSON without the hash field). The first
`prev` is 64 zeros. No secret bytes. `CAP_SET` records
`DEFAULT_CAP_USD_MICROS`.

`apply(jail, tree_id, now) -> Path` writes `ledger/genesis.jsonl`, one JSON
object per line. A second apply with the same tree id is idempotent. A
different tree id raises `IDENTITY_MISMATCH`. Comment that the live ledger
filename is owned by Core and CCr picks the real name at landing time; this
file is the proposal's cold-start chain.
