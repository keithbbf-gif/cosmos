# spendcap

The day-one check before the first model call is an in-memory fold of reserve, settle, and release. It is not a second wallet. Core's ledger remains the authority when CCr lands this. If the fold and the chain disagree, the chain wins.

## What I read

- `CONTRACT.md` slot `spendcap`, plus the shared cap law in `README.md`.
- `cosmos_federation.product.check_cap`, `DEFAULT_CAP_USD_MICROS` (`250_000`, $0.25), and `MAX_CAP_USD_MICROS` (`1_000_000`, $1.00).
- `SpendGate` in `V:\A\Ai\COSMOS\cosmos\cosmos_spend.py` (read-only). `guarded_call` reserves a worst case, denies before the call when settled plus outstanding plus that worst case would pass the rail cap, then settles measured use. The gate appends `SPEND_RESERVED`, `SPEND_SETTLED`, and `SPEND_RELEASED` through the Core ledger. A later `BUDGET_SET` changes cap and expiry only. It does not wipe settled or reserved totals.

## What is already true

- Spend authority in the live tree is one append-only ledger behind `SpendGate`. The breaker sits on the call, not on a receipt written afterward.
- Live amounts are dollar floats. Day-one policy in this folder is integer micro-dollars. `1_000_000` micros is one dollar, not one million dollars.
- The live gate reads a clock (`time.time` unless the caller passes one). This fold does not. `now` is a caller epoch.
- Install does not open a ledger. This proposal does not open one either. No sqlite file.

## What this proposal adds

- `open_book(cap_usd_micros) -> Book`. The cap goes through `check_cap`. The ceiling stays `MAX_CAP_USD_MICROS`.
- `reserve(book, micros, now, event_id) -> Book` appends a `RESERVE` event and returns a new book.
- `settle(book, event_id, micros, now) -> Book` appends a `SETTLE` event. Measured micros may be lower than the hold, including zero, and may not be higher.
- `release(book, event_id, now) -> Book` appends a `RELEASE` event with micros `0` and drops the hold.
- `Book` is a frozen slotted dataclass: the cap plus a tuple of `Event`. Each call returns a new book. The prior book stays as it was. `SCHEMA` is `cosmos-federation-spendcap/1`.

A reserve equal to the remaining headroom is allowed. A reserve that would pass it is refused before any model call, matching `SpendGate`.

## Refusal codes

- `CAP` — book cap is outside `1 .. MAX_CAP_USD_MICROS`, including a boolean. The fold does not raise the policy cap.
- `BOUND` — `event_id` fails `bound_text` (limit 64), `now` is not a non-negative int, micros is not an int in range, the id matches `secret_shape`, or the book is not a clean fold. A reserve hold below 1 micro-dollar is `BOUND` because a zero hold would skip the pre-call check.
- `OVER_CAP` — the reserve would pass the cap, or settle micros is greater than the open hold.
- `DUP_EVENT` — `reserve` reuses an `event_id` that already has a `RESERVE`, including after settle or release.
- `NO_RESERVE` — `settle` or `release` does not name an open reserve (unknown, already settled, or already released).

## How CCr lands it

Keep the Core ledger as the only spend authority. On landing, write the same facts through `SpendGate` (`SPEND_RESERVED`, `SPEND_SETTLED`, `SPEND_RELEASED`). Do not add a second ledger file and do not add sqlite. Convert micro-dollars to the ledger's dollar amounts at that boundary (`1_000_000` micros = `$1`). Rebuild the fold from the chain when a peer starts. If this fold and the chain disagree, the chain wins and the fold is discarded. Do not raise `MAX_CAP_USD_MICROS`.

No extra files. The module and the tests are the slice.
