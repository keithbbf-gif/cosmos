# WXR draft-import generators (COSMOS content packs)

Generate **WordPress eXtended RSS (WXR) 1.2** files so Softaculous (or native WP **Tools → Import → WordPress**) can import COSMOS markdown posts as **drafts only**. This path never calls a live site or publishes content.

## Layout

| Path | Role |
|------|------|
| `tools/wxr/` | Python library + CLI (`markdown` + frontmatter → WXR) |
| `content/_ops/wxr/manifest.toml` | Configurable pack list (URLs, globs, authors) |
| `content/_ops/wxr/samples/` | Small fixtures for dry-run without full pack trees |
| `content/_ops/wxr/out/` | Default write target (gitignored via repo `out/`) |

Supported pack ids (from manifest):

`figroots-blog`, `furniture-craft-blog`, `ai-industry-blog`, `supplements-rd-blog`, `herbal-medicine-history-blog`, `slpwow-speech-pathology-history`, `wowtherapies-therapy-history`, `furniture-woods-500y-blog`, `furniture-fashion-fads-blog`, `ai-history-retrospective`

## Behaviour

- Parses YAML frontmatter and markdown body from each `*.md` post.
- **Strips** `voice_check` (and records that in dry-run JSON); it is not written to WXR.
- Sets **`wp:status` → `draft`** on every item; no publish hooks.
- **Figure paths** are preserved as:
  - HTML comments (`<!-- cosmos-media-notes ... -->`) prepended to `content:encoded`
  - `wp:postmeta` `_cosmos_media_notes` (JSON array of paths from frontmatter `figures` and markdown images)

## CLI

From the repository root:

```bash
# List configured packs
python3 -m tools.wxr list-packs

# Dry-run (JSON summary, uses sample_posts_glob — no output file)
python3 -m tools.wxr generate figroots-blog --dry-run

# Write WXR from real pack tree when present
python3 -m tools.wxr generate figroots-blog -o content/_ops/wxr/out/figroots-blog-draft.wxr.xml

# Force sample fixtures for a written file (CI / smoke)
python3 -m tools.wxr generate figroots-blog --samples -o /tmp/figroots-sample.wxr.xml
```

Requires **Python 3.11+** (stdlib `tomllib`) and **PyYAML** (already used elsewhere in COSMOS tooling).

## Sample dry-run

```bash
python3 -m tools.wxr generate figroots-blog --dry-run
```

Expected highlights in JSON:

- `post_count` ≥ 1
- `posts[].stripped_keys` contains `voice_check`
- `posts[].figure_paths` lists pack-relative media paths
- `dry_run`: true and no file under `content/_ops/wxr/out/` unless you omit `--dry-run`

## Import on WordPress (operator)

1. Copy the generated `.wxr.xml` to the target WP host (SFTP / file manager).
2. **Tools → Import → WordPress** (install importer if prompted).
3. Map authors if asked; leave posts as **draft** after import.
4. Upload media separately using paths in `_cosmos_media_notes` / HTML comments — WXR does not binary-embed images in this generator.

## Tests

```bash
python3 -m pytest tests/test_wxr_generator.py -q
```
