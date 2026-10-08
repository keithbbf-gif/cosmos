# pets

Hermes draws a cosmetic mascot beside the CLI, the TUI, and the desktop window. The sprite does not change the prompt, the token stream, the tool list, or an approval. Each profile keeps its own pets. Choosing one records a slug and an enabled flag. Surfaces share one activity map: a failed turn, a finished plan, a clean finish, thinking, and an idle agent settle to a resting pose; a tool or a turn in flight runs; a clarify or approval wait falls back to idle on a short sheet. Generation, gallery download, terminal graphics protocols, roaming, and pop-out windows stay on the host.

The live seam is new. COSMOS has no mascot module. Pets are cosmetic only. The neighbor is the attempt display record, not the spend gate and not a tool allowlist.

## Operations

`render` returns a frozen `Line`. A catalog name such as `ember` uses the idle line. A `Pet` uses that pet's mood. The text is a fixed catalog string. Caller text never becomes the line.

`act` returns a `Line` for `idle`, `run`, or `sleep`. An action named `shell`, `exec`, `command`, or `url`, in any case, raises `PET_EXEC` before the catalog lookup. Any other action raises `BAD_ACTIVITY`. The call starts nothing.

`present` reads one mapping and returns a frozen `Pet`. The sprite must be one of `PET_NAMES`. A well-formed unknown slug is `UNKNOWN`. A slug outside `^[a-z0-9-]{1,24}$` is `BAD_SPRITE`. The mood is `idle`, `run`, or `sleep`. Any other mood is `BAD_MOOD`, except the command names above, which are `PET_EXEC`. `enabled` defaults to false. Scale is an integer in milli-units. The floor is 100, the default is 330, and the policy cap is 3000. A requested scale above 3000 stays on `requested_scale`. The stored `scale` is 3000. A scale below 100 or above 1000000 is `OUT_OF_RANGE`.

`select` is `present` with `enabled` forced true. There is no off mode.

`activity_mood` maps `idle`, `nothing`, and `waiting` to idle, `run`, `tool`, and `inflight` to run, and `sleep` to sleep. `waiting` is the short-sheet fallback. Sheet names such as `wave`, `jump`, `review`, and `failed` are `BAD_ACTIVITY`. Command names are `PET_EXEC`.

`collect` checks every row, refuses a repeated sprite, and keeps at most `ROSTER_CAP` pets (8). A higher `limit` is ignored and the requested limit is recorded. Further valid rows increment `dropped`. An empty roster is an absent mascot. A bad row after the cap still refuses.

`describe` returns a `Status`. `ready` is true only when the pet is enabled. `network` is false on every successful record. `network` true, or `ready` that disagrees with `enabled`, raises `BAD_VALUE`.

`rebuild` returns the same `Pet` from a `Status`.

A mapping key named `command`, `url`, `exec`, or `shell`, in any case and at any nested mapping or list, raises `PET_EXEC`. The same words as sprite values are `UNKNOWN`, not a granted command. A mapping that yields the same key twice raises `DUPLICATE`.

## Authority

The human chooses a catalog sprite and a mood. This module grants no tool and holds no credential. A secret-shaped string is `SECRET`. No path is accepted, so no jail is opened. Line text is not taken from the caller.

## Refusal codes

`PET_EXEC`, `BAD_MOOD`, `BAD_SPRITE`, `BAD_ACTIVITY`, `BAD_KEY`, `BAD_VALUE`, `BAD_MAP`, `BAD_ROWS`, `BAD_PET`, `BAD_SCHEMA`, `MISSING_SPRITE`, `MISSING_MOOD`, `DUPLICATE`, `SECRET`, `NOT_TEXT`, `NOT_BOOL`, `NOT_INT`, `NULL_BYTE`, `OVERSIZE`, `OUT_OF_RANGE`, `UNKNOWN`.

`NOT_TEXT`, `NULL_BYTE`, and `OVERSIZE` come from `bound_text` when the value is text. `NOT_INT` and `OUT_OF_RANGE` are raised on scale and cap fields. Bool is not an int.

## Ship

- operations: `MOODS`, `PET_NAMES`, `ROSTER_CAP`, `SCALE_CAP`, `SCALE_DEFAULT`, `SCALE_FLOOR`, `SCHEMA`, `SPRITE_MAX`, `Line`, `Pet`, `Roster`, `Status`, `act`, `activity_mood`, `collect`, `describe`, `present`, `rebuild`, `render`, `select`
- refusal codes: `PET_EXEC`, `BAD_MOOD`, `BAD_SPRITE`, `BAD_ACTIVITY`, `BAD_KEY`, `BAD_VALUE`, `BAD_MAP`, `BAD_ROWS`, `BAD_PET`, `BAD_SCHEMA`, `MISSING_SPRITE`, `MISSING_MOOD`, `DUPLICATE`, `SECRET`, `NOT_TEXT`, `NOT_BOOL`, `NOT_INT`, `NULL_BYTE`, `OVERSIZE`, `OUT_OF_RANGE`, `UNKNOWN`
- what this module still refuses to execute: a shell, exec, command, or url action; gallery install and download; sprite generation; terminal graphics protocols; roaming; pop-out windows; config writes; an off mode; a retry; sheet poses `wave`, `jump`, `review`, and `failed`
- hot-path shape: one pass over the mapping or the rows; known sprites, moods, and activities resolve through a dict or set; a catalog hit does not scan secrets; `collect` validates every row, keeps rows until the policy cap, and counts the rest as dropped

CCr would store `Pet` on the attempt display record and let a later surface paint `render`'s line. Gallery bytes, when a human has already placed them, would sit in the attempt workspace under a `PathJail` that this package does not open. Install, hatch, and terminal protocols stay outside, and the land adds no network path and no process.
