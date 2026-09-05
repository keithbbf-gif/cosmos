# MAKER HANDS — decision-ready shortlist

**Pass:** Claude Code, native on the live tree, 2026-08-31 (probe `ts=2026-08-31T03:47:26Z`).
**Tree HEAD:** `56fa423c9e9600278a2e51248fcbde77307330a6` · sentinel `tree_id=KMesh-COSMOS-live` · host `KC-PC`.
**Wishlist rows:** *Maker-hands — sweep every AI-maker's tools; wire the useful ones as COSMOS
rails/nodes* · *ADD HANDS + PUBLIC AIs*.
**Prior stage read first, NOT redone:** `docs/critique/makerhands_STAGE3.md` (G46 rank 2026-08-25 +
STAGE-2 ARCH + STAGE-6 re-probe 2026-08-27). Its rubric, its rejected list, and its UNKNOWN register
are **carried forward unchanged**. This file adds one thing that document could not have: a
**fresh measurement of every candidate from this machine**, and it supersedes three of its
blockers that measurement shows are stale.

**Write-fence for this pass:** `builds/probe/` + `docs/research/` only. `cosmos/` is outside the
fence, so §6 is a **PROPOSAL for COW**, not an installed change.

---

## 1. What counts as a HAND

An API that exists is not a hand. A hand is **a named verb that runs on this machine and returns a
value only that surface can emit.** `--version` proves a binary shipped; it proves nothing about
whether COSMOS can reach the thing. So every row below was probed with an *authenticated or
functional* verb wherever one exists at $0.

| verdict | means |
|---|---|
| **HAND** | a verb ran here and emitted a surface-only value. Reachable now. |
| **CRED_BLOCKED** | the surface answered and refused for want of a credential. **Keith's domain.** |
| **ABSENT** | binary/endpoint is not on this machine. An install, not a credential. |
| **UNMEASURED** | not probed this pass. The row says what would close it. Never a guess. |

**Harness:** `builds/probe/maker_hands_probe.py` (this pass). Root is `--root`-supplied and verified
by sentinel **content**; no hard-coded paths. Secrets are never printed — credential rows carry the
refusal code only. Evidence: `builds/probe/maker_hands_evidence.json`.

**Tally this pass: HAND 19 · CRED_BLOCKED 3 · ABSENT 4 · UNMEASURED 1.**

> **Method scar, recorded because it nearly shipped.** The harness first scored *MCP python SDK* as
> **HAND** off a `ModuleNotFoundError` — Python 3.14 tracebacks echo the failing **source line**, so
> the very token being searched for came back verbatim from the crash. Substring-matching output is
> not proof. Fixed generally rather than per-row: **a non-zero exit can never be a HAND**
> (`maker_hands_probe.py`, `probe_cli`). The same guard is built into the §6 proposal and is
> pinned by a test there. Two rows changed verdict once it was in.

---

## 2. Three stage-3 blockers that measurement SUPERSEDES

Stated up front because they change what "cheap to wire" means.

**S1 — "Dispatcher rails are blocked on Kernel attach" is CLOSED at HEAD.**
Stage-3 ranked worker-first *because* `Kernel.__init__` did not call `register_node_rails`, making
any rail edit a false green. That is no longer true. `cosmos_kernel.py:141` now defines
`compose_rails()`, called from `__init__` on a writing boot (`:137`), over a six-entry table
(`:177–184`). Measured, read-only dry-run:

```
composed: node_rails, cursor-api, codex-cli, playwright-dom, firecrawl-web, claude-cli
warnings: {}
adapters: claude-cli, codex-cli, cursor-api, firecrawl-web, gem-api, gw-api, oa-api,
          playwright-dom, sgh-api
dispatcher_constructs: Dispatcher
```
→ **A rail is now the cheapest shape to wire, not the most expensive.** §6 uses it.

**S2 — Three of stage-3's "wire next" rows are ALREADY WIRED and live.**
`playwright-dom`, `firecrawl-web` and `cursor-api` exist as rail modules, compose into the Kernel,
and pass their own `--probe` today. They are **deltas, not candidates** — do not re-rank, do not
re-add.

**S3 — A NEW cross-cutting blocker that outranks every row below.**
`GET http://127.0.0.1:8770/api/v1/health` → `WinError 10061` (connection actively refused).
**COSMOS Core is not serving.** Rails compose correctly in a dry-run, but until Keith runs
`cosmos serve`, *no* rail is reachable through the API gateway — every green below is a satellite
probe. Wiring more hands into a Core that is down adds capability the mesh cannot yet call.

---

## 3. The shortlist — ranked by (value × cheapness)

**Value** = new COSMOS capability, not vendor marketing. **Cheapness** = work to reach a wired,
composed rail from where the tree is *today*. Both 1–5; score is the product.

### Tier 1 — wire now · no credential from Keith · no install

| # | hand | V×C | evidence (verb → surface-only value) | blocker |
|---|---|---:|---|---|
| **1** | **GitLab forge (`glab`)** | 5×5=**25** | `glab auth status` rc=0 → logged in `keithbbf-gif` (**keyring**), REST `gitlab.com/api/v4/`, git over ssh. `glab api user` rc=0 → `{"id":41407957,"username":"keithbbf-gif","state":"active"}`. `glab ci status` rc=0 → pipeline **2790929269** success 41s, SHA `419bfb5e…` | Green pipeline is on SHA `419bfb5e` ≠ HEAD `56fa423` — **a stale-SHA green, the C-48 class**. No project runner; hosted minutes UNKNOWN (both carried from stage-3, not re-measured). `glpat-` still embedded in the GitLab remote userinfo (stage-3 M2) — rotate if ever logged. |
| **2** | **GitHub forge (`gh`)** | 4×5=**20** | `gh auth status` rc=0 → `keithbbf-gif` (**keyring**), scopes `gist, read:org, repo, workflow`. `gh api rate_limit` rc=0 → `{"limit":5000,"remaining":5000,...}`. `gh repo view --json` rc=0 → `{"isPrivate":true,"visibility":"PRIVATE"}` | Repo is **PRIVATE** → hosted Actions burn the Free minute pool; stage-3 H3 (the "public = $0" stack) stays superseded. No `.github/workflows`. Actions minutes remaining UNKNOWN. |
| **3** | **xAI Docs MCP** | 3×5=**15** | `POST https://docs.x.ai/api/mcp` `initialize` → **HTTP 200**, `serverInfo={"name":"xai-docs-mcp","version":"1.0.0"}`, protocol `2025-06-18`, `capabilities.tools.listChanged=true`. **Keyless.** | Mounted in **no** host: `grok mcp list` → `BFast` only; `codex mcp list` → `bfast` only. Config drop, nothing more. |
| **4** | **OpenAI Docs MCP** | 3×5=**15** | `POST https://developers.openai.com/mcp` `initialize` → **HTTP 200**, `serverInfo={"name":"openai-docs-mcp","version":"1.0.0"}`. **Keyless.** | Same: not mounted anywhere. Replies in **SSE framing** (`event: message` / `data: {…}`) where xAI replies plain JSON — a client must parse both. |

### Tier 2 — wire now · a WALLET decision, not a credential

| # | hand | V×C | evidence | blocker |
|---|---|---:|---|---|
| **5** | **Codex CLI — ChatGPT seat** | 4×3=**12** | `codex login status` rc=0 → **`Logged in using ChatGPT`** (prepaid seat, live) | **Wallet mismatch, not a missing key.** The `codex-cli` rail probe returns `UNREACHABLE: NO_KEY: OpenAI key missing at live/config/openai_api_key.txt`. The rail demands a **metered API key** for a lane whose **seat is already paid and working**. Dropping a key here is the *wrong* fix — stage-3 H5: a key in that env **steals the seat** and opens a new bill. The fix is a rail change (seat mode). |
| **6** | **Claude Code CLI — F5 seat** | 4×3=**12** | `claude --version` rc=0 → **`2.1.251 (Claude Code)`** (stage-3 saw 2.1.220 — updated since) | Identical shape: `claude-cli` rail probe → `UNREACHABLE: NO_KEY: Anthropic key missing at live/config/anthropic_api_key.txt`. Same wrong-fix trap. |
| **7** | **Gemini CLI** | 2×4=**8** | `gemini --version` rc=0 → **`0.52.0`** | **Not a new lane.** Stage-3 measured `selectedAuthType=vertex-ai` — the same wallet as the existing `gem-api` rail (stage-3 M4 demoted it for this reason). **Not re-measured this pass**; if Keith ever adds a Studio key it becomes a distinct wallet and re-ranks. |

### Tier 3 — needs a CREDENTIAL from Keith · see §4

| # | hand | V×C | evidence | blocker |
|---|---|---:|---|---|
| **8** | **Groq (LPU speed class)** | 3×4=**12** | `GET https://api.groq.com/openai/v1/models` → **HTTP 401** `{"error":{"code":"invalid_api_key"}}` — endpoint live, refuses cleanly | **Credential.** No `groq_api_key` in `live/config/`. Free tier = no card, 429 when over. OpenAI-compatible, so cheap once keyed. Default model `openai/gpt-oss-20b` (stage-3 M3 — **not** MESH's stale Llama prose). |

### Tier 4 — install-blocked · no credential, an INSTALL

| # | hand | V×C | evidence | blocker |
|---|---|---:|---|---|
| **9** | **Ollama local** | 5×1=**5** | `GET http://127.0.0.1:11434/api/version` → **`WinError 10061`**, connection actively refused | **Not installed** (stage-3 H4 confirmed, third pass). Strategically the highest-value row in the whole sweep — the only candidate immune to quota/billing/consent-to-lapse, which is canon's DOM-first logic applied to inference. VRAM is known (RTX 3070, 8192 MiB, stage-3) so a small tool model fits. **Blocked on Keith installing it — nothing else.** |
| **10** | **Aider** | 2×1=**2** | `aider --version` → `NOT_ON_PATH` | Install. Earns its slot only on the distinct SEARCH/REPLACE + one-commit-per-edit protocol (stage-3 rubric 8). |
| **11** | **MCP Fetch** | 1×2=**2** | `uvx --version` → `NOT_ON_PATH`; `import mcp` → `ModuleNotFoundError` | Install (either path). **Value has decayed since stage-3 ranked it A4:** Playwright MCP (24 tools) and Firecrawl are both live rails now, so URL→content is already covered twice. Recommend **drop**, not defer. |

### Already wired — deltas only, do NOT re-add (S2)

| hand | live evidence this pass | delta / blocker |
|---|---|---|
| **Playwright MCP** `playwright-dom` | rail `--probe` → `ok=true`, **`tool_count=24`**, `serverInfo.version=1.63.0-alpha-2026-08-05`, navigate+snapshot present | Default DOM worker; `cosmos_browser --dump-dom` is overflow (stage-3 M5). Unreachable through Core while :8770 is down. |
| **Firecrawl** `firecrawl-web` | rail `--probe` → `ok=true`, **`primaryId=arxiv:gr-qc/9504041`**, `http=200` | Papers id differs from every prior pass (`pmid:11089135` 08-27, `arxiv:physics/0103087` 08-26) — **proves a live fetch, not a replayed record**. Keyless daily cap remains unpublished. |
| **Cursor** `cursor-api` | rail `--probe` → `ok=true`, `apiKeyName="Cursor COSMOS 2"`, `http=200` | Only rail with a COSMOS-held credential that works (`cursor_cosmos_key.txt`). |
| `sgh-api` / `gw-api` / `gem-api` / `oa-api` | present in the composed adapter set above | Stage-3 §"Already on the mesh" stands. |

---

## 4. Credential ledger — Keith's domain, not mine

I do not handle keys, money, or logins. Nothing below was attempted.

| # | hand | what is needed | kind | note |
|---|---|---|---|---|
| 8 | Groq | mint `gsk_…` at `console.groq.com/keys` → `live/config/groq_api_key.txt` | **credential** | Free tier: no card. 429 over-limit, never a silent bill. Only Tier-3 row. |
| 9 | Ollama | install the Windows app; pull one small tool model | **install, NOT a credential** | Highest-value blocked row. Keep `OLLAMA_NO_CLOUD=1` until he opts in. |
| 10 | Aider | `aider-install` | **install** | Isolates its own Python. |
| 11 | MCP Fetch | `uv` or `pip install mcp-server-fetch` | **install** | Recommend dropping instead (§3). |
| — | Core `:8770` | run `cosmos serve` | **neither** — an action | **S3.** Gates every rail's reachability. |
| 5, 6 | Codex / Claude rails | **nothing.** Do **not** mint `sk-` or `sk-ant-` for these | ⚠ **anti-credential** | A key in these envs **steals the live prepaid seat** and starts a metered bill (stage-3 H5). The fix is a rail change. |

`live/config/` this pass — **names only, no values read**: `api_token.txt`, `cursor_cosmos_key.txt`,
`cursor_rail.json`, `cursor_rail_probe.json`, `firecrawl_rail.json`, `firecrawl_rail_probe.json`,
`install_key.bin`, `install_record.json`, `node_rails.json`, `playwright_rail.json`,
`playwright_rail_probe.json`. No Groq / OpenAI / Anthropic / Gemini / Firecrawl key present.

---

## 5. UNMEASURED this pass (typed holes, not guesses)

| id | hole | what closes it |
|---|---|---|
| N1 | **browser-use** — not probed at all this pass | `pip show browser-use` + a headless run; stage-3 D4 rank stands untouched |
| N2 | Gemini CLI wallet — carried from stage-3, not re-measured | `gemini` `/stats` in a contained job |
| N3 | GitLab hosted minutes · GitHub Actions minutes | billing DOM (Keith) — stage-3 U5/U6, still open |
| N4 | GitLab project runner | `glab runner list` — stage-3 measured *none*; not re-run here |
| N5 | Whether `browser_navigate` downloads a browser binary on first real use | one navigate through the Playwright rail |

Stage-3's U1–U13 register is **not** restated here; it stands as written.

---

## 6. PROPOSAL for COW — wire the top TWO (#1 GitLab + #2 GitHub)

`cosmos/` is outside this pass's fence. Below is the diff; **COW executes it, or not.**

### 6.1 Why one module for two rails

`glab` and `gh` differ in exactly three values: the binary, the identity verb, and how the identity
is lifted from the reply. Spec load, authority refusal, registration and probe-record write are
identical. Two ~800-line vendor modules would be two places for one guard to drift — precisely the
cost `cosmos_rail_base` was created to stop (its own docstring: four byte-identical copies of
`_ledger_is_authority`). **One table-driven module, two `link_id`s, ~240 lines.** Improvement is not
bloat: this adds two hands and no duplicated guard.

### 6.2 Why these two are the cheapest real hands in the sweep

- Both are **already authenticated**, in the **OS keyring** — so this is the **first COSMOS rail
  holding no COSMOS secret**. There is no `read_key`, therefore the `NO_KEY` refusal that keeps
  `codex-cli` and `claude-cli` dark **cannot occur here**.
- Both probe verbs are **$0** and start no pipeline, so no CI minutes are spent. `metered_usd=0`
  → the Dispatcher never spend-gates them.
- **The probe binds auth, not presence** — GitHub `rate_limit.limit`, GitLab `user.id`, plus
  `rc==0` required. This is the §1 scar encoded: a CLI that printed the sought token while failing
  would otherwise score green.
- S1 means these compose on boot instead of stalling as satellite workers.

### 6.3 Status — this proposal is TESTED, not a sketch

Staged at `builds/probe/proposed/cosmos_forge_rail.py`, with its suite at
`builds/probe/test_forge_rail_proposal.py`. Nothing is registered and nothing is written.

`cosmos_selftest_clock` globs `builds/*/test_*.py`, so that suite is **one of the gated suites**.
It therefore runs **hermetic by default** — throwaway sentinel root in a tempdir, injected
`run`/`which`, no network, no live root — because a suite that reaches the network goes flaky and
reddens the clock for reasons unrelated to the code. The real forge probes are **evidence, not a
gate**, and sit behind `--live --root`.

```
mode: hermetic          # 11/11, no network
unknown link_id ok · empty links ok · overlay not a dict ok · bad link in ForgeRail ok
authority attach ok · default spec on a bare root ok · absent binary ok
rc!=0 with a valid body ok · timeout ok · rc==0 without the bound value ok
happy path passes ok

mode: live              # same 11 checks, plus the real binaries
github-forge  ok=true  binary=C:\Program Files\GitHub CLI\gh.EXE  rest_limit=5000 remaining=5000
gitlab-forge  ok=true  binary=…\glab\glab.EXE  user_id=41407957 username=keithbbf-gif
```

Three checks carry the weight. **`rc!=0 with a valid body`**: a run exiting non-zero while
returning a perfect payload carrying the bound value must not pass — the §1 scar. **`rc==0 without
the bound value`**: a clean exit whose body is `{"message":"401 Unauthorized"}` must not pass —
a reply is not an *authenticated* reply. **`happy path passes`**: without it the other two could be
satisfied by a probe that simply never returns true.

### 6.4 The diff

**(a) NEW FILE — `cosmos/cosmos_forge_rail.py`.** Full content is staged at
`builds/probe/proposed/cosmos_forge_rail.py`; copy it verbatim. It imports only from
`cosmos_rail_base` (`RailError`, `_real_run`, `_real_which`, `ledger_is_authority`,
`write_probe_record`) and `cosmos_paths`. Its `sys.path` line resolves to `cosmos/` once landed.

**(b) ONE-LINE additive edit — `cosmos/cosmos_kernel.py`**, the `compose_rails` table:

```diff
--- a/cosmos/cosmos_kernel.py
+++ b/cosmos/cosmos_kernel.py
@@ -177,6 +177,7 @@
         for name, mod, attr, attach in (
             ("node_rails", "cosmos_node_rails", "register_node_rails", False),
             ("cursor-api", "cosmos_cursor_rail", "attach_to_kernel", True),
             ("codex-cli", "cosmos_codex_rail", "attach_to_kernel", True),
             ("playwright-dom", "cosmos_playwright_rail", "attach_to_kernel", True),
             ("firecrawl-web", "cosmos_firecrawl_rail", "attach_to_kernel", True),
             ("claude-cli", "cosmos_claude_rail", "attach_to_kernel", True),
+            ("forge", "cosmos_forge_rail", "attach_to_kernel", True),
         ):
```

`attach_to_kernel(self, self.adapters, boot_compose=True)` is the call shape `compose_rails` uses
(`:188`); the proposed signature matches it. `compose_rails` is **fail-open per rail**, so if the
module is absent the boot records a warning and continues — the running fleet cannot be taken down
by this entry. That satisfies keep-her-afloat: additive, one writer, no restart-to-install.

**(c) NO spec file needed.** `load_spec` falls back to `default_spec()` when
`live/config/forge_rail.json` is absent, so nothing must be dropped into the runtime root first.

### 6.5 Runtime-binding gate for this slice (`rc=0` is NOT it)

After COW lands it and Keith restarts Core (S3), the value only the live tree can emit:

1. `cosmos_forge_rail --probe` → `gitlab-forge` `user_id=41407957` **and** `github-forge`
   `rest_limit=5000` — both from *this* keyring.
2. `gitlab-forge` and `github-forge` present in the **composed adapter list** of a writing boot
   (the S1 dry-run output shape), which today shows nine adapters and would then show eleven.
3. A `LINK_REGISTERED` pair on the authority ledger, written **only** by Kernel boot.

**Not yet bound, and named so it is not smuggled in:** #1's real prize — CI **artifacts** on a SHA
equal to fenced HEAD (stage-3 M1) — needs the stale-SHA green fixed first. This proposal wires the
**forge hand**; it does not claim the CI gate.

---

## 7. Recommendation in one line

Land §6 (two hands, zero credentials, zero dollars); ask Keith for **one credential** (Groq `gsk_`)
and **one install** (Ollama, the highest-value blocked row); drop MCP Fetch as superseded; and fix
the `codex-cli`/`claude-cli` **wallet mismatch** — two prepaid seats are live on this machine while
their rails sit dark waiting for keys that would cost money and steal the seats.

**Nothing in this file has passed the runtime-binding gate for a wired COSMOS forge hand.** The
probes are satellite evidence; Core `:8770` is down.

---

## Artifacts

| path | what |
|---|---|
| `builds/probe/maker_hands_probe.py` | the harness (27 probes, sentinel-verified root, no hard-coded paths) |
| `builds/probe/maker_hands_evidence.json` | full evidence, this pass |
| `builds/probe/maker_hands_evidence_extra.json` | **SUPERSEDED** intermediate — written before the `rc≠0` guard; its *MCP python SDK* row is the false pass described in §1. Kept, not deleted. |
| `builds/probe/proposed/cosmos_forge_rail.py` | §6 proposal, staged (target `cosmos/cosmos_forge_rail.py`) |
| `builds/probe/test_forge_rail_proposal.py` | the proposal's suite — hermetic by default (a gated `builds/*/test_*.py`), `--live --root` for real-forge evidence |

**Gate, this pass:** `py -3.14 builds/selftest_clock/cosmos_selftest_clock.py --root V:/A/Ai/COSMOS
--once` → `total 87 · passed 87 · flaky 0 · failed 0` (baseline before this pass: 83/83/0/0).
