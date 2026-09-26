# Gitur job 2 — P07 Layer A spawn grant ≠ Layer B fencing token

**After:** cosmos #128 `ccr/p11-seed-bite` (do not mix into that PR).
**Repo:** `keithbbf-gif/cosmos`
**Branch:** `ccr/p07-layer-a-b`
**From:** GitHub `main` blob. Do not pull unique HEAD. Not cDeck. No ballot. No IAM/AD.

## Gap (live)

- Layer B exists: `cosmos/cosmos_lock.py` monotonic fencing tokens + fenced commit. Stale token REJECTED.
- CCr occupancy exists: `cosmos/cosmos_ccr.py` `CCR.lease` (`sid/pid/stream/tree_id/taken_at`). **Not** a spawn grant. **No** `fencing_token` field on the lease blob.
- P10 workspace fence exists: `cosmos/cosmos_dispatch_workspace.py` `assert_not_live_workspace` — Python path check, not a spawn token.
- Missing: a Layer A **spawn grant** (folder = pen) issued at worker spawn, a different object from the Layer B fencing token. Collapsing A into B is the failure.

## Must not invent

IAM, Active Directory, extra Windows logins, a second Core, in-place ledger repair, ballot writer.

## Bite

1. Pin old: spawn grant and fencing token can be the same string / missing grant still publishes.
2. Fix: `SpawnGrant` (folder root + sid) ≠ lock fencing token. Worker write outside grant refuses (`GRANT_DENIED` / `EACCES` analog). Publish without current fencing token still `STALE_TOKEN` / `NO_LEASE`.
3. `_bite_p07_layer_ab.py` `all_bite:true`. Live files unchanged on both refusals.

## Reuse

`cosmos_lock.py` fencing. `assert_not_live_workspace`. `_delme\ccr-quarantine\`. Folder grant = pen.
