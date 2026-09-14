import type { Metadata } from "next";
import Link from "next/link";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "About",
  description: `About ${site.name} — helping teams rate and compare AI models with clarity and trust.`,
  alternates: { canonical: "/about/" },
};

export default function AboutPage() {
  return (
    <section className="section">
      <div className="container" style={{ maxWidth: "40rem" }}>
        <p className="eyebrow">About</p>
        <h1
          className="display"
          style={{ fontSize: "clamp(2rem, 5vw, 3rem)", margin: "0.75rem 0 1.5rem" }}
        >
          Built for clearer model decisions.
        </h1>
        <div className="muted" style={{ fontSize: "1.0625rem", display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <p style={{ margin: 0 }}>
            {site.name} exists because choosing an AI model is rarely a single benchmark —
            it is judgment across quality, risk, cost, and how a model feels in your
            product. We focus on the experience of comparing and rating models, not on
            publishing proprietary internals or unfounded claims.
          </p>
          <p style={{ margin: 0 }}>
            Our site at {site.domain} is the public home for the product. We are in a
            pre-release phase: features ship to waitlisted teams first while we refine
            workflows and polish the interface.
          </p>
          <p style={{ margin: 0 }}>
            If you evaluate models for a living — product, research, or operations — we
            would like to hear what would make comparison effortless for you.
          </p>
        </div>
        <p style={{ marginTop: "2.5rem" }}>
          <Link href="/contact/" className="btn">Get in touch</Link>
        </p>
      </div>
    </section>
  );
}
