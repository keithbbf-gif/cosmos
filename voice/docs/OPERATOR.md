# Operator

Run the client from `V:\streams\mobile` with `py -3.14`. The entry point is `cosmos_voice.cli`. This package is not installed into `V:\A\Ai\COSMOS` or `V:\streams\cosmos_code`. Do not install it into either tree from this folder. `pyproject.toml` names a script `cosmos-voice`. That script is not how this tree is run.

`cli.main` accepts five verbs: `doctor`, `say`, `status`, `kill`, and `queue`. This note states the contract. It does not record a run.

```
py -3.14 -m cosmos_voice.cli doctor
py -3.14 -m cosmos_voice.cli say --base <url> --transcript <text>
py -3.14 -m cosmos_voice.cli status
py -3.14 -m cosmos_voice.cli kill
py -3.14 -m cosmos_voice.cli queue
```

`doctor` prints `manifest()` and exits 0. It does not touch the network.

`say` requires `--base` and `--transcript`. It is the call that posts a transcript to `POST /api/v1/voice`. A voice read waits up to 70 seconds. Every other Core call waits 8 seconds. The contract names no further flags for `say` beyond the bearer exception below.

`status` reads control. `GET /api/v1/control?client_id=` returns `effective` with `pause`, `mic_off`, and `clear_queue`. Missing or unreadable control blocks. `blocked` is true when `pause` or `mic_off` is true, or when no poll has been applied.

## Bearer over HTTP

A bearer on an `http://` base raises `BEARER_OVER_HTTP`. Pass `--allow-http-bearer` to set `allow_bearer_over_http`. `https://` is allowed. A blank bearer is allowed. Do not print bearers, API keys, or kill tokens. This package does not store a bearer in a settings file.

## Kill

`kill` only mutes. It posts `{client_id, token}` to `POST /api/v1/kill`. That route may be unauthenticated. The effect is mic off. It does not turn the mic back on.

Resume is `POST /api/v1/control/resume` with body `{client_id}`. That route is bearer-authenticated. The CLI does not call it. Turning the mic back on is a Core route, separate from kill.

## Road queue

`queue` files a drop. It does not run one.

`RoadQueue` appends JSON lines at `<root>/road.jsonl`. `enqueue` redacts string values before the write. `mark_sent` rewrites the file in place and sets `sent: true` on that id. It never deletes a line and never opens a socket.

`POST /api/v1/voice_loop` with `{action: drop|new_sop, mouth, task}` files a drop. It does not run an agent. When Core cannot be reached, the turn is `UNREACHABLE`. The drop may sit in the road queue. The queue does not execute it.

## 4C

From this folder, the check is:

```
py -3.14 check4.py
```

It runs `py_compile`, then `ruff`, then `mypy --strict`, then `pytest`. A missing checker is `MISSING` and the process exits 127. Pytest exit 5 is `NO_TESTS` and blocks. Any status other than `PASS` blocks. Each checker times out at 180 seconds.

This note does not record a 4C result. Run the command to get one. A passing run still does not install this package into the live tree.
