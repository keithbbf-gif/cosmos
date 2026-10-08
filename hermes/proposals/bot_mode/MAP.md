# Bot mode

Hermes Bot Mode is a roster of named specialist profiles. A person addresses a bot with `@name`. In a group, a message can name several bots, and a room turn runs at most three serial rounds. The bots pane lists the roster. Command approval stays with the human. A bot does not grant it. Hermes also lets an unmentioned room speak and lets an unknown `@` pass through. This proposal requires one known mention and refuses an unknown `@`.

The live seam is mention route, and it does not approve. `cosmos/cosmos_profiles.py` stores occupancy skins, not a mention roster. `cosmos/cosmos_delegate.py` caps child jobs and does not resolve `@` names. `cosmos/cosmos_approval.py` remains the only approval authority. This module imports none of them.

## Operations

`make_roster` stores the caller's roster, fan-out, and screen requests. Policy is 20 bots, 3 fan-out rounds, and 20 screen lines. A higher request is recorded and ignored. A lower request is the effective cap.

`register` appends one specialist. The id is a lowercase token. Status is `ready` or `held`. The next id past the roster cap raises `BOT_CAP` and adds nothing. The same id raises `DUPLICATE`.

`room_message` binds a room token, a sender token, and the text.

`route` reads that message. A mention of a ready bot returns a `ReplyPlan` whose kind is `reply`. The plan names ids, specialties, and serial rounds. It leaves the caller text off the record. `enables_terminal` and `approves_tool` stay false. Zero mentions raise `NO_MENTION`. An `@` inside an email address is not a mention. A trailing dot stays off the id. An unknown mention raises `NO_BOT` and selects nobody. A held bot raises `HELD`. A sender who is one of the targets raises `SELF`. Two or three mentions with fan-out left false raise `NEED_FANOUT`. `fanout=True` returns those bots in first-seen order, at most the fan-out cap. A longer distinct list raises `FANOUT_CAP` and keeps every name off the plan. A message that asks the bot to approve a shell, a command, or a tool raises `BOT_APPROVAL`. A message that asks messaging to run or enable a shell, a terminal, or a command raises `NO_TERMINAL`. The word gate treats an enable verb plus one of those nouns as a refusal, and it reads a negation as the same refusal. `off` and `yolo` are not modes.

`approve` raises `BOT_APPROVAL`. `enable_terminal` raises `NO_TERMINAL`.

`screen` returns lines of id, specialty, and status, separated by a tab, in registration order. The window never exceeds the screen cap. A higher per-call limit is ignored. The lines are a pane projection.

`snapshot` emits a hash-chained projection. `rebuild` from that snapshot returns the same roster. A bad digest is `BROKEN`. A tip or link that misses the previous digest is `STALE`.

## Authority

The ledger is the authority for membership. This module returns frozen records only. Writes, sockets, backends, and clocks stay outside it. Approval stays a human act on the approval ledger. A bot id is not a grantor. A room message is not a terminal grant.

## Refusal codes

`BAD_FLAG`, `BAD_ID`, `BAD_KIND`, `BAD_LIMIT`, `BAD_MESSAGE`, `BAD_MODE`, `BAD_PLAN`, `BAD_RECORD`, `BAD_ROOM`, `BAD_ROSTER`, `BAD_SENDER`, `BAD_SPECIALTY`, `BAD_STATUS`, `BOT_APPROVAL`, `BOT_CAP`, `BROKEN`, `DUPLICATE`, `FANOUT_CAP`, `HELD`, `NEED_FANOUT`, `NO_BOT`, `NO_MENTION`, `NO_TERMINAL`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `SECRET`, `SELF`, `STALE`.

Ids and digests are compared with `const_eq`.

## Landing

CCr would land this later as a roster projection beside profiles: `register` becomes a guarded append, ingress calls `route` before any turn, and the bots pane renders `screen` with the same cap of 20. Fan-out stays 3 even if a caller asks for more. A `ReplyPlan` is the only messaging result. `approve` never grows a grant path. `cosmos_approval` stays the writer. A bot principal remains `BOT_APPROVAL`, and a room message remains unable to enable a terminal.

## Ship

- operations: `GENESIS`, `POLICY_FANOUT`, `POLICY_ROSTER`, `POLICY_SCREEN`, `REPLY_KIND`, `SCHEMA`, `Bot`, `Caps`, `Record`, `ReplyPlan`, `RoomMessage`, `Roster`, `Snapshot`, `approve`, `enable_terminal`, `make_roster`, `rebuild`, `register`, `room_message`, `route`, `screen`, `snapshot`
- refusal codes: `BAD_FLAG`, `BAD_ID`, `BAD_KIND`, `BAD_LIMIT`, `BAD_MESSAGE`, `BAD_MODE`, `BAD_PLAN`, `BAD_RECORD`, `BAD_ROOM`, `BAD_ROSTER`, `BAD_SENDER`, `BAD_SPECIALTY`, `BAD_STATUS`, `BOT_APPROVAL`, `BOT_CAP`, `BROKEN`, `DUPLICATE`, `FANOUT_CAP`, `HELD`, `NEED_FANOUT`, `NO_BOT`, `NO_MENTION`, `NO_TERMINAL`, `NOT_INT`, `NOT_TEXT`, `NULL_BYTE`, `OUT_OF_RANGE`, `OVERSIZE`, `SECRET`, `SELF`, `STALE`
- what this module still refuses to execute: a tool approval, a shell grant, a terminal session, a display start, a socket, a subprocess, a ledger write, a copy of the caller text on the reply plan, an unknown mention, a cap above policy, and any mode named off or yolo
- hot-path shape: one pass over intent words, one pass over mentions, a dict lookup confirmed with `const_eq`, and a screen loop that stops at the window. A list past the fan-out cap refuses instead of dropping names.
