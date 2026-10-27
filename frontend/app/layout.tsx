import type { Metadata } from "next"
import { Funnel_Display, Geist_Mono, Hanken_Grotesk, Noto_Nastaliq_Urdu } from "next/font/google"
import "./globals.css"
import { Providers } from "./providers"
import { ViewTransitions } from "next-view-transitions"
import { ServiceWorkerRegistrar } from "./service-worker-registrar"

// UI text
const hanken = Hanken_Grotesk({
  variable: "--font-hanken",
  subsets: ["latin"],
  display: "swap",
})

// Headlines
const funnel = Funnel_Display({
  variable: "--font-funnel",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  display: "swap",
})

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "optional",
  preload: false,
})

// Urdu font for Phase III: AI Chatbot bilingual support (T076)
// Noto Nastaliq Urdu is a Nastaliq-style font for Urdu text rendering
const notoNastaliqUrdu = Noto_Nastaliq_Urdu({
  variable: "--font-noto-nastaliq-urdu",
  subsets: ["arabic"],
  display: "swap",
  weight: ["400", "700"],
  preload: false, // only needed once Urdu text appears
})

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  title: {
    default: "Chronos | Evolution of Task Management",
    template: "%s | Chronos"
  },
  description: "A to-do list you can talk to. Add, plan and find tasks by typing or speaking, in English or Urdu.",
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
          className={`${hanken.variable} ${funnel.variable} ${geistMono.variable} ${notoNastaliqUrdu.variable} antialiased min-h-screen`}
        >
          <Providers>{children}</Providers>
          {/* Register service worker for push notifications */}
          <ServiceWorkerRegistrar />
        </body>
      </html>
    </ViewTransitions>
  )
}
