# Package v3 round-one grade (no Claude)

Occupancy is unchanged. Vendor rank tables are guidelines, not a pin
change. Fable is out. DS V4 Pro 0813 and Qwen3.8 Max 0902 are skip_pin.

## Cache (P11) — first reviews missed; prime then hit

First DS/Qwen reviews put PREFIX on system and live slices on the user
turn. That is not CACHE_FAT.

| Call | cached_tokens | cache_write | usd | note |
|---|---|---|---|---|
| Q_dspro review | 0 | 0 | 0.170 | fat in user; key hashed PREFIX.md |
| Q_qwenmax review | 0 | 7187 | 0.597 | PREFIX write only |
| CACHE_dspro write | 7168 | 0 | 0.152 | fat on system |
| CACHE_dspro hit | **268288** / 268680 | 0 | **0.016** | key `cdeck-or-pv1-tv1-60761f2fc91f` |
| CACHE_qwenmax write | 0 | 272362 | 0.681 | fat on system |
| CACHE_qwenmax hit | **272362** / 272388 | 0 | **0.046** | same key family, fat hash |
| CACHE_dspro re-warm write | **268288** / 268679 | 0 | **0.016** | TTL still live; no rewrite |
| CACHE_dspro re-warm hit | **268288** / 268680 | 0 | **0.016** | still a hit |
| CACHE_qwenmax re-warm write | 0 | 272362 | 0.681 | Qwen TTL had expired; paid write |
| CACHE_qwenmax re-warm hit | **272362** / 272388 | 0 | **0.046** | hit on the new write |

Runner fix: `FAT_SEATS` (luna/glm/dspro/qwenmax) send CACHE_FAT as
system and a short ITEM as the tail. Do not `cache_control` the user
block. Next `--query dspro` / `--query qwenmax` must show cached_tokens
near prompt_tokens or it is another miss.

Ling stays compact (262k window < ~272k fat). Do not occupancy-pin DS/Qwen.

## Review quality (same extra-pane occupancy; studio `};` was the tell)

| Seat | Merge line | Caught stray `};` in deck_studio.js | Notes |
|---|---|---|---|
| **Sol** Q1 | HOLD | **yes** — studio/runs/review INCOMPLETE | Winner on this job. Fixed in cDeck #106. |
| Fable Q2/Q2a | truncated / cache 0 | yes (do not retry) | $4.79 + $5.19. ANTHROPIC_OFF. |
| Gemini 3.1 Pro Q2b | COMPLETE | no | Missed the parse. $1.33. |
| Luna Flex | COMPLETE then HOLD | saw syntax, missed the exact line | $0.028. |
| GLM-5.3 Flash | ship-with-fixes | no | Occupancy-pin reader. $0.019. Cheapest “looks shippable.” |
| Ling 3.0 Flash | INCOMPLETE (app.js tabs) | no | Compact slices. Essay. $0.004. |
| DS V4 Pro 0813 | COMPLETE (messy) | no | Did not beat Sol on the parse. |
| Qwen3.8 Max 0902 | COMPLETE | no | Merge line not closed. Did not beat Sol. |

**Winner this job: Sol.** GLM is the cheap “ship-with-fixes” seat, not
the parse-finder. DS/Qwen did not earn an occupancy pin from this round.

## Day 1 close (Q3 / Q5 / 5b)

| Call | Seat | cached / prompt | usd | Role |
|---|---|---|---|---|
| Q3 deep dive | Sol | write 262777 / 262780 | 0.757 | required |
| Q5 blueprint | Sol | **254116 / 263540** | 0.149 | required; fat hit |
| Q5b Terra | Terra Flex | write 254116 | 0.368 | same family — **not** the critic; artifact kept |
| Q5b DS V4 Pro | DS 0813 | 0 / 276392 | 0.176 | Rule B critic (not OpenAI, not Claude) |

Do not kill a fat-cache call. Terra 5b stands as extra notes. Independent
critique of Sol’s blueprint is DS. Blueprint → CREW jobs still **PENDING
APPROVAL**.
