# updater

## Read

- `V:\streams\federation\CONTRACT.md`, slot `updater`.
- `V:\streams\federation\README.md`.
- `V:\A\Ai\COSMOS\README.md` (still says Pre-implementation).
- `V:\A\Ai\COSMOS\docs\federation\UPDATE_SERVICE.md`.
- `V:\A\Ai\COSMOS\docs\federation\GRAYSON.md` (peer pulls, or the hub pushes, the same packet).
- `cosmos/cosmos_kernel.py` `install()` and `cosmos/cosmos_paths.py` sentinel, read-only.

## Already true

The live installer stamps one root. `install()` writes `.cosmos-root.json`, the role directories, `config/install_key.bin`, and `config/install_record.json`. A second install with a different tree id refuses `IDENTITY_MISMATCH`. The sentinel carries `system`, `tree_id`, and `schema_version` (default 1). That `schema_version` is the install stamp. It is not an update counter.

`UPDATE_SERVICE.md` names the meeting point for comms and for OS/app packets. The hub host is not chosen. T7920 and SRV1 are both still `NO_HOST`. The service does not become Core, CCr, or Crucible, and it does not silently overwrite a peer. The peer applies through its own fenced commit or refuses. The packet carries hash and identity. `cosmos_mail` has a schema and no transport until a host is named and a tick lands. This proposal does not name that host and does not open a socket.

## This proposal adds

`verify` checks one in-memory packet against the caller's tree id and last applied version. `stage` writes only `updates/<version>/payload.bin` inside a `PathJail`, and only after `verify`. The staged file is the raw payload, not an envelope. The running tree, the sentinel, the install record, and every other file stay untouched. `local_version` is an argument. This module does not read a sentinel or a ledger to discover it.

`sha256` must equal `hashlib.sha256(payload).hexdigest()` (lowercase hex). `signer_id` is an id string. `UpdateOk` holds the new version and the byte length. It also pins that digest so `stage` can hash the bytes it is about to write. The pin is not part of equality. `repr` of that result does not include the payload, the digest, or the signer id.

`SCHEMA` is `cosmos-federation-updater/1`.

## Refusal codes

Checked in this order:

| Code | When |
|---|---|
| `BOUND` | The packet is not a mapping, a required field is missing or the wrong type, a string or int is outside its cap, `version` is a bool, or `now` is outside `0 .. 10**18`. |
| `UNSIGNED` | `signer_id` is `""`. |
| `SECRET` | `signer_id` matches `secret_shape`. The detail does not echo the value. |
| `TREE_ID` | Either id fails `check_tree_id`, including `GMesh`, `KMesh-COSMOS-live`, and `live`. |
| `TREE_MISMATCH` | Both ids are valid and they differ. |
| `DOWNGRADE` | `version` is not greater than `local_version`. Equality is a replay, not an update. |
| `BAD_HASH` | `sha256` does not match the payload bytes. `stage` hashes its second read and refuses when that is not the digest `verify` pinned, including a same-length swap. |
| `PRESENT` | `updates/<version>/payload.bin` is already on disk. `stage` does not replace it. |
| `JAIL` | `stage` was not given a `PathJail`. |
| `PATH` | `PathJail.contain` rejects the destination. The version path is a decimal int, so this is the jail's own escape refuse. |

A failed `verify` writes nothing.

## How CCr lands it later

The peer's own writer, under that peer's lease, reads the staged file, hashes it again, and commits it through the fenced gate onto that peer's root. The hub does not receive a lease on the peer. `schema_version` moves only inside that commit, if the peer's writer moves it. Core's ledger stays the authority for the apply. If a staged file and the chain disagree, the chain wins and the running tree stays as the chain left it. The hub process, when a host is finally named, ships the same packet this module already checks. It still does not overwrite the peer.
