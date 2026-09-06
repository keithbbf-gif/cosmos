# MOTIF Step 1 COMPARE — finish cDeck as COSMOS_2 backend

Prompt: `work_orders/ccr/CREW/IN/20260906_MOTIF1_CDECK_COSMOS2.md`
Fired: Bing SERP, Cloudflare AI Playground, Copilot CLI (LIVE rails 2026-09-06).
Not dump-dom. Occupancy already bound — not a re-pick of surface merge.

## Lanes

| Lane | Result |
|---|---|
| Bing SERP | **ok** 18540 chars. Hits: `openworklabs.com`, `github.com`, name collision `openwork.com`. No merge-how-to body in a11y headings. |
| Cloudflare AI | **partial** 12760 chars. Started: “I'll research OpenWork architecture…” then “available libraries don't include OpenWork documentation.” Snapshot cut mid-run. Leftover prior `PONG_DOM_4` in the same playground thread. Not a finish recipe. |
| Copilot CLI | **ok** rc=0 3938 chars (`copilot.md`). Web fetch of the two cited URLs **permission denied**; GitHub MCP read README + code search (`command-palette-recents.ts`, `use-ui-control-mailbox.ts`). |

## Copilot (usable return)

- **Next honest link is cDeck → Core HTTP `:8770`**, not stuffing OpenWork into cDeck. OpenWork docs describe desktop workspace + remote MCP `https://api.openworklabs.com/mcp/agent`, **not** COSMOS Core. Whether Core’s API is “compatible” is **UNKNOWN from OpenWork sources** — COSMOS already has `/api/v1/*`.
- **C0 focus/launch and Recents click are UI navigation**, not the integration. Repo has command-palette recents; **no evidence** they bind COSMOS Core.
- **OpenWork UI-control mailbox** (`POST /experimental/ui-control/request`, `GET …/pending`) is **OpenWork’s own server poll**. Not proven as a COSMOS `cm\` bridge. Do not persist that bearer (already bound).
- **Do not use OpenWork MCP as the Core link** unless Core is deliberately exposed as an OpenWork capability. Skills/plugins stay consume-in-OpenWork.
- **Finish sequence:** keep two windows; cDeck backend calls authenticated Core HTTP; paint health/nodes/surfaces/rails; C0/mailbox optional UI. Subtract iframe / second Core / skill clone.

## This TUI

MOTIF Step 1 is on disk. Does **not** start Gitur BUILD from this compare. COSMOS Core routes are already the contract (`GET /status /health /spend /rails /events`, recents, C0). Grok.com / ChatGPT / Perplexity still AUTH on the COSMOS Chrome profile.
