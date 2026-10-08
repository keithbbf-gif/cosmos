# wizard

Pure state machine for the day-one questions. It returns a frozen `Wizard`. It does not open a root, mint a bearer, bind a socket, or write a ledger.

## What I read

- `CONTRACT.md` wizard slot and the shared laws.
- `README.md` day-one sequence: label root, tree id, display name, one door, one pasted key, cap at or under one dollar, then loopback chat.
- `cosmos_federation` checkers: `check_tree_id`, `check_door`, `check_cap`, `secret_shape`, `const_eq`, `redact`, `bound_text`, `bound_int`, `Refuse`. Caps are `DEFAULT_CAP_USD_MICROS` (250000) and `MAX_CAP_USD_MICROS` (1000000). Doors are `openrouter` and `xai`.
- Live `cosmos/cosmos_kernel.py` `install` and live `cosmos/cosmos_service.py` `Service.__init__`, read only.

## What is already true

Live `install` writes `.cosmos-root.json`, the role directories, `config/install_key.bin` (32 random bytes when the file is absent), and `config/install_record.json`. The record stores `root` as `str(root)`, `tree_id`, and `installed_epoch` from `time.time()`. A second install with a different tree id raises `IDENTITY_MISMATCH`. Install does not mint `api_token.txt`, does not open a ledger, and does not open a chat window.

Live `serve` binds `127.0.0.1:8770` unless the bind is remote. Remote without TLS raises `REMOTE_CLEARTEXT` unless `insecure_http` is set. Remote with `--no-auth` raises `REMOTE_OPEN_ACCESS`. A missing token on a remote bind is `TOKEN_MISSING`. The serve banner points at `kdash/index.html`, which is telemetry. There is no first-run wizard in that page.

`docs/CREDENTIALS_NEEDED.md` still lists an Anthropic filename for the Claude rail. Day-one doors in this federation are OpenRouter and xAI. This wizard refuses Anthropic through `check_door`.

## What this proposal adds

`begin(now)` starts at `root`. `submit` then accepts `tree_id`, `name`, `door`, and, after `accept_key`, `cap`, then `bind`. `now` is a caller epoch. The module does not call `time.time`.

`root` is a non-empty label. A slash, a backslash, a drive colon, or a dot segment raises `ROOT`. The function never builds a filesystem path from that label.

`tree_id` goes through `check_tree_id`. `name` is a short display string. `door` goes through `check_door`, which folds `OpenRouter` and `XAI` and refuses Anthropic with `ANTHROPIC_OFF`.

`accept_key` runs only on the key step, after door and before cap. It checks the stored door again, refuses a paste or credential id that contains `sk-ant-` by calling `check_door("anthropic")`, and refuses a paste that is not `secret_shape`. The marker is not required to be a prefix: a leading space, a tab, or a Bearer wrapper still matches `secret_shape` and would otherwise be accepted. The marker check runs before the length cap, so a long Anthropic paste is `ANTHROPIC_OFF`. It stores `credential_id` only. An id that is secret-shaped, or that compares equal to the paste with `const_eq`, raises `KEY`. `repr(Wizard)` prints the id and the other answers, then passes the text through `redact`. The paste is not a field.

`cap` is a digit string. `check_cap` enforces 1 through `MAX_CAP_USD_MICROS`. `RECOMMENDED_CAP_USD_MICROS` equals `DEFAULT_CAP_USD_MICROS` for the UI. `begin` does not fill it in.

`bind` accepts `loopback` or `remote`. `loopback` skips tls, sets the step to `confirm`, and `ready` is true. `remote` returns a wizard whose step is `tls` and whose `ready` is false. The next legal submit is `tls`. The value `yes` enters `confirm` and `ready` becomes true. Any other tls value raises `REMOTE_PLAIN`. tls is not legal before a remote bind, and it is not legal after loopback. There is no `insecure_http` answer in this slot.

`ready` is true only when the step is `confirm` and every required answer is set. Remote also requires `tls == "yes"`.

## Refusal codes

- `STEP` — field is not the current step, submit ran on the key step, tls ran before remote bind, or a call arrived after confirm.
- `BOUND` — epoch, label, name, or credential id failed `bound_int` / `bound_text`, or the text had padding whitespace.
- `ROOT` — root label is path-shaped. The wizard does not open it.
- `SECRET` — root or name matches `secret_shape`. The detail does not echo the text.
- `TREE_ID` — `check_tree_id` refused the id.
- `DOOR` — `check_door` refused an unknown door.
- `ANTHROPIC_OFF` — `check_door` refused an Anthropic door, or a paste or credential id that contains `sk-ant-`.
- `KEY` — paste is not `secret_shape`, or the credential id is key material.
- `CAP` — cap is not a digit string, or `check_cap` refused the integer.
- `BIND` — bind is not `loopback` or `remote`.
- `REMOTE_PLAIN` — remote bind is waiting on tls and the submit is not `yes`.

## How CCr lands it

The setup route calls this machine in order and passes the caller epoch. The HTTP layer holds the paste for the `accept_key` call and then drops it. This module never had a place to log it. `wizardhtml` clears the field on the page.

On `ready`, CCr reads `root`, `tree_id`, `name`, `door`, `credential_id`, `cap_usd_micros`, `bind`, and `tls`. The label goes to the path step as a name, not as identity. `tree_id` is the sentinel identity and matches `coldroot`. `credential_id` goes to `account` and `seat`. The paste itself stays in the secrets writer for that one call, which is a different slot. `cap_usd_micros` is the day-one fold passed to `spendcap`. Core's ledger stays the authority when the fold and the chain disagree.

`bind=loopback` maps to `127.0.0.1:8770` in `bindpol`. `bind=remote` with `tls=yes` maps to a TLS serve. `REMOTE_PLAIN` is this slot's name for the live `Service` refusal `REMOTE_CLEARTEXT`. Day one does not surface `insecure_http`.

Files in this slot: `MAP.md`, `wizard.py`, `test_wizard.py`.
