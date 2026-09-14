export const site = {
  name: "ModelRater",
  domain: "modelraters.com",
  url: "https://modelraters.com",
  tagline: "Rate and compare AI models with clarity.",
  description:
    "ModelRater helps teams evaluate, compare, and trust AI models through thoughtful workflows and a calm, transparent experience.",
  contactEmail: "hello@modelraters.com",
} as const;

export const navLinks = [
  { href: "/", label: "Home" },
  { href: "/how-it-works/", label: "How it works" },
  { href: "/pricing/", label: "Pricing" },
  { href: "/about/", label: "About" },
  { href: "/contact/", label: "Contact" },
] as const;
