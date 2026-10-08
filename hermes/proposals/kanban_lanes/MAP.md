# kanban_lanes

Hermes kanban routes a card to a worker lane. A lane is one assignee, one spawn shape, and a cap on assignments that are active at the same time. The kanban kernel keeps lifecycle truth (`ready`, `running`, `review`, `blocked`, `done`, `archived`). A lane records an assignment and a terminator. It does not own that truth. An assignee that is not on the board stays unclaimed. The spawn shape is an argv list. A shell string is not a spawn shape. A crashed assignment is recorded once and may be retried once, and only for the failure class `crash`. A second automatic requeue is the breaker. Descendant processes are not the owner of the claim.

The live seam is no spawn. `cosmos/cosmos_platform.py` already accepts argv lists and refuses a shell string. `cosmos/cosmos_delegate.py` already ignores a caller who asks for a higher concurrency cap. Neither module owns a kanban lane. This proposal does not import them. Lanes here are assignments, not processes.

## Operations

`make_lane` stores the assignee, the kind (`profile` or `external`), the credential id, the interpreter allowlist, and the caps. `policy_cap` is 4. `worker_cap` is the lesser of the request and 4. A higher request is stored on `requested_cap` and does not raise the enforced cap. An empty allowlist, a missing credential id, an unknown kind (`off` and `yolo` included), a duplicate assignee, or a raw key shape refuses. No path is accepted.

`make_board` copies those lanes into an empty assignment ledger and seals one hash-chained lane event per lane.

`spec_argv(interpreter, script)` returns a fresh list of two strings. It does not start a worker. A single string command raises `SHELL_STRING`.

`assign` appends one `ASSIGNED` row whose argv is that list. The running count is the number of `ASSIGNED` rows on the lane. When that count would pass `worker_cap`, `assign` raises `LANE_FULL` and appends nothing. The interpreter must be on the lane allowlist. The credential id must match the lane. The fence is single-use. A clock that moves backwards is `STALE`.

`crash` records one crash and sets that row to `REQUEUED` with `requeues` 1. A requeued row does not occupy the cap. A second crash on a row that already carries a crash or a requeue raises `REQUEUE_CAP`.

`retry` is the one confirming retry, and only when `failure` is `crash` and the latest row for the card is `REQUEUED`. Any other failure class is `NO_RETRY`. A second confirming retry is `RETRY_CAP`.

`terminate` records `COMPLETE`, `REVIEW`, or `BLOCK` on an `ASSIGNED` row. `BLOCK` is stored as `BLOCKED`. Any other action, including `off` and `yolo`, is `UNCLASSIFIED`. The terminator is a record. It is not executed.

`spawn` validates the board, the lane, the credential, and the card, then raises `NO_SPAWN`. It does not start a worker and it does not append an event.

`rebuild` replays the event log. The same events reproduce the same board. A broken prev hash is `CHAIN`. A repeated event id is `DUPLICATE`.

## Authority

The kanban ledger is the authority for lifecycle truth. This module returns frozen records a later guarded append would store. It does not write a database, open a workspace, read a clock, or start a worker. The caller passes `now`. Authority to execute the argv list stays outside this proposal. A lane assignment is not a process, so this module cannot hand a claim to a child.

## Refusal codes

`BAD_ARGV`, `BAD_ASSIGNMENT`, `BAD_BOARD`, `BAD_EVENT`, `BAD_FENCE`, `BAD_ID`, `BAD_LANE`, `BAD_LIMIT`, `BAD_SCHEMA`, `CHAIN`, `CLOSED`, `CRED_MISMATCH`, `DUPLICATE`, `EMPTY_ALLOW`, `EMPTY_ARG`, `LANE_FULL`, `MISSING_CRED`, `NOT_ALLOWED`, `NOT_ASSIGNED`, `NOT_INT`, `NOT_TEXT`, `NO_RETRY`, `NO_SPAWN`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `REPLAY`, `REQUEUE_CAP`, `RETRY_CAP`, `SECRET`, `SHELL_STRING`, `STALE`, `UNCLASSIFIED`, `UNKNOWN_ASSIGNMENT`, `UNKNOWN_LANE`, `UNKNOWN_MODE`.

`NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, and `OUT_OF_RANGE` come from `bound_text` and `bound_int` when the caller hits those bounds. Credential ids and fences are compared with `const_eq`. `repr` of a returned record stays free of raw key shapes.

## Landing

CCr would land a new seam beside the kanban ledger, not a second dispatcher. `assign` becomes a guarded append that counts `ASSIGNED` rows for the lane and refuses `LANE_FULL` at the policy cap of 4. `crash` appends one crash and one requeue fact. `retry` appends the one confirming retry for `crash`, and a second one is `RETRY_CAP` on the ledger, not a retry loop. The two-string list is the only spawn shape a later clock may pass onward, and only after the approval gate. `spawn` stays a refusal in this module. This module still does not start the worker.

## Ship

Operations: `Assignment`, `Board`, `Event`, `Lane`, `POLICY_WORKER_CAP`, `RETRY_FAILURE`, `SCHEMA`, `assign`, `crash`, `make_board`, `make_lane`, `rebuild`, `retry`, `spawn`, `spec_argv`, `terminate`.

Refusal codes: `BAD_ARGV`, `BAD_ASSIGNMENT`, `BAD_BOARD`, `BAD_EVENT`, `BAD_FENCE`, `BAD_ID`, `BAD_LANE`, `BAD_LIMIT`, `BAD_SCHEMA`, `CHAIN`, `CLOSED`, `CRED_MISMATCH`, `DUPLICATE`, `EMPTY_ALLOW`, `EMPTY_ARG`, `LANE_FULL`, `MISSING_CRED`, `NOT_ALLOWED`, `NOT_ASSIGNED`, `NOT_INT`, `NOT_TEXT`, `NO_RETRY`, `NO_SPAWN`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `REPLAY`, `REQUEUE_CAP`, `RETRY_CAP`, `SECRET`, `SHELL_STRING`, `STALE`, `UNCLASSIFIED`, `UNKNOWN_ASSIGNMENT`, `UNKNOWN_LANE`, `UNKNOWN_MODE`.

What this module still refuses to execute: a worker, a shell string, a thread, a child process, a second automatic requeue, and a cap above 4. `COMPLETE`, `REVIEW`, and `BLOCK` are records. `spawn` is `NO_SPAWN`. An assignment is not a process, so a descendant cannot inherit the claim from here.

Hot-path shape: one pass over the event log. Lane, card, fence, and occupancy indexes are dicts and sets. The allowlist is a set. An assignment that would pass `worker_cap` refuses. Later cards are not dropped inside that call because each card is its own call, and a card that fits still succeeds on a later call once a slot is free.
