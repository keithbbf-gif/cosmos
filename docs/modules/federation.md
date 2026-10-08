# Federation

## What it is

Propose-only day-one peer install. A stranger with the installer file already on disk gets one writable runtime root, one door (OpenRouter or xAI), a cap at or under one dollar, and a loopback chat page. The clock is 120 seconds (`INSTALL_BUDGET_S`): 90 for software, 30 for the person to paste a key. Identity is `.cosmos-root.json` (`system=COSMOS` plus a tree id they choose). It is not a drive letter and it is not `KMesh-COSMOS-live`. Core on a peer would bind `127.0.0.1:8770`. The page is `ROUTE_PAGE` (`/dayone`). Chat is `ROUTE_CHAT` (`/api/v1/dayone/chat`). Those day-one routes are proposals. They are not Core today. Law is `CONTRACT.md`. Shared refusals, the path jail, and product constants are `cosmos_federation`.

## Where it lives

Repo path: `V:\A\Ai\COSMOS\federation`. Applied 2026-10-07 from `V:\streams\federation`. The streams original stays in place. The public repo is keithbbf-gif/cosmos. This checkout is that repo plus a dirty working tree. A new machine does not get this machine's `live/` root, keys, or seat files. Package name: `cosmos-federation-proposals`.

## Entry points

Checker: `py -3.14 check4.py` with no slug grades `cosmos_federation`, `tests/test_product.py`, `conftest.py`, and `check4.py`. `py -3.14 check4.py <slug>` grades one `proposals/<slug>/` slice. `check4.main` is the function. It skips `rehearse.py` when no slug is passed.

Story runner: `rehearse(root, now=1_700_000_000)`. It returns a report of ids. It stops before any model call. `fake_reply` stands in for the body `request_body` would POST.

Shared names: `PathJail`, `Refuse`, `bound_int`, `bound_text`, `const_eq`, `redact`, `secret_shape`, `check_tree_id`, `check_door`, `check_cap`, `repo_disposition`. Constants include `DEFAULT_CAP_USD_MICROS` (250_000), `MAX_CAP_USD_MICROS` (1_000_000), `DEFAULT_HOST`, `DEFAULT_PORT`, `ROLES`, `ROUTE_PAGE`, `ROUTE_SETUP`, `ROUTE_CHAT`.

Slot functions (real names): `coldroot.plan` / `apply`; `pathscan.scan_text` / `scan_root`; `shipset.classify` / `measured_gaps`; `deps.classify_module` / `census` / `dayone_pyproject`; `runtime.plan`; `wizard.begin` / `submit` / `accept_key` / `ready`; `wizardhtml.page_text`; `secrets.mint` / `acknowledge` / `write_files`; `account.open_account`; `identity.peer_card`; `seat.suggested_pin` / `bind` / `user_turn` / `request_body` / `fake_reply`; `chatwindow.page` / `issue_nonce` / `redeem`; `bindpol.decide`; `spendcap.open_book` / `reserve` / `settle` / `release`; `package.steps` / `total_seconds` / `members`; `updater.verify` / `stage`; `credcat.catalog`; `routes.table`; `domdefer.choose` / `later`; `ledgerboot.genesis` / `apply`.

## What it refuses

Writes to `live/`, taking `CCR.lease`, opening this machine's `install_key.bin`, and becoming a second Core or ledger. Anthropic (`ANTHROPIC_OFF`). Unknown door (`DOOR`). A cap above one dollar (`CAP`). Scraping a browser profile or driving a vendor login (`SCRAPE`). Copying Keith's keys, `live/`, BU seat files, or `D:\R2Cloner`. Forbidden tree ids include `KMesh-COSMOS-live` and `GMesh` (`TREE_ID`). A second install with a different tree id is `IDENTITY_MISMATCH`. Remote bind without TLS is `REMOTE_PLAIN`. `no_auth` is `OPEN_AUTH`. Blank token, empty credential id, and raw key shapes refuse. `repo_disposition` returns `DENY` for `live`, secret filenames, and BU files. The spend fold is a day-one check. If it disagrees with Core's ledger, the chain wins. The wizard stores a credential id only.

## What it is not

Not a second Core. Not this machine's live tree. Not cDeck's Tauri shell, npm, a Rust compile, Tailscale, R2, phone voice, or Crucible. Not a two-minute path that assumes `kdash/index.html` or a preinstalled Python on a clean machine. `rehearse` does not call a model. `ledgerboot` writes a proposal cold-start chain. Core still owns the live ledger filename.

## Grade

On main `501fdee2` (2026-10-08), the package check (no slug) passed `py_compile`, `ruff`, `mypy`, and `pytest`. A separate `mypy --strict` fails on `rehearse.py` at the unused type ignore on line 35, because `check4` skips that file when no slug is passed. That is the recorded grade. It was not re-run for this note.
