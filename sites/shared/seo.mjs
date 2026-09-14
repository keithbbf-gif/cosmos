/**
 * Shared SEO head fragments for static HTML site packages.
 * Novelty-safe copy only — no internal COSMOS architecture in public metadata.
 */

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/"/g, "&quot;");
}

/**
 * @param {object} opts
 * @param {string} opts.title - Document title
 * @param {string} opts.description - Meta description
 * @param {string} opts.siteName - Brand / og:site_name
 * @param {string} opts.origin - e.g. https://dailyscar.com (no trailing slash)
 * @param {string} opts.path - e.g. / or /product.html
 * @param {string} [opts.themeColor]
 * @param {boolean} [opts.noindex]
 * @param {boolean} [opts.jsonLd] - WebSite + Organization on index-style pages
 * @param {string} [opts.organizationLegalName]
 */
export function renderSeoHead(opts) {
  const {
    title,
    description,
    siteName,
    origin,
    path,
    themeColor = "#0f1419",
    noindex = false,
    jsonLd = false,
    organizationLegalName = siteName,
  } = opts;

  const canonical = path === "/" ? `${origin}/` : `${origin}${path}`;
  const robots = noindex ? "noindex, nofollow" : "index, follow";
  const lines = [
    `    <title>${esc(title)}</title>`,
    `    <meta name="description" content="${esc(description)}" />`,
    `    <link rel="canonical" href="${esc(canonical)}" />`,
    `    <meta name="robots" content="${robots}" />`,
    `    <meta name="theme-color" content="${esc(themeColor)}" />`,
    `    <meta property="og:type" content="website" />`,
    `    <meta property="og:locale" content="en_US" />`,
    `    <meta property="og:site_name" content="${esc(siteName)}" />`,
    `    <meta property="og:title" content="${esc(title)}" />`,
    `    <meta property="og:description" content="${esc(description)}" />`,
    `    <meta property="og:url" content="${esc(canonical)}" />`,
    `    <meta name="twitter:card" content="summary" />`,
    `    <meta name="twitter:title" content="${esc(title)}" />`,
    `    <meta name="twitter:description" content="${esc(description)}" />`,
  ];

  if (jsonLd && !noindex) {
    const graph = {
      "@context": "https://schema.org",
      "@graph": [
        {
          "@type": "WebSite",
          "@id": `${origin}/#website`,
          url: `${origin}/`,
          name: siteName,
          description,
          inLanguage: "en-US",
        },
        {
          "@type": "Organization",
          "@id": `${origin}/#organization`,
          name: organizationLegalName,
          url: `${origin}/`,
        },
      ],
    };
    lines.push(
      `    <script type="application/ld+json">${JSON.stringify(graph)}</script>`
    );
  }

  return lines.join("\n");
}

/** @type {Record<string, { origin: string; siteName: string; themeColor: string; organizationLegalName?: string; noindex?: boolean; pages: Record<string, { title: string; description: string; jsonLd?: boolean }> }>} */
export const staticSites = {
  dailyscar: {
    origin: "https://dailyscar.com",
    siteName: "DailyScar",
    themeColor: "#1a2332",
    pages: {
      "index.html": {
        title: "DailyScar — Clarity across your days",
        description:
          "DailyScar helps you notice patterns across your days with calm, human-centered continuity—not another noisy dashboard.",
        jsonLd: true,
      },
      "product.html": {
        title: "Product — DailyScar",
        description:
          "A non-technical overview of DailyScar: calm daily continuity, pattern visibility, and private-first design.",
      },
      "waitlist.html": {
        title: "Waitlist — DailyScar",
        description:
          "Join the DailyScar waitlist for early access to calm daily continuity and pattern visibility.",
      },
      "privacy.html": {
        title: "Privacy — DailyScar",
        description:
          "How DailyScar handles information on this marketing site and what to expect before launch.",
      },
    },
  },
  lmnator: {
    origin: "https://lmnator.com",
    siteName: "LMNator",
    themeColor: "#12181f",
    pages: {
      "index.html": {
        title: "LMNator — Illuminate what matters next",
        description:
          "LMNator brings calm clarity to complex work—highlighting the next right move without drowning you in detail.",
        jsonLd: true,
      },
      "product.html": {
        title: "Product — LMNator",
        description:
          "How LMNator helps you see the next step on real projects—focused guidance without inbox overload.",
      },
      "waitlist.html": {
        title: "Waitlist — LMNator",
        description: "Join the LMNator waitlist for early access to focused workflow clarity.",
      },
      "privacy.html": {
        title: "Privacy — LMNator",
        description:
          "Privacy information for the LMNator marketing site and waitlist interest form.",
      },
    },
  },
  mdrater: {
    origin: "https://mdrater.com",
    siteName: "MD Rater",
    organizationLegalName: "ModelRater",
    themeColor: "#f7f6f3",
    pages: {
      "index.html": {
        title: "MD Rater — Model evaluation, clearly rated",
        description:
          "mdrater.com is the short home for ModelRater — practical ratings and guidance for choosing AI models.",
        jsonLd: true,
      },
      "privacy.html": {
        title: "Privacy — MD Rater",
        description: "Privacy notice for the mdrater.com alias site.",
      },
    },
  },
  "ai-cluster-hub": {
    origin: "https://hub.example.com",
    siteName: "AI Cluster",
    themeColor: "#0b0d10",
    noindex: true,
    pages: {
      "index.html": {
        title: "AI Cluster — Private staging",
        description: "Private staging hub — AI product portfolio (invitation only).",
        jsonLd: false,
      },
    },
  },
};
