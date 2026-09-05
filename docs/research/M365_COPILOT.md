# M365 → GitHub Copilot / Codex agent — research (SGH, 2026-08-26)

**Source:** SGH (Grok research) job `a3a52ecb`, rc=0, 159.7s. Live web sources, Aug 2026.
Filed by COW as MOTIF stage-1 research feeding the codex-rail / in-GitHub Codex agent path
(`cosmos/cosmos_codex_rail.py`, disposed 2026-08-26T18:59).

## Crux (the honest answer)
**Microsoft 365 Family / Premium does NOT include a GitHub Copilot seat, GitHub AI credits, or
any path to enable the in-GitHub OpenAI Codex coding agent.** It includes only Microsoft's
Office/Windows Copilot (Word/Excel/PowerPoint/Outlook/Designer + monthly AI credits). Office
Copilot and GitHub Copilot are different products, different billing, no link path from a consumer
M365 subscription to github.com.

## 1. What M365 Family / Premium includes
- **Family** ($12.99/mo, $129.99/yr): Copilot in Office apps + 60 AI credits/mo for in-app
  edits/drafts/image-gen. Owner only, not shareable.
- **Premium** ($19.99/mo, $199.99/yr): Family + extensive usage beyond the 60-credit cap +
  exclusive agents (Researcher, Analyst, Actions, Photos). Owner only.
- Credits are **Microsoft 365 / Windows AI credits**, not GitHub credits. Copilot Pro standalone
  ($20 add-on) is discontinued — folded into Premium (new sales ended 2025-10-01; support ended
  2026-08-01). Microsoft's own "which Copilot" page (updated 2026-08-18) lists **GitHub Copilot as
  a separate product**, licensed on GitHub, not an M365 benefit.

## 2. Mapping to a GitHub seat / credits
**None.** M365 AI credits ≠ GitHub AI Credits (1 GitHub credit = $0.01). Not interchangeable;
linking a Microsoft account to GitHub does not transfer M365 Copilot.

## 3. Activation/link path for keithbbf-gif
**No activation path exists.** Getting the in-GitHub Codex agent on `keithbbf-gif/cosmos` requires
a **separate GitHub Copilot purchase** on the GitHub account, then a Copilot policy toggle.

## 4. Cheapest path to the coding agent (the actionable finding)
GitHub Copilot **Free does NOT** unlock the cloud/PR agent — only IDE completions + limited chat.

Two different "coding agents":
1. **GitHub Copilot cloud agent** (assign Copilot on an issue → it opens a PR): cheapest =
   **Copilot Pro, $10/mo** (~1,500 GitHub AI credits). Free excluded.
2. **OpenAI Codex as a GitHub partner agent** (the Codex-branded agent on github.com — what the
   codex-rail targets): Pro marketing blurb says Pro includes it, **but the live feature matrix
   says that row is Pro+ ($39/mo) only.** Codex VS Code "Sign in with Copilot" is Pro+/Max only.

**Honest reading:** for *an* in-GitHub agent that files PRs on the repo, **Pro at $10 is enough**
(Copilot's own cloud agent). For the **Codex** agent specifically, treat **Pro+ at $39** as the
plan the table guarantees; Pro is "try it, the Codex toggle may be missing."

**Possibly $0:** verified students/teachers/maintainers of *popular* OSS repos get Copilot Pro
free (GitHub re-checks monthly). `keithbbf-gif/cosmos` being public does not auto-qualify — must
meet GitHub's popular-maintainer bar.

### Steps on keithbbf-gif (GitHub side, nothing to do in M365)
- Turn on Copilot: github.com/copilot → Start Copilot Free; upgrade at
  github.com/features/copilot/plans → Pro (or Pro+) → Activate.
- Enable agent on repo: github.com/settings/copilot/coding_agent → repo access (all or
  `keithbbf-gif/cosmos`) → Partner agents → toggle **OpenAI Codex** (and Claude if wanted).
- Run: github.com/copilot/agents, or assign the agent on an issue, or `@`-mention on a PR.
  Needs write access (Keith owns the repo). Agent sessions burn GitHub Actions minutes + AI credits.

## Bottom line for COSMOS
The codex-rail's in-GitHub Codex agent is **gated behind a paid GitHub Copilot seat on the GitHub
account** — not obtainable via Keith's existing M365. **Money/credentials = Keith's call** (no-bats;
COW surfaces, does not purchase). Recommended: **Copilot Pro $10/mo** for a working cloud agent, or
**Pro+ $39/mo** if the Codex-branded partner agent is required; check the free-Pro eligibility path
first.

## Cited sources
- Microsoft Support — Copilot in M365 subscriptions (FAQ)
- Microsoft Support — AI credits and limits (updated 2026-07)
- Microsoft — "Meet Microsoft 365 Premium" (2025-10-01)
- Microsoft Learn — Decide which Copilot is right for you (updated 2026-08-18)
- github.com/features/copilot/plans (fetched 2026-08-26)
- GitHub Docs — About Copilot cloud agent · Managing Copilot policies · About third-party coding
  agents · OpenAI Codex · Getting free access (student/teacher/maintainer)
