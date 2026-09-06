# RESEARCH QUESTION — OpenWork × COSMOS integration

**Stage:** 1 RESEARCH. **Not ARCH. Not BUILD.** Do not design the join in this file. Do not implement.

**Framed by:** CCr G46 TUI (Keith: *don't answer — frame the question and put it out for research*). Independent lanes. No peeking at another lane. Do not treat `docs/arch/OPENWORK_INTEGRATION.md` or PR #45 as the answer if you see them.

## The question

**How should COSMOS and OpenWork integrate — concretely, on this machine, without cloning each other?**

COSMOS is the OS (Core `:8770`, ledger, leases, clocks, Gitur). OpenWork is the orch harness (GFO, skills, plugins, MCP, session groups, automations, built-in browser, connectors, folder grants). Keith: *OpenWork has too much of what we need to ignore.* Until cDeck and OpenWork **merge**, Keith runs this Grok TUI himself (left HP 24N); GFO is fullscreen on the right HP 24N (Legal with Keith). Target ORC is GFO.

## What “integrate” must mean (constraints — not solutions)

- Two pens: CCr writes `V:\A`. GFO writes its grant. No COSMOS root grant to OpenWork.
- Do **not** iframe `OpenWork.exe`. Do **not** iframe OpenWork Web (Cloud; URL is a credential; $50/member).
- Do **not** rebuild OpenWork skills/Library/MCP/Automations/browser inside CORE.
- Do **not** rebuild Open Sessions in place (LIVE). `cowork_to_openwork` is a seed, not ORC recode; 666 stay on COSMOS for federation — do not re-ingest.
- Native COSMOS clocks stay Windows. Do not mint a 27th CLOCKS row that duplicates OpenWork Automations.
- Gitur: BUILD lands on **branched trees**. One job, one branch, one PR. Side jobs included.
- Legal stays GFO+Keith. This research does not open legal transcripts.
- Fail-closed. UNKNOWN where not bound. A claim is not evidence.

## Bound starting points (read; do not assume they are the join)

- https://openworklabs.com/docs/start-here/get-started
- https://openworklabs.com/docs/llms.txt
- `docs/OPENWORK_BIND.md`
- `builds/cdeck/ORCH_HOME_SPEC.md` P5 (C0 OPEN/LIVE; embed UNMEASURED)
- `builds/open_sessions/` + `GET /api/v1/recents`
- Live: Core `:8770`; GFO sit `V:\OPENWORK\COSMOS_2`; kept `V:\Streams\openwork`

## What to return

A **research** artifact only: `docs/research/OPENWORK_INTEGRATE_<lane>.md`

Must include:

1. What OpenWork actually offers that COSMOS would have to rebuild if ignored (bound to vendor docs + this install — version, paths, `/health`, grant).
2. What COSMOS already exposes that OpenWork could call (bound to `/api/v1/*` and cDeck C0 — list endpoints; note MCP **absent** if you measure that).
3. Candidate join shapes (at least two, independent). For each: pipes, what stays in which process, failure modes, what is UNMEASURED.
4. What is **not** the join (iframe, Cloud Web, second Core, second skill OS).
5. A recommended **next measurement** (one experiment, Gitur-sized), not a BUILD.

No CORE writes. No `main`. No merge of PRs #30 #32 #36 #37 #38.

## Lanes

- **Lane A:** Grok CLI / CCr worktree. Output `docs/research/OPENWORK_INTEGRATE_LANE_A.md`
- **Lane B:** Cursor Cloud Agent, independent clone. Output `proposals/OPENWORK_INTEGRATE_LANE_B.md` (P10). Pin Opus 5; refuse Composer 2.5.

CCr compares after both land. This TUI does not answer the question in-band.
