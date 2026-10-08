# Resession trigger — Keith, 2026-10-02

Measured in Grok session `01a0fbf2`. This note is for the resession and auto-resession work. Session `01a0f6ca` owns that work.

## Trigger

Resession fires at **190000 input tokens** on a live Grok session.

Keith cannot watch the counter. 190000 is the explicit line, 10000 under the 200000-token point where Grok's long-context surcharge covers the whole prefix. Compaction is the expensive event. It rebuilds the cache. A resession carries a short pointer into a fresh session. Waiting until compaction, then also resessioning, pays both. On Grok the surcharge makes those last tokens well over 2× a resession.

The stock clock still asks at 75 / 80 / 85 percent and forces at 92 percent of a 200000 window (184000) only when `engage` is on. `docs/RESESSION_SOP.md` still warns at 130000 and packs near 70 percent without closing. 190000 replaces that close line for a live Grok session. Dead sessions stay idle. Operator hold still holds. Do not close other grok processes.

## The 10000-token gap

10000 tokens is enough for one tight close. It is not enough for a close that re-reads the tree.

The pointer pack is about 2000 tokens. Measured bytes:

| File | Bytes |
|---|---|
| `BUcr.toml` | 2351 |
| `BUhar.toml` | 2153 |
| `live/state/BOOTUP_PASTE.md` | 2051 |
| a `TIDYUP.md` | 1480 |
| a `tu2_adversarial.json` | about 1500 |
| `SEED.json` | 217 |

One short turn in the measuring session grew the prompt by about 3500 to 4000 tokens. The counter went 64021, then 67877, then 71226. A close that writes the pointer, runs TidyUP and TidyUP2, and injects is that size.

The measuring session's close did not fit. That turn made 16 model calls and 10201 output tokens while the prompt was already near 195000. The session counter crossed at 200313 and peaked at 205110. Compaction then dropped the next prompt to 64021.

At 190000 the close is one turn: write, run, inject. Do not open the tree again. A second look spends the whole gap.

## The new session is a separate bill

A new Grok Build session starts near 20000 tokens before any old history. The first tool call in the measuring session reported 19987. The successor pays that plus the short paste. That cache is under 200000, so it does not pay the surcharge. It does not come out of the old 10000.

## What to update

- A live Grok session resessions at 190000 tokens without Keith watching the counter.
- The close stays inside the remaining 10000: pointer, TidyUP, TidyUP2, inject. No corpus re-read on that turn.
- Compaction is not the close.
- Dead sessions stay idle. Operator hold still holds.
- Leave `CCR.lease`, `BUcr.toml`, and `live/state/BOOTUP_PASTE.md` as they are. The websites handoff in those two files stays.
