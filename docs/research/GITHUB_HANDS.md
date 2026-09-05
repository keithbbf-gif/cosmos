# GITHUB HANDS — G46 scout return (GitHub platform)

**Scout:** G46 (Grok Build), mesh scout. **Date:** 2026-08-25.
**Consumer:** COSMOS / COW. Candidate backlog, **not** a live-mesh claim.
**Repo in play:** `keithbbf-gif/cosmos` (GitHub + GitLab both connected; Cursor Cloud Agents already push GitHub branches). GitLab remains the named forge for CI (`glab`); GitHub is the **second forge** with more agent/MCP/Actions surface.

**Filter:** a surface with no hands is rejected. Every row is an **action** COSMOS could fire: REST/GraphQL endpoint, `gh` subcommand, webhook subscription, Actions trigger, Copilot agent-dispatch, MCP tool, or CLI.

**Rank key:** FREE + high-power first. `POWER` = new capability × reliability × how many COSMOS rails it unlocks. Equal power, cheaper wins. Copilot credits sit **below** the free API/CLI/webhook/Actions-public cluster even when the agent is more autonomous.

**How COSMOS would reach GitHub (reach column, one pattern):**
Core stays sole ledger writer. GitHub is reached as (1) **native worker** wrapping `gh` / `copilot` / `git` in an attempt-private workspace, (2) **HTTP** through the spend gate (`https://api.github.com`, `https://api.github.com/graphql`), (3) **MCP-client** to the official GitHub MCP (`https://api.githubcopilot.com/mcp/` or local Docker), (4) **webhook ingress** into Core's return-watcher (HMAC-verified), (5) **DOM worker** on github.com only when the API is AUTH_REQUIRED / UNREACHABLE. Keith owns credentials (`gh auth login`, PAT, App private key). No bats. Fenced commit still gates any tree write.

**Auth primer (all API/CLI rows inherit this unless overridden):**

| method | token shape | REST primary limit | GraphQL primary | notes |
|--------|-------------|--------------------|-----------------|-------|
| none | — | 60 req/hr/IP | n/a | public data only |
| PAT (fine-grained **preferred**, or classic) | `github_pat_…` / `ghp_…` | **5,000 req/hr** | **5,000 points/hr** | Keith creates; store under `live/config/` never in git. Fine-grained needs per-endpoint permissions. Classic `repo` + `workflow` for `.github/workflows`. |
| GitHub App **installation** token | `ghs_…` (1h) | 5,000–12,500/hr (scales with repos/users; 15k on GHEC) | 5,000–12,500 points/hr | JWT (app id + private key) → `POST /app/installations/{id}/access_tokens`. Best production identity. Server-to-server. **Does not** work for Copilot cloud-agent tasks API. |
| GitHub App **user** token | `ghu_…` | user's 5,000/hr | user's 5,000 points | OAuth user-to-server. Required for Copilot agent-tasks API. |
| OAuth app | `gho_…` | user's 5,000/hr | user's 5,000 points | Broad scopes; GitHub recommends Apps instead. |
| `GITHUB_TOKEN` (Actions) | job-scoped | **1,000 req/hr/repo** (15k on GHEC) | 1,000 points/hr/repo | Auto in workflows. Events it emits do **not** retrigger workflows except `workflow_dispatch` / `repository_dispatch`. |
| Copilot CLI | `COPILOT_GITHUB_TOKEN` > `GH_TOKEN` > `GITHUB_TOKEN` > `gh auth` | Copilot AI-credits, not REST | — | Fine-grained PAT needs **Copilot Requests** (Account tab, personal owner). |

Headers for REST: `Authorization: Bearer <token>`, `Accept: application/vnd.github+json`, `X-GitHub-Api-Version: 2022-11-28` (docs also show `2026-03-10`). GraphQL: `POST https://api.github.com/graphql`. Secondary limits apply to both (≤100 concurrent; content-create ~80/min, 500/hr). Prefer **webhooks over polling**.

**GitHub plan cost floor (Free personal, which `keithbbf-gif` is on unless Pro):** 2,000 Actions minutes/mo **private** (public + self-hosted = **free**); 500 MB Packages (public packages **free**; Container registry storage currently **free**); 120 Codespaces core-hours + 15 GB storage/mo. REST/GraphQL/webhooks/`gh` are **free** at the rate limits above.

**Sources (official, fetched 2026-08-25):** [REST getting started](https://docs.github.com/en/rest/using-the-rest-api/getting-started-with-the-rest-api), [REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), [GraphQL forming calls](https://docs.github.com/en/graphql/guides/forming-calls-with-graphql), [GraphQL rate limits](https://docs.github.com/en/graphql/overview/rate-limits-and-query-limits-for-the-graphql-api), [Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions), [Actions events](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows), [workflow dispatch REST](https://docs.github.com/en/rest/actions/workflows), [webhook events](https://docs.github.com/en/webhooks/webhook-events-and-payloads), [GitHub Apps vs OAuth](https://docs.github.com/en/apps/differences-between-apps), [installation tokens](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-an-installation-access-token-for-a-github-app), [gh manual](https://cli.github.com/manual/gh), [Copilot cloud agent API](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api), [Copilot plans](https://docs.github.com/en/copilot/get-started/plans), [Copilot CLI](https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli), [GitHub products](https://docs.github.com/en/get-started/learning-about-github/githubs-products), [Packages billing](https://docs.github.com/en/billing/concepts/product-billing/github-packages), [GitHub MCP server](https://github.com/github/github-mcp-server).

---

## Ranking table

| # | name | kind | HANDS (what it DOES) | auth | cost | power | how COSMOS reaches it |
|---|------|------|----------------------|------|------|-------|------------------------|
| 1 | **`gh` CLI (official)** | CLI | One binary that **is** the GitHub hand: issues, PRs (create/review/merge/checks), Actions (`workflow run`, `run watch/rerun/cancel`, logs, artifacts), releases, gists, codespaces, projects, search, secrets/variables, `gh api` (any REST) + `gh api graphql` (any mutation). `gh auth login` stores the token; `gh auth token` feeds other tools. | `gh auth login` (OAuth device or PAT). Fine-grained or classic. | **free** (OSS; API rate limits only) | **highest** | Native worker: `gh` on PATH after Keith authenticates. Preferred over raw curl. JSON via `--json`/`--jq`. Never a `.bat`. |
| 2 | **REST: issues + comments** | REST | `GET/POST /repos/{o}/{r}/issues` — list/create. `GET/PATCH /issues/{n}` — read/edit/close. `POST …/issues/{n}/comments` — comment. `POST …/issues/{n}/assignees` — assign (incl. Copilot bot). `POST/DELETE …/issues/{n}/labels`. The coordination surface: file work, close it, talk on it. | PAT `issues:write` or App `issues:write`. Classic `repo`. | **free** (5k/hr) | **highest** | HTTP spend-gate **or** `gh issue create/list/view/comment/close/edit`. Return-watcher can consume `issues` / `issue_comment` webhooks instead of polling. |
| 3 | **REST: pull requests + reviews + merge** | REST | `POST /repos/{o}/{r}/pulls` — open PR. `GET …/pulls/{n}` (+ `Accept: application/vnd.github.diff` / `.patch`). `GET …/pulls/{n}/files` (max 3000). `GET …/pulls/{n}/commits`. `PUT …/pulls/{n}/merge` — merge. `PUT …/pulls/{n}/update-branch`. `POST …/pulls/{n}/reviews` then `POST …/reviews/{id}/events` with `APPROVE` / `REQUEST_CHANGES` / `COMMENT`. `POST …/pulls/{n}/requested_reviewers`. | PAT `pull_requests:write` + `contents:write` to merge. App same. | **free** | **highest** | `gh pr create/checkout/diff/review --approve/merge --squash/checks --watch`. Core never merges unfenced: PR is the publish path; fenced commit still owns the live tree. |
| 4 | **REST: contents + Git database** | REST | `GET/PUT/DELETE /repos/{o}/{r}/contents/{path}` — read/create/update/delete a file (Base64; serial only, concurrent PUT/DELETE 409). `GET …/readme`, `GET …/tarball/{ref}`, `GET …/zipball/{ref}`. Git DB: `POST …/git/blobs`, `POST …/git/trees`, `POST …/git/commits`, `POST …/git/refs`, `PATCH …/git/refs/{ref}` — full commit without a local git. Tree API for >1000 files. | `contents:write`. **`workflow` scope extra** to touch `.github/workflows`. | **free** | **highest** | Native `git` in the attempt workspace is usually better; Contents API for single-file hotfixes; Git DB for batch commits from a worker that must not clone. Still publish through fenced commit / PR. |
| 5 | **`repository_dispatch` (out-of-band trigger)** | REST + Actions + webhook | `POST /repos/{o}/{r}/dispatches` body `{event_type, client_payload}` (`event_type` ≤100 chars; payload <64 KB, ≤10 top-level keys). Fires Actions `on: repository_dispatch` **and** App webhooks. Workflow file must exist on **default branch**. Always creates a run even if the caller used `GITHUB_TOKEN`. **This is COSMOS → GitHub CI.** | PAT/App `contents:write` (docs). | **free** (Actions minutes: public=0, private from 2,000 quota) | **highest** | Spend-gate HTTP or `gh api -X POST /repos/keithbbf-gif/cosmos/dispatches -f event_type=cosmos-job`. Pair with a workflow that runs tests / Copilot CLI / artifact upload. Return via `workflow_run` webhook. |
| 6 | **`workflow_dispatch` (named workflow + inputs)** | REST + Actions + CLI | `POST /repos/{o}/{r}/actions/workflows/{id}/dispatches` `{ref, inputs}`. Inputs: ≤25 keys, ≤65,535 chars. Returns run id + `html_url` (newer API). Same default-branch constraint. Manual/API/CLI trigger of a **specific** workflow. | `actions:write`. | **free** on public; private minutes from plan | **highest** | `gh workflow run ci.yml -f k=v` then `gh run watch`. Cleaner than dispatch when the workflow is known. |
| 7 | **Webhooks (ingress event bus)** | webhook | GitHub POSTs to COSMOS when something happens. HMAC `X-Hub-Signature-256` (secret). Events COSMOS actually needs: `push`, `pull_request` (`opened/synchronize/closed/ready_for_review/review_requested`), `issues`, `issue_comment`, `pull_request_review`, `pull_request_review_comment`, `workflow_run`, `workflow_job`, `check_run`, `check_suite`, `status`, `release`, `package`, `deployment_status`, `repository_dispatch`, `create`/`delete` (branch/tag), `dependabot_alert`, `code_scanning_alert`, `discussion`. Payload cap 25 MB (undelivered if over). `ping` on create. | Webhook secret (not a PAT). Deliveries retry; redeliver via REST. | **free** | **highest** | `POST /repos/{o}/{r}/hooks` `{events, config.url, secret}` pointing at Core (Tailscale/`cosmos up` public URL). Verify HMAC, ledger the delivery id (`X-GitHub-Delivery`), drive return-watcher. GitHub App = one central webhook for all installed repos (better than per-repo OAuth hooks). |
| 8 | **GitHub official MCP** (`github/github-mcp-server`) | MCP + API | Hosted tools: repos (get/create file, branch, search code, commits, fork), issues (CRUD, comments, sub-issues), PRs (create, review, merge, comments), Actions, git, gists, labels, notifications, orgs, projects, Dependabot, code scanning, secret scanning, users, stargazers. **Remote-only:** `create_pull_request_with_copilot`, Copilot spaces, docs search. Toolsets via URL `/mcp/x/{toolset}` or `X-MCP-Toolsets`. Read-only mode `/readonly`. | Remote: OAuth **or** `Authorization: Bearer <PAT>`. Local: Docker `ghcr.io/github/github-mcp-server` + PAT. | **free** (API rate limits) | **highest** | MCP-client HTTP to `https://api.githubcopilot.com/mcp/` (OAuth, Keith grants). Fallback: Docker stdio worker. Prefer read-write toolsets scoped (`issues,pull_requests,actions,repos`) not `all`. Complements `gh`; MCP is for agent brains, `gh` for Core jobs. |
| 9 | **Actions run control + artifacts + logs** | REST + CLI | `GET …/actions/runs`, `GET …/actions/runs/{id}`, `POST …/runs/{id}/rerun` / `rerun-failed-jobs` / `cancel`. `GET …/runs/{id}/logs` (zip). `GET …/runs/{id}/artifacts`, `GET …/artifacts/{id}/{archive_format}` (302). `GET …/actions/jobs/{id}/logs`. Cache: `GET/DELETE …/actions/caches`. Enable/disable workflow. Approve fork-PR runs. | `actions:read`/`write`. | **free** API; artifact storage shares Packages pool (500 MB Free) | **highest** | `gh run list/view --log-failed/watch/rerun/cancel/download`. After `workflow_dispatch`, poll or webhook `workflow_run.completed` then download artifacts into GEM (hash-named). |
| 10 | **GraphQL API (query + mutation)** | GraphQL | Single `POST /graphql`. Queries: nested issues/PRs/projects/files in one round-trip (saves REST chatter). Mutations COSMOS would use: `createIssue`, `updateIssue`, `addAssigneesToAssignable`, `replaceActorsForAssignable` (Copilot assign), `addComment`, `createPullRequest`, `mergePullRequest`, `addPullRequestReview`, `submitPullRequestReview`, `enablePullRequestAutoMerge`, `createCommitOnBranch`, `createRef`/`updateRefs`, `addReaction`, `createProjectV2`, `addProjectV2ItemById`, `updateProjectV2ItemFieldValue`, `addProjectV2DraftIssue`. Node IDs required. | Same tokens as REST. `GraphQL-Features` header for Copilot-assign preview. | **free** (5k points/hr; mutations cost more) | **highest** | `gh api graphql -f query='…'`. Use when a REST fan-out would burn the 5k budget (Projects V2 **requires** this historically; REST Projects exists now but GraphQL is still the complete surface). |
| 11 | **GitHub App (installation identity)** | App + REST + webhook | Register an app → JWT from app id + private key → `POST /app/installations/{id}/access_tokens` (1h `ghs_`, optional repo/permission subset). Act **as the app** (attribution: "COSMOS bot", survives user leaving). One webhook for all installed repos. Rate limit scales. Events: `installation`, `installation_repositories`, `github_app_authorization` (user revoked — stop using their user token). | App JWT (RS256, ~10 min) then installation token. Private key is a secret — Keith holds it. | **free** to register; API free | **high** | Long-lived Core sidecar mints installation tokens, never logs them. Prefer App over a PAT for anything that runs unattended. User-to-server OAuth still needed for Copilot tasks. |
| 12 | **Actions on public repos / self-hosted** | Actions | Standard GitHub-hosted minutes are **$0** on public repos, GitHub Pages, Dependabot, and **all self-hosted runners**. Private hosted: 2,000 min/mo Free (Linux 2-core $0.006/min overage; Windows $0.010; macOS $0.062). Larger runners always billed. Cache 10 GB/repo included. | `GITHUB_TOKEN` in-job; OIDC `id-token: write` for cloud login without long-lived secrets. | **free** (public / self-hosted); prepaid quota then metered private | **high** | Keep `keithbbf-gif/cosmos` public for $0 CI, **or** register a Windows self-hosted runner on this machine (Job-Object contained) so private workflows cost $0 minutes. OIDC → no PAT in secrets. |
| 13 | **Checks + commit statuses** | REST + webhook | `POST /repos/{o}/{r}/check-runs` — create a check (name, head_sha, status, conclusion, output, actions). `PATCH` to complete. `POST …/check-suites/{id}/rerequest`. Legacy: `POST …/statuses/{sha}`. Webhooks `check_run` / `check_suite` / `status`. Merge queue: `merge_group` `checks_requested`. | App `checks:write` (Apps auto-subscribe). PAT classic `repo`. | **free** | **high** | COSMOS posts a check on PRs it reviews (runtime-binding evidence: the check output **is** the artifact). Completes the "gate that runs" canon on GitHub's merge UI. |
| 14 | **Search API** | REST | `GET /search/code`, `/search/issues`, `/search/commits`, `/search/repositories`, `/search/users`. Separate, tighter limit: **30 req/min** authenticated (10 unauth). Qualifiers (`repo:`, `is:open`, `language:`). | any authenticated token | **free** (search bucket) | **high** | `gh search issues/prs/code/commits/repos`. Sweep upstream deps / COSMOS-named issues without cloning. Don't poll — 30/min is the cliff. |
| 15 | **Releases + tags + assets** | REST + CLI | `POST /repos/{o}/{r}/releases` — create release (tag, notes, draft, prerelease). Upload assets. `GET …/releases/latest`. `POST …/git/tags` annotated tags. | `contents:write` | **free** | **high** | `gh release create vX --generate-notes --target main`. Versioned COSMOS artifacts besides the ledger. |
| 16 | **Compare / commits / branches** | REST | `GET …/compare/{base}...{head}` — commits + files + `ahead_by`/`behind_by`/`status`. `GET …/commits/{sha}` (diff media types). `GET/POST/DELETE …/branches/{branch}/protection` (Pro+ on private). `GET …/commits/{ref}/status(es)`. | `contents:read` | **free** | **high** | `gh api repos/{o}/{r}/compare/main...HEAD`. Pre-merge / pre-fence evidence of what would land. |
| 17 | **Fork + clone URL surface** | REST + CLI | `POST /repos/{o}/{r}/forks`. `GET /repos/{o}/{r}` (clone urls, default branch, permissions). `gh repo clone/fork/create/sync/view`. | `contents` / public | **free** | **high** | Native `gh repo clone keithbbf-gif/cosmos` into attempt workspace. Forks for untrusted agent work. |
| 18 | **Gists** | REST + CLI | `POST /gists` — create secret/public gist (multi-file). `PATCH /gists/{id}`, comments. Instant paste-bin / scratch artifact without a repo commit. | `gist` scope (classic) | **free** | **med-high** | `gh gist create file.py --desc "…"`. Spill logs/snippets that should not enter the cosmos tree. |
| 19 | **Projects V2** | GraphQL + REST + CLI + webhook | GraphQL: `createProjectV2`, `addProjectV2ItemById`, `updateProjectV2ItemFieldValue`, `addProjectV2DraftIssue`, query fields/iterations/single-select options. REST now: `/orgs/{org}/projectsV2/…/items` (add Issue/PR by id or owner/repo/number). Webhooks `projects_v2`, `projects_v2_item`, `projects_v2_status_update` (org; preview). Classic projects (`project`/`project_card`) are sunset — do not build on them. | `project` scope / App `projects:write` | **free** (Issues & Projects on Free) | **med-high** | `gh project` + `gh api graphql`. Board for the 135-tool port backlog if Keith wants GitHub as the card surface; otherwise GitLab issues remain primary. |
| 20 | **Packages / GHCR** | REST + registry + webhook | Publish/install: `ghcr.io` (containers), `npm.pkg.github.com`, Maven, NuGet, Rubygems, Gradle. REST: `GET /user/packages`, `/orgs/{org}/packages`, `/users/{u}/packages`, get/delete package+version, restore. Webhook `package` (`published`/`updated`). `DELETE` GraphQL `deletePackageVersion`. | `read:packages` / `write:packages` / `delete:packages`. `GITHUB_TOKEN` in Actions with `packages: write`. docker login `ghcr.io -u USER --password-stdin`. | **public packages free**. Private: 500 MB + 1 GB transfer/mo Free then $0.25/GB-mo (shared with Actions artifacts). **Container registry storage currently free** (docs, with 1-month notice if that changes). 10 GB/layer, 10 min upload timeout. | **high** (artifact rail) | Actions job `docker push ghcr.io/keithbbf-gif/cosmos:sha`. COSMOS stores the digest; ledger holds the pointer. Complements GEM (content-addressed local) with a public pull URL. |
| 21 | **Copilot CLI (`copilot -p`)** | CLI + agent | Headless coding agent on this machine: edit, shell, MCP (GitHub MCP **built in**), plan/agent modes. `copilot -p "…" --allow-tool='write,shell(git:*)' -s`. `--yolo`/`--allow-all` for unattended. `--autopilot --max-autopilot-continues N`. `--acp --stdio` ACP server (preview) for IDE/CI orchestration. `--model`, BYOK (`COPILOT_PROVIDER_BASE_URL` → Ollama/OpenAI/Anthropic). Hooks (preToolUse). Windows: PowerShell or WSL. | Copilot account. Token: `COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN` / `gh auth`. Fine-grained: **Copilot Requests**. | **Copilot Free**: limited AI credits, auto model, 2,000 completions/mo, **cloud agent limited**. Pro $10/mo (1,500 credits). Student free. | **high** (local agent lane) | Native worker in attempt workspace, spend-gated as a Copilot-credit rail. Prefer `--allow-tool` allowlist over `--yolo`. Pair with existing Grok/Cursor lanes (vendor-plural). BYOK to Ollama = $0 credits. |
| 22 | **Copilot cloud agent (coding agent) via API** | REST + GraphQL + agent-trigger | **Dispatch a cloud SWE agent** that clones, edits, tests, opens a draft PR. `POST /agents/repos/{o}/{r}/tasks` `{prompt, base_ref, model, create_pull_request}` (public preview). `GET /agents/repos/{o}/{r}/tasks`, `GET /agents/tasks`, `GET …/tasks/{id}` states: `queued/in_progress/completed/failed/idle/waiting_for_user/timed_out/cancelled`. **Issue assign:** REST `assignees: ["copilot-swe-agent[bot]"]` + `agent_assignment`; GraphQL `createIssue`/`updateIssue`/`addAssigneesToAssignable`/`replaceActorsForAssignable` + `agentAssignment` + header `GraphQL-Features: issues_copilot_assignment_api_support,coding_agent_model_selection`. Runs on Actions (minutes + AI credits). MCP via `.github/copilot/mcp.json` (no OAuth remote MCP). | **User-to-server only** (PAT / App user token / OAuth). Installation tokens **rejected**. Fine-grained: metadata read + actions/contents/issues/PRs write. Classic `repo`. | **paid credits** (Pro+ cloud agent included on paid plans; Free = limited). Also burns Actions minutes on **private** repos. Public Actions minutes free. | **high** (cloud coding lane, Cursor-shaped) | `gh agent-task create "…" --repo keithbbf-gif/cosmos --follow` **or** spend-gate `POST /agents/repos/keithbbf-gif/cosmos/tasks`. Poll task state; PR URL is the result artifact. Same pattern as Cursor Cloud Agents API. Do not double-dispatch Cursor + Copilot on the same issue without a lease. |
| 23 | **`gh agent-task`** | CLI | Preview wrapper over the cloud-agent API: `create` (inline / `-F file` / stdin), `list`, `view` (by PR number or task UUID). `--base`, `--custom-agent` (`.github/agents/my-agent.md`), `--follow` logs. Aliases: `gh agent`, `gh agents`. | `gh auth` user token | same as row 22 | **high** | Native worker. Preferred COSMOS trigger for Copilot cloud agent (no raw JSON). |
| 24 | **MCP tool `create_pull_request_with_copilot` / `assign_copilot_to_issue`** | MCP + agent-trigger | Remote GitHub MCP: give Copilot a `problem_statement` → coding agent PR. Local MCP: `assign_copilot_to_issue`. Same agent, agent-shaped tool instead of REST. | MCP OAuth/PAT (user) | same as row 22 | **high** | MCP-client (row 8) with `copilot` toolset enabled: `https://api.githubcopilot.com/mcp/x/copilot`. |
| 25 | **Copilot CLI inside Actions** | Actions + CLI | Workflow installs `@github/copilot`, runs `copilot -p … --yolo --no-ask-user` with `COPILOT_GITHUB_TOKEN` or (newer CLI) `GITHUB_TOKEN` + permission `copilot-requests: write`. Unattended review/summary/patch on the runner. | PAT with Copilot Requests **or** `GITHUB_TOKEN` + `copilot-requests: write` | AI credits + Actions minutes (private) | **high** | Workflow on `keithbbf-gif/cosmos`; Core fires `workflow_dispatch`. Artifact = step summary / committed patch / PR. Fork-PR trigger is unsafe (`--yolo`) — restrict to `push` / `workflow_dispatch` on default branch. |
| 26 | **`gh aw` Agentic Workflows** | CLI ext + Actions | `gh extension install github/gh-aw`. `gh aw add-wizard …`, `gh aw run <workflow>`. Markdown agentic workflows on Actions with engines Copilot / Claude / Codex / Gemini. `assign-to-agent` safe-output. | `gh` + engine secret (`COPILOT_GITHUB_TOKEN` / `ANTHROPIC_API_KEY` / …). Linux/macOS/WSL. | engine cost + Actions minutes | **high** | Optional; overlaps COSMOS scheduler. Use only if Keith wants GitHub-hosted agent recipes rather than Core jobs. |
| 27 | **OIDC from Actions (`id-token: write`)** | Actions | Job requests JWT from `https://token.actions.githubusercontent.com`. Claims: `sub` (`repo:ORG/REPO:environment:…`), `ref`, `sha`, `run_id`, `actor`. Cloud providers mint short-lived creds — **no long-lived secrets in GitHub**. | workflow permission `id-token: write` | **free** | **high** (secret hygiene) | If COSMOS (or a worker) is the audience, validate `iss`/`sub`/`aud` and accept the job. Inverse of PAT-in-secrets. |
| 28 | **Codespaces** | REST + CLI | `POST /repos/{o}/{r}/codespaces` `{ref, machine}` — create. List/start/stop/delete. `GET …/codespaces/devcontainers`. `gh codespace create/ssh/stop/delete/logs`. Full VM + editor against a branch. | `codespace` scope / Codespaces repo permission | **Free:** 120 core-hours + 15 GB/mo. Pro: 180 h + 20 GB. Then metered. Org Codespaces is a Team toggle. | **med-high** | `gh codespace create -r keithbbf-gif/cosmos` for a human/agent cloud box. Heavier and metered vs Copilot cloud agent (which is the coding-shaped Codespace). Spend-gate hours. |
| 29 | **Pages** | REST + Actions | `GET/PUT /repos/{o}/{r}/pages` — enable/configure. Builds from Actions or `/docs`. Webhook `page_build`. Free on public repos. | `pages:write` | **free** (public) | **med** | Publish KDash static or research HTML. Not the live Core. |
| 30 | **Dependabot + code scanning + secret scanning** | REST + webhook | Dependabot alerts REST + webhook `dependabot_alert`. Code scanning alerts REST + `code_scanning_alert`. Secret scanning REST + webhooks. MCP toolsets `dependabot`, `code_security`, `secret_protection`. | security-events / specific perms | **free** Dependabot alerts on Free. Advanced Security paid on private Team+. | **med-high** | Subscribe webhooks → Core incidents. Don't auto-merge Dependabot without a fence. |
| 31 | **Discussions** | GraphQL + webhook + CLI | Discussions GraphQL; webhooks `discussion` / `discussion_comment` (preview). `gh discussion`. | `discussions:write` | **free** | **med** | Only if the cosmos repo uses Discussions instead of issues. |
| 32 | **Notifications** | REST + MCP | `GET /notifications`, mark read, subscribe thread. MCP `notifications` toolset. | `notifications` | **free** | **med** | Drain Keith's GitHub inbox into a COSMOS watcher. Easy to abuse rate limits — prefer webhooks. |
| 33 | **Rulesets** | REST + CLI | `GET/POST /repos/{o}/{r}/rulesets` — branch rules as data (required checks, linear history). `gh ruleset`. | admin | **free** (some rules Pro/Team on private) | **med** | Encode "no unfenced merge to main" as a GitHub ruleset that requires the COSMOS check (row 13). |
| 34 | **Secrets + variables (Actions)** | REST + CLI | `gh secret set` / `gh variable set`. REST encrypted secrets. Org/env/repo levels. | admin / `secrets:write` | **free** | **med** | Keith sets; COSMOS must **not** mint GitHub secrets from the ledger. Core may *read* via `gh` only inside a worker if a job needs them — prefer OIDC (row 27). |
| 35 | **Deployments + environments** | REST + webhook | `POST …/deployments`, statuses, protection-rule callbacks (`deployment_protection_rule`, `deployment_review` — Apps). Environment wait gates. | `deployments:write` | **free** | **med** | Map COSMOS "live vs attempt" to GitHub environments (`staging`/`live`) if a Pages/GHCR deploy exists. Protection-rule webhook lets Core approve a deploy after ledger evidence. |
| 36 | **Attestations** | CLI | `gh attestation` — verify artifact provenance (sigstore). | `gh auth` | **free** | **med** | Bind a published GHCR image / release asset to the git SHA — runtime-binding cousin on GitHub's side. |
| 37 | **`gh skill` (preview)** | CLI | Install/manage agent skills for Copilot-shaped agents. | `gh auth` | **free** tool; agent still costs credits | **med** | Only if Copilot custom agents are adopted (`.github/agents/*.md`). |
| 38 | **OAuth app (user login)** | OAuth | Web or device flow → `gho_` user token with scopes. Identify-as-Keith for user-only APIs (Copilot tasks, Codespaces, notifications). | client id+secret (Keith). Never in the tree. | **free** | **med** | GitHub App user-to-server is the modern path; keep classic OAuth only if an endpoint still demands it. Device flow fits a headless service poorly — prefer PAT/App. |
| 39 | **Markdown + emojis + gitignore + licenses** | REST | `POST /markdown` render; `GET /emojis`; `GET /gitignore/templates`; `GET /licenses`. Tiny utilities. | none/auth | **free** | **low-med** | Render issue bodies. Not a rail. |
| 40 | **Rate-limit probe** | REST | `GET /rate_limit` (does not consume primary). Headers `x-ratelimit-*` on every call. | any | **free** | **infra** | Spend-gate / worker checks remaining before a burst; fail-closed on 403/429 with `x-ratelimit-reset`. |
| 41 | **DOM on github.com** | DOM | Click through issue assign, PR merge, Actions rerun, Copilot panel, billing, App install consent — everything the API cannot do when AUTH_REQUIRED / MFA / new product UI. | Keith's browser session (contained profile) | **free** | **high as fallback** | Existing `cosmos_browser` / Playwright MCP. Canon: **DOM first when the API depends on something that can run out** (Copilot credits, PAT expiry). For ordinary issue/PR/CI, API/`gh` is correct. |

---

## Actions triggers COSMOS can fire or subscribe

| trigger | how COSMOS fires it | notes |
|---------|---------------------|-------|
| `workflow_dispatch` | `POST …/actions/workflows/{file}/dispatches` or `gh workflow run` | Named workflow + typed inputs. File must be on default branch. |
| `repository_dispatch` | `POST …/dispatches` `{event_type, client_payload}` | Custom event; many workflows can listen with `types:`. |
| `workflow_call` | another workflow `uses:` | Reusable; not an external hand unless COSMOS commits a caller workflow. |
| `schedule` (cron) | commit cron to workflow YAML | GitHub's clock, not Core's scheduler. Use Core scheduler + dispatch instead (one authority). |
| `push` / `pull_request` / `release` / `package` | git/PR/release/package hands above | Automatic. |
| `workflow_run` | subscribe webhook | Chain: COSMOS dispatch → run completes → webhook back. |
| `workflow_job` | subscribe webhook | Per-job start/finish for live KDash. |

Public-repo hosted minutes = $0. Private hosted = plan quota then metered. Self-hosted = $0 minutes.

---

## Webhook events worth installing (subset)

Install **one GitHub App webhook** (or one repo hook) with a secret. Subscribe only to what Core handles (docs: don't subscribe to everything).

| event | COSMOS use |
|-------|------------|
| `push` | ingest new SHAs; ignore `GITHUB_TOKEN` loops |
| `pull_request` | Cursor/Copilot agent PRs landed; review gate |
| `pull_request_review` / `_comment` | human/agent review loop |
| `issues` / `issue_comment` | assign Copilot / comment results |
| `workflow_run` / `workflow_job` | return-watcher for dispatched CI |
| `check_run` / `check_suite` / `status` | merge evidence |
| `release` / `package` | published artifact pointer |
| `deployment_status` | env promote |
| `dependabot_alert` / `code_scanning_alert` | incident |
| `installation` / `github_app_authorization` | App lifecycle; stop on revoke |
| `projects_v2_item` | if Projects is the board |
| `ping` / `meta` | hook health |

Validate `X-Hub-Signature-256`. Dedup on `X-GitHub-Delivery`. Sender may be `ghost`.

---

## Copilot surfaces (credit vs free)

| surface | trigger | Free plan | paid |
|---------|---------|-----------|------|
| Inline completions | IDE | 2,000/mo | included |
| Copilot Chat | IDE / github.com / mobile | limited credits, auto model | models + credits |
| Copilot CLI `copilot -p` | native worker | limited credits; CLI itself free | Pro+ models |
| Copilot cloud agent | `POST /agents/…/tasks`, issue assign, `gh agent-task`, MCP `create_pull_request_with_copilot` | **limited** | included on Pro/Pro+/Max/Business/Enterprise (credits) |
| Copilot code review | PR | VS Code "review selection" only | full; **also burns Actions minutes on private repos** |
| MCP in Copilot | config | Free has MCP | yes |
| ACP server | `copilot --acp` | preview | preview |

Copilot is **not** a $0 coding rail except on Free's leftover credits or BYOK/Ollama. Cursor Cloud Agents (already live, SuperGrok-included) stay the prepaid coding overflow; Copilot is the GitHub-native twin.

---

## Recommended COSMOS GitHub stack (not implemented this pass)

1. Keith: `gh auth login` (fine-grained PAT or GitHub App). Token never printed; live config only.
2. Native jobs speak **`gh`** (issues/PRs/Actions/releases) and `gh api graphql` when needed.
3. **Ingress:** GitHub App webhook → Core HMAC verify → ledger → return-watcher.
4. **Egress CI:** `repository_dispatch` / `workflow_dispatch` on `keithbbf-gif/cosmos` (public = $0 minutes). **SUPERSEDED for this tree — see Host bind H3 below.** Live `keithbbf-gif/cosmos` is **PRIVATE**; hosted Actions minutes are **not** $0. WAVE A2 does not enable hosted Actions.
5. **Agent overflow:** `gh agent-task create` **or** Cursor Cloud Agents — lease so they don't double-write a branch.
6. **MCP:** remote `https://api.githubcopilot.com/mcp/` for agent brains; don't give Core a shell via MCP when `gh` exists.
7. **DOM:** only AUTH_REQUIRED / billing / App-install consent.
8. Fail-closed on 401/403/429; never invent a green Actions log.

---

## Explicitly not hands / do not build

- Polling `GET /events` or notifications as a substitute for webhooks.
- Classic Projects (`/projects` cards/columns) — sunset.
- Scraping github.com HTML when REST/`gh` works (ToS + rate limits).
- Storing App private keys, client secrets, or PATs in the tracked tree.
- `GITHUB_TOKEN` from Actions writing back in a way that is expected to retrigger workflows (it won't, except dispatch).
- Claiming Copilot cloud agent is free — it is credit-metered; Free is a trial allowance.
- Treating GitHub as a second ledger. PRs/Actions/Packages are projections + worker rails.

---

## Verification status

Docs-grounded scout (official pages listed in the header). **Not live-probed** against `keithbbf-gif/cosmos` this pass: no `gh auth status`, no dispatch, no webhook installed. Per canon, nothing here is claimed working until Core emits the ledger event / API body for it.

---

## Host bind (additive, 2026-08-25 ARCH) — H3

Live this machine, this process (`gh` 2.97.0):

- `gh auth status` → logged in **`keithbbf-gif`** (keyring); scopes `gist`, `read:org`, `repo`, `workflow`; protocol https.
- `gh repo view keithbbf-gif/cosmos --json isPrivate,visibility` → **`isPrivate: true`**, **`visibility: PRIVATE`**, default branch `main`.
- `.github/workflows` → **missing**.

Step 4 of the recommended stack (`workflow_dispatch` on public = $0 minutes) is **false for this tree**. Copying it would burn the Free **2,000** private hosted minutes or silently no-op. **WAVE A2 (ARCH):** queue-native `gh` worker for issues / PRs / `gh api` only (5k REST/hr, $0). Hosted Actions stay dark until a self-hosted runner or Keith changes visibility. Copilot cloud-agent is credit-metered — not this row. Dispatcher `ApiRail` waits on Kernel attach (BACKLOG). This is **not** a wired COSMOS worker and **not** a stage-6 pass.

---

## Host bind (additive, 2026-08-27 s6 re-probe) — H3 still holds

This process (`gh` 2.97.0, 2026-08-27T01:53-05):

- `gh api user` → **`keithbbf-gif`**
- `gh repo view keithbbf-gif/cosmos --json isPrivate,visibility,defaultBranchRef,nameWithOwner` → **`isPrivate: true`**, **`visibility: PRIVATE`**, default branch `main`, `keithbbf-gif/cosmos`
- scopes still `gist`, `read:org`, `repo`, `workflow` (keyring); protocol https
- `.github/workflows` still **missing**

H3 is not a stale 08-25 note. WAVE A2 remains queue-native `gh` (issues/PRs/`gh api`); hosted Actions stay dark. Not a COSMOS worker.
