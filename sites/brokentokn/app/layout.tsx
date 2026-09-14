import type { Metadata, Viewport } from "next";
import { DM_Sans, Instrument_Serif } from "next/font/google";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { JsonLd } from "@/components/JsonLd";
import { site } from "@/lib/site";
import "./globals.css";

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-dm-sans",
  display: "swap",
});

const instrumentSerif = Instrument_Serif({
  subsets: ["latin"],
  weight: "400",
  style: ["normal", "italic"],
  variable: "--font-instrument",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  title: {
    default: `${site.name} — ${site.tagline}`,
    template: `%s · ${site.name}`,
  },
  description: site.description,
  applicationName: site.name,
  keywords: [
    "access management",
    "credentials",
    "security hygiene",
    "BrokenTokn",
    "waitlist",
  ],
  authors: [{ name: site.name, url: site.url }],
  creator: site.name,
  openGraph: {
    type: "website",
    locale: "en_US",
    url: site.url,
    siteName: site.name,
    title: site.name,
    description: site.description,
  },
  twitter: {
    card: "summary_large_image",
    title: site.name,
    description: site.description,
  },
  robots: { index: true, follow: true },
  alternates: {
    canonical: "/",
    languages: { "en-US": "/" },
  },
  category: "technology",
};

export const viewport: Viewport = {
  themeColor: site.themeColor,
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${dmSans.variable} ${instrumentSerif.variable}`}>
      <head>
        <JsonLd />
      </head>
      <body
        style={{
          // Bridge next/font CSS variables to design tokens
          ["--font-sans" as string]: "var(--font-dm-sans), system-ui, sans-serif",
          ["--font-display" as string]: "var(--font-instrument), Georgia, serif",
        }}
      >
        <a className="skip-link" href="#main-content">Skip to content</a>
        <div className="site-shell">
          <Header />
          <main id="main-content" className="site-main">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
