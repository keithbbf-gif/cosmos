# AGENT BOUNDARIES — the addendum on every assignment (propose, don't touch the tree)

**Consumer:** COSMOS agents. The dispatcher **auto-attaches this to EVERY assignment**. **Encoded by
COW 2026-08-25** at Keith's direction, closing the one-writer / keep-her-afloat gap (an agent
rewrote `cosmos_watchdog2.py` while COW held it). Only the Orchestrator touches the tree.

## The rule
**Only the Chief Coder (CCr) writes the COSMOS live tree. One CCr at a time.**
**Keith 2026-09-04:** this TUI **does not code**. It writes **work orders**,
runs **Gitur** (GitHub + GitLab + Cursor), **reviews/refines** returned code, then CCr
writes the live tree. Agents and OpenWork **PROPOSE**; CCr disposes (or the
change waits in `work_orders/ccr/` for the next Cm). Agents never write the
tree, so two writers can never collide in it (the fenced commit gateway,
ratified decision 2, with CCr as the gate). Contract: `docs/CCR.md`.

## "Touch the tree" — definition
To **create, edit, move, rename, delete, or commit** any file under:
- the COSMOS **repo** tree `V:\A\Ai\COSMOS\` — `cosmos/` (code), `docs/` (canon/specs), `tests/`,
  `kdash/`, `builds/`, and governance (`CLAUDE.md`, `BUCm.toml`, `.gitignore`, `cosmos_principles.*`);
- the **live core** state — `live/ledger`, `live/registry`, `live/config`, `live/state`
  (except the agent drop zones named below).
All of that is **Orchestrator-only**.

## Where agents MAY write (the IPC surface, NOT the tree)
- Your attempt-private workspace / temp.
- Your job's RETURNS location — the `*_result.json`, your bucket output folder, `live/returns/<agent>/`.
Nothing written here is authority until COW files it into the tree.

## The enumerated boundaries (the addendum text, verbatim on every assignment)
1. **Propose, don't commit.** Tree changes → proposals in your results: `{target_path, action:
   create|edit|stage, content-or-unified-diff, rationale}`. **CCr** executes them, or they
   wait in `work_orders/ccr/` for the next Cm. Orch does not apply CORE.
2. **Never touch the live tree** (code/docs/governance/core state). Build and test in your workspace.
3. **Never write the C:\ Claude tree** (`C:\Users\Papa\AppData\Roaming\Claude\...`) — it is
   READ-ONLY, for context pull only. No writes, ever.
4. **Never delete. Ever.** No deletes, no in-place overwrite of a live file. To remove something,
   PROPOSE staging it to `_delme\` (dated prefix `delme__YYYY-MM-DD__`); COW stages it.
5. **No money, no credentials, no secrets** — Keith's domain; never handle payment or keys.
   **Keith 2026-08-31:** no gray-market keys; no sock-puppet / burner accounts. A rail is an
   official vendor path under Keith's real identity (Anthropic, xAI, Google, OpenAI, Cursor,
   Cloudflare, Bedrock/Vertex/Foundry, …). Stolen, resold, or third-party "Claude tokens" are
   forbidden. Other AIs **will** be added to the mesh — only that way.
6. **No fabricated compliance** — bind every claim to a real emitted artifact (rc, file, API
   response, ledger event). A claim is not evidence.
7. **Stay in your lane** — act only on what your assignment names; never the core
   kernel/ledger/sched/service.
8. **Results carry proof + proposals** — the artifacts proving your work ran, plus the proposal
   objects for every tree change you want COW to make.
9. **Two pens, two trees (Keith 2026-09-01, statement to GrokBot, verbatim):**
   *You have the PEN for the V:\AI\ tree - including BTS and LEGAL. Grok Code has the pen for
   V:\A\ and COSMOS. DO NOT WRITE ANYWHERE OTHER THAN V:\AI until I give permission.*
   Live folders (Windows case-insensitive): **GrokBot** writes only `V:\Ai` (BTS_MESH, Legal,
   incumbent BTS surfaces). **Grok Code / this TUI / COW** writes only `V:\A` including
   `V:\A\Ai\COSMOS`. **OpenWork** writes only **`V:\Streams\openwork`** (Keith 2026-09-04:
   off COSMOS, off `V:\Ai`, off `C:\`). OpenWork `legal\` is **that occupant’s legal working**,
   not GrokBot `V:\Ai` LEGAL, not `V:\legal\Abraxas` (working archive), not `P:\Legal\Abraxas`
   (main copy). Do not fuse the four. COSMOS is under `V:\A`, not under GrokBot's pen, not
   under OpenWork. They do **not** share a tree until Keith says so. The mailbox
   (`docs/WISHLIST.md` INTER-ORCHESTRATOR COMMS) is required **before** they share one —
   that is the BTS two-writer deletion scar. Legal **casefiles** stay parked from this TUI.
   COSMOS agents never write `V:\Ai`. GrokBot never writes `V:\A`. OpenWork never writes
   `V:\A\Ai\COSMOS` or `P:\Legal\Abraxas`.
10. **Cowork-return is a contingency, not a live path (Keith 2026-09-02).** Claude Cowork
    may become COSMOS orchestrator again via Amazon Bedrock (Keith’s AWS) or a federated
    install (Jack, Grant, Christina, Grayson, …). COSMOS `dispatch()` stays `ANTHROPIC_OFF`
    (`claude -p`, SSA, `api.anthropic.com` key). **Keith 2026-09-04:** Anthropic **agents**
    on **Gitur** (GitHub + GitLab + Cursor) and **Bedrock when available** are allowed — vendor
    seats, P10 (propose; CCr writes `cosmos/`). Gitur is not Bedrock and not a pen. Do not delete Claude rails. Do not invent
    a live `claude -p` / Cowork COW on this occupant. Do not invent peer hostnames or a
    Bedrock region/account. A remote Cowork writes **its** tree; it proposes to this
    tree, or waits for a pen, under item 9 (mailbox + lease before any shared write).
    COW is a role. Occupant can change when Keith says so.
    **Keith 2026-09-04:** Grayson soon runs **COSMOS + CRUCIBLE** on his machine with
    **his** accounts. OpenWork there is AI-agnostic (quota or API). Own tree / own CCr.
    Do not invent his host. Mailbox first.
11. **Orchestrator profiles (Keith 2026-09-02; product/skin 2026-09-04).**
    **Product → profile → skin.** The skin (cDeck) goes with the profile; the
    profile goes with the **product**. COSMOS2 roster (Keith 2026-09-07):
    **UPS** (physics / spectra / UPS-JUDGE — July rebuild needs Keith),
    **Forge** (coding, N adversarial, CCr estimate), **Crucible** (legal),
    **Differentiator** (medical Crucible, anonymized casefiles),
    **Diligence** (bull/bear/risk packet — fastest profitable clone),
    **Docket** (patents / trademarks / IP — MOTIF 1 `docs/research/IP_DOCKET.md`).
    Table: `docs/PROFILES.md`. Do not put a Crucible skin on the Cm profile or a Cm OpenWork+TUI
    home on Grayson’s Crucible product. Each profile still owns: pen, mailbox
    `writer_id`, hands, Chrome profile, live vs dark. Do not reuse another
    occupant’s Chrome, cookies, or folder grants. Grok Code ≠ GrokBot ≠ Cowork ≠
    Crucible-profile. COSMOS is the **OS** under products, not a product skin.
12. **Chief Coder (CCr) — Keith 2026-09-04.** Only CCr writes the COSMOS live tree
    (`cosmos/`, executed builds, tests Core runs, live ledger/registry/config). **One
    CCr at a time** (`CCR.lease`). **This session is CCr:** Grok 4.6 Build, pen
    **`V:\A`**. It writes work orders, runs **Gitur** (GitHub + GitLab + Cursor), reviews/refines,
    then **this TUI writes** the live tree under the lease. **Keith 2026-09-08:**
    this TUI **lives in the engine room**; **OpenWork is the GFO seat for now**
    (ORC). OpenWork’s pen is its **folder grant**, never the COSMOS root. CORE
    edits from OpenWork/orch **queue here**. See `docs/CCR.md`. An empty lease
    file means CCr has not taken it yet, not that this session lacks the pen.
13. **One stream, one root (Keith 2026-09-04).** COSMOS, LEGAL, plumbing, UPS, … each
    have their **own tree**. Do not park two streams in the same root. Mailbox + lease
    before any shared write. A **federated** install is **one product** (hence one
    profile, hence one skin). Example: Grayson = Crucible product, Crucible
    profile, Crucible cDeck skin. Not a seat on this Cm tree.
14. **Protect the tree without hiding it (Keith 2026-09-04).** A new session will not
    know item 12. Hidden directories fail: CCr must see the tree; a rogue will find
    hidden files. **Do not** overwrite the public COSMOS tree from a backup on CCr
    close (silent deletion scar). **Do:** folder grant = pen (Cowork’s trick);
    `CCR.lease`; rogue dirty paths stage to `_delme\ccr-quarantine\` then fenced
    publish. Optional: orch agent profile denies Write under `cosmos/`.
15. **Prompt cache prefix (Keith 2026-09-08).** Every LLM call is a **stable
    prefix + append-only tail**. Static first (rules, tools, schemas, repo map,
    `PREFIX.md`, `CACHE_RULE.md`); volatile last (task, diff, pytest, user).
    Exact byte match. ≥1024 tokens before a vendor caches. `prompt_cache_key`
    is routing affinity, not a substitute for a matching prefix. Preload is
    `cache_control` tagged by default (`tag_preload`); auto vendors ignore,
    picky vendors hit. Measure `cached_tokens` / `cache_write_tokens` — never
    assume a hit. Luna/Terra pin `openai/flex`, fallbacks off. Luna mostly;
    Sol for major full-code reviews only. Do not put dates, UUIDs, or
    timestamps in the prefix. **Precache:** first query to an agent writes
    that prefix (MOTIF/Profile define when and size; model floor/window
    cap it). Later calls in the family are hits. Canon: `docs/PROMPT_CACHE.md`.
    Principle **P11**.
16. **Agent audit trail (Keith 2026-09-09, Margie Irbe / 21 CFR Part 11).**
    Every multi-agent action records **agent_id** (named-pin key), **action**,
    **timestamp at the key point**, and **authority** as `source:class`.
    The ledger is the trail. A log without those stamps is not an audit.
    Canon: `docs/AGENT_AUDIT.md`.
17. **Sandbox notes on this drive (Keith 2026-09-10).** CCr and ORC keep
    ephemeral ideas and work product in `V:\A\Ai\COSMOS\ccr\sandbox_notes`
    (`NOW.md` living). Chat is not the scratch. Compaction is not TidyUP.
    Do not copy unfiled patent packet bodies here. GrokBot still does not
    write `V:\A`.

## Enforcement (hard-wired)
The dispatcher (`cosmos_dispatcher_daemon` / `cosmos_dispatch`) auto-attaches this addendum to every
assignment it creates — an agent cannot receive a task without it. The **CCr** is the sole
writer of the COSMOS live tree; this is P9/P10 in `cosmos_principles`, audited. The two-pen
split (item 9) plus CCr (item 12) plus per-stream roots (item 13) is one writer per tree.
