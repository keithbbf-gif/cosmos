# Agent prompting — CCr style book

CCr writes the prompts. Agents code. Gitur is the last hop. **Reprompt = the
prompt failed.** Fix the prompt; do not add a second review panel.

Complete · concise · effective. One job, one tail, one return shape.

## Shape (every call)

1. **Stable prefix** (byte-identical across a cache family). No dates, UUIDs,
   branch names, or “this hour” status.
2. **Volatile tail** — the ITEM only: path, reuse, bite, must-not.
3. **Return shape** in the tail: `path` + unified diff or full file, or
   KEEP/DROP one line. Mouth still: **diff first or none**.

Canon: `docs/PROMPT_CACHE.md` · `CREW/IN/CACHE_RULE.md` · `CREW/IN/CODING_GUIDELINES.md`.
P11 occupancy. Measure `cached_tokens`. A hit not in usage is not a hit.

## Do

- One area per team. Dual-family: **one Vertex + one other family**.
- At least **3 families** on the farm. **4th = Cursor Sonnet** when that is
  the actual Cloud Agent model. Today Cursor is pinned **grok-4.6** (xAI) —
  that is a 4th family only if you count Gitur as a coder; it is **not**
  Anthropic until the pin is Sonnet.
- Families now: Google (GF38 / Gemini 3.1 Pro) · Zhipu (GLM) · DeepSeek (DS).
  Luna Flex = OpenAI credit mouth, **not** a second Google seat, **not** Sol.
- Bounded corpus for cDeck (ORCH_HOME + FEATURES + CODE_CDECK). Do not send
  the 407k pack to a tab job.
- `require_bootup` before CREW/Gitur. `NO_BOOTUP` is correct.
- Stub, don’t forget: Profile skin select (`data-stub=profile-skin`) —
  default graphics + colors. **Do not build skins this pass.**

## Do not

- Recite occupancy the mouths already have (ballot DROP, two pens, UNMEASURED).
- Luna KEEP/DROP every file (that is a review panel). Luna: one-line BLOCKING
  or skip.
- Sol as Luna’s pair (same family, ~0 orthogonality).
- Ling / Solar / Luna Pro unless Keith names them.
- Naked first query. Reorder prefix. Dates in prefix.
- Third-fire Cursor on an empty branch. Fix the WO instead.
- Mix cosmos Core and cDeck in one ITEM.

## Seat card (windows + cache)

| Seat | Family | Window | Cache | Use |
|---|---|---|---|---|
| GF38 `gemini-3.8-flash` Vertex | Google | large | Vertex implicit; measure | Team A quality |
| Gemini 3.1 Pro Vertex | Google | large | same | Team B quality (not same team as GF38) |
| GLM `z-ai/glm-5.3-flash` | Zhipu | **1.4M** | OR `cache_control`; often write=0 | Team A cheap |
| DS V4 Flash | DeepSeek | **1.4M** | same | Team B cheap; 429 retry |
| Luna Flex | OpenAI | **1.1M** | Flex TTL ~30m; `prompt_cache_key` + breakpoint | Credit / short follow-up on **same prefix** |
| Cursor Cloud Agent | xAI grok-4.6 **or** Sonnet if pinned | vendor window; **stay under 200k** | n/a | Gitur last hop, autoCreatePR, **must commit**. xAI **2× surcharge >200k** — cheaper to new-session. G46 coding does not need a huge load. |
| Sol | OpenAI | 1.1M | not Luna’s cache | Major review only, Keith-named |

Prefix floor ~1024 tokens. Luna/Gemini floors in CACHE_RULE. Exact bytes.

## Teams

| Team | Area | Vertex | OR |
|---|---|---|---|
| A | cDeck needed tabs (not skins) | GF38 | GLM |
| B | COSMOS leftover bites | Gemini 3.1 Pro | DS |

Then CCr Gitur + apply. Cursor if Sonnet = 4th family on Gitur, not a fifth check.

## ITEM template (tail)

```
Repo: keithbbf-gif/{cosmos|cdeck}  Branch: ccr/<slug>
Reuse: <existing files>
Do: <one behavior>
Bite: <typed refuse + all_bite>
Must not: ballot, GET /forge, leftover PRs, skins buildout, Cowork-home rewrite
Keep stub: data-stub=profile-skin
Return: unified diff first
```

If the agent empty-branches or ramble-answers, **the ITEM failed**. Shorten.
Drop recited occupancy. Name the file. **Size after preload:** `MAX = window − (cache + prompts) − 0.20×window` (hard, never 0). **OPTIMUM** = expected+headroom if known (10k py → 15k, must be > 0) or `"float"` — **never 0**. `cap_tokens` never 0. Shoot OPTIMUM when it is a count; obey MAX. On **xAI/G46**, also keep the **input** under **200k** (2× surcharge above that; cheaper to new-session).

## cDeck Gitur tab (canon)

10-minute CCr roster + spend + coder output **must land on the Gitur tab**,
not only this TUI. JSONL `live/state/crew/roster.jsonl`. GET `/api/v1/gitur`
folds `crew`; GET `/api/v1/crew` is the same read. GET never mkdir.
`#bd-gitur-crew`. Coders propose paint/diffs; CCr Gitur/applies.

## Luna cache (do not overwrite)

- Mouths: `gf38-001.json`, never `gf38.json` clobber (`_iter_out.next_pair`).
- First successful Luna write **freezes** `CREW/OUT/LUNA_IMPROVE/frozen/{sys,user0,user1}.txt`.
- 2h window: later calls **only read frozen**. New crew rounds do not enter the prefix.
- Queries = untagged tail only. `cached_tokens==0` means prefix moved — you overwrote.
- Keep-alive every 30m with **identical** frozen bytes. Flex TTL 30m.
- Do not edit `LUNA_PREFIX.md` during the window.
