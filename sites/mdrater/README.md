# mdrater.com — brand alias shell

Thin static site for **mdrater.com**: a premium, minimal landing that routes attention to **ModelRater** on [modelraters.com](https://modelraters.com/) without duplicating full marketing copy or product UI.

## Contents

| File | Purpose |
|------|---------|
| `index.html` | Home with soft CTA to modelraters.com |
| `privacy.html` | Short privacy stub (alias + redirect context) |
| `styles.css` | Shared layout and typography |

## Local preview

From this directory:

```bash
python3 -m http.server 8080
```

Open `http://localhost:8080/` and check `privacy.html`.

## Deployment

Serve the folder as static files on the **mdrater.com** host (object storage + CDN, Netlify, Cloudflare Pages, GitHub Pages custom domain, etc.). No build step.

Optional hard redirect (entire apex → modelraters.com) is a hosting choice; this tree intentionally keeps a **readable landing** plus legal stub rather than a bare 302 only.

Suggested DNS: point `mdrater.com` (and `www` if used) at your static host. Enable HTTPS. If both apex and `www` are used, pick one canonical host and redirect the other.

## Scope

- No backend, APIs, or user accounts on this domain.
- No embedded patents, internal architecture, or operational documentation.
- Product policy and detailed privacy terms remain on modelraters.com.

## License

Copyright ModelRater. Deployment rights follow your organization’s policy for customer-facing web properties.
