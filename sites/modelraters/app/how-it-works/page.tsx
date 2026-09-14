import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "How it works",
  description:
    "A high-level look at how ModelRater helps teams rate and compare AI models with structured workflows.",
  alternates: { canonical: "/how-it-works/" },
};

const steps = [
  {
    title: "Define what good looks like",
    body:
      "Set criteria that match your use case — accuracy, tone, latency, cost, or custom rubrics your team already uses.",
  },
  {
    title: "Compare models side by side",
    body:
      "Run the same prompts or tasks across candidates and capture ratings in a single, comparable workspace.",
  },
  {
    title: "Review with your team",
    body:
      "Invite reviewers, collect notes, and see where models agree or diverge before you commit to a default.",
  },
  {
    title: "Decide with confidence",
    body:
      "Export a concise summary for stakeholders. Revisit when models or requirements change — without starting from scratch.",
  },
];

export default function HowItWorksPage() {
  return (
    <section className="section">
      <div className="container">
        <p className="eyebrow">Process</p>
        <h1
          className="display"
          style={{ fontSize: "clamp(2rem, 5vw, 3rem)", margin: "0.75rem 0 1.5rem" }}
        >
          How it works
        </h1>
        <p className="lead" style={{ marginBottom: "3rem" }}>
          ModelRater is built for teams who need a repeatable way to rate and compare models —
          without drowning in spreadsheets or one-off demos. Details of the product are
          rolling out with early access; this is the shape of the experience.
        </p>

        <ol
          style={{
            listStyle: "none",
            margin: 0,
            padding: 0,
            display: "flex",
            flexDirection: "column",
            gap: "2rem",
          }}
        >
          {steps.map((step, i) => (
            <li
              key={step.title}
              className="card"
              style={{ display: "grid", gap: "0.5rem", gridTemplateColumns: "auto 1fr" }}
            >
              <span
                className="eyebrow"
                style={{ gridRow: "span 2", paddingTop: "0.25rem", minWidth: "2rem" }}
              >
                {String(i + 1).padStart(2, "0")}
              </span>
              <h2
                className="display"
                style={{ fontSize: "1.5rem", margin: 0, gridColumn: 2 }}
              >
                {step.title}
              </h2>
              <p className="muted" style={{ margin: 0, gridColumn: 2, fontSize: "0.9375rem" }}>
                {step.body}
              </p>
            </li>
          ))}
        </ol>

        <p style={{ marginTop: "3rem" }}>
          <Link href="/contact/" className="btn">Request access</Link>
        </p>
      </div>
    </section>
  );
}
