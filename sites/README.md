# Product static sites

Distinct marketing packages for the AI cluster. Each site is self-contained static HTML; no COSMOS runtime dependency.

| Package | Domain | Path |
|---------|--------|------|
| DailyScar | [dailyscar.com](https://dailyscar.com) | `sites/dailyscar/` |
| LMNator | [lmnator.com](https://lmnator.com) | `sites/lmnator/` |

Shared visual primitives live in `sites/shared/` (design tokens and base layout). Brand colors and copy stay in each package.

## Local preview

From a site directory:

```bash
python3 -m http.server 8080 --bind 127.0.0.1
```

Open `http://127.0.0.1:8080/` (paths are relative to that site root; shared assets use `../shared/`).
