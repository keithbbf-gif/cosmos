# kanban_fleet

Hermes runs one gateway process per profile. Only one profile owns the kanban dispatcher: `dispatch_in_gateway` stays true there and false on the others, so two processes cannot spawn the same card. Other gateways still deliver for profiles whose adapters they host. The atomic claim is what stops the double run. A `changes_requested` review is a notification and does not create, unblock, or requeue a task. This proposal does not start those processes and does not read `config.yaml`.

The live seam is the fencing token. This module does not import the live lease table and does not replace it.

`Fleet.claim` records one gateway and one fence for a card. The same pair renews. A different gateway is `FENCE` until `release`. `release` by any other gateway is `FENCE`, including when that gateway copies the live fence. A fence that is not the live token, presented by the gateway that holds the card, is `STALE`. That mismatch is the one confirming retry (`RETRY_CLASS`). The next mismatch appends a cap row and is `RETRY_CAP`; the card stays held, and a later correct fence does not clear it. After a real release the same fence is `REPLAY`. The next holder needs a new fence. An unknown card is `UNKNOWN_CARD`. Gateway names and fences are compared with `const_eq`.

The first log row is the policy. Each accepted claim, renew, release, retry, and cap appends a `ClaimRecord`. `rebuild` replays that chain into the same holds, the same burned fences, the same retry lock, and the same caps. A broken link is `CHAIN`. A repeated record id is `DUPLICATE`. The caller passes `at`. A clock that moves backward is `CLOCK`. A requested card cap above 32 or log cap above 256 is stored and is not applied. Bool is not an int.

Authority for this ledger is the claim log. A human names gateways, cards, and fences. The module does not spawn a worker, open a socket, or start a thread.

Refusal codes: `BAD_ID`, `BAD_RECORD`, `CAP`, `CHAIN`, `CLOCK`, `DUPLICATE`, `EMPTY`, `FENCE`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `REPLAY`, `RETRY_CAP`, `SECRET`, `STALE`, `UNKNOWN_CARD`.

CCr would later fold `ClaimRecord` into the lease log and keep this package out of the process supervisor. The live dispatcher would call `claim` before marking a card running and `release` when the run ends. Notification delivery and review fan-out stay where they are.

## Ship

Operations: `SCHEMA`, `CARD_CAP`, `LOG_CAP`, `NAME_CAP`, `FENCE_CAP`, `CLOCK_HI`, `MAX_CONFIRMING_RETRIES`, `RETRY_CLASS`, `Policy`, `Claim`, `Release`, `Hold`, `FleetStatus`, `ClaimRecord`, `Fleet`, `rebuild`. `Fleet` methods are `claim`, `release`, `hold`, `status`, `policy`, and `records`.

Refusal codes: `BAD_ID`, `BAD_RECORD`, `CAP`, `CHAIN`, `CLOCK`, `DUPLICATE`, `EMPTY`, `FENCE`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `REPLAY`, `RETRY_CAP`, `SECRET`, `STALE`, `UNKNOWN_CARD`.

What this module still refuses to execute: a gateway process, a dispatcher thread, a socket, a write of `dispatch_in_gateway`, notification delivery, and any review mutation of a task. `Claim` and `Release` are descriptors. A second live fence for one card is `FENCE`. A raised cap is not applied. There is no `off` and no `yolo`.

Hot-path shape: one dict lookup for the card, then one `const_eq` pair on the holding gateway and the live fence. A free card scans that card's burned fences with `const_eq` and refuses `REPLAY` without dropping other holds. A card that does not fit the remaining card cap is `CAP`. One sha256 links each committed row. The policy row is first and counts toward the log cap.
