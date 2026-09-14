import Link from "next/link";
import { WaitlistForm } from "@/components/WaitlistForm";

const pillars = [
  {
    title: "Intentional",
    text: "Access decisions stay visible, reviewable, and aligned with how your team actually works.",
  },
  {
    title: "Composed",
    text: "A quiet interface for noisy environments—fewer alerts, clearer ownership, less guesswork.",
  },
  {
    title: "Ready",
    text: "Built for teams who outgrew spreadsheets but refuse another sprawling admin console.",
  },
];

export default function HomePage() {
  return (
    <>
      <section className="hero" aria-labelledby="hero-heading">
        <p className="eyebrow">Private preview</p>
        <h1 id="hero-heading" className="display hero__title">
          Access, <em>without</em> the noise.
        </h1>
        <p className="lead">
          BrokenTokn helps security-minded teams keep credentials and access
          understandable—before something breaks. We&apos;re opening invites
          gradually.
        </p>
        <div className="hero__actions">
          <Link href="/waitlist" className="btn btn--primary">
            Join the waitlist
          </Link>
          <Link href="/privacy" className="btn">
            Privacy
          </Link>
        </div>
      </section>

      <section className="pillars" aria-label="Principles">
        {pillars.map((p) => (
          <article key={p.title} className="pillar">
            <h2 className="pillar__title">{p.title}</h2>
            <p className="pillar__text">{p.text}</p>
          </article>
        ))}
      </section>

      <section style={{ marginTop: "4rem" }} aria-labelledby="home-waitlist">
        <p className="eyebrow" id="home-waitlist">Early access</p>
        <h2 className="display" style={{ fontSize: "1.75rem", marginTop: "0.75rem" }}>
          Be first in line.
        </h2>
        <p className="lead" style={{ marginTop: "0.75rem" }}>
          Leave your email—we&apos;ll send a single note when your invite is ready.
        </p>
        <WaitlistForm compact />
      </section>
    </>
  );
}
