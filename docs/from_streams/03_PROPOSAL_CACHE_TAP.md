# Proposal — cache tapping

**Status:** proposal for review. Not landed. Does not edit `docs\PROMPT_CACHE.md` or the harness loop.  
**Asked:** 2026-10-02. A small ping that does not ask for a reply, sent so a warm cache does not expire. Claude on the monthly $20 plan was observed to drop cache every hour, and a small message restarts that clock.

## Idea

A tap replays the exact cached prefix plus a tiny uncached tail, a few minutes before that prefix’s TTL. The tail is not a question. Output is capped at one token and thrown away. The tap is not a conversation turn, so the next real call still sees the same prefix bytes.

P11 still holds: exact byte match, no clock in the prefix, measure `cached_tokens`. A tap with `cached_tokens=0` did not refresh anything.

This is not the existing “user-only ping.” That class is left untagged on purpose (`PROMPT_CACHE.md`). A tap must carry the same tagged prefix and the same `prompt_cache_key` the real calls use. An untagged ping does not keep the fat cache hot.

## Controls

One setting per seated prefix, default `off`.

| Mode | Behavior |
|---|---|
| `off` | No taps. |
| `on` | Fire `taps` times on the lead schedule below. |
| `smart` | Fire only when the cache is already warm, the prefix is large, and the chance the next real call arrives inside the refreshed window is above the floor. |

`taps` is an integer, default 1. Range 1–3. Smart mode may spend a confirm tap inside that cap. It does not exceed `taps`.

`lead` is how long before expiry the tap goes out. Default for a one-hour TTL is 3 minutes. The operator can set it.

`floor` is the minimum chance of a later hit. Default **0.20**, the bound from this request. Smart mode will not tap when its estimate is at or below the floor.

## When the taps go out

Clock starts at the last measured cache hit on that prefix (`cached_tokens > 0`). Expiry is that time plus the door TTL.

| TTL | Default taps | Schedule |
|---|---|---|
| About 1 hour (Claude $20, as observed) | 1 | One tap at expiry minus 3 minutes. |
| 5 or 10 minutes | 2 | First tap at expiry minus 90 seconds. Second tap at expiry minus 20 seconds, only if the first tap did not report `cached_tokens > 0`. |

A second tap after a confirmed hit is a wasted read. Short TTLs get two slots because a single shot can miss the window to jitter. The hourly Claude seat stays at one tap unless the first tap comes back cold.

The tail is a fixed byte string, identical every tap, and it is not appended to the session. Putting the tap into the transcript changes the prefix and the next real call misses.

## What “no reply” means

- Same prefix bytes as the last hit. Tail is a few tokens, outside the cache breakpoint.
- `max_tokens=1` and a stop at the first token.
- Discard that token. Do not show it. Do not write it into the harness journal.
- The tap does not enter the eight-hook loop, does not call `learn.step`, and does not clear a scar latch. One sample per turn stays the turn rule. A tap is a transport keepalive beside the loop.

If a door cannot cap output, that door’s tap stays `off` until a measured one-token call exists. A tap that draws a normal answer is not a tap.

## When it is a win

Names: `P` prefix tokens, `R` cache-read multiplier, `W` what a miss costs as a multiplier of the normal input price (a full uncached prompt, or a cache rewrite), `n` taps actually sent, `T` tail tokens, `O` output tokens.

```
tap_cost = n × (R×P + T + O)
save     = (W − R) × P
q*       = tap_cost / save
```

`q` is the chance a real call lands before the refreshed expiry. Tap when `q > max(floor, q*)`.

Large `P`, `T` and `O` near 0, `R=0.1`:

| Miss price `W` | Taps | Break-even `q*` |
|---|---|---|
| 1.0 (full input) | 1 | about 11% |
| 1.0 | 2 | about 22% |
| 2.0 (one-hour cache rewrite) | 1 | about 5% |
| 2.0 | 2 | about 11% |

The 20% floor sits above the one-tap rows and next to the two-tap full-price row. Above 20% on a large prefix, one or two taps are a win on these multipliers. Smart mode still computes `q*` from the door’s own `R` and `W`, then applies the floor. Rates in `PROMPT_CACHE.md` are guidelines. Re-measure before trusting a row.

`q` comes from the recent gaps between real calls on that same prefix. A chair that has gone quiet longer than the TTL does not get a tap. A cold prefix does not get a tap: the tap would be the write, and the real call is the right time to pay for that write.

Subscription seats need one extra price. If the $20 Claude plan counts the tap as a message, put that message cost into `O`. Token math alone can say win while the message cap says loss. Measure that once per seat and store it on the door row. Until that measurement exists, Claude-subscription smart mode stays `off` and manual `on` is the operator’s choice.

## Door row (starting point)

| Door | TTL | Default taps | Lead | Note |
|---|---|---|---|---|
| Claude subscription, $20 | 3600s, observed | 1 | 180s | Confirm tap only if the first returns `cached_tokens=0`. |
| Claude API, 5-minute ephemeral | 300s | 2 | 90s, then 20s | Second only if the first missed. |
| Claude API, 1-hour ephemeral | 3600s | 1 | 180s | Same shape as the subscription clock, different bill. |
| Qwen explicit | 300s, already in `PROMPT_CACHE.md` | 2 | 90s, then 20s | Tagged system block. |
| Vertex explicit `cachedContents` | the `ttl` already sent, often 3600s | 0 | — | Refresh by extending that object if the API allows it. Do not replay 100k tokens if a TTL patch exists. |
| Auto-cache doors (OpenAI, DeepSeek, GLM) | unmeasured | off | — | A tap is allowed only after a measured TTL and a measured `cached_tokens` hit. |

Minimum prefix: the door’s cache floor (OpenAI often 1024, Gemini often 4096, GF38 often 4096). Below the floor a tap cannot hit.

## State

Per prefix hash, in the attempt, not in the ledger:

- mode, taps, lead, floor
- last hit time, last tap time, last `cached_tokens`, last `cache_write_tokens`
- door TTL, `R`, `W`, message-cost flag
- recent real-call gaps, used only by smart mode

No key material. A tap log line is the prefix hash, the mode, `cached_tokens`, and the cost. Not the prefix text.

## Acceptance

1. `off` sends nothing.
2. `on` with `taps=1` and a one-hour TTL sends one request inside the lead window, and the usage line shows `cached_tokens` near `P`.
3. `on` with a 5-minute TTL and `taps=2` sends the second request only when the first line has `cached_tokens=0`.
4. The following real call’s prefix hash matches the pre-tap hash. The discarded tap token is absent from that prefix.
5. Smart mode skips a cold cache, a prefix under the floor, an idle chair, and any `q` at or below 0.20.
6. A tap does not move the harness turn count, the scar latch, or the seat journal.
