# SLP WOW — community & resource site

Professional community site for [slpwow.com](https://slpwow.com): news for speech-language pathologists, free resources, word-list structures, and a forum placeholder.

**Audience:** licensed and training SLPs, CFs, and related professionals — not patients or caregivers as the primary reader.

**Scope:** This package lives under `sites/slpwow/` only. It is **not** part of the COSMOS core runtime, AI mesh, or patent-related material.

## Pages

| Route | Purpose |
|-------|---------|
| `/` | Home |
| `/news/` | News & blog index |
| `/news/posts/*` | Individual posts (from `content/posts/`) |
| `/resources/` | Free SLP resources hub |
| `/word-lists/` | Word list categories & structure |
| `/forum/` | Forum placeholder (Discourse stub) |
| `/about/` | About SLP WOW |
| `/privacy/` | Privacy policy |

## Local development

```bash
cd sites/slpwow
npm install
npm run serve
```

Open `http://localhost:8080`.

## Production build

```bash
npm run build
```

Static output: `_site/` (deploy to any static host).

## Content

Draft posts live in `content/posts/` with YAML front matter. Categories: `research`, `clinical`, `wellness`, `resources`.

## Forum

`/forum/` documents a future Discourse embed. Set `discourseUrl` in `src/_data/site.json` when ready.
