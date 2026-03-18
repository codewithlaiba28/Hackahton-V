import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "AgentForge | 24/7 AI Employee Platform",
  description:
    "Build your first 24/7 AI Employee — a Customer Success FTE that works around the clock across Email, WhatsApp, and Web channels.",
  keywords: [
    "AI Agent",
    "Customer Success",
    "24/7 Support",
    "Digital FTE",
    "OpenAI",
    "Multi-Channel",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} antialiased`} suppressHydrationWarning>{children}</body>
    </html>
  );
}
