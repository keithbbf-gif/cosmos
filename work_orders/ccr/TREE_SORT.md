# Tree + Gitur sort — ORC finish (CCr not looped yet)

Keith: one track. ORC finishes the grade. Then CCr.

## Heads (sorted)

| Pointer | SHA | Role |
|---|---|---|
| **LiT `main`** | `e7603036` = `origin/main` | **The head.** Gitur merges live here. |
| `backup/unique-head-37` | `8b5ad84e` | **Archive.** Do not check out. Do not merge. |
| `stash@{0,1,2}` | KEEP / restore / docs-wip | **Archive.** Do not `stash pop`. KEEP already graded via 568/569/577. |

Two **commit** heads are gone. What remains is **dirt on disk** (untracked files) sitting on top of a clean `main`.

## Dirty `cosmos_*.py` — grades

**131 ADOPT_MAIN** — working bytes match `HEAD`. Already Gitur. **No merge, no revise.** Leave or ignore; do not add as a second copy.

**18 GRADE_DIFF** — python saw byte mismatch; `git diff HEAD` is **empty** (CRLF phantom, same as the bash-sandbox scar). **ADOPT_MAIN.** Do not “fix” with a rewrite.

**17 LOCAL_ONLY** (not on `main`). These are the only real leftovers. **Do not dump as one PR (577 was that mistake).**

| File | Grade | Next (CCr, after this sheet) |
|---|---|---|
| `cosmos_sandbox.py` | **KEEP** thin Gitur | Job-Object facade; 564 closed (HOST_PEN=V:\\). New small PR from `main`. |
| `cosmos_skills.py` | **KEEP** thin Gitur | Skill registry; 577 closed as bundle. |
| `cosmos_approval.py` `cosmos_delegate.py` `cosmos_recall.py` `cosmos_recall_clock.py` | **KEEP** thin Gitur | Hermes four; GET routes may already exist on main — CCr diffs vs `HEAD` before PR. |
| `cosmos_chamber.py` `cosmos_action_chain.py` `cosmos_temporal_fold.py` | **KEEP** or **HOLD** | Chamber GET on Core; cDeck **#320** still HOLD. Don’t dual-track. |
| `cosmos_nlcron.py` | **HOLD** | Same job as cosmos **#567**. Grade 567 vs this file, then one path. |
| `cosmos_packets.py` | **DROP / file** | `cosmos_packet.py` **already on main** (569). Plural file is a fork. |
| `cosmos_porosity_v6.py` | **HOLD** | Tensor `/5` frozen. Don’t land v6. |
| `cosmos_seat.py` `cosmos_crew_roster.py` | **HOLD** | Seats GET; occupancy. |
| `cosmos_research_call.py` `cosmos_session_ideas.py` `cosmos_session_tools_kit.py` | **HOLD** | Wishlist/session-tools FIFO later. |

## Gitur still open — CCr after ORC

| PR | Grade | Action |
|---|---|---|
| cosmos **567** | HOLD | Same as `cosmos_nlcron.py`. Pick **one**. |
| cDeck **320** | HOLD | Chamber paint. Don’t merge until Core chamber on `main` or explicit yes. |
| 570, 577 | DROP | **Already closed.** |

## House rule

ORC grades. CCr merges/opens **one** thin PR at a time from `main`. No unique-head checkout. No stash pop. No parallel TUI writing `cosmos/`.

ORC **done** when this file is the source of truth. Then loop CCr: start with **sandbox.py** thin PR **or** close 567 — Keith picks.
