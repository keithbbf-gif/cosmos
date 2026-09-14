import type { Metadata } from "next";
import Link from "next/link";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Home",
  description: site.description,
  alternates: { canonical: "/" },
};

export default function HomePage() {
  return (
    <>
      <section className="section" style={{ paddingTop: "var(--space-2xl)" }}>
        <div className="container">
          <p className="eyebrow">modelraters.com</p>
          <h1
            className="display"
            style={{
              fontSize: "clamp(2.5rem, 6vw, 4rem)",
              margin: "1rem 0 1.5rem",
              maxWidth: "16ch",
            }}
          >
            Know which model to trust.
          </h1>
          <p className="lead" style={{ marginBottom: "2rem" }}>
            {site.tagline} ModelRater brings structure to evaluation — side-by-side
            comparison, shared criteria, and a experience designed for calm decisions.
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
            <Link href="/contact/" className="btn">Request access</Link>
            <Link href="/how-it-works/" className="btn btn--ghost">How it works</Link>
          </div>
        </div>
      </section>

      <section className="section section--tight">
        <div className="container">
          <hr className="divider" />
        </div>
      </section>

      <section className="section">
        <div className="container">
          <p className="eyebrow">Why teams reach for ModelRater</p>
          <h2
            className="display"
            style={{ fontSize: "clamp(1.75rem, 4vw, 2.5rem)", margin: "0.75rem 0 2.5rem" }}
          >
            Comparison without the noise.
          </h2>
          <div className="card-grid card-grid--3">
            <article className="card">
              <h3>Clear ratings</h3>
              <p>
                Score models against what matters to you — quality, speed, cost, and fit —
                in one readable view.
              </p>
            </article>
            <article className="card">
              <h3>Shared workflows</h3>
              <p>
                Align reviewers with lightweight workflows so evaluations stay consistent
                across people and projects.
              </p>
            </article>
            <article className="card">
              <h3>Trust by design</h3>
              <p>
                A restrained interface that foregrounds evidence and context, not hype —
                so stakeholders can agree faster.
              </p>
            </article>
          </div>
        </div>
      </section>

      <section className="section" style={{ background: "var(--bg-elevated)", borderTop: "1px solid var(--line)" }}>
        <div className="container" style={{ textAlign: "center" }}>
          <span className="badge-soon">Coming soon</span>
          <h2
            className="display"
            style={{
              fontSize: "clamp(1.5rem, 3vw, 2rem)",
              margin: "1.25rem auto 1rem",
              maxWidth: "28rem",
            }}
          >
            Early access is opening gradually.
          </h2>
          <p className="lead" style={{ margin: "0 auto 2rem" }}>
            We are onboarding design partners who compare models in production. Request
            access to join the waitlist.
          </p>
          <Link href="/contact/" className="btn">Join the waitlist</Link>
        </div>
      </section>
    </>
  );
}
