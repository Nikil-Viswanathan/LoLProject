import type { Metadata } from "next";
import { DM_Sans, Space_Grotesk } from "next/font/google";
import "./globals.css";

const bodyFont = DM_Sans({ subsets: ["latin"], variable: "--font-body" });
const displayFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
});

export const metadata: Metadata = {
  title: "Rift Rankings | Higher or Lower",
  description: "Read the match. Call the stat.",
  openGraph: {
    title: "Rift Rankings | Higher or Lower",
    description: "Read the match. Call the stat. A League of Legends Higher or Lower game.",
  },
  twitter: {
    card: "summary_large_image",
    title: "Rift Rankings | Higher or Lower",
    description: "Read the match. Call the stat. A League of Legends Higher or Lower game.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${bodyFont.variable} ${displayFont.variable}`}>
        {children}
      </body>
    </html>
  );
}
