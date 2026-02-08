import type { Metadata } from "next"
import { Geist, Geist_Mono, Noto_Nastaliq_Urdu } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import { ViewTransitions } from "next-view-transitions"
import { ServiceWorkerRegistrar } from "./service-worker-registrar"

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

// Urdu font for Phase III: AI Chatbot bilingual support (T076)
// Noto Nastaliq Urdu is a Nastaliq-style font for Urdu text rendering
const notoNastaliqUrdu = Noto_Nastaliq_Urdu({
  variable: "--font-noto-nastaliq-urdu",
  subsets: ["arabic"],
  display: "swap",
  weight: ["400", "700"],
})

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
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
    icon: [
      { url: "/favicon.png", sizes: "32x32", type: "image/png" },
      { url: "/icon.png", sizes: "192x192", type: "image/png" },
    ],
    shortcut: "/favicon.png",
    apple: [
      { url: "/icon.png", sizes: "192x192", type: "image/png" },
    ],
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
        <head>
          {/* Viewport meta tag with mobile keyboard handling support */}
          {/* interactive-widget=resizes-content ensures the viewport resizes when the virtual keyboard opens */}
          {/* This prevents the keyboard from covering input fields on iOS Safari */}
          <meta
            name="viewport"
            content="width=device-width, initial-scale=1, viewport-fit=cover, interactive-widget=resizes-content"
          />
        </head>
        <body
          className={`${geistSans.variable} ${geistMono.variable} ${notoNastaliqUrdu.variable} antialiased min-h-screen`}
        >
          <Providers>{children}</Providers>
          {/* Register service worker for push notifications */}
          <ServiceWorkerRegistrar />
        </body>
      </html>
    </ViewTransitions>
  )
}
