import type { Metadata } from "next";
import { WaitlistForm } from "@/components/WaitlistForm";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Contact",
  description: `Contact ${site.name} or join the waitlist for early access.`,
  alternates: { canonical: "/contact/" },
};

export default function ContactPage() {
  return (
    <section className="section">
      <div
        className="container"
        style={{
          display: "grid",
          gap: "3rem",
          alignItems: "start",
        }}
      >
        <div>
          <p className="eyebrow">Contact</p>
          <h1
            className="display"
            style={{ fontSize: "clamp(2rem, 5vw, 3rem)", margin: "0.75rem 0 1.5rem" }}
          >
            Waitlist &amp; inquiries
          </h1>
          <p className="lead" style={{ marginBottom: "1.5rem" }}>
            Request early access or ask a question about {site.name}. We read every
            message and respond as access opens.
          </p>
          <p className="muted" style={{ fontSize: "0.9375rem" }}>
            Email:{" "}
            <a href={`mailto:${site.contactEmail}`}>{site.contactEmail}</a>
          </p>
        </div>
        <div style={{ maxWidth: "28rem" }}>
          <WaitlistForm />
        </div>
      </div>
    </section>
  );
}
