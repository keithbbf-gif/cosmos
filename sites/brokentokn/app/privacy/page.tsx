import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy",
  description: "BrokenTokn privacy policy for the public marketing site and waitlist.",
};

export default function PrivacyPage() {
  return (
    <>
      <header className="page-head">
        <p className="eyebrow">Legal</p>
        <h1 className="display page-head__title">Privacy</h1>
        <p className="privacy-updated">Last updated: September 14, 2026</p>
        <p className="lead">
          This policy describes how we handle information on brokentokn.com and
          through the waitlist form. It is written for a marketing preview, not
          a live product tenant.
        </p>
      </header>

      <article className="prose">
        <h2>Who we are</h2>
        <p>
          BrokenTokn (&quot;we,&quot; &quot;us&quot;) operates the public website at
          brokentokn.com. Contact:{" "}
          <a href="mailto:hello@brokentokn.com">hello@brokentokn.com</a>.
        </p>

        <h2>What we collect</h2>
        <p>On this site we may collect:</p>
        <ul>
          <li>
            <strong>Waitlist information</strong> — email address you submit,
            plus a timestamp when you joined.
          </li>
          <li>
            <strong>Basic technical data</strong> — standard server or hosting
            logs (IP address, browser type, pages viewed) if enabled by our
            hosting provider.
          </li>
        </ul>
        <p>
          We do not sell your personal information. We do not use this preview
          site to process production credentials or customer secrets.
        </p>

        <h2>How we use information</h2>
        <ul>
          <li>To respond when preview invites become available.</li>
          <li>To operate, secure, and improve the public website.</li>
          <li>To comply with law when required.</li>
        </ul>

        <h2>Storage and retention</h2>
        <p>
          Waitlist submissions on this preview may be stored locally in your
          browser until a production endpoint is connected, or transmitted to a
          service we designate for invite management. We retain waitlist emails
          only as long as needed for the preview program or until you ask us to
          delete them.
        </p>

        <h2>Your choices</h2>
        <p>
          You may request access, correction, or deletion of your waitlist email
          by contacting{" "}
          <a href="mailto:hello@brokentokn.com">hello@brokentokn.com</a>. We
          will verify the request before acting.
        </p>

        <h2>Cookies</h2>
        <p>
          This marketing shell does not set advertising cookies. Fonts may be
          loaded from Google Fonts when you use the hosted Next.js build; your
          browser may send requests to Google accordingly.
        </p>

        <h2>Children</h2>
        <p>
          This site is not directed at children under 16, and we do not knowingly
          collect their information.
        </p>

        <h2>Changes</h2>
        <p>
          We may update this policy as the preview evolves. Material changes will
          be reflected on this page with a revised date.
        </p>

        <h2>International visitors</h2>
        <p>
          If you access this site from outside your home country, you understand
          that information may be processed in jurisdictions where our hosting
          providers operate.
        </p>
      </article>
    </>
  );
}
