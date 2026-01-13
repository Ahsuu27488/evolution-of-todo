import type { Metadata } from "next"
import { Geist, Geist_Mono } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import { ViewTransitions } from "next-view-transitions"

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "optional", // Only load if needed, reduces preload warnings
  adjustFontFallback: true,
})

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "optional", // Only load if needed, reduces preload warnings
  adjustFontFallback: true,
})

export const metadata: Metadata = {
  title: "Todo App | Phase II",
  description: "Full-stack todo application with authentication",
  icons: {
    icon: "/favicon.png",
    apple: "/favicon.png",
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <ViewTransitions>
      <html lang="en" suppressHydrationWarning>
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen`}
        >
          <Providers>{children}</Providers>
        </body>
      </html>
    </ViewTransitions>
  )
}
