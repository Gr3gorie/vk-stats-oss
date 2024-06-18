import type { Metadata } from "next";
import { Inter as FontSans } from "next/font/google";

import { Toaster } from "@/components/ui/sonner";

import "./globals.css";

import { cn } from "@/lib/utils";

import { Providers } from "./providers";

const fontSans = FontSans({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "vk-stats",
  description: "VK analytics tool",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <Providers>
      <html lang="en">
        <body
          className={cn(
            "bg-background font-sans antialiased",
            fontSans.variable,
          )}
        >
          {children}
        </body>

        <Toaster />
      </html>
    </Providers>
  );
}
