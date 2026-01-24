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
  // metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  title: {
    default: "Chronos | Evolution of Task Management",
    template: "%s | Chronos"
  },
  description: "A modern full-stack todo application demonstrating spec-driven development. Features include task management, recurring tasks, real-time search/filter, dark mode, and seamless authentication.",
  keywords: ["todo", "task management", "productivity", "chronos", "next.js", "fastapi"],
  authors: [{ name: "Chronos" }],
  creator: "Chronos",
  publisher: "Chronos",

  // Open Graph (Facebook, LinkedIn, etc.)
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://chronos-todo.vercel.app",
    title: "Chronos | Evolution of Task Management",
    description: "A modern full-stack todo application with authentication, recurring tasks, and real-time updates.",
    siteName: "Chronos",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Chronos - Evolution of Task Management"
      }
    ]
  },

  // Additional metadata
  icons: {
    icon: "/favicon.png",
    apple: "/apple-touch-icon.png"
  },
  // manifest: "/manifest.json", // Uncomment when PWA manifest is added

  // SEO
  robots: {
    index: true,
    follow: true,
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
