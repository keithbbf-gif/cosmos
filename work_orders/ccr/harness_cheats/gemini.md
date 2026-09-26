# CHEAT — Gemini / Vertex

GF38 door. Two entries, one model family. No `--harness` flag exists on this `gemini.cmd`.

- **CLI:** `gemini.cmd -m <model> -p <prompt>`. Flags seen: `-m`, `-p/--prompt`, `--approval-mode`, `--allowed-tools` (deprecated). Runner maps L3 to this binary. Do not pass `--harness`.
- **Vertex:** Kelly `vertex-coding` (`orders.ggn`), failover Joanna on error. `VertexRail(key_file, spec).dispatch(...)`. There is no `from_config`. Set `role=coding`.
- **Tools:** `generateContent` had no tools array. The caller files the reply through PathJail. Do not claim the model wrote the file.
- **Wrapper:** prompt carries `WRAP.md` then `TASK.md`. `GEMINI.md` in cwd is the CLI stand-in (no `--system-instruction` on this install).
- **COSMOS CODE:** caller write through PathJail, not the model.

## Not

`_fire_gf38` tab farm. OpenRouter as this door. Treat a saved mouth file as a tool call.
