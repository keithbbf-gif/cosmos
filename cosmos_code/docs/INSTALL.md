# Install COSMOS CODE from this repo

A new machine needs Python 3.11 or newer. The three packages have no third-party
runtime dependencies. Optional doors are not downloaded by this install.

```
py -3.14 install.py
```

That writes `installs/LOCAL.toml` for this machine and prints which doors are
present. The same check is `py -3.14 -m g47 doctor` after the packages are on
the path.

Editable installs, from this directory:

```
py -3.14 -m pip install -e harness/G47 -e cosmos_harness -e product
py -3.14 -m pytest -q harness/G47/tests cosmos_harness/tests product/tests
```

`installs/DOORS.toml` is the list a clone ships. `installs/LOCAL.toml` is
generated and is not part of the clone. Seat evidence under
`harness/G47/seats/all/` and the vendor source dumps are local. They are not
required to install.

Optional doors, after the catalog says they are missing:

- Codex: `npm install -g @openai/codex`. OpenRouter pins set `wire_api=responses` on the argv. Copy `installs/codex-openrouter.config.toml` to `%USERPROFILE%\.codex\cosmos-openrouter.config.toml` if you want that profile. The key stays in `OPENROUTER_API_KEY`.
- DeepSeek harness source: `git clone --depth 1 https://github.com/deepseek-ai/deepseek-harness`. On this machine the tree is `V:\deepseek-harness`. The CLI is `dsh.cmd`.
- Claude, OpenCode, pi, Cursor, and Gemini are named in `DOORS.toml`. A missing binary is missing. It is not a pass.

Do not start `grok.exe`. Do not write a key into a file in this repo. Do not copy this tree into `live/`.
