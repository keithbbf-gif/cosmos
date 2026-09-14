import Link from "next/link";

const nav = [
  { href: "/", label: "Home" },
  { href: "/waitlist", label: "Waitlist" },
  { href: "/privacy", label: "Privacy" },
] as const;

export function Header() {
  return (
    <header className="header">
      <div className="header__inner">
        <Link href="/" className="header__brand">
          BrokenTokn
        </Link>
        <nav className="header__nav" aria-label="Primary">
          {nav.map((item) => (
            <Link key={item.href} href={item.href} className="header__link">
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
