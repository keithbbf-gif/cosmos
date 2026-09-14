import Link from "next/link";
import { navLinks, site } from "@/lib/site";

export function SiteHeader() {
  return (
    <header
      style={{
        borderBottom: "1px solid var(--line)",
        background: "var(--bg)",
        position: "sticky",
        top: 0,
        zIndex: 50,
      }}
    >
      <div
        className="container"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: "1rem",
          paddingBlock: "1rem",
        }}
      >
        <Link
          href="/"
          style={{
            textDecoration: "none",
            fontFamily: "var(--font-display)",
            fontSize: "1.25rem",
            letterSpacing: "-0.02em",
          }}
        >
          {site.name}
        </Link>
        <nav aria-label="Primary">
          <ul
            style={{
              listStyle: "none",
              margin: 0,
              padding: 0,
              display: "flex",
              flexWrap: "wrap",
              gap: "clamp(0.75rem, 2vw, 1.5rem)",
              justifyContent: "flex-end",
            }}
          >
            {navLinks.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  style={{
                    textDecoration: "none",
                    fontSize: "0.8125rem",
                    letterSpacing: "0.06em",
                    textTransform: "uppercase",
                    color: "var(--ink-muted)",
                  }}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
}
