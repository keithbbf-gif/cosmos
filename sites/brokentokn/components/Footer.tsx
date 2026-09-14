import Link from "next/link";

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer__inner">
        <p className="footer__copy">
          © {year} BrokenTokn. All rights reserved.
        </p>
        <div className="footer__links">
          <Link href="/privacy">Privacy</Link>
          <a href="mailto:hello@brokentokn.com">hello@brokentokn.com</a>
        </div>
      </div>
    </footer>
  );
}
