# package

The installer file is already on disk. It already contains embeddable CPython 3.14. The clock is 120 seconds from unpack to the chat page. Key paste is the 30-second human slice. The other steps sum to 90.

## What this proposal read

- `CONTRACT.md` slot `package`, plus the shared product constants `INSTALL_BUDGET_S` (120), `SOFTWARE_BUDGET_S` (90), and `KEY_PASTE_BUDGET_S` (30).
- `README.md` for the two-minute order: runtime root, wizard, local bearer, loopback serve, chat page.
- `cosmos_federation.repo_disposition`. `cosmos/cosmos.py` and `kdash/index.html` are `SHIP`. `live/`, BU seat files, `api_token.txt`, `install_key.bin`, and `src-tauri/target` are `DENY`. Unknown paths are `DEV`.
- Live `cosmos.py` serve banner and live `install()` in `cosmos_kernel.py`.
- Load imports of the kernel slice that this payload names: paths, ledger, lock, mail, sched, validate, spend, and the OpenRouter rail's imports of `cosmos_packet` and `cosmos_rail_base`.
- The Python 3.14.8 Windows release page. The 64-bit embeddable package is named `python-3.14.8-embed-amd64.zip` and is listed at 12.0 MB. This slot did not download it.

## What is already true

- `install()` writes `.cosmos-root.json`, the role directories, `config/install_key.bin` (32 random bytes), and `config/install_record.json`. A second install with a different tree id refuses `IDENTITY_MISMATCH`. Install does not mint `api_token.txt` and does not open a chat window. The live record stores a root path string beside `tree_id` and `installed_epoch`.
- `serve` binds `127.0.0.1:8770` unless asked for remote. A missing bearer is minted only on loopback. The banner points at `kdash/index.html`. That page is telemetry.
- `cosmos_service.py` imports `Kernel` and also imports the CVM projection and voice hardening modules at load. Those extra modules are outside this copy set.
- The OpenRouter rail imports `cosmos_packet` and `cosmos_rail_base` at load. No separate xAI rail file is in this copy set. The xAI door is still a wizard choice. The vendor key file is created on the peer, and its name is a denied member.
- `serve.bat` and `README.md` are `SHIP`. `README.md` still says pre-implementation. The kernel those pages describe is implemented. `serve.bat` expects an interpreter the clean machine does not have yet.
- cDeck under `builds/cdeck` is a Tauri skin. Its `src-tauri/target` output is `DENY`. A peer does not compile it inside this clock.

## What this proposal adds

`steps()` is seven allowances, in order: unpack runtime (20), apply cold root (10), key paste (30), mint secrets (10), write account (10), bind loopback (15), open the chat page (25). `total_seconds()` is 120.

Unpack extracts `runtime/python-3.14.8-embed-amd64.zip`. That zip is already inside the installer. Apply cold root writes the sentinel, the role directories, and the install record, and it leaves the install key to mint. Key paste is the person typing one OpenRouter or xAI key. Mint writes the loopback bearer and the 32-byte install key on that machine. Write account stores the display name, the door, a credential id, and the cap, without key bytes. Bind listens on `127.0.0.1:8770` with bearer auth. Open shows `app/dayone.html` on that origin. The page does not hold the bearer or the pasted key.

`members()` is an explicit file list. `cosmos/` is not a directory member. The kernel package is the named files under `cosmos/`, which are `SHIP`. The day-one page is `app/dayone.html`. The wizard page is `wizard/wizard.html`, with its static css and js. `kdash/index.html` stays in the payload because the current serve banner names it. It is not the chat window. `consider` refuses a `DENY` path with `DENY_MEMBER` before that path can become a member.

The payload omits `live/`, BU seat files, `api_token.txt`, `install_key.bin`, `serve.bat`, `README.md`, docs, probes, bytecode, and every cDeck path. Secrets and the cold root are created on the machine. The checkout keeps `README.md` and `serve.bat`.

## Refusal codes

- `DENY_MEMBER` — `repo_disposition` is `DENY`, or the path or the member reason matches a secret shape. `consider("live/config/api_token.txt")` raises this.
- `NOT_SHIP` — the path is not `SHIP` and is not an installer-built file under `runtime/`, `app/`, or `wizard/`. A bare `cosmos/`, `docs/`, or `kdash/` directory raises this so the copy stays a file list.
- `TOOL` — a step name or detail names npm, npx, cargo, git clone, rustc, or a compiler.
- `BUDGET` — the key-paste step is missing or is not 30 seconds, the other steps sum past 90, or the total passes 120.
- `BOUND` — a shared checker refused an empty or oversized name.

## How CCr lands it

CCr builds the installer artifact with `python-3.14.8-embed-amd64.zip` already inside, then the peer clock only unpacks it. CCr copies the named `SHIP` files and the static pages. CCr adds another `cosmos/*.py` file only when `repo_disposition` is `SHIP` and the day-one import path needs it. Probes, `__pycache__`, the live root, and cDeck stay out.

CCr gives `install_key.bin` a single writer in the secrets step. Cold root keeps the tree id and does not treat a drive path as identity. CCr serves the day-one page on loopback from a thin binder. Until that binder exists, `cosmos_service.py` remains the behavior source and its wider import graph stays a landing task, not a second copy of the whole tree. The spend ledger stays the one Core ledger. This clock does not add a wallet.
