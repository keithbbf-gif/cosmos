# Agent audit trail (Margie Irbe / 21 CFR Part 11 inspired)

**Keith 2026-09-09.** Logs are not an audit trail. A log says what happened
to the system. The trail says **which agent did what action, when, on whose
authority.**

Source of the standard: **21 CFR 11.10(e)** (time-stamped audit trails;
who did what, wrote what, and when; later changes do not obscure prior
entries) — the regime Margie Irbe works under. Records more generally:
**ISO 15489**. Provenance family: W3C PROV. BTS named this in
`V:\Ai\Publish\crew\WHITEPAPER_CoW.md`. COSMOS does **not** write that
tree. This file is the COSMOS encoding.

## What every multi-agent action carries

One append-only ledger event (or a porosity/farm row that the ledger
already points at). **Not a second log.** The service-signed JSONL is
authority.

| Field | Is | Not |
|---|---|---|
| **t / utc_off** | Timestamp at the **key point** (when the action committed) | a clock in the prompt prefix |
| **agent_id** | Named pin / seat / writer — a **key**, not a display label | rotator, `:free` alias, Auto |
| **action** | The verb (propose, ballot, review, dispose, spawn, refuse) | a paragraph of intent |
| **authority** | `source:class` — who let this happen | a vibe, a missing field |

**`source:class` vocabulary (named, not invented per call):**

| source:class | Means |
|---|---|
| `human:keith` | Keith typed / clicked |
| `ccr:g46` | this TUI disposed / wrote `V:\A` |
| `crew:<seat>` | farm mouth (`crew:glm`, `crew:luna`, `crew:gf38`, …) |
| `grokbot:qa` | Cursor Grok Bot QA manager **proposed** |
| `gitur:<leg>` | GitHub / GitLab / Cursor Cloud Agent |
| `core:ledger` | Core itself (hash chain, refuse) |
| `gfo:openwork` | GFO orch drop, not CCr |

Missing `source:class` → the row is **UNMEASURED** as an audit event. A
green log without these stamps is fabricated compliance.

A later public **weighted average** of agent tensors may be anchored on a
chain (P03 [0036b]). TABLED: `docs/research/docket/P03_PUBLIC_TENSOR.md`.
That digest still carries these stamps. It is not a second ledger.

## Rules

- Append-only. Never repair in place (same as the ledger).
- Agent ID is a **key** (named pin). Same agent, same id, every time.
- Timestamps mark **key points** (ballot in, review posted, CCr dispose),
  not every token.
- Grok Bot / CREW **propose**. Only `ccr:g46` writes the live tree.
- Do not put timestamps inside the **prompt prefix** (P11). They live on
  the trail, not in the cache.
- GET never mkdir. GET never invents a stamp.

## Bind — Model Rater is the unique join

Vendor catalogs (INT/COD/AGT, price) are **guidelines**. They do not say
who punched which hole, when, or on whose authority.

**COSMOS Model Rater** is the join:

| Layer | GET | Is |
|---|---|---|
| Catalog | `/api/v1/model_rater` | vendor rates; UNMEASURED if missing |
| Seats | same | occupancy pins (CCr, CREW, MOTIF lanes) |
| Scalar porosity | `/model_rater/porosity` | size-only hole fold (`loc_per_100 × severity`) |
| Pair tensor | `/api/v1/porosity` | orthogonality sketch + complement C |
| **Audit stamps** | on every observation | `t`, `agent_id` (key), `action`, `authority`=`source:class` |

That combination is the unique piece: **observed** multi-agent runs, not a
leaderboard, with an Irbe-style trail so a score is attributable. A
porosity number without stamps is not occupancy. A Grok Bot QA rubric
only counts when those stamps are on the row.

Ledger record already has `seq`, `event`, `t`, `utc_off`, `writer`, HMAC.
Multi-agent **payload** must also carry `agent_id`, `action`,
`authority` (`source:class`). Porosity `obs.jsonl` already has `at`,
`model_a`/`model_b`; add `authority` when the trial records. Farm
proposal JSON already has `model`; stamp `authority` on write.
