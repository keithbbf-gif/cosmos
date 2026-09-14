import Link from "next/link";
import { navLinks, site } from "@/lib/site";

export function SiteFooter() {
  const year = new Date().getFullYear();
  return (
    <footer className="section--tight" style={{ borderTop: "1px solid var(--line)" }}>
      <div className="container">
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "1.5rem",
          }}
        >
          <p className="display" style={{ fontSize: "1.125rem", margin: 0 }}>
            {site.name}
          </p>
          <nav aria-label="Footer">
            <ul
              style={{
                listStyle: "none",
                margin: 0,
                padding: 0,
                display: "flex",
                flexWrap: "wrap",
                gap: "1rem 1.5rem",
              }}
            >
              {navLinks.map((item) => (
                <li key={item.href}>
                  <Link href={item.href} className="muted" style={{ fontSize: "0.875rem" }}>
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
          <p className="muted" style={{ fontSize: "0.8125rem", margin: 0 }}>
            © {year} {site.name}. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
