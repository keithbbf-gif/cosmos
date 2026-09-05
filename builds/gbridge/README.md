# gbridge — synchronous COW ⇄ GrokBot-team ask (T1 slice 1)

Design: `docs/T1_ARCH.md`. One blocking `ask()` returns a structured `Answer` or a
**typed refusal**. Transports are injected: `MailboxTransport` is primary (real team
identity via `to_gbot/` / `from_gbot/` files), `XaiApiTransport` is the API-second
fallback (refuses in this slice). Python 3.14 stdlib only; no third-party deps.

## Run

```
py -3.14 -m pytest                              # from builds/gbridge; pytest wraps the selftest
py -3.14 builds\gbridge\test_gbridge.py         # selftest suite, no network
py -3.14 builds\gbridge\gbridge.py selftest     # loopback (green log — NOT stage 6)
py -3.14 builds\gbridge\gbridge.py ask "question for the team" --root <mailroot> --register
py -3.14 builds\gbridge\gbridge.py gate --root builds\gbridge\mail --live-root V:\A\Ai\COSMOS\live
```

`--root` is the mail root, handed in — gbridge never resolves paths itself.
`--register` creates `to_gbot/` and `from_gbot/` (explicit, one-time). The GrokBot
team answers by writing `from_gbot/<request_id>.json` in the wire shape (see T1_ARCH §5).
Prefer `MailboxTransport.write_reply(request_id, status, answer)` (atomic tmp→`os.replace`);
`poll` still treats a present-but-unparseable file as "not yet" until the deadline.
Refusals are `GBridgeError` with a `RefusalKind` (a `StrEnum`; `kind == "TIMEOUT"` still holds).
The wire key `body_sha256` is the SHA-256 of the `text` (request) or `answer` (reply) field,
not of the whole JSON document.

`selftest` is a loopback green log. Stage 6 is `gate`: a real mailbox round-trip that
writes `builds/gbridge/STAGE6_GATE.json`. The proof is that file's `live_value` /
`emitted` — never the process exit code. `--live-root` is handed in; the module
reads `.cosmos-root.json` and refuses if `system` is not `COSMOS`.

## Not in this slice

MCP wrapper (`gbridge_ask` as a native COW tool), `collect` verb for late replies,
live xAI HTTP wiring, ledger-recorded ask/answer facts.
