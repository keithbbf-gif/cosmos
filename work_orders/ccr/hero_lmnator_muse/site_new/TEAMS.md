# LMNator four-team build

This pass wrote only new files under `site_new`. It did not modify `site/engines.js`, `site/arcade.html`, existing packs, or `tokenctr/mdata/v1/games.json`. Nothing was published, committed, or uploaded.

The files were written in one pass from the live catalog so the id ranges could not collide. They are assigned to teams below.

## Priority

`games.json` (`lmn-game-grade/1`, 371 rows) was read. `grade` is null on every row (`grades_non_null` 0). That file has no play-count field. Multiplayer order does not follow a grade or a play count.

It follows two rules, in this order:

1. The ten ids a live browser test had already opened: `s01`, `s50`, `m01`, `m15`, `m30`, `m50`, `c01`, `c80`, `c150`, `c200`.
2. Then the other catalog games. Engines whose local board already has two sides are the better fit: `board` (both sides advance on the same roll), `lane` (two bars), `cards` and `quiz` (a call). `quiz` in `engines.js` calls `cards`. The other engines are a local board plus the lobby.

Those ten are the first rows in `pack-teamB-priority.js` (`e472`–`e481`).

| Id | Title | Engine | Players on the parent | Parent inspired line |
| --- | --- | --- | --- | --- |
| s01 | Sweet Grid | match3 | single | Candy Crush Saga |
| s50 | Tile Draw | cards | single | Vita Mahjong |
| m01 | Throne Lane | lane | multi | Honor of Kings |
| m15 | Realm Sprint | runner | multi | Genshin Impact |
| m30 | Snap Trivia | quiz | multi | QuizUp |
| m50 | Party Buzz | quiz | multi | Stumble-party quiz |
| c01 | Sugar Prism | match3 | single | Candy Crush Saga |
| c80 | Orbit Merge | merge | multi | 2048 |
| c150 | Bubble Drop | blast | single | Toon Blast |
| c200 | Cube Detonator | blast | single | Toon Blast |

`players: "multi"` mounts `#lobby` in `shell()` when `lobby.js` is loaded. The 18 engine functions do not read the match. Two phones do not share a grid. The card text says that.

Blurbs are `After <name>` only when the name is a real game and this engine's loop is that family. The parent inspired line is kept in `settings.listed_inspired` either way. It is copied onto `inspired` only when the blurb is set. Vita Mahjong, Honor of Kings, Genshin Impact, QuizUp, 2048, and the string "Stumble-party quiz" do not get a blurb on these cards. 483 pack rows have a blurb. 384 do not.

## What the engines actually read

From `site/engines.js`, `LMN_PLAY` clamps `goal` to the cap and clamps `speed` above 4 down to 3. Caps: match3 12, blast 8, runner 24, stack 8, merge 6, memory 8, snake 10, breakout 18, whack 10, slide 1, word 1, idle 80, cards 5, lane 20, board 12, rhythm 10, farm 4, quiz 5.

Knobs that change play:

- match3 reads goal and lives. A line is three in a straight row. Speed is not read.
- blast reads goal. Speed and lives are not read.
- runner reads goal and speed. One jump button. Lives are not read.
- stack reads goal and speed. Every drop counts. Alignment is not checked.
- merge reads goal (tier).
- memory reads lives. The deck is 6 pairs, and each pair attempt spends one life, including a match. Goal is not read. Lives under 6 cannot finish a clean deck, so those entries store at least 6.
- snake reads goal and speed. The buttons are Left, Right, and Up. There is no Down button.
- breakout reads speed. Brick count is 18. Goal and lives are not read.
- whack reads goal and lives. The hole moves on a tap. Speed is not read.
- slide, word: goal, speed, and lives are not read.
- idle reads goal and multiplies it by 5 to get the coin target.
- cards and quiz read goal and lives. quiz is the cards game.
- lane reads speed (how hard the field bar drains). Both bars start at 20. Goal is not read.
- board reads goal. Each roll adds 1, 2, or 3 to both sides.
- rhythm reads goal and lives.
- farm reads goal and speed. There are three plots.

Listed goals such as Sweet Grid's 5000 are stored on the new row as the cap (12), because that is the number `LMN_PLAY` will run.

## Team A — new single-player games

Ids `t101`–`t165` (65). `players` is `single`.

| File | Count | First game |
| --- | --- | --- |
| pack-teamA-01.js | 20 | t101 Straight Three |
| pack-teamA-02.js | 20 | t121 Six Flips |
| pack-teamA-03.js | 20 | t141 Cap Shift |
| pack-teamA-04.js | 5 | t161 Fast Harvest |

## Team B — multiplayer

New games `t201`–`t234` (34) in `pack-teamB-new.js`. First game: t201 Shared Line.

Support rows for the existing 371 games, ids `e472`–`e842`:

| File | First game |
| --- | --- |
| pack-teamB-priority.js | e472 Sweet Grid queue (s01) |
| pack-teamB-multi-s.js | e482 Crown Align queue |
| pack-teamB-multi-m.js | e530 Block Party queue |
| pack-teamB-multi-c1.js | e576 Cube Detonator queue 2 |
| pack-teamB-multi-c2.js | e666 Siege Breakers queue |
| pack-teamB-multi-c3.js | e756 Sugar Cascader queue |

`pack-teamB-new.js` first game is t201 Shared Line. The priority file is the ten-id list above.

## Team C — contest bouts

Ids `t301`–`t334` (34). `players` is `multi`. Goals are the short end of the cap where the engine reads goal.

| File | First game |
| --- | --- |
| pack-teamC-01.js | t301 Bout of Four |
| pack-teamC-02.js | t321 Bout Twenty |

## Enhancements, levels, modes

One tuned row per catalog game, ids `e101`–`e471` (371). First is e101 Sweet Grid tuned in `pack-enh-s.js`.

| File | First game |
| --- | --- |
| pack-enh-s.js | e101 Sweet Grid tuned |
| pack-enh-m.js | e151 Throne Lane tuned |
| pack-enh-c1.js | e201 Sugar Prism tuned |
| pack-enh-c2.js | e291 Tap Titans Duel tuned |
| pack-enh-c3.js | e381 Gem Blitz Merge tuned |
| pack-enh-c4.js | e471 Quickfire Crowd tuned |

Level and mode data are not pushed onto `LMN_PACK`. `APPLY_SETTINGS.js` applies a level or a mode only when the def passed to `LMN_PLAY` sets `settings.level` or `settings.mode_name`. The arcade does not set those.

| File | Rows | First base |
| --- | --- | --- |
| levels-s.js, modes-s.js | 50 | s01 |
| levels-m.js, modes-m.js | 50 | m01 |
| levels-c.js, modes-c.js | 271 | c01 |

Where the engine has a knob, the three levels are short, mid, and cap, and the three modes are chill, bout, and cap. slide and word have one level, named only, and one mode, as-shipped.

## Team D — checks and proposals

`engines-new-proposals.js` does not replace `LMN_PLAY` and does not edit `site/engines.js`. It sets `window.LMN_ENGINES_NEW` to `snake4` (adds Down), `slideCounted` (legal slides, scramble count), `breakoutRows` (brick count), and `laneBars` (goal is the bar size). memory, word, quiz, and stack are described in the file header and not reimplemented.

`APPLY_SETTINGS.js` loads after `engines.js`. It copies `settings.goal`, `settings.speed`, and `settings.lives` onto the play object when the top-level field is missing, and it copies a fair blurb onto `inspired` when `inspired` is empty. `LMN_PLAY` still applies its own clamp.

`load-test.html` loads `../site/engines.js`, the wrapper, every new pack, the level and mode files, and the proposals. It mounts t101 and the proposal snake.

`qa-result.json` is the node report. `games_new.jsonl` is also at `C:\Users\Papa\AppData\Local\Temp\lmn_teams\games_new.jsonl`. The two files are the same 1,112,970 bytes, 1,621 lines.

Grade rows use schema `lmn-game-grade/1`. `grade`, `matches_listing`, and `playable` are null. `built_by` and `builder` are empty. `builder_note` is `pending Keith's per-pack confirmation`. Counts by `enhancement_type`: new_game 137 (133 pack games plus 4 proposals), enhancement 371, multiplayer 371, levels 371, mode 371.

## Parse checks

Catalog load, before any new file was trusted: 371 pack objects, 0 duplicate ids, 0 pack files that threw, 0 slugs missing from the packs, 0 pack ids missing from `games.json`.

`node --check` on the 27 JS files this pass wrote: 27 ok, 0 fail.

Node load of the pack files: push-only (`window.LMN_PACK = window.LMN_PACK || []` and `push`), 875 objects, 0 duplicate ids, 0 collisions with existing ids. Level and mode files do not assign `LMN_PACK`.

Headless Edge (`msedge --headless --dump-dom` on `site_new/load-test.html`) wrote this into `#out`:

`{"pack":875,"levels":371,"modes":371,"play":"function","proposals":["snake4","slideCounted","breakoutRows","laneBars"],"dup":0,"has_t101":true,"has_e101":true,"has_t201":true,"has_t301":true,"t101":3238,"down":true}`

The mounted t101 board showed "AFTER Bejeweled", "Cleared 0 / 6", and "misses 5". The proposal board included a Down button. That is one mount of t101 and one mount of snake4. It is not a play-through of the other games, so `playable` stays null.

## Other files already in this folder

This pass did not write or edit `arcade_new.html`, `lobby_new.js`, `lobby-map-n.js`, `lobby.css`, `mock_queue.js`, `engines-lobby-n.js`, or `CURRENCY_OBOLS_TALENTS.md`.

## Team E - Lobby

N-player lobby and matchmaking. No edit to `site/arcade.html`, `site/lobby.js`, `site/queue.php`, `site/engines.js`, or any `pack-team*` / `pack-enh*` file.

Files: `lobby_new.js`, `lobby.css`, `mock_queue.js`, `lobby-map-n.js`, `engines-lobby-n.js`, `arcade_new.html`, `LOBBY_API_DESIGN.md`, `ARCADE_PATCH_NOTE.md`, `games_new_lobby.jsonl`. The same jsonl is at `C:\Users\Papa\AppData\Local\Temp\lmn_teams\games_new_lobby.jsonl`.

`lobby_new.js` replaces `LMN_MOUNT_LOBBY` and keeps `lmn-pid`, `LMN_MATCH`, and `LMN_BEGIN`. Seats are 2 through 8. Fill is people only, AI only, or people then AI after 8 seconds. Difficulty is easy, medium, or hard for the table or for one seat. A four-seat two-team table can use the current Librarian 0.76, Sprinter 0.58, and Novelist 0.4 mix. `engines-lobby-n.js` holds the original `LMN_PLAY` until that match exists. The 18 engine functions are unchanged.

`lobby-map-n.js` bakes the 371 rows from `tokenctr/mdata/v1/games.json` plus higher, tiles, and derby. Index size 374. `resolve()` also profiles any later `LMN_PACK` row, including the team packs, at 2–8 seats. Multi defaults to 4 seats and two teams of two. Single defaults to 2 seats and free for all. Priority ids, titles taken from `games.json`: s01 Sweet Grid, s50 Tile Draw, m01 Throne Lane, m15 Realm Sprint, m30 Snap Trivia, m50 Party Buzz, c01 Sugar Prism, c80 Orbit Merge, c150 Bubble Drop, c200 Cube Detonator.

Grade rows: 374 lines, schema `lmn-game-grade/1`, `grade` null, `built_by` empty, `builder_note` `pending Keith's per-pack confirmation`, `enhancement_type` `multiplayer`. Unmeasured fields are empty. These rows are the lobby offer. They are not a play measurement. Team-pack ids stay in `games_new.jsonl`.

### Works in this browser now

`arcade_new.html` uses the local mock. Chrome headless `--dump-dom` on the file URL returned status 0. The desk said "Queue and lobby" and "Local mock in this browser only", with m01 Throne Lane selected, and the list said 1246 games. `#/m01` showed the hold line "The board starts when the match is full" and did not include `#gstage`. `?demo=1#/m01` auto-joined an AI-only mock table: the DOM had `#gstage`, the Strike button, "Matched.", and then "The field takes it." with "You 0 · field 20". The headless virtual clock ran the lane interval, so that bout had already ended when the DOM was saved. Practice-seat and fill-now stay inside one page.

`node --check` passed for `mock_queue.js`, `lobby_new.js`, `lobby-map-n.js`, and `engines-lobby-n.js`. `node mock_queue.js` printed `SIM_OK 33` (33 checks, exit 0). `node --check` on `lobby.css`, `arcade_new.html`, the two markdown files, and the jsonl returned `ERR_UNKNOWN_FILE_EXTENSION`. Those files are not JavaScript.

### Needs a backend

Two phones share a match only when `queue.php` grows the ops in `LOBBY_API_DESIGN.md`. The live file still answers an unknown op with `{"error":"op"}`. Its join is four seats, and slot b2 is always the Novelist AI. Its game allow-list is `higher`, `tiles`, `derby`, and `^[sm][0-9]{2}$`, so a contest id is rejected there. higher and tiles still paint only `you`, `teammate`, `enemy`, and `enemy2`. The arcade engines still do not read `LMN_MATCH`. After the match starts, the board on this page is local.

## Team F - LLM Chess

Browser chess under `site_new/chess/`. No Stockfish. No edit to `site/engines.js`, `site/lobby.js`, `site/queue.php`, `site/buy.js`, Team A–E packs, or `lobby_new.js`. Pack file: `pack-teamF-chess.js` (push only, ids `t901`–`t904`). Grade rows: `games_new_chess.jsonl` and `C:\Users\Papa\AppData\Local\Temp\lmn_teams\games_new_chess.jsonl`. Schema `lmn-game-grade/1`, `grade` null, `built_by` empty, `builder_note` `pending Keith's per-pack confirmation`, `enhancement_type` `new_game`. Measurement fields are empty.

Rules are original code in `chess/chess_rules.js`. chess.js 1.4.0 (BSD-2-Clause, compiled file about 107KB) was on jsDelivr and was not vendored. See `chess/LICENSES.md`.

`seats.json` has 54 ids and no ratings. Of the brief names, only Muse Spark 1.3 is in that file (`meta/muse-spark-1.3-contributor`). Spark, Gemini 3.8 Flash, Grok 4.7, Argon 4, Sol 6, Luna 6, and Max are not. Gemini 3.8 Flash is disabled in the picker: off per Keith; future calls only via Joanna Vertex account after Keith re-enables. The other missing names are local mock labels with `seats_id` null. Detail: `chess/SEATS.md`. `node chess/test_mock.js` printed `MOCK_OK seats 54`.

### Works in this browser now

Open `chess/index.html`. Human vs local mock, with a picker before start, or blind (the name is hidden in the page until win, lose, resign, draw, or abort). Agent vs agent, with play-money bets. Hotseat for two people on one device. Commentary is generated from the move list and says it is not a claim about a model. Benchmark rows are labelled mock: legal-move counts, illegal attempts, latency, and null tokens. Prompts and replies are not stored.

House cut default is `0.05` in `chess/config.js` only. Pool is stakes minus `Math.round(stakes * rate)`. Draw, abort, and a result nobody bet refund every stake and take no cut. That policy is in `chess/TOKEN_INTERFACE.md`. The purses are `localStorage` key `lmn-chess-mock-balances-v1`. They are not TokenCTR and not `lmnator-game-tokens`.

`node --check` passed for `chess_rules.js`, `config.js`, `bets.js`, `models.js`, `mock_opponent.js`, `commentary.js`, `bench.js`, `app.js`, `test_perft.js`, `test_rules.js`, `test_bets.js`, `test_mock.js`, `test_pack.js`, and `pack-teamF-chess.js`. `node chess/test_perft.js` printed perft 1 `20`, perft 2 `400`, perft 3 `8902`, and perft 4 `197281` (exit 0). `node chess/test_rules.js` printed `RULES_OK`. `node chess/test_bets.js` printed `BETS_OK`. `node chess/test_pack.js` printed `PACK_OK 4`.

Headless Chrome `--dump-dom` of `http://127.0.0.1:8891/chess/index.html` (server root `site_new`) showed `<title>LLM Chess</title>`, `#boot` text `ready`, and `#perft-line` text `perft 20 400 8902`. Gemini 3.8 Flash was a disabled option. `../lobby_new.js` loaded, `#lobby` had Team E's lobby for `t904`, and the note said `LMN_MOUNT_LOBBY` was called. Chrome's stderr had an os_crypt "Access is denied" line. The DOM dump itself was produced.

Blind mode hides the label in the DOM until the game ends. The id is still in this browser's memory. A server has to withhold it before the agent is actually unknown.

### Needs a backend

`chess/PROXY_API.md` describes `POST /v1/chess/move` with `model_id`, FEN, PGN, and legal moves. This build does not call it. There is no model API and no key in the chess files.

`site/queue.php` still allows only `higher`, `tiles`, `derby`, and `^[sm][0-9]{2}$`. `t904` is outside that list, and `lobby.js` posts to a relative `queue.php`. A queued human-vs-human chess match needs that allow-list plus a page served beside the queue. `window.LMN_CHESS_LOBBY_START({ white: "human", black: "human" })` only starts hotseat.

`engines.js` has no `chess` branch. `LMN_PLAY` falls through to `idle` for these pack rows. Do not add the pack to the live arcade until that is deliberate.

Betting real tokens on outcomes may be regulated as gambling depending on how tokens are bought or cashed out. It needs Keith's OK plus a legal check before going live. Nothing here moves real money.
