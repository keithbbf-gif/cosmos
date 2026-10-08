# kanban

Hermes Kanban is a shared board of cards. A card is a row. Columns in this slice are `todo`, `doing`, and `done`. Hermes also runs a dispatcher, workers, comments, attachments, and a SQLite file. This proposal keeps the placement chain only.

Seam: the COSMOS queue stays the authority. This board is a projection a later landing can fold from ledger events. It does not spawn workers. Live seam: chained projection. This module is not a second queue and not a ledger writer.

`Board(requested_cap=None)` records a card cap. The policy cap is 64. A requested cap above 64 is ignored and 64 is recorded. A lower positive cap is recorded as asked. `add_card` appends one `add` link and starts in `todo` unless the caller names another column. A second add of the same card raises `DUPLICATE` and does not append. `move` appends one `move` link for a card already on the board. The current column is a legal target. `column_of` reads the projected column. `cards` lists placements in add order. `events` returns the chain. `snapshot` freezes the schema, the applied cap, the tip sha, and the columns. `rebuild(events)` replays that chain into an equal snapshot. `link_sha` is the hex digest of one link.

A body is `kind|card|column` with exactly two bars. A body that does not split into those three fields raises `BAD_BODY`. It does not raise `ValueError`. A sha that is not 64 lowercase hex digits raises `BAD_SHA`. A well-formed sha that does not match the link raises `CHAIN` when an `Event` is constructed. A later link whose `prev_sha` is not the previous tip also raises `CHAIN`. The chain ceiling is 256 events. The caller cannot raise it. There is no confirming retry. A refused call leaves the chain as it was.

Authority stays on the ledger. The board holds no worker, no claim, and no database. Card ids are names, not paths and not secrets.

## Ship

- operations: `SCHEMA`, `COLUMNS`, `KINDS`, `GENESIS`, `POLICY_CAP`, `EVENT_CAP`, `CARD_LIMIT`, `COLUMN_LIMIT`, `BODY_LIMIT`, `Event`, `Placement`, `Snapshot`, `Board`, `link_sha`, `rebuild`. `Board` methods are `add_card`, `move`, `column_of`, `cards`, `events`, `snapshot`, and `recorded_cap`.
- refusal codes: `BAD_BODY`, `BAD_CARD`, `BAD_COLUMN`, `BAD_EVENT`, `BAD_EVENTS`, `BAD_SCHEMA`, `BAD_SHA`, `BAD_SNAPSHOT`, `CARD_CAP`, `CHAIN`, `DUPLICATE`, `EMPTY`, `EVENT_CAP`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `SECRET`, `UNKNOWN_CARD`
- what this module still refuses to execute: a second queue, a ledger write, SQLite, a dispatcher tick, a worker spawn, a claim or fence, a heartbeat, an attachment, a workspace path, a network call, and any caller request to raise the card cap or the event ceiling. There is no off switch and no retry.
- hot-path shape: one dict lookup for the card, set membership for the column and the kind, one sha256 to seal the commit. Rebuild walks the chain once and hashes each link once to check it. A body is split once and refused when it is not three fields. A link that does not fit is refused. Later links are not applied and are not skipped, because a gap would break the chain.

CCr would later fold ledger events through `rebuild` and read `column_of` from the projection. The queue remains the only writer. This module still does not dispatch a worker.
