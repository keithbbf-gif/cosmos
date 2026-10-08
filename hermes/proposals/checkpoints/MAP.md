# Checkpoints

Hermes snapshots a working tree before `write_file`, `patch`, and destructive terminal commands, at most once per directory per turn. Checkpoints are opt-in. A shared shadow git store keeps one ref per project. `/rollback` lists those commits. `/rollback N` restores files the agent changed and skips human edits whose bytes no longer match the agent-write ledger. `/rollback N --all` restores every captured file. `/rollback diff N` previews the delta. `/rollback N <file>` restores one path. A restore records a pre-rollback snapshot first. Oversize files, huge trees, root and home, missing git, container backends, and nested gitlinks are skipped or refused. Snapshot count and store size are capped. An unchanged tree does not add a commit.

The live seam is the attempt workspace in `cosmos/cosmos_sandbox.py`. This proposal adds an in-memory record on that seam. It does not call git and it does not write disk.

`Checkpoints.snapshot` stores sha256 and bytes for each relative name and appends a hash-chained `Fence`. `rollback` returns the prior bytes and does not move the head. `read` returns the current bytes. `digest` returns the current sha256. `catalog` lists current records in name order. `fences` lists the chain. `records` emits that chain as text. `rebuild` replays fences or that text into the same catalog. The second snapshot of a name keeps the first generation as the rollback target and the second as current. A third snapshot drops the first generation's bytes and rolls back to the second. An equal sha256 does not move the prior and does not append a fence. Names are content keys: an absolute name, a `..` segment, or a backslash is `BAD_NAME`. Two names that decode to one path are `DUP`. A fence sha that does not match its body is `CHAIN`. A fence that does not link from `GENESIS` through the tip is `STALE`. Malformed records raise `Refuse` with `BAD_RECORD`, not `ValueError`. A requested cap above policy is ignored, and the policy cap is recorded on `Policy` and on `Snapshot`.

Authority sits in the attempt workspace. The store is the snapshot. There is no ledger write and no host path.

Refusal codes: `BAD_LIMIT`, `BAD_NAME`, `BAD_RECORD`, `CAP`, `CHAIN`, `DUP`, `EMPTY`, `NO_PRIOR`, `NO_SNAPSHOT`, `NOT_BYTES`, `NOT_INT`, `NOT_MAP`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `SECRET`, `STALE`.

## Ship

- operations: `SCHEMA`, `GENESIS`, `POLICY_HISTORY`, `POLICY_MAX_FILE_BYTES`, `POLICY_MAX_FILES`, `POLICY_MAX_GENERATIONS`, `POLICY_MAX_NAME`, `POLICY_MAX_TOTAL_BYTES`, `Chain`, `Checkpoints`, `Fence`, `FileRecord`, `Policy`, `Snapshot`, `rebuild`
- refusal codes: `BAD_LIMIT`, `BAD_NAME`, `BAD_RECORD`, `CAP`, `CHAIN`, `DUP`, `EMPTY`, `NO_PRIOR`, `NO_SNAPSHOT`, `NOT_BYTES`, `NOT_INT`, `NOT_MAP`, `NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `SECRET`, `STALE`
- what this module still refuses to execute: git, a host-path restore, a disk write, a second prior byte generation, a cap raised by the caller, and a partial batch when one name fails
- hot-path shape: one pass over the batch, one sha256 per blob, skip an unchanged digest, refuse the whole batch when a name, a secret, or a cap fails

CCr would call `snapshot` from the attempt workspace before a destructive tool and would apply `rollback` bytes only inside the workspace jail when a human restores. Policy caps stay where this module clamped them. The shadow git store is not ported.
