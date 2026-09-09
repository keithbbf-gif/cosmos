# P03 public tensor digest — TABLED

**Status:** TABLED 2026-09-09. **Not this BUILD.** Not a 14th provisional
slot. Not Core. Not a USPTO click. Not a public post.

Keith 2026-09-09: park the weighted-average / blockchain occupancy digest
in one markdown and **code the live store**. Written description already
lives in `P03_POROSITY.md` [0036a][0036b]. This file is the operator
table so the chain does not leak into Core this pass.

This TUI does not click Patent Center. Legal + Keith file. Do not post
whitepaper / X / LinkedIn / arXiv until provisionals are filed. Do not
stand up a chain. Do not invent weights or scores.

## Named matter

| Id | Named invention | Embodiment (if any) | This BUILD |
|---|---|---|---|
| P03 [0036a] | Per named agent, a tensor that is that agent’s **parameter set against each other agent** on named axes (n, freq, mean_err, mag, xor_err, cofail, rescue, orthogonality sketch) | SQLite `agent_tensor` PRIMARY KEY `(agent, vs, axis)`; JSONL `obs.jsonl` is authority; SQLite is a rebuildable projection | **CODING** — live Core store. GET `/api/v1/porosity` → `tensors[agent][vs][axis]` |
| P03 [0036b] | A **weighted average** of those agent tensors, **publicly published** as an occupancy digest | Weights an embodiment *may* take as n_obs, token spend, or inverse unit cost | **TABLED** — weights UNMEASURED; do not invent |
| P03 [0036b] chain | Anchor the digest on a **blockchain** (hash of the canonical weighted tensor + time + publisher identity) so a third party can verify occupancy without the live observation log | Chain = **public projection**, not a second OS, not a replacement for the service-signed append-only ledger | **TABLED** — do not implement a chain this tick |
| Irbe stamps on the digest | Timestamp at the key point, named-pin `agent_id`, `action`, `authority` as `source:class` travel with any later digest | Same stamps as `docs/AGENT_AUDIT.md` | **CODING** on live obs / HTTP POST; digest publish stays TABLED |

## Weights (UNMEASURED — do not invent)

| Candidate weight | Meaning | Status |
|---|---|---|
| `n_obs` | Observation count in the pair / agent slice | Named, not chosen |
| tokens | Token spend on that agent in the slice | Named, not chosen |
| inverse unit cost | `1 / cost` so cheap orthogonal specialists are not drowned by spend | Named, not chosen |

A formula that picks one of these without a measured occupancy decision is
a fabricated score. Leave the cell empty until Keith names the weight.

## What the chain is / is not

| Is | Is not |
|---|---|
| A **projection** of occupancy a third party can verify | Core |
| Hash of a canonical weighted tensor + time + publisher | A second ledger |
| Optional later embodiment of P03 [0036b] | The operating-system authority |
| Carrier of Irbe stamps | A repair-in-place store |

P07 already refuses “blockchain as the OS.” That refusal stands. A public
digest on a chain, if used later, does not become a second COSMOS.

## Live coding this pass (not the patent)

| Surface | Job |
|---|---|
| `state/porosity/obs.jsonl` | Authority. Append-only. Irbe `at`, `authority`, `action` |
| `state/porosity/porosity.sqlite` | Rebuildable. Tables `obs`, `pair_fold`, `agent_tensor` |
| GET `/api/v1/porosity` | Snapshot. Never mkdir. `tensors[agent][vs][axis]` |
| POST `/api/v1/porosity` | Pair or `action=trial` hook. Forwards Irbe stamps |
| POST `/api/v1/model_rater/porosity` | Scalar size-only fold. Forwards `agent_id` / `action` / `authority` |
| Forge `facilitate` | Calls `hook_trial` with `authority=crew:forge`, `action=facilitate` |

Schema: `cosmos-porosity-tensor/4`. Rotators refused. UNMEASURED until
observed. Do not invent scores.

## Off limits until un-tabled

- Stand up a blockchain, wallet, smart contract, or public hash post.
- Publish the weighted tensor (HTTP, IPFS, X, whitepaper).
- Click USPTO / Patent Center.
- Add a 14th $65 slot.
- Freeze a weight formula.
- Treat the SQLite projection as authority.

Un-table: Keith + Legal, after provisionals, with a named weight.
Packet: `P03_POROSITY.md`. Index: `docs/research/IP_DOCKET.md`.
