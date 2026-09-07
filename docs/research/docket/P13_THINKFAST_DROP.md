# P13 — Voice / Chatbox drop box → OS daemon → agent → timestamped audit

**Kind:** system / method. **Status:** **FILE** (takes the 12th $65 slot; P12 Crucible stays HOLD).
**Fee:** US provisional micro $65.
**DEFINE:** `work_orders/ccr/DEFINE_THINKFAST_DROP.md`.
**In-tree:** `docs/WORK_ORDER_SOP.md`, `docs/WORK_ORDER_SPEC.md`,
`cosmos/cosmos_sgh_drop_ingest.py` (schtask **COSMOS SGH Drop Ingest**),
Work-Order Runner, `work_orders/drop/`, Grok Voice Think Fast 2.0 as the mouth
(`grok-voice-think-fast-2.0`). Keith 2026-09-07: *that's new.*

## What it is (in-tree)

An operator (voice or Chatbox) who **cannot see the live runtime root** writes a
typed JSON work order to a **GitHub folder** that they *can* reach. A **native
system daemon** on the COSMOS host monitors that drop box, files the order into
the live bucket, **calls an agent** named in the order, **collects the Output
file**, and **records results with timestamps and an audit trail**. GitHub files
are never deleted. The LLM does not poll itself. GitHub Actions is not the
executor.

Measured loop: Think Fast 2 (phone) → `keithbbf-gif/cosmos` `work_orders/drop/*.json`
→ ingest clock (~15s) → `live/state/work_orders/bucket/` → runner creates Agent
session WRITE-PRIVATE → Output exists = DONE → `assigned/` + heartbeat JSON +
ISO timestamps. CCr `--accept` / `--reject` still the only live-tree writer.

## Problem / scar

If the human is the wire, voice work dies when the chat dies. If GitHub Actions
runs the job, the audit is a vendor log and the agent is not COSMOS-fenced. If
the phone could write `live/`, that is a second writer on the runtime root
(two-writer deletion scar).

## Written description

1. Inbox the client can reach = GitHub path `work_orders/drop/` on a named repo/branch.
   Not the live tree. Not repo root. One JSON object, six fields (Agent, Context
   source, Task, Target & scope, Timestamp, Output). Filename Windows-legal.
2. Native OS clock (Windows Scheduled Task + pythonw daemon) lists the drop,
   parses, files DROPPED into the live bucket. Does not execute the Task.
3. Seen-set is append-only (sha). GitHub objects stay. Seen-set is not authority.
4. A second native runner picks DROPPED, **creates a session of the named Agent**,
   passes Task + read-only context, WRITE-PRIVATE to Output only.
5. Collect: DONE iff the Output file exists; else FAILED. File the order into
   the assigned/done folder with timestamps.
6. Audit: daemon heartbeats (`last_run_epoch`), ISO timestamps on the order,
   ledger events when Core is composed. Dashboards are projections.
7. Voice STS (Think Fast 2.0) is one mouth. Chatbox is the same inbox. Return
   path may be Drive so the phone can read without `live/`.
8. Dispose of live-tree writes remains one CCr. The daemon does not hold the pen.

## Already public

Work-order SOP and `work_orders/drop/` exist on public `cosmos` after 2026-08-23.
Voice loop named in wishlist / routing (local + later commits). GitHub date for
the *method as a voice→daemon→agent→audit loop* is thinner than Core's 2026-08-23
architecture dump — FILE before another public article.

## Prior art to name (crowding, not a novelty opinion)

GitHub Issues / PR templates as inbox; GitHub Actions on push; ChatOps (Slack →
Jenkins); cron + file drop; n8n / Zapier / Make webhooks; Temporal / Airflow /
Luigi; Siri Shortcuts / Alexa skills calling HTTP; Twilio **US20250165890A1**
(planner–critic–executor); voice-to-ticket SaaS. **Combination not found as a
blocking US claim set:** voice/chat client that **cannot** mount the authority
root drops a **typed work order on GitHub**; a **host OS daemon** (not Actions)
monitors, **instantiates a named AI agent**, collects a **single Output file** as
DONE, and writes a **timestamped COSMOS audit** while **never deleting** the
GitHub drop and **never** letting the agent write the live tree.

UNKNOWN unpublished apps. DOM research of Patent Public Search still owed.

## What this is not

Not GitHub Actions. Not a mobile backend. Not a mobile frontend. Not CVM.
Not "we invented work queues." Not cron. Not the MOTIF loop itself (P01) and
not the ledger primitive (P07) — this is the **ingress + execute + audit
path** that uses them.

## Suggested independent idea

A voice-reachable GitHub drop box, executed by a local OS daemon that creates
a fenced agent, with DONE = Output file and authority = timestamps + signed
ledger, operator out of the execution wire.
