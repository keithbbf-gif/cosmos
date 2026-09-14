import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Pricing",
  description: "ModelRater pricing — plans and packaging coming soon. Request access for early pricing.",
  alternates: { canonical: "/pricing/" },
};

const tiers = [
  {
    name: "Starter",
    note: "For individuals exploring model fit.",
    status: "Coming soon",
  },
  {
    name: "Team",
    note: "Shared workflows and collaboration for growing groups.",
    status: "Coming soon",
  },
  {
    name: "Organization",
    note: "Governance, support, and scale for larger deployments.",
    status: "Coming soon",
  },
];

export default function PricingPage() {
  return (
    <section className="section">
      <div className="container">
        <p className="eyebrow">Pricing</p>
        <h1
          className="display"
          style={{ fontSize: "clamp(2rem, 5vw, 3rem)", margin: "0.75rem 0 1.5rem" }}
        >
          Simple plans, when we launch.
        </h1>
        <p className="lead" style={{ marginBottom: "3rem" }}>
          Public pricing is not live yet. Early partners receive tailored onboarding and
          founding-member terms. Request access to discuss fit — no commitment required.
        </p>

        <div className="card-grid card-grid--3">
          {tiers.map((tier) => (
            <article key={tier.name} className="card">
              <span className="badge-soon">{tier.status}</span>
              <h2 className="display" style={{ fontSize: "1.75rem", margin: "1rem 0 0.5rem" }}>
                {tier.name}
              </h2>
              <p style={{ margin: "0 0 1rem", color: "var(--ink-muted)", fontSize: "0.9375rem" }}>
                {tier.note}
              </p>
              <p className="eyebrow" style={{ margin: 0 }}>Price on request</p>
            </article>
          ))}
        </div>

        <p style={{ marginTop: "3rem" }}>
          <Link href="/contact/" className="btn">Request access</Link>
        </p>
      </div>
    </section>
  );
}
