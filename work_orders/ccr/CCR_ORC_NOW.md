# ORC → CCr (2026-09-18)

Mailbox. Orch `716fbaea`. You hold the pen (`CCR.lease` sid `f47bad79`, grok pid **77372** alive).  
Keith: **STOP. SOP: they stay until judged.** Do not apply patches. Do not merge unjudged. SOL off. `CCR_LIT_QUEUE.md`.

**SUPERSEDES** `CCR_BRIEF_f47bad79.md` (that file still says unique-head / do-not-pull — that is stale and wrong).

Pack: `live/state/session_saves/20260918T094918/`  
Luna grades: `.../judge_luna-flex.txt` (MEASURED `openai/gpt-5.6-luna`, gen `gen-1789742965-JeBXw9L8flgtynVSxtGu`, $0.0063441, `cached_tokens=0`).

---

## LiT (do this first)

| | |
|---|---|
| **HEAD** | `4ebc4efd` = `origin/main` (#567 NL cron). `origin/main..HEAD` = **0**. |
| **Unique-head** | `8b5ad84e` **killed**. Ref `backup/unique-head-37` gone. Stashes empty. Do **not** check out, merge, or restore it. |
| **TidyUP of that head** | Git pointer in this orch TUI, **not** a grok session close, **not** a headless subagent. No `session close`, no 5a/5b. Valuables in the pack + `_delme/dirty-clean-20260918/`. |

## Dirty (leave / file)

- **KEEP dirty:** `CLAUDE.md` (prompt-cache SOP vs HEAD). Untracked canon (`docs/CANON_*.md`, `docs/arch/CSnS.md`, docket). KEEP tests: sandbox / packets / hermes / session_ideas / research_call.
- **LEAVE:** `builds/cdeck` submodule inner-dirty. **cDeck #320 HOLD.** Do not reset.
- **FILED:** scratch + untracked inbox copies → `_delme/dirty-clean-20260918/` (never deleted). Tracked `work_orders/` restored from HEAD after a bad move.
- **Do not ingest** `work_orders/drop/` as-is (no WOMBAT; no extra `grok.exe`).

## Judges (then Gitur)

Keith: other families, then Gitur. **Not Grok.**

| Seat | Result |
|---|---|
| **SOL Codex** `codex exec` read-only **#580–#586** (oa-api, data-share complimentary; **0 cache writes**) | **All seven request-changes. Do not merge.** Details `JUDGE_SOL_PR{n}_last.json`. Mouth often `gpt-5-codex`/`gpt-5` not requested gpt-5.4. |
| **GLM 5.3 Flash** `z-ai/glm-5.3-flash` | **HTTP 429.** DeepInfra `engine_overloaded`, `limit_source=upstream_provider_shared_pool`. **Not our OR key.** Same 429 on `z-ai/glm-5.3` via InferenceNet. No `z-ai` key on disk. Retry later or Z.AI BYOK. |
| **GF38** `google/gemini-3.8-flash` on OR | Truncated (reasoning ate `max_tokens`). Not a second full grade. Kelly Vertex is **GF38**, not GLM/Luna — do not burn Kelly to unstick GLM. |

### Luna KEEP → thin Gitur from `origin/main` (one job one PR)

`cosmos_sandbox.py` · `cosmos_skills.py` · `cosmos_approval.py` · `cosmos_delegate.py` · `cosmos_recall.py` · `cosmos_recall_clock.py` · `cosmos_action_chain.py`

Sources: `_delme/dirty-clean-20260918/cosmos/` + KEEP tests. Diff vs **HEAD** first. **#564 closed** (do not revive `HOST_PEN=V:\`). **#567 already merged.**

### Luna HOLD / DROP

- HOLD: chamber / seat / crew_roster / porosity_v6 / research_call / session_ideas / session_tools_kit / temporal_fold. Chamber stays with **cDeck #320 HOLD**.
- DROP: `cosmos_packets.py` (main has `cosmos_packet.py`). All **37** unique-head commits DROP — do not re-apply.

Inbox 107: Luna graded; many KEEP are already Gitur'd or docs. Do not re-fire WOMBAT. Split remaining KEEP to **one PR each**.

## Do / do not

**Do:** `git pull` (fast-forward only; you are already on origin/main). Gitur **sandbox** thin PR first unless Keith names another. Measure `cached_tokens`. One CCr.

**Do not:** extra `grok.exe`. Restore `8b5ad84e`. Ingest 103 as-is. USPTO. Write `V:\Ai`. Merge cDeck **#320**. Sit ORC. Dual-write `cosmos/` while this orch is grading.

## Wallets (for when you code, not this grade)

- GLM Flash + Luna Flex are the two **highest COD under $1/M output** on the A-team (71.5 @ $0.25 out · 71.4 @ $0.60 Flex out). Split: **GLM volume coder, Luna judge**. DS Flash is cheaper ($0.16 out) at 69.1.
- Luna via OpenRouter **is not** Codex. Codex = `codex exec` CLI, key `live/config/openai_api_key.txt` (**present**). Seat Luna there when Keith wants the harness.
- Kelly = Vertex GF38 (`vertex-coding.json`). Not GLM. Keith: another Kelly if this one depletes — ask before you spend it.
