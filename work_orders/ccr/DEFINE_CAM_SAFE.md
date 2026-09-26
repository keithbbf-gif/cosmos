# DEFINE — CAM + S:afe (one pen, OS-enforced)

Keith 2026-09-18: logical drive `S:` at install; only CAM (Cosmos Agent Master, **hard-coded, not an AI**) issues a write key (TTL, one at a time) **or** CAM keeps the key and applies Gitur→CCr-checked payloads onto a read-only live tree. Agents stay on the unsafe side. Same breaker for cloud/remote.

Research (GLM Flash + Ling `:free` round 2; Kleppmann fencing): a lease the agent holds is **not** enough. Zombie writers keep running after expiry. **The resource** must reject `token < highest_seen`. GitHub: protect `main`, no direct push, CI/bot-only merge. OS ACL: only one account can move the ref.

## Solution (research + Keith, compared)

**Pick CAM-holds-the-key (his OR).** Stronger than issuing a key *to* an AI CCr.

| Layer | What | Why (research) |
|---|---|---|
| **CAM** | Native Windows service / schtask. Not an LLM. Not Grok. Not Cursor. | Searchers: `cosmos-ci` / CI-only merge. AI can be jailbroken into a second pen. |
| **S:afe** | Install-time volume (VHD mounted `S:`). NTFS: Agents + TUI = **read**. CAM service account = **write**. Delete/modify ACL denied to everyone else. | Searchers: OS ACL on `.git/refs` + tree. Kleppmann: storage node checks the fence. |
| **Fence** | Monotonic `token` in `CCR.lease` (already exist). CAM records `highest_seen`. Stale token → **WARN ×3** then refuse write. TTL on any issued key; clock revokes; **one live token**. | Fencing papers: lease expiry does not kill the process; token on the **write** does. |
| **Hook** | Gitur PR merged (CCr checked) → payload to CAM → CAM writes `S:\`. No agent `search_replace` on `S:\`. | GLM: agents open `agent/*`; only CI fast-forwards `main`. |
| **Unsafe side** | `V:\A\Ai\COSMOS` (or worktrees) remains the dirty lab. Pen discipline still required. CAM does not replace P10. | Keith: does not obviate PEN DISCIPLINE on the unsafe side. |
| **GitHub** | `main` protected: no agent PAT push; squash-only; one GitHub account/bot = CAM or Keith. `starting_ref: main`. `origin/main..HEAD` ≠ 0 → WARN ×3. | Protected branches + linear history. |
| **Cloud** | Same breaker: remote bucket/volume write identity is CAM (or IAM role CAM assumes), not the model’s API key. | Same fencing: resource checks token. |

**Do not issue a write key to Grok/Cursor/GLM.** If CAM hands `S:` R/W to “whoever holds CCR.lease,” a second TUI that *thinks* it has the lease (zombie, 716fbaea after pen passed) writes again. CAM **applies**; it does not lend the ACL.

**Install:** `cosmos.py install` offers **two modes** (Keith: default flipped to A if executable; else user picks):

- **A Sandbox (default):** COSMOS + AIs **on `S:`**. Writes **outside `S:`** only via CAM/daemon (cDeck-controllable). Lab wipe of `S:` is still possible; off-`S:` (the rest of the PC) is Access Denied.
- **B S:afe:** `S:` is the **safe** LiT. Agents **read** only. **Only CAM** writes `S:`. Lab on `V:\A`. Human/AI `rd /s S:` denied.

Creates VHD, mount `S:`, ACL, CAM schtask. Cold peer, no bats. Same two modes for cloud/remote.

**Live tree on S:** ledger, `cosmos/`, `docs/` canon, `builds/cdeck` ship — whatever must survive a wipe. Work, logs, farm JSONL can stay unsafe until folded.

## Not

CAM is not an orch LLM. S: is not a second Core. Not OpenHands. Not a second scheduler. Unique HEAD “join GitHub keep local” is forbidden (CANON_ONE_HEAD). WARN ×3 before any refuse.
