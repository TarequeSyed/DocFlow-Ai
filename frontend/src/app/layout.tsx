import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DocuFlow AI | Enterprise Document Intelligence Platform",
  description:
    "An AI-powered platform for structured data extraction, document classification, provenance citation mapping, and semantic vector retrieval.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-[#FAFBFC] text-[#111827]">
        {children}
      </body>
    </html>
  );
}
