# coldroot

## What I read

I read `CONTRACT.md` for the coldroot slot and the shared laws. I read `README.md` for the day-one identity rule: `.cosmos-root.json` carries `system=COSMOS` plus a tree id the person chooses. I read `cosmos_federation/product.py` for `ROLES` and `check_tree_id`. I read live `cosmos/cosmos_paths.py` `write_sentinel` and live `cosmos/cosmos_kernel.py` `install`.

## What is already true

`write_sentinel` writes `.cosmos-root.json` with `system`, `tree_id`, and `schema_version`, in that order, via `json.dumps(..., indent=1)`. The system value is `COSMOS`. `schema_version` is an argument that defaults to `1`. `install` does not pass another value, so the stamp is `1`.

`install` writes that sentinel first, then creates every directory in the role table, including `root` as `.`. It writes `config/install_key.bin` when the file is missing (32 bytes from `os.urandom`, no mode bits) and always rewrites `config/install_record.json` with `root` (`str(root)`), `tree_id`, and `installed_epoch`. The epoch is a `time.time()` float. A second install whose sentinel `tree_id` is a different non-empty value raises `IDENTITY_MISMATCH`. The check is `cur.get("tree_id") not in ("", tree_id)`: a missing `tree_id` also refuses, and an empty string is unfinished, so `install` completes it. The same tree id does not raise. An existing `install_key.bin` stays. The record does not stay byte-for-byte: `installed_epoch` becomes a new `time.time()`. The docstring calls that path idempotent. `install` does not read the existing record before overwriting it, and it leaves `api_token.txt` unwritten.

`CosmosPaths.from_install_record` reads `root` out of that record and opens it.

## What this proposal adds

`plan(tree_id, now)` describes the sentinel body, the role rows, and the record keys. It writes nothing. `apply(jail, tree_id, now)` creates the role directories inside a `PathJail` and writes `.cosmos-root.json` and `config/install_record.json`.

The sentinel keys are `system`, `tree_id`, and `schema_version`. The JSON text matches `write_sentinel`: `json.dumps(..., indent=1)` with those keys in that order. Live `write_text` does not pass `newline`, so on Windows those bytes are CRLF. This slot forces LF so two machines emit the same bytes.

The record keys are `tree_id` and `installed_epoch`. The epoch is the int the caller passes. Identity stays in the sentinel. The jail path stays in the caller's hand.

Role rows come from `cosmos_federation.ROLES` in table order. The `tools` row is the directory `cosmos`. The `root` row is `.`, which is the jail itself, so `apply` creates the other directories only.

Live `install` writes `config/install_key.bin`. This slot leaves that file, and `config/api_token.txt`, to the secrets slot. One writer owns the key.

A repeat `apply` with the same tree id rewrites the sentinel and sets `installed_epoch` from the caller clock. It keeps one identity and mints no key. The same arguments write the same bytes. A different existing tree id on the sentinel or the record raises `IDENTITY_MISMATCH` and leaves both files as they were. An empty `tree_id` is unfinished, matching live `install`, and `apply` may finish it.

## Refusal codes

- `TREE_ID` — `check_tree_id` rejects a taken, empty, malformed, or secret-shaped id.
- `BOUND` — `now` is outside the int epoch range, or a public object is the wrong shape.
- `IDENTITY_MISMATCH` — an existing sentinel or install record carries a different tree id, or the two halves of a plan disagree.
- `UNPARSEABLE` — an existing sentinel or record is torn, or its `tree_id` is not a string.
- `UNREADABLE` — an existing sentinel or record cannot be read.
- `NOT_A_DIRECTORY` — a role path exists and is not a directory.
- `JAIL` — `apply` was given something other than a `PathJail`.
- `PATH` — `PathJail` rejects an empty, absolute, UNC, or `..` relative name.

## How CCr lands it

CCr keeps `write_sentinel` as the sentinel writer. `install` stops putting `root` in `config/install_record.json` and stores the caller epoch as an int. The `install_key.bin` write moves to the secrets slot, which draws the 32 bytes from the caller's `draw` and creates the file at mode `0o600`. `from_install_record` takes the root as an explicit argument and checks sentinel content against `tree_id`. It stops opening a path stored in the record.

Today's `from_install_record` still requires `root` and refuses when that key is missing. This proposal's record is the shape after that landing. It is not a file today's constructor accepts. A second install whose tree id differs still raises `IDENTITY_MISMATCH`.

## Files

This directory holds `MAP.md`, `coldroot.py`, and `test_coldroot.py`.
