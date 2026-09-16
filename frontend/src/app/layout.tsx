import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ALLSTREAK — Production-Grade WhatsApp Automation SaaS",
  description: "Automate. Engage. Convert. Enterprise WhatsApp Cloud API, AI Agents, Visual Flow Builder, Team Inbox, and CRM.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 font-sans min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
