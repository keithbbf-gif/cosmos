# AIDER HANDS — G46 scout return (Aider AI pair-programmer)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25.
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim. **No COSMOS core code was edited.**
**Assignment:** maker-docs sweep (DHx) — every Aider hand COSMOS could fire.

**Filter:** a surface is a HAND only if COSMOS can **do** something with it (edit, commit, lint, test, scrape, map, dispatch). Chat-only UI chrome is out unless it is a dispatchable CLI flag.

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks (coding-agent lane, fenced commit, spend-gate, vendor-plural). Equal power, cheaper wins. LLM **inference** cost sits on the provider, never on Aider: the tool is Apache-2.0 and BYO key.

**What Aider is (one sentence):** AI pair programming in the terminal — it adds files to a chat, sends a tree-sitter **repo map** plus those files to an LLM, applies SEARCH/REPLACE (or whole-file / udiff) edits to the local git repo, and **auto-commits each change** with a Conventional-Commits message. Official site: [aider.chat](https://aider.chat/). Docs index: [aider.chat/docs](https://aider.chat/docs/).

**Repo in play:** `keithbbf-gif/cosmos`. Aider is a **native worker**, never a second ledger writer. It runs in an attempt-private workspace; fenced commit still owns the live tree.

---

## Licensing / cost floor

| fact | official source | COSMOS implication |
|------|-----------------|--------------------|
| Aider is **open source**, **Apache License 2.0** | [FAQ — Aider AI LLC](https://aider.chat/docs/faq.html#what-is-aider-ai-llc), [LICENSE.txt](https://github.com/Aider-AI/aider/blob/main/LICENSE.txt) | Tool cost = **$0**. Install, copy, run, wrap. |
| Aider AI LLC is the company behind the tool | same FAQ | Attribution only. No seat, no SaaS bill for Aider itself. |
| **BYO API key.** Aider does not sell inference. | [Connecting to LLMs](https://aider.chat/docs/llms.html), [API Keys](https://aider.chat/docs/config/api-keys.html) | Spend-gate the **provider**, not Aider. Point `--model` at whichever rail has headroom that day (`ROUTING.md` / DHx). |
| Local models (Ollama, LM Studio, any OpenAI-compat endpoint) = **$0 inference** | [Ollama](https://aider.chat/docs/llms/ollama.html), [LM Studio](https://aider.chat/docs/llms/lm-studio.html), [OpenAI compatible APIs](https://aider.chat/docs/llms/openai-compat.html) | Highest-ranked rails: nothing that can run out (canon: DOM first / no credit-to-lapse). |
| Documented **free cloud** paths | [LLMs — Free models](https://aider.chat/docs/llms.html#free-models): OpenRouter free models; Gemini 2.5 Pro Exp (`--model gemini-exp`). Groq page still says “currently offers *free* API access” ([GROQ](https://aider.chat/docs/llms/groq.html)). | Use as overflow. Rate-limited; do not treat as a daily driver without a live quota probe. |
| GitHub Copilot path billed through the Copilot subscription | [GitHub Copilot](https://aider.chat/docs/llms/github.html) | Burns Copilot credits, not a new Aider bill. Aider still prints *estimated* costs. |
| Analytics are opt-in / disableable | `--analytics-disable`, [options](https://aider.chat/docs/config/options.html) | Default COSMOS: `--analytics-disable`. |

**Install (Windows, official):** `python -m pip install aider-install` then `aider-install` (isolates aider in its own Python 3.12). One-liner: `powershell -ExecutionPolicy ByPass -c "irm https://aider.chat/install.ps1 | iex"`. Also: `uv tool install --force --python python3.12 --with pip aider-chat@latest`. Package: `aider-chat`. Python 3.8–3.13 for aider-install; pip/pipx 3.9–3.12. Docs warn against distro package managers (wrong deps). Source: [Installation](https://aider.chat/docs/install.html).

---

## Auth (all LLM rows inherit this unless overridden)

Aider never has its own account. It is a **client**. Keys live in env / `.env` / `.aider.conf.yml` / CLI. Keith owns credentials; store under `live/config/` (git-ignored); never in the tree.

| method | how | env / flag | notes |
|--------|-----|------------|-------|
| OpenAI | dedicated | `OPENAI_API_KEY` or `--openai-api-key` or YAML `openai-api-key:` | Also `AIDER_OPENAI_API_KEY`. |
| Anthropic | dedicated | `ANTHROPIC_API_KEY` or `--anthropic-api-key` or YAML `anthropic-api-key:` | Also `AIDER_ANTHROPIC_API_KEY`. |
| Every other provider | generic | `--api-key provider=<key>` sets `PROVIDER_API_KEY`. YAML `api-key: [gemini=…, openrouter=…]`. `.env` `GEMINI_API_KEY=…` etc. | [API Keys](https://aider.chat/docs/config/api-keys.html). |
| OpenAI-compat / Copilot / local | base URL | `OPENAI_API_BASE` + `OPENAI_API_KEY` (dummy ok for some local servers) | Copilot: `https://api.githubcopilot.com` + oauth_token from JetBrains `apps.json`. LM Studio **requires** a dummy `LM_STUDIO_API_KEY` or Bearer is empty and fails. |
| Vertex | GCP ADC | `GOOGLE_APPLICATION_CREDENTIALS` + `VERTEXAI_PROJECT` + `VERTEXAI_LOCATION` | gcloud login / service account. |
| Bedrock | AWS | `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_PROFILE` / `AWS_REGION` | boto3 extra install. |
| Ollama | optional | `OLLAMA_API_BASE=http://127.0.0.1:11434`, optional `OLLAMA_API_KEY` | Default 2k ctx is a silent-truncation footgun; aider raises it per request + 8k reply. Use `ollama_chat/<model>` not `ollama/`. |

LiteLLM is the adapter: `aider --model <litellm-name>` reaches “hundreds of other models.” Provider list: [LiteLLM providers](https://docs.litellm.ai/docs/providers). Discover: `aider --list-models <partial>`.

---

## How COSMOS reaches Aider (one pattern)

Core stays sole ledger writer. Aider is a **native CLI worker** in an attempt-private workspace.

| Lane | Mechanism | When |
|------|-----------|------|
| **A. Headless CLI (preferred)** | `aider --yes-always --message "…" --model <rail> [--no-auto-commits \| review then fence] files…` | Queue job. Matches “no bats — in-app / COSMOS action.” |
| **B. `--message-file` + `--load`** | Prompt from a file; `/commands` replay from a file. | Long prompts, reconstructed sessions, CI. |
| **C. Python `Coder.create().run()`** | In-process. **Not officially supported**; can change without compatibility. | Only if a COSMOS module must stay in-process. Prefer CLI. |
| **D. Docker** | `paulgauthier/aider` / `aider-full`, volume-mount the attempt workspace. | Isolated Python; `/run` then executes *inside* the container (tests may miss host env). |

**Fenced-commit mapping:** Aider’s default is **one git commit per LLM edit**, Conventional Commits, weak-model writes the message, `(aider)` / `Co-authored-by` attribution. That is a revertible series in the **attempt** repo. Core reviews those commits, then the fenced commit gateway publishes — never let Aider write the live tree. `/undo` reverts the last *aider* commit only.

**Default COSMOS flags for unattended jobs:**

```
aider --yes-always --no-stream --no-show-release-notes --analytics-disable
      --message "<task>"
      --model <rail>
      --read CONVENTIONS.md
      [--no-auto-commits]   # if Core, not Aider, will commit
      [--auto-test --test-cmd "pytest -x"]
```

`--yes` (scripting page, env `AIDER_YES`) and `--yes-always` (options reference, env `AIDER_YES_ALWAYS`) both mean “always say yes to every confirmation.” COSMOS should use **`--yes-always`** — that is the current options-reference name.

---

## Ranking table

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it | source |
|---|------|------|----------------------|------|------|-------|------------------------|--------|
| 1 | **`aider` CLI (the worker)** | CLI | One binary that **is** the coding hand: add files, talk to an LLM, apply multi-file edits in the local git repo, auto-commit. Launch: `aider [file…]` or `aider --file f --read r`. Default chat mode = `code`. | BYO provider key (or none for local). | **free** (Apache-2.0). Inference = provider. | **highest** | Native worker in attempt workspace after Keith `aider-install`. Preferred dispatch. Never a `.bat`. | [Usage](https://aider.chat/docs/usage.html), [Install](https://aider.chat/docs/install.html) |
| 2 | **`--message` / `-m` one-shot (scripting)** | CLI + automation | Send **one** NL instruction, apply edits, **exit**. Disables interactive chat. `aider --message "make a script that prints hello" hello.js`. Env `AIDER_MESSAGE`. This is the COSMOS queue verb. | same | **free** tool | **highest** | Queue runner argv. Pair with `--yes-always`. | [Scripting](https://aider.chat/docs/scripting.html), [options `--message`](https://aider.chat/docs/config/options.html) |
| 3 | **`--yes-always` / `--yes` unattended confirm** | CLI + automation | Always yes to every confirmation (add file? apply edit? commit dirty?). Without this, a headless job hangs. | none | **free** | **highest** | Required on every COSMOS aider job. | [Scripting `--yes`](https://aider.chat/docs/scripting.html), [options `--yes-always`](https://aider.chat/docs/config/options.html) |
| 4 | **`--message-file` / `-f`** | CLI + automation | Same as `--message` but prompt is a file (long briefs, generated tasks). Env `AIDER_MESSAGE_FILE`. | same | **free** | **highest** | Drop the queue prompt into the attempt workspace; pass `-f`. | [Scripting](https://aider.chat/docs/scripting.html) |
| 5 | **Ollama local backend** | model + local HTTP | `aider --model ollama_chat/<model>` against `OLLAMA_API_BASE=http://127.0.0.1:11434`. Aider auto-sizes Ollama ctx (request + 8k reply) so Ollama does **not** silently drop context (Ollama default is 2k). Optional `num_ctx` in `.aider.model.settings.yml`. | none (or `OLLAMA_API_KEY` if the server requires it) | **free** ($0 inference, electricity) | **highest** | Point at the Ollama rail already on the mesh-additions backlog. Immune to quota/billing/consent-to-lapse. | [Ollama](https://aider.chat/docs/llms/ollama.html) |
| 6 | **LM Studio local backend** | model + local HTTP | `aider --model lm_studio/<name>` at `LM_STUDIO_API_BASE=http://localhost:1234/v1`. Dummy `LM_STUDIO_API_KEY` **required** (empty Bearer fails). | dummy key | **free** | **highest** | Same as Ollama: local coding lane. | [LM Studio](https://aider.chat/docs/llms/lm-studio.html) |
| 7 | **OpenAI-compatible endpoint (any local/proxy)** | model + HTTP | `OPENAI_API_BASE=<url>` + `OPENAI_API_KEY=<key>` then `aider --model openai/<name>`. This is how Aider talks to a LiteLLM sidecar, vLLM, llama.cpp server, or COSMOS’s existing OpenAI-shaped rails. | key as the endpoint requires | **free** adapter; inference = backend | **highest** | Preferred *shape*: one local LiteLLM/compat URL so Aider does not learn every vendor SDK. Spend-gate still sits in front of the real provider. | [OpenAI compatible APIs](https://aider.chat/docs/llms/openai-compat.html) |
| 8 | **Repository map** | context builder | Tree-sitter map of the git repo: files + key classes/functions/signatures. Graph-ranked to the `--map-tokens` budget (default **1024**). Sent with every request so the LLM can use APIs it has not been `/add`ed. Weak models may launch with map **disabled** (`Repo-map: disabled`) — force with `--map-tokens 1024`. `/map` prints it; `--show-repo-map` prints and **exits**. | none (local analysis) | **free** | **highest** | Always on for capable models. For COSMOS’s large tree: `--subtree-only` from `cosmos/` or a `.aiderignore`. Do **not** `/add` the whole repo. | [Repository map](https://aider.chat/docs/repomap.html), [FAQ](https://aider.chat/docs/faq.html#how-do-i-turn-on-the-repository-map), [blog](https://aider.chat/2023/10/22/repomap.html) |
| 9 | **Git auto-commit of every LLM edit** | git | Default **on**. Each aider edit is its own commit with a weak-model Conventional-Commits message. Dirty files are committed first (`dirty-commits`, default on) so human work is never mixed with AI work. `/undo` drops the last *aider* commit. Attribution: `(aider)` on author/committer and/or `Co-authored-by` trailer (default). Pre-commit hooks **skipped** (`git commit --no-verify`) unless `--git-commit-verify`. | local git identity | **free** | **highest** | Maps onto fenced commit: review the aider series in the attempt repo, then gateway. COSMOS may prefer `--no-auto-commits` and let Core commit — both are valid; the default is the more revertible. | [Git integration](https://aider.chat/docs/git.html) |
| 10 | **`--auto-test` + `--test-cmd` + `/test`** | CLI + quality gate | After each edit (or via `/test cmd`), run a test command. Non-zero exit → output is fed back and aider **tries to fix**. `--test` = run tests, fix, **exit**. Compiled languages: `--test-cmd "dotnet build && dotnet test"`. | none | **free** (burns LLM tokens on retries) | **highest** | COSMOS runtime-binding cousin: the test command **is** the gate that executes. Pair with `--yes-always` for unattended self-heal. | [Linting and testing](https://aider.chat/docs/usage/lint-test.html) |
| 11 | **`--auto-lint` + `--lint-cmd` + `/lint`** | CLI + quality gate | Built-in tree-sitter linters for most languages (default **on** after every edit). Custom: `--lint-cmd "python: ruff check --fix"`. `/lint` lints in-chat files (or all dirty). `--lint` = lint+fix then exit. | none | **free** | **high** | Catch syntax/format breakage before fenced publish. Formatter-as-linter must wrap so a reformat does not look like a lint failure (docs give a double-run script). | [Linting and testing](https://aider.chat/docs/usage/lint-test.html), [languages](https://aider.chat/docs/languages.html) |
| 12 | **Chat mode `ask` (`/ask`, `--chat-mode ask`)** | chat mode | Discuss / review code, **never edit**. Sticky via `/chat-mode ask` or one-shot `/ask …`. | same | **free** tool | **high** | Read-only review jobs (`--message` + `--chat-mode ask`) without dirtying the attempt tree. | [Chat modes](https://aider.chat/docs/usage/modes.html) |
| 13 | **Chat mode `code` (`/code`, default)** | chat mode | Make file edits. `/ok` = `/code Ok, please go ahead and make those changes.` Ask→code workflow: plan in ask, then “go ahead” in code. | same | **free** tool | **high** | Default for implement jobs. | [Chat modes](https://aider.chat/docs/usage/modes.html) |
| 14 | **Chat mode `architect` (`--architect`, `/architect`)** | chat mode + two-model | Main model **plans**; `--editor-model` **emits** SEARCH/REPLACE. Two LLM calls (slower, costlier, often better for reasoning models). `--auto-accept-architect` default **True**. Editor formats: `editor-diff` / `editor-whole`. | two models’ keys | **2× inference** | **high** | Use when the architect is a strong reasoner (o1/Grok) and the editor is a cheap local or flash model. | [Chat modes](https://aider.chat/docs/usage/modes.html), [edit formats](https://aider.chat/docs/more/edit-formats.html) |
| 15 | **`.aider.conf.yml` (YAML config)** | config | Most options as YAML. Search order: **home → git root → cwd** (later wins). `--config FILE` loads **only** that file. Lists: bullets or `[a, b]`. Sample lists *every* key. | may contain keys — **do not commit secrets** | **free** | **high** | COSMOS: a **job-local** conf in the attempt workspace (`--config`), not a committed repo conf with keys. Read-only `CONVENTIONS.md` via `read:`. | [YAML config](https://aider.chat/docs/config/aider_conf.html), [sample on GitHub](https://github.com/Aider-AI/aider/blob/main/aider/website/assets/sample.aider.conf.yml) |
| 16 | **`.env` / `--env-file`** | config + secrets | Keys + `AIDER_*` options. Search: home → git root → cwd → `--env-file`. Later wins. | **the secret store** | **free** | **high** | Point `--env-file` at `live/config/` (git-ignored). Never a `.env` in the tracked tree. | [Config with .env](https://aider.chat/docs/config/dotenv.html) |
| 17 | **`--load` + `/load` + `/save`** | session reconstruct | `/save file` writes commands that reconstruct the current chat’s files. `--load` / `/load` replays them. Deterministic session bootstrap. | none | **free** | **high** | Pre-load `/read` + `/add` for a known job shape. | [commands](https://aider.chat/docs/usage/commands.html), [options `--load`](https://aider.chat/docs/config/options.html) |
| 18 | **`--read` / `/read-only` (read-only context)** | context | Files the model can see but **not** edit. Best for `CONVENTIONS.md`, architecture docs, foreign-repo maps. Cached when `--cache-prompts`. | none | **free** (tokens) | **high** | Always `--read` COSMOS conventions / `docs/FINAL_ARCHITECTURE.md` as read-only. Never put the live ledger in chat. | [conventions](https://aider.chat/docs/usage/conventions.html), [usage](https://aider.chat/docs/usage.html) |
| 19 | **`.aiderignore` + `--subtree-only`** | scope | `.aiderignore` = gitignore syntax; default file `.aiderignore` in git root. `--subtree-only` ignores the repo outside cwd. FAQ gives a “ignore everything except foo/bar/baz” recipe for monorepos. `--aiderignore FILE` for frontend vs backend profiles. | none | **free** | **high** | COSMOS tree is large. Default job: cwd `cosmos/` + `--subtree-only`, or an ignore that drops `live/`, `_delme/`, `docs/research/` noise. | [FAQ large repo](https://aider.chat/docs/faq.html#can-i-use-aider-in-a-large-mono-repo) |
| 20 | **`/run` (alias `!`) + `/test`** | shell-in-chat | Run a host command; optionally add stdout/stderr to the chat. `/test` adds output **only on non-zero**. This is how aider sees a traceback. `/git` runs git **without** putting output in chat (so `/git diff` will **not** feed the model — use `/run git diff`). | same user as the worker | **free** (then tokens if added) | **high** | COSMOS Job-Object contains the process; still allowlist the command. Do not `/run` anything that could touch the live root. | [commands](https://aider.chat/docs/usage/commands.html), [FAQ git history](https://aider.chat/docs/faq.html#how-do-i-include-the-git-history-in-the-context) |
| 21 | **`/add` `/drop` `/ls` `/reset` `/clear` `/tokens`** | chat file-set | `/add` files (or a dir, recursive) to the editable set. `/drop` removes. `/ls` lists known vs in-chat. `/reset` drops files **and** history. `/clear` history only. `/tokens` reports context use. Docs: add **only** files that will change; repo-map covers the rest. Extra files confuse the model **and** cost tokens. | none | **free** (tokens) | **high** | COSMOS prompt should name the files on the CLI (`aider f1 f2`) rather than “add everything.” | [Usage — adding files](https://aider.chat/docs/usage.html), [FAQ all-files](https://aider.chat/docs/faq.html#how-can-i-add-all-the-files-to-the-chat), [commands](https://aider.chat/docs/usage/commands.html) |
| 22 | **`/undo` `/commit` `/diff` `/git`** | git in-chat | `/undo` = reset last **aider** commit. `/commit [msg]` commits dirty (non-aider) edits. `/diff` since last user message. `/git …` raw git, output **not** in chat. `--commit` CLI: commit pending with a generated message, **then exit**. | git | **free** | **high** | `/undo` is the cheap reject path before the fence. `--commit` is a one-shot “write the message and leave.” | [Git](https://aider.chat/docs/git.html) |
| 23 | **`--dry-run`** | safety | Perform the LLM turn **without modifying files**. | same | **free** (still pays inference) | **high** | Rehearse a prompt against the attempt tree. | [Scripting](https://aider.chat/docs/scripting.html) |
| 24 | **`--no-auto-commits` / `--no-dirty-commits` / `--no-git`** | git policy | Stop per-edit commits; stop dirty pre-commits; or disable git entirely (docs: **not recommended**, keep backups). | none | **free** | **high** | If Core is the only committer, `--no-auto-commits`. Do **not** `--no-git` on a COSMOS job — undo/review dies. | [Git — disabling](https://aider.chat/docs/git.html#disabling-git-integration) |
| 25 | **Edit formats (`--edit-format`)** | LLM protocol | `whole` (full file, simple/slow/costly), `diff` (SEARCH/REPLACE, default for many), `diff-fenced` (Gemini), `udiff` (GPT-4 Turbo lazy-code fix), `editor-diff` / `editor-whole` (architect editor). Wrong format = “model returned code but aider didn’t edit.” Weaker than GPT-3.5 often fail. | none | **free** (token efficiency varies) | **high** | Leave default unless a model warning says otherwise. Gemini jobs: expect `diff-fenced`. | [Edit formats](https://aider.chat/docs/more/edit-formats.html), [LLMs](https://aider.chat/docs/llms.html) |
| 26 | **`--model` / `/model` / `--list-models` / `/models`** | model switch | Set/search the main model. `/model` mid-chat. `/weak-model`, `/editor-model` for the other two slots. `--alias alias:model`. | provider key for the target | inference | **high** | COSMOS dispatcher picks `--model` from the rail with headroom. | [options](https://aider.chat/docs/config/options.html), [other LLMs](https://aider.chat/docs/llms/other.html) |
| 27 | **LiteLLM (built-in adapter)** | adapter | Aider uses LiteLLM to reach “hundreds” of providers. Any LiteLLM model name works: `aider --model <name>`. Env vars for keys: see the long list on the Other-LLMs page (OPENAI, ANTHROPIC, GEMINI, GROQ, XAI, DEEPSEEK, OPENROUTER, OLLAMA, MISTRAL, COHERE, …). | per-provider | **free** adapter | **high** | Do **not** invent a second spend ledger. LiteLLM is the *shape*; Core’s spend-gate remains authority. Optional localhost LiteLLM proxy so Aider always sees `openai/`. | [Other LLMs](https://aider.chat/docs/llms/other.html), [LiteLLM providers](https://docs.litellm.ai/docs/providers) |
| 28 | **Gemini backend (`--model gemini` / `gemini-exp`)** | model | `--model gemini` → Gemini 2.5 Pro. `--model gemini-exp` → Gemini 2.5 Pro Exp, documented **free with usage limits**. `GEMINI_API_KEY`. `aider --list-models gemini/`. | `GEMINI_API_KEY` | **free-tier** (`gemini-exp`); paid Pro otherwise. COSMOS also has `gem-api` / Vertex $300 credit (DHx / MESH_ADDITIONS). | **high** | Prefer existing `gem-api` spend-gate. `gemini-exp` is the documented $0 overflow. | [Gemini](https://aider.chat/docs/llms/gemini.html) |
| 29 | **Groq backend** | model | `aider --model groq/llama3-70b-8192`. Docs: Groq “currently offers *free* API access”; Llama 3 70B ≈ GPT-3.5 edit skill. `GROQ_API_KEY`. `aider --list-models groq/`. | `GROQ_API_KEY` | **free** per aider docs (live Groq console is a free tier + paid — **probe before treating as unlimited**) | **high** | Fast bulk edits. Bind remaining quota to the Groq console before a 24h pour. | [GROQ](https://aider.chat/docs/llms/groq.html) |
| 30 | **OpenRouter (incl. free models)** | model + router | `aider --model openrouter/<provider>/<model>`. `OPENROUTER_API_KEY`. Free-model catalog exists ([aider free-models note](https://aider.chat/docs/llms.html#free-models)). Privacy toggle: “enable providers that may train on inputs” or some models 403. Provider routing via `.aider.model.settings.yml` (`order`, `allow_fallbacks`, `data_collection: deny`). | `OPENROUTER_API_KEY` | **free models** rate-limited; paid otherwise | **high** (overflow) | MESH_ADDITIONS already flags `openrouter/free` rotation as a silent-fallback hazard. Pin a **named** free model, do not use a rotating “free” router as a gate. | [OpenRouter](https://aider.chat/docs/llms/openrouter.html) |
| 31 | **xAI / Grok backend** | model | `aider --model xai/grok-3-beta` (also `grok-3-fast-beta`, `grok-3-mini-beta`, `grok-3-mini-fast-beta`). Mini models take `--reasoning-effort`. `XAI_API_KEY`. `aider --list-models xai/`. | `XAI_API_KEY` | **paid** (COSMOS `sgh-api` / `gw-api` already budgeted) | **high** | Point Aider at the existing xAI rail rather than a second key. Vendor-plural: Aider+Grok is a second *coding agent* on the same model family as Grok-Build. | [xAI](https://aider.chat/docs/llms/xai.html) |
| 32 | **Anthropic / Claude backend** | model | Default when Anthropic key present. `--model sonnet` (deprecated switch still works). Thinking tokens via `.aider.model.settings.yml` `thinking.budget_tokens`. Prompt caching supported. Anthropic **direct** rate limits are low; docs recommend OpenRouter or Vertex for volume. | `ANTHROPIC_API_KEY` | **metered** (Claude Code weekly quota is a *different* pipe — F5) | **high** | Use as a Dispatcher rail so Claude Code weekly allotment is not the only Claude path (MESH_ADDITIONS row 17). Cache prompts (`--cache-prompts`) on Sonnet/Haiku. | [Anthropic](https://aider.chat/docs/llms/anthropic.html), [caching](https://aider.chat/docs/usage/caching.html) |
| 33 | **OpenAI backend** | model | `--model o3-mini` / `gpt-4o` / `o1-mini` / etc. `OPENAI_API_KEY`. Reasoning: `--reasoning-effort`. | `OPENAI_API_KEY` | **metered** (`oa-api` already a rail) | **high** | Same key as `oa-api`; spend-gate once. | [OpenAI](https://aider.chat/docs/llms/openai.html) |
| 34 | **DeepSeek backend** | model | `--model deepseek/deepseek-chat` (Chat V3: top aider-edit score per their page). `DEEPSEEK_API_KEY`. Caching by default on several DeepSeek settings. | `DEEPSEEK_API_KEY` | cheap metered (MESH_ADDITIONS: trial grant then low $/M) | **high** | Overflow coding rail; also distill-to-Ollama. | [DeepSeek](https://aider.chat/docs/llms/deepseek.html) |
| 35 | **GitHub Copilot OpenAI-style endpoint** | model | `OPENAI_API_BASE=https://api.githubcopilot.com` + oauth_token from JetBrains `~\AppData\Local\github-copilot\apps.json`. `aider --model openai/gpt-4o`. Docs: third-party agents hitting this API are allowed; billed through Copilot subscription; aider still prints estimates. List models: curl `/models` with `Copilot-Integration-Id: vscode-chat`. | Copilot oauth_token | **included** in Copilot plan / credits | **high** | Another way to spend Copilot credits as a **file-editing** agent (distinct from Copilot CLI / cloud agent). Do not double-dispatch with Cursor/Copilot-cloud on the same issue without a lease. | [GitHub Copilot](https://aider.chat/docs/llms/github.html) |
| 36 | **`--cache-prompts` + keepalive** | cost control | Cache system prompt, `/read` files, repo map, editable files. Anthropic Sonnet/Haiku + DeepSeek Chat. `--no-stream` required to see cache stats/costs. `--cache-keepalive-pings N` pings every 5 min (Anthropic cache TTL 5 min). | provider that supports cache | **saves** provider $ | **high** | Turn on for any long Sonnet/DeepSeek session. | [Prompt caching](https://aider.chat/docs/usage/caching.html) |
| 37 | **CONVENTIONS.md (`--read`)** | policy injection | Markdown coding rules loaded read-only. Community set: [Aider-AI/conventions](https://github.com/Aider-AI/conventions). YAML `read: CONVENTIONS.md`. This is the supported way to add standing instructions; system-prompt swap is coder-module surgery, not a supported flag. | none | **free** | **high** | One COSMOS conventions file: fail-closed, no fabricated compliance, no live-tree writes, Python 3.14, no bats. | [Conventions](https://aider.chat/docs/usage/conventions.html), [FAQ system prompts](https://aider.chat/docs/faq.html#can-i-change-the-system-prompts-that-aider-uses) |
| 38 | **`--watch-files` / AI comments** | IDE hook | Watch the repo for one-liner comments `# … AI!` / `AI?` / `//` / `--`. `AI!` triggers code edits; `AI?` triggers ask. Comment is removed after. Adds the file to chat. | same | **free** tool | **med-high** | Human-in-the-loop on Keith’s editor, not a queue verb. Useful if a DOM/IDE worker plants `AI!` comments. | [Aider in your IDE](https://aider.chat/docs/usage/watch.html) |
| 39 | **`/web` + URL scrape (Playwright)** | web ingest | `/web <url>` scrapes → markdown → chat. Also paste a URL and confirm. CLI: `python -m aider.scrape URL`. `--disable-playwright` to never install/prompt. `--detect-urls` default on. | none (Playwright may install) | **free** (then tokens) | **med-high** | Pull vendor docs into an aider job. Prefer COSMOS’s own fetch/Firecrawl when the scrape must be ledgered. | [Images & web pages](https://aider.chat/docs/usage/images-urls.html) |
| 40 | **Images (`/add` image, `/paste`)** | vision | Add screenshots/mockups for vision models (GPT-4o, Claude 3.7, …). `/paste` from clipboard. | vision-capable model | inference | **med** | UI-from-screenshot jobs. | [Images & web pages](https://aider.chat/docs/usage/images-urls.html) |
| 41 | **`--browser` / `--gui`** | GUI | Experimental browser UI over the same git editor. | same | **free** | **med** | Keith-facing; not a headless COSMOS job. | [Browser](https://aider.chat/docs/usage/browser.html) |
| 42 | **Copy/paste web-chat mode (`--copy-paste`, `/copy-context`, `/paste`)** | DOM-adjacent | Aider = file editor; a **web** LLM (no API) is the architect. `/copy-context` copies repo map + files; human pastes into the web UI; `/paste` applies the reply. `--copy-paste` automates aider-side copy/load only (web paste stays manual — TOS). | web-session (human) | **free** tool; web LLM = that product’s ToS/quota | **med-high as fallback** | Canon: **DOM first when the API can run out**. This is the documented Aider path for “API unavailable / workplace web-only / no API.” | [Copy/paste with web chat](https://aider.chat/docs/usage/copypaste.html) |
| 43 | **`/voice`** | input | Record → transcribe → treat as a chat message. Needs optional voice install + (webm/mp3) ffmpeg. `--voice-format` / `--voice-language` / `--voice-input-device`. | mic | **free** tool (STT may use a provider) | **low-med** | Keith voice; not a queue hand. Docker: needs host audio. | [Voice](https://aider.chat/docs/usage/voice.html) |
| 44 | **`--commit` (message-only, then exit)** | git + automation | Commit all pending changes with a weak-model message, exit. No coding turn. | git | **free** + cheap weak-model tokens | **med-high** | “Write the commit message for this dirty tree” as a one-shot. | [options `--commit`](https://aider.chat/docs/config/options.html), [Git](https://aider.chat/docs/git.html) |
| 45 | **`--weak-model` / `--commit-prompt` / `--commit-language`** | git messages | Weak model writes commit messages + history summarization. Custom prompt. Conventional Commits by default. | weak-model key | cheap tokens | **med** | Point weak-model at a local/flash model so commits don’t burn Sonnet. | [Git — commit messages](https://aider.chat/docs/git.html#commit-messages) |
| 46 | **`.aider.model.settings.yml` + `.aider.model.metadata.json`** | model tuning | Override edit format, extra_params (headers, `num_ctx`, thinking budget, OpenRouter provider routing), weak/editor models. Metadata: context window + $/token (reporting only — aider never *enforces* limits). Special name `aider/extra_params` applies to all models. | none | **free** | **med-high** | Per-job settings file for Ollama `num_ctx`, Anthropic thinking, OpenRouter `data_collection: deny`. | [Advanced model settings](https://aider.chat/docs/config/adv-model-settings.html) |
| 47 | **`--map-tokens` / `--map-refresh` / `/map-refresh`** | repo-map control | Token budget (0 = disable). Refresh: `auto` (default) / `always` / `files` / `manual`. `--map-multiplier-no-files` (default 2) expands the map when no files are in chat. | none | **free** (tokens) | **med-high** | Large COSMOS jobs: start 1024–4096; 0 only for tiny local models that try to *edit* the map. | [options repomap](https://aider.chat/docs/config/options.html), [repomap](https://aider.chat/docs/repomap.html) |
| 48 | **`--file` / `--read` (CLI add)** | context | Repeatable. Equivalent to `/add` and `/read-only` at launch. | none | **free** | **high** | Preferred over in-chat `/add` for headless jobs. | [options](https://aider.chat/docs/config/options.html) |
| 49 | **`--apply` / `--apply-clipboard-edits`** | debug / apply | Apply edits from a file (or clipboard) in the main model’s editor format, no chat. | none | **free** | **med** | Replay a saved SEARCH/REPLACE without another LLM call. | [options Modes](https://aider.chat/docs/config/options.html) |
| 50 | **`--exit` / `--show-repo-map` / `--show-prompts`** | debug | Startup then exit; print map; print system prompts. | none | **free** | **med** | Probe: `aider --show-repo-map` from `cosmos/` as evidence the map sees the right subtree. | [options](https://aider.chat/docs/config/options.html) |
| 51 | **`--reasoning-effort` / `--thinking-tokens` / `/reasoning-effort` / `/think-tokens`** | reasoning | Provider reasoning knobs (`low/medium/high` or a number; thinking budget e.g. `8k`, `0` to disable). | model that accepts them | extra tokens | **med-high** | Grok mini / o-series / Gemini thinking. `--check-model-accepts-settings` warns if the model ignores them. | [options](https://aider.chat/docs/config/options.html), [reasoning](https://aider.chat/docs/config/reasoning.html) |
| 52 | **History files** | logs | `.aider.input.history`, `.aider.chat.history.md`, optional `--llm-history-file`, `--restore-chat-history`. Share pretty logs via gist + `https://aider.chat/share/?mdurl=`. | none | **free** | **med** | Attempt-workspace only; gitignore (Aider offers to add `.aider*` to `.gitignore` — default **on**). Do not commit chat history (prompts + code). | [FAQ share](https://aider.chat/docs/faq.html#can-i-share-my-aider-chat-transcript), [YAML History Files](https://aider.chat/docs/config/aider_conf.html) |
| 53 | **Docker images** | packaging | `paulgauthier/aider` (core) and `paulgauthier/aider-full` (help, GUI, Playwright). Mount repo at `/app`. Set git `user.name`/`email` **in the repo** (container has no global git config). `/run` executes *inside* the container. | keys via flags/env | **free** images | **med** | Isolation when host Python is hostile. Prefer native `aider-install` on this Windows box. | [Docker](https://aider.chat/docs/install/docker.html) |
| 54 | **Python `Coder` API** | in-process | `from aider.coders import Coder; Coder.create(main_model=Model("…"), fnames=…).run("…")`. `InputOutput(yes=True)` ≈ `--yes`. `/` commands work via `run("/tokens")`. **Not officially supported; may break.** | same | **free** | **med** | Avoid. CLI is the supported automation surface. | [Scripting — Python](https://aider.chat/docs/scripting.html) |
| 55 | **Azure OpenAI** | model | `AZURE_API_KEY` + `AZURE_API_VERSION` + `AZURE_API_BASE`; `--model azure/<deployment>`. Also `AZURE_OPENAI_API_*`. | Azure key | **metered** | **med** | Only if Keith already has Azure OpenAI. | [Azure](https://aider.chat/docs/llms/azure.html) |
| 56 | **Vertex AI** | model | gcloud ADC + `VERTEXAI_PROJECT` + `VERTEXAI_LOCATION`; `--model vertex_ai/claude-3-5-sonnet@…`. Claude-on-Vertex is **region-locked**. | GCP ADC | **metered** / COSMOS Vertex credit | **high** if the $300 credit is live | Route Claude-volume here instead of Anthropic-direct rate limits. Confirm the credit expiry (MESH_ADDITIONS: 2026-10-13). | [Vertex AI](https://aider.chat/docs/llms/vertex.html) |
| 57 | **Amazon Bedrock** | model | AWS creds; `--model bedrock/<modelId or inference-profile>`. Some Claude IDs **require** the `us.` / inference-profile form. May need `pip install boto3` into aider’s env. | AWS | **metered** | **med** | Only if Keith already has Bedrock model access enabled. | [Bedrock](https://aider.chat/docs/llms/bedrock.html) |
| 58 | **`--attribute-*` commit attribution** | git policy | `--attribute-author` / `--attribute-committer` append `(aider)`. `--attribute-co-authored-by` (default True) uses a trailer and **disables** the `(aider)` name suffix unless those flags are explicit True. `--attribute-commit-message-author` prefixes `aider: `. | git | **free** | **med** | Keep default Co-authored-by so `git blame` stats stay honest (Aider’s own “wrote xx%” stats use this). | [Git — attribution](https://aider.chat/docs/git.html#commit-attribution) |
| 59 | **Chat mode `help` (`/help`)** | support | Questions about **aider** (usage, config, models), not about the repo. | same | **free** (tokens) | **low-med** | Operator help, not a COSMOS job. | [Chat modes](https://aider.chat/docs/usage/modes.html) |
| 60 | **Chat mode `context` (`/context`)** | chat mode | “Enter context mode to see surrounding code context.” | same | **free** | **low-med** | Occasional; not a dispatch verb. | [commands](https://aider.chat/docs/usage/commands.html) |
| 61 | **`--suggest-shell-commands`** | safety | Default **True**: model may propose `/run`s. Disable for locked-down jobs. | none | **free** | **med** | COSMOS default: `--no-suggest-shell-commands` unless the job is a test/fix loop. | [options](https://aider.chat/docs/config/options.html) |
| 62 | **`--analytics-disable`** | privacy | Permanently disable analytics (otherwise “random” / opt-in per session). | none | **free** | **infra** | Always on COSMOS jobs. | [options Analytics](https://aider.chat/docs/config/options.html) |
| 63 | **`--upgrade` / `--install-main-branch` / `--just-check-update`** | packaging | PyPI upgrade; install `main`; check and return status in exit code. `--check-update` default True on launch. | none | **free** | **low** | Keith upgrades; COSMOS jobs should `--no-check-update --no-show-release-notes`. | [options Upgrading](https://aider.chat/docs/config/options.html) |
| 64 | **`--shell-completions`** | UX | Print bash/tcsh/zsh completion script and exit. | none | **free** | **low** | Not a COSMOS job. | [options](https://aider.chat/docs/config/options.html) |
| 65 | **Text/config-file editing** | capability | Not just code: `.bashrc`, Dockerfile, `.gitconfig`, README, XML, editor configs. Same edit pipeline. | same | **free** tool | **med** | Docs, YAML, CI files in the attempt workspace. | [Editing config & text files](https://aider.chat/docs/usage/not-code.html) |
| 66 | **Languages / tree-sitter pack** | capability | Repo-map + linter for a long list (Python, JS/TS, Go, Rust, Java, C/C++, C#, Ruby, PHP, Kotlin, Swift, …). Works without map/lint on other languages; quality depends on the LLM. | none | **free** | **med** | COSMOS is Python-first; map is on for `.py`. | [Supported languages](https://aider.chat/docs/languages.html) |
| 67 | **Leaderboards (model pick)** | evidence | Quantitative code-edit and refactor scores. Use to pick `--model` when quota is equal. | none | **free** | **med** | Consult before pinning a new cheap model as a daily driver. | [Leaderboards](https://aider.chat/docs/leaderboards/) |
| 68 | **`--no-stream`** | CI hygiene | Streaming default on; cache stats need it off; CI logs are cleaner off. | none | **free** | **infra** | Default for COSMOS jobs. | [Scripting](https://aider.chat/docs/scripting.html), [caching](https://aider.chat/docs/usage/caching.html) |

---

## Slash-command catalog (every in-chat `/` hand)

Source: [In-chat commands](https://aider.chat/docs/usage/commands.html). Headless jobs reach these via `--load` or the Python `coder.run("/…")` (unsupported) path; interactive/watch jobs type them.

| command | does |
|---------|------|
| `/add` | Add files (or a directory, recursive) to the editable chat set. |
| `/architect` | One-shot architect turn, or sticky-switch with no args. |
| `/ask` | Question, no edits; or sticky-switch. |
| `/chat-mode` | Sticky switch: `code` / `architect` / `ask` / `help`. |
| `/clear` | Drop chat history, keep files. |
| `/code` | Request edits; or sticky-switch. |
| `/commit` | Commit dirty (non-chat) edits; optional message. |
| `/context` | Switch to context mode. |
| `/copy` | Copy last assistant message to clipboard. |
| `/copy-context` | Copy files + repo map + instructions for a web-LLM paste. |
| `/diff` | Diff since last user message. |
| `/drop` | Remove files from chat (free context). |
| `/edit` `/editor` | Open `$EDITOR` / `--editor` for the next prompt. |
| `/editor-model` | Switch editor model. |
| `/exit` `/quit` | Leave. |
| `/git` | Raw git; output **not** added to chat. |
| `/help` | Ask about aider itself. |
| `/lint` | Lint+fix in-chat files, or all dirty if none. |
| `/load` | Execute commands from a file. |
| `/ls` | Known files vs in-chat. |
| `/map` | Print current repo map. |
| `/map-refresh` | Force rebuild. |
| `/model` | Switch main model. |
| `/models` | Search model list. |
| `/multiline-mode` | Swap Enter / Meta-Enter. |
| `/ok` | `/code Ok, please go ahead and make those changes.` (+ extra args). |
| `/paste` | Clipboard image/text into chat (also the web-LLM apply path). |
| `/read-only` | Add as reference, or flip already-added files to read-only. |
| `/reasoning-effort` | `low/medium/high` or a number. |
| `/report` | Open a GitHub issue on Aider. |
| `/reset` | Drop files **and** history. |
| `/run` (`!`) | Shell command; optionally add output to chat. |
| `/save` | Write a reconstruct-the-files command script. |
| `/settings` | Print current settings. |
| `/test` | Run command; add output on **failure**. |
| `/think-tokens` | Budget (`8k`, `0` to disable). |
| `/tokens` | Token report for current context. |
| `/undo` | Reset last **aider** git commit. |
| `/voice` | Record + transcribe. |
| `/weak-model` | Switch commit/summary model. |
| `/web` | Scrape URL → markdown → chat. |

---

## CLI flag clusters COSMOS actually fires

Full list: [Options reference](https://aider.chat/docs/config/options.html) (`aider --help`). Env form is `AIDER_SNAKE_UPPER` of the flag (`--yes-always` → `AIDER_YES_ALWAYS`; `--map-tokens` → `AIDER_MAP_TOKENS`). Four equivalent setters: flag, YAML, env, `.env`.

| cluster | flags | COSMOS default |
|---------|-------|----------------|
| **Dispatch** | `--message`/`-m`, `--message-file`/`-f`, `--yes-always`, `--load`, `--exit` | `--yes-always --message` |
| **Model** | `--model`, `--weak-model`, `--editor-model`, `--architect`, `--auto-accept-architect`, `--edit-format`, `--editor-edit-format`, `--list-models`, `--alias`, `--reasoning-effort`, `--thinking-tokens` | `--model` from Dispatcher |
| **Keys** | `--openai-api-key`, `--anthropic-api-key`, `--api-key provider=`, `--openai-api-base`, `--set-env`, `--env-file` | `--env-file live/config/…` |
| **Git** | `--auto-commits`, `--dirty-commits`, `--commit`, `--commit-prompt`, `--git-commit-verify`, `--attribute-*`, `--no-git` | auto-commits on **or** `--no-auto-commits` if Core commits |
| **Map** | `--map-tokens`, `--map-refresh`, `--map-multiplier-no-files`, `--show-repo-map`, `--subtree-only`, `--aiderignore` | `--subtree-only` or `.aiderignore` |
| **Quality** | `--auto-lint`, `--lint-cmd`, `--lint`, `--auto-test`, `--test-cmd`, `--test` | `--auto-lint`; `--auto-test` when a test cmd exists |
| **Safety** | `--dry-run`, `--no-suggest-shell-commands`, `--analytics-disable`, `--disable-playwright` | analytics off; suggest-shell off unless needed |
| **CI hygiene** | `--no-stream`, `--no-pretty`, `--no-show-release-notes`, `--no-check-update`, `--verbose` | `--no-stream --no-show-release-notes` |
| **Context** | `--file`, `--read`, `--restore-chat-history` | `--read CONVENTIONS.md` |

Deprecated convenience switches still present: `--sonnet`, `--opus`, `--haiku`, `--4o`, `--mini`, `--deepseek`, `--o1-mini`, `--o1-preview`. Prefer `--model`.

---

## COSMOS binding notes (hazards, not theory)

1. **Aider is not Core.** It writes the attempt workspace and its own git commits. The fenced commit gateway is still the only publish path into the live tree / ledger.
2. **Do not `/add` the whole COSMOS repo.** Repo-map exists specifically so you don’t. Extra files degrade edits and burn tokens ([FAQ](https://aider.chat/docs/faq.html#how-can-i-add-all-the-files-to-the-chat)).
3. **Ollama 2k default is a silent-truncation scar.** Always `ollama_chat/` + aider’s auto ctx (or set `num_ctx`). [Ollama](https://aider.chat/docs/llms/ollama.html).
4. **Weaker models will “return code” and not edit.** That is a model-capability failure, not a COSMOS runner bug. Check the [leaderboard](https://aider.chat/docs/leaderboards/) before pinning a local 7B as the daily driver.
5. **`--git-commit-verify` is off.** Aider skips hooks. COSMOS’s Motif/GitLab gate still has to run **after** the fence, not inside Aider’s commit.
6. **Python API is unofficial.** CLI `--message` is the supported automation surface.
7. **Keys never in git.** `.aider.conf.yml` *can* hold `openai-api-key`; do not put that file in the tracked tree. `--env-file` → `live/config/`.
8. **Vendor-plural:** Aider is a fourth coding-agent **lane** (with Claude Code/F5, Grok-Build, Copilot CLI / Cursor). The value is that it can point at **whichever model rail has quota** that day — including $0 Ollama. That is the MESH_ADDITIONS claim this file now binds to official docs.
9. **Lease:** do not double-dispatch Aider + Cursor Cloud Agent + Copilot cloud agent on the same files without a lease.
10. **Windows:** official install is `aider-install` or `install.ps1`. `setx` for env requires a **new** shell. No bats — COSMOS invokes `aider` as a deep command.

---

## Sources (official, fetched 2026-08-25)

There is **no official Aider PDF**. Canon is HTML at `aider.chat/docs/`. Every URL below was opened this session.

- Docs index — https://aider.chat/docs/
- Usage — https://aider.chat/docs/usage.html
- In-chat commands — https://aider.chat/docs/usage/commands.html
- Chat modes — https://aider.chat/docs/usage/modes.html
- Scripting — https://aider.chat/docs/scripting.html
- Repository map — https://aider.chat/docs/repomap.html
- Repo-map blog — https://aider.chat/2023/10/22/repomap.html
- Git integration — https://aider.chat/docs/git.html
- Configuration — https://aider.chat/docs/config.html
- YAML `.aider.conf.yml` — https://aider.chat/docs/config/aider_conf.html
- Sample YAML — https://github.com/Aider-AI/aider/blob/main/aider/website/assets/sample.aider.conf.yml
- Options reference — https://aider.chat/docs/config/options.html
- API keys — https://aider.chat/docs/config/api-keys.html
- `.env` — https://aider.chat/docs/config/dotenv.html
- Advanced model settings — https://aider.chat/docs/config/adv-model-settings.html
- Reasoning models — https://aider.chat/docs/config/reasoning.html
- Connecting to LLMs — https://aider.chat/docs/llms.html
- OpenAI — https://aider.chat/docs/llms/openai.html
- Anthropic — https://aider.chat/docs/llms/anthropic.html
- Gemini — https://aider.chat/docs/llms/gemini.html
- GROQ — https://aider.chat/docs/llms/groq.html
- xAI — https://aider.chat/docs/llms/xai.html
- DeepSeek — https://aider.chat/docs/llms/deepseek.html
- Ollama — https://aider.chat/docs/llms/ollama.html
- LM Studio — https://aider.chat/docs/llms/lm-studio.html
- OpenAI compatible APIs — https://aider.chat/docs/llms/openai-compat.html
- OpenRouter — https://aider.chat/docs/llms/openrouter.html
- GitHub Copilot — https://aider.chat/docs/llms/github.html
- Azure — https://aider.chat/docs/llms/azure.html
- Vertex AI — https://aider.chat/docs/llms/vertex.html
- Amazon Bedrock — https://aider.chat/docs/llms/bedrock.html
- Other LLMs / LiteLLM — https://aider.chat/docs/llms/other.html
- LiteLLM providers — https://docs.litellm.ai/docs/providers
- Linting and testing — https://aider.chat/docs/usage/lint-test.html
- Conventions — https://aider.chat/docs/usage/conventions.html
- Watch / IDE AI comments — https://aider.chat/docs/usage/watch.html
- Images & URLs — https://aider.chat/docs/usage/images-urls.html
- Voice — https://aider.chat/docs/usage/voice.html
- Browser GUI — https://aider.chat/docs/usage/browser.html
- Copy/paste web chat — https://aider.chat/docs/usage/copypaste.html
- Prompt caching — https://aider.chat/docs/usage/caching.html
- Config & text files — https://aider.chat/docs/usage/not-code.html
- Edit formats — https://aider.chat/docs/more/edit-formats.html
- Installation — https://aider.chat/docs/install.html
- Docker — https://aider.chat/docs/install/docker.html
- Supported languages — https://aider.chat/docs/languages.html
- FAQ — https://aider.chat/docs/faq.html
- Leaderboards — https://aider.chat/docs/leaderboards/
- LICENSE (Apache-2.0) — https://github.com/Aider-AI/aider/blob/main/LICENSE.txt
- GitHub repo — https://github.com/Aider-AI/aider

---

## Host bind (additive, 2026-08-27 s6) — C2 still dark

This process: `Get-Command aider` → **NOT_ON_PATH**. WAVE C2 remains designed-but-dark until Keith `aider-install`. Distinct protocol (SEARCH/REPLACE + one git commit per edit) still earns a slot **after** install. `--subtree-only --analytics-disable`; `--no-auto-commits` if Core fences. Not a stage-6 pass.
