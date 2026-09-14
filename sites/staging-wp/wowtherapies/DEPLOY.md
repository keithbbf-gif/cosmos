# Deploy — WOW Therapies (MochaHost + WordPress + GeneratePress Premium)

Target: **wowtherapies.com** (staging subdomain first, e.g. `staging.wowtherapies.com`).

## Prerequisites

- MochaHost account with **WordPress** installed (Softaculous or manual).
- **GeneratePress** (free) + **GP Premium** plugin ZIP from generatepress.com (license on your account).
- FTP/SFTP or MochaHost File Manager + wp-admin access.

## 1. WordPress baseline

1. Install WordPress on the staging domain; complete site title **WOW Therapies** and timezone **America/Chicago**.
2. Settings → General: discourage search engines **on** until launch.
3. Install plugins (minimum):
   - **GeneratePress** (theme)
   - **GP Premium** (upload ZIP; enter license)
   - Optional: **Safe SVG**, **WPForms Lite** or **Contact Form 7** for eval requests
   - Optional import: **Markdown Importer** or use manual block paste from `content/`

## 2. GeneratePress Premium modules (recommended)

Enable in GP Premium:

- **Elements** — header/footer hooks for disclaimer (child theme also prints footer disclaimer).
- **Spacing** — consistent section padding.
- **Typography** — system font stack or **Source Sans 3** / **Nunito Sans** (readable, clinical-calm).
- **Colors** — map to child CSS variables in `style.css` (`--wt-brand`, `--wt-accent`).
- **Menu Plus** — sticky nav optional.

Customizer → Layout: container width ~1200px; content separation with light borders if desired.

## 3. Child theme

1. Zip folder `themes/wowtherapies-gp-child/` (inner files at zip root) or upload via Appearance → Themes → Add New → Upload.
2. Activate **WOW Therapies (GeneratePress Child)**.
3. Confirm parent **GeneratePress** is installed.

## 4. Menus & pages

Create pages matching slugs in `content/pages/`:

| Page | Suggested slug |
|------|----------------|
| Home | `home` (set as static front page) |
| Pediatric Services | `pediatric` |
| Adult Services | `adult` |
| About | `about` |
| Contact / Request eval | `contact` |
| Resources | `resources` |
| Privacy | `privacy` |

**Import copy:** Open each `.md` file; paste body (below front matter) into the block editor, or use your Markdown import workflow. Keep status **Draft** until clinical/legal review.

Settings → Reading: **A static page** → Home.

Primary menu (Appearance → Menus): Home, Pediatric, Adult, About, Resources, Contact.

## 5. Posts

Import eight drafts from `content/posts/`; leave as **Draft**. Schedule only after owner review.

## 6. Forms (Contact / Request evaluation)

Child theme does not ship a form plugin. Recommended:

- WPForms: fields — name, email, phone, client age range, concern, preferred contact, HIPAA-friendly consent checkbox linking to Privacy page.
- Route notifications to practice email; do not store PHI in plain-text logs.

## 7. Launch checklist

- [ ] Privacy policy reviewed for Arkansas / HIPAA marketing boundaries (no PHI in web forms storage without BAA).
- [ ] Educational disclaimer visible (footer via child theme).
- [ ] No testimonial placeholders.
- [ ] SSL active; Really Simple SSL or host force HTTPS.
- [ ] GP Premium license and WordPress/core updates scheduled.
- [ ] Remove staging `noindex` when going live.

## 8. Package from repo

From repository root:

```bash
./sites/staging-wp/scripts/package-sites.sh wowtherapies
```

Upload `sites/staging-wp/dist/wowtherapies-staging.zip` and extract under `wp-content/themes/` (theme) plus copy `content/` for import reference.
