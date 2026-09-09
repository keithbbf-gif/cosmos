# Agent Landscape — What Can Check Code Natively Inside GitHub / GitLab (Sept 2026)

## Native to GitHub (runs inside the repo, no external IDE)

### GitHub Copilot Code Review (GA since March 2026)
- Agentic: reads the full diff, explores the repo, comments on architecture and cross-cutting concerns.
- Supports AGENTS.md, custom agent skills, and MCP servers for team context.
- Medium tier routes complex PRs to a higher-reasoning model.
- Can review bot-authored and very large PRs (Aug 2026 update).
- Trigger: assign @copilot as reviewer, or `gh pr edit --add-reviewer @copilot`.

### GitHub Copilot Coding Agent (cloud)
- Picks up an issue or work order, works in a GitHub Actions sandbox, opens a PR.
- ~59 min session cap. Returns a PR for human review.

### GitHub Code Quality (GA Aug 2026)
- Combines CodeQL + AI for maintainability/reliability. Uses Copilot Autofix.
- 67% of findings resolved before merge in GitHub's own org.

### Cursor (via GitHub App)
- Bugbot: automated PR review for bugs and security.
- Cloud Agents: run in the cloud on your repos, open PRs.
- Cursor Origin (beta Aug 2026): hosts repos + PRs + agents in one surface, syncs with GitHub.

### Third-party GitHub Apps (run as reviewers)
- CodeRabbit — broadest platform support, strong on recall.
- Qodo (ex-Codium) — multi-agent, multi-repo awareness.
- Greptile — high bug-catch rate, more false positives.
- Macroscope — highest detection rate in 2026 benchmarks (48%, 98% precision).
- Open-source: pr-agent, Kodus AI, shippie.

## Native to GitLab

### GitLab Duo Code Review Flow (GA Jan 2026)
- Agentic: analyzes changes, cross-file dependencies, pipeline + security context.
- Assign @GitLabDuo as reviewer on a merge request.
- Custom instructions via .gitlab/duo/mr-review-instructions.yaml.
- Security Review Flow (beta July 2026) catches logic flaws scanners miss.
- Duo Agent Platform supports custom flows and external Claude Code / Codex agents.

## Recommendation for Cosmos
1. **Default Gitur reviewer is Claude** (Keith 2026-09-09). Trigger
   `@claude review` on every GitHub PR and GitLab MR. `cosmos_gitur.request_default_review`.
2. **CCr (Grok 4.6 this TUI) reviews all code** before dispose onto the live tree.
   Two families: Claude on the forge, Grok as CCr. Diversity is the point.
3. Cursor Cloud Agents stay Lane B **BUILD** (Opus 5 / Sonnet). PR review is still Claude on GitHub.
4. Copilot Code Review is available, not the default. Do not assign Copilot as the Gitur default reviewer.
5. COSMOS `dispatch()` stays `ANTHROPIC_OFF` — no `claude -p`. Gitur vendor agents are ON.

See docs/AGENTS.md for the conventions these agents will read.
