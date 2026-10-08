# COSMOS CODE

Snapshot of main `501fdee25a581648ee0ddb096bdafa70a2325a71`.

## What it is

Propose-only coding rail. G47 plans the harness call. This package jails the worktree, requires a red oracle before a nontrivial edit, and grades Python with the 4Cs.

`propose()` always returns `done: false`. `dispatch` stays locked: `Provider.prepare_call` raises `DISPATCH_LOCKED` and does not send HTTP. The enclosure reason is `policy_only`. `wipe_proof` is false. Seeing `bwrap` on `PATH` is not an attached enclosure.

Default posture is WOMBAT: mode propose, sandbox workspace-write, approval on request, delete policy archive-only. CCr publishes. This package does not write `live/`.

## Where it lives

`cosmos_code/` at the repo root. Library code is `cosmos_code/cosmos_code/`. Door rows are `specs/*.toml`. Tests are `cosmos_code/tests/`. Import inserts `harness/G47` on `sys.path`. It does not own the live runtime root.

## Entry points

- `py -3.14 -m cosmos_code doctor` — default hooks and the enclosure label.
- `py -3.14 -m cosmos_code enclosure` — JSON enclosure status.
- `py -3.14 -m cosmos_code scars <text>` — a scar name, or `clean`.
- `py -3.14 -m cosmos_code refuse-retry` — unsandboxed retry must raise.
- `py -3.14 -m cosmos_code check <tree>` — one 4C receipt per tool.
- `propose(legend, door, worktree, ...)` — session log, optional red oracle, jailed writes, then G47 `plan`. The return field `done` is false.
- `cosmos_code.own.seat_here` — writes a G47 pack into an attempt. It does not start the native door and it does not start `grok.exe`.

## What it refuses

Named refusals include `LIVE_TREE`, `UNKNOWN_DOOR`, `NO_ORACLE_SPEC`, `NO_SHOT1_IR`, `PLAN_UNBOUND`, and `DISPATCH_LOCKED`.

The path jail refuses `..`, a drive-relative path, UNC, encoded dot-dot, a null byte, a bare drive root, and a `file:` URL. A path outside the grant list is refused. `JailedFS` refuses a write under `live/`.

Hooks deny a format command and a force-push. A delete-shaped shell command or a delete tool is denied and rewritten toward archive. `refuse_unsandboxed_retry` always raises.

A nontrivial edit needs a red oracle whose command fails before the write. The oracle cwd cannot be `live/`. Done needs a `DoneBundle` of five non-empty hashes: `diff_hash`, `oracle_id`, `oracle_log_hash`, `pack_hash`, `cmd_hash`. Green prose is not done.

A door spec that omits a layer, uses an unknown bind state, or names a door G47 does not have raises `SPEC_INVALID` or `SPEC_UNKNOWN_DOOR` at load.

## What it is not

Not a provider. Not a start of `grok.exe`. Not the Core ledger and not `CCR.lease`. Not wipe-proof. Not G47: G47 only builds the thin pack, and `execute` on the cosmos-code door raises `EXECUTE_IS_RAIL`. Not a fifth checker. The archive rewrite is not the authority ledger.

## Grade

4C is `py_compile`, `ruff`, `mypy`, `pytest`. No fifth C. A missing tool is `MISSING` (receipt return code 127). `pytest` exit 5 is `NO_TESTS`. `FAIL` and `MISSING` block. `NO_TESTS` does not.

`python -m cosmos_code check` exits 0 when the only bad row is `NO_TESTS`, because `fails_of` treats only `FAIL` and `MISSING` as blocking. The harness verify hook blocks any status that is not four `PASS` rows. That mismatch is real.

Package 4C for this tree passed at this tip. Run the four tools inside `cosmos_code/`, not as a repo-root scan. A root scan walks `live/`.
