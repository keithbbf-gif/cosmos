# account

## What I read

I read `CONTRACT.md` slot `account` and the laws above that slot. I read `README.md`. I read `check_door` and `secret_shape` in `cosmos_federation`, plus `bound_text`, `bound_int`, and `Refuse`. On the live tree I read the source-id table in `cosmos/cosmos_cred_kit.py`, the header of `cosmos/cosmos_openrouter_rail.py`, the Anthropic key-file constant in `cosmos/cosmos_claude_rail.py`, and the profile list in `cosmos/cosmos_profiles.py`. I did not open key files and I did not copy key bytes.

## What is already true

The live kernel stores vendor keys as files under the runtime `config/` role. OpenRouter's file name is `openrouter_api_key.txt` (fill-first also looks at numbered copies). xAI's file name is `xai_api_key.txt` and its link id is `sgh-api`. Anthropic's file name is `anthropic_api_key.txt` on a rail that still exists in the kernel. Cred-kit GET does not return secret material. Profiles are occupancy skins (forge, crucible, and the rest), not a peer login. Identity in the kernel is a tree id. There is no frozen account object that pairs a display name, a day-one door, and a credential id without the key bytes.

## What this proposal adds

`open_account(name, door, credential_id, now)` returns a frozen slotted `Account` with `name`, `door`, `credential_id`, and `created_epoch`. The door value is the folded `check_door` result, so the stored door is `openrouter` or `xai`. The name and the credential id are short strings capped at 80. `now` is the caller's epoch and this module does not read the clock. The object has no key-byte field. `repr` redacts every string, so a later slot poke still cannot print a secret shape. `SCHEMA` is `cosmos-federation-account/1`.

## Refusal codes

- `BOUND` — blank, empty, or over-long name (`name`, limit 80); empty, blank, or over-long credential id (`credential_id`, limit 80); `now` that is not an int, is a bool, is negative, or sits above the signed 64-bit epoch (`now`).
- `SECRET` — `name` or `credential_id` matches `secret_shape`. The detail is empty, so the exception text does not echo the value. A long key is `SECRET`, not `BOUND`.
- `ANTHROPIC_OFF` — the door is Anthropic or Claude, from `check_door`.
- `DOOR` — any other door, from `check_door`, including a non-string door.

## How CCr would land it

CCr reviews this slice, then lands it through one Gitur branch and one PR. The live tree stays the only write target. The landed module keeps storing the credential id the peer minted on their own machine. It does not read `live/config`, it does not copy Keith's key files, and it does not turn the Anthropic rail on. A later seat slot binds that id to a pin and a cap. The key bytes stay in the secrets slot's config files.
