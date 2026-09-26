---
name: dsh-headless-diff
description: Use when coding on deepseek-v4-flash via dsh --profile headless. Trigger on Gitur WO, patch, headless job. DeepSeek Harness: skills load by name; do not dump 70 tools.
---
# DeepSeek Flash — dsh headless

1. Via = `dsh --profile headless`. DSH_HOME = V:\A\Ai\COSMOS\live\work\dsh-home. Not `dsh web`.
2. Official `DEEPSEEK_API_KEY` preferred. Free pair still uses **dsh** (not OpenCode): set `DEEPSEEK_BASE_URL=https://openrouter.ai/api/v1` and the OpenRouter key as `DEEPSEEK_API_KEY`, model `deepseek/deepseek-v4-flash-0731:free`. Do not switch the harness to OpenCode.
3. The reply is python only. Kind-gate in the worktree. No git push/merge. No grok.exe.
4. Load this skill by name if the harness offers `skill`. Do not enable the full 70-tool dump.
5. Partner GLM (paid-low mix). ortho/mag UNMEASURED until a tensor cell exists.
6. MAX after PREFIX; 20% window margin; OPTIMUM floats.
