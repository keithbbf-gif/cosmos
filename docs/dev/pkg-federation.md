# Package: federation

`cosmos-federation-proposals` is the propose-only day-one packaging of a COSMOS peer. It is not a second Core, not a second ledger, and not a finished installer. The import package is `cosmos_federation`. The product name on a peer card is `dayone-chat`. Schema of the shared constants is `cosmos-federation/1`.

This page describes the copy under `federation/` on the COSMOS tree. COSMOS itself is not finished. The two-minute chat install described here is a reviewable proposal. Core does not serve it yet.

## What this package is

A stranger can clone `keithbbf-gif/cosmos`. The live checkout on this machine is that repo plus a working tree they must not receive: no `live/` root, no keys, no BU seat files, no `D:\R2Cloner`. `federation/` is the gap between those two and a day-one chat window. Proposal code does not import the live tree and does not take `CCR.lease`.

`pyproject.toml` names the project `cosmos-federation-proposals`, version `0.1.0`, description "Propose-only day-one installer for a COSMOS peer. Not the live tree." That file configures ruff, mypy, and pytest. It does not declare a console script. There is no `pip install` entry that becomes the peer installer.

The harness metadata allows Python `>=3.11`. The day-one product and the house check are Python 3.14. Do not treat a 3.11 run as the peer product.

The folder was applied from `V:\streams\federation` onto this tree. The streams original stays in place. Do not replace this copy with an older stream tree, and do not treat either tree as a writer of `live/`.

## Layout

| Path | Role |
|---|---|
| `CONTRACT.md` | Law for every proposal slice. Read it before adding one. |
| `README.md` | Two-minute story and what stays out of it. |
| `REVIEW.md` | Measured distribution review. Blockers stay blockers until Core lands them. |
| `cosmos_federation/` | Shared refusals, path jail, bounds, redaction, and product constants. |
| `proposals/<slug>/` | One slice: `MAP.md`, the module, and tests. Slices do not import each other. |
| `check4.py` | Package checker. |
| `rehearse.py` | In-process day-one story. Not the kernel verb `cosmos.py rehearse`. |
| `conftest.py` | Puts proposal directories on `sys.path`. Tests use the `scratch` fixture, not `tmp_path`. |
| `tests/` | Shared product pins and the rehearse test. |

Twenty slices: `account`, `bindpol`, `chatwindow`, `coldroot`, `credcat`, `deps`, `domdefer`, `identity`, `ledgerboot`, `package`, `pathscan`, `routes`, `runtime`, `seat`, `secrets`, `shipset`, `spendcap`, `updater`, `wizard`, `wizardhtml`.

## Check entry

Run checkers from the `federation` directory, not from the COSMOS repo root. The interpreter in the command is the one that is checked.

Shared package (no slug). This covers `cosmos_federation`, `tests/test_product.py`, `conftest.py`, and `check4.py`. It does not run `rehearse.py` and it does not run the slices:

```
py -3.14 check4.py
```

One slice. A missing directory prints `MISSING` and exits 127:

```
py -3.14 check4.py <slug>
```

`check4.py` runs, in order, `py_compile`, `ruff check`, `mypy --strict`, and `pytest` on that target. A missing tool exits 127. Pytest exit 5 is `NO_TESTS`, not a pass. Ruff here follows the package table: line length 120, target `py314`, select `E`, `F`, `I`, ignore `E501`.

The day-one story is a separate pytest, still from `federation`:

```
py -3.14 -m pytest tests/test_rehearse.py -q
```

`rehearse(root)` needs an empty directory the caller created. The report keeps ids (`token_id`, `key_id`) and sets `show_token` to `None`. It must not contain a secret shape. The function stops before any model call. `fake_reply` stands in for the body that `request_body` would POST. A real reply is later landing work on Core.

Plain `py -3.14 -m pytest` from this directory also collects `tests` and `proposals`. That is wider than `check4.py` with no arguments.

`cosmos.py rehearse --root … --backup … --scratch …` is the kernel backup rehearse. It is not this package.

## What a peer runs today

A peer who already has the Windows launcher and CPython 3.14 runs the kernel, not `check4.py`. The root is one install-configured directory, identified by sentinel content (`.cosmos-root.json`), not by a drive letter.

```
py -3.14 cosmos\cosmos.py install --root <dir> --tree-id <id>
py -3.14 cosmos\cosmos.py serve --root <configured root> --port 8770
```

`install` writes the sentinel, the role directories, `config/install_key.bin` (32 random bytes), and `config/install_record.json`. A second install with a different tree id refuses `IDENTITY_MISMATCH`. Install does not mint `config/api_token.txt`, does not open a ledger, and does not open a chat window.

`serve` binds `127.0.0.1:8770` unless `--remote`. A missing bearer is minted only on loopback. A remote bind refuses to mint. `--no-auth` with `--remote` is refused. The banner points at `kdash/index.html`. That page is telemetry, not a first-run wizard.

That pair is not a closed clean-machine product. There is no root `pyproject.toml` for the kernel. README can still say "Pre-implementation" while `cosmos/` is an implemented kernel. A machine without Python 3.14 cannot start this line, and the serve banner does not open a day-one chat.

Taken tree ids include `GMesh`, `KMesh-COSMOS-live`, `COSMOS`, `live`, and `main`. A new peer picks a different id. Do not copy this machine's install key. If a published history still contains `live/config/install_key.bin`, that key is replaced on the live machine and `live/` stays off the published tree. This package does not open that file.

## What the proposal says a peer runs

The clock starts when an installer file is already on disk. It ends when `http://127.0.0.1:8770/dayone` shows a live model reply, or a typed refusal that a key is still required. The download of the installer is outside the clock. Budget is 120 seconds: 90 for software and 30 for one key paste (`INSTALL_BUDGET_S`, `SOFTWARE_BUDGET_S`, `KEY_PASTE_BUDGET_S`).

`proposals/package` names the allowances, in order:

| Step | Seconds | What it is |
|---|---|---|
| `unpack_runtime` | 20 | Extract embeddable CPython already inside the installer. |
| `apply_cold_root` | 10 | Sentinel, role directories, install record. No install key in this step. |
| `key_paste` | 30 | The person pastes one OpenRouter or xAI key. |
| `mint_secrets` | 10 | Loopback bearer and 32-byte install key, created on that machine. |
| `write_account` | 10 | Display name, door, credential id, cap. No key bytes. |
| `bind_loopback` | 15 | `127.0.0.1:8770` with bearer auth. |
| `open_chat_page` | 25 | Static `app/dayone.html` on that origin. |

No step runs npm, cargo, git clone, or a compiler. cDeck's Tauri shell is not the window. `proposals/runtime` names the zip to pack before the clock: `python-3.14.8-embed-amd64.zip`. If that zip is missing and Python is missing, the plan refuses `RUNTIME_MISSING` instead of downloading during install.

`rehearse.py` walks that order in a scratch directory: wizard, cold root, mint, account, API door, seat, spend fold, fake reply, genesis chain, loopback bind, one-time nonce, chat page. It is a library function. A peer does not launch it as the product.

Day-one doors are `openrouter` and `xai` only. Anthropic refuses `ANTHROPIC_OFF`. Default cap is `250_000` micro-dollars ($0.25). The policy ceiling is `1_000_000` ($1). A higher cap refuses. The spend fold in `proposals/spendcap` is a check. Core's ledger stays the authority. If the fold and the chain disagree, the chain wins.

The wizard order is root label, tree id, display name, door, key paste, cap, bind. Loopback can confirm. Remote refuses `REMOTE_PLAIN` until TLS is recorded. The paste is not kept. `repr` of public objects stays free of raw key material. The chat page does not hold the bearer or the vendor key. A one-time nonce (`NONCE_TTL_S` is 60) redeems into an httpOnly loopback cookie. Remote, mismatch, replay, and expiry refuse.

DOM stays the preferred path after a person already has a vendor browser session of their own. A clean machine has no such session, so the two-minute chooser never returns DOM. Asking the installer to scrape a browser profile refuses `SCRAPE`.

Role directory names, copied from the live path table, are `state`, `ledger`, `queue`, `work`, `logs`, `registry`, `backups`, `publish`, `config`, `docs`, and `cosmos` (the tools role inside a runtime root, not the git checkout).

`repo_disposition` classifies a repo-relative path as `SHIP`, `DEV`, or `DENY`. Unknown paths are `DEV` so a new file is not shipped by accident. `live/`, seat files, token and key filenames, `src-tauri/target`, and a drive or UNC path are `DENY`. The installer payload is an explicit file list, not a bare `cosmos/` directory. `missing_for_serve` records kernel modules the list still omits. The review names `cosmos_cvm_projection.py` and `cosmos_voice_hardening.py` at import time, and `cosmos.py serve` also imports `cosmos_crucible_critics`. The landing copy is every `cosmos/*.py` whose disposition is `SHIP`, plus the embed zip, the wizard, and the day-one page. It is not a hand-picked subset and it is not `builds/cdeck`.

## Proposed routes that are not on Core

`proposals/routes` marks existing service paths `EXISTS` only when they were read in `cosmos/cosmos_service.py`. These three are `DAY_ONE` and are not served today:

| Method | Path | Role |
|---|---|---|
| GET | `/dayone` | Chat page. |
| POST | `/api/v1/dayone/setup` | Same-origin wizard submit. One-time loopback nonce. |
| POST | `/api/v1/dayone/chat` | First live turn. |

Until those exist, opening `kdash/index.html` is the serve banner, not the day-one window. `proposals/bindpol` also refuses `--no-auth` on loopback (`OPEN_AUTH`). Live `serve` still allows `--no-auth` on loopback. The stricter rule is the proposal, not current serve.

## Shared law

`cosmos_federation` exports the constants and checkers the slices share: `Refuse`, `PathJail`, `bound_text`, `bound_int`, `check_tree_id`, `check_door`, `check_cap`, `repo_disposition`, `redact`, `secret_shape`, `const_eq`. A refusal is a result. Detail text does not carry a secret.

Library code does not call the network, sleep, or read the clock. Timestamps and random bytes are arguments. `check4.py` is the only runner that starts subprocesses. `shipset` and `runtime` may read public docs. No slice calls a model.

Tests write only through `PathJail` and the `scratch` fixture. A proposal module imports `cosmos_federation` and the standard library. It does not import a sibling slice and it does not import `V:\A\Ai\COSMOS`.

## What stays out

Phone voice, Tailscale, R2, Crucible, the cDeck Tauri shell, Cursor, Codex, Firecrawl, a kill token, a second ledger, and this machine's `live/` root. `proposals/credcat` marks those `LATER` or `REFUSED`. Day-one files are the bearer and install key minted on the peer, plus one model key the person pastes (`openrouter_api_key.txt` or `xai_api_key.txt`). Keith's satisfied credential rows are not shipped.

`proposals/updater` can verify a later packet and stage `updates/<version>/payload.bin`. It does not replace a running tree. The peer's own writer applies it later.

`proposals/identity` leaves `host` empty and `mesh_id` as `UNASSIGNED`. It does not assign an address. `docs/federation/GRAYSON.md` is one named person whose product was Crucible. That card is not this general peer card.

## Read next

`federation/README.md`, `federation/CONTRACT.md`, and `federation/REVIEW.md` are the package's own record. `docs/federation/UPDATE_SERVICE.md` is the later update hub, not this installer. Kernel install and serve remain `cosmos/cosmos.py`. Landing the chat routes, the closed file list, and the embeddable runtime is still CCr work. Nothing in this package is that landing.
