# secrets

## What I read

I read `CONTRACT.md` (slot secrets), `README.md`, and the live functions `_load_api_token` and `_write_private` in `V:\A\Ai\COSMOS\cosmos\cosmos_service.py`. I read `install` in `cosmos\cosmos_kernel.py` for the existing install-key write. I did not read `live\config`. I used `cosmos_federation` for `PathJail`, `Refuse`, `bound_int`, `bound_text`, `secret_shape`, and `ROLES`.

## What is already true

Loopback serve mints `config/api_token.txt` only when the file is absent. The mint is `token_urlsafe(24)`, encoded as UTF-8 with no added newline, and written through `_write_private`. That helper opens with `O_WRONLY | O_CREAT | O_TRUNC` and mode `0o600` before the first byte. Serve then strips the file. An empty or whitespace token is `BLANK_TOKEN`. A remote bind does not mint. It raises `TOKEN_MISSING`.

`install` creates the sentinel, the role directories (including `config`), and `config/install_key.bin` when that file is absent. The body is 32 bytes from the operating-system random source, written with `write_bytes`, not with `_write_private`. A second install keeps the existing key. This proposal does not edit that function.

## What this proposal adds

`mint(draw, now)` asks `draw` for 24 bytes and then 32 bytes. The first block becomes a url-safe bearer with padding stripped, the same construction as `token_urlsafe(24)`. The second block is the install key. `Mint.show_token` holds the bearer until `acknowledge`. `token_id` is 12 hex characters of SHA-256 over the bearer UTF-8. `key_id` is 12 hex characters of SHA-256 over the 32 key bytes. Those inputs are the file bodies, so an id can be checked against disk after the raw material is dropped.

`acknowledge` returns a new mint with `show_token` and the key bytes cleared. `token_id`, `key_id`, and `minted_epoch` stay. `__repr__` prints only a 12-hex id or the word `hidden`, plus the epoch and whether a bearer is still held. It does not print the bearer or the key.

`write_files` writes `config/api_token.txt` and `config/install_key.bin` inside a `PathJail`. Both use the live open flags and mode `0o600`. The token file is the stripped bearer and does not gain a newline. The library does not read the clock and does not draw from the operating system.

Files in this slice: `MAP.md`, `secrets.py`, `test_secrets.py`.

## Refusal codes

- `BLANK_TOKEN` — token missing, not a string, or only whitespace.
- `BAD_KEY` — key is not a `bytes` object of length 32.
- `DRAW` — `draw` is missing or did not return the requested number of bytes.
- `SECRET_SHAPE` — the minted bearer matched a vendor-key shape.
- `BOUND` — `now` or the token text is outside its bound.
- `JAIL` — the writer was not given a `PathJail`.
- `MINT` — `acknowledge` was not given a `Mint`.

`TOKEN_MISSING` stays in live serve. This module does not raise it. A remote bind must not call `mint`.

## How CCr lands it

Keep the remote branch of `_load_api_token` on `TOKEN_MISSING`. On loopback, call `mint` with a draw that returns fresh bytes, show `show_token` once, call `write_files`, then `acknowledge` before the mint is stored on the server. Replace the `install` write of `install_key.bin` with `write_files` so coldroot and this slot do not both own the file. Coldroot still creates the sentinel, the role directories, and `config/install_record.json`. Leave Core's ledger and the serve banner alone.
