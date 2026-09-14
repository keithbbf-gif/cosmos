import path from "node:path";
import { fileURLToPath } from "node:url";
import { DateTime } from "luxon";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const sitesRoot = path.join(__dirname, "..");

/**
 * @param {import("@11ty/eleventy").UserConfig} eleventyConfig
 * @param {{ siteDir: string }} opts  e.g. "slpwow" or "therapy"
 */
export function applySharedConfig(eleventyConfig, { siteDir }) {
  const input = path.join(sitesRoot, siteDir, "src");
  const output = path.join(sitesRoot, siteDir, "_site");
  const includes = path.join(sitesRoot, "shared", "_includes");

  const includesRel = path.relative(input, includes);

  eleventyConfig.addPassthroughCopy({
    [path.join(sitesRoot, "shared", "assets")]: "assets",
  });

  eleventyConfig.addFilter("absoluteUrl", (url, base) => {
    const b = String(base || "").replace(/\/$/, "");
    if (!url) return b || "";
    if (/^https?:\/\//i.test(String(url))) return String(url);
    const p = String(url).startsWith("/") ? String(url) : `/${url}`;
    return `${b}${p}`;
  });

  eleventyConfig.addFilter("currentYear", () => String(new Date().getFullYear()));

  eleventyConfig.addFilter("date", (value, format = "yyyy-MM-dd") => {
    if (!value) return "";
    const d = value instanceof Date ? value : new Date(value);
    return DateTime.fromJSDate(d).toFormat(format);
  });

  return {
    dir: {
      input,
      includes: includesRel,
      output,
    },
    pathPrefix: "/",
    htmlTemplateEngine: "njk",
    markdownTemplateEngine: "njk",
    templateFormats: ["md", "njk", "html"],
  };
}
