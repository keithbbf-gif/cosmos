# Delegation

Hermes `delegate_task` starts a child with a fresh conversation. The child inherits the parent's toolset and cannot widen it. Leaf children lose further delegation. A blocked set (messaging, memory writes, scheduling, seat changes, spend admin, approvals, and principal admin) never reaches a child. Depth, concurrency, iteration, and lease budgets are install policy. A caller that asks for more is recorded and ignored. Batches larger than the free child slots fail instead of being truncated. The parent receives the child's final summary, not its running log. A child that stops making progress is reported and is not started again. One schema miss may be corrected once; the work is kept either way. Nothing here starts a process, a thread, or a model call.

The live seam is `cosmos/cosmos_delegate.py`. It already reserves a child on the scheduler ledger, strips blocked capabilities, ignores a raised iteration request, and reports stale running work without retrying it. This proposal does not import that module. The live spawn still submits a scheduler job. This review copy returns a descriptor and does not.

## Operations

`make_board` stores a caller's depth, children, iteration, and lease request. Policy is depth 2, children 3, iterations 8, and lease 450 seconds. A higher request stays on the record. The enforced cap stays at policy. A lower request is the enforced cap.

`register` records a depth-0 parent, a credential id, and a fencing token.

`open_child` opens one child under a registered parent or an open child. The caller must present that actor's fence. A wrong fence raises `FENCE` and appends nothing. A child whose lease is past raises `STALE_LEASE` and appends nothing. A reported child's fence raises `STALE_FENCE`. The new child is a frozen descriptor with `executes` false. It receives its own fence and a lease that cannot exceed the board cap. The call strips `mail:send`, `wo:propose`, `seat:take`, `spend:admin`, `approval:grant`, and `principal:admin` at every depth. It strips `delegate` when the new child's depth equals the effective max depth. A depth past that cap raises `DEPTH` and creates no child. A parent that already has `max_children` open children raises `CONCURRENCY` and creates no child. An iteration or lease request above the effective cap is stored; the enforced budget stays the cap. Notes are taken in one pass. A note that does not fit the remaining 512-character budget is skipped. Later notes that fit are still kept.

`open_batch` opens every goal or none. A batch larger than the free slots raises `CONCURRENCY` and appends nothing.

`strip_tools` is the pure grant split `open_child` uses. A max-depth argument above policy is clamped. A depth past that clamped cap raises `DEPTH`.

`present` returns the open child when the fence matches and the lease is live. It does not start a process.

`complete` stores the summary the parent may see. The child fence must match. A stale lease refuses. When the child was opened with schema keys, the first miss stays `OPEN`, records `SCHEMA_MISS`, and does not publish the summary. The next `complete` is the one confirming retry. A second miss finishes the child, keeps the text, and sets `schema_valid` false. There is no third try.

`parent_view` returns that summary string when the caller presents the child fence or the parent fence. It has no log parameter and the records have no log field.

`report_stale` sets an open child past its lease to `REPORTED`. The lease is the one fixed at open. The caller cannot stretch it here. The call does not open a replacement. A second report with the same fence returns the same board. After the report, that fence is `STALE_FENCE` for `present`, `complete`, and further delegation.

`rebuild` checks the hash chain and folds the facts. `snapshot` is the public projection. The same facts reproduce the same snapshot.

## Authority

The scheduler ledger is the authority. This module returns frozen records a later guarded append would store. It does not write a ledger, start a job, or read a clock. The caller passes `now`. A fence is compared with `const_eq`. Credential ids are compared with `const_eq`.

## Refusal codes

`BAD_BOARD`, `BAD_FENCE`, `BAD_ID`, `BROKEN_CHAIN`, `CLOCK`, `CONCURRENCY`, `CRED_MISMATCH`, `DEPTH`, `DUPLICATE`, `EMPTY_ALLOW`, `EMPTY_GOAL`, `EMPTY_NOTE`, `EMPTY_SCHEMA`, `EMPTY_SUMMARY`, `FENCE`, `FRESH`, `MISSING_CRED`, `NO_SPAWN`, `NOT_INT`, `NOT_LIST`, `NOT_OPEN`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `SECRET`, `STALE_FENCE`, `STALE_LEASE`, `UNCLASSIFIED`, `UNKNOWN_CHILD`, `UNKNOWN_PARENT`.

`NOT_TEXT`, `NULL_BYTE`, `OVERSIZE`, `NOT_INT`, and `OUT_OF_RANGE` come from `bound_text` and `bound_int`. An empty tool list, an unknown tool, a missing credential id, or a raw key shape refuses. `repr` of a refusal stays free of raw key material.

## Landing

CCr would keep `cosmos_delegate.Delegation.spawn` as the write path and would not add a second scheduler. Map `open_child` onto the existing depth check, per-parent live-child count, and capability strip inside `append_guarded`. Issue the fence in that same critical section and refuse a mismatched fence before `submit`. Map the child lease onto the stale sweep: a child past `lease_until` is `REPORTED`, and a later present or complete with that fence is refused instead of running the command. Map `report_stale` onto `Scheduler.report_stale` so the fact is `REPORTED` and the child is not re-queued. The parent-facing read stays a summary string. Caps in this review copy stay 2, 3, 8, and 450 even if the caller asks for more.

## Ship

- operations: `ALWAYS_STRIP`, `CLASSIFIED`, `EXECUTES`, `POLICY_CHILDREN`, `POLICY_DEPTH`, `POLICY_ITERATIONS`, `POLICY_LEASE_S`, `POLICY_NOTE_BUDGET`, `SCHEMA`, `SCHEMA_MISS`, `Board`, `Caps`, `Child`, `Fact`, `Parent`, `Snapshot`, `complete`, `make_board`, `open_batch`, `open_child`, `parent_view`, `present`, `rebuild`, `register`, `report_stale`, `snapshot`, `strip_tools`
- refusal codes: `BAD_BOARD`, `BAD_FENCE`, `BAD_ID`, `BROKEN_CHAIN`, `CLOCK`, `CONCURRENCY`, `CRED_MISMATCH`, `DEPTH`, `DUPLICATE`, `EMPTY_ALLOW`, `EMPTY_GOAL`, `EMPTY_NOTE`, `EMPTY_SCHEMA`, `EMPTY_SUMMARY`, `FENCE`, `FRESH`, `MISSING_CRED`, `NO_SPAWN`, `NOT_INT`, `NOT_LIST`, `NOT_OPEN`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `SECRET`, `STALE_FENCE`, `STALE_LEASE`, `UNCLASSIFIED`, `UNKNOWN_CHILD`, `UNKNOWN_PARENT`
- what this module still refuses to execute: a child process, a terminal, a model call, a scheduler submit, a second schema retry, a replacement for a stale child, a tool grant outside the classified set, and any cap above policy
- hot-path shape: one pass over notes that skips a note which does not fit the remaining budget; one pass over the fact chain to fold, with dict indexes for parent and child ids; tool membership is a set; one new digest per appended fact
