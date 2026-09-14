import type { Metadata } from "next";
import { WaitlistForm } from "@/components/WaitlistForm";

export const metadata: Metadata = {
  title: "Waitlist",
  description: "Join the BrokenTokn waitlist for early access.",
};

export default function WaitlistPage() {
  return (
    <>
      <header className="page-head">
        <p className="eyebrow">Waitlist</p>
        <h1 className="display page-head__title">Request an invite.</h1>
        <p className="lead">
          BrokenTokn is in a closed preview. Tell us where to reach you and
          we&apos;ll notify you when a seat opens—no mailing-list cadence, no
          product roadmap spam.
        </p>
      </header>

      <WaitlistForm />

      <section className="prose" style={{ marginTop: "3rem" }}>
        <h2>What to expect</h2>
        <ul>
          <li>A short onboarding conversation for founding teams.</li>
          <li>Access to the preview on web; mobile-friendly from day one.</li>
          <li>Direct feedback channel while we refine the experience.</li>
        </ul>
        <p>
          Questions?{" "}
          <a href="mailto:hello@brokentokn.com">hello@brokentokn.com</a>
        </p>
      </section>
    </>
  );
}
