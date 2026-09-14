const markdownIt = require("markdown-it");
const markdownItAnchor = require("markdown-it-anchor");

module.exports = function (eleventyConfig) {
  eleventyConfig.ignores.add("README.md");
  eleventyConfig.ignores.add("SCOPE.md");
  eleventyConfig.ignores.add("package.json");
  eleventyConfig.ignores.add("package-lock.json");
  eleventyConfig.ignores.add("eleventy.config.js");
  eleventyConfig.ignores.add("_site");
  eleventyConfig.ignores.add("node_modules");

  eleventyConfig.addPassthroughCopy({ "src/assets": "assets" });
  eleventyConfig.addPassthroughCopy("src/robots.txt");

  eleventyConfig.addFilter("readableDate", (dateObj) => {
    return dateObj.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  });

  eleventyConfig.addFilter("isoDate", (dateObj) => {
    return dateObj.toISOString().slice(0, 10);
  });

  eleventyConfig.addShortcode("currentYear", () => new Date().getFullYear());

  const md = markdownIt({ html: true, linkify: true, typographer: true }).use(
    markdownItAnchor,
    { permalink: false }
  );
  eleventyConfig.setLibrary("md", md);

  eleventyConfig.addCollection("posts", (collectionApi) => {
    return collectionApi
      .getFilteredByGlob("content/posts/*.md")
      .sort((a, b) => b.date - a.date);
  });

  return {
    dir: {
      input: ".",
      includes: "src/_includes",
      data: "src/_data",
      output: "_site",
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
    templateFormats: ["md", "njk", "html"],
  };
};
