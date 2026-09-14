import { applySharedConfig } from "../shared/eleventy.shared.js";

/** @param {import("@11ty/eleventy").UserConfig} eleventyConfig */
export default function (eleventyConfig) {
  eleventyConfig.addCollection("articles", (collectionApi) =>
    collectionApi.getFilteredByGlob("**/articles/*.md").sort((a, b) => b.date - a.date)
  );

  return applySharedConfig(eleventyConfig, { siteDir: "slpwow" });
}
