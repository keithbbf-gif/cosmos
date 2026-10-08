# COSMOS Code plugin

This module is a COSMOS Code plugin. It is not a G47 door.

G47 door ids are a closed set. The table in `V:\streams\cosmos_code\harness\G47\g47\doors.py` is `cosmos-code`, `opencode`, `pi`, `dsh`, `codex`, `copilot`, `grok`, `openrouter`, `vertex`, `claude`, `hermes`, `antigravity`, and `none`. A spec whose id is not in that set raises `SPEC_UNKNOWN_DOOR` at load. `grok` and `codex` are coder seats in that table. Voice is not one of them. A voice module that pretended to be a new door would be `SPEC_UNKNOWN_DOOR`. This plugin does not add a door id and does not edit that table.

`open_door` in this package is a separate, smaller table: `core`, `grok`, `openai`, and `claude`. `grok` and `openai` raise `NO_KEY` without a key and `NOT_COMPOSED` when no transport is injected. They do not open a socket themselves. `claude` always raises `ANTHROPIC_OFF` and does not build a client. That refusal is not a request to seat the G47 `claude` door. Anthropic stays off the route. The Claude phone app is a research source only.

The plugin is a client of Core. It is not a second Core, not a second ledger, and not a second spend gate. A spoken turn becomes a kernel action only at `POST /api/v1/voice`.

## manifest()

`manifest()` returns this record. `doctor` prints it and does not use the network.

- `id`: `cosmos-voice`
- `plugin_of`: `cosmos-code`
- `writes_live_tree`: false
- `authority`: `core-http-client`
- `anthropic`: `off`
- layers: role `file`, model `none`, harness `native`, wrapper `file`, skills `none`, tools `native`, enviro `file`, mission `file`
- tools: `voice.say`, `voice.status`, `voice.kill`, `voice.queue`

`writes_live_tree` false is the write rule. Calling the plugin does not write `V:\A\Ai\COSMOS`. `compat.probe` reads source text only. It does not import the live tree. Its rows are `voice_route`, `cvm_routes`, `max_transcript`, `known_kinds`, `code_package`, and `code_layers`. Each row is `{name, status, detail}` with status `PASS` or `MISSING`.

`anthropic` `off` matches `ClaudeDoor`. A door with that name raises and does not build a client.

## The four tools

`register` adds the four names to a dict the caller supplies. Each callable takes a `CoreClient` and plain arguments. None of them read the environment for secrets.

- `voice.say` sends one transcript through the Core voice route.
- `voice.status` reads the control view (`pause`, `mic_off`, `clear_queue`).
- `voice.kill` mutes. It posts `{client_id, token}` to `POST /api/v1/kill`. It does not resume.
- `voice.queue` files a road drop. It does not run the drop and does not run an agent.

Resume stays on Core: `POST /api/v1/control/resume` with `{client_id}`, bearer-authenticated. The tools do not call it.

## Later registration

Leave this folder at `V:\streams\mobile`. Do not copy it into `V:\A\Ai\COSMOS`, and do not copy it into `V:\streams\cosmos_code`, until Keith accepts a landing.

A later Chief Coder registers it without that copy. Code supplies the tool dict. CCr imports `manifest` and `register` from `cosmos_voice.plugin` in this tree, checks the record above, and calls `register` so the four tools are added. That call does not write the live checkout, does not add a G47 door id, and does not change `writes_live_tree`. Authority stays `core-http-client`.

Copying the folder into `V:\A\Ai\COSMOS` is a separate landing. It waits until Keith accepts it. One CCr writes that tree, after review. Until then the live tree stays unmodified and this package stays here.
