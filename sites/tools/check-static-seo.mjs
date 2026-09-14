#!/usr/bin/env node
/**
 * Verifies static HTML packages include expected SEO tags (from sites/shared/seo.mjs config).
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { renderSeoHead, staticSites } from "../shared/seo.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const REQUIRED_SUBSTRINGS = [
  'rel="canonical"',
  'property="og:title"',
  'property="og:description"',
  'name="twitter:card"',
  "application/ld+json",
];

let failed = false;

for (const [dir, cfg] of Object.entries(staticSites)) {
  for (const [file, page] of Object.entries(cfg.pages)) {
    const full = path.join(root, dir, file);
    if (!fs.existsSync(full)) {
      console.error(`MISSING ${dir}/${file}`);
      failed = true;
      continue;
    }
    const html = fs.readFileSync(full, "utf8");
    const pathUrl = file === "index.html" ? "/" : `/${file}`;
    const expected = renderSeoHead({
      title: page.title,
      description: page.description,
      siteName: cfg.siteName,
      origin: cfg.origin,
      path: pathUrl,
      themeColor: cfg.themeColor,
      noindex: cfg.noindex ?? false,
      jsonLd: page.jsonLd ?? false,
      organizationLegalName: cfg.organizationLegalName ?? cfg.siteName,
    });

    if (!html.includes(page.title)) {
      console.error(`FAIL ${dir}/${file}: title not in document`);
      failed = true;
    }
    for (const needle of REQUIRED_SUBSTRINGS) {
      if (needle === "application/ld+json" && !(page.jsonLd ?? false)) continue;
      if (!html.includes(needle)) {
        console.error(`FAIL ${dir}/${file}: missing ${needle}`);
        failed = true;
      }
    }
    if (!html.includes(cfg.origin)) {
      console.error(`FAIL ${dir}/${file}: missing origin ${cfg.origin}`);
      failed = true;
    }
    if ((cfg.noindex ?? false) && !html.includes("noindex")) {
      console.error(`FAIL ${dir}/${file}: expected noindex`);
      failed = true;
    }
    void expected;
  }
}

if (failed) process.exit(1);
console.log("Static SEO checks passed.");
