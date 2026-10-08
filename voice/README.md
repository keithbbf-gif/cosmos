Applied 2026-10-07 from V:\streams\mobile onto this tree. The streams original stays in place. Nothing here writes live/, takes CCR.lease, or opens a second ledger. Live COSMOS seams stay the authority. The phone does not listen. WebSocket and WebRTC stay closed unless a transport is injected. Claude raises ANTHROPIC_OFF.

# COSMOS voice module

Propose-only client and COSMOS Code plugin. It lives here, at `V:\streams\mobile`.
It is not installed in `V:\A\Ai\COSMOS` or `V:\streams\cosmos_code`.

Core remains the authority. This package speaks `/api/v1/voice`, the CVM pull
and snapshot routes, and the control kill switch. It does not write the live
tree, does not keep a second ledger, and does not spend on its own.

## Read

- `docs/ARCHITECTURE.md` — the decision and the turn
- `docs/PHONE.md` — thin phone contract
- `docs/OPERATOR.md` — commands
- `docs/PLUGIN.md` — why it is a plugin, not a G47 door
- `research/` — Claude, Grok, OpenAI, and the transport notes
- `CONTRACT.md` — the module boundary the code follows

## Check

From this folder:

```
py -3.14 check4.py
```

That runs `py_compile`, `ruff`, `mypy --strict`, and `pytest`. A missing
checker exits 127. The compat test reads the two working trees and does not
write them.

## Run

```
py -3.14 -m cosmos_voice.cli doctor
```

`doctor` prints the plugin manifest and does not open a socket.
