# DEFINE — ThinkFast drop-box daemon (MOTIF stage 1)

**Keith 2026-09-07.** Frozen prompt. Verbatim to every model. Do not paraphrase.

## WHAT

A spoken (or Chatbox) query becomes a **JSON work order** dropped on **GitHub**
(`work_orders/drop/`). A **native OS daemon** (not GitHub Actions, not the LLM)
monitors that drop box, files the order into the live bucket, **creates an agent
session**, collects the agent's **Output** file, and records **timestamps plus an
audit trail** (heartbeat, DROPPED/PICKED/DONE, ledger). The phone never sees
`live/`. CCr still disposes live-tree writes.

Loop as run: **Grok Voice Think Fast 2.0** → GitHub drop → `cosmos_sgh_drop_ingest`
(schtask **COSMOS SGH Drop Ingest**) → **COSMOS Work-Order Runner** → agent →
Output → assigned folder / Drive / CCr. Voice may read Drive for the return.

## WHY

Keith cannot be the wire. Voice on a phone can write GitHub and cannot mount the
runtime root. GitHub Actions would run in the vendor cloud on a push; this clock
runs on the **operator's Windows box**, creates a **named agent**, and the
authority of "what happened" is COSMOS timestamps + ledger, not a green Actions log.

## ACCEPTANCE (live emit)

- Drop `wo-<stamp>.json` (six fields, Windows-legal name) on GitHub `work_orders/drop/`.
- Ingest daemon lists it, parse_order, drop_order into `live/state/work_orders/bucket/`.
- GitHub file is **never deleted**; skip is append-only `github_seen.json` (not authority).
- Runner creates the Agent named in the order, WRITE-PRIVATE (Output only).
- DONE = Output file exists; FAILED = no Output. Assigned folder is the done folder.
- Heartbeats and ISO timestamps on ingest and runner. Ledger events for dispatch when composed.
- Phone/Voice is the mouth, not a mobile backend or frontend.

## OFF-LIMITS

Do not rebuild CVM. Do not ship `cosmos-voice.apk` as the product (draft seed only).
Do not make GitHub Actions the executor. Do not invent a second drop desk.
Do not write `V:\Ai`. Do not file USPTO from this TUI. Do not auto-MOTIF Forge.

Consumer ChatBot phone (named OpenRouter `:free` picker, funnel to Desktop)
is a **separate** DEFINE: `DEFINE_CHATBOT_PHONE.md`. Same inbox. Not this
operator Voice path.

## THIS TEXT

Copy this file into every lane's prompt.
