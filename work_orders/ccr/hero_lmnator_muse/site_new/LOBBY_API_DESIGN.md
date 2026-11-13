# Lobby API design

Extends `site/queue.php`. Nothing in this file is deployed. The live PHP file is unchanged. `mock_queue.js` is the runnable copy of this contract, in the browser and under node.

## What queue.php does today

Read from `site/queue.php` in this work order.

- Store: `/home/papafigc/lmn_match.json`, locked with `flock`.
- Runs log, `op: "save"` only: append one JSON line to `/home/papafigc/lmn_runs.jsonl`. Allowed record keys: `game`, `event`, `match_id`, `seed`, `models`, `calls`, `lanes`, `seats`, `outcome`. No player name is written.
- Body cap: 12000 bytes. `pid` is required, stripped to 40 characters of `[A-Za-z0-9_-]`.
- Game allow-list: `higher`, `tiles`, `derby`, or an id matching `^[sm][0-9]{2}$`. A contest id such as `c01` returns `{"error":"mode"}`.
- Ops: `join`, `poll`, `move`, `leave`, `save`. Anything else returns `{"error":"op"}`.
- Modes for `teammate` and `enemy`: `human`, `ai`, `either`.
- Tickets with `seen` older than 45 seconds are dropped. Matches older than 1200 seconds are dropped.
- `either` fills that side with AI when the ticket is at least 8 seconds old, or earlier if the other side already has a person.
- Roster is always four slots: `a1`, `a2`, `b1`, `b2`.
- `a1` is the player who opened the match. `a2` is the teammate. `b1` is the enemy. `b2` is always an AI seat named Novelist with skill `0.4`, even when three people are in the queue.
- Immediate AI game (`teammate: "ai"` and `enemy: "ai"`) uses Librarian skill `0.76` on `a2` and Sprinter skill `0.58` on `b1`.
- `public_match` renames slots for the caller as `you`, `teammate`, `enemy`, `enemy2`. `higher.js`, `tiles.js`, and `derby.js` read those role names.
- `move` stores `pick` under `moves[round][pid]`.

`lobby.js` posts `join` with `game`, `name`, `teammate`, and `enemy`, then polls every 1500 ms. `engines.js` mounts that lobby only when `players === "multi"`. The 18 engine loops do not read `LMN_MATCH`.

## Capability probe

Old clients keep working because a missing `seats` field still means the four-seat join above.

New clients send this first:

```json
{"op":"caps","pid":"<pid>"}
```

Until `queue.php` grows this op, the answer is `{"error":"op"}`. The page then uses `mock_queue.js` and says so. It does not pretend the live file accepted an N-seat join.

When the op exists, answer:

```json
{
  "status": "ok",
  "n_player": true,
  "min_seats": 2,
  "max_seats": 8,
  "fill_after_s": 8,
  "ticket_ttl_s": 45,
  "match_ttl_s": 1200,
  "difficulties": {"easy": 0.4, "medium": 0.58, "hard": 0.76},
  "ops": ["caps", "join", "poll", "leave", "move", "save", "lobby_open", "lobby_join", "lobby_poll"]
}
```

`min_seats` and `max_seats` match the phone lobby in this pack. They are not a limit measured on the current PHP. `fill_after_s`, `ticket_ttl_s`, and `match_ttl_s` are the numbers already in `queue.php`. The three skills are the Librarian, Sprinter, and Novelist values already written on AI seats.

## Shared rules for the new ops

- Same `pid`, name cleaning, lock, and expiry as today.
- `name` stays 16 characters of letters, digits, space, `_`, and `-`. Empty becomes `Player`.
- `game` for the new ops is `^[a-z][a-z0-9]{0,15}$`. That covers `s01`, `m01`, `c01`, `higher`, `tiles`, `derby`, and later pack ids. The old join does not gain this wider allow-list.
- `seats` is an integer from 2 to 8.
- `fill` is `human`, `ai`, or `either`.
- `difficulty` is `easy`, `medium`, `hard`, or `legacy`.
- `legacy` is allowed only with `layout: "2v2"` and `seats: 4`. AI seats then use the current names and skills: `a2` Librarian `0.76`, `b1` Sprinter `0.58`, `b2` Novelist `0.4`.
- `slot_difficulty` is an optional array, one entry per seat, values `easy`, `medium`, or `hard`. An empty string means "use the table". A per-seat value wins over the table, including `legacy`.
- `layout` is `2v2` only when `seats` is 4. Every other count is `ffa`. Slot ids for `2v2` stay `a1`, `a2`, `b1`, `b2`. Other matches use `s1` … `sN`.
- A bad game, seat count, fill, or difficulty returns `{"error":"mode"}`.
- `save` and `move` stay as they are. `save` still must not store a player name.

## Queue join

`seats` present means the new join. `teammate` and `enemy` are ignored on that request. A body without `seats` stays the old join, including the rule that `b2` is always the Novelist.

```json
{
  "op": "join",
  "pid": "p1",
  "game": "m01",
  "name": "Ada",
  "seats": 6,
  "fill": "either",
  "difficulty": "medium",
  "layout": "ffa",
  "slot_difficulty": ["", "easy", "hard", "", "", ""]
}
```

Buckets are `(game, seats, layout)`.

- `fill: "ai"` starts now. The caller is the only person. Every other seat is AI.
- `fill: "human"` starts only when that many people are in the bucket. The 8 second clock does not add AI. This is the all-human table, which the current PHP cannot build for four people because `b2` is hard-coded AI.
- `fill: "either"` takes other `either` tickets. It does not take a `human` ticket, so a people-only waiter is not pulled into a table that is about to add AI. At 8 seconds it starts and fills the open seats with AI.
- A `human` anchor may take waiting `either` tickets. Those people already accepted a human seat. The table starts only when it is full, and it does not add AI. Two people who asked for 2 seats, one `either` and one `human`, therefore become an all-human match immediately.
- The oldest ticket in the bucket is the anchor and sits in `a1` or `s1`.

`poll` is unchanged for the caller: refresh `seen`, try to make a match, return `matched` or `queued`.

## Lobby code

```json
{"op":"lobby_open","pid":"p1","game":"m30","name":"Ada","seats":3,"fill":"either","difficulty":"medium","layout":"ffa"}
```

Answer while it is open:

```json
{"status":"lobby","code":"AB3K","game":"m30","seats":3,"fill":"either","layout":"ffa","difficulty":"medium","have":1,"host":"p1","wait":0,"members":[{"name":"Ada","slot":"s1","kind":"human","pid":"p1"}]}
```

The code is four characters. `lobby_join` posts `op`, `pid`, `code`, and `name`. Unknown or already started codes return `{"error":"closed"}`. A full room returns `{"error":"full"}`.

The same fill rules as the queue apply, timed from `created`. `lobby_poll` uses the same body shape as `poll`. A client may send `poll`; if that pid is in an unstarted lobby, the server answers the lobby view or the match.

`leave` drops a queue ticket. If the host leaves before the start, the lobby closes. Another member who leaves is removed and the room stays if someone remains.

## Match object

Old four-role pages keep working when `layout` is `2v2` and there are four seats. `seats` is still ordered `you`, `teammate`, `enemy`, `enemy2`, with `slot`, `kind`, `name`, `pid`, and `skill`. Added fields: `difficulty`, `seats_n`, `layout`, `fill`, `legacy`.

`legacy: true` means the old join produced it, so `b2` is AI. `legacy: false` means a new join, so a human may sit in every seat, including `b2`.

For any other shape, each seat is `{role, slot, kind, name, pid, skill, difficulty}`. The caller's role is `you`. Other roles are the slot ids (`s2`, `s3`, …). `higher.js` and `tiles.js` only paint `teammate`, `enemy`, and `enemy2`. A 5-seat match does not gain extra rivals on those pages. `derby.js` prints whatever is in `seats`.

`moves` stays a JSON object, never a list, including when it is empty.

## Errors

Keep the current strings: `bad`, `pid`, `store`, `mode`, `record`, `nomatch`, `op`. Add `closed` and `full` for lobby codes.

## What the mock does not copy

- It does not write `/home/papafigc/lmn_match.json` or `lmn_runs.jsonl`. `save` stays in memory for the simulation.
- Match ids use an FNV-1a tail. `queue.php` uses the first six hex characters of `md5`.
- The mock seed is `(now % 100000) + (seq % 999) + 1`. `queue.php` uses `mt_rand` for the second term.
- One mock store is one browser. Two phones do not see each other unless they both reach a `queue.php` that implements this document.
