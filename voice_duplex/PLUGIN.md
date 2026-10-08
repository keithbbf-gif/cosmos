# COSMOS Code plugin

Voice is staged beside COSMOS Code, not inside it.

`V:\streams\cosmos_code\harness\KEITH_20260930_STANDALONE.md` says the app takes plugins later and names two: SESSIONS and CLUSTERS. This package does not add itself to that list and does not edit that file. `tests/test_trees.py` reads the file and checks those two names are still there, and checks that `cosmos_voice_duplex` is not under `product/` or under `V:\A\Ai\COSMOS\cosmos`.

## Host

A host implements `CodeHost`:

- `on_user_text`
- `on_assistant_text`
- `call_tool`
- `spend_snapshot` (read-only)

`VoicePlugin.attach(session)` points the session callbacks at the host and registers three tools:

| Tool | Confirm | What it does |
| --- | --- | --- |
| `status` | no | Returns the host spend snapshot. Does not change a balance. |
| `check` | no | Calls `host.call_tool("check", ...)`. |
| `propose` | yes | Returns a proposal record only after the spoken confirm gate says yes. |

Handlers return JSON strings. They do not write files, `live/`, or the product tree. The module does not import `cosmos_code`.

## Spend sidebar

If Code shows a voice spend line, it should read `spend_snapshot`. That snapshot is not a ledger and not TokenCTR. The Core spend gate remains the authority when a production hook is injected.

## Bind to live voice

`cosmos_voice_duplex.bind.probe(path)` parses `cosmos_voice.py` and returns `SPOKEN_MAX`, `MAX_TRANSCRIPT`, `CONFIRM_TTL`, the verb sets, and the `handle` argument names. It uses `ast`. It does not import Core.

`CosmosVoiceBind(handle).attach(session)` installs that handle on the session gate. The handle is the live `VoiceMode` only when a CCr session built one. This package never constructs it and never opens the ledger.
