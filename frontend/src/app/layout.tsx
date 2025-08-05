"use client";

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

import { useState } from "react";
import { cn } from "@/lib/utils";
import { AppSidebar } from "@/components/app-sidebar";
import { ThemeProvider } from "@/components/theme-provider";
import Header from "@/components/header";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [isSidebarOpen, setSidebarOpen] = useState(false);

  return (
    <html lang="en" className="h-full" suppressHydrationWarning>
      <body
        className={cn(
          geistSans.variable,
          geistMono.variable,
          "font-sans antialiased h-full bg-background"
        )}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <div className="flex flex-col h-full">
            <Header
              isSidebarOpen={isSidebarOpen}
              setSidebarOpen={setSidebarOpen}
            />

            <div className="flex flex-1 overflow-hidden">
              <aside
                className={cn(
                  "border-r overflow-y-auto transition-all duration-300",
                  isSidebarOpen ? "w-64" : "w-18"
                )}
              >
                <AppSidebar state={isSidebarOpen} />
              </aside>
              <main className="flex-1 overflow-y-auto p-4 md:p-6">
                {children}
              </main>
            </div>
          </div>
        </ThemeProvider>
      </body>
    </html>
  );
}
