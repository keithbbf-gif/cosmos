# Approval

Hermes checks a command before it runs. `smart` may auto-approve one low-risk command, `manual` always prompts, and `off` skips the prompt. `--yolo`, `/yolo`, and `HERMES_YOLO_MODE` skip prompts too. A hardline blocklist still refuses destructive commands under yolo, off, cron, and an allow-always rule. An unanswered prompt denies the command. Session and permanent allowlists skip a later prompt only for a command the operator already accepted.

The live seam is `cosmos/cosmos_approval.py`. That module stays the authority. This package does not import it and does not replace it.

This proposal adds `classify` of an action dict into `HARDLINE`, `CONFIRM`, or `ALLOW`; `request` of a confirm ticket; `grant` of one nonce; `consume` of that nonce; `deny`; `unanswered`; `allow_rule`; `authorize`; and `rebuild`. `consume` returns an `Admit` descriptor. The package does not run the command. A `file_read` inside the path grant is still `CONFIRM` until a captain `grant` or a live allow rule. A shell with an empty or expired allow list is `EMPTY_ALLOW`.

Authority is the ledger, and a captain is the human grantor. The ledger stores the sha256 of the canonical action JSON (`sort_keys`) and the sha256 of a `secrets.token_hex` nonce. It does not store the nonce or the command. `consume` compares those digests with `const_eq`. The same principal cannot grant its own request. A projection rebuilds from the events.

`REQUEST_TTL_CAP` is 900 seconds and `GRANT_TTL_CAP` is 120 seconds. A caller who asks for a higher cap keeps the policy cap, and the policy records the asked value. `request` accepts a caller `deadline`. A deadline past the policy ceiling is ignored and the ticket records the ceiling. `ACTION_MISMATCH` is the only confirming retry, and only once, on `grant` and on `consume`. The next miss is `RETRY_CAP`. A pending request that nobody answers is `DENIED` once `now` is past that deadline. `grant` of an expired pending request stays `EXPIRED`.

Refusal codes: `BAD_MODE`, `BAD_ACTION`, `BAD_ACTOR`, `BAD_CREDENTIAL`, `BAD_EVENT`, `BAD_NONCE`, `BAD_PATTERN`, `EMPTY_ALLOW`, `EXPIRED`, `HARDLINE`, `MISSING_CREDENTIAL`, `NOT_APPROVER`, `NOT_DUE`, `NOT_LISTED`, `NOT_OWNER`, `OUT_OF_RANGE`, `REPLAY`, `RETRY_CAP`, `SECRET`, `SELF`, `UNCLASSIFIED`, `UNGRANTED`, `ACTION_MISMATCH`, `ALREADY`, `DENIED`. Jail and bounds add `OVERSIZE`, `NULL_BYTE`, `NOT_TEXT`, `NOT_INT`, `NO_GRANT`, `RELATIVE_PATH`, and `OUTSIDE_GRANT`. There is no `off` mode and no `yolo` mode.

CCr would land this later by folding `Ticket` and `Admit` into the live gate's ledger events, leaving `cosmos_approval.py` as the only writer, and deleting this package. The live hardline set stays the superset. This copy does not widen a grant past it.

## Ship

Operations: `SCHEMA`, `MODE`, `HARDLINE`, `CONFIRM`, `ALLOW`, `REQUEST_TTL_CAP`, `GRANT_TTL_CAP`, `FIELD_CAP`, `RETRY_FAILURE`, `action_sha`, `canonical_json`, `Policy`, `Verdict`, `Ticket`, `Admit`, `LedgerEvent`, `ApprovalGate`. Gate methods: `classify`, `request`, `grant`, `deny`, `consume`, `allow_rule`, `authorize`, `unanswered`, `rebuild`, `ledger`.

Refusal codes: `ACTION_MISMATCH`, `ALREADY`, `BAD_ACTION`, `BAD_ACTOR`, `BAD_CREDENTIAL`, `BAD_EVENT`, `BAD_MODE`, `BAD_NONCE`, `BAD_PATTERN`, `DENIED`, `EMPTY_ALLOW`, `EXPIRED`, `HARDLINE`, `MISSING_CREDENTIAL`, `NOT_APPROVER`, `NOT_DUE`, `NOT_INT`, `NOT_LISTED`, `NOT_OWNER`, `NOT_TEXT`, `NO_GRANT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OUTSIDE_GRANT`, `OVERSIZE`, `RELATIVE_PATH`, `REPLAY`, `RETRY_CAP`, `SECRET`, `SELF`, `UNCLASSIFIED`, `UNGRANTED`.

What this module still refuses to execute: a command, a delete, a publish, a spend, or a network call. `Admit` is a descriptor. Hardline stays hardline after a captain grant. `off` and `yolo` are not modes. An empty effective allow does not run a shell.

Hot-path shape: one pass over the normalized fields, module-level hardline patterns, then allow rules bucketed by kind. Expired rules are not a live allow. A pending request past its deadline is one denial append.
