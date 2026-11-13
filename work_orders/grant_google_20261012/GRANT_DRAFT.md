# COSMOS - Google grant application draft (DRAFT, NOT SUBMITTED)

Date: 2026-10-12. Status: outline for Keith to review. Nothing has been submitted.

## 1. Target program

- No Google program called a "$350,000 challenge grant" was found. The $350,000 figure matches the **Google for Startups Cloud Program, AI startup track (Scale tier)**.
- Official pages: https://cloud.google.com/startup/ai , https://cloud.google.com/startup/faq , https://cloud.google.com/startup/early-stage
- Award: up to $350,000 in Google Cloud credits over 2 years. This is credit, not cash. Year 1 covers 100% up to $250,000 for AI-first startups. Year 2 covers 20% up to another $100,000. Credits cover Google Cloud services and Gemini/Gemma. They do not cover third-party models or Marketplace offerings.
- Eligibility, from the pages: the startup builds on Gemini or Google's agent platform as the core of its product, is AI-first, has raised Pre-Seed/Seed within 5 years or Series A within 12 months from an institutional investor (SAFEs count), was founded recently, and has received no more than $5,000 in Google Cloud credits before. Google decides eligibility at its discretion.
- Deadline: rolling application. No deadline is listed.
- Required materials: the pages list no pitch deck or demo. The application form asks for company and funding details. Confirm the field list on the live form.
- Fit: weak on funding. COSMOS has no documented company entity or institutional funding. The lower Start tier (up to $2,000 in credits) or a funding round first may be needed. Keith to decide.

## 2. Project name

COSMOS - Carry-Over State Mesh Operating System.

## 3. Summary

COSMOS is an operating system that coordinates AI models from several vendors on the same work. It treats carry-over state as the main object: what a session must keep after it ends. One resident Windows service, COSMOS Core, is the single authority. It runs the scheduler, the spend gate, the lease arbiter, and a hash-chained, signed event ledger. Workers run in private workspaces and publish only through a fenced commit gateway. A test harness seats judge models against coder models and records each result. (Source: README.md, COSMOS_OVERVIEW.md)

## 4. Problem

Multi-model AI work fails at session boundaries, not on compute. The predecessor system (BTS_MESH, 139 modules) lost corrections between sessions. Its scheduler ran eight-day-old code. Its handoffs stated three different counts of one fact. A verifier there had never run. (Source: README.md)

## 5. Solution

- Single-writer ledger: append-only, hash-chained, signed JSONL. Everything else is a rebuildable projection.
- Spend gate that reserves, then denies or calls, then settles. It denies before spending instead of reporting after.
- Vendor-plural review: models from different families check each other's work.
- Hero-pack seats: each model seat gets 8 layer files (role, pin, harness, wrap, skill, tools, env, task).
- Executable gates: a check that never ran counts as a failure.
(Source: COSMOS_OVERVIEW.md section 2, README.md)

## 6. Why COSMOS qualifies

- AI is the core of the product, not an add-on.
- It already calls Gemini 3.8 Flash on Vertex AI through `cosmos_vertex_rail`. A one-chunk test on 2026-10-12 read 207,801 input tokens in one call. (Source: I:\harness_update\flash_chunk_test_20261012_1922\)
- Credits would pay for Vertex/Gemini seats in the judge/coder harness.
- Gap: the funding and company requirements are not met on paper. See section 10.

## 7. Team

- Keith (builder and operator). [PLACEHOLDER: Keith to add full name, role, background, company entity.]
- Jack and Grayson are named as future installers on cold machines. Their roles are not documented. (Source: COSMOS_OVERVIEW.md section 1)

## 8. Traction evidence

- Core code: 253 .py files, about 89,400 lines in `cosmos/`. Core live at 127.0.0.1:8770. Ledger seq about 15,513 as of 2026-09-19. (Source: COSMOS_OVERVIEW.md, dated 2026-10-01; not re-measured)
- Feature status: 46 DONE, 16 PARTIAL, 3 BLOCKED, 5 ABSENT. (Source: Plan4Nov-SP4.md)
- First product: Open Sessions, `builds/open_sessions/Open_sessions.py`, `/api/v1/recents` live. (Source: Plan4Nov-SP4.md)
- Hero run 2026-10-08: 25 judges x 86 coders = 2,150 pairs tried, 1,034 graded, 21 blocked, 1,383 recorded as full seat. (Source: I:\harness_add\_hero_run_20261008\cross_status.json) UNVERIFIED: a one-judge digest found judge J15 never met the strict first-line rule, so 1,383 may count loosely parsed replies. Recount before citing. (Source: I:\harness_update\flash_chunk_test_20261012_1922\DIGEST.md)
- Billing control: the GF38 hero pack now bills a single named Vertex account, with no fallback to other wallets. (Source: work_orders\ccr\hero_gf38\DUD.toml, L7_ENVIRO.md)
- Packaged harness: I:\harness_claude, described as cosmos-code 0.2.0. UNVERIFIED in this pass.

## 9. The ask

Up to $350,000 in Google Cloud credits over 2 years, used for:
- Gemini on Vertex AI for judge and coder seats in the harness.
- Cloud storage and compute for the ledger, content store, and test runs.
[PLACEHOLDER: Keith to set a 24-month budget split.]

## 10. Open gaps and to-do

1. Funding and entity: the AI track needs institutional funding (Pre-Seed/Seed within 5 years or Series A within 12 months). None is documented. Confirm or consider the Start tier.
2. Prior credits: confirm that total Google Cloud credits received across Keith's accounts are not above $5,000. The trial credits on the Joanna and Kelly Vertex accounts may count.
3. Recount the 1,383 full passes under the strict first-line rule.
4. One-command install: README says "Installable by a peer on a cold machine" is a requirement, and README status says "Pre-implementation". No working one-command install was confirmed.
5. Nov 1 launch, SpiderCaster, Token Center: Plan4Nov-SP4.md targets Oct 31 for core work. No SpiderCaster or Token Center launch plan was confirmed in this pass. HARNESS_PLAN.md's 7-role SpiderCaster has no evidence yet.
6. Update stale numbers in COSMOS_OVERVIEW.md (dated 2026-10-01).
7. Add users or customers. No external users are documented.
8. Write a short demo script and record a demo, in case the form or a Google contact asks for one.
