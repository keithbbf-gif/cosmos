# GHX stage hygiene — mesh-repo (third copy)

Snapshot is not the pen. Do not push. Do not commit. Do not run TidyUP.
This file is inspect-only output. Restore/unstage commands below are for Keith/QA to run later. Snapshot did not execute them.

## Scope

- Inspected copy: `V:\Ai\mesh-repo` (exists). Fallback `V:\Research4\Ai\mesh-repo` was not used (missing).
- This is the THIRD copy of the mesh — not the live tree, not GitHub HEAD.
- Live trees were not written: `V:\Ai\BTS_MESH` and `V:\Research4\Ai\BTS_MESH` were not touched.
- Legal/ was not opened, listed, or read. One staged PUA path *looks like* a Legal path-as-filename; only the index name is recorded here.
- No tokens, secrets, API keys, or `.env` contents are printed.

## Git facts

- Branch: `main`
- HEAD sha: `fb6c53d78f7b905ed74c914565fd8b0964abdf29`
- Last commit subject: `full mesh snapshot 2026-08-16 - private repo, everything ships: modules, registries, ledgers, live state`
- Staged change count (`git diff --cached --name-only`): 306
- Unstaged modified tracked files (`git diff --name-only`): 0
- Untracked (`git ls-files --others --exclude-standard`): 1

## .env status

QA asked to confirm `.env` is unstaged. Actual fact:

| path | index (`git ls-files`) | staged delta | unstaged modified | untracked | HEAD tree |
|---|---|---|---|---|---|
| `BTS_MESH/.env` | absent | no | no | **yes** (`??`) | absent |
| any other `.env` / `.env.*` | none | none | none | none | none |

**Confirmed: `.env` is unstaged.** It is untracked only (`?? BTS_MESH/.env`). It is not in the index and not in HEAD. Do not `git add` it.

## Staged literal-backslash / PUA junk — lock/board (second universes)

These are path-as-filename artifacts (colon = U+F03A, backslash = U+F05C). They are **not** the real modules and **not** the live files.

Real modules (DO NOT restore/unstage/exclude):

- `BTS_MESH/bts_board.py` (staged; keep)
- `BTS_MESH/tree_lock.py` (staged; keep)

Real live files (not in this repo stage as those names; DO NOT touch):

- `V:\Ai\_board\board.json`
- `V:\Ai\_queue\tree_lock.json`

Junk lock/board staged paths (Python repr / unicode-escape):

1. Lock/board junk A
   - repr: `'BTS_MESH/V\uf03a\uf05cAi\uf05c_board\uf05cboard.json'`
   - unicode-escape: `BTS_MESH/V\uf03a\uf05cAi\uf05c_board\uf05cboard.json`
   - basename is the entire fake `V:\Ai\_board\board.json` (PUA). Second board universe.

2. Lock/board junk B
   - repr: `'BTS_MESH/V\uf03a\uf05cAi\uf05c_queue\uf05ctree_lock.json'`
   - unicode-escape: `BTS_MESH/V\uf03a\uf05cAi\uf05c_queue\uf05ctree_lock.json`
   - basename is the entire fake `V:\Ai\_queue\tree_lock.json` (PUA). Second lock universe.

## Other staged PUA / literal-backslash junk (same encoding, not lock/board)

3. `'BTS_MESH/V\uf03a\uf05cAi\uf05cLegal\uf05cWARGAME/_RUN_LOG.txt'`
   - unicode-escape: `BTS_MESH/V\uf03a\uf05cAi\uf05cLegal\uf05cWARGAME/_RUN_LOG.txt`
   - Index name only. File was not opened. Legal/ was not listed or read.

4. `'BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05c00_WORKING\uf05cSGH_returns/SGH_2026-07-31_194710_47d96b.md'`

5. `'BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05c00_WORKING\uf05cSGH_returns/SGH_2026-07-31_195011_781fa9.md'`

6. `'BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05c00_WORKING\uf05cSGH_returns/SGH_2026-07-31_195103_781fa9.md'`

7. `'BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05cpapers\uf05cGrok_on_this\uf05c+Papers/A unified secondary electron cut-off presentation and common mistakes in photoelectron spectroscopy.pdf'`

8. `'BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05cpapers\uf05cGrok_on_this\uf05c+Papers/Effects, determination, and correction of count rate nonlinearity in multi-channel analog electron detectors.pdf'`

9. `'BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05cpapers\uf05cGrok_on_this\uf05c+Papers/_oagrab_manifest.json'`

## Other staged secrets / junk globs

Checked staged names for: `.env`, `.env.*`, `gemini_cli_env.json`, `client_secrets.json`, `credentials.json`, `token.json`, `*.pem`, `*.key`, `*service-account*.json`, `*.lock` (not `tree_lock.py`), `~$*`.

**None of those names are staged.**

`BTS_MESH/.env` is untracked only (see above). Leave it untracked.

## Restore / unstage commands (NOT executed by Snapshot)

Prefer `git restore --staged` so the junk drops from the index without deleting the real modules or the live board/lock files.

PUA characters cannot be typed reliably in cmd. Use Python to pass the exact index paths. Run from any directory on the Windows machine.

### 1) Lock/board junk only (minimum)

```powershell
python -c "import subprocess; repo=r'V:\Ai\mesh-repo'; junk=['BTS_MESH/V\uf03a\uf05cAi\uf05c_board\uf05cboard.json','BTS_MESH/V\uf03a\uf05cAi\uf05c_queue\uf05ctree_lock.json']; subprocess.run(['git','-C',repo,'restore','--staged','--']+junk, check=True)"
```

Equivalent per-path form (same PUA literals; Python is safer):

```powershell
git -C "V:\Ai\mesh-repo" restore --staged -- <exact-index-path>
```

### 2) All nine staged PUA junk paths

Save as a throwaway `.py` and run `python thatfile.py` if the one-liner is awkward. Contents:

```python
import subprocess
repo = r"V:\Ai\mesh-repo"
junk = [
    "BTS_MESH/V\uf03a\uf05cAi\uf05c_board\uf05cboard.json",
    "BTS_MESH/V\uf03a\uf05cAi\uf05c_queue\uf05ctree_lock.json",
    "BTS_MESH/V\uf03a\uf05cAi\uf05cLegal\uf05cWARGAME/_RUN_LOG.txt",
    "BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05c00_WORKING\uf05cSGH_returns/SGH_2026-07-31_194710_47d96b.md",
    "BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05c00_WORKING\uf05cSGH_returns/SGH_2026-07-31_195011_781fa9.md",
    "BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05c00_WORKING\uf05cSGH_returns/SGH_2026-07-31_195103_781fa9.md",
    "BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05cpapers\uf05cGrok_on_this\uf05c+Papers/A unified secondary electron cut-off presentation and common mistakes in photoelectron spectroscopy.pdf",
    "BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05cpapers\uf05cGrok_on_this\uf05c+Papers/Effects, determination, and correction of count rate nonlinearity in multi-channel analog electron detectors.pdf",
    "BTS_MESH/V\uf03a\uf05cResearch4\uf05cAi\uf05cPhD2_DATA_ARCHIVE\uf05cpapers\uf05cGrok_on_this\uf05c+Papers/_oagrab_manifest.json",
]
subprocess.run(["git", "-C", repo, "restore", "--staged", "--"] + junk, check=True)
```

### 3) If a path is already in HEAD and restore --staged is not enough

These nine paths showed as staged **A** (new). `git restore --staged` should make them untracked. If any remain in the index after that, use cached-only remove (does not delete the real modules or live files):

```powershell
python -c "import subprocess; repo=r'V:\Ai\mesh-repo'; p='BTS_MESH/V\uf03a\uf05cAi\uf05c_board\uf05cboard.json'; subprocess.run(['git','-C',repo,'rm','--cached','--',p], check=True)"
```

Repeat per leftover junk path. Do **not** `git rm` without `--cached`. Do **not** pass `BTS_MESH/bts_board.py` or `BTS_MESH/tree_lock.py`.

### Do not run

- `git add BTS_MESH/.env` or any `.env*`
- `git restore --staged -- BTS_MESH/bts_board.py`
- `git restore --staged -- BTS_MESH/tree_lock.py`
- any command against `V:\Ai\_board\board.json` or `V:\Ai\_queue\tree_lock.json`
- `git commit` / `git push` / `git commit --amend` / force
- TidyUP / TidyUP!

## Verify after someone else unstages (not run here)

```powershell
git -C "V:\Ai\mesh-repo" diff --cached --name-only
git -C "V:\Ai\mesh-repo" status --short -- "BTS_MESH/.env"
```

Expect: the nine PUA paths gone from the staged list; `bts_board.py` and `tree_lock.py` still staged if they were; `.env` still `??`.

## Refusals

- Did not push.
- Did not commit / amend / force.
- Did not run TidyUP.
- Did not take the live-tree pen.
- Did not write under `V:\Ai\BTS_MESH` or `V:\Research4\Ai\BTS_MESH`.
- Did not open, list, or read Legal/.
- Did not print tokens or `.env` contents.
- Did not execute the restore/unstage commands in this file.

## .gitignore trap (2026-08-16)

Snapshot is not the pen. Do not push. Do not commit. This section is inspect-only.

### Paths used

| path | exists |
|---|---|
| `V:\Ai\mesh-repo` | yes (git root, branch already recorded above) |
| `V:\Research4\Ai\mesh-repo` | no |
| `V:\Ai\BTS_MESH` | no |
| `V:\Research4\Ai\BTS_MESH` | yes (live BTS_MESH) |
| `V:\Ai\mesh-repo\.gitignore` | yes |
| `V:\Research4\Ai\.gitignore` | yes (Research4/Ai git root) |
| `V:\Ai\.gitignore` | no |

`.env` is not at mesh-repo root. The copy in that tree is `V:\Ai\mesh-repo\BTS_MESH\.env`.

### mesh-repo `.gitignore` is push-it-all and does NOT deny `.env`

Quoted ignore rules and the comment that states the policy (no secret values):

```
# Keith, 2026-08-16: "that's a private repo, push it all there."
#
# So this is NOT an allowlist. The whole mesh ships
# Only the things that are noise or actively break a checkout:
__pycache__/
*.pyc
*.guard.bak
*.lock
.git/
~$*
```

There is no `.env` / `.env.*` deny rule.

`git -C V:\Ai\mesh-repo check-ignore -v -- .env` -> no output, exit 1 (not ignored).
`git -C V:\Ai\mesh-repo check-ignore -v -- BTS_MESH/.env` -> no output, exit 1 (not ignored).

**mesh-repo WILL ship `.env` if someone `git add -A` / commit from that copy.**

### Research4/Ai `.gitignore` is an allowlist and will NOT ship `.env`

Quoted deny/allow lines:

```
*
!BTS_MESH/
!BTS_MESH/**/*.py
!BTS_MESH/**/*.json
!BTS_MESH/**/*.html
!BTS_MESH/**/*.bat
!BTS_MESH/**/*.vbs
!ROLD/
!ROLD/**/*.py
!ROLD/**/*.toml
!ROLD/**/*.md
!ROLD/**/*.jsonl
!.gitignore
```

`.env` is not in the allowlist. Confirm:

`git -C V:\Research4\Ai check-ignore -v -- .env` -> `.gitignore:24:*	.env`
`git -C V:\Research4\Ai check-ignore -v -- BTS_MESH/.env` -> `.gitignore:24:*	BTS_MESH/.env`

**Research4 allowlist will not ship `.env`.**

### `.env` size / identity (contents not printed)

| path | size | SHA256 vs the other |
|---|---|---|
| `V:\Ai\mesh-repo\BTS_MESH\.env` | 748 B | match |
| `V:\Research4\Ai\BTS_MESH\.env` | 748 B | match |

QA 748 B claim: confirmed. Same size and same SHA256 (same file, not just same size). Hash values not written here.

### mesh-repo git status of `.env`

- `git ls-files --stage -- BTS_MESH/.env` -> empty (not in index)
- `git status --short -- BTS_MESH/.env` -> `?? BTS_MESH/.env` (untracked, unstaged)
- `check-ignore` -> not ignored (see above)

`.env` is untracked. It is not staged, so no restore/unstage is needed.

**Do not `git add BTS_MESH/.env`. Do not `git add -A` from `V:\Ai\mesh-repo`.** That copy's ignore will not stop `.env` from entering the index.

If it ever becomes staged, unstage without deleting the working file:

```
git -C "V:\Ai\mesh-repo" restore --staged -- BTS_MESH/.env
```

or cached-only remove:

```
git -C "V:\Ai\mesh-repo" rm --cached -- BTS_MESH/.env
```

Do not `git rm` without `--cached`. Do not commit. Do not push.
