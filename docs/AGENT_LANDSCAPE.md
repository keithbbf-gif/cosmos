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
1. Enable Copilot Code Review on keithbbf-gif/cosmos — it reads AGENTS.md automatically.
2. Add Cursor Bugbot as a second reviewer for a second opinion.
3. Keep Grok Code 4.6 as the primary executor via the work-order loop; use Copilot/Cursor as the review gate, not the builder.
4. Mirror to GitLab only if you need Duo's pipeline-aware security review.

See docs/AGENTS.md for the conventions these agents will read.
