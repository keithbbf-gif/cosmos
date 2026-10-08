Applied 2026-10-07 from V:\streams\federation onto this tree. The streams original stays in place. Nothing here writes live/, takes CCR.lease, opens install_key.bin, or becomes a second Core or ledger. Live COSMOS seams stay the authority.

# Federation — day-one peer install

Propose-only. This folder does not write `V:\A\Ai\COSMOS` and it is not a second Core.

The public repo is [keithbbf-gif/cosmos](https://github.com/keithbbf-gif/cosmos).
The live checkout on this machine is that repo plus a dirty working tree. A new
machine does not get this machine's `live/` root, keys, or seat files.

## What a new person gets in two minutes

The clock starts when the installer file is already on disk. It ends when a
window on `127.0.0.1:8770` shows a live model reply.

1. The installer creates one runtime root anywhere the person can write.
   Identity is `.cosmos-root.json` (`system=COSMOS` plus a tree id they choose).
   It is not a drive letter and it is not `KMesh-COSMOS-live`.
2. A local wizard asks for a display name, a tree id, one door (OpenRouter or
   xAI), one key they paste themselves, and a spend cap at or under one dollar.
3. The installer mints `config/api_token.txt` and `config/install_key.bin` on
   that machine, shows the bearer once, and then keeps only ids in memory.
4. Core serves loopback only. The browser opens `/dayone`. A one-time nonce
   sets an httpOnly cookie. The page never contains the bearer or the model key.
5. The first chat turn goes out through the door they chose, under the cap.
   The reply is painted in the same window.

Anthropic is off. The installer does not read another person's keys, does not
open `D:\R2Cloner`, and does not drive a browser login. DOM stays the preferred
path after a person has a vendor session of their own. A clean machine has no
such session, so day one is the key they just pasted.

## What is not in the two minutes

cDeck's Tauri shell, npm, a Rust compile, Tailscale, R2, phone voice, Crucible,
a second ledger, and Keith's live tree. Those are later doors. The serve line
today tells a peer to open `kdash/index.html` and to already have Python 3.14.
Neither is a two-minute clean install.

## Layout

- `CONTRACT.md` — law for every proposal.
- `cosmos_federation/` — shared refusals, path jail, and product constants.
- `proposals/<slug>/` — one reviewable slice: `MAP.md`, the module, and tests.

Read `CONTRACT.md` before adding a slice.
