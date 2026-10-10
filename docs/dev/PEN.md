# Pen

One Chief Coder (CCr) writes the COSMOS live tree. That hold is `CCR.lease`. Everyone else queues. This page is the developer map. The contract is `docs/CCR.md`. COSMOS is not finished. Naming the rule is not a claim that every write path checks it.

## One holder

The lease path is the configured root's `state/control` role, file `CCR.lease` (`cosmos/cosmos_ccr.py`, `lease_path`). Under the usual runtime root that file is `live/state/control/CCR.lease`. Do not assemble the path by hand. The resolver is `cosmos_paths`. Identity is the sentinel, not a drive letter.

`acquire` takes the lease for one session. A second acquire while that lease is live refuses with `CCR_HELD`. It does not steal a live writer and it does not write beside them. `assert_pen` requires a live lease whose session matches the caller. A missing lease is `CCR_NO_LEASE`. A different session is `CCR_SID_MISMATCH`. No lease means not CCr.

An empty lease file is not "no pen" and it is not permission to write. The Chief Coder takes the lease. Until that take, the pen is not held.

The file is a projection. Schema `cosmos-ccr-lease/2` carries a fencing token and an expiry. Schema `cosmos-ccr-lease/1` (no token) stays held until that same session releases. There is no TTL steal of a legacy lease. A new `/2` grant uses a 90-minute default TTL. Authority for the token, the TTL, and renew is `cosmos_lock.Arbiter` on resource `CCR.lease`. The projection is not the append-only ledger. `cosmos_ccr.py` does not write that ledger, and that file does not wire the check into Watchdog2. Callers check `held` or `assert_pen` themselves. Skill activate and reject do call `assert_pen`. That is not proof that every write path does.

## Do not print the token

The fencing token stays in the lease projection and in the arbiter record beside it (`CCR.lease.jsonl` under the same role). Do not copy it into docs, chat, proposals, commits, or a status paste. `status()` returns the lease record. Do not publish that record. This page does not print a token, a session id, or a sample lease body.

## Others queue

A session that does not hold the lease does not create, edit, move, rename, delete, or commit the repo tree or live core state. That covers `cosmos/`, `docs/`, `tests/`, `builds/`, governance, and `live/ledger`, `live/registry`, `live/config`, and `live/state` outside the drop zones.

Propose. A proposal names the target path, the action, the content or unified diff, and the rationale (principle P10). The contract's queue for the next CCr is:

- `work_orders/drop/`
- `work_orders/ccr/`
- `work_orders/ccr/proposals/`

Attempt-private work stays in `live/state/attempts/` and `live/work/`. Nothing there is authority until CCr files it through the fence. Removals are proposed as a stage into `_delme\`, never a delete. A rogue dirty tree is staged to `_delme\ccr-quarantine\` and ledgered. It is not silently overwritten from a backup.

Orchestrator and OpenWork do not hold this pen. Their CORE changes wait in that queue. OpenWork's folder grant is its own workspace, not this tree. Gitur (GitHub, GitLab, and Cursor) runs one job, one branch, one pull request. Gitur is not a second pen. Good output waits for the judge. Bad output is rerun. Do not merge past the judge. Do not put files on `main` by a second API. The pipe is `docs/CANON_PEN.md`. One git head is `docs/CANON_ONE_HEAD.md`.

## Taking the pen

When the pen is granted, other writers stop first (principle P12, Keith 2026-09-18). Stop means stop the write. A write already in flight may finish. Do not start a second write beside it. Do not kill the process. Ask before a session is closed, and say what is going on. A session that is only running has not taken the pen. Leave it open.

Then take `CCR.lease`. Then write. A claim of the pen while another writer is still live is the two-writer scar.

The same stop covers a farm or cloud writer that is writing `cosmos/` or merging, and an orchestrator applying while CCr also writes. One mouth.

## Two trees

GrokBot's pen is `V:\Ai` (BTS and LEGAL). The COSMOS pen is `V:\A`, including this repo. OpenWork writes only its grant tree. No two streams share a root. Mailbox before any shared write. A federated install has its own tree and its own Chief Coder. It does not write this one.

## Where the rule lives

| What | Where |
|---|---|
| Contract | `docs/CCR.md` |
| Pen receipt and the pipe | `docs/CANON_PEN.md` |
| One head | `docs/CANON_ONE_HEAD.md` |
| Assignment addendum | `docs/AGENT_BOUNDARIES.md` items 9, 12–14, 18–19 |
| Principles | P9, P10, P12, P13 in `cosmos/cosmos_principles.toml` |
| Lease module | `cosmos/cosmos_ccr.py` |

The contract says folder grant plus the lease is the protection. A social rule is not enough for a session that has not read it. Hiding the tree is not the protection. Overwriting it from a backup on close is the deletion scar. Do not do that.

This page does not say COSMOS is finished. The lease can refuse a second acquire. That is not a finished write-gate on every path.
