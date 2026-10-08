# ledgerboot

Cold-start pair for the one spend ledger. This slice does not write the live COSMOS tree and it does not open `live/ledger`.

## What I read

- `CONTRACT.md` laws and the `ledgerboot` slot.
- `README.md`: a day-one peer gets one install, and spend stays one append-only ledger.
- `cosmos_federation.product.DEFAULT_CAP_USD_MICROS` (`250000`) and `check_tree_id`.
- The head of `cosmos/cosmos_ledger.py`. The live authority is an append-only JSONL chain. A record carries `seq`, `event`, a canonical payload and its sha256, `prev_sha`, `writer`, and an HMAC made with the install key. The first `prev_sha` is an empty string. Later records store the sha256 of the previous full line. A corrupt record refuses. History is not repaired in place.
- `cosmos/cosmos_kernel.py` opens that chain as `ledger/authority.jsonl` with the install key and a signed head sidecar `authority.jsonl.head.json`. A writing kernel appends `BOOT_VERIFIED` when it opens. Install does not open a ledger.

## What is already true

The live chain name is `ledger/authority.jsonl`. Core owns that filename. The chain is service-authenticated with the install key. The first live link is an empty `prev_sha`, not a run of zero hex. A day-one cap is a fold of ledger events, not a second wallet. A second install that names a different tree already refuses `IDENTITY_MISMATCH`. The kernel boot path does not append `INSTALL` or `CAP_SET`.

## What this proposal adds

`genesis(tree_id, now)` returns two frozen events, `INSTALL` then `CAP_SET`. Both carry the caller epoch. The first `prev` is 64 zeros. `hash` is the sha256 hex of the other fields as canonical JSON: keys sorted, separators comma and colon, no whitespace, and no `hash` field. `CAP_SET` adds integer `cap_usd_micros` set to `DEFAULT_CAP_USD_MICROS`. `INSTALL` has no cap field, no token, and no key bytes.

`apply(jail, tree_id, now)` writes `ledger/genesis.jsonl` under the path jail, one JSON object per line. The same tree id leaves those bytes in place and does not append a second copy, including when the later call passes a different epoch. A different tree id raises `IDENTITY_MISMATCH`.

`ledger/genesis.jsonl` is this proposal's cold-start chain only. It is not a second authority. If this file and the Core chain ever disagree, the Core chain wins.

## Refusal codes

- `TREE_ID` — rejected tree id, including taken names and secret-shaped text.
- `BOUND` — epoch is not an int from 0 through 2**62.
- `CAP` — the shared cap check, if the product constant ever leaves day-one policy.
- `JAIL` — `apply` was not given a `PathJail`.
- `IDENTITY_MISMATCH` — the cold-start file already names another tree.
- `TORN` — the cold-start path exists but is not a small UTF-8 JSON object this slot can identify, or the ledger directory cannot be created.

## How CCr lands it

Append the same two facts onto `ledger/authority.jsonl` in Core's record shape, with Core's `prev_sha` rule and the install-key HMAC. Keep one chain. Do not keep `genesis.jsonl` as authority, and do not rename `authority.jsonl` from this proposal. Point the spend fold at `CAP_SET`'s `cap_usd_micros` (`250000`, under the one-dollar ceiling). Leave key minting in the secrets slot. `BOOT_VERIFIED` stays the kernel's open event; `INSTALL` and `CAP_SET` are the day-one facts that open does not write today.
