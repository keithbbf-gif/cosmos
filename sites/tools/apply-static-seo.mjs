#!/usr/bin/env node
/**
 * Injects or refreshes SEO blocks in static HTML (between viewport and stylesheet).
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { renderSeoHead, staticSites } from "../shared/seo.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const VIEWPORT_RE =
  /(<meta\s+name="viewport"\s+content="[^"]*"\s*\/?>)\s*(?:<!--\s*@seo[\s\S]*?<!--\s*\/@seo\s*-->\s*)?[\s\S]*?(?=<link\s+rel="stylesheet")/;

for (const [dir, cfg] of Object.entries(staticSites)) {
  for (const [file, page] of Object.entries(cfg.pages)) {
    const full = path.join(root, dir, file);
    let html = fs.readFileSync(full, "utf8");
    const pathUrl = file === "index.html" ? "/" : `/${file}`;
    const block = renderSeoHead({
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
    const wrapped = `${block}\n    <!-- /@seo -->`;
    if (!VIEWPORT_RE.test(html)) {
      console.error(`SKIP ${dir}/${file}: viewport/stylesheet pattern not found`);
      process.exit(1);
    }
    html = html.replace(
      VIEWPORT_RE,
      `$1\n    <!-- @seo -->\n${wrapped}\n    `
    );
    fs.writeFileSync(full, html);
    console.log(`Updated ${dir}/${file}`);
  }
}
