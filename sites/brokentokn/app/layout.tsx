import type { Metadata, Viewport } from "next";
import { DM_Sans, Instrument_Serif } from "next/font/google";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
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
  metadataBase: new URL("https://brokentokn.com"),
  title: {
    default: "BrokenTokn — Clarity for high-stakes access",
    template: "%s · BrokenTokn",
  },
  description:
    "BrokenTokn is in private development. Join the waitlist for early access to a calmer way to manage credentials and access at scale.",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://brokentokn.com",
    siteName: "BrokenTokn",
    title: "BrokenTokn",
    description:
      "A premium approach to access and credentials. Waitlist open.",
  },
  robots: { index: true, follow: true },
};

export const viewport: Viewport = {
  themeColor: "#080808",
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
      <body
        style={{
          // Bridge next/font CSS variables to design tokens
          ["--font-sans" as string]: "var(--font-dm-sans), system-ui, sans-serif",
          ["--font-display" as string]: "var(--font-instrument), Georgia, serif",
        }}
      >
        <div className="site-shell">
          <Header />
          <main className="site-main">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
