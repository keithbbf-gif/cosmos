# WOW Therapies — marketing site package

Static, mobile-first marketing pages for [WOW Therapies](https://wowtherapies.com), a private speech-language pathology practice serving **Southeast Arkansas** (pediatric and adult services).

## Contents

| Path | Purpose |
|------|---------|
| `index.html` | Home |
| `pediatric.html` | Pediatric speech-language therapy |
| `adult.html` | Adult cognitive, dysphagia, voice, and related services |
| `about.html` | Christina Chambers, SLP — background and mission |
| `contact.html` | Request an evaluation / contact |
| `resources.html` | Educational links and blog index |
| `privacy.html` | Privacy notice (template — review with counsel) |
| `assets/css/main.css` | Shared styles (accessible, calm palette) |
| `assets/js/main.js` | Mobile navigation toggle |
| `content/blog/` | Eight draft Markdown articles for editorial review |

## Local preview

Any static file server works from this directory:

```bash
cd sites/wowtherapies
python3 -m http.server 8080
```

Open `http://localhost:8080/`.

## Deployment notes

- Replace placeholder phone, email, and service-area details on `contact.html` before production.
- Wire the evaluation form to your HIPAA-compliant intake workflow (form is HTML-only in this package).
- Blog posts are **drafts** with `[CITE NEEDED]` markers for claims that need citations.
- No patient testimonials are included by design; add only verified, consented quotes later.

## SEO

Pages include titles, meta descriptions, canonical hints, Open Graph tags, and `MedicalBusiness` JSON-LD scoped to Southeast Arkansas speech therapy. Tune city names and NAP (name, address, phone) when the live listing is finalized.

## License

Site copy and structure are for WOW Therapies client use. COSMOS core is unchanged by this package.
