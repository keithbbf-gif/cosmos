# Shipset

`classify` reports the shared `repo_disposition` for one repo-relative path and adds a why a reviewer can read. `measured_gaps` lists rules that classifier is missing. This proposal leaves the shared classifier unchanged.

## What I read

I read `CONTRACT.md`, `README.md`, and `cosmos_federation.product.repo_disposition`. I read the live checkout `.gitignore`. I listed the public tree of `keithbbf-gif/cosmos` with `gh` on 2026-10-01. I did not print file bodies. The install-key path below is REDACTED.

## Default branch and the tree I saw

The default branch is `main`. The repo is public. The recursive tree report was not truncated. It contains 2800 entries.

`live/` is not absent. The directory is on `main`.

Top-level directories: `.claude`, `.cursor`, `.github`, `builds`, `ccr`, `cosmos`, `docs`, `kdash`, `live`, `proof`, `queries`, `tests`, `tools`, `work`, `work_orders`.

`builds/cdeck` and `builds/cdm` are submodule commits. The tree listing does not expand them.

## What is already true

`repo_disposition` returns `SHIP`, `DEV`, or `DENY`. `SHIP` is the `cosmos/`, `docs/`, and `kdash/` roots, plus the root files `README.md`, `Claude.md`, `.gitignore`, and `serve.bat`. `DENY` covers an empty path, a NUL, a drive letter, a UNC or absolute path, a URL, a parent walk, the names `api_token.txt`, `install_key.bin`, `secrets.json`, `.env`, `id_rsa`, `.npmrc`, and the BU seat files in the exact spelling `BUCm.toml`, `BUcr.toml`, `BUhar.toml`, and `BUorc.toml`. It also covers the segments `live`, `node_modules`, `__pycache__`, `.git`, `_delme`, `tmp`, and `.secrets`, any path that contains both `src-tauri` and `target`, and the suffixes `.pem`, `.pyc`, `.pyo`, `.log`, `.bak`, `.apk`, `_key.txt`, `_token.txt`, `_ledger.jsonl`, and `.env`. Names that contain `api_key` or `apikey`, and basenames that start with `credentials`, are `DENY` too. Every other path is `DEV`, so a new file stays out of the installer.

The `live` segment is already `DENY`. The public `live/` tree is a commit of paths the classifier already rejects. That is a repo leak, not a missing rule.

## Public files that should have been DENY

These paths are on `main`. Gitignore excludes them, or the bakeoff note calls the same artifact local-only.

`live/` matches gitignore `/live/`. The classifier already returns `DENY` for each of these:

- `live/.cosmos-root.json`
- `live/config/_cutover_proof.py`
- `live/config/_serve_proof.py`
- `live/config/install_key.bin` REDACTED
- `live/config/install_record.json`
- `live/queue/manifests/1787485334732-740d78bf3a.json`
- `live/queue/sched_ledger.jsonl.lock`
- `live/work/1787485334732-740d78bf3a/3f31141b14/result.json`

The same tree also contains the directories `live`, `live/config`, `live/queue`, `live/queue/manifests`, `live/work`, `live/work/1787485334732-740d78bf3a`, and `live/work/1787485334732-740d78bf3a/3f31141b14`.

Gitignore excludes `work_orders/ccr/*_last.txt`. The classifier returns `DEV` for all 116 blobs:

- `work_orders/ccr/CAT_BONSAI_last.txt`
- `work_orders/ccr/CAT_BUNNY_last.txt`
- `work_orders/ccr/CAT_DOTS3_last.txt`
- `work_orders/ccr/CAT_DS41_last.txt`
- `work_orders/ccr/CAT_GEMMA31P_last.txt`
- `work_orders/ccr/CAT_LAGUNASF_last.txt`
- `work_orders/ccr/CAT_LAGUNAS_last.txt`
- `work_orders/ccr/CAT_LAGUNAXS_last.txt`
- `work_orders/ccr/CAT_LUNA6_last.txt`
- `work_orders/ccr/CAT_LUNAPRO_last.txt`
- `work_orders/ccr/CAT_MUSE12_last.txt`
- `work_orders/ccr/CAT_QWEN37_last.txt`
- `work_orders/ccr/CAT_SOLARMINI4_last.txt`
- `work_orders/ccr/CODESTRAL_HERO_last.txt`
- `work_orders/ccr/DOC_DOTS3_last.txt`
- `work_orders/ccr/DOC_GEMMA26P_last.txt`
- `work_orders/ccr/DOC_LUNA6_last.txt`
- `work_orders/ccr/DOC_LUNAPRO_last.txt`
- `work_orders/ccr/DOC_MUSE12_last.txt`
- `work_orders/ccr/DOC_MUSE13_last.txt`
- `work_orders/ccr/DOC_QWEN27P_last.txt`
- `work_orders/ccr/DS0423_HERO_last.txt`
- `work_orders/ccr/DS0731_HERO_last.txt`
- `work_orders/ccr/FIX2_DOTS3FIX_last.txt`
- `work_orders/ccr/FIX2_INKLINGP_last.txt`
- `work_orders/ccr/FIX2_NANOOMNI_last.txt`
- `work_orders/ccr/FIX2_QWEN36_last.txt`
- `work_orders/ccr/FIX2_ULTRAFREE_last.txt`
- `work_orders/ccr/FIX2_ULTRAP_last.txt`
- `work_orders/ccr/FIX3_GEMMA26F_last.txt`
- `work_orders/ccr/FIX3_GEMMA31F2_last.txt`
- `work_orders/ccr/FIX3_GEMMA31F_last.txt`
- `work_orders/ccr/FIX3_INKSMALL_last.txt`
- `work_orders/ccr/FIX3_NANOOMNI_last.txt`
- `work_orders/ccr/FIX3_QWEN27F2_last.txt`
- `work_orders/ccr/FIX3_QWEN27F_last.txt`
- `work_orders/ccr/FIX3_ULTRA2_last.txt`
- `work_orders/ccr/FIX3_ULTRAFREE_last.txt`
- `work_orders/ccr/FREE_HERO_last.txt`
- `work_orders/ccr/GEMMA31BF_HERO_last.txt`
- `work_orders/ccr/GEMMA426B_HERO_last.txt`
- `work_orders/ccr/GF38OR_HERO_last.txt`
- `work_orders/ccr/GLM_HERO_last.txt`
- `work_orders/ccr/GLM_OR_HERO_last.txt`
- `work_orders/ccr/GPTOSS20_HERO_last.txt`
- `work_orders/ccr/HY3PREVIEW_HERO_last.txt`
- `work_orders/ccr/INKLINGSMALL_HERO_last.txt`
- `work_orders/ccr/INKLING_HERO_last.txt`
- `work_orders/ccr/JUDGE_GF38_CODE_last.txt`
- `work_orders/ccr/JUDGE_LUNA_CODE2_last.txt`
- `work_orders/ccr/JUDGE_LUNA_CODE_last.txt`
- `work_orders/ccr/JUDGE_LUNA_HERO_last.txt`
- `work_orders/ccr/JUDGE_SOL_last.txt`
- `work_orders/ccr/LINGVLPAID_HERO_last.txt`
- `work_orders/ccr/LINGVL_HERO_last.txt`
- `work_orders/ccr/LING_HERO_last.txt`
- `work_orders/ccr/LLAMASCOUT_HERO_last.txt`
- `work_orders/ccr/LUNA6_HERO_last.txt`
- `work_orders/ccr/MIMO25_HERO_last.txt`
- `work_orders/ccr/MINISTRAL_HERO_last.txt`
- `work_orders/ccr/MUSE13_HERO_last.txt`
- `work_orders/ccr/NANOOMNI_HERO_last.txt`
- `work_orders/ccr/NEMO35F2_HERO_last.txt`
- `work_orders/ccr/NEMO35F_HERO_last.txt`
- `work_orders/ccr/NEMOSUPER_HERO_last.txt`
- `work_orders/ccr/NEMOULTRA_HERO_last.txt`
- `work_orders/ccr/NEXMINI2_HERO_last.txt`
- `work_orders/ccr/NEXMINI_HERO_last.txt`
- `work_orders/ccr/NEXPRO_HERO_last.txt`
- `work_orders/ccr/NORTHMINI_HERO_last.txt`
- `work_orders/ccr/POKE_BONSAI_last.txt`
- `work_orders/ccr/POKE_BUNNY_last.txt`
- `work_orders/ccr/POKE_CODESTRAL_last.txt`
- `work_orders/ccr/POKE_DOTS3_last.txt`
- `work_orders/ccr/POKE_DS0423_last.txt`
- `work_orders/ccr/POKE_DS0731_last.txt`
- `work_orders/ccr/POKE_DS41_last.txt`
- `work_orders/ccr/POKE_GEMMA26P_last.txt`
- `work_orders/ccr/POKE_GEMMA31P_last.txt`
- `work_orders/ccr/POKE_GF38_last.txt`
- `work_orders/ccr/POKE_GLM_last.txt`
- `work_orders/ccr/POKE_HY3P_last.txt`
- `work_orders/ccr/POKE_INKLINGP_last.txt`
- `work_orders/ccr/POKE_LAGUNASF_last.txt`
- `work_orders/ccr/POKE_LAGUNASP_last.txt`
- `work_orders/ccr/POKE_LAGUNAXS_last.txt`
- `work_orders/ccr/POKE_LINGVL_last.txt`
- `work_orders/ccr/POKE_LUNA6OR_last.txt`
- `work_orders/ccr/POKE_LUNAPRO_last.txt`
- `work_orders/ccr/POKE_MIMO_last.txt`
- `work_orders/ccr/POKE_MINISTRAL_last.txt`
- `work_orders/ccr/POKE_MUSE12_last.txt`
- `work_orders/ccr/POKE_MUSE13_last.txt`
- `work_orders/ccr/POKE_NANOOMNI_last.txt`
- `work_orders/ccr/POKE_NEMO35_last.txt`
- `work_orders/ccr/POKE_NEMOSUPER_last.txt`
- `work_orders/ccr/POKE_NEXMINI_last.txt`
- `work_orders/ccr/POKE_NEXPRO_last.txt`
- `work_orders/ccr/POKE_NORTH_last.txt`
- `work_orders/ccr/POKE_OSS20_last.txt`
- `work_orders/ccr/POKE_QWEN27P_last.txt`
- `work_orders/ccr/POKE_QWEN36_last.txt`
- `work_orders/ccr/POKE_QWEN37_last.txt`
- `work_orders/ccr/POKE_QWEN38F_last.txt`
- `work_orders/ccr/POKE_QWENOMNI_last.txt`
- `work_orders/ccr/POKE_SEED_last.txt`
- `work_orders/ccr/POKE_SOLARMINI_last.txt`
- `work_orders/ccr/POKE_SOLARPRO_last.txt`
- `work_orders/ccr/POKE_ULTRA_last.txt`
- `work_orders/ccr/QWEN27F2_HERO_last.txt`
- `work_orders/ccr/QWEN27F_HERO_last.txt`
- `work_orders/ccr/QWEN38FLASH_HERO_last.txt`
- `work_orders/ccr/SEED20_HERO_last.txt`
- `work_orders/ccr/SOLARPRO4_HERO_last.txt`
- `work_orders/ccr/WOMBAT_LAYER_PROBE_last.txt`
- `work_orders/ccr/WOMBAT_LUNA_last.txt`

Eighteen more bakeoff blobs sit under `work_orders/ccr/hero_pings/`. The gitignore star does not cross a slash, so that published line misses them. The classifier returns `DEV`:

- `work_orders/ccr/hero_pings/07_hy3preview_last.txt`
- `work_orders/ccr/hero_pings/08_nemo35f_last.txt`
- `work_orders/ccr/hero_pings/09_northmini_last.txt`
- `work_orders/ccr/hero_pings/10_lagunaxs_last.txt`
- `work_orders/ccr/hero_pings/11_dots3_last.txt`
- `work_orders/ccr/hero_pings/14_lingvl_last.txt`
- `work_orders/ccr/hero_pings/15_qwen37_last.txt`
- `work_orders/ccr/hero_pings/16_nanoomni_last.txt`
- `work_orders/ccr/hero_pings/17_qwen3635b_last.txt`
- `work_orders/ccr/hero_pings/18_gemma426b_last.txt`
- `work_orders/ccr/hero_pings/19_qwen27f_last.txt`
- `work_orders/ccr/hero_pings/20_lagunas_last.txt`
- `work_orders/ccr/hero_pings/21_hy3_last.txt`
- `work_orders/ccr/hero_pings/22_qwenomni_last.txt`
- `work_orders/ccr/hero_pings/23_solarpro4_last.txt`
- `work_orders/ccr/hero_pings/24_inklingf_last.txt`
- `work_orders/ccr/hero_pings/25_mimo25_last.txt`
- `work_orders/ccr/hero_pings/26_gemma431b_last.txt`

`docs/CREDENTIALS_NEEDED.md` is public and the classifier marks it `DENY`, because the basename starts with `credentials`. Gitignore only excludes `credentials*.json`, and `docs/` is otherwise a ship root. That file is a false `DENY`. It belongs in the ship set.

## What this proposal adds

`Classified` is a frozen slotted dataclass with `rel`, `kind`, and `why`. `classify` calls `repo_disposition`. An empty path is `DENY` rather than a raised refusal, so the function is total. An unknown kind becomes `DENY`. `rel` and `why` pass through `redact`, so a secret-shaped path does not survive in `repr`.

`measured_gaps` returns a fixed 16-line snapshot. Calling it does not touch the network. The lines are the holes I checked by calling the shared classifier:

- `*_env.json`, including `gemini_cli_env.json`, is `DEV` at the root and `SHIP` under `cosmos/`, `docs/`, or `kdash/`. That file is not on `main`.
- Live-state JSON names (`*_heartbeat*.json`, `*_state.json`, `mesh_state.json`, `dash.json`, `bench.json`, `chan.json`, `drive_health.json`, `spend*.json`, `*_spend*.json`, `budget_knobs.json`) are `DEV` at the root and `SHIP` under a ship root. Those basenames are not on `main`.
- `*_state/` is `DEV`.
- `_queue/` and `_lanes/` are `DEV`, and the same segments under a ship root are `SHIP`.
- `logs/` and `out/` are `DEV` unless the name already ends in `.log`. A non-log file under a ship root is `SHIP`.
- `docs/COLLECTOR.md` is `SHIP`. The file is absent on `main`.
- `.venv/`, `venv/`, and `*.egg-info/` are `DEV`, and those segments under a ship root are `SHIP`.
- `*.bak-*`, `delme__*`, and `*.PRE_*` are `DEV`, and the same names under a ship root are `SHIP`. A final `.bak` suffix is already `DENY`.
- `/trylive/` is `DEV`, and `trylive` under a ship root is `SHIP`. Only the `live` segment is `DENY`.
- `work_orders/ccr/*_last.txt` is `DEV`, and 116 such blobs are on `main`.
- `work_orders/ccr/hero_pings/*_last.txt` is `DEV`, and 18 such blobs are on `main`.
- `work_orders/ccr/hero_coders` `grade.json`, `wire.json`, and `harness_log.jsonl`, plus `work_orders/ccr/BAKEOFF70.jsonl`, are `DEV`. Those paths are absent on `main`.
- The CREW patent preload and `work_orders/ccr/CREW/OUT/ELEGANT/` are `DEV`. Those paths are absent on `main`.
- BU seat files are `DENY` only in one spelling. `bucm.toml` is `DEV` and `docs/bucm.toml` is `SHIP`.
- The `credentials` prefix denies public `docs/CREDENTIALS_NEEDED.md`.
- Editor and OS names (`.vscode/`, `.idea/`, `Thumbs.db`, `desktop.ini`, `~$*`) are `DEV` at the root and `SHIP` under a ship root.

## Refusal codes

This slot adds no refusal code. A path the installer must reject is kind `DENY`.

## How CCr lands it

CCr extends `repo_disposition` with the sixteen missing rules and narrows the `credentials` prefix so `docs/CREDENTIALS_NEEDED.md` stays on the `docs/` ship root. The peer installer copies `SHIP` only. `DEV` stays in the checkout. `DENY` stays out of the installer and out of the public tree.

CCr leaves `live/` and `live/config/install_key.bin` out of the peer package. Taking those objects off public history is a Core write. This proposal records the leak and does not rewrite history.
