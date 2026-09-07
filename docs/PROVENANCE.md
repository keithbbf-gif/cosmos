# Public provenance vs private build (Keith 2026-09-07)

**Goal:** most of the **build** goes **private**. What stays public is enough to
**prove COSMOS ran** — including as **BTS-MESH from early July 2026** — and to
show **provenance**. Not a history rewrite. Not a secret-scrub of GitHub
(that history is already public).

## Do not

- Flip `keithbbf-gif/cosmos` or `cdeck` or `bts-mesh` private **until** Keith
  does it (credentials) **and** a frozen public provenance pointer exists.
- Force-push or delete GitHub history (apk-blob scar; also destroys provenance).
- Commit `live/ledger/`, keys, `gemini_cli_env.json`, spend files.
- Pretend private-now undoes public-then (see `docs/research/IP_DOCKET.md` clock).

## What stays public (provenance pack)

Enough for a third party to see **dates and identity**, not the live tree.

| Artifact | Why it proves run | Where |
|---|---|---|
| GitHub `bts-mesh` created **2026-08-16** | Public repo; description names CRUCIBLE | https://github.com/keithbbf-gif/bts-mesh |
| July dated BTS docs | Operation in early/mid July | `V:\Ai\BTS_MESH` (GrokBot tree; copy **excerpts** into a public provenance folder, not the whole mesh) |
| GitHub `cosmos` created **2026-08-23** | Ratification day | https://github.com/keithbbf-gif/cosmos |
| `docs/RATIFIED.md` + `docs/FINAL_ARCHITECTURE.md` | Architecture named and dated | public cosmos (already) |
| `docs/MOTIF.md` | Method named 2026-08-25 | public cosmos (already) |
| GitHub `cdeck` **2026-08-24** | Product BUILD | https://github.com/keithbbf-gif/cdeck |
| Live ledger **head** (seq + event + hash), not the full JSONL | This install is still running | quoted in a provenance note; **not** the ledger file |
| KDash / jack_command dated lift | Dashboard existed pre-COSMOS name | `_lift/jack_command_2026-08-16.html` in cDeck; BTS `jack_command.html` |

A **provenance README** on the public repo should say: COSMOS is the OS;
BTS-MESH was the July predecessor; Core has been resident; source of the
continuing build is **private**. Do not dump `live/`.

## What moves private

| | |
|---|---|
| **Continuing source** | `cosmos/` implementation, cDeck `ui/` beyond the provenance snapshot, session-tools, rails, spend, workers |
| **New GitHub repo** | Private. Keith creates (credentials). Suggested name `cosmos-private` or org `KMesh`. CCr does not mint the repo. |
| **Gitur** | Point BUILD at the **private** remote once it exists. Public `cdeck`/`cosmos` become **archive + provenance**, not the daily BUILD. |
| **Occupancy / CCR / profiles** | Stay on the live tree; do not need a second public occupancy dump |

## Split procedure (when Keith has created the private repo)

1. Freeze public HEADs (note SHAs: cosmos, cdeck `5a7450d`, bts-mesh).
2. Mirror to private (full history). Daily push = private.
3. Public: provenance README + tagged `provenance-2026-09` of docs that prove dates. No new feature source.
4. Legal files provisionals (Docket). This stream does not.

Until the private remote exists, CCr **keeps Gitur synced on the current
public product remotes** (Keith: keep GitHub synced) **and** does not add
new novel source to public if Legal says stop. That stop is Keith’s word.
