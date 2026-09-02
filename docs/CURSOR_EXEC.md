# Cursor Execution for Cosmos Work Orders

## Goal
Use Cursor Cloud Agents (Composer 2.5) as an alternate executor for work orders dropped in work_orders/drop/.

## Why Cursor
- Native GitHub app: clones repo, creates branches, opens PRs, leaves review comments.
- Cloud Agents can run on schedules or GitHub events (PR opened, issue comment, workflow completed, webhook).
- Bugbot reviews the resulting PRs automatically.
- AGENTS.md is read natively, so conventions and verdict spec are picked up without extra config.

## How to trigger
1. Keep work orders as JSON files in work_orders/drop/ (same format as Grok Code).
2. Preferred: convert each work order to a GitHub Issue titled "WO: <task>" with the JSON in the body, then label it `cursor-execute`.
3. Cursor Automation trigger: Issue label changed (label = cursor-execute) OR scheduled poll of work_orders/drop/.
4. Alternative: webhook from the desktop daemon POSTing the work-order JSON to the Cursor automation endpoint.

## Known limitation
Cloud Agent sandbox token historically lacks Issues read/write scope even when the GitHub App has it. Workaround: add a fine-grained PAT named GH_TOKEN (or GITHUB_TOKEN) to the Cloud Agent environment secrets with Issues: Read and write. Without it, paste the work-order content directly into the agent prompt instead of asking it to fetch the issue.

## Output contract
- Cursor opens a PR against main (or the branch named in the work order).
- PR title: "WO: <task>" matching the work order.
- On merge or close, write a verdict back to the work order file (or a linked issue comment) using the VERDICT_SPEC.md format: status, reason, objection with file+line+fix, timestamp.
- Bugbot should be enabled on the repo so every Cursor PR gets an automatic review.

## Family note
Cursor Cloud Agents run on Cursor's in-house Composer 2.5 (Moonshot Kimi K2.5 base). Not Claude, not GPT. Bugbot is the same family.

## Recommendation
Keep Grok Code 4.6 as the primary builder. Use Cursor as a parallel executor or review gate — drop the same work order, let both race, compare verdicts.
